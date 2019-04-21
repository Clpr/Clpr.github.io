# Prepare your Julia pro 1.0: instructions of package installing

[Back to index](../../index.html)
> @author: Tianhao Zhao
>
> @date: April 21, 2019
>
> @copyright: free

[TOC]

## Informal Introduction

This blog provides a useful list for economists to install and prepare their Julia 1.0 environment for economic research. Similar to many online instructions, this blog recommend users combine their Julia with mature Python, R, C and Fortran libraries to obtain most comfortable coding experience. However, this blog  prepares a series of questions to help users decide which packages are what they really need.

**<u>Of course, I always agree that it is thoughts, mathematics, algorithms and designs that really matter rather than specific languages. Languages are just how to tell these things. A well-trained developer is required to learn any language in hours and quickly begin to work with it.</u>** However, for some specific purposes, e.g. economic research, a proper language can visibly improve productivities. This is the reason why I introduce and recommend Julia language in this blog. This language has several impressive advantages which make it a top choice for different economists.

## Why Julia?

### Who need Julia?

Learning cost is one of the main reasons that people are not willing to use a new language. Sometimes they  even do not look through a small function with patience.

> "oh no, unreadable! so strange syntax! what exactly does the symbol $ mean!" (by someone without programming trainings)
>
> "It looks familiar but still some subtle differences there ... but holy f\*\*k, who cares. I am too busy to learn them!" (by someone familiar to one or two languages but worry about a sharp learning curve)
>
> "I am used to old grandpa Fortran. I keep reservation about if that new guy is worth learning. Too costing to transfer my works to a new language." (by someone with piles of zombie codes)
>
> "Yes, it is quite easy to learn. But is it necessary? or is it worth spending time on?" (by programmers used to many other popular languages)

Are you one of the four types of perspective developers? If so, please look at:

1. For programming beginners, Julia provides intuitive syntax, many syntax sugars, multiple programming styles, full OO features through multiple dispatch and a fast-growing community. As long as you do not insist to learn programming alchemy with Lisp, Julia is a good choice which has a flat learning curve.
2. For developers familiar to one or two languages, esp. R, Matlab or Python, you may find many familiar syntaxes, symbols even APIs in Julia. (e.g. `randn()`). You have approached to the final when you start! And, if you do not want to drop your old projects in other languages, just call them from Julia! It is so easy a job that you can make it like calling Julia programs with least contact cost. And, in most cases, Julia's performance is better than R, Matlab and Python (even in linear algebras!).
3. For zombie code owners, esp. Fortran or C, you can simply call your old programs from Julia now. Julia provides a user-friendly calling which has the same cost as calling your old programs locally in C/Fortran. You may easily enjoy Julia's high-level data types, easy visualizations together with C/Fortran's lower operations. In fact, Julia provides complete wrappers of BLAS and LAPACK. Many of your old programs can be translated with no performance loss but very familiar syntaxes.
4. For experienced programmers, if you work in the field of scientific computing, ML/DL, economic modeling or other performance-matter fields, Julia should be one of your primary considers. You may enjoy lots of syntax sugars, easy metaprogramming, both cookbook and low-level parallel/distributional computing control, and convenient abstractions when obtaining a high performance near to C or Fortran. 

Of course, this blog is not for general purpose but mainly for economists. So what next to introduce are targeted at economic research. They are definitely useful for economists but may not be so for developers in other fields.

### Zombie Codes?

Many economists may have "**zombie codes**" which were developed years ago and extremely hard to refactor or optimize. This happens usually in large economic model systems such as an old DSGE. These codes are usually written in **<u>Fortran</u>** or **<u>C</u>**. In addition to translation or re-documentation, Julia is able to call the methods in these libraries with least cost like just calling them from local Fortran or C programs. It means zombie codes will not lose any performance when called from Julia. Therefore, economists have no need to worry about the transfer cost from one old language to Julia. Please refer to <https://docs.julialang.org/en/v1/manual/calling-c-and-fortran-code/> for technical details of how to call C or Fortran codes in Julia programs.

### Calling Python or R?

Nowadays, R language has become the 1st choice to do econometric research. Even I will primarily write R programs for a econometric study. (Of course, Julia has its own statistical APIs but the number of relative packages is not very large now) In the same way, Python, which though provides less user-friendly statistical APIs, is also popular in econometric research. So, how can those economists who have been used to R or Python transfer their projects to Julia? Or how can they continue writing Python/R programs in Julia **without learning costs**? Further, how can they combine the advantages, e.g. the impressive number of R's statistical packages, with Julia's high-performance computing?

The solution is so straight that economists can just leave their Python/R environments with no extra change, but just calling them from Julia with least contacting/calling cost.

```julia
# julia 1.0
	using RCall  # R-lang calling API
# just pacakge your R program in a string and evaluate it!
R"
	dat <- data.frame(y=rnorm(100),x1=rnorm(100),x2=rnorm(100))
	mod <- lm( y ~ x1 + x2, data = dat )
	summary(mod)
	modcoef <- coefficients(mod)
"
coef = @rget(modcoef) # pull variable values
```

