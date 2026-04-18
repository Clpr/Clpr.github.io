---
title: "Standard notations for my notes about HJB equation"
date: 2026-04-01T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

tags: ["GE model","HJB","PDE"]

showSummary: true
summary: "A collection of standard notations for all of my notes about HJB equation and numerical PDE."

featureAsset: "img/feature_default.webp"
---

{{< katex >}}


## 1. Generic 

Many notations are consistent with the textbook by Evans, and the textbook by Yong & Zhou, e.g.

|Notation|Definition|Notes|
|----|-----|----|
|\(\mathbb{R}^{m\times n}\)|Space of \(m\times n\) matrix||
|\(\mathbf{0}_{m\times n},\mathbf{1}_{m\times n}\)|All-zero/all-one matrix of size \(m\times n\)||
|\(\mathbf{I}_{m}\)|Identity matrix of size \(m\times m\)||
|\(x\in\mathbb{R}^n\)|\(n\)-dim real point/vector/column vector||
|\(x[j] \in\mathbb{R},j=1,\dots,n\)|The \(j\)-th element of \(x\)||
|\(\partial \mathcal{X}\)|Boundary of open space \(\mathcal{X}\)||
|\(\text{D}^\alpha u(x)\)|Differentiation operator of multi-index \(\alpha\)||
|\(g[u(\cdot)]\)|Functional \(g\) of real valued function \(u\)||
|\([x]^+:=\max\{0,x\},[x]^-:=\min\{x,0\}\)|Truncation operator||
|\(\iota_i := (0,0,\dots,1,0,\dots)\)|Unit vector with only the \(i\)-th element as 1||
|\(\mathcal{L}_x[u](x,z)\)|2nd-order infinisimal generator about \(x\)||
|\(\{x_t\}_{t=0}^T\)|Sequence or discrete time process||
|\((\Omega,\mathcal{F}_t,\{\mathcal{F}_t\}_{t\geq0},\mathbf{P})\)|Filtered probability space||
|\(L^p_\mathcal{F}(0,T;H)\)|Set of all \(H\)-valued, \(\{\mathcal{F}_t\}_{t\geq0}\)-adapted processes \(X(\cdot)\) such that \(\mathbb{E} \int_0^T \| X(t)\|^p_H \text{d} t < \infty\), and \(L^p_\mathcal{F}(0,T;H)\) means bounded processes, and by \(L^p_\mathcal{F}(\Omega;C([0,T];H))\) the set of all \(\dots\) continuous processes \(X(\cdot)\) such that \(\mathbb{E}\left\{ \sup_{t\in[0,T]} \| X(t) \|^p_H \right\}<\infty\)||
|\(\mathcal{V}[0,T]\)|The set of all measurable functions \(u:[0,T]\to U\)||
|\(\mathcal{V}_{ad}[0,T]\)|The set of deterministic admissible controls \(u:[0,T]\times \Omega\to U\)||
|\(\mathcal{U}^s_{ad}[0,T]\)|The set of (stochastic) strong admissible controls||
|\(\mathcal{U}^w_{ad}[0,T]\)|The set of (stochastic) weak admissible controls||
|\(C([0,T];\mathbb{R}^n)\)|The set of all continuous functions \(\varphi:[0,T]\to\mathbb{R}^n\)||
|\([\underline{x}_i,\overline{x}_i]^n:=\prod_{i=1}^n [\underline{x}_i,\overline{x}_i]\)|A rectangular space with anisotropic lower and upper bounds||




## 2. Optimal control problems

### 2.1 Strong formulation


Consider stochastic control problem of strong formulation:

$$
\begin{aligned}
& \max_{c(\cdot)\in\mathcal{U}^s_{ad}[0,T]} V[c(\cdot)] \\
\text{s.t. }& \text{d}x(t) = \mu(t,x(t),c(t))\text{d}t + \sigma(t,x(t),c(t))\text{d}W(t) \\
& x(0) = x_0 \in\mathbb{R}^{n} \\
& V[c(\cdot)] := \mathbb{E}_0 \int_0^T u(t,x(t),c(t))\text{d} t + h(x(T)) \\
\end{aligned}
$$

where

