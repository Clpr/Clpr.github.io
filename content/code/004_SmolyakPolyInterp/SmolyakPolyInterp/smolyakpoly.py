"""Anisotropic Smolyak polynomial interpolation with Chebyshev basis."""

from __future__ import annotations

import pickle
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

import numpy as np
import scipy.linalg


ArrayLike = Sequence[float] | np.ndarray


def _as_1d_float_array(values: ArrayLike, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    return arr


def _smolyak_degree_block(level: int) -> np.ndarray:
    if level == 1:
        return np.array([0], dtype=int)
    if level == 2:
        return np.array([1, 2], dtype=int)
    start = 2 ** (level - 2) + 1
    stop = 2 ** (level - 1) + 1
    return np.arange(start, stop, dtype=int)


def _cc_level_nodes(level: int) -> np.ndarray:
    if level == 1:
        return np.array([0.0], dtype=float)
    if level == 2:
        return np.array([-1.0, 1.0], dtype=float)
    m = 2 ** (level - 1) + 1
    k = np.arange(m, dtype=float)
    return np.cos(np.pi * k / (m - 1))


def _cc_incremental_nodes(level: int) -> np.ndarray:
    nodes = _cc_level_nodes(level)
    if level == 1:
        return nodes
    prev = _cc_level_nodes(level - 1)
    mask = np.ones(nodes.shape[0], dtype=bool)
    for value in prev:
        mask &= ~np.isclose(nodes, value, atol=1e-14, rtol=0.0)
    return nodes[mask]


def _generate_multi_indices(level_caps: np.ndarray, accuracy: int) -> list[tuple[int, ...]]:
    dim = level_caps.size
    min_sum = dim
    max_sum = dim + int(accuracy)
    current = [1] * dim
    out: list[tuple[int, ...]] = []

    def rec(pos: int, running_sum: int) -> None:
        if pos == dim:
            if min_sum <= running_sum <= max_sum:
                out.append(tuple(current))
            return

        for level in range(1, int(level_caps[pos]) + 1):
            new_sum = running_sum + level
            min_tail = dim - pos - 1
            max_tail = int(np.sum(level_caps[pos + 1 :]))
            if new_sum + min_tail > max_sum:
                break
            if new_sum + max_tail < min_sum:
                continue
            current[pos] = level
            rec(pos + 1, new_sum)

    rec(0, 0)
    out.sort(key=lambda idx: (sum(idx), idx))
    return out


def _cartesian_product(arrays: Sequence[np.ndarray]) -> np.ndarray:
    if not arrays:
        return np.empty((1, 0), dtype=float)
    mesh = np.meshgrid(*arrays, indexing="ij")
    stacked = np.stack(mesh, axis=-1)
    return stacked.reshape(-1, len(arrays))


def _normalize_points(x: ArrayLike, dim: int) -> tuple[np.ndarray, bool]:
    arr = np.asarray(x, dtype=float)
    if arr.ndim == 1:
        if arr.size != dim:
            raise ValueError(f"Expected a vector of length {dim}, got {arr.size}.")
        return arr.reshape(1, dim), True
    if arr.ndim != 2 or arr.shape[1] != dim:
        raise ValueError(f"Expected an array of shape (N, {dim}).")
    return arr, False


def _evaluate_function_serial(func: Callable[[np.ndarray], float], points: np.ndarray) -> np.ndarray:
    return np.asarray([float(func(point.copy())) for point in points], dtype=float)


@dataclass(frozen=True)
class _ModelState:
    levels: tuple[int, ...]
    lb: np.ndarray
    ub: np.ndarray
    accuracy: int
    showtrace: bool
    n_jobs: int
    coef: np.ndarray | None


class SmolyakPolyInterp:
    """
    Anisotropic Smolyak polynomial interpolant on a rectangular domain.

    The interpolant uses nested Clenshaw-Curtis / Chebyshev-Gauss-Lobatto nodes
    and a tensor-product Chebyshev basis assembled through the anisotropic
    Smolyak construction. Input points are mapped implicitly between the user
    domain ``[lb, ub]`` and the canonical cube ``[-1, 1]^n``.

    Example
    -------
    ```python
    import smolyakpoly as slp
    import numpy as np

    # fake: define a multivariate function to fit/interpolate
    def f(x: np.ndarray) -> float:
        \"\"\"x is a 1D array (vector), 4 dim in this example\"\"\"
        return np.sin(x[0]) + np.cos(x[1]) + np.sin(x[2] * x[3])

    # fake: domain of `f` to be fitted
    lbs = (-10, -0.5, -0.1, -3)
    ubs = (20, 2.0, 3.0, 1.5)

    # define a Smolyak polynomial interpolant, where the constructor builds the grid
    itp = slp.SmolyakPolyInterp(
        levels=(5, 3, 7, 8),  # anisotropic max level of each dimension
        lb=lbs,
        ub=ubs,
        accuracy=6,  # Smolyak accuracy cutoff
        showtrace=False,
    )

    # inspect grid information
    itp.summary()

    # fit a callable f(x)
    itp.fit(
        f,
        showtrace=True,
    )

    # evaluate at one point
    y = itp([0.1, 0.22, 0.777, 0.98])

    # evaluate at many points
    ys = itp(np.random.rand(2000, 4))

    # evaluate basis
    b1 = itp.basis([0.1, 0.22, 0.777, 0.98])
    bN = itp.basis(np.random.rand(2000, 4))

    # interpolation coefficient
    c = itp.coef()

    # basis times coefficients equals interpolant value
    Xs = np.random.rand(2000, 4)
    np.allclose(itp.basis(Xs) @ itp.coef(), itp(Xs))

    # derivatives
    x = np.random.rand(4)
    g = itp.jacobian(x)
    G = itp.jacobian(Xs)
    H = itp.hessian(x)
    Hs = itp.hessian(Xs)

    # save and load
    itp.save("smolyak_model.pkl")
    itp_recovered = slp.SmolyakPolyInterp.load("smolyak_model.pkl")

    # extract support nodes in a M*n matrix, where M is the number of nodes and n is the dimension
    nodes = itp.nodes()  # in user domain
    norm_nodes = itp.nodes(normalized=True)  # in canonical cube [-1,1]^n

    # update the model with new nodal values (e.g. if the function values at the nodes have changed)
    new_values = [x.sum() for x in nodes] # fake: some new function values at the nodes
    itp.update(new_values) # re-fit the model with the new nodal values
    ```
    """

    def __init__(
        self,
        levels: Sequence[int],
        lb: ArrayLike,
        ub: ArrayLike,
        accuracy: int,
        showtrace: bool = False,
        n_jobs: int | None = None,
    ) -> None:
        self.levels = tuple(int(v) for v in levels)
        if not self.levels:
            raise ValueError("levels must be a non-empty sequence.")
        if any(v < 1 for v in self.levels):
            raise ValueError("All levels must be positive integers.")

        self.dim = len(self.levels)
        self.lb = _as_1d_float_array(lb, "lb")
        self.ub = _as_1d_float_array(ub, "ub")
        if self.lb.size != self.dim or self.ub.size != self.dim:
            raise ValueError("lb and ub must have the same length as levels.")
        if np.any(self.ub <= self.lb):
            raise ValueError("Each upper bound must exceed its lower bound.")

        self.accuracy = int(accuracy)
        if self.accuracy < 0:
            raise ValueError("accuracy must be non-negative.")

        self.showtrace = bool(showtrace)
        self.n_jobs = int(n_jobs if n_jobs is not None else 1)
        self._scale = 2.0 / (self.ub - self.lb)
        self._shift = -(self.ub + self.lb) / (self.ub - self.lb)

        self.multi_indices = _generate_multi_indices(np.asarray(self.levels), self.accuracy)
        if not self.multi_indices:
            raise ValueError("No admissible Smolyak multi-indices were generated.")

        self._basis_degrees = self._build_basis_degrees()
        self._max_degree = int(np.max(self._basis_degrees)) if self._basis_degrees.size else 0
        self.grid_cube = self._build_sparse_grid()
        self.grid = self._cube_to_domain(self.grid_cube)
        self._basis_matrix = self._basis_from_cube(self.grid_cube)
        self._lu_factor = scipy.linalg.lu_factor(self._basis_matrix)
        self._coef: np.ndarray | None = None
        self._fitted_values: np.ndarray | None = None

        if self._basis_matrix.shape[0] != self._basis_matrix.shape[1]:
            raise RuntimeError("Internal error: interpolation system is not square.")

    def _build_basis_degrees(self) -> np.ndarray:
        basis_terms: list[np.ndarray] = []
        for multi_idx in self.multi_indices:
            degree_blocks = [_smolyak_degree_block(level) for level in multi_idx]
            basis_terms.append(_cartesian_product(degree_blocks).astype(int))

        all_terms = np.vstack(basis_terms)
        unique_terms = np.unique(all_terms, axis=0)
        return unique_terms

    def _build_sparse_grid(self) -> np.ndarray:
        points: list[np.ndarray] = []
        for multi_idx in self.multi_indices:
            node_blocks = [_cc_incremental_nodes(level) for level in multi_idx]
            points.append(_cartesian_product(node_blocks))

        if not points:
            raise RuntimeError("Failed to build any sparse-grid points.")

        raw = np.vstack(points)
        rounded = np.round(raw, decimals=14)
        _, unique_idx = np.unique(rounded, axis=0, return_index=True)
        unique_idx.sort()
        return raw[unique_idx]

    def _domain_to_cube(self, x: np.ndarray) -> np.ndarray:
        z = x * self._scale + self._shift
        if np.any(z < -1.0 - 1e-12) or np.any(z > 1.0 + 1e-12):
            raise ValueError("Evaluation point falls outside the interpolation domain.")
        return np.clip(z, -1.0, 1.0)

    def _cube_to_domain(self, z: np.ndarray) -> np.ndarray:
        return (z - self._shift) / self._scale

    def _eval_cheb_family(self, z: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        n_pts = z.shape[0]
        T = np.empty((n_pts, self.dim, self._max_degree + 1), dtype=float)
        dT = np.empty_like(T)
        ddT = np.empty_like(T)

        T[:, :, 0] = 1.0
        dT[:, :, 0] = 0.0
        ddT[:, :, 0] = 0.0

        if self._max_degree >= 1:
            T[:, :, 1] = z
            dT[:, :, 1] = 1.0
            ddT[:, :, 1] = 0.0

        for k in range(2, self._max_degree + 1):
            T[:, :, k] = 2.0 * z * T[:, :, k - 1] - T[:, :, k - 2]
            dT[:, :, k] = 2.0 * T[:, :, k - 1] + 2.0 * z * dT[:, :, k - 1] - dT[:, :, k - 2]
            ddT[:, :, k] = 4.0 * dT[:, :, k - 1] + 2.0 * z * ddT[:, :, k - 1] - ddT[:, :, k - 2]

        return T, dT, ddT

    def _basis_from_cube(self, z: np.ndarray) -> np.ndarray:
        T, _, _ = self._eval_cheb_family(z)
        n_pts = z.shape[0]
        n_basis = self._basis_degrees.shape[0]
        basis = np.ones((n_pts, n_basis), dtype=float)
        for dim_idx in range(self.dim):
            basis *= T[:, dim_idx, self._basis_degrees[:, dim_idx]]
        return basis

    def _basis_and_derivatives_from_cube(
        self, z: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        T, dT, ddT = self._eval_cheb_family(z)
        n_pts = z.shape[0]
        n_basis = self._basis_degrees.shape[0]

        values_by_dim = np.empty((self.dim, n_pts, n_basis), dtype=float)
        dvalues_by_dim = np.empty_like(values_by_dim)
        ddvalues_by_dim = np.empty_like(values_by_dim)

        for dim_idx in range(self.dim):
            degrees = self._basis_degrees[:, dim_idx]
            values_by_dim[dim_idx] = T[:, dim_idx, degrees]
            dvalues_by_dim[dim_idx] = dT[:, dim_idx, degrees]
            ddvalues_by_dim[dim_idx] = ddT[:, dim_idx, degrees]

        basis = np.prod(values_by_dim, axis=0)
        jac_basis = np.empty((n_pts, self.dim, n_basis), dtype=float)
        hess_basis = np.empty((n_pts, self.dim, self.dim, n_basis), dtype=float)

        for i in range(self.dim):
            if self.dim == 1:
                prod_other = np.ones((n_pts, n_basis), dtype=float)
            else:
                prod_other = np.prod(values_by_dim[np.arange(self.dim) != i], axis=0)
            jac_basis[:, i, :] = dvalues_by_dim[i] * prod_other

            for j in range(self.dim):
                if i == j:
                    if self.dim == 1:
                        prod_rest = np.ones((n_pts, n_basis), dtype=float)
                    else:
                        prod_rest = np.prod(values_by_dim[np.arange(self.dim) != i], axis=0)
                    hess_basis[:, i, j, :] = ddvalues_by_dim[i] * prod_rest
                else:
                    if self.dim == 2:
                        prod_rest = np.ones((n_pts, n_basis), dtype=float)
                    else:
                        mask = (np.arange(self.dim) != i) & (np.arange(self.dim) != j)
                        prod_rest = np.prod(values_by_dim[mask], axis=0)
                    hess_basis[:, i, j, :] = dvalues_by_dim[i] * dvalues_by_dim[j] * prod_rest

        return basis, jac_basis, hess_basis

    def summary(self) -> dict[str, object]:
        info = {
            "dim": self.dim,
            "levels": self.levels,
            "accuracy": self.accuracy,
            "n_multi_indices": len(self.multi_indices),
            "n_nodes": int(self.grid.shape[0]),
            "n_basis": int(self._basis_degrees.shape[0]),
            "lb": tuple(float(v) for v in self.lb),
            "ub": tuple(float(v) for v in self.ub),
            "fitted": self._coef is not None,
        }
        print("SmolyakPolyInterp summary")
        for key, value in info.items():
            print(f"  {key}: {value}")
        return info

    def fit(
        self,
        f: Callable[[np.ndarray], float],
        showtrace: bool | None = None,
        n_jobs: int | None = None,
    ) -> "SmolyakPolyInterp":
        trace = self.showtrace if showtrace is None else bool(showtrace)
        jobs = self.n_jobs if n_jobs is None else int(n_jobs)

        if trace:
            print(f"Evaluating function on {self.grid.shape[0]} sparse-grid nodes...")

        if jobs == 1:
            values = _evaluate_function_serial(f, self.grid)
        else:
            with ThreadPoolExecutor(max_workers=jobs) as pool:
                values = np.asarray(list(pool.map(lambda pt: float(f(pt.copy())), self.grid)), dtype=float)

        if trace:
            print("Solving interpolation system...")

        self._coef = scipy.linalg.lu_solve(self._lu_factor, values)
        self._fitted_values = values
        return self

    def nodes(self, normalized: bool = False) -> np.ndarray:
        return self.grid_cube.copy() if normalized else self.grid.copy()

    def update(self, values: ArrayLike) -> "SmolyakPolyInterp":
        y = np.asarray(values, dtype=float)
        if y.ndim != 1:
            raise ValueError("values must be a one-dimensional array of nodal function values.")
        if y.size != self.grid.shape[0]:
            raise ValueError(
                f"Expected {self.grid.shape[0]} nodal values, got {y.size}."
            )

        self._coef = scipy.linalg.lu_solve(self._lu_factor, y)
        self._fitted_values = y.copy()
        return self

    def basis(self, x: ArrayLike) -> np.ndarray:
        points, was_vector = _normalize_points(x, self.dim)
        z = self._domain_to_cube(points)
        out = self._basis_from_cube(z)
        return out[0] if was_vector else out

    def coef(self) -> np.ndarray:
        if self._coef is None:
            raise RuntimeError("Interpolator has not been fitted yet.")
        return self._coef.copy()

    def __call__(self, x: ArrayLike) -> np.ndarray | float:
        if self._coef is None:
            raise RuntimeError("Interpolator has not been fitted yet.")
        points, was_vector = _normalize_points(x, self.dim)
        values = self.basis(points) @ self._coef
        return float(values[0]) if was_vector else values

    def jacobian(self, x: ArrayLike) -> np.ndarray:
        if self._coef is None:
            raise RuntimeError("Interpolator has not been fitted yet.")
        points, was_vector = _normalize_points(x, self.dim)
        z = self._domain_to_cube(points)
        _, jac_basis, _ = self._basis_and_derivatives_from_cube(z)
        jac = np.tensordot(jac_basis, self._coef, axes=([2], [0]))
        jac *= self._scale.reshape(1, self.dim)
        return jac[0] if was_vector else jac

    def hessian(self, x: ArrayLike) -> np.ndarray:
        if self._coef is None:
            raise RuntimeError("Interpolator has not been fitted yet.")
        points, was_vector = _normalize_points(x, self.dim)
        z = self._domain_to_cube(points)
        _, _, hess_basis = self._basis_and_derivatives_from_cube(z)
        hess = np.tensordot(hess_basis, self._coef, axes=([3], [0]))
        scale_outer = np.outer(self._scale, self._scale)
        hess *= scale_outer.reshape(1, self.dim, self.dim)
        return hess[0] if was_vector else np.moveaxis(hess, 0, -1)

    def save(self, fpath: str | Path) -> None:
        state = _ModelState(
            levels=self.levels,
            lb=self.lb,
            ub=self.ub,
            accuracy=self.accuracy,
            showtrace=self.showtrace,
            n_jobs=self.n_jobs,
            coef=None if self._coef is None else self._coef.copy(),
        )
        with open(fpath, "wb") as handle:
            pickle.dump(state, handle)

    @classmethod
    def load(cls, fpath: str | Path) -> "SmolyakPolyInterp":
        with open(fpath, "rb") as handle:
            state: _ModelState = pickle.load(handle)

        obj = cls(
            levels=state.levels,
            lb=state.lb,
            ub=state.ub,
            accuracy=state.accuracy,
            showtrace=state.showtrace,
            n_jobs=state.n_jobs,
        )
        obj._coef = None if state.coef is None else state.coef.copy()
        return obj


__all__ = ["SmolyakPolyInterp"]
