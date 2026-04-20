# Distributional Regression PDF

`DistributionalRegressionPDF` is a single-file Python module for estimating the full conditional probability density function of a scalar outcome `y` given covariates `X`.

The implementation is aimed at distributional regression problems where the object of interest is not just `E[y | x]` or a few quantiles, but the entire conditional distribution:

\[
f(y \mid x).
\]

This is especially useful when the conditional outcome distribution is asymmetric, heteroskedastic, heavy-tailed, or otherwise far from Gaussian. A motivating example is **conditional wage growth**: workers with similar observed covariates may have very different upside risk, downside risk, and tail behavior, and those features can matter for forecasting, policy analysis, and counterfactual exercises.

## What This Module Is For

Suppose `y` is wage growth over the next year and `x` includes worker characteristics such as:

- current wage level
- age
- tenure
- education
- occupation or industry indicators
- local labor-market conditions

In many applications, the conditional distribution of wage growth is:

- skewed rather than symmetric
- more dispersed for some workers than others
- potentially long-tailed on the upside or downside
- not well described by a simple Gaussian location-scale model

This module fits a flexible conditional density model that can learn those features directly. Instead of only predicting a conditional mean, it can answer questions like:

- What is the predicted density of wage growth for a worker with a given profile?
- How does the right tail change with education or tenure?
- How much probability mass sits below zero wage growth for different workers?
- How different are the full predictive distributions across groups, not just their averages?

## Wage-Growth Illustration

Below is a stylized example in which `y` is wage growth and `X` contains worker covariates. The model is fit once, then used to evaluate the full predicted density for a given worker profile.

```python
import numpy as np
from distributional_regression_pdf import DistributionalRegressionPDF

rng = np.random.default_rng(123)
n = 1500

# Example covariates:
# x0 = baseline wage proxy
# x1 = tenure
# x2 = local labor market strength
X = rng.normal(size=(n, 3))

# Synthetic wage-growth-like outcome with asymmetry and right tail
loc = 0.015 + 0.02 * np.tanh(X[:, 0]) - 0.01 * X[:, 1]
sigma = 0.18 + 0.05 * np.abs(X[:, 2])
tail = rng.lognormal(mean=0.04 * X[:, 0], sigma=sigma)
y = loc + tail - np.exp(0.04 * X[:, 0] + 0.5 * sigma**2)

mod = DistributionalRegressionPDF(
    basis="chebyshev",
    degree_y=5,
    degree_x=2,
    include_interactions=True,
    x_interaction_order=1,
    n_integration_nodes=64,
)

mod.fit(
    y,
    X,
    l1_alpha=1e-4,
    l2_alpha=1e-3,
    cv=True,
    folds=3,
    rng=1234,
)

# Evaluate the conditional PDF for one worker profile
x_worker = np.array([0.5, 1.0, -0.25])
y_grid = np.linspace(mod.y_domain_[0], mod.y_domain_[1], 300)
pdf_vals = mod.pdf(y_grid, x_worker)

print(mod.summary())
print("Probability density at zero wage growth:", mod.pdf(0.0, x_worker))
```

Interpretation:

- `pdf_vals` is the fitted conditional density curve for that worker profile.
- The mass below zero can be approximated using `mod.cdf(0.0, x_worker)`.
- The shape of `pdf_vals` reveals skewness, tail thickness, and dispersion in a way that a mean regression cannot.

## Underlying Ideas

### High-level idea

The module uses a **sieve-based conditional density model**. A sieve estimator approximates an unknown infinite-dimensional object, here a conditional density, by a flexible but finite-dimensional basis expansion whose complexity can grow with the sample size.

The conditional density is represented through a normalized log-density:

\[
\log f(y \mid x) = \eta(y, x) - \log Z(x),
\]

where

\[
Z(x) = \int_{\mathcal Y} \exp(\eta(u, x))\,du.
\]

This construction guarantees that, for each fixed `x`:

- \( f(y \mid x) \ge 0 \)
- \( \int_{\mathcal Y} f(y \mid x)\,dy = 1 \)

### Basis expansion

In this implementation, `eta(y, x)` is built from **Chebyshev polynomial** basis terms. The practical fitted form is:

\[
\eta(y, x)
=
\sum_{r=1}^{R} \alpha_r T_r(\tilde y)
+
\sum_{j=1}^{k}\sum_{r=1}^{R}\sum_{s=1}^{S}
\beta_{jrs}\, T_r(\tilde y)\,T_s(\tilde x_j)
+
\sum_{j<\ell}\sum_{r=1}^{R}\sum_{s=1}^{S}\sum_{t=1}^{S}
\gamma_{j\ell rst}\, T_r(\tilde y)\,T_s(\tilde x_j)\,T_t(\tilde x_\ell),
\]

where:

- \(T_r(\cdot)\) is the Chebyshev polynomial of degree `r`
- \(\tilde y\) and \(\tilde x_j\) are affinely scaled versions of `y` and `x_j`
- `R = degree_y`
- `S = degree_x`

The module automatically maps each feature and the working `y` domain to `[-1, 1]` when standardization is enabled, which is numerically natural for Chebyshev polynomials.

### Important identifiability detail

In a normalized model of the form

\[
f(y \mid x) = \frac{\exp(\eta(y, x))}{\int \exp(\eta(u, x))\,du},
\]

any term in `eta(y, x)` that depends **only on `x`** cancels out between numerator and denominator. A global intercept cancels for the same reason. So the identifiable object is the part of `eta` that changes with `y`.

