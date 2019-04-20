# LHS on Multivariate Normal Distribution with correlations

[Back to Index Page](../../index.html)

> Date: April 4, 2019
>
> Author: Tianhao Zhao
>
> Project Page: [NumToolLibs/NovDist.jl](https://github.com/Clpr/NumToolLibs)
>
> Copyright free but please cite the references of this blog.

[TOC]

## Informal Introduction

Latin Hypercube Sampling (LHS) is quite useful in Monte-Carlo simulation. It samplings in equal-probability spaces which makes it easy to re-build a distribution or simulate extreme (tail) risks. In performance-matter simulations (e.g. large-scale economic model systems), we usually requires high-performance & low-cost programs to generate thousands even millions of normal random numbers. This blog aims to provide a Julia realization which samplings from a given univariate or multivariate normal distribution. Though there has been mature functions in MatLab (e.g. lhsnorm()) to do this job, it still worths discussion because current public papers or technical documents rarely give intuitive introductions to the algorithm which helps developers to design and integrate their own Latin Hypercube Sampling programs.

About basic principles and mathematics of LHS, readers may just read the [pages on Wikipedia](https://en.wikipedia.org/wiki/Latin_hypercube_sampling).



* **Methodology**: using rank correlations to approximate target correlation matrix
* **Reason**: LHS on each dimension will produce some impossible samples if there are correlations among dimensions



## LHS on Univariate Normal Distribution $N(\mu,\sigma)$

### Input

1. a given univariate normal distribution $N(\mu,\sigma)$ with parameter $(\mu,\sigma)$;
2. the number of equal-probability spaces to divide in $[0,1]​$: $N \in N^+​$
3. the number of samples in each equal-probability space to generate: $P \in N^+​$

### Output

1. a sample vectors $\vec{x}$ with $N\times P$ elements

### Algorithm

1. equally divide the probability space $[0,1]$ into $N$ sections
2. sampling $P​$ points on a uniform distribution in each section: $[\frac{n-1}{N},\frac{n}{N}],n=1,\dots,N​$
3. use the inverse of CDF of $N(\mu,\sigma)​$ to convert probabilities to samples
4. shuffle the result, then output

### Demo

```julia
# julia 1.0
# -----------------------------
	import Distributions  # std lib of distributions
	import Random  # std lib of random
	import LinearAlgebra  # std lib of linear algebra, including BLAS
	import StatsBase  # std lib of basic statistical methods
# -----------------------------
function LatinHyperCube( D::Distributions.UnivariateDistribution, N::Int, P::Int )
    # validation
    @assert( (N > 0) & (P > 0), "requries N,P > 0 but received: $(N) and $(P)" )
    # sampling in N divided Uniform(0,1)
    # NOTE: sampling N*P points in ONE Uniform(0,1) then scale them to each Uniform
    local Res::Vector{Float64} = rand( Float64, N * P )
    # loop to re-scale & inverse
    for x in 0:N-1
        for y in 1:P
						# re-scale to a new Uniform & inverse prob to a point
            Res[ x * P + y ] = Distributions.quantile( D, (Res[ x * P + y ] + x) / N )
        end
    end
	# return sampling points which are shuffled by Random.shuffle
    return Random.shuffle(Res)::Vector{Float64}
end # end function LatinHyperCube
```

1. The full documentation of this function can be found in one of my GitHub project: [NumToolLibs/NovDist.jl](https://github.com/Clpr/NumToolLibs/blob/master/InJulia/NovDist.jl)
2. *Distirbutions.quantile()* computes the inverse CDF through interpolations automatically. Users do not need to write an interpolation function. But in some other languages like *C/C++*, user may need to do so. Please refer to this [blog on CSDN](https://blog.csdn.net/Superwen_go/article/details/7689063).
3. Specific to Julia, using simple loops can obtain better performance than vectorization. And of course, try to do all jobs in as least as possible loops.

### Timing

> 1. **Benchmark**: Intel Core i7 6700 3.40GHz; SATA3.0; no SSD; 16G DDR3;
> 2. **Scenario**: sampling 10000 points on $N(0,1)​$ for each time, repeat 10000 times then average time costs

```julia
# julia 1.0
	import StatsBase
	import Distributions
TimeCost = []
D = Distributions.Normal(0.0, 1.0)
for x in 1:10000
  # sampling, and get the time cost (gc time included), then store
  push!(TimeCost, @timed( NovDist.LatinHyperCube(D, 100,100) )[2] )
end
# averaging
StatsBase.mean(TimeCost)
```

<img src="../../image/blog_190420_LHSonMvNormal.svg">

The average time cost to sampling 10000 samples is: **<u>0.00035095323575284963</u>** s. As comparison, the average time of using *randn()* to sampling 10000 samples from $N(0,1)$ is about 0.0002 s.







## LHS on K-dim Multivariate Normal Distribution $N(\vec{\mu},\vec{\sigma},R^*)$

### Denotation

1. $\vec{\mu} = [ \mu_1,\dots,\mu_K ]$ is the mean parameter
2. $R^*$ is a the $K\times K$ correlation matrix rather than the covariance matrix $\Sigma$
3. $\vec{\sigma} = [\sigma_1,\dots,\sigma_K]​$ is the vector of the standard error of each marginal distributions

### Difficulty & Solution

1. Conventional LHS on multi-dimension distributions cannot generate a proper correlation matrix. It sometimes generates impossible points if there are correlations among dimensions
2. According to (Iman & Conover, 1982), we use rank correlations to approximate the target correlation matrix $R^*$. The algorithm is developed based on (Zhang & Pinder, 2003)

### Inputs

1. Target correlation matrix $R^*$ with size $K \times K$. This matrix is a part to define the multivariate normal distribution $N(\vec{\mu},\vec{\sigma},R^*)$
2. $K$ known marginal normal distributions: $N_j(\mu_j,\sigma_j),j=1,\dots,K$
3. The LHS function defined before: *NovDist.LatinHyperCube()*
4. the number of equal-probability spaces to divide in $[0,1]$: $N \in N^+$. The division happens on each dimension
5. the number of samples in each equal-probability space to generate: $P \in N^+$$

### Outputs

1. A $(NP)\times K$ matrix $X^*$ whose rows are sample points; $NP$ is the number of samples and $K$ is the dimensions of each sample point

### Original Algorithm

1. Using LHS to sampling on each marginal distribution $N_j(\mu_j,\sigma_j),j=1,\dots,K$. Denote each sample in a column vector $x_j$ with $NP$ elements. Please note, the elements in each column is shuffled.
2. Define an unadjusted sample matrix $X_0 = [x_1,\dots,x_K]$. $X_0$ is equivalent to a sample matrix from a no-correlation multivariate normal distribution $N(\vec{\mu},\vec{\sigma},0)$
3.  Record the **ordinal ranks** (it ensures the uniqueness of rank values) of each $x_j$, denote the ranks as $w_j,j=1,\dots,K$, and define a column-rank matrix $W_0 = [w_1,\dots,w_K]$.  e.g.
$$
\begin{bmatrix}
0.3 & 12 & -13.2 \\
-0.4 & 2 & -2  \\
-0.4 & 15.2 & -20 \\
0.5 & 2.2 & 1.11 \\
\end{bmatrix} \longrightarrow_{ordinal rank} \begin{bmatrix}
3 & 3 & 2 \\
1 & 1 & 3 \\
2 & 4 & 1 \\
4 & 2 & 4 \\
\end{bmatrix}
$$
4. Compute a sample correlation matrix $R = cor(X_0)$, use Choleskey decomposition to get the decomposed lower-triangular matrix $Q$, where $R = QQ^T$
5. Use Choleskey decomposition to get the decomposed lower-triangular matrix $P$, where $R^* = PP^T$, $R^*$ is the target correlation matrix to approximate
6. Compute the adjusted sample matrix $X_1 = X_0 (PQ^{-1})^T$. It is still a $NP\times K$ matrix whose correlation matrix equals to $R^*$
7. Similar to step 3, get the column-rank matrix $W_1$ of $X_1$
8. Re-arrange each column of $X_0$ to get $X^*$. It makes the new matrix $X^*$ has the same rank matrix $W^*$ as $X_1$, i.e. $W^* = W_1$. The rearrangement is **column by column** (do not simultaneously arrange all columns together), e.g.
   1. Now we re-arrange the 2nd column of Eq (2) which is $x_2 = [12,2,15.2,2.2]^T$ with a column-rank $[3,1,4,2]^T$
   2. Now we have the 2nd column in $W_1$ as $[2,4,1,3]^T$
   3. Rearrange the elements to $s^*_2 = [2.2,15.2,2,12]^T$ which has a rank vector $[2,4,1,3]^T$
9. Return $X^*$

### Demo









### Timing















## Reference 

1. Iman, R. L., and W. J. Conover. 1982. A Distribution-free Approach to Inducing Rank Correlation Among Input Variables. Communications in Statistics B 11:311-334
2. Zhang, Y. , & Pinder, G. . (2003). Latin hypercube lattice sample selection strategy for correlated random hydraulic conductivity fields. Water Resources Research, 39(8).