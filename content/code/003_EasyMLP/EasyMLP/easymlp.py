"""
easymlp
=======

`easymlp` provides a compact, single-file wrapper around a PyTorch-based
multi-layer perceptron (MLP) pipeline for approximating vector-valued
functions

    f(x): R^n -> R^m

with optional architecture-level monotonicity constraints.

The public entry point is :class:`EasyMLP`. The class handles model
construction, automatic train/validation splitting, early stopping,
fine-tuning, serialization, prediction, and derivative evaluation.

Quick example
-------------

```python
import numpy as np

from easymlp import EasyMLP

X = np.random.rand(500, 2)
Y = np.column_stack(
    [
        np.exp(0.8 * X[:, 0] + 0.4 * X[:, 1]),
        2.0 * X[:, 0] - 0.5 * X[:, 1],
        1.0 / (1.0 + np.exp(-(X[:, 0] - X[:, 1]))),
    ]
)

model = EasyMLP(
    in_dim=2,
    out_dim=3,
    hidden_dims=[128, 64, 32],
    activations=["Softplus", "Tanh", "Sigmoid"],
    out_spaces=["positive", "real", "[0,1]"],
    monotonicity=[1, 0, -1],
)

model.train(X, Y, random_seed=7, show_trace=False)
model.summary()

point_prediction = model([0.2, 0.8])
batch_prediction = model(X[:10])
jac = model.jacobian([0.2, 0.8])
hes = model.hessian([0.2, 0.8])
payload = model.serialize()
```

Notes
-----

- The simple one-dimensional ``monotonicity`` convention follows the user
  requirement in which one sign is supplied per output dimension:
  ``[1, 0, -1]`` means the first output is increasing in all inputs, the
  second output is unconstrained, and the third output is decreasing in all
  inputs.
- For more detailed partial monotonicity, a two-dimensional
  ``out_dim x in_dim`` matrix is also supported. Each entry must be one of
  ``{-1, 0, 1}``.
- Monotonicity is imposed by architecture, not by a soft penalty.
- PyTorch is required for model construction and training.
"""

from __future__ import annotations

import copy
import math
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - exercised in numpy-free envs
    np = None
    _NUMPY_IMPORT_ERROR = exc
else:
    _NUMPY_IMPORT_ERROR = None

try:
    import torch
    from torch import nn
    from torch.nn import functional as F
    from torch.utils.data import DataLoader, TensorDataset
except ImportError as exc:  # pragma: no cover - exercised in torch-free envs
    torch = None
    nn = None
    F = None
    DataLoader = None
    TensorDataset = None
    _TORCH_IMPORT_ERROR = exc
else:
    _TORCH_IMPORT_ERROR = None

try:  # pragma: no cover - optional dependency
    from tqdm.auto import tqdm
except ImportError:  # pragma: no cover - optional dependency
    tqdm = None


if np is not None:
    ArrayLike = Union[Sequence[float], np.ndarray]
else:  # pragma: no cover - exercised only when numpy is absent
    ArrayLike = Sequence[float]
MonotonicityArg = Union[Sequence[int], Sequence[Sequence[int]], np.ndarray]


def _require_numpy() -> None:
    if np is None:
        raise ImportError(
            "NumPy is required to use EasyMLP. Install it first, for example "
            "with `pip install numpy`."
        ) from _NUMPY_IMPORT_ERROR


def _require_torch() -> None:
    if torch is None:
        raise ImportError(
            "PyTorch is required to use EasyMLP. Install it first, for example "
            "with `pip install torch` or a platform-specific PyTorch build."
        ) from _TORCH_IMPORT_ERROR


def _normalize_name(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


_ACTIVATION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "identity": {
        "factory": lambda: nn.Identity(),
        "order": math.inf,
        "monotone_ok": True,
        "label": "Identity",
    },
    "relu": {
        "factory": lambda: nn.ReLU(),
        "order": 0,
        "monotone_ok": True,
        "label": "ReLU",
    },
    "leakyrelu": {
        "factory": lambda: nn.LeakyReLU(negative_slope=0.01),
        "order": 0,
        "monotone_ok": True,
        "label": "Leaky ReLU",
    },
    "elu": {
        "factory": lambda: nn.ELU(),
        "order": math.inf,
        "monotone_ok": True,
        "label": "ELU",
    },
    "selu": {
        "factory": lambda: nn.SELU(),
        "order": math.inf,
        "monotone_ok": True,
        "label": "SELU",
    },
    "sigmoid": {
        "factory": lambda: nn.Sigmoid(),
        "order": math.inf,
        "monotone_ok": True,
        "label": "Sigmoid",
    },
    "tanh": {
        "factory": lambda: nn.Tanh(),
        "order": math.inf,
        "monotone_ok": True,
        "label": "Tanh",
    },
    "softplus": {
        "factory": lambda: nn.Softplus(),
        "order": math.inf,
        "monotone_ok": True,
        "label": "Softplus",
    },
    "gelu": {
        "factory": lambda: nn.GELU(),
        "order": math.inf,
        "monotone_ok": False,
        "label": "GELU",
    },
    "silu": {
        "factory": lambda: nn.SiLU(),
        "order": math.inf,
        "monotone_ok": False,
        "label": "SiLU",
    },
}

_OUTPUT_SPACE_LABELS = {
    "real": "real",
    "positive": "positive",
    "negative": "negative",
    "[0,1]": "[0,1]",
    "[-1,1]": "[-1,1]",
}