In the above demo, `RCall` package starts a backend R session and evaluates given R programs. the `@rget` macro pulls the value of `modcoef` from the R session and automatically converts it to a Julia vector. The total time cost, including contact cost, is less than 0.005 seconds. When `coef` or some other R-results pulled, users may use powerful optimization APIs such as `JuMP` to effectively improve their productivity. Of course, R programs in a string means that the metaprogramming advantages of both R & Julia can now be perfectly combined. In Julia REPL, users may even type `$` to enter an R REPL and directly write R programs. Please refer to <http://juliainterop.github.io/RCall.jl/stable/gettingstarted.html> for the full usage of `RCall`. (There are only several syntaxes to remember. 5min, then you can start to work with R in Julia!)

Things go similar in `PyCall`, another popular Python API in Julia. However, because Python is not a functional language like R or Lisp, this package uses symbols to calling Python programs. But do not worry, it is still easy to learn `PyCall`. Please refer to <https://github.com/JuliaPy/PyCall.jl> for more guidance. And, I will use a single section to talk about how to **perfectly** install your `PyCall` and build it with your custom Python installation.

### Used to Matlab?

Matlab is so popular in economic teaching that most economic departments require students to write their homework codes in Matlab. It is not only because Matlab has a plain syntax which is readable across readers with different programming backgrounds, but also because there is less "lazy" packages in Matlab which allow students to be "package callers". However, though Matlab is powerful in industrial production and economic teaching, it has two main disadvantages which prevent it to be the most ideal language for economic research:

1. Low performance in non-algebra cases: Of course, one of Matlab's most-featured advantages is its great linear algebra operations and `optimization` toolbox. A near-C performance of numerical operations makes Matlab so popular in computing-focused cases. However, this software/language lacks the ability of general programming and shows impressive low performance in non-linear-algebra scenarios. It works well in little research projects but shows its short-band when program logics go complicated.
2. Fat and commercial license: Matlab installation is so big. It takes nearly an hour to install and usually half a minute to start. Meanwhile, it is not free and not open-source, which prevents developers to customize their projects or quickly diagnose programs (esp. when errors occur in a low-level function).

In economic teaching, Matlab is enough. But in research, esp. in large-scale economic models and other performance-matter projects, it becomes less satisfying.

So, can Julia be a better alternative of Matlab in most cases? How much can Julia improve than Matlab? There are several points Matlab users need to know:

1. <u>Julia is high-performance in both linear algebra and general cases</u>. While Matlab uses Fortran-MKL as its underlying numerical engine, Julia uses BLAS + LAPACK to acquire an equal even better performance on numerical operations than Matlab. In general cases, Julia overweighs Matlab in IO, control flows etc. This is partly because that Julia uses JIT (just in time) compilation: Julia is a compiling language but Matlab is a foot-script language. The performance difference is therefore impressive. ([Performance testing between Julia and Matlab](https://julialang.org/benchmarks/))
2. <u>Julia has high performance optimization APIs</u>. Many people like Matlab because of its `optimization` toolbox. Its comparable alternatives can be found in Julia, such as `JuMP` and `Optim`. For economists familiar to GAMS, SAS/OR or Lingo, they will find no obscure when simply running their codes in Julia with`JuMP`; for those used to Matlab's `optimization` toolbox, `Optim` provides nearly the same APIs, options and parameters as those in Matlab's `optimization` toolbox. The performance? Well, equal or better in Julia!
3. <u>There is least learning cost for Matlab users to transfer to Julia</u>. If you read the story of how Julia was initiated, you will find that this language uses Matlab's syntax as its fundamental syntax. This feature is more significant before Julia 6.0, where many Matlab's API names were kept and many original Matlab codes can even run in Julia. (Julia pro even provided releases built on MKL at that time) Though Julia's syntax has formed its own styles since Julia 0.7, this language is still very friendly for Matlab users. However, it is wrong if readers think Julia language is a simple improvement based on Matlab. The two languages are designed in totally different philosophies & frameworks, and realized in totally different ways in lower levels. You may easily start writing Julia in Matlab-like syntax, but things go quite different when more Julia features (e.g. macro, metaprogramming, multiple dispatch) introduced. This is just the spirit I discussed at the beginning of this blog: language is just the way to express your thoughts. But do not worry, you can safely write Matlab-style programs in Julia for most teaching & research purposes until you are interested in advanced Julia features or designing your programs for special demands.



## Install Julia Pro

### Download Julia Pro

Readers may download core language from [Julia's official website](https://julialang.org/). It is only about 50MB. Julia Pro is a powerful release of Julia language for scientific computing. In addition to core language, this release provides a Juno IDE based on Atom, `IJulia` REPL, and the support of Jupyter Notebook. Like `Anaconda`, users may easily download and install Julia Pro from: <https://juliacomputing.com/>. Since Julia Pro 1.0, 3rd party packages (e.g. DataFrames) are no longer pre-installed, so users need to install them DIY.

If you do not like Juno IDE, the "VScode + Julia plug-in" is a good alternative. However, this alternative does not support workspace pane which is provided in Juno IDE. Users used to Matlab and R are recommended to continue using Juno.

### Standard Libraries









### Questions Which Help to Select 3rd-party Packages









### Package Manager, Shell and Help in Julia REPL





### Installing popular packages for economic research





### Installing `PyCall` and `RCall`









### Visualization in Julia







