That is why the implementation emphasizes:

- marginal `y` basis terms
- `y × x_j` interaction terms
- optional `y × x_j × x_l` interaction terms

rather than trying to estimate pure `x`-only terms that normalization removes anyway.

### Estimation criterion

Given observations \((y_i, x_i)_{i=1}^N\), the module maximizes penalized conditional log-likelihood:

\[
\max_{\beta}
\frac{1}{N}\sum_{i=1}^N \log f(y_i \mid x_i)
-
\lambda_1 \sum_m \sqrt{\beta_m^2 + \varepsilon}
-
\frac{\lambda_2}{2}\sum_m \beta_m^2.
\]

Equivalently, the optimizer minimizes the penalized negative average log-likelihood. Here:

- \(\lambda_1\) controls smooth L1 regularization
- \(\lambda_2\) controls L2 regularization
- \(\varepsilon\) is a small smoothing constant that makes the L1 penalty differentiable

### Numerical normalization

The normalizing constant

\[
Z(x) = \int_{\mathcal Y} \exp(\eta(u, x))\,du
\]

is computed numerically by **Gauss-Legendre quadrature** over a finite raw-`y` domain:

\[
\mathcal Y = [y_{\min}, y_{\max}].
\]

If the user does not specify `y_domain`, the module infers it from the observed sample with padding. The current implementation uses a log-sum-exp form internally for numerical stability.

## Practical Design Choices

The module is intentionally practical rather than theoretically maximal.

- **Single file**: the main estimator lives in one reusable Python file.
- **Chebyshev-first design**: chosen for numerical stability on bounded intervals.
- **Automatic affine scaling**: applied to `X` and, by default, to the `y` working domain.
- **Quadrature-based normalization**: gives a proper density for each `x`.
- **Analytic gradients**: used with `scipy.optimize.minimize` and `L-BFGS-B`.
- **Regularization support**: smooth L1, L2, or both.
- **Optional cross-validation**: selects regularization strengths using out-of-fold conditional log-likelihood.

## Repository Files

- [distributional_regression_pdf.py](distributional_regression_pdf.py): main single-file module implementing `DistributionalRegressionPDF`
- [test.py](test.py): runnable test suite for the module
- [illustration.ipynb](illustration.ipynb): notebook comparing fitted conditional PDFs to the true conditional PDFs in simulated data
- [benchmark.ipynb](benchmark.ipynb): notebook benchmarking fit and prediction performance across sample sizes and feature dimensions
- [prompt.md](prompt.md): original project specification

## Typical Workflow

1. Fit the model on observed outcomes `y` and regressors `X`.
2. Evaluate `pdf(y, x)` on a grid to recover a full conditional density curve.
3. Use `cdf(y, x)` for event probabilities, such as the probability of negative wage growth.
4. Use the illustration notebook to compare fitted versus true PDFs in controlled simulations.
5. Use the benchmark notebook to understand how runtime changes with data size and model complexity.

## Limitations

- The model works on a **finite modeled `y` domain**, not the entire real line.
- Version 1 supports **Chebyshev bases only**.
- The outcome must be **scalar**.
- Very rich interaction structures can become expensive as the number of regressors grows.
- The estimated density is only as good as the chosen basis complexity, penalty strengths, and the suitability of the finite support approximation.

## References

The implementation is inspired by the broader literature on conditional density estimation, series/sieve methods, and semi-nonparametric likelihood methods. Bibliographic metadata below was checked against publisher or repository pages.

1. Gallant, A. Ronald, and Douglas W. Nychka. 1987. “Semi-Nonparametric Maximum Likelihood Estimation.” *Econometrica* 55(2): 363-390.  
   Source: https://www.econometricsociety.org/publications/econometrica/1987/03/01/semi-nonparametric-maximum-likelihood-estimation

2. Shen, Xiaotong. 1997. “On Methods of Sieves and Penalization.” *The Annals of Statistics* 25(6): 2555-2591.  
   Source: https://experts.umn.edu/en/publications/on-methods-of-sieves-and-penalization-2

3. Newey, Whitney K. 1997. “Convergence Rates and Asymptotic Normality for Series Estimators.” *Journal of Econometrics* 79(1): 147-168.  
   Source: https://www.sciencedirect.com/science/article/abs/pii/S0304407697000110

4. Hall, Peter, Jeff Racine, and Qi Li. 2004. “Cross-Validation and the Estimation of Conditional Probability Densities.” *Journal of the American Statistical Association* 99(468): 1015-1026.  
   Source: https://www.tandfonline.com/doi/abs/10.1198/016214504000000548

5. Bierens, Herman J. 2014. “Consistency and Asymptotic Normality of Sieve ML Estimators Under Low-Level Conditions.” *Econometric Theory* 30(5): 1021-1076.  
   Source: https://www.cambridge.org/core/journals/econometric-theory/article/consistency-and-asymptotic-normality-of-sieve-ml-estimators-under-lowlevel-conditions/4FCE8A96D85253A2DCC0F7966C143CBC

6. Brunk, H. D. 1978. “Univariate Density Estimation by Orthogonal Series.” *Biometrika* 65(3): 521-528.  
   Source: https://academic.oup.com/biomet/article-pdf/65/3/521/636906/65-3-521.pdf

## Notes

This repository contains a production-style prototype rather than a large framework. The goal is to keep the code inspectable and modifiable for researchers who want a flexible, density-focused distributional regression estimator in plain scientific Python.
