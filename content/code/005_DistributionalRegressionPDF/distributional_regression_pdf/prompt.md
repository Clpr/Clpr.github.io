You are asked to build a production-quality, single-file Python module that implements a sieve-based conditional density estimator for distributional regression, with the primary goal of fitting and predicting the full conditional probability density function (PDF) of a scalar outcome y given covariates x.

Environment and execution assumptions
- I am using a Conda environment named `PyMain`.
- In terminal, you can activate it with: `conda activate PyMain`
- You are allowed to install any required Python packages via `pip install ...` without asking for permission.
- The deliverable must be a single Python file, not a package with multiple modules.
- The code should be clean, well-structured, well-documented, and ready to use as a reusable module.
- Favor robust, standard scientific Python libraries. Use only packages that are well maintained and easy to install in a normal scientific Python environment.

High-level econometric objective
- We observe data {(y_i, x_i)} for i = 1,...,N.
- y_i is a scalar real-valued outcome, e.g. wage growth.
- x_i is a k-dimensional regressor vector.
- The objective is to estimate the full conditional density:
  f(y | x)
  using a sieve-based conditional density model.
- The model should be flexible enough to capture strong asymmetry, skewness, and a long right tail.
- The model should not impose symmetry, Gaussianity, or a location-scale-only restriction.
- The primary target is a smooth conditional PDF. The conditional CDF can be obtained by integrating the fitted PDF numerically if needed, but the main object is the PDF.

Requested modeling approach
Implement Scheme A: sieve-based conditional density estimation.

A good default design is the following:
1. Represent the conditional log-density flexibly using basis expansions in y and x.
2. Ensure the fitted object is a proper density in y conditional on x, i.e. nonnegative and integrating to 1 over y for each x.
3. A recommended construction is:
   log f(y | x) = eta(y, x) - log Z(x)
   where eta(y, x) is a flexible sieve expansion and
   Z(x) = integral exp(eta(u, x)) du over the y-domain.
4. The y-domain can be approximated by a finite interval inferred from the observed y sample, with a safety margin and optional clipping / integration bounds expansion.
5. Basis expansions should support at least Chebyshev as an explicit option because that is my preferred basis in the usage example.
6. You may also implement additional basis options such as spline or ordinary polynomial if useful, but Chebyshev support is mandatory.
7. The estimator should be implemented by maximizing the conditional log-likelihood over the sample:
   sum_i log f(y_i | x_i)
   plus optional regularization penalties.
8. Use numerically stable optimization and normalization.
9. Since the normalization Z(x) depends on x, you will likely need numerical integration over y for each observation or for each unique design point in transformed space. Make this implementation efficient and reasonably robust.
10. Include practical engineering choices for stability, such as:
   - standardization / affine scaling of X automatically
   - affine scaling of y to a working interval if that helps numerical stability
   - cached basis evaluations where helpful
   - stable exp / log-sum-exp style computations
   - safe clipping to avoid overflow / underflow
   - meaningful convergence diagnostics
11. The estimator should allow regularization:
   - L1 penalty
   - L2 penalty
   - both at the same time if requested
12. If CV is requested, tune regularization hyperparameters and, if practical, basis complexity parameters using cross-validation on conditional log-likelihood or another clearly justified density-forecast criterion.
13. The design should be practical rather than theoretically maximal. Prioritize a robust, interpretable, well-engineered implementation.

Main API requirement
The single-file module must expose a class named:

    DistributionalRegressionPDF

This class is the main entry point.

It must have a detailed docstring at the class level, including:
- conceptual overview
- model description
- assumptions / limitations
- explanation of basis handling
- explanation of automatic data transformation and stored ranges
- explanation of regularization
- explanation of numerical integration and normalization
- explanation of output
- end-to-end usage examples

The module should be centered around an API broadly similar to the following usage style, but you may improve the signatures if there is a clearly better design:

