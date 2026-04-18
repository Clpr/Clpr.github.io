# Smolyak Polynomial Interpolation in Practice

`smolyakpoly.py` is a single-file Python module for anisotropic Smolyak polynomial interpolation of scalar-valued functions \(f : \mathbb{R}^n \to \mathbb{R}\). It is built around nested Clenshaw-Curtis grids, Chebyshev polynomial basis functions, implicit domain normalization, and an interface that follows standard basis-coefficient interpolation language.

This note is written as a compact blog post for people who want both the mathematical picture and the implementation intuition.

## 1. Introduction

The central problem is straightforward: given a function \(f(x)\) defined on a rectangular domain
$$
\Omega = [a_1, b_1] \times \cdots \times [a_n, b_n],
$$
we want an approximation \(\hat f(x)\) that is accurate, cheap to evaluate, differentiable, and practical in moderately high dimensions.

If one uses a full tensor grid, the number of support nodes grows exponentially with dimension. Smolyak’s construction reduces that curse-of-dimensionality pressure by keeping only a carefully selected subset of tensor-product components.

### Domain normalization

Chebyshev interpolation is naturally defined on the hypercube \([-1,1]^n\), so each coordinate is transformed from the user domain into the normalized cube:

$$
z_i = \frac{2x_i - (a_i + b_i)}{b_i - a_i}, \qquad i = 1, \dots, n.
$$

Equivalently, the inverse map is

$$
x_i = \frac{b_i - a_i}{2} z_i + \frac{a_i + b_i}{2}.
$$

This is why the module accepts lower and upper bounds from the user but still builds the interpolation machinery in normalized coordinates.

### Chebyshev basis

The underlying one-dimensional basis is the Chebyshev family \(T_k(z)\), defined by

$$
T_k(z) = \cos(k \arccos z), \qquad z \in [-1,1].
$$

In multiple dimensions, a tensor-product basis function associated with a multi-degree \(\nu = (\nu_1, \dots, \nu_n)\) is

$$
\Psi_{\nu}(z) = \prod_{i=1}^n T_{\nu_i}(z_i).
$$

The interpolant is then written in basis-coefficient form:

$$
\hat f(z) = \sum_{\nu \in \mathcal{A}} c_{\nu} \, \Psi_{\nu}(z),
$$

where \(\mathcal{A}\) is the selected Smolyak basis index set and \(c_{\nu}\) are interpolation coefficients.

### Nested Clenshaw-Curtis / Chebyshev-Gauss-Lobatto nodes

The one-dimensional grids are nested. At level \(i\), the module uses:

$$
\mathcal{X}^{(1)} = \{0\},
$$

$$
\mathcal{X}^{(2)} = \{-1, 1\},
$$

and for \(i \ge 3\),

$$
\mathcal{X}^{(i)} = \left\{ \cos\left(\frac{\pi k}{m_i - 1}\right) : k = 0, \dots, m_i - 1 \right\},
\qquad
m_i = 2^{i-1} + 1.
$$

Because these grids are nested, sparse-grid assembly can reuse nodes rather than duplicating them. That nesting is one of the main reasons Smolyak interpolation is computationally attractive.

### The Smolyak idea

Let \(\ell = (\ell_1, \dots, \ell_n)\) be a multi-index of one-dimensional levels. For each \(\ell_i\), define a one-dimensional incremental basis block and a one-dimensional incremental node block. Smolyak interpolation constructs a sparse union of tensor products over admissible multi-indices instead of taking the entire tensor grid.

In the isotropic case, one often writes the admissible set as

$$
\mathcal{I}(n,\mu)
=
\left\{
\ell \in \mathbb{N}^n :
\ell_i \ge 1,\;
n \le |\ell|_1 \le n + \mu
\right\},
$$

where \(\mu\) is the accuracy parameter.

In the anisotropic case implemented here, each dimension also has a user-specified maximum level \(L_i\), so the admissible set becomes

$$
\mathcal{I}_{\text{aniso}}(n,\mu,L)
=
\left\{
\ell \in \mathbb{N}^n :
1 \le \ell_i \le L_i,\;
n \le |\ell|_1 \le n + \mu
\right\}.
$$

This is a very practical compromise. The accuracy parameter controls the global sparsity rule, while the per-dimension caps \(L_i\) let the user invest more grid depth in some coordinates than others.

### Interpolation as a linear system

Once the sparse grid nodes \(z^{(1)}, \dots, z^{(M)}\) and basis functions \(\Psi_{\nu_1}, \dots, \Psi_{\nu_M}\) are fixed, interpolation becomes a square linear system:

$$
\begin{bmatrix}
\Psi_{\nu_1}(z^{(1)}) & \cdots & \Psi_{\nu_M}(z^{(1)}) \\
\vdots & \ddots & \vdots \\
\Psi_{\nu_1}(z^{(M)}) & \cdots & \Psi_{\nu_M}(z^{(M)})
\end{bmatrix}
\begin{bmatrix}
c_{\nu_1} \\
\vdots \\
c_{\nu_M}
\end{bmatrix}
=
\begin{bmatrix}
f(z^{(1)}) \\
\vdots \\
f(z^{(M)})
\end{bmatrix}.
$$

If we call the matrix \(B\), the coefficient vector \(c\), and the nodal values \(y\), then

$$
Bc = y.
$$

This viewpoint is important because it explains the whole user-facing API:

