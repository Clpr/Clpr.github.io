import unittest

import numpy as np

import fwcp
import fwcp_bunch_and_symmetric as legacy_bs
import fwcp_hw2009 as legacy_hw


class FWCPRefactorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(42)
        cls.data = np.concatenate(
            [
                rng.normal(0.03, 0.12, 1500),
                rng.uniform(-0.01, 0.01, 120),
            ]
        )
        cls.reference = rng.laplace(0.05, 0.18, 2200)

    def test_bunching_matches_legacy(self):
        legacy = legacy_bs.FWCPBunchingEstimator(
            self.data,
            kink_point=0.0,
            bin_width=0.02,
            xlim=(-0.6, 0.8),
            degree=12,
            alpha=1e-3,
            cv=False,
        )
        modern = fwcp.BunchingEstimator(
            kink_point=0.0,
            bin_width=0.02,
            xlim=(-0.6, 0.8),
            degree=12,
            alpha=1e-3,
            cv=False,
        ).fit(self.data)

        self.assertAlmostEqual(modern.fwcp_absolute, legacy.fwcp_absolute, places=12)
        self.assertAlmostEqual(modern.fwcp_relative, legacy.fwcp_relative, places=12)

        plot = modern.plotdata()
        self.assertEqual(plot["x"].shape, plot["y_actual"].shape)
        self.assertEqual(plot["x"].shape, plot["y_notional"].shape)

    def test_symmetric_matches_legacy(self):
        legacy = legacy_bs.FWCPSymmetricEstimator(
            self.data,
            kink_point=0.0,
            bin_width=0.02,
            xlim=(-0.6, 0.8),
            degree=12,
            alpha=1e-3,
            cv=False,
            symmetry_type="median",
            centering=True,
        )
        modern = fwcp.SymmetricEstimator(
            kink_point=0.0,
            bin_width=0.02,
            xlim=(-0.6, 0.8),
            degree=12,
            alpha=1e-3,
            cv=False,
            symmetry_type="median",
            centering=True,
        ).fit(self.data)

        self.assertAlmostEqual(modern.fwcp_absolute, legacy.fwcp_absolute, places=12)
        self.assertAlmostEqual(modern.fwcp_relative, legacy.fwcp_relative, places=12)

        plot = modern.plotdata()
        self.assertEqual(plot["x_original"].shape, plot["y_actual"].shape)
        self.assertEqual(plot["x_original"].shape, plot["y_notional"].shape)

    def test_hw2009_matches_legacy(self):
        legacy = legacy_hw.HoldenWulfsberg2009(self.reference)
        modern = fwcp.HoldenWulfsberg2009Estimator(self.reference).fit(self.data)

        self.assertAlmostEqual(modern.fwcp_frequency(), legacy.fwcp_freq(self.data), places=12)
        self.assertAlmostEqual(
            modern.fwcp_integral(weighted=False),
            legacy.fwcp_int(self.data, weighted=False),
            places=12,
        )
        self.assertAlmostEqual(
            modern.fwcp_integral(weighted=True),
            legacy.fwcp_int(self.data, weighted=True),
            places=12,
        )

    def test_rule_of_thumb_matches_definition(self):
        est = fwcp.RuleOfThumbEstimator().fit(self.data)
        expected = 1.0 - 2.0 * np.mean(self.data <= 0)
        self.assertAlmostEqual(est.fwcp_absolute, expected, places=12)
        self.assertAlmostEqual(est.fwcp_relative, expected, places=12)

    def test_aliases_exist(self):
        self.assertIs(fwcp.UnivariateChebRidgeRegression, fwcp.ChebyshevRidgeRegressor)
        self.assertIs(fwcp.FWCPBunchingEstimator, fwcp.BunchingEstimator)
        self.assertIs(fwcp.FWCPSymmetricEstimator, fwcp.SymmetricEstimator)
        self.assertIs(fwcp.HoldenWulfsberg2009, fwcp.HoldenWulfsberg2009Estimator)


if __name__ == "__main__":
    unittest.main()
