# A quick start for collocation method in macroeconomics

> Apr 30, 2023
>
> <a href="./postgallary.html">Back to post gallery</a>

[TOC]

## Takeaways

<u>Collocation method</u>, esp. in macroeconomics, refers to the idea of approximating a non-linear function (e.g. value function) to speed up solving non-linear models. It has the following pros and cons:

* **Pros**:
    1. Jacobian even Hessian is now available, which means that derivative-based algorithms (e.g. Newton-like methods) can be applied now. Faster than fixed point iteration
    2. The approximated system is almost linear and easy to vectorize, which allows parallel and GPU computing to accelerate model solving
* **Cons**:
    1. Hard to deal with functions with kinks (e.g. model with sudden stops). Collocation method can approximate the neighbor of kinks but cannot really get there
    2. One needs to re-derive almost everything after modifying the model. (So usually one may do fixed iterations first but collocation for the final version with more grid points)
    3. Sometimes too many equations for finite-horizon problems such as OLG with a large number of generations

Even with many cons, collocation method is still essential for macroeconomists. This document uses examples to illustrate how to apply collocation method in some macroeconomic models.

## Notations and math

### Spaces and operators

1. **General**: $\mathbf{x}:=[x^1,\dots,x^k]'\in\mathbb{R}^{k\times 1}$ be a column vector. Define its stacking $\mathbf{X}_n:=[\mathbf{x}_1,\dots,\mathbf{x}_n]'\in\mathbb{R}^{n\times k}$. Define a vector function $\phi(\mathbf{x}):=[\varphi^1(\mathbf{x}),\dots,\varphi^m(\mathbf{x})]\in\mathbb{R}^{1\times m}$ and its stacking $\Phi(\mathbf{X}_n):=[\phi(\mathbf{x}_1);\dots;\phi(\mathbf{x}_n)]\in\mathbb{R}^{n\times m}$.

2. **Distributions**: A well-defined discrete distribution with a support of $q$ elements can be characterized by a state space vector $\mathbf{s}\in\mathbb{R}^{q\times 1}$ and a density vector $\mathbf{p}\in\mathbb{R}^{1\times q}$. Thus, its mean can be calculated by $\mathbf{ps}$.

3. **Markov chain**: A finite state Markov chain with a support of $q$ elements can be characterized by a state space vector $\mathbf{s}\in\mathbb{R}^{q\times 1}$ and a transition matrix $\mathbf{P}:=[\mathbf{p}^1;\dots;\mathbf{p}^q]\in\mathbb{R}^{q\times q}$, where each $\mathbf{p}^i$ is a conditional distribution density.

4. **Hadamard product**: Let $\odot$ be Hadamard product operator between two same-shape matrices.

5. **Stacked functions**: For functions such as $\log$, capitalize its first letter to denote is stacking mapping to the same shape as its input: $\text{Log}(\mathbf{x}):=[\log{x^1},\dots,\log{x^k}]'\in\mathbb{R}^{k\times 1}$. For functions such as $f:\mathbb{R}^{k\times 1}\to\mathbb{R}$, add $\vec\cdot$ symbol on the top of the function to denote its stacking: $\vec{f}(\mathbf{X}_n):=[f(\mathbf{x}_1),\dots,f(\mathbf{x}_n)]'\in\mathbb{R}^{n\times 1}$

6. **Stacked data points**: Consider many data points $(\mathbf{x}_i,y_i)\in\mathbb{R}^{k\times 1}\times \mathbb{R}$. Its stacking can be written in a matrix as $[\mathbf{X}_{n},\mathbf{Y}_n]$ where $\mathbf{Y}_n:=[y_1,\dots,y_n]'\in\mathbb{R}^{n\times 1}$.

### Interpolation