- `basis(x)` evaluates rows of \(B\)-like basis matrices at new points.
- `coef()` returns \(c\).
- `update(ynew)` solves the same system again with a new right-hand side on the same grid.
- `__call__(x)` computes \( \hat f(x) = \Phi(x)c \), where \(\Phi(x)\) is the basis row or basis matrix at \(x\).

### Why derivatives are cheap

Because the interpolant is a polynomial in Chebyshev basis form, derivatives are analytic. For a basis function
$$
\Psi_{\nu}(z) = \prod_{i=1}^n T_{\nu_i}(z_i),
$$
the partial derivative with respect to coordinate \(z_j\) is

$$
\frac{\partial \Psi_{\nu}}{\partial z_j}(z)
=
T'_{\nu_j}(z_j)\prod_{i \ne j} T_{\nu_i}(z_i),
$$

and second derivatives follow similarly:

$$
\frac{\partial^2 \Psi_{\nu}}{\partial z_j^2}(z)
=
T''_{\nu_j}(z_j)\prod_{i \ne j} T_{\nu_i}(z_i),
$$

$$
\frac{\partial^2 \Psi_{\nu}}{\partial z_j \partial z_k}(z)
=
T'_{\nu_j}(z_j)T'_{\nu_k}(z_k)\prod_{i \ne j,k} T_{\nu_i}(z_i).
$$

Then the Jacobian and Hessian of \(\hat f\) are just coefficient-weighted sums of these derivative basis terms. The module also applies the chain rule to convert derivatives from normalized coordinates back to the user domain.

## 2. Implementation

The design philosophy of `smolyakpoly.py` is simple: make the sparse-grid structure explicit, make basis-coefficient access first-class, and do the expensive setup work once so repeated evaluation is cheap.

### A single-file module, but not a black box

The module intentionally exposes the essential interpolation primitives:

- `nodes(normalized=False)` returns the sparse-grid support set.
- `fit(f)` evaluates the target function on the support nodes and solves for coefficients.
- `update(values)` skips function evaluation and recomputes coefficients from nodal values directly.
- `basis(x)` returns the basis matrix at arbitrary points.
- `coef()` returns the coefficient vector.
- `jacobian(x)` and `hessian(x)` evaluate exact derivatives of the interpolating polynomial.

This mirrors the standard numerical interpolation workflow rather than hiding everything inside one opaque prediction method.

### How the sparse grid is built

There are two parallel constructions:

1. The sparse-grid nodes are assembled from incremental Clenshaw-Curtis node blocks.
2. The polynomial basis is assembled from matching incremental Chebyshev degree blocks.

Those two pieces are aligned so that the final interpolation matrix is square. Duplicate nodes are removed deterministically, so node ordering stays invariant across repeated calls to `nodes()`. That stability matters for reproducibility and for the `update()` workflow.

### Why the implementation is efficient

The module is efficient for several concrete reasons.

First, it uses nested Clenshaw-Curtis rules. This means higher levels reuse many lower-level points, which cuts down the number of distinct support nodes compared with naive tensor construction.

Second, it precomputes the basis matrix on the sparse grid and LU-factorizes it once. After that, solving for coefficients is just a linear solve with a cached factorization:

$$
c = B^{-1} y
$$

in conceptual notation, or more practically an LU solve. This is exactly why `update(ynew)` is fast: the grid and matrix structure are fixed, so only the right-hand side changes.

Third, basis, Jacobian, and Hessian evaluation all share the same recursive Chebyshev machinery. The module computes \(T_k\), \(T_k'\), and \(T_k''\) by recurrence, which avoids repeatedly calling slower transcendental formulas point-by-point.

Fourth, the domain transformation is implicit and vectorized. Users work in their original rectangular domain, while the module performs the normalized-coordinate bookkeeping internally.

Fifth, `fit()` supports parallel nodal function evaluation through `n_jobs`. For expensive user-supplied functions, that can reduce wall-clock time materially even though the interpolation logic itself remains NumPy/SciPy based.

### Why this is a good fit for Smolyak interpolation

Smolyak interpolation is most attractive when:

- dimension is too high for dense tensor grids,
- the target function is smooth enough for polynomial approximation,
- derivatives are useful,
- one wants an explicit surrogate rather than a purely local interpolator.

This module leans into that use case. It does not try to be a general-purpose machine learning framework. Instead, it gives a compact and transparent sparse-grid polynomial interpolant with inspectable nodes, inspectable coefficients, and exact derivative formulas.

### Practical trade-offs

No sparse-grid method escapes dimensionality entirely. If one pushes dimension, level caps, and accuracy all upward at once, node counts and solve costs will still grow quickly. The anisotropic design is therefore not just a mathematical detail; it is a practical control knob. By allocating deeper levels only where they matter, one often gets much better efficiency than a symmetric grid would provide.

That same philosophy appears in the companion notebooks:

- `smolyakpoly_demo.ipynb` visualizes interpolation quality, gradient quality, and Hessian quality.
- `smolyakpoly_benchmark.ipynb` measures runtime and approximation error across dimension and accuracy sweeps.

Together, the code and notebooks make a useful workflow: build a sparse interpolant, inspect its node set and coefficients, validate the approximation, and then use it as a fast differentiable surrogate.

## 3. Reference

- Judd, Kenneth L., Lilia Maliar, Serguei Maliar, and Rafael Valero. *Smolyak Method for Solving Dynamic Economic Models: Lagrange Interpolation, Anisotropic Grid and Adaptive Domain*. Econometrica. PDF link provided by the user: <https://web.stanford.edu/~maliars/Files/NBER19326.pdf>