- \(\text{d}x(t)\) is controlled state process
- \(W(\cdot)\) is an \(\mathbb{R}^m\)-valued Brownian motion
- \(\mu \in\mathbb{R}^{n}\) is drift vector
- \(\sigma \in\mathbb{R}^{n\times m}\) is diffusion/volatility matrix
- \(c(\cdot)\) is the control, where each \(c(t)\) is a \(\mathbb{R}^k\)-valued vector
- \(u(\cdot)\mapsto \mathbb{R}\) is flow utility (or cost function in minimization context)
- \(h(\cdot):\mathbb{R}^{n}\to\mathbb{R}\) is terminal value function. It implies transversality condition as \(T\to\infty\)

### 2.2 HJB equation

Corresponding to the optimal control problem in Section 2.1, an HJB equation with discounting \(\rho\) often looks like:

$$
\begin{aligned}
& \rho v(t,x(t)) = \max_{c(t)\in\mathcal{U}^s_{ad}(t)} u(t,x(t),c(t)) + \mathcal{L}_{t,x}[v](t,x(t),c(t)) \\
& \mathcal{L}_{t,x}[v](t,x(t),c(t)) = \left< \text{D}_{t,x}v(t,x(t)), \mu(t,x(t),c(t)) \right> + \frac{1}{2}\text{tr}\left\{ \sigma(\dots)^T \cdot \text{D}^2_{t,x} v(\dots) \cdot \sigma(\dots)  \right\}
\end{aligned}
$$



## 3. Grid space and node arithmetic

### 3.1 Generic grid space

Let \(\mathcal{X}\subset \mathbb{R}^n\) be an open subspace to discretize. Consider total \(N_{interior}\) unique grid points (nodes) from \(\mathcal{X}\). The set

$$
\hat{\mathcal{X}}_{N_{interior}} = \{x^i \in\mathcal{X} : i=1,\dots,N_{interior} \}
$$

is the interior grid space of \(\mathcal{X}\). Meanwhile, consider another total \(N_{boundary}\) unique grid points (nodes) from \(\partial\mathcal{X}\). The set

$$
\partial\hat{\mathcal{X}}_{N_{boundary}} = \{x^i \in\partial\mathcal{X} : i=1,\dots,N_{boundary} \}
$$

is the boundary grid space of \(\mathcal{X}\).

Usually, we do not separately manage the two grid spaces[^2] but work on

$$
\hat{\mathcal{X}}\left( \mathcal{X}; N \right) := \hat{\mathcal{X}}_{N_{interior}} \cup \partial\hat{\mathcal{X}}_{N_{boundary}}
$$

where \(N = N_{interior} + N_{boundary}\).

### 3.2 Node arithmetic

In general, we can sort the nodes in a specific order and write:

$$
\hat{\mathcal{X}}\left( \mathcal{X}; N \right) = \left( x^1, x^2, \dots, x^{i}, \dots, x^{N}   \right)
$$

where index \(i\) locates a specific node in the (sorted) grid space. By different specialized grid design, more arithmetic can be defined for convenience then.

Meanwhile, we define _stacking_ operation that converts the set of points to a \(N\times n\) matrix:

$$
\mathbf{X}\left( \hat{\mathcal{X}}\left( \mathcal{X}; N \right) \right) = \begin{bmatrix}
(x^1)' \\ \vdots \\ (x^N)'
\end{bmatrix}
$$


#### 3.2.a (Anisotropic) uniform grid

An anisotropic uniform grid \(\hat{\mathcal{X}}\left([\underline{x}_i,\overline{x}_i]^n_{i=1};\mathbf{N}=(N^1,\dots,N^n\right))\) is a grid space:

- defined on a rectangular space
- along every dimenison, it has \(N^i>1\) even-spaced nodes where the grid step size along dimension \(i\) is \(\Delta x[i] = \frac{\overline{x}_i-\underline{x}_i}{N^i-1}\)
- has total \(\|\mathbf{N}\|=\prod_{i=1}^n N^i\) node points

Let \(\mathbf{i}=(i^1,i^2,\dots,i^n)\) be a Cartesian index that queries a unique node point \(x^\mathbf{i}\) from \(\hat{\mathcal{X}}\left([\underline{x}_i,\overline{x}_i]^n_{i=1};\mathbf{N}\right)\) where \(i^j=1,\dots,N^j\) and \(x^\mathbf{i}[i^j] = \underline{x}_j + (i^j-1)\Delta x[j]\).

