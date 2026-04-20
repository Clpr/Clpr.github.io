r"""distributional_regression_pdf
================================

Single-file implementation of a sieve-based conditional density estimator for
distributional regression.

The main public entry point is :class:`DistributionalRegressionPDF`, which fits
the conditional density of a scalar outcome ``y`` given covariates ``X`` using
a normalized log-density representation

.. math::

    \log f(y \mid x) = \eta(y, x) - \log Z(x),

where

.. math::

    Z(x) = \int_{\mathcal{Y}} \exp(\eta(u, x)) \, du.

The implementation uses Chebyshev polynomial sieve bases, numerical
normalization via Gauss-Legendre quadrature, penalized maximum likelihood, and
optional cross-validation over regularization strengths.

The module is designed to be self-contained and researcher-friendly:

- one file
- NumPy / SciPy / scikit-learn / joblib based
- no hidden global state
- fully documented public API
- synthetic demonstration under ``if __name__ == "__main__":``

Notes on identifiability
------------------------
Because the density is normalized separately for each ``x``, any term in
``eta(y, x)`` that depends only on ``x`` or is a global intercept cancels out
of ``f(y|x)``. The fitted parameterization therefore keeps only terms that vary
with ``y``:

- marginal Chebyshev terms in ``y``
- interactions between ``y`` basis terms and feature-wise Chebyshev bases
- optional interactions between ``y`` basis terms and pairwise feature-basis
  products

This is slightly different from a naïve raw tensor expansion that includes
``x``-only terms, but it is the identifiable version of the normalized density
model.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Sequence
import warnings

import joblib
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import minimize
from scipy.special import logsumexp
from sklearn.model_selection import KFold

try:
    import pandas as pd
except ImportError:  # pragma: no cover - optional dependency
    pd = None


ArrayLike = Any


@dataclass(frozen=True)
class _AffineScaler:
    """Affine map for a single variable."""

    lower: float
    upper: float
    scale_to_unit: bool
    is_constant: bool = False

    @property
    def span(self) -> float:
        return float(self.upper - self.lower)

    @property
    def midpoint(self) -> float:
        return 0.5 * (self.lower + self.upper)

    def transform(self, values: np.ndarray) -> np.ndarray:
        arr = np.asarray(values, dtype=float)
        if not self.scale_to_unit:
            return arr.copy()
        if self.is_constant or self.span <= 0.0:
            return np.zeros_like(arr, dtype=float)
        return 2.0 * (arr - self.lower) / self.span - 1.0


@dataclass(frozen=True)
class _QuadratureRule:
    """Quadrature nodes and weights on the raw y-domain."""

    nodes: np.ndarray
    weights: np.ndarray
    log_weights: np.ndarray


def _check_rng(rng: int | np.random.Generator | None) -> np.random.Generator:
    """Return a NumPy generator."""

    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(rng)


def _iqr_scaled_std(y: np.ndarray) -> float:
    """Robust scale estimate based on std and IQR."""

    y = np.asarray(y, dtype=float)
    std = float(np.std(y, ddof=1)) if y.size > 1 else 0.0
    q75, q25 = np.percentile(y, [75.0, 25.0])
    iqr_scale = float((q75 - q25) / 1.349)
    return max(std, iqr_scale, 1e-8)


def _make_feature_names(X: ArrayLike, n_features: int) -> list[str]:
    """Derive feature names from pandas objects when available."""

    if pd is not None and isinstance(X, pd.DataFrame):
        return [str(col) for col in X.columns]
    return [f"x{idx}" for idx in range(n_features)]


def _as_1d_float_array(y: ArrayLike, name: str = "y") -> np.ndarray:
    """Convert inputs to a finite 1D float array."""

    if pd is not None and isinstance(y, (pd.Series, pd.Index)):
        arr = y.to_numpy(dtype=float)
    else:
        arr = np.asarray(y, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional array-like object.")
    if arr.size == 0:
        raise ValueError(f"{name} must not be empty.")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains missing or non-finite values.")
    return arr


def _as_2d_float_array(X: ArrayLike, name: str = "X") -> np.ndarray:
    """Convert inputs to a finite 2D float array."""

    if pd is not None and isinstance(X, pd.DataFrame):
        arr = X.to_numpy(dtype=float)
    else:
        arr = np.asarray(X, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be a two-dimensional array-like object.")
    if arr.shape[0] == 0 or arr.shape[1] == 0:
        raise ValueError(f"{name} must have positive shape in both dimensions.")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains missing or non-finite values.")
    return arr


def _chebyshev_nonconstant_basis(values: np.ndarray, degree: int) -> np.ndarray:
    """Evaluate non-constant Chebyshev basis terms T1..Td."""

    arr = np.asarray(values, dtype=float).reshape(-1)
    if degree <= 0:
        return np.empty((arr.size, 0), dtype=float)
    basis = np.empty((arr.size, degree), dtype=float)
    basis[:, 0] = arr
    if degree == 1:
        return basis
    t_prev = np.ones_like(arr)
    t_curr = arr.copy()
    for idx in range(2, degree + 1):
        t_next = 2.0 * arr * t_curr - t_prev
        basis[:, idx - 1] = t_next
        t_prev, t_curr = t_curr, t_next
    return basis


class DistributionalRegressionPDF:
    r"""Sieve-based conditional density estimator for distributional regression.

    Parameters
    ----------
    basis : str, default="chebyshev"
        Basis family for the sieve expansion. Version 1 supports only
        ``"chebyshev"``.
    degree_y : int, default=6
        Maximum degree for the non-constant outcome basis ``T_1(y), ..., T_d(y)``.
        Larger values increase flexibility but also the number of parameters and
        the need for regularization.
    degree_x : int, default=3
        Maximum degree for each feature-wise non-constant Chebyshev basis used
        inside interactions with the outcome basis.
    include_interactions : bool, default=True
        Whether to allow feature-dependent conditional shapes via interactions
        between the ``y`` basis and the ``X`` basis.
    x_interaction_order : int, default=2
        Order of covariate interactions inside the coefficient functions on
        ``y``. ``1`` includes feature-wise ``y:x_j`` interactions. ``2`` also
        includes ``y:x_j:x_l`` terms constructed as ``y`` basis terms times
        pairwise feature-basis products. These are the identifiable analogue of
        pairwise covariate interaction effects in the normalized log-density.
    y_domain : tuple[float, float] or None, default=None
        Integration domain for ``y`` in raw outcome units. When ``None``, the
        domain is inferred from the data with padding.
    y_domain_padding : float, default=0.15
        Padding multiplier used when ``y_domain`` is inferred:

        ``pad = y_domain_padding * max(std(y), IQR(y)/1.349, 1e-8)``.
    n_integration_nodes : int, default=64
        Number of Gauss-Legendre quadrature nodes for the normalizing integral.
    integration_method : str, default="gauss-legendre"
        Numerical integration method. Version 1 supports only
        ``"gauss-legendre"``.
    standardize_X : bool, default=True
        If ``True``, each feature is affinely mapped from its training range to
        ``[-1, 1]``. The transform is stored and reused at prediction time.
    standardize_y : bool, default=True
        If ``True``, raw ``y`` values inside the integration domain are affinely
        mapped to ``[-1, 1]`` before Chebyshev basis evaluation. The returned
        density remains in raw ``y`` units because normalization is done over
        the original domain.
    fit_intercept : bool, default=True
        Included for API familiarity. In normalized conditional density models,
        a pure intercept is not identifiable and is therefore omitted from the
        optimization.
    optimizer : str, default="L-BFGS-B"
        Optimizer passed to :func:`scipy.optimize.minimize`.
    max_iter : int, default=500
        Maximum optimizer iterations.
    tol : float, default=1e-6
        Optimization tolerance.
    verbose : int, default=0
        Verbosity level used in fitting and summary diagnostics.

    Conceptual overview
    -------------------
    The estimator approximates the conditional log-density through a finite
    sieve expansion and turns it into a proper conditional density by numerical
    normalization:

    .. math::

        f(y|x) = \frac{\exp(\eta(y, x))}{
            \int_{\mathcal{Y}} \exp(\eta(u, x)) \, du }.

    This construction allows asymmetric and right-skewed conditional densities
    without imposing Gaussianity or a location-scale restriction.

    Basis handling
    --------------
    Chebyshev support is mandatory in this implementation. The model uses:

    - marginal ``y`` basis terms
    - feature-wise ``y:x_j`` interaction blocks
    - optional pairwise ``y:x_j:x_l`` interaction blocks when
      ``x_interaction_order=2``

    Terms that depend only on ``x`` are excluded because they cancel after
    normalization and cannot be identified separately.

    Automatic data transformation and stored ranges
    -----------------------------------------------
    When ``standardize_X=True``, each feature column is mapped from its observed
    training min/max to ``[-1, 1]`` and the original range is stored in the
    fitted object. Nearly constant columns are flagged and excluded from the
    interaction basis to avoid unstable or redundant parameters.

    When ``standardize_y=True``, the raw integration domain is mapped to
    ``[-1, 1]`` for basis evaluation. The density itself is still normalized
    over the original raw ``y`` domain, so ``pdf`` returns values in the
    original outcome units.

    Regularization
    --------------
    The objective is penalized conditional log-likelihood with optional L1 and
    L2 penalties. The L1 term is implemented with a smooth approximation

    ``sum(sqrt(beta**2 + eps_l1))``

    so that gradients remain stable under quasi-Newton optimization.

    Numerical integration and normalization
    ---------------------------------------
    Normalizing constants ``Z(x)`` are computed by Gauss-Legendre quadrature
    over the modeled raw ``y`` domain. The implementation uses a log-sum-exp
    form with quadrature weights to remain stable.

    Assumptions and limitations
    ---------------------------
    - The outcome support is truncated to a finite domain determined either by
      ``y_domain`` or by the observed sample plus padding.
    - Predictions outside the fitted ``y`` domain return ``0`` for ``pdf`` and
      ``-inf`` for ``logpdf``.
    - Extrapolation in ``X`` is allowed but a warning is issued when transformed
      values are materially outside the training support.
    - Version 1 supports only the Chebyshev basis and one scalar outcome.

    Output
    ------
    Fitted objects store coefficients, parameter names, scaling metadata,
    integration settings, cross-validation results, optimizer diagnostics, and
    summary statistics such as in-sample mean log-likelihood.

    Examples
    --------
    Basic usage:

    >>> import numpy as np
    >>> rng = np.random.default_rng(123)
    >>> X = rng.normal(size=(300, 2))
    >>> tail = rng.lognormal(mean=0.2 * X[:, 0], sigma=0.35 + 0.15 * (X[:, 1] > 0))
    >>> y = 0.5 * np.sin(X[:, 0]) - 0.3 * X[:, 1] + tail
    >>> mod = DistributionalRegressionPDF(
    ...     basis="chebyshev",
    ...     degree_y=5,
    ...     degree_x=2,
    ...     include_interactions=True,
    ... )
    >>> mod.fit(y, X, l2_alpha=1e-3)
    DistributionalRegressionPDF(...)
    >>> float(mod(1.0, X[0]))
    ...

    User-style API:

    >>> mod = DistributionalRegressionPDF(basis="chebyshev", degree_y=6, degree_x=3)
    >>> mod.fit(
    ...     y,
    ...     X,
    ...     l1_alpha=1e-4,
    ...     l2_alpha=1e-3,
    ...     cv=True,
    ...     folds=5,
    ...     rng=1234,
    ...     showtrace=False,
    ... )
    DistributionalRegressionPDF(...)
    >>> pdf_val = mod.pdf(1.25, X[10])
    >>> text = mod.summary()
    >>> mod.save("distributional_model.joblib")
    >>> loaded = DistributionalRegressionPDF.load("distributional_model.joblib")
    >>> np.allclose(loaded.pdf(1.25, X[10]), pdf_val)
    True

    Optional density plotting example:

    >>> x_profile = np.array([0.0, 1.0])
    >>> grid = np.linspace(mod.y_domain_[0], mod.y_domain_[1], 200)
    >>> vals = mod.pdf(grid, x_profile)
    >>> vals.shape
    (200,)
    """

    def __init__(
        self,
        basis: str = "chebyshev",
        degree_y: int = 6,
        degree_x: int = 3,
        include_interactions: bool = True,
        x_interaction_order: int = 2,
        y_domain: tuple[float, float] | None = None,
        y_domain_padding: float = 0.15,
        n_integration_nodes: int = 64,
        integration_method: str = "gauss-legendre",
        standardize_X: bool = True,
        standardize_y: bool = True,
        fit_intercept: bool = True,
        optimizer: str = "L-BFGS-B",
        max_iter: int = 500,
        tol: float = 1e-6,
        verbose: int = 0,
    ) -> None:
        if basis.lower() != "chebyshev":
            raise ValueError("Only basis='chebyshev' is supported in this version.")
        if integration_method.lower() != "gauss-legendre":
            raise ValueError(
                "Only integration_method='gauss-legendre' is supported in this version."
            )
        if not isinstance(degree_y, int) or degree_y < 1:
            raise ValueError("degree_y must be an integer greater than or equal to 1.")
        if not isinstance(degree_x, int) or degree_x < 0:
            raise ValueError("degree_x must be an integer greater than or equal to 0.")
        if x_interaction_order not in (1, 2):
            raise ValueError("x_interaction_order must be either 1 or 2.")
        if n_integration_nodes < 8:
            raise ValueError("n_integration_nodes must be at least 8.")
        if y_domain is not None:
            if len(y_domain) != 2 or not np.all(np.isfinite(y_domain)):
                raise ValueError("y_domain must be a finite tuple (lower, upper).")
            if float(y_domain[1]) <= float(y_domain[0]):
                raise ValueError("y_domain must satisfy upper > lower.")
        if y_domain_padding < 0:
            raise ValueError("y_domain_padding must be non-negative.")

        self.basis = basis.lower()
        self.degree_y = degree_y
        self.degree_x = degree_x
        self.include_interactions = bool(include_interactions)
        self.x_interaction_order = x_interaction_order
        self.y_domain = (
            None if y_domain is None else (float(y_domain[0]), float(y_domain[1]))
        )
        self.y_domain_padding = float(y_domain_padding)
        self.n_integration_nodes = int(n_integration_nodes)
        self.integration_method = integration_method.lower()
        self.standardize_X = bool(standardize_X)
        self.standardize_y = bool(standardize_y)
        self.fit_intercept = bool(fit_intercept)
        self.optimizer = optimizer
        self.max_iter = int(max_iter)
        self.tol = float(tol)
        self.verbose = int(verbose)

    def _get_init_params(self) -> dict[str, Any]:
        """Return constructor parameters for cloning."""

        return {
            "basis": self.basis,
            "degree_y": self.degree_y,
            "degree_x": self.degree_x,
            "include_interactions": self.include_interactions,
            "x_interaction_order": self.x_interaction_order,
            "y_domain": self.y_domain,
            "y_domain_padding": self.y_domain_padding,
            "n_integration_nodes": self.n_integration_nodes,
            "integration_method": self.integration_method,
            "standardize_X": self.standardize_X,
            "standardize_y": self.standardize_y,
            "fit_intercept": self.fit_intercept,
            "optimizer": self.optimizer,
            "max_iter": self.max_iter,
            "tol": self.tol,
            "verbose": self.verbose,
        }

    def _make_clone(self, y_domain_override: tuple[float, float] | None = None) -> "DistributionalRegressionPDF":
        """Create a fresh model with the same constructor arguments."""

        params = self._get_init_params()
        if y_domain_override is not None:
            params["y_domain"] = y_domain_override
        return self.__class__(**params)

    def _infer_y_domain(self, y: np.ndarray) -> tuple[float, float]:
        """Infer the raw y-domain from the data."""

        if self.y_domain is not None:
            return self.y_domain
        y = np.asarray(y, dtype=float)
        scale = _iqr_scaled_std(y)
        pad = self.y_domain_padding * scale
        lower = float(np.min(y) - pad)
        upper = float(np.max(y) + pad)
        if upper <= lower:
            upper = lower + max(scale, 1.0)
        return (lower, upper)

    def _fit_x_scalers(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Fit feature-wise scaling metadata and return transformed X."""

        n_features = X.shape[1]
        x_lower = np.min(X, axis=0)
        x_upper = np.max(X, axis=0)
        x_span = x_upper - x_lower
        feature_scale = np.maximum(np.max(np.abs(X), axis=0), 1.0)
        constant_mask = x_span <= (1e-10 * feature_scale)
        x_scaled = np.zeros_like(X, dtype=float)

        if self.standardize_X:
            nonconstant = ~constant_mask
            if np.any(nonconstant):
                x_scaled[:, nonconstant] = (
                    2.0
                    * (X[:, nonconstant] - x_lower[nonconstant])
                    / x_span[nonconstant]
                    - 1.0
                )
        else:
            x_scaled = X.astype(float, copy=True)

        self.x_lower_ = x_lower
        self.x_upper_ = x_upper
        self.x_span_ = x_span
        self.constant_feature_mask_ = constant_mask
        self.active_feature_mask_ = ~constant_mask
        self.n_constant_features_ = int(np.sum(constant_mask))
        return x_scaled, np.flatnonzero(self.active_feature_mask_)

    def _transform_X(self, X: np.ndarray, warn_on_extrapolation: bool = False) -> np.ndarray:
        """Apply stored X transform."""

        self._check_is_fitted()
        X = np.asarray(X, dtype=float)
        if X.shape[1] != self.n_features_in_:
            raise ValueError(
                f"Expected X with {self.n_features_in_} columns, got {X.shape[1]}."
            )

        if self.standardize_X:
            scaled = np.zeros_like(X, dtype=float)
            nonconstant = ~self.constant_feature_mask_
            if np.any(nonconstant):
                scaled[:, nonconstant] = (
                    2.0
                    * (X[:, nonconstant] - self.x_lower_[nonconstant])
                    / self.x_span_[nonconstant]
                    - 1.0
                )
            if warn_on_extrapolation and np.any(np.abs(scaled[:, nonconstant]) > 1.05):
                warnings.warn(
                    "Prediction covariates extend materially beyond the training "
                    "support used for scaling. Extrapolation is being used.",
                    RuntimeWarning,
                    stacklevel=3,
                )
            return scaled

        if warn_on_extrapolation and np.any(np.abs(X) > 1.05):
            warnings.warn(
                "standardize_X=False with Chebyshev bases can be numerically fragile "
                "when covariates lie outside [-1, 1].",
                RuntimeWarning,
                stacklevel=3,
            )
        return X.astype(float, copy=True)

    def _fit_y_scaler(self, y_domain: tuple[float, float]) -> None:
        """Store y-domain and scaler metadata."""

        self.y_domain_ = (float(y_domain[0]), float(y_domain[1]))
        self.y_scaler_ = _AffineScaler(
            lower=self.y_domain_[0],
            upper=self.y_domain_[1],
            scale_to_unit=self.standardize_y,
            is_constant=False,
        )

    def _transform_y(self, y: np.ndarray) -> np.ndarray:
        """Apply stored y transform."""

        self._check_is_fitted()
        return self.y_scaler_.transform(y)

    def _build_quadrature_rule(self) -> None:
        """Precompute Gauss-Legendre quadrature on the raw y-domain."""

        nodes_std, weights_std = leggauss(self.n_integration_nodes)
        a, b = self.y_domain_
        nodes = 0.5 * (b - a) * nodes_std + 0.5 * (a + b)
        weights = 0.5 * (b - a) * weights_std
        self.quadrature_ = _QuadratureRule(
            nodes=nodes,
            weights=weights,
            log_weights=np.log(weights),
        )

    def _build_x_basis(
        self, x_scaled: np.ndarray
    ) -> tuple[list[np.ndarray], list[tuple[int, np.ndarray]]]:
        """Build feature-wise and pairwise X basis arrays."""

        if self.degree_x <= 0 or not self.include_interactions:
            return [], []

        x_basis_single: list[np.ndarray] = []
        active_indices = np.flatnonzero(self.active_feature_mask_)
        for feature_idx in active_indices:
            basis_vals = _chebyshev_nonconstant_basis(
                x_scaled[:, feature_idx], self.degree_x
            )
            x_basis_single.append(basis_vals)

        x_basis_pair: list[tuple[int, np.ndarray]] = []
        if self.x_interaction_order >= 2 and len(active_indices) >= 2:
            for pair_idx, (left_pos, right_pos) in enumerate(
                combinations(range(len(active_indices)), 2)
            ):
                left_basis = x_basis_single[left_pos]
                right_basis = x_basis_single[right_pos]
                pair_basis = np.einsum(
                    "ni,nj->nij", left_basis, right_basis, optimize=True
                ).reshape(x_scaled.shape[0], -1)
                x_basis_pair.append((pair_idx, pair_basis))
        return x_basis_single, x_basis_pair

    def _build_parameter_layout(self) -> None:
        """Create parameter slices and names."""

        active_indices = np.flatnonzero(self.active_feature_mask_)
        qy = self.degree_y
        qx = self.degree_x

        names: list[str] = []
        offset = 0
        self.slice_y_ = slice(offset, offset + qy)
        names.extend([f"T{d}(y)" for d in range(1, qy + 1)])
        offset += qy

        self.slice_yx_ = []
        if self.include_interactions and qx > 0:
            for feature_idx in active_indices:
                size = qy * qx
                self.slice_yx_.append(slice(offset, offset + size))
                feat_name = self.feature_names_[feature_idx]
                for dy in range(1, qy + 1):
                    for dx in range(1, qx + 1):
                        names.append(f"T{dy}(y):T{dx}({feat_name})")
                offset += size

        self.slice_yxx_ = []
        self.pair_feature_indices_ = list(combinations(active_indices, 2))
        if self.include_interactions and qx > 0 and self.x_interaction_order >= 2:
            for left_idx, right_idx in self.pair_feature_indices_:
                size = qy * qx * qx
                self.slice_yxx_.append(slice(offset, offset + size))
                left_name = self.feature_names_[left_idx]
                right_name = self.feature_names_[right_idx]
                for dy in range(1, qy + 1):
                    for dx1 in range(1, qx + 1):
                        for dx2 in range(1, qx + 1):
                            names.append(
                                f"T{dy}(y):T{dx1}({left_name}):T{dx2}({right_name})"
                            )
                offset += size

        self.parameter_names_ = names
        self.n_parameters_ = offset
        self.penalty_mask_ = np.ones(self.n_parameters_, dtype=float)

    def _compute_gamma(
        self,
        x_basis_single: list[np.ndarray],
        x_basis_pair: list[tuple[int, np.ndarray]],
        beta: np.ndarray,
    ) -> np.ndarray:
        """Compute coefficient functions on the y basis for each observation."""

        n_obs = (
            x_basis_single[0].shape[0]
            if x_basis_single
            else x_basis_pair[0][1].shape[0]
            if x_basis_pair
            else self._gamma_n_obs_
        )
        gamma = np.repeat(beta[self.slice_y_][None, :], n_obs, axis=0)

        if self.include_interactions and self.degree_x > 0:
            for block_basis, block_slice in zip(x_basis_single, self.slice_yx_):
                block = beta[block_slice].reshape(self.degree_y, self.degree_x)
                gamma += block_basis @ block.T
            if self.x_interaction_order >= 2:
                for (_, block_basis), block_slice in zip(x_basis_pair, self.slice_yxx_):
                    block = beta[block_slice].reshape(
                        self.degree_y, self.degree_x * self.degree_x
                    )
                    gamma += block_basis @ block.T
        return gamma

    def _objective_factory(
        self,
        y_basis_obs: np.ndarray,
        y_basis_nodes: np.ndarray,
        x_basis_single: list[np.ndarray],
        x_basis_pair: list[tuple[int, np.ndarray]],
        l1_alpha: float,
        l2_alpha: float,
        eps_l1: float = 1e-8,
    ):
        """Create objective and gradient closures for optimization."""

        y_nodes_t = y_basis_nodes.T
        log_weights = self.quadrature_.log_weights
        n_obs = y_basis_obs.shape[0]
        self._gamma_n_obs_ = n_obs
        cache: dict[str, Any] = {"beta": None, "obj": None, "grad": None}

        def evaluate(beta: np.ndarray) -> tuple[float, np.ndarray]:
            cached_beta = cache["beta"]
            if cached_beta is not None and np.array_equal(beta, cached_beta):
                return cache["obj"], cache["grad"]

            gamma = self._compute_gamma(x_basis_single, x_basis_pair, beta)
            log_kernel = gamma @ y_nodes_t
            logZ = logsumexp(log_kernel + log_weights[None, :], axis=1)
            logpdf = np.sum(y_basis_obs * gamma, axis=1) - logZ
            neg_mean_loglik = -float(np.mean(logpdf))

            probs = np.exp(log_kernel + log_weights[None, :] - logZ[:, None])
            expected_y = probs @ y_basis_nodes
            diff = y_basis_obs - expected_y

            grad = np.zeros_like(beta)
            grad[self.slice_y_] = -np.mean(diff, axis=0)

            if self.include_interactions and self.degree_x > 0:
                for block_basis, block_slice in zip(x_basis_single, self.slice_yx_):
                    block_grad = -(diff.T @ block_basis) / n_obs
                    grad[block_slice] = block_grad.reshape(-1)
                if self.x_interaction_order >= 2:
                    for (_, block_basis), block_slice in zip(
                        x_basis_pair, self.slice_yxx_
                    ):
                        block_grad = -(diff.T @ block_basis) / n_obs
                        grad[block_slice] = block_grad.reshape(-1)

            penalty = 0.0
            if l2_alpha > 0.0:
                penalty += 0.5 * l2_alpha * float(
                    np.sum(self.penalty_mask_ * beta * beta)
                )
                grad += l2_alpha * self.penalty_mask_ * beta
            if l1_alpha > 0.0:
                smooth_abs = np.sqrt(beta * beta + eps_l1)
                penalty += l1_alpha * float(np.sum(self.penalty_mask_ * smooth_abs))
                grad += l1_alpha * self.penalty_mask_ * (beta / smooth_abs)

            obj = neg_mean_loglik + penalty
            cache["beta"] = beta.copy()
            cache["obj"] = obj
            cache["grad"] = grad
            return obj, grad

        return evaluate

    def _prepare_training_data(
        self, y: ArrayLike, X: ArrayLike
    ) -> tuple[np.ndarray, np.ndarray]:
        """Validate and convert training data."""

        y_arr = _as_1d_float_array(y, name="y")
        X_arr = _as_2d_float_array(X, name="X")
        if X_arr.shape[0] != y_arr.shape[0]:
            raise ValueError(
                f"X and y must have the same number of rows; got {X_arr.shape[0]} and {y_arr.shape[0]}."
            )
        return y_arr, X_arr

    def _fit_single(
        self,
        y: np.ndarray,
        X: np.ndarray,
        l1_alpha: float,
        l2_alpha: float,
        showtrace: bool = False,
    ) -> "DistributionalRegressionPDF":
        """Internal fit routine on already validated arrays."""

        self.n_samples_ = int(y.shape[0])
        self.n_features_in_ = int(X.shape[1])
        pending_feature_names = getattr(self, "_pending_feature_names_", None)
        self.feature_names_ = (
            pending_feature_names
            if pending_feature_names is not None
            else _make_feature_names(X, self.n_features_in_)
        )
        self.fit_intercept_identifiable_ = False

        y_domain = self._infer_y_domain(y)
        self._fit_y_scaler(y_domain)
        x_scaled, self.active_feature_indices_ = self._fit_x_scalers(X)
        self._build_quadrature_rule()

        y_scaled_obs = self.y_scaler_.transform(y)
        y_scaled_nodes = self.y_scaler_.transform(self.quadrature_.nodes)
        y_basis_obs = _chebyshev_nonconstant_basis(y_scaled_obs, self.degree_y)
        y_basis_nodes = _chebyshev_nonconstant_basis(y_scaled_nodes, self.degree_y)
        self.y_basis_nodes_ = y_basis_nodes
        x_basis_single, x_basis_pair = self._build_x_basis(x_scaled)

        self._build_parameter_layout()
        beta0 = np.zeros(self.n_parameters_, dtype=float)
        objective = self._objective_factory(
            y_basis_obs=y_basis_obs,
            y_basis_nodes=y_basis_nodes,
            x_basis_single=x_basis_single,
            x_basis_pair=x_basis_pair,
            l1_alpha=l1_alpha,
            l2_alpha=l2_alpha,
        )

        evaluation_counter = {"n": 0}

        def fun(beta: np.ndarray) -> float:
            evaluation_counter["n"] += 1
            value, _ = objective(beta)
            return value

        def jac(beta: np.ndarray) -> np.ndarray:
            _, grad = objective(beta)
            return grad

        if showtrace or self.verbose > 0:
            print(
                "Fitting DistributionalRegressionPDF: "
                f"n={self.n_samples_}, p={self.n_parameters_}, "
                f"l1_alpha={l1_alpha:.3g}, l2_alpha={l2_alpha:.3g}"
            )

        result = minimize(
            fun=fun,
            x0=beta0,
            jac=jac,
            method=self.optimizer,
            options={
                "maxiter": self.max_iter,
                "disp": bool(showtrace or self.verbose > 1),
                "ftol": self.tol,
            },
        )

        final_obj, final_grad = objective(result.x)
        gamma = self._compute_gamma(x_basis_single, x_basis_pair, result.x)
        logZ = logsumexp(
            gamma @ y_basis_nodes.T + self.quadrature_.log_weights[None, :], axis=1
        )
        train_logpdf = np.sum(y_basis_obs * gamma, axis=1) - logZ

        self.coef_ = result.x.copy()
        self.selected_l1_alpha_ = float(l1_alpha)
        self.selected_l2_alpha_ = float(l2_alpha)
        self.optimizer_result_ = {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "nit": int(getattr(result, "nit", -1)),
            "nfev": int(getattr(result, "nfev", evaluation_counter["n"])),
            "objective_value": float(final_obj),
            "gradient_norm": float(np.linalg.norm(final_grad)),
        }
        self.fit_diagnostics_ = {
            "mean_loglik": float(np.mean(train_logpdf)),
            "std_loglik": float(np.std(train_logpdf, ddof=1))
            if train_logpdf.size > 1
            else 0.0,
            "n_active_features": int(np.sum(self.active_feature_mask_)),
            "n_constant_features": int(self.n_constant_features_),
            "fit_intercept_identifiable": self.fit_intercept_identifiable_,
            "fit_intercept_requested": self.fit_intercept,
        }
        self.is_fitted_ = True
        return self

    def fit(
        self,
        y: ArrayLike,
        X: ArrayLike,
        l1_alpha: float = 0.0,
        l2_alpha: float = 1e-4,
        cv: bool = False,
        folds: int = 5,
        rng: int | np.random.Generator | None = None,
        cv_grid: Sequence[tuple[float, float]] | None = None,
        showtrace: bool = False,
    ) -> "DistributionalRegressionPDF":
        """Fit the conditional density estimator.

        Parameters
        ----------
        y : array-like of shape (n_samples,)
            Scalar outcome.
        X : array-like of shape (n_samples, n_features)
            Covariates.
        l1_alpha : float, default=0.0
            Smooth L1 regularization strength.
        l2_alpha : float, default=1e-4
            L2 regularization strength.
        cv : bool, default=False
            If ``True``, select penalty strengths by cross-validation using
            out-of-fold conditional log-likelihood.
        folds : int, default=5
            Number of K-fold splits used when ``cv=True``.
        rng : int, Generator, or None, default=None
            Random seed or generator used for fold splitting and sampling.
        cv_grid : sequence of (l1_alpha, l2_alpha) pairs, optional
            Additional candidate penalties for cross-validation. The user-supplied
            pair ``(l1_alpha, l2_alpha)`` is always included.
        showtrace : bool, default=False
            Print fitting trace information.

        Returns
        -------
        DistributionalRegressionPDF
            The fitted estimator.
        """

        if l1_alpha < 0 or l2_alpha < 0:
            raise ValueError("l1_alpha and l2_alpha must be non-negative.")
        y_arr, X_arr = self._prepare_training_data(y, X)
        self._pending_feature_names_ = _make_feature_names(X, X_arr.shape[1])

        if not cv:
            self.cv_results_ = None
            try:
                return self._fit_single(
                    y=y_arr,
                    X=X_arr,
                    l1_alpha=float(l1_alpha),
                    l2_alpha=float(l2_alpha),
                    showtrace=showtrace,
                )
            finally:
                if hasattr(self, "_pending_feature_names_"):
                    delattr(self, "_pending_feature_names_")

        if folds < 2:
            raise ValueError("folds must be at least 2 when cv=True.")
        if folds > y_arr.shape[0]:
            raise ValueError("folds cannot exceed the number of observations.")

        global_y_domain = self._infer_y_domain(y_arr)
        base_grid = [
            (0.0, 1e-5),
            (0.0, 1e-4),
            (0.0, 1e-3),
            (1e-5, 1e-4),
            (1e-4, 1e-4),
            (1e-4, 1e-3),
            (1e-3, 1e-3),
        ]
        if cv_grid is not None:
            base_grid.extend(tuple(map(float, pair)) for pair in cv_grid)
        base_grid.append((float(l1_alpha), float(l2_alpha)))

        candidates: list[tuple[float, float]] = []
        seen: set[tuple[float, float]] = set()
        for pair in base_grid:
            if pair[0] < 0 or pair[1] < 0:
                raise ValueError("All cv_grid penalty values must be non-negative.")
            if pair not in seen:
                seen.add(pair)
                candidates.append(pair)

        rng_gen = _check_rng(rng)
        splitter = KFold(
            n_splits=folds,
            shuffle=True,
            random_state=int(rng_gen.integers(0, 2**31 - 1)),
        )

        cv_rows: list[dict[str, float | int | bool]] = []
        best_score = -np.inf
        best_pair = (float(l1_alpha), float(l2_alpha))

        if showtrace or self.verbose > 0:
            print(
                f"Cross-validating {len(candidates)} penalty combinations over {folds} folds."
            )

        for candidate_l1, candidate_l2 in candidates:
            fold_scores: list[float] = []
            failed = False
            for fold_id, (train_idx, valid_idx) in enumerate(splitter.split(X_arr), start=1):
                candidate = self._make_clone(y_domain_override=global_y_domain)
                candidate._fit_single(
                    y=y_arr[train_idx],
                    X=X_arr[train_idx],
                    l1_alpha=candidate_l1,
                    l2_alpha=candidate_l2,
                    showtrace=False,
                )
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=RuntimeWarning)
                    valid_logpdf = candidate.logpdf(y_arr[valid_idx], X_arr[valid_idx])
                score = float(np.mean(valid_logpdf))
                if not np.isfinite(score):
                    failed = True
                    score = -np.inf
                fold_scores.append(score)
                if showtrace and self.verbose > 0:
                    print(
                        f"  fold={fold_id}, l1={candidate_l1:.3g}, "
                        f"l2={candidate_l2:.3g}, score={score:.6f}"
                    )

            mean_score = float(np.mean(fold_scores))
            cv_rows.append(
                {
                    "l1_alpha": candidate_l1,
                    "l2_alpha": candidate_l2,
                    "mean_valid_loglik": mean_score,
                    "std_valid_loglik": float(np.std(fold_scores, ddof=1))
                    if len(fold_scores) > 1
                    else 0.0,
                    "failed": failed,
                }
            )

            if showtrace or self.verbose > 0:
                print(
                    f"Candidate l1={candidate_l1:.3g}, l2={candidate_l2:.3g}, "
                    f"mean valid log-lik={mean_score:.6f}"
                )

            if mean_score > best_score:
                best_score = mean_score
                best_pair = (candidate_l1, candidate_l2)

        self.cv_results_ = cv_rows
        self.cv_selected_ = {
            "l1_alpha": best_pair[0],
            "l2_alpha": best_pair[1],
            "mean_valid_loglik": best_score,
            "folds": int(folds),
        }

        try:
            return self._fit_single(
                y=y_arr,
                X=X_arr,
                l1_alpha=best_pair[0],
                l2_alpha=best_pair[1],
                showtrace=showtrace,
            )
        finally:
            if hasattr(self, "_pending_feature_names_"):
                delattr(self, "_pending_feature_names_")

    def _check_is_fitted(self) -> None:
        """Raise if the model is not yet fitted."""

        if not getattr(self, "is_fitted_", False):
            raise RuntimeError("This DistributionalRegressionPDF instance is not fitted.")

    def _prepare_prediction_inputs(
        self, y: ArrayLike, X: ArrayLike
    ) -> tuple[np.ndarray, np.ndarray, bool]:
        """Broadcast y and X according to the documented pairwise rules."""

        self._check_is_fitted()
        X_arr = _as_2d_float_array(X, name="X")
        if X_arr.shape[1] != self.n_features_in_:
            raise ValueError(
                f"Expected X with {self.n_features_in_} columns, got {X_arr.shape[1]}."
            )

        y_arr_raw = np.asarray(y, dtype=float)
        if y_arr_raw.ndim > 1:
            raise ValueError("y must be scalar or one-dimensional for prediction.")
        y_is_scalar = y_arr_raw.ndim == 0
        y_vec = np.atleast_1d(y_arr_raw).astype(float)
        if not np.all(np.isfinite(y_vec)):
            raise ValueError("y contains missing or non-finite values.")

        n_x = X_arr.shape[0]
        if y_is_scalar and n_x == 1:
            y_out = np.array([float(y_vec[0])], dtype=float)
            X_out = X_arr
            return y_out, X_out, True
        if not y_is_scalar and n_x == 1:
            X_out = np.repeat(X_arr, y_vec.size, axis=0)
            return y_vec, X_out, False
        if y_is_scalar and n_x > 1:
            y_out = np.repeat(float(y_vec[0]), n_x)
            return y_out, X_arr, False
        if y_vec.size == n_x:
            return y_vec, X_arr, False
        raise ValueError(
            "Prediction shapes are incompatible. Use one of: scalar y with one x row, "
            "vector y with one x row, scalar y with many x rows, or equal-length pairwise "
            "y and X rows."
        )

    def _compute_prediction_bases(
        self, X: np.ndarray
    ) -> tuple[list[np.ndarray], list[tuple[int, np.ndarray]]]:
        """Build X basis arrays for prediction."""

        X_scaled = self._transform_X(X, warn_on_extrapolation=True)
        return self._build_x_basis(X_scaled)

    def _logZ_from_gamma(self, gamma: np.ndarray) -> np.ndarray:
        """Compute log normalizers from gamma rows."""

        return logsumexp(
            gamma @ self.y_basis_nodes_.T + self.quadrature_.log_weights[None, :],
            axis=1,
        )

    def _gamma_for_X(self, X: np.ndarray) -> np.ndarray:
        """Compute gamma rows for prediction inputs."""

        x_basis_single, x_basis_pair = self._compute_prediction_bases(X)
        self._gamma_n_obs_ = X.shape[0]
        return self._compute_gamma(x_basis_single, x_basis_pair, self.coef_)

    def logpdf(self, y: ArrayLike, X: ArrayLike) -> np.ndarray | float:
        """Evaluate the fitted conditional log-density.

        Broadcasting rules follow the class docstring. Values outside the fitted
        ``y`` domain return ``-inf``.
        """

        y_vec, X_arr, scalar_output = self._prepare_prediction_inputs(y, X)
        gamma = self._gamma_for_X(X_arr)
        logZ = self._logZ_from_gamma(gamma)

        inside = (y_vec >= self.y_domain_[0]) & (y_vec <= self.y_domain_[1])
        out = np.full(y_vec.shape[0], -np.inf, dtype=float)
        if np.any(inside):
            y_scaled = self.y_scaler_.transform(y_vec[inside])
            y_basis = _chebyshev_nonconstant_basis(y_scaled, self.degree_y)
            out[inside] = np.sum(y_basis * gamma[inside], axis=1) - logZ[inside]
        if scalar_output:
            return float(out[0])
        return out

    def pdf(self, y: ArrayLike, X: ArrayLike) -> np.ndarray | float:
        """Evaluate the fitted conditional density in raw outcome units."""

        logvals = self.logpdf(y, X)
        if np.isscalar(logvals):
            return 0.0 if not np.isfinite(logvals) else float(np.exp(logvals))
        out = np.zeros_like(logvals, dtype=float)
        finite = np.isfinite(logvals)
        out[finite] = np.exp(logvals[finite])
        return out

    def __call__(self, y: ArrayLike, X: ArrayLike) -> np.ndarray | float:
        """Alias for :meth:`pdf`."""

        return self.pdf(y, X)

    def cdf(self, y: ArrayLike, X: ArrayLike) -> np.ndarray | float:
        """Evaluate the fitted conditional CDF by numerical integration."""

        y_vec, X_arr, scalar_output = self._prepare_prediction_inputs(y, X)
        gamma = self._gamma_for_X(X_arr)
        full_logZ = self._logZ_from_gamma(gamma)

        a, b = self.y_domain_
        out = np.empty(y_vec.shape[0], dtype=float)
        for idx, y_val in enumerate(y_vec):
            if y_val <= a:
                out[idx] = 0.0
                continue
            if y_val >= b:
                out[idx] = 1.0
                continue

            nodes_std, weights_std = leggauss(self.n_integration_nodes)
            nodes = 0.5 * (y_val - a) * nodes_std + 0.5 * (a + y_val)
            weights = 0.5 * (y_val - a) * weights_std
            y_basis = _chebyshev_nonconstant_basis(
                self.y_scaler_.transform(nodes), self.degree_y
            )
            log_num = logsumexp(
                y_basis @ gamma[idx] + np.log(weights), axis=0
            )
            out[idx] = float(np.exp(log_num - full_logZ[idx]))

        if scalar_output:
            return float(out[0])
        return out

    def sample(
        self,
        x: ArrayLike,
        size: int = 1,
        rng: int | np.random.Generator | None = None,
    ) -> np.ndarray:
        """Draw approximate random samples from the fitted conditional density.

        Sampling is performed for a single covariate row using inverse-CDF
        sampling on a dense grid over the modeled ``y`` domain.
        """

        if size < 1:
            raise ValueError("size must be at least 1.")
        X_arr = _as_2d_float_array(x, name="x")
        if X_arr.shape[0] != 1:
            raise ValueError("sample expects exactly one covariate row.")

        grid_size = max(512, 8 * self.n_integration_nodes)
        grid = np.linspace(self.y_domain_[0], self.y_domain_[1], grid_size)
        dens = np.asarray(self.pdf(grid, X_arr), dtype=float)
        cdf_grid = cumulative_trapezoid(dens, grid, initial=0.0)
        if cdf_grid[-1] <= 0.0:
            raise RuntimeError("Sampling failed because the approximated CDF is degenerate.")
        cdf_grid /= cdf_grid[-1]

        rng_gen = _check_rng(rng)
        u = rng_gen.uniform(size=size)
        return np.interp(u, cdf_grid, grid)

    def summary(self) -> str:
        """Return a human-readable model summary."""

        self._check_is_fitted()
        lines = [
            "DistributionalRegressionPDF Summary",
            "-----------------------------------",
            f"Basis: {self.basis}",
            f"degree_y={self.degree_y}, degree_x={self.degree_x}",
            f"include_interactions={self.include_interactions}, "
            f"x_interaction_order={self.x_interaction_order}",
            f"n_samples={self.n_samples_}, n_features={self.n_features_in_}",
            f"n_active_features={self.fit_diagnostics_['n_active_features']}, "
            f"n_constant_features={self.fit_diagnostics_['n_constant_features']}",
            f"y_domain={self.y_domain_}",
            f"standardize_X={self.standardize_X}, standardize_y={self.standardize_y}",
            f"fit_intercept_requested={self.fit_intercept}, "
            f"fit_intercept_identifiable={self.fit_intercept_identifiable_}",
            f"n_parameters={self.n_parameters_}",
            f"selected_l1_alpha={self.selected_l1_alpha_:.6g}, "
            f"selected_l2_alpha={self.selected_l2_alpha_:.6g}",
            f"optimizer={self.optimizer}, success={self.optimizer_result_['success']}",
            f"optimizer_message={self.optimizer_result_['message']}",
            f"objective_value={self.optimizer_result_['objective_value']:.6f}",
            f"gradient_norm={self.optimizer_result_['gradient_norm']:.6f}",
            f"mean_loglik={self.fit_diagnostics_['mean_loglik']:.6f}",
            f"cv_used={self.cv_results_ is not None}",
        ]
        if self.cv_results_ is not None:
            lines.append(
                "cv_selected="
                f"(l1={self.cv_selected_['l1_alpha']:.6g}, "
                f"l2={self.cv_selected_['l2_alpha']:.6g}, "
                f"mean_valid_loglik={self.cv_selected_['mean_valid_loglik']:.6f})"
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        """Concise representation."""

        if getattr(self, "is_fitted_", False):
            return (
                "DistributionalRegressionPDF("
                f"degree_y={self.degree_y}, degree_x={self.degree_x}, "
                f"n_samples={self.n_samples_}, n_features={self.n_features_in_}, "
                f"n_parameters={self.n_parameters_})"
            )
        return (
            "DistributionalRegressionPDF("
            f"basis='{self.basis}', degree_y={self.degree_y}, "
            f"degree_x={self.degree_x}, include_interactions={self.include_interactions})"
        )

    __str__ = __repr__

    def save(self, file_path: str | Path) -> None:
        """Serialize the fitted model to disk using joblib."""

        self._check_is_fitted()
        joblib.dump(self, file_path)

    @classmethod
    def load(cls, file_path: str | Path) -> "DistributionalRegressionPDF":
        """Load a serialized model from disk."""

        model = joblib.load(file_path)
        if not isinstance(model, cls):
            raise TypeError(
                f"Expected a serialized {cls.__name__} instance, got {type(model)!r}."
            )
        return model
if __name__ == "__main__":
    rng = np.random.default_rng(1234)
    n = 450
    X_demo = rng.normal(size=(n, 3))

    loc = 0.35 * np.sin(1.2 * X_demo[:, 0]) - 0.25 * X_demo[:, 1]
    sigma = 0.35 + 0.12 * (X_demo[:, 0] > 0) + 0.08 * np.abs(X_demo[:, 2])
    tail = rng.lognormal(mean=0.15 * X_demo[:, 1], sigma=sigma)
    tail_center = np.exp(0.15 * X_demo[:, 1] + 0.5 * sigma * sigma)
    y_demo = loc + tail - tail_center + 0.15 * X_demo[:, 0] * X_demo[:, 2]

    model = DistributionalRegressionPDF(
        basis="chebyshev",
        degree_y=5,
        degree_x=2,
        include_interactions=True,
        x_interaction_order=2,
        n_integration_nodes=64,
        verbose=1,
    )

    model.fit(
        y_demo,
        X_demo,
        l1_alpha=1e-4,
        l2_alpha=1e-3,
        cv=True,
        folds=3,
        rng=1234,
        showtrace=False,
    )

    print(model.summary())
    probe_x = X_demo[[0]]
    probe_y = np.array([-1.0, 0.0, 1.0, 2.0])
    print("PDF values:", model.pdf(probe_y, probe_x))
    print("CDF values:", model.cdf(probe_y, probe_x))
    draws = model.sample(probe_x, size=5, rng=4321)
    print("Sample draws:", draws)

    try:  # pragma: no cover - optional demo plotting
        import matplotlib.pyplot as plt

        grid = np.linspace(model.y_domain_[0], model.y_domain_[1], 240)
        profiles = np.vstack(
            [
                np.array([0.0, 0.0, 0.0]),
                np.array([1.0, -0.5, 0.75]),
                np.array([-1.0, 0.75, -0.5]),
            ]
        )
        plt.figure(figsize=(8, 5))
        for idx, profile in enumerate(profiles, start=1):
            plt.plot(grid, model.pdf(grid, profile), label=f"profile {idx}")
        plt.title("Fitted conditional densities")
        plt.xlabel("y")
        plt.ylabel("pdf")
        plt.legend()
        plt.tight_layout()
        plt.show()
    except Exception as exc:
        print(f"Matplotlib plot skipped: {exc}")
