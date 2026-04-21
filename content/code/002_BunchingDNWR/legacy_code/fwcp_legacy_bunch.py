# ==============================================================================
# BUNCHING ESTIMATOR FOR DOWNWARD NOMINAL WAGE RIGIDITY
# 
# Usage: check `bunching_fwcp_cv()` function for the main entry point.
#
#
# Author : Tianhao Zhao (Clpr)
# Version: Feb 7, 2026
# GitHub : clpr.github.io
# ==============================================================================
from typing import Tuple, List, Optional, Union

import numpy as np

# Chebyshev Ridge smoothing estimator
from dataclasses             import dataclass
from sklearn.base            import BaseEstimator, TransformerMixin
from sklearn.pipeline        import Pipeline
from sklearn.linear_model    import Ridge

# For cross-validation
from sklearn.model_selection import GridSearchCV, KFold


# ==============================================================================
class WeightedHistogram:
    """
    A histogram generator that bins continuous data into equal-width bins and computes weighted frequencies.
    
    This class creates a binning scheme centered around an origin point and computes weighted histograms
    with density normalization. The bins are symmetric around the origin and extend to cover a specified range.
    
    Attributes:
        origin (float): The center point around which bins are symmetrically arranged.
        binWidth (float): The width of each bin.
        edges (np.ndarray): The bin edges defining the histogram bins.
        centers (np.ndarray): The center points of each bin.
        density (np.ndarray): The normalized density of the weighted histogram.

    Uses:
        - To create a binning scheme for continuous data, especially for wage changes around zero.
        - To compute weighted histograms that can be used for density estimation in the context of bunching estimation for downward nominal wage rigidity.

    Example:
    ```python
    # Create a weighted histogram with origin at 0, bin width of 0.01, and range from -0.5 to 0.5
    hist = WeightedHistogram(origin=0.0, binWidth=0.01, xmin=-0.5, xmax=0.5)

    print(hist.edges)   # Bin edges
    print(hist.centers) # Bin centers
    print(hist.origin_bin_idx) # Index of the bin containing the origin point
    print(hist.centers[hist.origin_bin_idx]) # Center of the origin bin (should be very close to 0)
    
    # Generate some sample data and weights
    data = np.random.normal(loc=0, scale=0.1, size=1000)
    weights = np.random.rand(1000)
    
    # Compute the weighted histogram
    hist.histogram(data, weights=weights)
    
    print(hist.edges)   # Bin edges
    print(hist.centers) # Bin centers
    print(hist.density) # Normalized density of the histogram
    ```
    """
    def __init__(
            self, 
            origin   : float, 
            binWidth : float,
            xmin     : float,
            xmax     : float
        ):

        if np.isinf(origin):
            raise ValueError("Origin cannot be infinite.")
        if np.isinf(binWidth) or binWidth <= 0:
            raise ValueError("Bin width must be a positive finite number.")
        if np.isnan(origin) or np.isnan(binWidth):
            raise ValueError("Origin and bin width cannot be NaN.")

        # the origin point to center the bins around, typically 0
        # bin of the origin point will be removed in the estimation for identify
        # counterfactual distribution.
        self.origin   = float(origin)

        # the width/diameter of the bins, 0.01 for 1 percentage point bins
        self.binWidth = float(binWidth)
        
        if xmin >= xmax:
            raise ValueError("xmin must be less than xmax.")
        if np.isinf(xmin) or np.isinf(xmax):
            raise ValueError("xmin and xmax cannot be infinite.")
        if np.isnan(xmin) or np.isnan(xmax):
            raise ValueError("xmin and xmax cannot be NaN.")
        if xmin > self.origin or xmax < self.origin:
            raise ValueError("xmin must be less than origin and xmax must be greater than origin.")

        # calculate the bin edges, growing from the origin point in both directions
        edges = [self.origin - self.binWidth/2, self.origin + self.binWidth/2]
        ptr = self.origin - self.binWidth/2
        while ptr > xmin:
            ptr -= self.binWidth
            edges.append(ptr)
        ptr = self.origin + self.binWidth/2
        while ptr < xmax:
            ptr += self.binWidth
            edges.append(ptr)
        edges = np.array(sorted(edges))

        # locate: the bin that contains/centers the origin point
        origin_bin_idx = np.searchsorted(edges, self.origin) - 1
        if origin_bin_idx < 0 or origin_bin_idx >= len(edges) - 1:
            raise ValueError("Origin point is out of the bin edges range.")
        self.origin_bin_idx = int(origin_bin_idx)

        # calculate the bin centers as the midpoints between edges
        centers = (edges[:-1] + edges[1:]) / 2

        self.edges   = edges
        self.centers = centers

        # ex-post validation: at least two bins
        if len(self.edges) < 3:
            raise ValueError("The binning scheme must produce at least two bins (three edges).")

        return None
    
    def histogram(
            self,
            data    : np.ndarray,
            weights : Optional[np.ndarray] = None
        ):

        # validation
        if not isinstance(data, np.ndarray):
            raise ValueError("Data must be a numpy array.")
        if np.isnan(data).any():
            raise ValueError("Data cannot contain NaN values.")
        if np.isinf(data).any():
            raise ValueError("Data cannot contain infinite values.")
        if weights is not None:
            if not isinstance(weights, np.ndarray):
                raise ValueError("Weights must be a numpy array.")
            if np.isnan(weights).any():
                raise ValueError("Weights cannot contain NaN values.")
            if np.isinf(weights).any():
                raise ValueError("Weights cannot contain infinite values.")
            if len(weights) != len(data):
                raise ValueError("Weights must have the same length as data.")
            if any(weights <= 0):
                raise ValueError("Weights cannot contain non-positive values.")
        else:
            weights = np.ones_like(data)

        # normalize the weights to sum to 1
        Ws = weights / np.sum(weights)

        # compute the weighted histogram using numpy's histogram function
        hist, _ = np.histogram(data, bins=self.edges, weights=Ws)

        # normalize the histogram to get a density
        density = hist / np.sum(hist)

        self.density = density
        return None
