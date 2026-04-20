"""Tests for distributional_regression_pdf.py.

Run with:

    conda run -n PyMain python test.py
"""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import numpy as np
from scipy.integrate import trapezoid

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

from distributional_regression_pdf import DistributionalRegressionPDF


def _simulate_data(
    n_samples: int = 180,
    n_features: int = 2,
    seed: int = 123,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate asymmetric synthetic data with known conditional density."""

    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n_samples, n_features))
    x0 = X[:, 0]
    x1 = X[:, 1] if n_features > 1 else np.zeros(n_samples)
    loc = 0.55 * np.sin(0.9 * x0) - 0.25 * x1
    mu = 0.20 * x0 - 0.10 * x1
    sigma = 0.35 + 0.12 * np.abs(x1)
    lognormal_part = rng.lognormal(mean=mu, sigma=sigma)
    y = loc + lognormal_part
    return y, X


class DistributionalRegressionPDFTests(unittest.TestCase):
    """End-to-end regression tests for the distributional regression module."""

    def test_pdf_normalization_is_close_to_one(self) -> None:
        y, X = _simulate_data(n_samples=180, n_features=2, seed=7)
        model = DistributionalRegressionPDF(
            degree_y=4,
            degree_x=2,
            x_interaction_order=1,
            n_integration_nodes=48,
        )
        model.fit(y, X, l1_alpha=1e-4, l2_alpha=1e-3)

        grid = np.linspace(model.y_domain_[0], model.y_domain_[1], 500)
        for row in (0, 20, 40):
            density = np.asarray(model.pdf(grid, X[row]), dtype=float)
            area = trapezoid(density, grid)
            self.assertTrue(np.isfinite(area))
            self.assertAlmostEqual(area, 1.0, places=2)

    def test_prediction_shapes_and_boundary_behavior(self) -> None:
        y, X = _simulate_data(n_samples=140, n_features=2, seed=11)
        model = DistributionalRegressionPDF(
            degree_y=3,
            degree_x=2,
            x_interaction_order=1,
            n_integration_nodes=32,
        )
        model.fit(y, X, l2_alpha=1e-3)

        scalar_pdf = model.pdf(float(np.median(y)), X[0])
        self.assertIsInstance(scalar_pdf, float)

        y_grid = np.array([np.min(y), np.median(y), np.max(y)])
        vector_pdf = model.pdf(y_grid, X[0])
        self.assertEqual(vector_pdf.shape, (3,))

        pairwise_logpdf = model.logpdf(y[:5], X[:5])
        self.assertEqual(pairwise_logpdf.shape, (5,))

        cdf_vals = model.cdf(y_grid, X[0])
        self.assertEqual(cdf_vals.shape, (3,))
        self.assertTrue(np.all(np.diff(cdf_vals) >= -1e-8))

        outside_low = model.y_domain_[0] - 1.0
        outside_high = model.y_domain_[1] + 1.0
        self.assertEqual(model.pdf(outside_low, X[0]), 0.0)
        self.assertEqual(model.logpdf(outside_low, X[0]), float("-inf"))
        self.assertEqual(model.cdf(outside_low, X[0]), 0.0)
        self.assertEqual(model.cdf(outside_high, X[0]), 1.0)

    def test_persistence_sampling_and_cv(self) -> None:
        y, X = _simulate_data(n_samples=160, n_features=2, seed=21)
        model = DistributionalRegressionPDF(
            degree_y=4,
            degree_x=2,
            x_interaction_order=1,
            n_integration_nodes=40,
        )
        model.fit(y, X, l1_alpha=1e-4, l2_alpha=1e-3, cv=True, folds=3, rng=42)

        self.assertIsNotNone(model.cv_results_)
        self.assertIn("l1_alpha", model.cv_selected_)
        self.assertIn("l2_alpha", model.cv_selected_)

        draws = model.sample(X[0], size=8, rng=99)
        self.assertEqual(draws.shape, (8,))
        self.assertTrue(np.all(draws >= model.y_domain_[0]))
        self.assertTrue(np.all(draws <= model.y_domain_[1]))

        probe_y = np.linspace(np.quantile(y, 0.2), np.quantile(y, 0.8), 7)
        probe_pdf = np.asarray(model.pdf(probe_y, X[0]), dtype=float)

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "dr_pdf.joblib"
            model.save(file_path)
            reloaded = DistributionalRegressionPDF.load(file_path)
            reloaded_pdf = np.asarray(reloaded.pdf(probe_y, X[0]), dtype=float)

        np.testing.assert_allclose(probe_pdf, reloaded_pdf, rtol=1e-8, atol=1e-10)

    def test_constant_columns_and_pandas_support(self) -> None:
        if pd is None:
            self.skipTest("pandas is not installed in the active environment.")

        y, X = _simulate_data(n_samples=120, n_features=2, seed=77)
        X_df = pd.DataFrame(
            {
                "skill": X[:, 0],
                "constant_feature": np.ones(X.shape[0]),
                "shock": X[:, 1],
            }
        )

        model = DistributionalRegressionPDF(
            degree_y=3,
            degree_x=2,
            x_interaction_order=1,
            n_integration_nodes=32,
        )
        model.fit(y, X_df, l2_alpha=1e-3)

        self.assertEqual(model.n_constant_features_, 1)
        self.assertIn("skill", "".join(model.parameter_names_))
        self.assertIn("shock", "".join(model.parameter_names_))
        self.assertNotIn("constant_feature", "".join(model.parameter_names_))


if __name__ == "__main__":
    unittest.main(verbosity=2)