Let $f(\mathbf{x}):\mathbb{R}^{k\times 1}\to \mathbb{R}$ be a real functional. An interpolation $v(\mathbf{x}):\mathbb{R}^{k\times 1}\to \mathbb{R}$ of degree $m$ is defined as $v(\mathbf{x}):=\phi(\mathbf{x})\cdot c$, where $\phi(\mathbf{x})\in\mathbb{R}^{1\times m}$ is basis, and $c\in\mathbb{R}^{m\times 1}$ is the coefficient vector of the interpolation. The function form of $\phi(\mathbf{x})$ is user assigned (e.g. polynomial, B-spline) and $c$ is estimated by $m+1$ distinct points $[\mathbf{\tilde X}_{m+1},\mathbf{\tilde Y}_{m+1}]$ from $f$ by solving linear system $\Phi(\mathbf{\tilde{X}_{m+1}})c=\mathbf{\tilde Y}_{m+1}$. This system is exactly identified.

**Q: I know how to interpolate a function from $\mathbb{R}\to\mathbb{R}$, but how to extend to $\mathbb{R}^{k\times 1}\to\mathbb{R}$?**

**A**: Suppose for each dimension of $\mathbf{x}$, there is a basis $\phi^i(x)\in\mathbb{R}^{1\times m^i}$ (maybe of different types). Then, $\phi(\mathbf{x}):=\otimes_{i=1}^k \phi^i(x^i)\in\mathbb{R}^{1\times \prod_i m^i}$.

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
To apply collation method, we want to interpolate value function $V(\cdot)$ with a specific interpolation method. Suppose the stacked state space of $k$ is $K\in\mathbb{R}^{n\times 1}$, suppose we have known policy functions $g_{k'}(k)\mapsto\mathbb{R}$ and $g_{c}(k)\mapsto \mathbb{R}$. Then, for any given $k\in K$, we can define the following linear equation given a $m$-degree interpolation:
$$
\phi(k)\cdot z = \log(g_{c}(k)) + \beta \phi(g_{k'}(k))\cdot z, k\in K
$$

Now, stacking this system:
$$
\begin{aligned}
& \Phi(\mathbf{K}_n)\cdot z = \text{Log}(\vec{g}_c(\mathbf{K}_n)) + \beta \Phi(\vec{g}_{k'}(\mathbf{K}_n)) \cdot z \\
& \text{where:} \\
& \text{Log}(\vec{g}_c(\mathbf{K}_n)) := [ \log(g_{c}(k^1));\dots;\log(g_{c}(k^n)) ]\in\mathbb{R}^{n\times 1} \\
& \Phi(\mathbf{K}_n) := [\phi(k^1) ; \dots ; \phi(k^n)] \in\mathbb{R}^{n\times m} \\
& \Phi(\vec{g}_{k'}(\mathbf{K}_n)) := [\phi(g_{k'}(k^1)) ; \dots ; \phi(g_{k'}(k^n))] \in\mathbb{R}^{n\times m}
\end{aligned}
$$

Our purpose is to solve $z$, the interpolation coefficients. In this simple example, $z$ can be explicitly written out after having policies $g_c$ and $g_{k'}$:
$$
z = [ \Phi(\mathbf{K}_n) - \beta \Phi(\vec{g}_{k'}(\mathbf{K}_n)) ]^{-1}\text{Log}(\vec{g}_c(\mathbf{K}_n))
$$
Or alternatively, do fixed point iteration. So how to obtain policies $g_c$ and $g_{k'}$? The answer is one-dimensional searching (e.g. Golden Section) for each state $k$ in $\mathbf{K}_n$ given a guess of $z$. (Just like what we used to do in fixed point iterations). Fortunately, such searching process can be stacked to speed up.

So far, what we have done does not really accelerate the solving process (fixed point iteration after interpolation is as slow as before). Now, let's play magics by deriving Jacobian of the stacked system in Equation (3). Let $F(z)$ be the RHS minus the LHS of Equation (3), then:
$$
\begin{aligned}
J(z) := D_zF(z) = \beta \Phi(\vec{g}_{k'}(\mathbf{K}_n)) - \phi(k)
\end{aligned}
$$
Feed this Jacobian to any derivative-based algorithm such as pseudo-Newton methods, then you make it. Usually, it may save $90\%$ time than fixed point iterations.







