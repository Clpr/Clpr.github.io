# Interpolation implementations in macro modelling

> Apr 30, 2023
>
> <a href="./postgallary.html">Back to post gallery</a>

[TOC]

## Takeaways

Interpolations is widely used in the numerical exercises of macroeconomics. This short post gives implementations of some common interpolation methods. Meanwhile, extrapolations are also discussed which is useful in corner cases.

## Notation

Consider a functional mapping from $\R$. Given a set of data points $\{(x_i,y_i)\}_0^n$, let its interpolation $v(x)$ of degree $n$ be in the form $v(x):=\sum_j^n c_j \phi_j(x) = \vec\phi(x)\vec{c}$, where $\vec\phi(x)\in\R^{1\times (n+1)}$ is basis vector and $c_j\in\R^{(n+1)\times 1}$ is interpolation coefficient vector. To evaluate $v(x)$ at $m$ points stacked in a vector $X_m:=[x^1,\dots,x^m]\in\R^{m\times 1}$, we stack $m$ basis vectors in a matrix $\Phi(X_m)\in \R^{m\times (n+1)}$ as $\Phi(X_m):=[\vec\phi(x^1);\dots;\vec\phi(x^m)]$. The evaluated interpolation value is then $\vec v(X_m):=\Phi(X_m)\vec{c}$.

To generalize such setup to multi-dimensional functional mapping from $\R^{k\times 1}$, we Kronecker product basis vector of each dimension. For example, suppose a function mapping from $\R^{2\times 1}$ to $\R$ and there is an interpolation basis $\vec\phi^1$ for the first dimension of $x:=(x^1,x^2)$, and $\vec\phi^2$ for the second dimension. Then, the basis vector of such $\R^{2\times 1}\to\R$ function is defined as $\vec\phi(x):=\vec\phi^1(x^1)\otimes\vec\phi^2(x^2)$. For function mapping from a general $R^{k\times 1}$, there is $\vec\phi(x):=\bigotimes_{j=1}^k \vec\phi^j(x^j)$.

In practice, we often use piecewise interpolations such as piecewise linear and cubic spline. In this pose, we only consider the case where knots $(x_0,\dots,x_n)$ are the same as break points. We will give hat functions for piecewise methods. We assume the knots are distinct and have been ascendingly sorted.

## Basis: piecewise linear

Hat function for piecewise linear interpolation
$$
\phi_j(x) = \begin{cases}
\frac{x-x_{j-1}}{x_j-x_{j-1}}, x_{j-1}\leq x < x_j \\
\frac{x-x_{j+1}}{x_j-x_{j+1}}, x_j\leq x < x_{j+1} \\
0, \text{otherwise}
\end{cases}, j=1,\dots,n-1
$$
To allow *linear extrapolation*, we modify it to be
$$
\phi_j(x) = \begin{cases}
a
\end{cases}
$$






## Basis: cubic spline









## Basis: Bezier curve









## Basis: B-spline









