# Bunching (kink) estimator for FWCP (fraction of wage cuts prevented)
# Version: Feb 27, 2026 05:47 PM GMT+8
# Author: Tianhao Zhao
# ==============================================================================
from typing import Union, Optional
from collections.abc import Callable

import numpy as np
from numpy.polynomial.chebyshev import chebvander
from sklearn.linear_model import Ridge, RidgeCV
from scipy.stats import percentileofscore # to compute income quantiles





# ==============================================================================
# HELPERS
# ==============================================================================
def normalize(xvec : np.ndarray, xlim : tuple = (-1, 1)) -> np.ndarray:
    """Normalizes the input vector to a specified range.
    """
    return (xvec-xlim[0])/(xlim[1]-xlim[0]) * 2 - 1
# ------------------------------------------------------------------------------
def wtint_mirror(
    f : Callable[[float], float], 
    xmid : float, 
    xmin : float, 
    xmax : float,
    weighted_by_x : bool = False,
    weight_shift  : float = 0.0
) -> float:
    """
    Consider a univariate function f(x) defined on support [xmin, xmax].
    Define a clapmed version of f(x) as: f1(x) = f(x) for x in [xmin, xmax] and f1(x) = 0 otherwise.

    Compute the following weighted integral:

    $$
    \\int_{\\min\\{ xmin, 2*xmid - xmax \\}}^{xmid}  |x + weight_shift| \\cdot (f1(2xmid-x) - f1(x)) dx
    $$

    where `x+weight_shift` is the weight function, and `f1(2xmid-x) - f1(x)` is the mirror difference of f1 at x.
    
    Arguments:
    - f: the univariate function to be integrated. must be evaluatable at any x in [xmin, xmax].
    - xmid: the midpoint of the mirror operation.
    - xmin: the minimum x value of the support of f.
    - xmax: the maximum x value of the support of f.
    - weighted_by_x: if True, the weight function is x; if False, the weight function is 1.
    - weight_shift: a constant shift added to the weight function.

    Returns:
    - The computed value of the weighted integral.

    Dependencies:
    - from collections.abc import Callable for type hinting the function argument.
    - scipy.integrate.quad for numerical integration.

    Notes:
    - This function is designed to compute the FWCP measure based on symmetry assumptions, where f(x) is supposed to be PDF of de-meaned wage growth distribution.
    """
    from scipy import integrate
    
    def f1(x):
        """Clamped version of f(x)"""
        if xmin <= x <= xmax:
            return f(x)
        return 0.0
    
    def integrand(x):
        """The weighted mirror difference function"""
        weight = abs(x + weight_shift) if weighted_by_x else (1.0 + weight_shift)
        mirror_diff = f1(2 * xmid - x) - f1(x)
        return weight * mirror_diff
    
    # Integration bounds
    lower = min(xmin, 2 * xmid - xmax)
    upper = xmid
    
    # Compute the integral
    result, _ = integrate.quad(integrand, lower, upper)
    
    return float(result)



