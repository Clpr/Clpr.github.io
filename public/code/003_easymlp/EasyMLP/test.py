import unittest

import numpy as np

try:
    import torch  # noqa: F401
except ImportError:
    TORCH_AVAILABLE = False
else:
    TORCH_AVAILABLE = True

from easymlp import EasyMLP


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch is required for EasyMLP tests.")
class EasyMLPTestCase(unittest.TestCase):
    def test_constructor_validation(self) -> None:
        with self.assertRaises(ValueError):
            EasyMLP(
                in_dim=2,
                out_dim=1,
                hidden_dims=[8, 4],
                activations=["Tanh"],
                out_spaces=["real"],
                monotonicity=[0],
            )

        with self.assertRaises(ValueError):
            EasyMLP(
                in_dim=2,
                out_dim=1,
                hidden_dims=[8],
                activations=["GELU"],
                out_spaces=["real"],
                monotonicity=[1],
            )

    def test_training_prediction_and_monotonicity(self) -> None:
        rng = np.random.default_rng(42)
        x = rng.uniform(0.0, 1.0, size=(160, 2)).astype(np.float32)
        y0 = np.exp(0.8 * x[:, 0] + 0.4 * x[:, 1]).astype(np.float32)
        y1 = (1.5 * x[:, 0] - 0.25 * x[:, 1] + 0.1).astype(np.float32)
        y = np.column_stack([y0, y1]).astype(np.float32)

        model = EasyMLP(
            in_dim=2,
            out_dim=2,
            hidden_dims=[32, 16],
            activations=["Softplus", "Tanh"],
            out_spaces=["positive", "real"],
            monotonicity=[1, 0],
            advanced_options={
                "max_epochs": 120,
                "patience": 20,
                "fine_tune_epochs": 20,
                "batch_size": 32,
            },
        )

        model.train(x, y, random_seed=123, show_trace=False, gpu_acceleration="none")
        pred = model(x[:12])

        self.assertEqual(pred.shape, (12, 2))
        self.assertTrue(np.all(pred[:, 0] > 0.0))
        self.assertEqual(model.fitted().shape, y.shape)
        self.assertEqual(model.residual().shape, y.shape)

        low = np.array([0.2, 0.3], dtype=np.float32)
        high = np.array([0.8, 0.9], dtype=np.float32)
        self.assertGreaterEqual(float(model(high)[0]), float(model(low)[0]))

        residual_mse = float(np.mean(model.residual() ** 2))
        self.assertLess(residual_mse, 0.05)

    def test_serialization_round_trip(self) -> None:
        rng = np.random.default_rng(7)
        x = rng.uniform(-1.0, 1.0, size=(80, 2)).astype(np.float32)
        y = np.column_stack(
            [
                1.0 / (1.0 + np.exp(-(x[:, 0] + x[:, 1]))),
                -np.exp(-(0.5 * x[:, 0] - 0.2 * x[:, 1])),
            ]
        ).astype(np.float32)

        model = EasyMLP(
            in_dim=2,
            out_dim=2,
            hidden_dims=[24, 12],
            activations=["Tanh", "Softplus"],
            out_spaces=["[0,1]", "negative"],
            monotonicity=[[1, 1], [0, 0]],
            advanced_options={
                "max_epochs": 100,
                "patience": 15,
                "fine_tune_epochs": 10,
                "batch_size": 16,
            },
        )
        model.train(x, y, random_seed=11, show_trace=False, gpu_acceleration="none")

        payload = model.serialize()
        restored = EasyMLP.from_dict(payload)

        original_pred = model(x[:10])
        restored_pred = restored(x[:10])
        np.testing.assert_allclose(original_pred, restored_pred, atol=1e-5, rtol=1e-5)
        np.testing.assert_allclose(model.fitted(), restored.fitted(), atol=1e-5, rtol=1e-5)

    def test_derivatives(self) -> None:
        model = EasyMLP(
            in_dim=2,
            out_dim=1,
            hidden_dims=[12, 8],
            activations=["Tanh", "Softplus"],
            out_spaces=["[-1,1]"],
            monotonicity=[[1, 0]],
        )

        jac = model.jacobian([0.2, -0.4])
        hes = model.hessian([0.2, -0.4])

        self.assertEqual(jac.shape, (1, 2))
        self.assertEqual(len(hes), 1)
        self.assertEqual(hes[0].shape, (2, 2))
        self.assertTrue(np.all(np.isfinite(jac)))
        self.assertTrue(np.all(np.isfinite(hes[0])))

    def test_nonsmooth_activations_raise_for_hessian(self) -> None:
        model = EasyMLP(
            in_dim=2,
            out_dim=1,
            hidden_dims=[8],
            activations=["ReLU"],
            out_spaces=["real"],
            monotonicity=[0],
        )

        with self.assertRaises(RuntimeError):
            model.jacobian([0.0, 0.0])

        with self.assertRaises(RuntimeError):
            model.hessian([0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
