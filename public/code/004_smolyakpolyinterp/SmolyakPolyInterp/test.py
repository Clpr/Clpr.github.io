from __future__ import annotations

import os
import tempfile

import numpy as np

import smolyakpoly as slp


def f(x: np.ndarray) -> float:
    return (
        np.sin(0.3 * x[0])
        + np.cos(0.7 * x[1])
        + 0.5 * x[2] * x[3]
        + x[0] * x[2] ** 2
        - 0.2 * x[1] * x[3]
    )


def analytic_grad(x: np.ndarray) -> np.ndarray:
    return np.array(
        [
            0.3 * np.cos(0.3 * x[0]) + x[2] ** 2,
            -0.7 * np.sin(0.7 * x[1]) - 0.2 * x[3],
            0.5 * x[3] + 2.0 * x[0] * x[2],
            0.5 * x[2] - 0.2 * x[1],
        ],
        dtype=float,
    )


def analytic_hess(x: np.ndarray) -> np.ndarray:
    out = np.zeros((4, 4), dtype=float)
    out[0, 0] = -0.09 * np.sin(0.3 * x[0])
    out[1, 1] = -0.49 * np.cos(0.7 * x[1])
    out[0, 2] = out[2, 0] = 2.0 * x[2]
    out[1, 3] = out[3, 1] = -0.2
    out[2, 2] = 2.0 * x[0]
    out[2, 3] = out[3, 2] = 0.5
    return out


def main() -> None:
    lbs = (-1.5, -0.5, -0.75, -1.0)
    ubs = (2.0, 1.25, 1.5, 0.8)

    itp = slp.SmolyakPolyInterp(
        levels=(3, 3, 3, 3),
        lb=lbs,
        ub=ubs,
        accuracy=3,
        showtrace=False,
    )

    info = itp.summary()
    assert info["n_nodes"] == info["n_basis"]

    nodes = itp.nodes()
    norm_nodes = itp.nodes(normalized=True)
    assert nodes.shape == norm_nodes.shape == (info["n_nodes"], 4)
    assert np.allclose(nodes, itp.nodes(), atol=0.0, rtol=0.0)
    assert np.allclose(norm_nodes, itp.nodes(normalized=True), atol=0.0, rtol=0.0)
    assert np.all(norm_nodes <= 1.0 + 1e-12)
    assert np.all(norm_nodes >= -1.0 - 1e-12)

    itp.fit(f, showtrace=False)

    node_values = itp(itp.grid)
    true_node_values = np.array([f(x) for x in itp.grid])
    assert np.allclose(node_values, true_node_values, atol=1e-10, rtol=1e-10)

    Xs = np.random.default_rng(123).uniform(np.array(lbs), np.array(ubs), size=(64, 4))
    basis_vals = itp.basis(Xs) @ itp.coef()
    interp_vals = itp(Xs)
    assert np.allclose(basis_vals, interp_vals, atol=1e-11, rtol=1e-11)

    updated = slp.SmolyakPolyInterp(
        levels=(3, 3, 3, 3),
        lb=lbs,
        ub=ubs,
        accuracy=3,
        showtrace=False,
    )
    updated_nodes = updated.nodes()
    assert np.allclose(updated_nodes, nodes, atol=0.0, rtol=0.0)
    updated.update(np.array([f(x) for x in updated_nodes]))
    assert np.allclose(updated.coef(), itp.coef(), atol=1e-10, rtol=1e-10)
    assert np.allclose(updated(Xs), interp_vals, atol=1e-10, rtol=1e-10)

    x = np.array([0.2, 0.1, -0.3, 0.4], dtype=float)
    jac = itp.jacobian(x)
    hess = itp.hessian(x)

    assert jac.shape == (4,)
    assert hess.shape == (4, 4)
    assert np.allclose(jac, analytic_grad(x), atol=2e-1, rtol=2e-1)
    assert np.allclose(hess, analytic_hess(x), atol=5e-1, rtol=5e-1)

    Hs = itp.hessian(Xs[:5])
    assert Hs.shape == (4, 4, 5)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "interp.pkl")
        itp.save(path)
        loaded = slp.SmolyakPolyInterp.load(path)
        assert np.allclose(loaded(Xs), interp_vals, atol=1e-12, rtol=1e-12)

    print("All tests passed.")


if __name__ == "__main__":
    main()
