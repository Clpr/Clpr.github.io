---
title: "Discretize OU process over non-integer time step"
date: 2025-11-18T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

showSummary: true
summary: "Approximate OU process with Markov chain when time step is non-integer"

featureAsset: "img/feature_code.webp"
---

{{< katex >}}


When applying some kinds of semi-Lagrangian (SL) schemes, it is required to discretize exogenous processes over a small time step \(\Delta t \neq 1\) as a finite state Markov chain on a pre-determined grid. Let's consider the following OU process:

$$
\begin{aligned}
\text{d} X = \kappa(\mu - X) \text{d} t + \sigma \text{d} W, \kappa > 0
\end{aligned}
$$

The OU process is Gaussian and has a closed-form transition:

$$
\begin{aligned}
& X(t+\Delta t) | X(t) =: x \sim N\left( m(x), v   \right) \\
& m(x) := \mu + (x - \mu) \cdot \exp( -\kappa \Delta t ) \\
& v := \frac{\sigma^2}{2\kappa}(1 - \exp(-2\kappa \Delta t))
\end{aligned}
$$

Equivalently, there is discrete-time recursion:

$$
\begin{aligned}
& X(t+\Delta t) = \mu + (X(t) - \mu) \cdot \exp(-\kappa \Delta t) + \sigma \sqrt{\frac{1-\exp(-2\kappa \Delta t)}{2\kappa}} \cdot \varepsilon(t+\Delta t) \\
& \varepsilon(t+\Delta t) \overset{\text{i.i.d.}}{\sim} N(0,1)
\end{aligned}
$$

This recursion defines an AR(1) process with step length \(\Delta t\). The fact that \(\Delta t\) is non-integer is irrelevant as it only appears inside the exponentials and the variance term.
Then, one can apply standard AR(1) discretization techniques such as Tauchen or Tauchen-Hussey to obtain a finite state Markov chain approximation.