Let \(\mathbf{i}'\) be another Cartesian index that only has the \(j\)-th element different from \(\mathbf{i}\). Then in convention, if the the \(j\)-th element of \(\mathbf{i}'\) is greater than or equal to the \(j\)-th element of \(\mathbf{i}\), then \(x^{\mathbf{i}'}[j] \geq x^{\mathbf{i}}\) holds. In other words, the grid is dimension-wise ascendingly sorted.

In practice, such a uniform grid is often represented by an \(n\)-dim array. To stack the grid space, without special instruction, we use column-major (anti-lexicographical order) order which is the opposite of standard lexicographical (row-major) order in Python and other languages. For example,

$$
\mathbf{X}\left(\hat{\mathcal{X}}\left( [1,2]^3 ; (2,2,2) \right)\right)= \begin{bmatrix}
1 & 1 & 1 \\
2 & 1 & 1 \\
1 & 2 & 1 \\
2 & 2 & 1 \\
1 & 1 & 2 \\
2 & 1 & 2 \\
1 & 2 & 2 \\
2 & 2 & 2 \\
\end{bmatrix}
$$


The lattice structure of uniform grid allows us to "move" on the grid along specific direction \(\vec{v}\in\mathbb{R}^{n}\) where \(\vec{v}\) is a direction/velocity vector. The movement operation can be written as \(\mathbf{i} + d\cdot \vec{v}\) where \(d\in\mathbb{R}\) is the step length. Please be careful that the operation does not necessarily moves to another grid point but may fall into some off-grid points.

A special case is： \(\vec{v} = \iota_j\) where \(\iota_j\) is the unit vector along dimension \(j\)； and \(d = \Delta x[j]\) is the grid step size. In this case, \(\mathbf{i} + \Delta x[j] \cdot \iota_j\) always arrives at another grid point[^1]. And trivially, any direction \(\vec{v}\) can be represented by a weighted summation of \(n\) unit vectors.



### 3.3 (Linear) stencil

Consider linear combination of function values at all nodes in grid space \(\hat{\mathcal{X}}\left( \mathcal{X}; N \right)\)

$$
f\left( \mathbf{a} ; \hat{\mathcal{X}}\left( \mathcal{X}; N \right) \right) := \left< \mathbf{a}, \hat{\mathcal{X}}\left( \mathcal{X}; N \right) \right> = \sum_{j=1}^N a[j] \cdot u(x^j)
$$

where \(\mathbf{a} \in\mathbb{R}^{N}\) is weight vector. \(f(\cdot)\) is linear so that all standard arithmetic applies.

In some scenarios (e.g. finite difference approximation of function derivatives), a large amount of similar but different \(f\) need to be constructed and evaluated for many times. These differential \(f\), usually, only differ in \(\mathbf{a}\) and it can be decomposed into a scalar coefficient varying by \(f\) and a constant _stencil_ vector shared by all differential \(f\), i.e. 

$$
\mathbf{a}(\beta) = \beta \cdot \tilde{\mathbf{a}}
$$

Here the shared stencil vector \(\tilde{\mathbf{a}}\) serves like a "template". One only needs to construct the stencil once, then compute \(\beta\) for every \(f\), which greatly reduces computation burden.

In practice, \(\mathbf{a}\) is often sparse: there might be millions of nodes but only 2 or 3 nodes have non-zero coefficients. Then, a short vector (typically integer vector) is used for simplicity. e.g. 3-point central difference approximation of \(\partial^2 u(x)/\partial x[j]^2\) at a grid point \(x^\mathbf{i}\) in a uniform grid.

$$
\frac{\partial^2 u(x)}{\partial x[j]^2} \approx \underbrace{ \frac{1}{\Delta x[j]^2}  }_{\text{coefficient}}  \underbrace{ \begin{bmatrix}
1 & -2 & 1
\end{bmatrix} }_{\text{stencil}} \cdot  \begin{bmatrix}
u(x^{\mathbf{i}-\Delta x[j] \cdot \iota_j}) \\
u(x^{\mathbf{i}}) \\
u(x^{\mathbf{i}+\Delta x[j] \cdot \iota_j})
\end{bmatrix}
$$




















[^1]: WLOG, we do not list the case of jumping to a point outside \(\partial\mathcal{X}\). It is trivial to manage the boundary check.

[^2]: Unless when we are handling boundary conditions.