# ==============================================================================
class ChebyshevFeatures(BaseEstimator, TransformerMixin):
    """
    Create Chebyshev (1st kind) Vandermonde features up to degree K on x scaled to [-1, 1].
    Includes degree 0 term (constant).

    `x_min` and `x_max` are used to replicate the scaling used in Chebyshev interpolation,
    which is important for prediction stability when feeding new data.
    """
    def __init__(self, degree=12, x_min=-1.0, x_max=2.0, include_bias=True):
        self.degree = int(degree)
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.include_bias = bool(include_bias)

    def fit(self, X, y=None):
        X = self._validate_X(X)
        if not np.isfinite(X).all():
            raise ValueError("X contains NaN/inf.")
        if self.x_max <= self.x_min:
            raise ValueError("x_max must be > x_min.")
        if self.degree < 0:
            raise ValueError("degree must be >= 0.")
        return self

    def transform(self, X):
        X = self._validate_X(X).astype(float)
        x = X[:, 0]
        # scale to [-1, 1]
        z = 2.0 * (x - self.x_min) / (self.x_max - self.x_min) - 1.0
        # clip slightly for numerical safety if x has tiny out-of-range noise
        z = np.clip(z, -1.0, 1.0)

        # Chebyshev Vandermonde: columns are T_0(z), ..., T_degree(z)
        V = np.polynomial.chebyshev.chebvander(z, self.degree)

        if not self.include_bias:
            V = V[:, 1:]
        return V

    @staticmethod
    def _validate_X(X):
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if X.ndim != 2 or X.shape[1] != 1:
            raise ValueError("X must be shape (n_samples, 1).")
        return X
# ==============================================================================
def fit_cheb_ridge_cv(
        x, 
        y, 
        x_min        = -1.0, 
        x_max        = 2.0, 
        degrees      = (8, 10, 12, 15, 18),
        alphas       = None, 
        n_splits     = 5, 
        random_state = 0
    ):
    """
    Jointly tune (degree K, ridge alpha) with CV using GridSearchCV.
    Returns: best_estimator, grid_search_object
    """
    x = np.asarray(x).reshape(-1, 1)
    y = np.asarray(y).ravel()

    if alphas is None:
        # wide log-grid; Ridge uses "alpha" as lambda
        alphas = np.logspace(-6, 6, 97)

    pipe = Pipeline([
        ("cheb", ChebyshevFeatures(degree=12, x_min=x_min, x_max=x_max, include_bias=True)),
        ("ridge", Ridge(fit_intercept=False))
    ])

    param_grid = {
        "cheb__degree": list(degrees),
        "ridge__alpha": list(alphas),
    }

    cv = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    gs = GridSearchCV(
        estimator=pipe,
        param_grid=param_grid,
        scoring="neg_mean_squared_error",
        cv=cv,
        n_jobs=-1,
        refit=True,
        return_train_score=False,
    )
    gs.fit(x, y)
    return gs.best_estimator_, gs