# ==============================================================================
# UNIVARIATE CHEBYSHEV-RIDGE REGRESSION
# ==============================================================================
class UnivariateChebRidgeRegression:
    """Univariate Chebyshev regression with ridge regularization.

    Example usage:
    ```python
    import numpy as np
    import bunchingfwcp as bf
    
    # Sample data
    Xs = np.linspace(0, 10, 200)
    Ys = np.sin(Xs) + 0.1 * np.random.randn(200)

    # Initialize and fit the model
    crr = bf.UnivariateChebRidgeRegression(
        degree = 20,
        alpha  = 0.1,
        xlim = (Xs.min(), Xs.max())
    )

    # fit: use current hyperparameters
    crr.fit(Xs, Ys)

    # fit: use LOOCV to select best hyperparameters from grids
    crr.fit_loocv(
        Xs, Ys,
        degree_grid = np.arange(10, 30),
        alpha_grid  = np.logspace(-4, 4, 100),
        scoring     = 'neg_root_mean_squared_error'
    )

    # predict: the model is callable after fitting
    Y_pred = crr(Xs)

    # access best hyperparameters and CV score
    print(f"Best degree: {crr.degree}")
    print(f"Best alpha: {crr.alpha}")
    print(f"Best CV score: {crr.best_score} ({crr.best_score_name})")

    # visualize the fit
    import matplotlib.pyplot as plt
    plt.figure()
    plt.scatter(Xs, Ys, label='Data', alpha=0.5)
    plt.plot(Xs, Y_pred, label='ChebRidge Fit', color='red')
    plt.legend()
    plt.show()
    ```
    """
    def __init__(
        self, 
        degree : int   = 20 , # default: 20, common for smooth function approx
        alpha  : float = 0.0, # default: 0.0, no regularization, can be tuned
        xlim   : tuple = (-1, 1), # default: (-1, 1), range for chebyshev poly
    ):
        """Initializes the ChebRidgeRegression object.

        Parameters
        ----------
        degree : int
            Max degree of the Chebyshev polynomial. starts at 0. Defaults to 20,
            which is a common choice for smooth function approximation; can be
            tuned based on the complexity of the underlying function.
        alpha : float
            Ridge regularization parameter. Defaults to 0.0 (no regularization).
            Can be tuned to prevent overfitting, esp for high-frequency noise.
        xlim : tuple
            Range of the input variable. Defaults to (-1, 1). For transformation
        model : Optional[np.ndarray]
            sklearn Ridge regression model instance. Initialized as None.
        """
        if not isinstance(degree, int):
            raise ValueError("Degree must be an integer.")
        if not isinstance(alpha, (int, float)):
            raise ValueError("Alpha must be a numeric value.")
        if degree < 0:
            raise ValueError("Degree must be non-negative.")
        if alpha < 0:
            raise ValueError("Alpha must be non-negative.")
        if not isinstance(xlim, tuple) or len(xlim) != 2:
            raise ValueError("xlim must be a tuple of length 2.")
        if xlim[0] >= xlim[1]:
            raise ValueError("xlim must be a tuple (min, max) with min < max.")
        
        self.degree = int(degree)
        self.alpha  = float(alpha)
        self.xlim   = xlim
        self.model  = None

    def design_matrix(self, xvec : Union[float,np.ndarray]) -> np.ndarray:
        """Constructs the design matrix for Chebyshev regression.
        """
        xvec_normed = normalize(np.array(xvec), self.xlim)
        return chebvander(xvec_normed, self.degree)

    def __call__(self, xvec : Union[float,np.ndarray]) -> np.ndarray:
        """Predicts the output for the given input vector using the fitted model
        """
        if self.model is None:
            raise ValueError("Model has not been fitted yet.")
        return self.model.predict(self.design_matrix(xvec))

    def fit(self, xvec : np.ndarray, yvec : np.ndarray):
        """Fits the Chebyshev regression model to the data.
        using parameter stored in the object.
        """
        if not isinstance(xvec, np.ndarray) or not isinstance(yvec, np.ndarray):
            raise ValueError("xvec and yvec must be numpy arrays.")
        if xvec.ndim != 1 or yvec.ndim != 1:
            raise ValueError("xvec and yvec must be 1-dimensional.")
        self.model = Ridge(alpha = self.alpha, fit_intercept=False)
        self.model.fit(self.design_matrix(xvec), yvec)

    def fit_loocv(
        self, 
        xvec : np.ndarray,
        yvec : np.ndarray, 
        
        degree_grid : Union[np.ndarray, list] = np.arange(10, 30),
        alpha_grid  : Union[np.ndarray, list] = np.logspace(-4, 4, 100),
        scoring     : str = 'neg_root_mean_squared_error'
    ):
        """Fits the Chebyshev regression model using leave-one-out CV to select
        the best degree and alpha from the provided grids. This function will
        update the model's degree, alpha, and fitted model attributes with the
        best found parameters; also, a new attribute `best_score` will be added
        to store the best CV score achieved.
        """
        if not isinstance(xvec, np.ndarray) or not isinstance(yvec, np.ndarray):
            raise ValueError("xvec and yvec must be numpy arrays.")
        if xvec.ndim != 1 or yvec.ndim != 1:
            raise ValueError("xvec and yvec must be 1-dimensional.")
        if not isinstance(degree_grid, (np.ndarray, list)):
            raise ValueError("degree_grid must be a numpy array or list.")
        if not isinstance(alpha_grid, (np.ndarray, list)):
            raise ValueError("alpha_grid must be a numpy array or list.")
        if not isinstance(scoring, str):
            raise ValueError("scoring must be a string representing a valid sklearn scoring metric.")

        # malloc
        best_score  : float           = -np.inf
        best_degree : Optional[int]   = None   
        best_alpha  : Optional[float] = None   

        # pre-conditioning
        dm = self.design_matrix(xvec)

        # idea: best of best: use the best alpha for each degree, then select 
        # the best degree among those, to maximize performance provided by 
        # sklearn's RidgeCV which is optimized for alpha selection.
        for deg in degree_grid:
            condi_best_model = RidgeCV(
                alphas        = alpha_grid, # candidate L2 penalties
                fit_intercept = False,      # due to ChebT_0 = 1
                scoring       = scoring,    # CV score to maximize
                cv            = None,       # leave-one-out CV
                gcv_mode      = 'auto',     # automatic choice; SVD primarily
                store_cv_results = False,   # do not store CV result traces (use `store_cv_values` if version of sklearn < 1.5)
            ).fit(dm[:, :deg+1], yvec)
            condi_best_alpha = condi_best_model.alpha_
            condi_best_score = condi_best_model.best_score_
            if condi_best_score > best_score:
                best_score  = float(condi_best_score)
                best_degree = deg
                best_alpha  = float(condi_best_alpha)

        # fit the final model with the best hyperparameters
        self.degree = best_degree
        self.alpha  = best_alpha
        self.model  = Ridge(alpha = self.alpha, fit_intercept=False)
        self.model.fit(self.design_matrix(xvec), yvec)

        # extraly, store the best score for reference
        self.best_score = best_score
        self.best_score_name = scoring





