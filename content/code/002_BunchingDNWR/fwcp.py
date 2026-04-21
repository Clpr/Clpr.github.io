"""Unified tools for estimating the fraction of wage cuts prevented (FWCP).

This module merges the functionality of the legacy
`fwcp_bunch_and_symmetric.py` and `fwcp_hw2009.py` files into a single,
object-oriented interface while preserving their numerical behavior.

The package supports four practical estimator families:

1. Bunching around a kink or spike at zero wage growth.
2. Symmetry-based integration using the same sample.
3. Holden and Wulfsberg (2009) reference-sample estimators.
4. A simple rule-of-thumb symmetry-about-zero estimator.

Examples
--------
```python
import numpy as np
from fwcp import BunchingEstimator, SymmetricEstimator, HoldenWulfsberg2009Estimator

rng = np.random.default_rng(0)
data = np.concatenate([rng.normal(0.03, 0.12, 1200), rng.uniform(-0.01, 0.01, 80)])

bunch = BunchingEstimator(bin_width=0.02, xlim=(-0.5, 0.8)).fit(data)
print(bunch.fwcp_relative)

sym = SymmetricEstimator(bin_width=0.02, xlim=(-0.5, 0.8)).fit(data)
print(sym.fwcp_absolute, sym.fwcp_relative)

reference = rng.laplace(loc=0.05, scale=0.18, size=2500)
hw = HoldenWulfsberg2009Estimator(reference).fit(data)
print(hw.fwcp_frequency(), hw.fwcp_integral(weighted=False))
```
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Tuple, Union

import numpy as np
import scipy.integrate as integrate
from numpy.polynomial.chebyshev import chebvander
from scipy.stats import gaussian_kde
from sklearn.linear_model import Ridge, RidgeCV

ArrayLike1D = Union[Sequence[float], np.ndarray]


def _as_1d_array(x: ArrayLike1D, *, name: str) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    if arr.size == 0:
        raise ValueError(f"{name} must not be empty.")
    if np.isnan(arr).any():
        raise ValueError(f"{name} contains NaN values.")
    if np.isinf(arr).any():
        raise ValueError(f"{name} contains infinite values.")
    return arr


def _validate_xlim(xlim: Tuple[float, float]) -> Tuple[float, float]:
    if not isinstance(xlim, tuple) or len(xlim) != 2:
        raise ValueError("xlim must be a tuple of length 2.")
    xmin, xmax = float(xlim[0]), float(xlim[1])
    if xmin >= xmax:
        raise ValueError("xlim must satisfy xlim[0] < xlim[1].")
    return xmin, xmax


def _normalize_to_chebyshev_domain(xvec: np.ndarray, xlim: Tuple[float, float]) -> np.ndarray:
    xmin, xmax = xlim
    return (xvec - xmin) / (xmax - xmin) * 2.0 - 1.0


def normalize(xvec: np.ndarray, xlim: Tuple[float, float] = (-1.0, 1.0)) -> np.ndarray:
    """Backward-compatible alias for the legacy helper name."""
    return _normalize_to_chebyshev_domain(np.asarray(xvec, dtype=float), xlim)


def _validate_weights(xvec: np.ndarray, weights: Optional[ArrayLike1D]) -> Optional[np.ndarray]:
    if weights is None:
        return None
    arr = _as_1d_array(weights, name="weights")
    if arr.shape != xvec.shape:
        raise ValueError("weights must have the same shape as xvec.")
    if (arr < 0).any():
        raise ValueError("weights must be non-negative.")
    if arr.sum() <= 0:
        raise ValueError("weights must sum to a positive value.")
    return arr


def _is_in_01(x: float) -> bool:
    return 0.0 <= float(x) <= 1.0


def _validate_norm_quantiles(norm_qt: Tuple[float, float]) -> Tuple[float, float]:
    if not isinstance(norm_qt, tuple) or len(norm_qt) != 2:
        raise TypeError("norm_qt must be a tuple of two floats.")
    q0, q1 = float(norm_qt[0]), float(norm_qt[1])
    if not _is_in_01(q0) or not _is_in_01(q1):
        raise ValueError("norm_qt entries must be in [0, 1].")
    if q0 >= q1:
        raise ValueError("norm_qt[1] must be greater than norm_qt[0].")
    return q0, q1


def weighted_mirror_integral(
    f: Callable[[float], float],
    xmid: float,
    xmin: float,
    xmax: float,
    *,
    weighted_by_x: bool = False,
    weight_shift: float = 0.0,
) -> float:
    """Compute the mirror-difference integral used by symmetry estimators."""

    def f1(x: float) -> float:
        return float(f(x)) if xmin <= x <= xmax else 0.0

    def integrand(x: float) -> float:
        weight = abs(x + weight_shift) if weighted_by_x else (1.0 + weight_shift)
        return weight * (f1(2.0 * xmid - x) - f1(x))

    lower = min(xmin, 2.0 * xmid - xmax)
    upper = xmid
    result, _ = integrate.quad(integrand, lower, upper)
    return float(result)


def wtint_mirror(
    f: Callable[[float], float],
    xmid: float,
    xmin: float,
    xmax: float,
    weighted_by_x: bool = False,
    weight_shift: float = 0.0,
) -> float:
    """Backward-compatible alias for the legacy helper name."""
    return weighted_mirror_integral(
        f,
        xmid,
        xmin,
        xmax,
        weighted_by_x=weighted_by_x,
        weight_shift=weight_shift,
    )


@dataclass
class FWCPResult:
    """Container for common estimator outputs."""

    absolute: float
    relative: float
    method: str


class ChebyshevRidgeRegressor:
    """Univariate Chebyshev polynomial regression with ridge regularization.

    Examples
    --------
    ```python
    import numpy as np
    from fwcp import ChebyshevRidgeRegressor

    x = np.linspace(-1, 1, 200)
    y = np.sin(2 * x)
    model = ChebyshevRidgeRegressor(degree=12, alpha=1e-3, xlim=(-1, 1)).fit(x, y)
    y_hat = model.predict(x)
    ```
    """

    def __init__(self, degree: int = 20, alpha: float = 0.0, xlim: Tuple[float, float] = (-1.0, 1.0)):
        if not isinstance(degree, int) or degree < 0:
            raise ValueError("degree must be a non-negative integer.")
        if float(alpha) < 0:
            raise ValueError("alpha must be non-negative.")
        self.degree = int(degree)
        self.alpha = float(alpha)
        self.xlim = _validate_xlim(xlim)
        self.model: Optional[Ridge] = None
        self.best_score: Optional[float] = None
        self.best_score_name: Optional[str] = None

    def design_matrix(self, xvec: ArrayLike1D, degree: Optional[int] = None) -> np.ndarray:
        x = _as_1d_array(xvec, name="xvec")
        return chebvander(_normalize_to_chebyshev_domain(x, self.xlim), self.degree if degree is None else degree)

    def fit(self, xvec: ArrayLike1D, yvec: ArrayLike1D) -> "ChebyshevRidgeRegressor":
        x = _as_1d_array(xvec, name="xvec")
        y = _as_1d_array(yvec, name="yvec")
        if x.shape != y.shape:
            raise ValueError("xvec and yvec must have the same shape.")
        self.model = Ridge(alpha=self.alpha, fit_intercept=False)
        self.model.fit(self.design_matrix(x), y)
        return self

    def fit_loocv(
        self,
        xvec: ArrayLike1D,
        yvec: ArrayLike1D,
        *,
        degree_grid: Sequence[int] = tuple(range(10, 30)),
        alpha_grid: Sequence[float] = tuple(np.logspace(-4, 4, 100)),
        scoring: str = "neg_root_mean_squared_error",
    ) -> "ChebyshevRidgeRegressor":
        x = _as_1d_array(xvec, name="xvec")
        y = _as_1d_array(yvec, name="yvec")
        if x.shape != y.shape:
            raise ValueError("xvec and yvec must have the same shape.")

        full_dm = self.design_matrix(x)
        best_score = -np.inf
        best_degree: Optional[int] = None
        best_alpha: Optional[float] = None

        for deg in degree_grid:
            if int(deg) < 0:
                raise ValueError("degree_grid must contain non-negative integers.")
            cv_model = RidgeCV(
                alphas=np.asarray(alpha_grid, dtype=float),
                fit_intercept=False,
                scoring=scoring,
                cv=None,
                gcv_mode="auto",
                store_cv_results=False,
            ).fit(full_dm[:, : int(deg) + 1], y)
            if float(cv_model.best_score_) > best_score:
                best_score = float(cv_model.best_score_)
                best_degree = int(deg)
                best_alpha = float(cv_model.alpha_)

        if best_degree is None or best_alpha is None:
            raise RuntimeError("Cross-validation did not produce valid hyperparameters.")

        self.degree = best_degree
        self.alpha = best_alpha
        self.best_score = best_score
        self.best_score_name = scoring
        self.model = Ridge(alpha=self.alpha, fit_intercept=False)
        self.model.fit(self.design_matrix(x), y)
        return self

    def predict(self, xvec: ArrayLike1D) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model has not been fitted yet.")
        x = _as_1d_array(xvec, name="xvec")
        return self.model.predict(self.design_matrix(x))

    def __call__(self, xvec: ArrayLike1D) -> np.ndarray:
        return self.predict(xvec)


class KinkHistogram:
    """Histogram with a designated kink bin centered at `kink_point`."""

    def __init__(self, kink_point: float = 0.0, bin_width: float = 0.1, xlim: Tuple[float, float] = (-1.0, 1.0)):
        if float(bin_width) <= 0:
            raise ValueError("bin_width must be positive.")
        xmin, xmax = _validate_xlim(xlim)
        if not xmin <= float(kink_point) <= xmax:
            raise ValueError("kink_point must lie inside xlim.")

        self.kink_point = float(kink_point)
        self.bin_width = float(bin_width)
        self.xlim = (xmin, xmax)
        self.hist: Optional[np.ndarray] = None

        lb = self.kink_point - self.bin_width / 2.0
        ub = self.kink_point + self.bin_width / 2.0
        lb -= np.ceil((lb - xmin) / self.bin_width) * self.bin_width
        ub += np.ceil((xmax - ub) / self.bin_width) * self.bin_width

        self.bin_edges = np.arange(lb, ub + self.bin_width, self.bin_width)
        self.mid_points = (self.bin_edges[:-1] + self.bin_edges[1:]) / 2.0
        self.deviation_from_kink = np.round((self.mid_points - self.kink_point) / self.bin_width).astype(int)
        self.kink_bin_index = int((self.kink_point - lb) // self.bin_width)

    def fit(self, xvec: ArrayLike1D, weights: Optional[ArrayLike1D] = None, *, density: bool = True) -> "KinkHistogram":
        x = _as_1d_array(xvec, name="xvec")
        w = _validate_weights(x, weights)
        if w is None:
            w = np.ones_like(x)
        w = w / w.sum()

        self.hist = np.histogram(
            x,
            bins=self.bin_edges,
            weights=w,
            density=density,
            range=self.xlim,
        )[0]
        return self

    def counterfactual_data(self) -> dict:
        if self.hist is None:
            raise ValueError("Histogram has not been fitted yet.")
        return {
            "mid_points": np.delete(self.mid_points, self.kink_bin_index),
            "hist": np.delete(self.hist, self.kink_bin_index),
            "deviation_from_kink": np.delete(self.deviation_from_kink, self.kink_bin_index),
        }

    def hist_counterfactual(self) -> dict:
        """Backward-compatible alias."""
        return self.counterfactual_data()


class BaseFWCPEstimator:
    """Base class for unified estimator APIs."""

    method_name = "fwcp"

    def __init__(self) -> None:
        self.result: Optional[FWCPResult] = None

    @property
    def fwcp_absolute(self) -> float:
        if self.result is None:
            raise ValueError("Estimator has not been fitted yet.")
        return self.result.absolute

    @property
    def fwcp_relative(self) -> float:
        if self.result is None:
            raise ValueError("Estimator has not been fitted yet.")
        return self.result.relative

    def summary(self) -> FWCPResult:
        if self.result is None:
            raise ValueError("Estimator has not been fitted yet.")
        return self.result


class BunchingEstimator(BaseFWCPEstimator):
    """Bunching FWCP estimator based on a smoothed histogram counterfactual.

    Examples
    --------
    ```python
    import numpy as np
    from fwcp import BunchingEstimator

    rng = np.random.default_rng(1)
    x = np.concatenate([rng.normal(0.02, 0.12, 2000), rng.uniform(-0.01, 0.01, 100)])
    est = BunchingEstimator(bin_width=0.02, xlim=(-0.6, 0.8)).fit(x)
    print(est.fwcp_relative)
    ```
    """

    method_name = "bunching"

    def __init__(
        self,
        data: Optional[ArrayLike1D] = None,
        *,
        weights: Optional[ArrayLike1D] = None,
        kink_point: float = 0.0,
        bin_width: float = 0.02,
        xlim: Tuple[float, float] = (-1.0, 2.0),
        density: bool = True,
        degree: int = 20,
        alpha: float = 0.0,
        cv: bool = False,
        degree_grid: Sequence[int] = tuple(range(10, 30)),
        alpha_grid: Sequence[float] = tuple(np.logspace(-4, 4, 100)),
        scoring: str = "neg_root_mean_squared_error",
    ):
        super().__init__()
        self.weights = weights
        self.kink_point = float(kink_point)
        self.bin_width = float(bin_width)
        self.xlim = _validate_xlim(xlim)
        self.density = bool(density)
        self.degree = int(degree)
        self.alpha = float(alpha)
        self.cv = bool(cv)
        self.degree_grid = degree_grid
        self.alpha_grid = alpha_grid
        self.scoring = scoring

        self.hist_estimator: Optional[KinkHistogram] = None
        self.notional_dist_estimator: Optional[ChebyshevRidgeRegressor] = None
        self.kink_mass_actual: Optional[float] = None
        self.kink_mass_notional: Optional[float] = None

        if data is not None:
            self.fit(data, weights=weights)

    def fit(self, data: ArrayLike1D, weights: Optional[ArrayLike1D] = None) -> "BunchingEstimator":
        x = _as_1d_array(data, name="data")
        w = self.weights if weights is None else weights

        self.hist_estimator = KinkHistogram(
            kink_point=self.kink_point,
            bin_width=self.bin_width,
            xlim=self.xlim,
        ).fit(x, weights=w, density=self.density)

        cf = self.hist_estimator.counterfactual_data()
        self.notional_dist_estimator = ChebyshevRidgeRegressor(
            degree=self.degree,
            alpha=self.alpha,
            xlim=self.xlim,
        )
        if self.cv:
            self.notional_dist_estimator.fit_loocv(
                cf["mid_points"],
                cf["hist"],
                degree_grid=self.degree_grid,
                alpha_grid=self.alpha_grid,
                scoring=self.scoring,
            )
        else:
            self.notional_dist_estimator.fit(cf["mid_points"], cf["hist"])

        self.kink_mass_actual = float(self.hist_estimator.hist[self.hist_estimator.kink_bin_index])
        self.kink_mass_notional = float(self.notional_dist_estimator.predict(np.array([self.kink_point]))[0])
        absolute = self.kink_mass_actual - self.kink_mass_notional
        relative = absolute / self.kink_mass_actual if self.kink_mass_actual != 0 else np.nan
        self.result = FWCPResult(absolute=absolute, relative=relative, method=self.method_name)
        return self

    def plotdata(self) -> dict:
        if self.hist_estimator is None or self.notional_dist_estimator is None:
            raise ValueError("Estimator has not been fitted yet.")
        return {
            "x": self.hist_estimator.mid_points,
            "y_actual": self.hist_estimator.hist,
            "y_notional": self.notional_dist_estimator.predict(self.hist_estimator.mid_points),
            "kink_point": self.kink_point,
            "kink_mass_actual": self.kink_mass_actual,
            "kink_mass_notional": self.kink_mass_notional,
            "bin_width": self.bin_width,
        }

    def __str__(self) -> str:
        return (
            f"BunchingEstimator(kink_point={self.kink_point}, bin_width={self.bin_width}, "
            f"xlim={self.xlim}, fwcp_absolute={self.fwcp_absolute}, fwcp_relative={self.fwcp_relative})"
        )


class SymmetricEstimator(BaseFWCPEstimator):
    """Same-sample symmetry FWCP estimator using mirrored density differences.

    Examples
    --------
    ```python
    import numpy as np
    from fwcp import SymmetricEstimator

    rng = np.random.default_rng(2)
    x = np.concatenate([rng.normal(0.01, 0.09, 1500), rng.uniform(-0.01, 0.01, 60)])
    est = SymmetricEstimator(bin_width=0.02, xlim=(-0.5, 0.7), symmetry_type="median").fit(x)
    print(est.fwcp_absolute, est.fwcp_relative)
    ```
    """

    method_name = "symmetric"

    def __init__(
        self,
        data: Optional[ArrayLike1D] = None,
        *,
        weights: Optional[ArrayLike1D] = None,
        kink_point: float = 0.0,
        bin_width: float = 0.02,
        xlim: Tuple[float, float] = (-1.0, 2.0),
        density: bool = True,
        degree: int = 20,
        alpha: float = 0.0,
        cv: bool = False,
        degree_grid: Sequence[int] = tuple(range(10, 30)),
        alpha_grid: Sequence[float] = tuple(np.logspace(-4, 4, 100)),
        scoring: str = "neg_root_mean_squared_error",
        symmetry_type: Union[str, float] = "median",
        centering: bool = True,
        use_original_x_for_weight: bool = False,
    ):
        super().__init__()
        self.weights = weights
        self.kink_point = float(kink_point)
        self.bin_width = float(bin_width)
        self.xlim = _validate_xlim(xlim)
        self.density = bool(density)
        self.degree = int(degree)
        self.alpha = float(alpha)
        self.cv = bool(cv)
        self.degree_grid = degree_grid
        self.alpha_grid = alpha_grid
        self.scoring = scoring
        self.symmetry_type = symmetry_type
        self.centering = bool(centering)
        self.use_original_x_for_weight = bool(use_original_x_for_weight)

        self.datMid: Optional[float] = None
        self.hist_estimator: Optional[KinkHistogram] = None
        self.notional_dist_estimator: Optional[ChebyshevRidgeRegressor] = None

        if data is not None:
            self.fit(data, weights=weights)

    def _compute_center(self, data: np.ndarray, weights: Optional[np.ndarray]) -> float:
        if isinstance(self.symmetry_type, str):
            if self.symmetry_type == "median":
                return float(np.median(data)) if self.centering else 0.0
            if self.symmetry_type == "mean":
                return float(np.mean(data)) if self.centering else 0.0
            if self.symmetry_type == "weighted mean":
                return float(np.average(data, weights=weights)) if self.centering else 0.0
            raise ValueError("symmetry_type must be 'median', 'mean', 'weighted mean', or a numeric value.")
        if isinstance(self.symmetry_type, (int, float)):
            return float(self.symmetry_type) if self.centering else 0.0
        raise TypeError("symmetry_type must be a string or numeric value.")

    def fit(self, data: ArrayLike1D, weights: Optional[ArrayLike1D] = None) -> "SymmetricEstimator":
        x = _as_1d_array(data, name="data")
        w = _validate_weights(x, self.weights if weights is None else weights)

        idx = (np.abs(x - self.kink_point) > self.bin_width / 2.0) & (self.xlim[0] <= x) & (x <= self.xlim[1])
        dat = x[idx]
        if dat.size == 0:
            raise ValueError("No observations remain after removing the kink bin and applying xlim.")
        w_fit = w[idx] if w is not None else None

        self.datMid = self._compute_center(dat, w_fit)
        centered = dat - self.datMid
        xlim_new = (self.xlim[0] - self.datMid, self.xlim[1] - self.datMid)

        self.hist_estimator = KinkHistogram(kink_point=0.0, bin_width=self.bin_width, xlim=xlim_new).fit(
            centered, weights=w_fit, density=self.density
        )
        cf = self.hist_estimator.counterfactual_data()
        self.notional_dist_estimator = ChebyshevRidgeRegressor(
            degree=self.degree,
            alpha=self.alpha,
            xlim=xlim_new,
        )
        if self.cv:
            self.notional_dist_estimator.fit_loocv(
                cf["mid_points"],
                cf["hist"],
                degree_grid=self.degree_grid,
                alpha_grid=self.alpha_grid,
                scoring=self.scoring,
            )
        else:
            self.notional_dist_estimator.fit(cf["mid_points"], cf["hist"])

        weighted_value = -weighted_mirror_integral(
            f=lambda z: self.notional_dist_estimator.predict(np.array([z]))[0],
            xmid=self.hist_estimator.kink_point,
            xmin=self.hist_estimator.xlim[0],
            xmax=self.hist_estimator.xlim[1],
            weighted_by_x=True,
            weight_shift=self.datMid if self.use_original_x_for_weight else 0.0,
        )
        unweighted_value = -weighted_mirror_integral(
            f=lambda z: self.notional_dist_estimator.predict(np.array([z]))[0],
            xmid=self.hist_estimator.kink_point,
            xmin=self.hist_estimator.xlim[0],
            xmax=self.hist_estimator.xlim[1],
            weighted_by_x=False,
        )
        self.result = FWCPResult(absolute=unweighted_value, relative=weighted_value, method=self.method_name)
        return self

    def plotdata(self) -> dict:
        if self.hist_estimator is None or self.notional_dist_estimator is None or self.datMid is None:
            raise ValueError("Estimator has not been fitted yet.")
        x_centered = self.hist_estimator.mid_points
        return {
            "x_centered": x_centered,
            "x_original": x_centered + self.datMid,
            "y_actual": self.hist_estimator.hist,
            "y_notional": self.notional_dist_estimator.predict(x_centered),
            "center": self.datMid,
            "bin_width": self.bin_width,
        }

    def __str__(self) -> str:
        return (
            f"SymmetricEstimator(bin_width={self.bin_width}, xlim={self.xlim}, center={self.datMid}, "
            f"fwcp_absolute={self.fwcp_absolute}, fwcp_relative={self.fwcp_relative})"
        )


class HoldenWulfsberg2009Estimator(BaseFWCPEstimator):
    """FWCP estimators based on Holden and Wulfsberg (2009).

    The estimator first builds a normalized notional distribution from a
    reference sample, then rescales it to match the observed sample's median and
    inter-quantile dispersion.

    Examples
    --------
    ```python
    import numpy as np
    from fwcp import HoldenWulfsberg2009Estimator

    rng = np.random.default_rng(3)
    ref = rng.laplace(0.05, 0.2, 2000)
    obs = rng.normal(0.01, 0.1, 500)

    hw = HoldenWulfsberg2009Estimator(ref).fit(obs)
    print(hw.fwcp_frequency())
    print(hw.fwcp_integral(weighted=False))
    ```
    """

    method_name = "hw2009"

    def __init__(
        self,
        ref_data: ArrayLike1D,
        *,
        top_cut: float = 0.25,
        norm_qt: Tuple[float, float] = (0.35, 0.75),
    ):
        super().__init__()
        self.ref_data = _as_1d_array(ref_data, name="ref_data")
        self.top_cut = float(top_cut)
        self.norm_qt = _validate_norm_quantiles(norm_qt)
        if not _is_in_01(self.top_cut):
            raise ValueError("top_cut must be in [0, 1].")

        top = self.ref_data[self.ref_data >= np.quantile(self.ref_data, 1.0 - self.top_cut)]
        if top.size == 0:
            raise ValueError("Reference sample produced an empty top-cut subsample.")
        mid = float(top.min())
        mirrored = np.concatenate((top, 2.0 * mid - top), axis=0)
        scale = float(np.quantile(mirrored, self.norm_qt[1]) - np.quantile(mirrored, self.norm_qt[0]))
        if scale == 0:
            raise ValueError("Reference distribution has zero normalization scale.")

        self.datNotional = (mirrored - mid) / scale
        self.observed_data: Optional[np.ndarray] = None
        self._rescaled_notional: Optional[np.ndarray] = None
        self._obs_quantiles: Optional[np.ndarray] = None
        self._obs_mid: Optional[float] = None

    def rescale(self, locPar: float, scalePar: float) -> np.ndarray:
        return self.datNotional * float(scalePar) + float(locPar)

    def fit(self, observed_data: ArrayLike1D) -> "HoldenWulfsberg2009Estimator":
        obs = _as_1d_array(observed_data, name="observed_data")
        qt = np.quantile(obs, self.norm_qt)
        mid = float(np.median(obs))
        self.observed_data = obs
        self._obs_quantiles = qt
        self._obs_mid = mid
        self._rescaled_notional = self.rescale(mid, float(qt[1] - qt[0]))

        self.result = FWCPResult(
            absolute=self.fwcp_integral(weighted=False),
            relative=self.fwcp_frequency(),
            method=self.method_name,
        )
        return self

    def rescale_dat(self, datObs: ArrayLike1D) -> Tuple[np.ndarray, np.ndarray, float]:
        obs = _as_1d_array(datObs, name="datObs")
        qt = np.quantile(obs, self.norm_qt)
        mid = float(np.median(obs))
        return self.rescale(mid, float(qt[1] - qt[0])), qt, mid

    def _require_fit(self) -> Tuple[np.ndarray, np.ndarray]:
        if self.observed_data is None or self._rescaled_notional is None:
            raise ValueError("Estimator has not been fitted to observed data yet.")
        return self.observed_data, self._rescaled_notional

    def fwcp_frequency(self, observed_data: Optional[ArrayLike1D] = None) -> float:
        if observed_data is None:
            obs, notion = self._require_fit()
        else:
            obs = _as_1d_array(observed_data, name="observed_data")
            notion, _, _ = self.rescale_dat(obs)

        p_actual = float(np.mean(obs < 0))
        p_notion = float(np.mean(notion < 0))
        return float(1.0 - p_actual / p_notion) if p_notion != 0 else -np.inf

    def fwcp_integral(
        self,
        observed_data: Optional[ArrayLike1D] = None,
        *,
        weighted: bool = True,
        bw_method: str = "scott",
    ) -> float:
        if observed_data is None:
            obs, notion = self._require_fit()
            ub = float(self._obs_mid)
        else:
            obs = _as_1d_array(observed_data, name="observed_data")
            notion, _, ub = self.rescale_dat(obs)

        lb = float(min(obs.min(), notion.min()))
        kde_actual = gaussian_kde(obs, bw_method=bw_method)
        kde_notion = gaussian_kde(notion, bw_method=bw_method)

        def integrand(x: float) -> float:
            wt = abs(x) if weighted else 1.0
            return wt * (kde_notion.evaluate(x)[0] - kde_actual.evaluate(x)[0])

        return float(integrate.quad(integrand, lb, ub)[0])

    def fwcp_freq(self, datObs: Optional[ArrayLike1D] = None) -> float:
        """Backward-compatible alias for the legacy frequency method name."""
        return self.fwcp_frequency(datObs)

    def fwcp_int(
        self,
        datObs: Optional[ArrayLike1D] = None,
        weighted: bool = True,
        bw_method: str = "scott",
    ) -> float:
        """Backward-compatible alias for the legacy integral method name."""
        return self.fwcp_integral(datObs, weighted=weighted, bw_method=bw_method)

    def plotdata(self, grid_size: int = 400, *, bw_method: str = "scott") -> dict:
        obs, notion = self._require_fit()
        xmin = float(min(obs.min(), notion.min()))
        xmax = float(max(obs.max(), notion.max()))
        grid = np.linspace(xmin, xmax, int(grid_size))
        kde_actual = gaussian_kde(obs, bw_method=bw_method)
        kde_notion = gaussian_kde(notion, bw_method=bw_method)
        return {
            "x": grid,
            "y_actual": kde_actual(grid),
            "y_notional": kde_notion(grid),
            "center": self._obs_mid,
        }

    def __str__(self) -> str:
        return (
            f"HoldenWulfsberg2009Estimator(top_cut={self.top_cut}, norm_qt={self.norm_qt}, "
            f"fwcp_frequency={self.fwcp_relative}, fwcp_unweighted_integral={self.fwcp_absolute})"
        )


class RuleOfThumbEstimator(BaseFWCPEstimator):
    """Simple symmetry-about-zero FWCP estimator: 1 - 2 * q(0)."""

    method_name = "rule_of_thumb"

    def fit(self, data: ArrayLike1D) -> "RuleOfThumbEstimator":
        x = _as_1d_array(data, name="data")
        q0 = float(np.mean(x <= 0))
        value = float(1.0 - 2.0 * q0)
        self.result = FWCPResult(absolute=value, relative=value, method=self.method_name)
        return self


# Backward-compatible aliases for the legacy class names.
UnivariateChebRidgeRegression = ChebyshevRidgeRegressor
FWCPBunchingEstimator = BunchingEstimator
FWCPSymmetricEstimator = SymmetricEstimator
HoldenWulfsberg2009 = HoldenWulfsberg2009Estimator


__all__ = [
    "FWCPResult",
    "ChebyshevRidgeRegressor",
    "UnivariateChebRidgeRegression",
    "KinkHistogram",
    "BunchingEstimator",
    "FWCPBunchingEstimator",
    "SymmetricEstimator",
    "FWCPSymmetricEstimator",
    "HoldenWulfsberg2009Estimator",
    "HoldenWulfsberg2009",
    "RuleOfThumbEstimator",
    "normalize",
    "wtint_mirror",
    "weighted_mirror_integral",
]