# ==============================================================================
def get_fwcp(
    massActual   : float,
    massNotional : float,
    truncate0    : bool = True
) -> float:
    """
    compute the FWCP (fraction of wage cuts prevented) measure of bunching.

    Arguments:
    - massActual: the actual mass/density at the origin bin (the "bunching" bin)
    - massNotional: the counterfactual/notional mass/density at the origin bin, estimated from the fitted function
    - truncate0: if True, then return max(0, FWCP) to avoid negative values; if False, return the raw FWCP which can be negative if massNotional > massActual (which can happen due to estimation noise or if there is actually "bunching" in the opposite direction, i.e. excess mass of wage increases instead of cuts)
    """
    if massActual == 0.0:
        return 0.0
    
    fwcpRaw = 1.0 - massNotional / massActual
    if truncate0:
        return max(0.0, fwcpRaw)
    else:
        return fwcpRaw
# ==============================================================================
def bunching_fwcp_cv(
    data : np.ndarray,

    # bunching FWCP parameter
    truncate0 : bool = True,

    # histogram binning parameters
    origin   : float = 0.00,
    binWidth : float = 0.01,
    xmin     : float = -1.0,
    xmax     : float =  1.0,

    # weighting scheme for the histogram, if None then equal weights
    weights : Optional[np.ndarray] = None,

    # ridge regression CV parameters
    cheby_deg_candidates : List[int] = [8,10,12,15,18],
    alpha_candidates     : Optional[List[float]] = None,
    cv_folds             : int = 5,
    cv_seed              : Optional[int] = None,
) -> dict:
    """
    Estimate the FWCP measure of bunching using a Chebyshev Ridge regression 
    with cross-validation to select the degree of the Chebyshev polynomial and 
    the ridge penalty parameter.

    Args:
    - data: a 1D numpy array of the continuous wage growth variable to be binned
    - truncate0: whether to truncate the FWCP measure at 0 to avoid negative values
    - origin: the center point for the histogram bins (typically 0 for wage changes)
    - binWidth: the width of the histogram bins (e.g. 0.01 for 1 percentage point bins if `data` is in decimal form; if `data` is in percentage points, then binWidth=1 would be 1 percentage point bins)
    - xmin: the minimum value for the histogram bins (e.g. -1 for -100% wage change)
    - xmax: the maximum value for the histogram bins (e.g. 1 for +100% wage change)
    - weights: an optional 1D numpy array of weights for the histogram; if None, equal weights are used
    - cheby_deg_candidates: a list of integers for the candidate degrees of the Chebyshev polynomial to be tuned by CV
    - alpha_candidates: an optional list of floats for the candidate ridge penalty parameters to be tuned by CV; if None, a default wide log-grid from 1e-6 to 1e6 is used
    - cv_folds: the number of folds for cross-validation (must be at least 2)
    - cv_seed: an optional integer seed for reproducibility of the CV splits; if None, the CV splits will be random without a fixed seed

    Returns a dictionary with the following keys:
    - "mse_cv_best": the best cross-validated MSE
    - "cheby_deg_best": the best degree of Chebyshev polynomial
    - "ridge_alpha_best": the best ridge penalty parameter
    - "f": the fitted callable function, can be evaluated at any x in the range
        of the original data (and even slightly outside due to the scaling), and
        the function can take a numpy 1D-array (vector) as input.
    - "fwcp": the estimated FWCP measure of bunching
    - "densityActual": the actual density/mass at the origin bin from the histogram
    - "densityNotional": the counterfactual/notional density/mass at the origin bin estimated from the fitted function
    - "histogram": the WeightedHistogram object containing the histogram details (edges, centers, density, etc.)

    Example:
    ```python
    # Sample data: 1000 wage changes drawn from a normal distribution
    np.random.seed(0)
    data = np.random.normal(loc=0, scale=0.1, size=1000)
    data = np.append(np.zeros(200), data)  # add some bunching at 0
    weights = np.random.rand(len(data))    # random weights for the histogram

    # Estimate the FWCP measure of bunching
    results = bunching_fwcp_cv(
        data = data,
        truncate0 = True,
        origin    = 0.0,
        binWidth  = 0.01,
        xmin      = data.min(),
        xmax      = data.max(),
        weights   = weights,
        cheby_deg_candidates = [8, 10, 12, 15, 18],
        alpha_candidates     = np.logspace(-6, 6, 97),
        cv_folds = 5,
        cv_seed  = 42
    )

    # visualization
    plt.figure()
    plt.bar(
        results["histogram"].centers, 
        results["histogram"].density, 
        width=results["histogram"].binWidth*0.9, 
        alpha=0.5, 
        label="Weighted Histogram"
    )
    x_fit = np.linspace(results["histogram"].edges[0], results["histogram"].edges[-1], 200)
    plt.plot(x_fit, results["f"](x_fit), color="red", label="Fitted Chebyshev Ridge")
    plt.axvline(0, color="black", linestyle="--", label="Origin (0)")
    plt.title(f"FWCP Estimate (5-fold CV): {results['fwcp']}")
    plt.xlabel(f"Wage Change, OptChebDeg = {results['cheby_deg_best']}, RidgeAlpha = {results['ridge_alpha_best']:.2e}")
    plt.ylabel("Density")
    plt.legend()
    plt.show()
    ```
    """

    if not isinstance(cheby_deg_candidates, list):
        raise ValueError("cheby_deg_candidates must be a list of integers")
    if len(cheby_deg_candidates) == 0:
        raise ValueError("cheby_deg_candidates must be a non-empty list")
    if not all(isinstance(k, int) and k > 0 for k in cheby_deg_candidates):
        raise ValueError("cheby_deg_candidates must be a list of positive int")
    
    if cv_folds < 2:
        raise ValueError("cv_folds must be at least 2")
    if cv_seed is not None and not isinstance(cv_seed, int):
        raise ValueError("cv_seed must be an integer or None")
    
    # step 1: create weighted histogram
    hist = WeightedHistogram(
        origin   = origin, 
        binWidth = binWidth, 
        xmin     = xmin, 
        xmax     = xmax
    )
    hist.histogram(np.array(data), weights = np.array(weights))

    # step 2: get the original density at the origin bin, which will be used to compute the FWCP measure
    densityActual = hist.density[hist.origin_bin_idx]

    # step 3: prepare the counterfactual/notional data for regression
    # by removing the origin bin and treating the bin centers as X and the densities as Y
    mask = np.arange(len(hist.centers)) != hist.origin_bin_idx
    X = hist.centers[mask]
    Y = hist.density[mask]

    # step 4: fit chebyshev ridge with CV to the histogram density
    best_model, gs = fit_cheb_ridge_cv(
        X,
        Y,
        x_min        = X.min(),
        x_max        = X.max(),
        degrees      = cheby_deg_candidates,
        alphas       = alpha_candidates,
        n_splits     = cv_folds,
        random_state = cv_seed
    )

    # step 5: define a prediction method
    ffit = lambda x : best_model.predict([x,]) if np.isscalar(x) else best_model.predict(x.reshape(-1,1))

    # step 6: compute the counterfactual density at the origin point
    densityNotional = ffit(origin)

    # step 7: compute the FWCP measure
    fwcp = get_fwcp(densityActual, densityNotional, truncate0 = truncate0)

    # step 8: return results in a dictionary
    return {
        "mse_cv_best"      : gs.best_score_,
        "cheby_deg_best"   : best_model.named_steps["cheb"].degree,
        "ridge_alpha_best" : best_model.named_steps["ridge"].alpha,
        "f"    : ffit,
        "fwcp" : fwcp,
        "densityActual"   : densityActual,
        "densityNotional" : densityNotional,
        "histogram" : hist,
    }
