---
title: "Finite difference scheme: Monotonicity violation of a class of interpolations"
date: 2025-11-17T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

showSummary: true
summary: "Monotonicity condition can be violated when points are denoted by multiple grid points."

featureAsset: "img/feature_default.webp"
---

{{< katex >}}


The Barles–Souganidis (1991) convergence theorem states that a numerical scheme for a fully nonlinear second-order PDE converges uniformly to the unique viscosity solution provided the following conditions hold:
- Monotonicity
- Stability
- Consistency
- PDE that satisfies a comparison principle

While most conditions are automatically satisfied in many economic models, economists must be very careful with the monotonicity condition, which may fail in some cases and hard to detect at first glance.







## Notations

Let's consider the following PDE of \(v(x):\mathbb{R}^N\to\mathbb{R}\). For simplicity, I shut down all uncertainties (it is trivial to realize that adding diffusion term won't change the conclusion).

$$
\begin{aligned}
& \rho v(x) = u(x) + \sum_{i=1}^N \mu_i(x) \cdot \frac{\partial v}{\partial x_i}(x)
\end{aligned}
$$

Let's consider a grid \(\mathcal{X}\) over a subset of \(\mathbb{R}^N\). For a point \(x\in \mathbb\)







## Solution




## Reference

Barles and P. E. Souganidis. Convergence of approximation schemes for fully nonlinear second order equations. *Asymptotic analysis*, 4(3):271–. 283, 1991.