# ==============================================================================
# BUNCHING (KINK) HISTOGRAM ESTIMATOR
# ==============================================================================
class KinkHistogram:
    """Bunching (1 kink, 1 point mass spike) histogram estimator
    """
    def __init__(
        self,
        kink_point : float = 0.0,    # default: 0.0, location of the kink (bunching point)
        bin_width  : float = 0.1,    # default: 0.1, width of the histogram bins
        xlim       : tuple = (-1, 1) # default: (-1, 1), range for the histogram to cover; data outside this range will be ignored
    ):
        if not isinstance(kink_point, (int, float)):
            raise ValueError("kink_point must be a numeric value.")
        if not isinstance(bin_width, (int, float)):
            raise ValueError("bin_width must be a numeric value.")
        if bin_width <= 0:
            raise ValueError("bin_width must be positive.")
        if not isinstance(xlim, tuple) or len(xlim) != 2:
            raise ValueError("xlim must be a tuple of length 2.")
        if xlim[0] >= xlim[1]:
            raise ValueError("xlim must be a tuple (min, max) with min < max.")
        if not (xlim[0] <= kink_point <= xlim[1]):
            raise ValueError(f"kink_point must be within the range specified by xlim but got {kink_point} with xlim={xlim}.")

        self.kink_point = kink_point
        self.bin_width  = bin_width
        self.xlim       = xlim
        self.hist       = None # to store the fitted histogram counts

        # design bin edges
        lb = kink_point - bin_width/2
        ub = kink_point + bin_width/2
        lb -= np.ceil((lb - xlim[0]) / bin_width) * bin_width
        ub += np.ceil((xlim[1] - ub) / bin_width) * bin_width
        self.bin_edges = np.arange(lb, ub + bin_width, bin_width)

        # midpoints of the bins, for reference & fitting purposes
        self.mid_points = (self.bin_edges[:-1] + self.bin_edges[1:]) / 2

        # deviation of each bin from the kink point, for reference purposes, denoted as integers (deviation of kink bin itself is 0)
        # (e.g. for mirroring the distribution for symmetric FWCP estimation)
        self.deviation_from_kink = np.round((self.mid_points - kink_point) / bin_width).astype(int)

        # locate in which bin the kink point falls (note: python use 0-based indexing)
        self.kink_bin_index = int((kink_point - lb) // bin_width)

    def fit(
        self, 
        xvec : np.ndarray, 
        weights : Optional[np.ndarray] = None,
        density : bool = True
    ):
        """Fits the kink histogram model to the data. The `weights` parameter can be used
        to provide sample weights for the histogram counts.
        Weights are normalized to sum 1, and treated as analytical weights.

        Updates the `hist` attribute with the fitted histogram counts for each bin. If `density=True`,
        the histogram will be normalized to represent a probability density function (PDF) over the specified range.
        """
        if weights is None:
            weights = np.ones_like(xvec)
        else:
            if not isinstance(weights, np.ndarray):
                raise ValueError("weights must be a numpy array.")
            if weights.shape != xvec.shape:
                raise ValueError("weights must have the same shape as xvec.")
            if np.any(weights < 0):
                raise ValueError("weights must be non-negative.")
        
        # normalize to sum 1, to treat them as analytical weights for the histogram
        weights = weights / np.sum(weights)

        # store the histogram counts for reference
        self.hist = np.histogram(
            xvec, 
            bins    = self.bin_edges, 
            weights = weights, 
            density = density,
            range   = self.xlim
        )[0] # only keep the counts, ignore the bin edges returned

    def hist_counterfactual(self):
        """Constructs the counterfactual histogram counts by removing the point
        mass at the kink bin.

        returns a dictionary with keys:
        - "mid_points": the mid points of the bins (excluding the kink bin)
        - "hist": the histogram counts for each bin (excluding the kink bin)
        """
        if self.hist is None:
            raise ValueError("Model has not been fitted yet.")
        return {
            "mid_points" : np.delete(self.mid_points, self.kink_bin_index),
            "hist"       : np.delete(self.hist, self.kink_bin_index),
            "deviation_from_kink" : np.delete(self.deviation_from_kink, self.kink_bin_index)
        }




# ==============================================================================
# BUNCHING FWCP ESTIMATOR (MAIN ENTREE)
# ==============================================================================
class FWCPBunchingEstimator:
    """FWCP (fraction of wage cuts prevented) bunching estimator using a kink histogram approach.
    Counterfactual/notional distribution is constructed by removing the point mass at the kink bin, 
    then fit a smooth density function using the UnivariateChebRidgeRegression to the remaining bins.

    # Example
    ```python
    # another example: simulated data
    import numpy as np

    dW = np.concatenate([
        np.random.randn(1000) / 1.96,
        np.random.rand(20) * 0.02 - 0.01 # limit to [-0.01, 0.01]
    ])
    est_sim = bf.FWCPBunchingEstimator(
        dW,
        kink_point = 0.0,
        bin_width  = 0.02,
        xlim       = (-1.0, 2.0),
        density    = True,
        cv = True,
        degree_grid = np.arange(1,30)
    )

    # viz
    dat = est_sim.plotdata()
    plt.figure()
    plt.bar(
        dat["x"],
        dat["y_actual"],
        width = dat["bin_width"] * 0.9,
        label = "Actual PDF"
    )
    plt.plot(
        dat["x"],
        dat["y_notional"],
        label = "Notional PDF",
        color = "red"
    )
    plt.axhline(dat["kink_mass_notional"], color = "red", linestyle = "--", label = "Notional kink mass")
    plt.axhline(dat["kink_mass_actual"], color = "blue", linestyle = "--", label = "Actual kink mass")

    # advanced stats
    plt.title(f"Simulated FWCP = {est_sim.fwcp_relative: .3f}")
    plt.xlabel(f"Actual mass/Notional mass = {dat["kink_mass_actual"]: .3f}/{dat["kink_mass_notional"]: .3f}")
    plt.ylabel(f"CV Cheb degree = {est_sim.notional_dist_estimator.degree}, CV Ridge alpha = {est_sim.notional_dist_estimator.alpha: .3f}")

    plt.legend()
    plt.show()
    ```
    """
    def __init__(
        self,
        Xs : np.ndarray, # the wage change data (e.g., log wage changes; NOT histogram bin mid points, but the raw data points to be binned)

        # histogram parameters
        weights    : Optional[np.ndarray] = None, # optional weights for the histogram counts; if None, equal weights are used
        kink_point : float = 0.0,  # default: 0.0, location of the kink (bunching point)
        bin_width  : float = 0.02, # default: 0.02, width of the histogram bins (+-1% wage change)
        xlim       : tuple = (-1.0, 2.0), # default: (-1.0, 2.0), range for the histogram to cover; data outside this range will be ignored
        density    : bool = True, # default: True, whether to normalize the histogram to represent a density function (PDF)

        # Chebyshev Ridge regression parameters
        degree : int   = 20 , # default: 20, common for smooth function approx
        alpha  : float = 0.0, # default: 0.0,
        cv     : bool  = False, # default: False, whether to use LOOCV to select best hyperparameters for Chebyshev Ridge regression; if true, then `degree_grid` and `alpha_grid` will be used to search for the best hyperparameters and `degree` and `alpha` parameters will be ignored
        degree_grid : Union[np.ndarray, list] = np.arange(10, 30),
        alpha_grid  : Union[np.ndarray, list] = np.logspace(-4, 4, 100),
        scoring     : str = 'neg_root_mean_squared_error'
    ):
        # step: make the histogram estimator
        self.hist_estimator = KinkHistogram(
            kink_point = kink_point,
            bin_width  = bin_width,
            xlim       = xlim
        )
        self.hist_estimator.fit(
            xvec    = Xs,
            weights = weights,
            density = density
        )

        # step: get data for the counterfactual distribution (remove the kink bin)
        data_cf = self.hist_estimator.hist_counterfactual()
        Xs_cf = data_cf["mid_points"]
        Ys_cf = data_cf["hist"]

        # step: fit the counterfactual distribution with Chebyshev regression
        self.notional_dist_estimator = UnivariateChebRidgeRegression(
            degree = degree,
            alpha  = alpha,
            xlim   = xlim
        )
        if cv:
            self.notional_dist_estimator.fit_loocv(
                xvec = Xs_cf,
                yvec = Ys_cf,
                degree_grid = degree_grid,
                alpha_grid  = alpha_grid,
                scoring     = scoring
            )
        else:
            self.notional_dist_estimator.fit(Xs_cf, Ys_cf)

        # extract: spike/kink point mass: actual vs. notional
        self.kink_mass_actual   = self.hist_estimator.hist[self.hist_estimator.kink_bin_index]
        self.kink_mass_notional = self.notional_dist_estimator(self.hist_estimator.kink_point)[0]

        # define: FWCP, absolute and relative
        self.fwcp_absolute = self.kink_mass_actual - self.kink_mass_notional
        self.fwcp_relative = self.fwcp_absolute / self.kink_mass_actual if self.kink_mass_actual != 0 else np.nan

    def __str__(self):
        return (f"FWCPBunchingEstimator(kink_point={self.hist_estimator.kink_point}, "
                f"bin_width={self.hist_estimator.bin_width}, "
                f"xlim={self.hist_estimator.xlim}, "
                f"fwcp_absolute={self.fwcp_absolute}, "
                f"fwcp_relative={self.fwcp_relative})")

    def plotdata(self):
        """Prepare data for visualization of the actual vs. notional distribution around the kink point.
        """
        if self.hist_estimator.hist is None or self.notional_dist_estimator.model is None:
            raise ValueError("Model has not been fitted yet.")
        return {
            "x" : self.hist_estimator.mid_points,
            "y_actual" : self.hist_estimator.hist,
            "y_notional" : self.notional_dist_estimator(self.hist_estimator.mid_points),
            "kink_point" : self.hist_estimator.kink_point,
            "kink_mass_actual" : self.kink_mass_actual,
            "kink_mass_notional" : self.kink_mass_notional,
            "bin_width" : self.hist_estimator.bin_width
        }







# ==============================================================================
# SYMMETRIC FWCP ESTIMATOR - INTEGRATION (MAIN ENTREE 2)
# ==============================================================================
class FWCPSymmetricEstimator:
    """FWCP (fraction of wage cuts prevented) symmetric estimator using a kink histogram approach.
    Counterfactual/notional distribution is constructed by:
    0. estimating a kink histogram as in the KinkHistogram, to get (wage growth, density) pairs for the actual distribution)
    1. removing the point mass at the kink bin (to account for potential asymmetry in the distribution around the kink point, which may bias the FWCP estimation if not accounted for)
    2. centering the remaining distribution by deducting the median of the remaining data
    3. fitting a smooth density function using the UnivariateChebRidgeRegression to the centered distribution
    4. compute FWCP by integrating the mirror difference of the fitted notional distribution, weighted by (de-medianed) wage growth to account for the impact of the distribution's span

    # Example
    ```python
    # another example: simulated data
    import numpy as np

    dW = np.concatenate([
        np.random.randn(1000) / 1.96,
        np.random.rand(20) * 0.02 - 0.01 # limit to [-0.01, 0.01]
    ])
    est_sim = bf.FWCPSymmetricEstimator(
        dW,
        kink_point = 0.0,
        bin_width  = 0.02,
        xlim       = (-1.0, 2.0),
        density    = True,
        cv = True,
        degree_grid = np.arange(1,30),

        symmetry_type = 'median', # the type of symmetry assumption to make for the distribution; can be: "median", "mean", "weighted mean"
        centering : bool = True, # default: True, whether to center the distribution by deducting the median to control for potential wage growth trend
        use_original_x_for_weight  = False, # whether to use the original (not de-medianed) wage growth for the weight function in FWCP integration; if True, then the weight function is original wage growth instead of de-medianed wage growth; advanced options for research purposes; don't change this unless you know what you are doing
    )

    # result access
    print(f"Median of the distribution after removing kink bin = {est_sim.datMid: .3f}")
    print(f"FWCP (weighted by abs of de-medianed growth) = {est_sim.fwcp_relative: .3f}")
    print(f"FWCP (unweighted) = {est_sim.fwcp_absolute: .3f}")
    ```
    """
    def __init__(
        self,
        Xs : np.ndarray, # the wage change data (e.g., log wage changes; NOT histogram bin mid points, but the raw data points to be binned)

        # kink histogram parameters
        weights    : Optional[np.ndarray] = None, # optional weights for the histogram counts; if None, equal weights are used
        kink_point : float = 0.0,  # default: 0.0, location of the kink (bunching point)
        bin_width  : float = 0.02, # default: 0.02, width of the histogram bins (+-1% wage change)
        xlim       : tuple = (-1.0, 2.0), # default: (-1.0, 2.0), range for the histogram to cover; data outside this range will be ignored
        density    : bool = True, # default: True, whether to normalize the histogram to represent a density function (PDF)

        # Chebyshev Ridge regression parameters
        degree : int   = 20 , # default: 20, common for smooth function approx
        alpha  : float = 0.0, # default: 0.0,
        cv     : bool  = False, # default: False, whether to use LOOCV to select best hyperparameters for Chebyshev Ridge regression; if true, then `degree_grid` and `alpha_grid` will be used to search for the best hyperparameters and `degree` and `alpha` parameters will be ignored
        degree_grid : Union[np.ndarray, list] = np.arange(10, 30),
        alpha_grid  : Union[np.ndarray, list] = np.logspace(-4, 4, 100),
        scoring     : str = 'neg_root_mean_squared_error',

        # symmetric FWCP integration parameters
        symmetry_type    : Union[str,float]  = 'median', # default: 'median', the type of symmetry assumption to make for the distribution; can be: "median", "mean", "weighted mean", or a specific number to use as the center point for mirroring operation
        centering        : bool = True, # default: True, whether to center the distribution by deducting the median to control for potential wage growth trend
        use_original_x_for_weight : bool = False, # default: False, whether to use the original (not de-medianed) wage growth for the weight function in FWCP integration; if True, then the weight function will be original wage growth instead of de-medianed wage growth; advanced options for research purposes; don't change this unless you know what you are doing
    ):
        
        # step: index the data by removing the kink bin (to slice data and obs weights) & do slicing
        # note: if not truncating the data to the specified xlim, extreme values would severely bias the median and thus the centering step
        idx1 = np.abs(Xs - kink_point) > bin_width/2
        idx2 = (xlim[0] <= Xs) & (Xs <= xlim[1])
        idx  = idx1 & idx2
        
        # step: remove the observations in the kink bin
        dat = Xs[idx]
        wts = weights[idx] if weights is not None else None

        # step: center the remaining distribution by deducting the median of the remaining data
        #       to remove the impact of potential wage growth trend
        # note: set `datMid` to 0 de facto disables the de-meaning and centering step
        if isinstance(symmetry_type, str):
            if symmetry_type == 'median':
                datMid = float(np.median(dat)) if centering else 0.0
            elif symmetry_type == 'mean':
                datMid = float(np.mean(dat)) if centering else 0.0
            elif symmetry_type == 'weighted mean':
                datMid = float(np.average(dat, weights=wts)) if centering else 0.0
            else:
                raise ValueError(f"Invalid symmetry_type: {symmetry_type}. Must be one of 'median', 'mean', 'weighted mean', or a specific number.")
        elif isinstance(symmetry_type, (int, float)):
            datMid = float(symmetry_type) if centering else 0.0
        else:
            raise TypeError(f"Invalid type for symmetry_type: {type(symmetry_type)}. Must be a string or a numeric value.")
        self.datMid = datMid
        dat = dat - self.datMid

        # step: adjust range accordingly after centering
        xlimNew = (xlim[0] - self.datMid, xlim[1] - self.datMid)

        # step: make the histogram estimator and fit to the centered distribution
        self.hist_estimator = KinkHistogram(
            kink_point = 0.0, # called kink point but actually is the median point after centering; for API re-use purpose
            bin_width  = bin_width,
            xlim       = xlimNew
        )
        self.hist_estimator.fit(
            xvec    = dat,
            weights = wts,
            density = density
        )
        
        # step: fit the counterfactual distribution with Chebyshev regression
        data_cf = self.hist_estimator.hist_counterfactual()
        Xs_cf = data_cf["mid_points"]
        Ys_cf = data_cf["hist"]
        self.notional_dist_estimator = UnivariateChebRidgeRegression(
            degree = degree,
            alpha  = alpha,
            xlim   = xlimNew
        )
        if cv:
            self.notional_dist_estimator.fit_loocv(
                xvec = Xs_cf,
                yvec = Ys_cf,
                degree_grid = degree_grid,
                alpha_grid  = alpha_grid,
                scoring     = scoring
            )
        else:
            self.notional_dist_estimator.fit(Xs_cf, Ys_cf)       

        # step: compute the FWCP measure by integrating the mirror difference of the fitted notional distribution

        # type 1: weighted integral, int x * (f(2xmid-x) - f(x)) dx, simultaneously accounts for the quantity and the span of job cuts prevented
        self.fwcp_relative = -wtint_mirror(
            f = lambda x: self.notional_dist_estimator(x)[0],
            xmid = self.hist_estimator.kink_point,
            xmin = self.hist_estimator.xlim[0],
            xmax = self.hist_estimator.xlim[1],
            weighted_by_x = True,
            weight_shift  = self.datMid if use_original_x_for_weight else 0.0
        )

        # type 2: unweighted integral, int (f(2xmid-x) - f(x)) dx, only measures the quantity of job cuts prevented, without accounting for the span of the distribution
        self.fwcp_absolute = -wtint_mirror(
            f = lambda x: self.notional_dist_estimator(x)[0],
            xmid = self.hist_estimator.kink_point,
            xmin = self.hist_estimator.xlim[0],
            xmax = self.hist_estimator.xlim[1],
            weighted_by_x = False
        )

        return None

    def __str__(self):
        return (f"FWCPSymmetricEstimator(kink_point={self.hist_estimator.kink_point}, "
                f"bin_width={self.hist_estimator.bin_width}, "
                f"xlim={self.hist_estimator.xlim}, "
                f"median(no kink)={self.datMid}, "
                f"fwcp(unweighted)={self.fwcp_absolute}, "
                f"fwcp(weighted)={self.fwcp_relative})")

    def plotdata(self):
        """Not support yet
        """
        raise NotImplementedError("Plot data preparation for FWCPSymmetricEstimator is not implemented yet.")
    




