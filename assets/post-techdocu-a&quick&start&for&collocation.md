# A quick start for collocation method in macroeconomics

> Apr 30, 2023
>
> <a href="./postgallary.html">Back to post gallary</a>

[TOC]

## Introduction

<u>Collocation method</u>, esp. in macroeconomics, refers to the idea of approximating a non-linear function (e.g. value function) to speed up solving non-linear models. It has the following pros and cons:

* **Pros**:
    1. Jacobian even Hessian is now available, which means that derivative-based algorithms (e.g. Newton-like methods) can be applied now. Faster than fixed point iteration in theory
    2. The approximated system is almost linear and easy to vectorize, which allows parallel and GPU computing to accelerate model solving
* **Cons**:
    1. Hard to deal with functions with kinks (e.g. sudden stop). Collocation method can approximate neighbor of the kinks but cannot really get there
    2. High degree of coupling. One needs to re-derive almost everything after modifying the model. (So usually one may do fixed iterations first but collocation for the final version with more grid points)
    3. Sometimes too many equations for finite-horizon problems such as OLG with a large number of generations

Even with many cons, collocation method is still an essential method for macroeconomists. In this document, I will use examples to illustrate how to apply collocation method in some macroeconomic models.

## Notations







## Example: A deterministic saving problem

Let’s consider the following standard infinite-horizon saving problem:
$$
\begin{aligned}
& V(k) = \max_{c,k'} \log{c} + \beta V(k') \\
\text{s.t. }& c + k' = Rk + y \\
& c\geq 0, k'\geq 0\\
& y,R\in\mathbb{R}
\end{aligned}
$$
To apply collation method, we want to interpolate value function $V(\cdot)$ with a specific interpolation method. Suppose the stacked state space of $k$ is $K\in\mathbb{R}^{n_k\times 1}$, suppose we have known policy functions $g_{k'}(k):\mapsto\mathbb{R}$ and $g_{c}(k):\mapsto \mathbb{R}$. Then, for any given $k\in K$, we can define the following linear equation:
$$
\Phi(k)\cdot x = (\log\circ g_{c})(k) + \beta (\Phi\circ g_{k'})(k)\cdot x
$$











