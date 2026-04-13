# EasyMLP

`EasyMLP` is a single-file Python module for building and training customized
multi-layer perceptrons in the PyTorch ecosystem. It is designed for
high-dimensional function approximation problems of the form

`f(x): R^n -> R^m`

and supports architecture-level monotonicity constraints, output-space
constraints, automatic validation splitting, early stopping, and hidden
fine-tuning.

The repository consists of four main files:

- `easymlp.py`: the full implementation
- `test.py`: unit tests
- `README.md`: usage guide
- `demo_easymlp.ipynb`: a notebook demo with fit visualizations

## Features

- Single entry point: `EasyMLP`
- Works with scalar or vector outputs
- Supports common activation functions such as `ReLU`, `Leaky ReLU`,
  `Sigmoid`, `Tanh`, `Softplus`, `ELU`, and `SELU`
- Output-space transforms per output dimension:
  `real`, `positive`, `negative`, `[0,1]`, `[-1,1]`
- Monotonicity enforced by network architecture instead of soft penalties
- Automatic internal train/validation split and early stopping
- Automatic final fine-tuning on the full sample
- Serialization and restoration through JSON-compatible dictionaries
- Jacobian and Hessian evaluation for smooth activation choices

## Installation

Install the main dependencies first:

```bash
pip install numpy torch
```

Optional:

```bash
pip install tqdm
```

`tqdm` is only used for nicer progress bars. Without it, `EasyMLP` falls back
to plain text training traces.

## Quick Start

```python
import numpy as np

from easymlp import EasyMLP

rng = np.random.default_rng(1)
X = rng.uniform(0.0, 1.0, size=(500, 2)).astype(np.float32)
Y = np.column_stack(
    [
        np.exp(0.8 * X[:, 0] + 0.4 * X[:, 1]),
        1.5 * X[:, 0] - 0.25 * X[:, 1] + 0.1,
        1.0 / (1.0 + np.exp(-(X[:, 0] - X[:, 1]))),
    ]
).astype(np.float32)

model = EasyMLP(
    in_dim=2,
    out_dim=3,
    hidden_dims=[256, 128, 64],
    activations=["Softplus", "Tanh", "Sigmoid"],
    out_spaces=["positive", "real", "[0,1]"],
    monotonicity=[1, 0, -1],
)

model.train(
    x=X,
    y=Y,
    random_seed=42,
    show_trace=True,
    gpu_acceleration="cuda",
    l1_regularization=False,
    l2_regularization=True,
)

model.summary()

print(model([0.2, 0.8]))
print(model(X[:5]))
print(model.jacobian([0.2, 0.8]))
print(model.hessian([0.2, 0.8]))
```

## Notebook Demo

For a more visual walkthrough, open [demo_easymlp.ipynb](/Users/tianhaozhao/Desktop/test-MLP-codex/demo_easymlp.ipynb).

The notebook:

- generates a synthetic two-output regression problem
- trains `EasyMLP` with monotonicity constraints
- visualizes predicted-vs-actual fit
- plots residual distributions
- shows a one-dimensional slice of the fitted function to illustrate monotone behavior

The plotting cells use `matplotlib`, so make sure it is installed in the environment you use to run the notebook.

## Monotonicity Convention

`EasyMLP` supports two monotonicity formats.

### 1. Simple per-output format

This matches the example in the prompt.

```python
monotonicity = [1, 0, -1]
```

Interpretation:

- output 0 is increasing in all input dimensions
- output 1 is unconstrained
- output 2 is decreasing in all input dimensions

### 2. Partial monotonicity matrix

For finer control, provide an `out_dim x in_dim` matrix.

```python
monotonicity = [
    [1, 0],   # output 0: increasing in x0, unconstrained in x1
    [-1, 1],  # output 1: decreasing in x0, increasing in x1
]
```

This is the more expressive option when only some coordinates must be
monotone.

## Output Spaces

Each output dimension can be mapped into a target space:

- `"real"`: unconstrained real values
- `"positive"`: strictly positive outputs
- `"negative"`: strictly negative outputs
- `"[0,1]"`: values constrained to the unit interval
- `"[-1,1]"`: values constrained to the symmetric unit interval

These transforms are built into the network output layer automatically.

## Training Pipeline

Calling `model.train(...)` does more than just run gradient descent:

- scales the input variables by default
- splits the sample into training and validation subsets
- trains with Adam
- keeps the best validation checkpoint
- fine-tunes the selected model on the full sample

All of that is automatic for standard users.

## Advanced Training Options

Advanced users can override the hidden training pipeline with the
`advanced_options` dictionary. You can supply it either in the constructor for
default behavior or in `model.train(...)` for a specific training run.

Supported keys:

- `validation_fraction`
- `max_epochs`
- `learning_rate`
- `batch_size`
- `patience`
- `min_delta`
- `fine_tune_epochs`
- `fine_tune_learning_rate`
- `standardize_inputs`
- `l1_lambda`
- `l2_lambda`
- `gradient_clip_norm`
- `trace_every`

Example:

```python
model = EasyMLP(
    in_dim=2,
    out_dim=1,
    hidden_dims=[64, 32],
    activations=["Softplus", "Tanh"],
    out_spaces=["positive"],
    monotonicity=[1],
    advanced_options={
        "validation_fraction": 0.15,
        "max_epochs": 300,
        "patience": 30,
        "fine_tune_epochs": 50,
    },
)
```

## Serialization

`EasyMLP.serialize()` returns a JSON-compatible dictionary that contains:

- model architecture metadata
- hidden training configuration
- parameter tensors converted to plain lists
- scaler statistics
- cached training sample and fitting diagnostics when available

Round-trip example:

```python
payload = model.serialize()

restored = EasyMLP(
    in_dim=2,
    out_dim=3,
    hidden_dims=[256, 128, 64],
    activations=["Softplus", "Tanh", "Sigmoid"],
    out_spaces=["positive", "real", "[0,1]"],
    monotonicity=[1, 0, -1],
)
restored.load(payload)
```

You can also use:

```python
restored = EasyMLP.from_dict(payload)
```

## Derivatives

For smooth activation choices, you can evaluate:

- `model.jacobian(x)` returning an `(out_dim, in_dim)` array
- `model.hessian(x)` returning a list of `out_dim` Hessian matrices

If the model uses non-smooth activations such as `ReLU` or `Leaky ReLU`,
derivative methods raise an error because the derivatives are not globally
well-defined.

## Running Tests

```bash
python test.py
```

If PyTorch is not installed, the tests are skipped with a clear message.
