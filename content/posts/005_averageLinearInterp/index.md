---
title: "Linearity of (multi-)linear interpolation under weighted averaging"
date: 2025-10-16T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

showSummary: true
summary: "Discusses a numerical issue in computing expected value function in dynamic programming."

featureAsset: "img/feature_default.webp"
---

{{< katex >}}

Consider a collection of functions \(\{f_i(x)\}_i\), each associated with a constant weight \(w_i\).  
The weighted average of these functions is:
$$
F(x) = \sum_i w_i f_i(x).
$$

Suppose each \(f_i(x)\) is interpolated on **the same grid** using (multi-)linear interpolation, yielding interpolants \(\hat{f}_i(x)\).  
We can then form two natural operations:

- **Operation A:**  
  $$
  G_A(x) = \sum_i w_i\,\hat{f}_i(x)
  $$

- **Operation B:**  
  $$
  G_B(x) = \widehat{F}(x) = \text{interpolant of } \sum_i w_i f_i(x)
  $$

---

## Are They Equivalent?

Yes — under the assumptions of:
1. identical interpolation grids,  
2. (multi-)linear interpolation, and  
3. constant weights \(w_i\) (independent of \(x\)),

these two operations are **mathematically identical** for all \(x\).

### Proof Sketch

Let \(\{x_j\}_j\) denote the grid nodes and \(\phi_j(x)\) the (multi-)linear basis (“hat”) functions.  
Each interpolant can be written as
$$
\hat{f}_i(x) = \sum_j f_i(x_j)\,\phi_j(x).
$$
Then,
$$
\widehat{F}(x)
= \sum_j \Big(\sum_i w_i f_i(x_j)\Big)\phi_j(x)
= \sum_i w_i \sum_j f_i(x_j)\phi_j(x)
= \sum_i w_i\,\hat{f}_i(x).
$$
Hence, \( G_A(x) = G_B(x) \).

---

## When the Equivalence Fails

The linearity breaks if **any** of the following hold:
- the weights \(w_i\) depend on \(x\);
- different grids or interpolation stencils are used for each \(f_i\);
- interpolation is nonlinear (e.g., monotone cubic, clamped, or spline with slope limiters);
- extrapolation outside the grid domain uses nonlinear rules.

---

## Why this matters?

When solving a Bellman equation, the main computational bottleneck is optimizing the Lagrangian or Q-function at each grid point, which requires evaluating the expected value function millions or even billions of times. Direct computation is often prohibitively slow.  

A common workaround is to precompute an interpolant of the expected value function  

$$
\overline{v}(x,z) := \mathbb{E}\{v(x',z') \mid z\},
$$
  
so that it can be evaluated cheaply everywhere.  

However, this post highlights a subtle numerical pitfall: treating the interpolated function as the true one can distort the shape of the expected value function when nonlinear interpolation (e.g., cubic splines) is used. Such overshooting in local regions of the state space can lead to unexpected or unstable behavior in the resulting solution.