```python
# define model by specifying Chebyshev basis
mod = DistributionalRegressionPDF(
    basis="chebyshev",
    degrees=[2, 4, ...],  # maximum degree of Chebyshev polynomials
)

# fit the model to data {y_i, x_i}
mod.fit(
    y,   # shape (N,)
    X,   # shape (N, k)

    l1penalty=True,
    l2penalty=True,
    cv=True,
    folds=5,
    rng=1234,

    showtrace=True,
)

# evaluate the fitted conditional PDF at specific point y, conditional on x
mod(y, x)   # y scalar, x vector

# print summary information
mod.summary()
print(mod)

# save / load
mod.save(FILE_PATH)
mod.load(FILE_PATH)
```

You may modify and improve this API if needed, but keep the overall spirit and keep the class name exactly as DistributionalRegressionPDF.

Detailed functional requirements

1. Constructor
    Implement a constructor with clear keyword arguments. At minimum support:

* basis: str, at least “chebyshev” supported
* degrees: user-facing control for basis degree
* optional separate controls for degree in y and degree in X if your design benefits from it
* include_interactions: whether to include tensor / interaction terms between y-basis and x-basis
* y_domain: optional manual domain bounds for integration; otherwise infer from data
* y_domain_padding: safety margin when inferring bounds from data
* n_integration_nodes: number of quadrature / integration nodes for normalization
* integration_method: e.g. Gauss-Legendre quadrature or another well-justified method
* standardize_X: bool
* standardize_y: bool if used internally
* fit_intercept: bool
* solver / optimizer settings
* verbose or trace controls

2. Automatic transformation and storage of ranges
    This is important.

* X may not live inside [-1, 1].
* If Chebyshev basis is used, the class must automatically transform each column of X to the working interval required by the basis, e.g. [-1, 1].
* It must store the original range information and transformation parameters internally so that:
    * fit uses them consistently
    * later prediction on new x uses the same transformation
* Do the same for y if your implementation uses an internal working interval for y.
* Handle nearly constant columns robustly.
* Document exactly how the transformation works.
* Include safeguards or warnings when prediction points are far outside the training support. You may extrapolate, but it should be explicit and handled consistently.

3. Fit method
    Implement a .fit(...) method taking y and X as main inputs.
    Requirements:

* validate input shapes and types carefully
* allow NumPy arrays and, if easy, pandas objects
* convert to internal NumPy arrays
* support optional L1 and L2 penalties
* support optional cross-validation
* support reproducible fold splitting with RNG seed
* print trace information when showtrace=True
* store all fitted parameters, metadata, transformation info, CV results, convergence results, and fitting diagnostics inside the object
* return self

The fit method should support arguments along the lines of:

* l1penalty: bool or numeric strength
* l2penalty: bool or numeric strength
* cv: bool
* folds: int
* rng: int or Generator
* showtrace: bool

But you are free to improve the design. For example, it may be better to separate boolean flags from actual alpha / lambda values, e.g.:

* l1_alpha
* l2_alpha
* cv_grid
* cv_metric
* etc.
    If you do improve the API, keep it simple and very well documented.

4. Basis construction
    Implement the sieve basis carefully.
    A strong candidate design:

* Basis in y: B_y(y)
* Basis in x: B_x(x)
* Combined basis eta(y, x) built from tensor products or selected interactions between B_y and B_x
* Allow a controlled basis size to avoid explosion
* For Chebyshev:
    * support stable recursive evaluation
    * support multivariate X by applying 1D basis columnwise and then combining terms in a controlled way
* You must make an explicit, thoughtful design choice about how to represent the multivariate x basis.
    Possible options include:
    * additive basis in x
    * selected pairwise interactions
    * full tensor up to limited degree
    * sparse tensor construction
        Choose a sensible default and document it.
* Favor practicality and numerical tractability.

5. Proper density normalization
    This is central.
    The fitted object must represent a proper density in y conditional on x.
    You must implement normalization so that for each x:

* f(y | x) >= 0
* integral f(y | x) dy = 1

A recommended approach:

* define an unnormalized score s(y, x) = exp(eta(y, x))
* define f(y | x) = s(y, x) / Z(x)
* approximate Z(x) numerically on the y-domain using quadrature
* make sure this is numerically stable and efficient

If you know a better approach that still matches the sieve-based conditional density idea, you may use it, but explain it clearly in the code docstrings and comments.

6. Prediction / call interface
    Implement __call__(self, y, x) so that:

