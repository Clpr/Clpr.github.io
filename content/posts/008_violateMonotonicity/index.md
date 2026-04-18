---
title: "Finite difference scheme: Monotonicity violation of a class of interpolations"
date: 2026-04-04T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

tags: ["GE model","HJB","PDE"]

showSummary: true
summary: "Monotonicity condition can be violated when points are denoted by multiple grid points."

featureAsset: "img/feature_default.webp"
---

{{< katex >}}


The Barles–Souganidis (1991) convergence theorem states that a finite difference scheme for a fully nonlinear second-order PDE converges uniformly to the unique viscosity solution provided the following conditions hold:
- Monotonicity
- Stability
- Consistency
- PDE that satisfies a comparison principle

While most conditions are automatically satisfied in many economic models, economists must be very careful with the monotonicity condition, which may fail in some cases and hard to detect at first glance.



Before diving into technical details, let's setup a generic problem and formalize notations.



## 1. Notations

### 1.1 Boundary problem

Consider HJB equation, which is a 2nd-order non-linear PDE, looking like:
$$
\begin{aligned}
& \rho v(x) = u + \mathcal{L}_x[v] \\
& \mathcal{L}_x[v] := \left<\nabla v(x), \mu  \right> + \frac{1}{2}\text{tr}\left\{ \sigma^T \cdot \nabla^2 v(x) \cdot \sigma    \right\} \\
& x \in \mathcal{X} \subset \mathbb{R}^n \\
& v\in\mathbb{R} \\
& \nabla v(x) \in\mathbb{R}^n, \nabla^2 v(x)\in\mathbb{R}^{n\times n} \\
& u \in \mathbb{R} \\
& \mu \in \mathbb{R}^{n}, \sigma \in\mathbb{R}^{n\times m} \\
& \text{d}x = \mu \cdot \text{d}t + \sigma \cdot \text{d}W, W\in\mathbb{R}^{m}
\end{aligned}
$$
where 
- \(\rho\) is discounting rate
- \(n\) is not necessary to be equal to \(m\)
- \(u = u(x,v(x),\nabla v(x),\nabla^2 v(x))\) is instantaneous payoff term that can be a function of \(x\), function value at \(x\), derivatives and Hessian at \(x\)
- \(\mu = \mu(x,v(x),\nabla v(x),\nabla^2 v(x))\) is drift term that can be a function
- \(\sigma = \sigma(x,v(x),\nabla v(x),\nabla^2 v(x))\) is diffusion/volatility matrix that can be a function

Meanwhile, also consider boundary conditions up to 1st order:

$$
b(x,v(x),\nabla v(x)) = \mathbf{0}_{2^n}, x \in \partial\mathcal{X}
$$

### 1.2 Grid space & index algebra


TBD




### 1.3 Monotonic numerical scheme


#### 1.3.1 Monotonic scheme


The Barles–Souganidis (1991) theorem requires monotonic scheme for local convergence. 


#### 1.3.1 Explicit (Euler forward) scheme


#### 1.3.2 Fully implicit (Euler backward) scheme










## Solution




## Reference

Barles and P. E. Souganidis. Convergence of approximation schemes for fully nonlinear second order equations. *Asymptotic analysis*, 4(3):271–. 283, 1991.