@dataclass
class _TrainingOptions:
    validation_fraction: float = 0.2
    max_epochs: int = 250
    learning_rate: float = 1e-3
    batch_size: int = 128
    patience: int = 25
    min_delta: float = 1e-6
    fine_tune_epochs: int = 40
    fine_tune_learning_rate: float = 3e-4
    standardize_inputs: bool = True
    l1_lambda: float = 1e-7
    l2_lambda: float = 1e-7
    gradient_clip_norm: Optional[float] = None
    trace_every: int = 10

    def merged(self, overrides: Optional[Dict[str, Any]]) -> "_TrainingOptions":
        data = self.__dict__.copy()
        if overrides:
            unknown = sorted(set(overrides) - set(data))
            if unknown:
                raise ValueError(
                    "Unknown advanced training option(s): "
                    + ", ".join(str(item) for item in unknown)
                )
            data.update(overrides)
        return _TrainingOptions(**data)

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


def _canonical_activation_name(name: str) -> str:
    _require_torch()
    if not isinstance(name, str):
        raise TypeError("Each activation must be provided as a string.")
    key = _normalize_name(name)
    if key not in _ACTIVATION_REGISTRY:
        supported = ", ".join(
            sorted(spec["label"] for spec in _ACTIVATION_REGISTRY.values())
        )
        raise ValueError(
            f"Unsupported activation '{name}'. Supported activations: {supported}."
        )
    return key