* if y is scalar and x is a 1D covariate vector, it returns a scalar estimated conditional PDF value
* also support vectorized evaluation when practical:
    * y can be array-like
    * x can be one row or multiple rows
* document broadcasting behavior clearly
* the returned value should be the fitted conditional PDF evaluated at those points

Also consider adding explicit methods such as:

* pdf(y, x)
* logpdf(y, x)
* cdf(y, x)    # optional but useful; can be via numerical integration
* sample(x, size=…)   # optional, nice to have if easy and stable
    These are encouraged if they improve usability.

7. Summary and printing
    Implement:

* summary() returning a nicely formatted human-readable summary string and/or printing it
* __repr__ / __str__ with concise but informative content

The summary should report useful information such as:

* basis type
* degree settings
* number of observations
* dimension of X
* inferred or chosen y-domain
* standardization / transformation info
* penalty settings
* whether CV was used
* selected hyperparameters
* optimizer convergence status
* final objective value
* in-sample average log-likelihood
* optionally simple pseudo-fit diagnostics

8. Save / load
    Implement model persistence.
    Requirements:

* save(file_path) saves the fitted model to disk
* load(file_path) loads a saved model
* choose a robust serialization method such as pickle / joblib
* be explicit about whether load is an instance method or class method
* a good design is:
    DistributionalRegressionPDF.load(file_path)
    returning a new instance
* if you keep the mod.load(FILE_PATH) style, make sure it works cleanly
* document the chosen design clearly in the docstring and usage examples

9. Good engineering and software quality
    This module should look like serious reusable scientific code.
    Please include:

* top-level module docstring
* imports grouped cleanly
* type hints where sensible
* clear comments
* defensive input validation
* modular internal helper methods
* no unnecessary global state
* reproducibility controls
* meaningful warnings and error messages
* graceful handling of edge cases

10. Usage examples inside docstrings
    Provide detailed examples in the class docstring and/or method docstrings, including at least:

* simple synthetic data example
* the user-style example based on the API above
* example of evaluating the PDF at new points
* example of saving and loading
* optional example of plotting fitted densities for a few x profiles

11. Minimal demonstration block
    Include:

* if __name__ == "__main__":
    with a concise runnable demonstration on synthetic data.
    This should:
* generate data from an asymmetric conditional distribution depending on x
* fit the model
* print summary
* evaluate some pdf values
* optionally plot a few conditional densities if matplotlib is available
    Keep it short and clear.

Econometric and numerical preferences

* Since the outcome distribution may be asymmetric and right-skewed, avoid designs that implicitly assume symmetry.
* The code should prioritize smooth conditional density estimation.
* The method should be robust enough for wage-growth-like data.
* If you need to choose between ordinary polynomials and Chebyshev stability, favor the more numerically stable design.
* Use regularization in a principled way when basis dimension grows.
* For CV, a natural criterion is out-of-fold conditional log-likelihood. If you add additional metrics, document them.
* If some design decision is ambiguous, choose the one that is most practical, stable, and scientifically interpretable.

Suggested package ecosystem
You may use common packages such as:

* numpy
* scipy
* pandas
* scikit-learn
* joblib
* matplotlib (optional, only for demo / plotting)
    Avoid obscure dependencies unless clearly necessary.

Preferred implementation style

* Keep everything in one file.
* Use object-oriented design centered on DistributionalRegressionPDF.
* Internals can use helper classes or dataclasses if still kept in the same file.
* Write code that a researcher can read, modify, and extend.
* Do not produce a toy sketch; produce a genuinely usable implementation.

Important deliverable requirement
Return exactly one complete single-file Python module implementing the above.
The file should be self-contained and directly runnable after installing dependencies.
Do not split code into multiple files.
Do not give a partial sketch.
Do not only provide pseudocode.
Provide full code.

Before finalizing the code, think carefully about:

* how to represent the sieve basis cleanly
* how to normalize the density robustly
* how to make the API intuitive
* how to keep numerical optimization stable
* how to support both scalar and vectorized evaluation
* how to store transformation ranges and apply them consistently at prediction time

The final code should reflect thoughtful econometric design, not just software mechanics.