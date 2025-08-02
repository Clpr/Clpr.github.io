---
title: "Multivariate case for Young (2010) non-stochastic simulation"
date: 2025-08-02T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

showSummary: true
summary: "Explains how to implement the multivariate case of Young (2010) non-stochastic simulation algorithm."

featureAsset: "img/feature_default.webp"
---

{{< katex >}}

Consider a controlled Markovian process \(Y=(X,Z)\):

$$
\begin{aligned}
& X' = f(X,Z) \\
& Z' \sim \text{MarkovianProcess}(Z)
\end{aligned}
$$

where \(X \in \mathbb{R}^N\) is a vector of endogenous states that evolves according to some rules \(f\); \(Z \in \mathbb{R}^M\) is an exogenous process that drives the stochasticity of the joint process \(Y=(X,Z)\). The structure accommodates many models on which a recursive equilibrium can be defined.

Young (2010)'s non-stochastic simulation algorithm provides a convenient tool to approximate such a controlled Markov process \(Y\) with a finite-state Markov chain. However, typical implementations of  the algorithm focus on univariate case i.e. \(X\in\mathbb{R}\) which is common in Krusell-Smith model. My package `MultivariateMarkovChains.jl` implements the multivariate version of Young's algorithm and provides a generic API. This post explains how the multivariate version algorithm works.

To kick off the algorithm, assume:

1. The process of \(Z\) is (or has been approximated by) a finite-state multivariate Markov chain \((\mathcal{Z},P_Z)\) where \(\mathcal{Z}\in\{\mathbb{R}^{M}\}^{D_Z}\) is the vector of total \(D_Z\) states, and \(P_Z \in\mathbb{R}^{D_Z\times D_Z}\) is the transition matrix. The Markov chain is totally exogenous and is not affected by \(X\).
2. The function \(f(X,Z):\mathbb{R}^{N}\times \mathbb{R}^{M} \to \mathbb{R}^{N}\) is a continuous mapping that decides the transition from \(X\) to next period's \(X'\).
3. The economist has got a desired grid \(\mathcal{X}\in\mathbb{R}^{D_N}\) for \(X\). The grid is typically obtained by Cartesian/tensor joining \(X\)'s every dimension's grid. For example, let \(\mathcal{X}_i := [X_i^1,\dots,X_i^{N_i}] \in\mathbb{R}^{N_i}\) be a grid for the \(i\)-th dimension of \(X\), then

$$
\begin{aligned}
\mathcal{X} := \bigtimes^N_{i=1} \mathcal{X}_i \in \{\mathbb{R}^{N}\}^{\prod_{i=1}^NN_i}
\end{aligned}
$$

The challenge of Young's algorithm is to properly allocate the grid for \((X,Z)\): the dependency of \(f\) on \(Z\) makes it wrong to separately construct a chain for \(X\) and a chain \(Z\) then merge them together as if they are independent from each other. To properly handle this issue, we do the following procedures:

**Step 1**: design the finite state space for \(Y=(X,Z)\) joint process. The space has \(D_X \cdot D_Z\) states and every state is a \(N+M\) vector.

$$
\mathcal{Y} := \mathcal{X} \times \mathcal{Z}
$$

**Step 2**: allocate the transition matrix \(P_Y\) of size \((D_XD_Z,D_XD_Z)\).

**Step 3**: loop over all \(Y\) grid points in \(\mathcal{Y}\). At each point \(Y^i\), do the following steps:

1. Given \(Y^i\), evaluate \(f(X^i,Z^i)\) to get the next period's \(X^{i'}\) prediction which is continuous and likely to not match any grid point
2. Construct a discrete distribution over \(\mathcal{X}\) in which the probabilities is propotional to the distance between every grid point to the \(X^{i'}\) prediction. Let the distribution/density/probability vector be \(p^i$
   1. The distance typically only considers the first two nearest neighbor grid points but truncate the probabilities for all the left grid points to zero. This is for sparsity of the transition dynamics. It leads to \(2\) support grid points over \(\mathcal{X}\)
   2. The distance is usually normalized along each dimension to avoid the scale effects. An alternative method is to use the  two nearest neighbor grid points for _every_ dimension, which leads to \(2N\) support grid points over \(\mathcal{X}\)
3. Construct the \(i\)-th row of the transition matrix \(P_Y\) by Kronecker/tensor product \(P_{Z,i} \otimes p^i\) where \(P_{Z,i}\) is the row of \(Z\)'s transition matrix that corresponds to the \(Z\) components of \(Y^i\).

**Step 4**: Construct a `MultivariateMarkovChain` instance by passing in the state space \(\mathcal{Y}\) and the transition matrix \(P_Y\).

So far, we have successfully implemented the multivariate case of Young (2010)'s algorithm. In package `MultivariateMarkovChains.jl`, users can simply run:

```julia
young(
  f, # function f(X,Z) that receives two vectors and returns X' prediction
  Zproc, # a `MultivariateMarkovChain` instance that defines Z's (exogenous) dynamics
  xgrids, # an N-vector of grid (vector of grid points) for every dimension of X
)
```

And everything is done automatically.


> Notes: if your controlled Markoc process has \(X'=f(X)\) i.e. the motion of \(X\) is independent from \(Z\), then `merge()` function should be good enough.




> - Young, Eric R. “Solving the Incomplete Markets Model with Aggregate Uncertainty Using the Krusell–Smith Algorithm and Non-Stochastic Simulations.” Journal of Economic Dynamics and Control 34, no. 1 (2010): 36–41. https://doi.org/10.1016/j.jedc.2008.11.010.