def _canonical_output_space(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Each output space must be provided as a string.")
    stripped = name.strip().lower()
    aliases = {
        "real": "real",
        "positive": "positive",
        "negative": "negative",
        "[0,1]": "[0,1]",
        "0,1": "[0,1]",
        "unit": "[0,1]",
        "[-1,1]": "[-1,1]",
        "-1,1": "[-1,1]",
    }
    if stripped not in aliases:
        supported = ", ".join(_OUTPUT_SPACE_LABELS.values())
        raise ValueError(
            f"Unsupported output space '{name}'. Supported output spaces: {supported}."
        )
    return aliases[stripped]


def _ensure_2d_numpy(
    array: ArrayLike,
    *,
    name: str,
    expected_cols: Optional[int] = None,
) -> np.ndarray:
    _require_numpy()
    arr = np.asarray(array, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be a 2-D array.")
    if expected_cols is not None and arr.shape[1] != expected_cols:
        raise ValueError(
            f"{name} must have exactly {expected_cols} columns; got {arr.shape[1]}."
        )
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must contain only finite values.")
    return arr


def _ensure_1d_numpy(
    array: ArrayLike,
    *,
    name: str,
    expected_len: Optional[int] = None,
) -> np.ndarray:
    _require_numpy()
    arr = np.asarray(array, dtype=np.float32)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be a 1-D array.")
    if expected_len is not None and arr.shape[0] != expected_len:
        raise ValueError(
            f"{name} must have exactly {expected_len} elements; got {arr.shape[0]}."
        )
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must contain only finite values.")
    return arr


def _compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    _require_numpy()
    residual = y_true - y_pred
    mse = float(np.mean(residual**2))
    mae = float(np.mean(np.abs(residual)))
    denom = float(np.sum((y_true - np.mean(y_true, axis=0, keepdims=True)) ** 2))
    if denom <= 0.0:
        r2 = 1.0 if mse <= 0.0 else 0.0
    else:
        r2 = 1.0 - float(np.sum(residual**2)) / denom
    return {"mse": mse, "mae": mae, "r2": r2}


def _split_indices(
    n_samples: int,
    validation_fraction: float,
    seed: Optional[int],
) -> Tuple[np.ndarray, np.ndarray]:
    _require_numpy()
    if not 0.0 <= validation_fraction < 1.0:
        raise ValueError("validation_fraction must lie in [0, 1).")
    rng = np.random.default_rng(seed)
    indices = np.arange(n_samples, dtype=np.int64)
    rng.shuffle(indices)
    if n_samples <= 1 or validation_fraction <= 0.0:
        return indices, np.empty(0, dtype=np.int64)
    n_val = int(round(n_samples * validation_fraction))
    n_val = max(1, min(n_samples - 1, n_val))
    return indices[n_val:], indices[:n_val]


def _select_device(request: str) -> "torch.device":
    _require_torch()
    key = request.strip().lower()
    if key == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    if key == "apple" and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _output_transform(z: "torch.Tensor", space: str) -> "torch.Tensor":
    if space == "real":
        return z
    if space == "positive":
        return F.softplus(z)
    if space == "negative":
        return -F.softplus(-z)
    if space == "[0,1]":
        return torch.sigmoid(z)
    if space == "[-1,1]":
        return torch.tanh(z)
    raise ValueError(f"Unknown output space '{space}'.")


if torch is not None:

    def _inverse_softplus(x: "torch.Tensor") -> "torch.Tensor":
        return x + torch.log(-torch.expm1(-x))


    class _PositiveLinear(nn.Module):
        def __init__(self, in_features: int, out_features: int, bias: bool = True) -> None:
            super().__init__()
            self.in_features = in_features
            self.out_features = out_features
            self.raw_weight = nn.Parameter(torch.empty(out_features, in_features))
            self.bias = nn.Parameter(torch.empty(out_features)) if bias else None
            self.reset_parameters()

        def reset_parameters(self) -> None:
            bound = 1.0 / math.sqrt(max(1, self.in_features))
            initial = torch.rand(self.out_features, self.in_features) * bound + 1e-3
            self.raw_weight.data.copy_(_inverse_softplus(initial))
            if self.bias is not None:
                nn.init.uniform_(self.bias, -bound, bound)

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            weight = F.softplus(self.raw_weight) + 1e-8
            return F.linear(x, weight, self.bias)


    class _InputPartiallyMonotoneLinear(nn.Module):
        def __init__(
            self,
            in_features: int,
            out_features: int,
            monotonicity_row: Sequence[int],
            bias: bool = True,
        ) -> None:
            super().__init__()
            self.in_features = in_features
            self.out_features = out_features

            mono_idx = [idx for idx, sign in enumerate(monotonicity_row) if sign != 0]
            free_idx = [idx for idx, sign in enumerate(monotonicity_row) if sign == 0]
            signs = [float(monotonicity_row[idx]) for idx in mono_idx]

            self.register_buffer(
                "mono_indices",
                torch.tensor(mono_idx, dtype=torch.long),
                persistent=True,
            )
            self.register_buffer(
                "free_indices",
                torch.tensor(free_idx, dtype=torch.long),
                persistent=True,
            )
            self.register_buffer(
                "mono_signs",
                torch.tensor(signs, dtype=torch.float32),
                persistent=True,
            )

            if mono_idx:
                self.raw_mono_weight = nn.Parameter(
                    torch.empty(out_features, len(mono_idx))
                )
            else:
                self.raw_mono_weight = None

            if free_idx:
                self.free_weight = nn.Parameter(torch.empty(out_features, len(free_idx)))
            else:
                self.free_weight = None

            self.bias = nn.Parameter(torch.empty(out_features)) if bias else None
            self.reset_parameters()

        def reset_parameters(self) -> None:
            bound = 1.0 / math.sqrt(max(1, self.in_features))
            if self.raw_mono_weight is not None:
                initial = (
                    torch.rand(self.out_features, self.raw_mono_weight.shape[1]) * bound
                    + 1e-3
                )
                self.raw_mono_weight.data.copy_(_inverse_softplus(initial))
            if self.free_weight is not None:
                nn.init.uniform_(self.free_weight, -bound, bound)
            if self.bias is not None:
                nn.init.uniform_(self.bias, -bound, bound)

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            result = None
            if self.raw_mono_weight is not None:
                mono_x = torch.index_select(x, dim=1, index=self.mono_indices)
                mono_x = mono_x * self.mono_signs.unsqueeze(0)
                mono_w = F.softplus(self.raw_mono_weight) + 1e-8
                result = F.linear(mono_x, mono_w, None)
            if self.free_weight is not None:
                free_x = torch.index_select(x, dim=1, index=self.free_indices)
                free_part = F.linear(free_x, self.free_weight, None)
                result = free_part if result is None else result + free_part
            if result is None:
                result = torch.zeros(
                    x.shape[0],
                    self.out_features,
                    device=x.device,
                    dtype=x.dtype,
                )
            if self.bias is not None:
                result = result + self.bias.unsqueeze(0)
            return result


    class _ScalarNetBase(nn.Module):
        def __init__(
            self,
            hidden_dims: Sequence[int],
            activation_names: Sequence[str],
            out_space: str,
        ) -> None:
            super().__init__()
            self.hidden_dims = list(hidden_dims)
            self.activation_names = list(activation_names)
            self.out_space = out_space

        def _apply_hidden(self, x: "torch.Tensor") -> "torch.Tensor":
            raise NotImplementedError

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            z = self._apply_hidden(x)
            return _output_transform(z, self.out_space)


    class _StandardScalarNet(_ScalarNetBase):
        def __init__(
            self,
            in_dim: int,
            hidden_dims: Sequence[int],
            activation_names: Sequence[str],
            out_space: str,
        ) -> None:
            super().__init__(hidden_dims, activation_names, out_space)
            dims = [in_dim, *hidden_dims, 1]
            self.linears = nn.ModuleList(
                nn.Linear(dims[idx], dims[idx + 1]) for idx in range(len(dims) - 1)
            )
            self.activations = nn.ModuleList(
                _ACTIVATION_REGISTRY[name]["factory"]() for name in activation_names
            )

        def _apply_hidden(self, x: "torch.Tensor") -> "torch.Tensor":
            for linear, activation in zip(self.linears[:-1], self.activations):
                x = activation(linear(x))
            return self.linears[-1](x)


    class _PartiallyMonotoneScalarNet(_ScalarNetBase):
        def __init__(
            self,
            in_dim: int,
            hidden_dims: Sequence[int],
            activation_names: Sequence[str],
            out_space: str,
            monotonicity_row: Sequence[int],
        ) -> None:
            super().__init__(hidden_dims, activation_names, out_space)
            dims = [in_dim, *hidden_dims, 1]
            self.first_linear = _InputPartiallyMonotoneLinear(
                dims[0], dims[1], monotonicity_row
            )
            tail_dims = dims[1:]
            self.tail_linears = nn.ModuleList(
                _PositiveLinear(tail_dims[idx], tail_dims[idx + 1])
                for idx in range(len(tail_dims) - 1)
            )
            self.activations = nn.ModuleList(
                _ACTIVATION_REGISTRY[name]["factory"]() for name in activation_names
            )

        def _apply_hidden(self, x: "torch.Tensor") -> "torch.Tensor":
            x = self.activations[0](self.first_linear(x))
            for linear, activation in zip(self.tail_linears[:-1], self.activations[1:]):
                x = activation(linear(x))
            return self.tail_linears[-1](x)


    class _VectorMLP(nn.Module):
        def __init__(
            self,
            in_dim: int,
            hidden_dims: Sequence[int],
            activation_names: Sequence[str],
            out_spaces: Sequence[str],
            monotonicity_matrix: Sequence[Sequence[int]],
        ) -> None:
            super().__init__()
            self.subnets = nn.ModuleList()
            for out_space, mono_row in zip(out_spaces, monotonicity_matrix):
                if any(sign != 0 for sign in mono_row):
                    subnet = _PartiallyMonotoneScalarNet(
                        in_dim=in_dim,
                        hidden_dims=hidden_dims,
                        activation_names=activation_names,
                        out_space=out_space,
                        monotonicity_row=mono_row,
                    )
                else:
                    subnet = _StandardScalarNet(
                        in_dim=in_dim,
                        hidden_dims=hidden_dims,
                        activation_names=activation_names,
                        out_space=out_space,
                    )
                self.subnets.append(subnet)

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            outputs = [subnet(x) for subnet in self.subnets]
            return torch.cat(outputs, dim=1)


class EasyMLP:
    """
    High-level wrapper for a PyTorch-based MLP approximator.

    Parameters
    ----------
    in_dim:
        Dimension of the input vector.
    out_dim:
        Dimension of the output vector.
    hidden_dims:
        Number of neurons in each hidden layer.
    activations:
        Activation function used in each hidden layer.
    out_spaces:
        Output-space specification for each output dimension. Supported values
        are ``"real"``, ``"positive"``, ``"negative"``, ``"[0,1]"``, and
        ``"[-1,1]"``.
    monotonicity:
        Either a one-dimensional list of length ``out_dim`` or a two-dimensional
        matrix of shape ``(out_dim, in_dim)``. In the one-dimensional form,
        each sign applies to all input dimensions for the corresponding output.
        Values must belong to ``{-1, 0, 1}``.
    advanced_options:
        Optional overrides for the hidden training pipeline. Supported keys are
        listed in ``EasyMLP.DEFAULT_TRAINING_OPTIONS``.

    Examples
    --------
    ```python
    model = EasyMLP(
        in_dim=2,
        out_dim=3,
        hidden_dims=[256, 128, 64],
        activations=["ReLU", "Leaky ReLU", "Sigmoid"],
        out_spaces=["real", "positive", "[0,1]"],
        monotonicity=[1, 0, -1],
    )
    ```

    ```python
    # More granular partial monotonicity:
    # output 0: increasing in x0, unconstrained in x1
    # output 1: decreasing in x0, increasing in x1
    model = EasyMLP(
        in_dim=2,
        out_dim=2,
        hidden_dims=[64, 32],
        activations=["Softplus", "Tanh"],
        out_spaces=["positive", "real"],
        monotonicity=[[1, 0], [-1, 1]],
    )
    ```
    """

    DEFAULT_TRAINING_OPTIONS = _TrainingOptions().as_dict()

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        hidden_dims: Sequence[int],
        activations: Sequence[str],
        out_spaces: Sequence[str],
        monotonicity: MonotonicityArg,
        advanced_options: Optional[Dict[str, Any]] = None,
    ) -> None:
        _require_numpy()
        self._default_training_options = _TrainingOptions().merged(advanced_options)
        self._configure(
            in_dim=in_dim,
            out_dim=out_dim,
            hidden_dims=hidden_dims,
            activations=activations,
            out_spaces=out_spaces,
            monotonicity=monotonicity,
        )

    def _configure(
        self,
        *,
        in_dim: int,
        out_dim: int,
        hidden_dims: Sequence[int],
        activations: Sequence[str],
        out_spaces: Sequence[str],
        monotonicity: MonotonicityArg,
    ) -> None:
        _require_torch()

        if not isinstance(in_dim, int) or in_dim <= 0:
            raise ValueError("in_dim must be a strictly positive integer.")
        if not isinstance(out_dim, int) or out_dim <= 0:
            raise ValueError("out_dim must be a strictly positive integer.")
        if not isinstance(hidden_dims, Sequence):
            raise TypeError("hidden_dims must be a sequence of integers.")
        if not isinstance(activations, Sequence):
            raise TypeError("activations must be a sequence of strings.")
        hidden_dims = [int(item) for item in hidden_dims]
        if not hidden_dims:
            raise ValueError("At least one hidden layer must be specified.")
        if any(item <= 0 for item in hidden_dims):
            raise ValueError("Each hidden dimension must be a strictly positive integer.")
        if len(hidden_dims) != len(activations):
            raise ValueError("hidden_dims and activations must have the same length.")
        if len(out_spaces) != out_dim:
            raise ValueError("out_spaces must have length equal to out_dim.")

        activation_names = [_canonical_activation_name(name) for name in activations]
        canonical_out_spaces = [_canonical_output_space(name) for name in out_spaces]
        monotonicity_matrix = self._normalize_monotonicity(monotonicity, out_dim, in_dim)

        if any(any(sign != 0 for sign in row) for row in monotonicity_matrix):
            invalid = [
                _ACTIVATION_REGISTRY[name]["label"]
                for name in activation_names
                if not _ACTIVATION_REGISTRY[name]["monotone_ok"]
            ]
            if invalid:
                joined = ", ".join(invalid)
                raise ValueError(
                    "Monotone outputs require hidden activations that are "
                    f"non-decreasing. Unsupported activation(s): {joined}."
                )

        self.in_dim = in_dim
        self.out_dim = out_dim
        self.hidden_dims = hidden_dims
        self.activations = [_ACTIVATION_REGISTRY[name]["label"] for name in activation_names]
        self._activation_names = activation_names
        self.out_spaces = canonical_out_spaces
        self.monotonicity = copy.deepcopy(monotonicity_matrix)
        self._network = _VectorMLP(
            in_dim=self.in_dim,
            hidden_dims=self.hidden_dims,
            activation_names=self._activation_names,
            out_spaces=self.out_spaces,
            monotonicity_matrix=self.monotonicity,
        )
        self._device = torch.device("cpu")
        self._network.to(self._device)

        self._trained = False
        self._random_seed: Optional[int] = None
        self._last_gpu_request = "none"
        self._regularization = {"l1": False, "l2": False}
        self._input_mean = np.zeros(self.in_dim, dtype=np.float32)
        self._input_scale = np.ones(self.in_dim, dtype=np.float32)
        self._training_history: List[Dict[str, float]] = []
        self._training_summary: Dict[str, Any] = {}
        self._metrics: Dict[str, float] = {}
        self._train_x: Optional[np.ndarray] = None
        self._train_y: Optional[np.ndarray] = None
        self._fitted_cache: Optional[np.ndarray] = None
        self._residual_cache: Optional[np.ndarray] = None

    @staticmethod
    def _normalize_monotonicity(
        monotonicity: MonotonicityArg,
        out_dim: int,
        in_dim: int,
    ) -> List[List[int]]:
        _require_numpy()
        arr = np.asarray(monotonicity, dtype=np.int64)
        if arr.ndim == 1:
            if arr.shape[0] != out_dim:
                raise ValueError(
                    "A one-dimensional monotonicity specification must have "
                    "length equal to out_dim."
                )
            matrix = np.repeat(arr[:, None], repeats=in_dim, axis=1)
        elif arr.ndim == 2:
            if tuple(arr.shape) != (out_dim, in_dim):
                raise ValueError(
                    "A two-dimensional monotonicity specification must have "
                    "shape (out_dim, in_dim)."
                )
            matrix = arr
        else:
            raise ValueError("monotonicity must be a 1-D or 2-D array-like object.")
        allowed = {-1, 0, 1}
        if any(int(value) not in allowed for value in matrix.ravel()):
            raise ValueError("monotonicity entries must each be one of {-1, 0, 1}.")
        return matrix.astype(int).tolist()

    def _current_training_options(
        self,
        advanced_options: Optional[Dict[str, Any]],
    ) -> _TrainingOptions:
        return self._default_training_options.merged(advanced_options)

    def _set_seed(self, seed: Optional[int]) -> None:
        self._random_seed = seed
        if seed is None:
            return
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    def _scale_inputs(self, x: np.ndarray) -> np.ndarray:
        return (x - self._input_mean[None, :]) / self._input_scale[None, :]

    def _to_tensor(self, x: np.ndarray, *, requires_grad: bool = False) -> "torch.Tensor":
        tensor = torch.tensor(
            x,
            dtype=torch.float32,
            device=self._device,
            requires_grad=requires_grad,
        )
        return tensor

    def _forward_tensor(self, raw_x: "torch.Tensor") -> "torch.Tensor":
        mean = torch.tensor(self._input_mean, device=raw_x.device, dtype=raw_x.dtype)
        scale = torch.tensor(self._input_scale, device=raw_x.device, dtype=raw_x.dtype)
        x_scaled = (raw_x - mean.unsqueeze(0)) / scale.unsqueeze(0)
        return self._network(x_scaled)

    def _regularization_penalty(
        self,
        *,
        l1_regularization: bool,
        l2_regularization: bool,
        options: _TrainingOptions,
    ) -> "torch.Tensor":
        penalty = torch.tensor(0.0, device=self._device)
        if l1_regularization:
            penalty = penalty + options.l1_lambda * sum(
                parameter.abs().sum() for parameter in self._network.parameters()
            )
        if l2_regularization:
            penalty = penalty + options.l2_lambda * sum(
                torch.sum(parameter**2) for parameter in self._network.parameters()
            )
        return penalty

    def _loss_on_tensor(
        self,
        x_tensor: "torch.Tensor",
        y_tensor: "torch.Tensor",
        *,
        l1_regularization: bool,
        l2_regularization: bool,
        options: _TrainingOptions,
    ) -> "torch.Tensor":
        predictions = self._network(x_tensor)
        loss = F.mse_loss(predictions, y_tensor)
        return loss + self._regularization_penalty(
            l1_regularization=l1_regularization,
            l2_regularization=l2_regularization,
            options=options,
        )

    def train(
        self,
        x: ArrayLike,
        y: ArrayLike,
        random_seed: Optional[int] = None,
        show_trace: bool = True,
        gpu_acceleration: str = "cuda",
        l1_regularization: bool = False,
        l2_regularization: bool = False,
        advanced_options: Optional[Dict[str, Any]] = None,
    ) -> "EasyMLP":
        """
        Train the model on the supplied sample.

        The training pipeline automatically performs:

        - a train/validation split
        - early stopping based on validation loss
        - a final fine-tuning phase on the full sample

        Advanced users can override these defaults through
        ``advanced_options``.
        """

        _require_torch()

        x_arr = _ensure_2d_numpy(x, name="x", expected_cols=self.in_dim)
        y_arr = _ensure_2d_numpy(y, name="y", expected_cols=self.out_dim)
        if x_arr.shape[0] != y_arr.shape[0]:
            raise ValueError("x and y must have the same number of rows.")
        if x_arr.shape[0] < 2:
            raise ValueError("At least two samples are required for training.")

        self._set_seed(random_seed)
        options = self._current_training_options(advanced_options)
        self._last_gpu_request = gpu_acceleration
        self._device = _select_device(gpu_acceleration)
        self._network.to(self._device)

        if options.standardize_inputs:
            self._input_mean = x_arr.mean(axis=0).astype(np.float32)
            self._input_scale = x_arr.std(axis=0).astype(np.float32)
            self._input_scale[self._input_scale < 1e-8] = 1.0
        else:
            self._input_mean = np.zeros(self.in_dim, dtype=np.float32)
            self._input_scale = np.ones(self.in_dim, dtype=np.float32)

        x_scaled = self._scale_inputs(x_arr).astype(np.float32)
        train_idx, val_idx = _split_indices(
            n_samples=x_arr.shape[0],
            validation_fraction=options.validation_fraction,
            seed=random_seed,
        )

        x_train = self._to_tensor(x_scaled[train_idx], requires_grad=False)
        y_train = self._to_tensor(y_arr[train_idx], requires_grad=False)
        x_val = self._to_tensor(x_scaled[val_idx], requires_grad=False) if len(val_idx) else None
        y_val = self._to_tensor(y_arr[val_idx], requires_grad=False) if len(val_idx) else None

        batch_size = min(int(options.batch_size), max(1, len(train_idx)))
        dataset = TensorDataset(x_train, y_train)
        shuffle = True
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

        optimizer = torch.optim.Adam(self._network.parameters(), lr=options.learning_rate)
        best_state = copy.deepcopy(self._network.state_dict())
        best_val = float("inf")
        best_epoch = 0
        epochs_without_improvement = 0
        self._training_history = []
        training_start = time.time()

        epoch_iterable: Iterable[int]
        if show_trace and tqdm is not None:
            epoch_iterable = tqdm(
                range(options.max_epochs),
                desc="EasyMLP train",
                leave=False,
            )
        else:
            epoch_iterable = range(options.max_epochs)

        for epoch in epoch_iterable:
            self._network.train()
            running_loss = 0.0
            seen = 0
            for batch_x, batch_y in loader:
                optimizer.zero_grad(set_to_none=True)
                batch_pred = self._network(batch_x)
                loss = F.mse_loss(batch_pred, batch_y)
                loss = loss + self._regularization_penalty(
                    l1_regularization=l1_regularization,
                    l2_regularization=l2_regularization,
                    options=options,
                )
                loss.backward()
                if options.gradient_clip_norm is not None:
                    torch.nn.utils.clip_grad_norm_(
                        self._network.parameters(),
                        max_norm=float(options.gradient_clip_norm),
                    )
                optimizer.step()
                batch_n = batch_x.shape[0]
                running_loss += float(loss.detach().cpu()) * batch_n
                seen += batch_n

            train_loss = running_loss / max(1, seen)

            self._network.eval()
            with torch.no_grad():
                if x_val is not None and y_val is not None:
                    val_loss = float(
                        self._loss_on_tensor(
                            x_val,
                            y_val,
                            l1_regularization=l1_regularization,
                            l2_regularization=l2_regularization,
                            options=options,
                        ).detach().cpu()
                    )
                else:
                    val_loss = train_loss

            self._training_history.append(
                {
                    "epoch": float(epoch + 1),
                    "train_loss": float(train_loss),
                    "val_loss": float(val_loss),
                }
            )

            if val_loss + options.min_delta < best_val:
                best_val = val_loss
                best_epoch = epoch + 1
                best_state = copy.deepcopy(self._network.state_dict())
                epochs_without_improvement = 0
            else:
                epochs_without_improvement += 1

            if show_trace and tqdm is None and (
                epoch == 0
                or (epoch + 1) % max(1, options.trace_every) == 0
                or epoch + 1 == options.max_epochs
            ):
                elapsed = time.time() - training_start
                avg = elapsed / float(epoch + 1)
                eta = avg * float(options.max_epochs - epoch - 1)
                print(
                    f"[EasyMLP] epoch={epoch + 1:4d}/{options.max_epochs} "
                    f"train_loss={train_loss:.6f} val_loss={val_loss:.6f} "
                    f"elapsed={elapsed:6.1f}s eta={eta:6.1f}s"
                )

            if epochs_without_improvement >= options.patience:
                break

        self._network.load_state_dict(best_state)

        if options.fine_tune_epochs > 0:
            full_x = self._to_tensor(x_scaled, requires_grad=False)
            full_y = self._to_tensor(y_arr, requires_grad=False)
            full_dataset = TensorDataset(full_x, full_y)
            full_loader = DataLoader(
                full_dataset,
                batch_size=min(batch_size, x_arr.shape[0]),
                shuffle=True,
            )
            fine_tune_optimizer = torch.optim.Adam(
                self._network.parameters(),
                lr=options.fine_tune_learning_rate,
            )
            fine_iterable: Iterable[int]
            if show_trace and tqdm is not None:
                fine_iterable = tqdm(
                    range(options.fine_tune_epochs),
                    desc="EasyMLP fine-tune",
                    leave=False,
                )
            else:
                fine_iterable = range(options.fine_tune_epochs)

            for epoch in fine_iterable:
                self._network.train()
                running_loss = 0.0
                seen = 0
                for batch_x, batch_y in full_loader:
                    fine_tune_optimizer.zero_grad(set_to_none=True)
                    batch_pred = self._network(batch_x)
                    loss = F.mse_loss(batch_pred, batch_y)
                    loss = loss + self._regularization_penalty(
                        l1_regularization=l1_regularization,
                        l2_regularization=l2_regularization,
                        options=options,
                    )
                    loss.backward()
                    if options.gradient_clip_norm is not None:
                        torch.nn.utils.clip_grad_norm_(
                            self._network.parameters(),
                            max_norm=float(options.gradient_clip_norm),
                        )
                    fine_tune_optimizer.step()
                    batch_n = batch_x.shape[0]
                    running_loss += float(loss.detach().cpu()) * batch_n
                    seen += batch_n

                if show_trace and tqdm is None and (
                    epoch == 0
                    or (epoch + 1) % max(1, options.trace_every) == 0
                    or epoch + 1 == options.fine_tune_epochs
                ):
                    print(
                        f"[EasyMLP] fine_tune_epoch={epoch + 1:4d}/{options.fine_tune_epochs} "
                        f"loss={running_loss / max(1, seen):.6f}"
                    )

        self._network.eval()
        self._trained = True
        self._regularization = {"l1": bool(l1_regularization), "l2": bool(l2_regularization)}
        self._training_summary = {
            "n_samples": int(x_arr.shape[0]),
            "n_train": int(len(train_idx)),
            "n_validation": int(len(val_idx)),
            "best_epoch": int(best_epoch),
            "best_validation_loss": float(best_val),
            "training_seconds": float(time.time() - training_start),
            "device": str(self._device),
            "fine_tune_epochs": int(options.fine_tune_epochs),
        }
        self._train_x = x_arr.copy()
        self._train_y = y_arr.copy()
        self._fitted_cache = self(x_arr)
        self._residual_cache = self._train_y - self._fitted_cache
        self._metrics = _compute_regression_metrics(self._train_y, self._fitted_cache)
        return self

    fit = train

    def _require_training_sample(self) -> None:
        if self._train_x is None or self._train_y is None:
            raise RuntimeError(
                "This method requires cached training data. Train the model first "
                "or load a serialized model that includes training data."
            )

    def fitted(self) -> np.ndarray:
        """Return fitted values on the full training sample."""
        self._require_training_sample()
        return np.asarray(self._fitted_cache, dtype=np.float32).copy()

    def residual(self) -> np.ndarray:
        """Return residuals on the full training sample."""
        self._require_training_sample()
        return np.asarray(self._residual_cache, dtype=np.float32).copy()

    def __call__(self, x: ArrayLike) -> np.ndarray:
        """
        Evaluate the model on one point or a batch of points.

        Parameters
        ----------
        x:
            Either a single point with shape ``(in_dim,)`` or a batch with
            shape ``(N, in_dim)``.
        """

        _require_torch()
        arr = np.asarray(x, dtype=np.float32)
        single = arr.ndim == 1
        if single:
            arr = _ensure_1d_numpy(arr, name="x", expected_len=self.in_dim)[None, :]
        else:
            arr = _ensure_2d_numpy(arr, name="x", expected_cols=self.in_dim)

        self._network.eval()
        with torch.no_grad():
            tensor = self._to_tensor(arr, requires_grad=False)
            prediction = self._forward_tensor(tensor).detach().cpu().numpy().astype(np.float32)
        return prediction[0] if single else prediction

    predict = __call__

    def _check_derivative_support(self, order: int) -> None:
        unsupported = [
            label
            for name, label in zip(self._activation_names, self.activations)
            if _ACTIVATION_REGISTRY[name]["order"] < order
        ]
        if unsupported:
            joined = ", ".join(unsupported)
            target = "Jacobians" if order == 1 else "Hessians"
            raise RuntimeError(
                f"{target} are not guaranteed to exist for the chosen activations: {joined}."
            )

    def jacobian(self, x: ArrayLike) -> np.ndarray:
        """Return the Jacobian matrix with shape ``(out_dim, in_dim)``."""
        _require_torch()
        self._check_derivative_support(order=1)
        point = _ensure_1d_numpy(x, name="x", expected_len=self.in_dim)
        tensor = self._to_tensor(point[None, :], requires_grad=True)
        output = self._forward_tensor(tensor)[0]

        rows = []
        for idx in range(self.out_dim):
            grad = torch.autograd.grad(
                output[idx],
                tensor,
                retain_graph=idx + 1 < self.out_dim,
                create_graph=False,
            )[0][0]
            rows.append(grad.detach().cpu().numpy())
        return np.stack(rows, axis=0).astype(np.float32)

    def hessian(self, x: ArrayLike) -> List[np.ndarray]:
        """Return one Hessian matrix per output component."""
        _require_torch()
        self._check_derivative_support(order=2)
        point = _ensure_1d_numpy(x, name="x", expected_len=self.in_dim)
        vector = self._to_tensor(point, requires_grad=True)

        def scalar_output(index: int):
            def fn(raw_point: "torch.Tensor") -> "torch.Tensor":
                return self._forward_tensor(raw_point.unsqueeze(0))[0, index]

            return fn

        hessians: List[np.ndarray] = []
        for idx in range(self.out_dim):
            hessian_tensor = torch.autograd.functional.hessian(scalar_output(idx), vector)
            hessians.append(hessian_tensor.detach().cpu().numpy().astype(np.float32))
        return hessians

    def summary(self) -> str:
        """
        Print and return a textual summary of the model.
        """

        param_count = int(sum(parameter.numel() for parameter in self._network.parameters()))
        lines = [
            "EasyMLP Summary",
            f"  trained           : {self._trained}",
            f"  input dimension   : {self.in_dim}",
            f"  output dimension  : {self.out_dim}",
            f"  hidden dims       : {self.hidden_dims}",
            f"  activations       : {self.activations}",
            f"  output spaces     : {self.out_spaces}",
            f"  monotonicity      : {self.monotonicity}",
            f"  parameters        : {param_count}",
            f"  random seed       : {self._random_seed}",
            f"  device            : {self._device}",
        ]
        if self._trained:
            lines.extend(
                [
                    f"  mse               : {self._metrics.get('mse', float('nan')):.6f}",
                    f"  mae               : {self._metrics.get('mae', float('nan')):.6f}",
                    f"  r2                : {self._metrics.get('r2', float('nan')):.6f}",
                    f"  n samples         : {self._training_summary.get('n_samples', 'n/a')}",
                    f"  train/val split   : "
                    f"{self._training_summary.get('n_train', 'n/a')}/"
                    f"{self._training_summary.get('n_validation', 'n/a')}",
                    f"  best epoch        : {self._training_summary.get('best_epoch', 'n/a')}",
                    f"  best val loss     : "
                    f"{self._training_summary.get('best_validation_loss', float('nan')):.6f}",
                    f"  training seconds  : "
                    f"{self._training_summary.get('training_seconds', float('nan')):.3f}",
                    f"  L1/L2 regularized : "
                    f"{self._regularization['l1']}/{self._regularization['l2']}",
                ]
            )
        lines.append("  architecture:")
        lines.append(f"    {self._network}")
        summary = "\n".join(lines)
        print(summary)
        return summary

    def serialize(self) -> Dict[str, Any]:
        """
        Return a JSON-compatible dictionary representation of the model.
        """

        _require_torch()
        payload = {
            "version": 1,
            "config": {
                "in_dim": self.in_dim,
                "out_dim": self.out_dim,
                "hidden_dims": list(self.hidden_dims),
                "activations": list(self.activations),
                "out_spaces": list(self.out_spaces),
                "monotonicity": copy.deepcopy(self.monotonicity),
                "advanced_options": self._default_training_options.as_dict(),
            },
            "trained": bool(self._trained),
            "random_seed": self._random_seed,
            "device_request": self._last_gpu_request,
            "regularization": copy.deepcopy(self._regularization),
            "input_mean": self._input_mean.tolist(),
            "input_scale": self._input_scale.tolist(),
            "metrics": copy.deepcopy(self._metrics),
            "training_summary": copy.deepcopy(self._training_summary),
            "training_history": copy.deepcopy(self._training_history),
            "state_dict": {
                name: value.detach().cpu().tolist()
                for name, value in self._network.state_dict().items()
            },
            "training_data": {
                "x": None if self._train_x is None else self._train_x.tolist(),
                "y": None if self._train_y is None else self._train_y.tolist(),
            },
        }
        return payload

    def load(self, payload: Dict[str, Any]) -> "EasyMLP":
        """
        Load model parameters from a dictionary produced by :meth:`serialize`.
        """

        _require_torch()
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary produced by serialize().")
        config = payload.get("config")
        if not isinstance(config, dict):
            raise ValueError("Invalid payload: missing 'config'.")

        advanced_options = config.get("advanced_options")
        self._default_training_options = _TrainingOptions().merged(advanced_options)
        self._configure(
            in_dim=int(config["in_dim"]),
            out_dim=int(config["out_dim"]),
            hidden_dims=config["hidden_dims"],
            activations=config["activations"],
            out_spaces=config["out_spaces"],
            monotonicity=config["monotonicity"],
        )

        reference_state = self._network.state_dict()
        restored_state = {}
        for name, reference_tensor in reference_state.items():
            if name not in payload.get("state_dict", {}):
                raise ValueError(f"Invalid payload: missing state tensor '{name}'.")
            restored_state[name] = torch.tensor(
                payload["state_dict"][name],
                dtype=reference_tensor.dtype,
                device=self._device,
            )
        self._network.load_state_dict(restored_state)
        self._network.to(self._device)
        self._network.eval()

        self._trained = bool(payload.get("trained", False))
        self._random_seed = payload.get("random_seed")
        self._last_gpu_request = payload.get("device_request", "none")
        self._regularization = copy.deepcopy(
            payload.get("regularization", {"l1": False, "l2": False})
        )
        self._input_mean = np.asarray(
            payload.get("input_mean", [0.0] * self.in_dim), dtype=np.float32
        )
        self._input_scale = np.asarray(
            payload.get("input_scale", [1.0] * self.in_dim), dtype=np.float32
        )
        self._metrics = copy.deepcopy(payload.get("metrics", {}))
        self._training_summary = copy.deepcopy(payload.get("training_summary", {}))
        self._training_history = copy.deepcopy(payload.get("training_history", []))

        training_data = payload.get("training_data", {})
        train_x = training_data.get("x")
        train_y = training_data.get("y")
        self._train_x = None if train_x is None else np.asarray(train_x, dtype=np.float32)
        self._train_y = None if train_y is None else np.asarray(train_y, dtype=np.float32)
        if self._train_x is not None and self._train_y is not None:
            self._fitted_cache = self(self._train_x)
            self._residual_cache = self._train_y - self._fitted_cache
        else:
            self._fitted_cache = None
            self._residual_cache = None
        return self

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "EasyMLP":
        """Construct an :class:`EasyMLP` instance from serialized data."""
        config = payload.get("config", {})
        model = cls(
            in_dim=int(config["in_dim"]),
            out_dim=int(config["out_dim"]),
            hidden_dims=config["hidden_dims"],
            activations=config["activations"],
            out_spaces=config["out_spaces"],
            monotonicity=config["monotonicity"],
            advanced_options=config.get("advanced_options"),
        )
        return model.load(payload)
