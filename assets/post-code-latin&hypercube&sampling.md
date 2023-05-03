# Code snippet: Latin Hypercube Sampling

[Back to Gallery](./postgallary.html)

> Date: April 24, 2023
>

[TOC]

## Takeaways

Latin Hypercube Sampling (LHS) samplings equal-probability spaces rather than state space. It is efficient to re-build a distribution or simulate extreme risks. There are functions such as `lhsnorm()` for normal distribution in MATLAB. This post gives technical details of LHS, esp. multivariate case with correlation matrix. The algorithms in this post can be easily generalized to other distributions.

## Univariate $N(0,1)$

Let $n$ be the number of folds in probability space, let $k$ be the number of draws in each fold, and let $F_{N(0,1)}(\cdot)$ be the distribution function. LHS returns a sample of size $n\times k$. The algorithm is

> **Algorithm 1**: Univariate $N(0,1)$
>
> 1. Evenly divide $[0,1]$ into $n$ fold: $[0,1/n),[1/n,2/n),\dots,[(n-1)/n,1]$
> 2. Draw $k$ points in each fold from a uniform distribution defined on this fold
> 3. Return a sample of $\{ F_{N(0,1)}^{-1}(p)\}$ where $p$ is all the draws above. If needed, reshuffle the sample

This example can be easily applied to other univariate distributions. A Julia realization is as follows

```julia
# julia
import StatsFuns as sf
import Random
"""
	lhsnorm(fold::Int, k::Int)

Latin Hypercube Sampling - univariate standard normal distribution N(0,1)
Returns a `k*fold` Vector{Float64}. Not shuffled
"""
function lhsrandn(k::Int, fold::Int ; seed::Union{Int,Nothing} = nothing)
	X = isa(seed,Int) ? rand(Random.MersenneTwister(seed),k,fold) : rand(k,fold)
	return sf.norminvcdf.(X ./ k .+ ((0:(k-1)) ./ k))[:]::Vector{Float64}
end
```

```R
# R
rnormlhs = function(k, fold, seed = NULL) {
    if (!is.null(seed)) {set.seed(seed)}
    return(c(qnorm(matrix(runif(k*fold), nrow=k) / k + ((0:(k-1)) / k))))
}
```

## Multivariate $N(\vec\mu,\Sigma=\text{diag}(\vec\sigma)^2)$

Let $\vec\mu:=[\mu_1,\dots,\mu_m]$ be the location parameter, $\vec\sigma:=[\sigma_1,\dots,\sigma_m]$ be the vector of standard deviation of marginal distributions. Then, marginal distributions of $N(\vec\mu,\Sigma=\text{diag}(\vec\sigma)^2)$ are independent to each other.

> **Algorithm 2**: Multivariate $N(\vec\mu,\Sigma=\text{diag}(\vec\sigma)^2)$
>
> 1. Prepare $\vec\mu$ and $\vec\sigma$
> 2. Do LHS of $n$ folds and $k$ draws on each marginal distribution $N(\mu_j,\sigma_j^2)$. <u>Shuffle</u> and save the sample in column vector $x_j$
> 3. Collect total $m$ samples in a matrix $X_0:=[x_1,\dots,x_m]$
> 4. The $X_0$ is the drawn sample from $N(\vec\mu,\Sigma=\text{diag}(\vec\sigma)^2)$

```julia
# julia
import StatsFuns as sf
import Random
"""
	lhsrandmvn0(k::Int, fold::Int, mu::AbstractVector{<:Real}, sigma::AbstractVector{<:Real} ; seed::Union{Int,Nothing} = nothing)

Latin Hypercube Sampling - multivariate normal distribution N(mu,diag(sigma)^2)
Marginal distributions independent to each other.
Returns a `(k*fold) * length(mu)` Matrix{Float64}. Shuffled.
"""
function lhsrandmvn0(
    k::Int,
    fold::Int,
    mu::AbstractVector{<:Real},
    sigma::AbstractVector{<:Real}
    ; seed::Union{Int,Nothing} = nothing
)
    m = length(mu)
    if length(sigma) != m
		throw(ArgumentError("len(mu)!=len(sigma)")) 
    elseif m == 1
		throw(ArgumentError("dim m must be greater than 1")) 
    end
    seeds = rand(
        Random.MersenneTwister(isa(seed,Int) ? seed : nothing),
        0:typemax(Int64), 2*m
    )
    return reduce(hcat,[
		Random.shuffle(
			Random.MersenneTwister(seeds[j]), 
			lhsrandn(k,fold,seed=seeds[m+j]) .* sigma[j] .+ mu[j]
        )
		for j in 1:m
    ])::Matrix{Float64}
end
```

```R
# R
mvrnormlhs = function(k, fold, mu, sigma, seed = NULL) {
	m = length(mu)
	if (length(sigma)!=m) {stop("len(mu)!=len(sigma)")}
	if (!is.null(seed)) {set.seed(seed)}
	seeds = sample((-.Machine$integer.max):(.Machine$integer.max), 2*m)
	return(sapply(1:m,
		function(j){
			set.seed(seeds[j])
			return(sample(
				rnormlhs(k,fold,seed=seeds[m+j]),
				k*fold,
				replace=FALSE
			))
	}))
}
```

## Multivariate $N(\vec\mu,\Sigma)$

Let $\vec\mu:=[\mu_1,\dots,\mu_m]$ be the location parameter, $\Sigma=D R D$ be covariance matrix, $R$ be correlation matrix, $\vec\sigma:=[\sigma_1,\dots,\sigma_m]$ be the vector of standard deviation of marginal distributions, and $D=\text{diag}(\vec\sigma)$ is a diagonal matrix. Conventional LHS on multi-dimension distributions cannot generate a proper correlation matrix. It sometimes generates impossible points if there are correlations among dimensions. According to (Iman & Conover, 1982), we use rank correlations to approximate the target correlation matrix $R^*$. The implementation is developed based on (Zhang & Pinder, 2003).

> **Algorithm 3**: Multivariate $N(\vec\mu,\Sigma)$
>
> 1. Prepare $\vec\mu$, target $R^*$, and $\vec\sigma$
> 2. Draw a sample from $N(\vec\mu,\Sigma=\text{diag}(\vec\sigma)^2)$ and let it be $X_0=[x_1,\dots,x_m]$ where $x_j$ is a $nk$ column vector
> 3. Record the **ordinal ranks** (“1234” ranking) of each $x_j$, denote the ranks as $w_j,j=1,\dots,K$, and define a column-rank matrix $W_0 = [w_1,\dots,w_K]$.  e.g.
>
> $$
> \begin{bmatrix}
> 0.3 & 12 & -13.2 \\
> -0.4 & 2 & -2  \\
> -0.4 & 15.2 & -20 \\
> 0.5 & 2.2 & 1.11 \\
> \end{bmatrix} \xrightarrow[\text{ordinal rank}]{\text{by column}} \begin{bmatrix}
> 3 & 3 & 2 \\
> 1 & 1 & 3 \\
> 2 & 4 & 1 \\
> 4 & 2 & 4 \\
> \end{bmatrix}
> $$
>
> 4. Compute a sample correlation matrix $R_0 = corr(X_0)$, use Cholesky decomposition to get the decomposed lower-triangular matrix $Q$, where $R_0 = QQ^T$
> 5. Use Cholesky decomposition to get the decomposed lower-triangular matrix $P$, where $R = PP^T$, $R$ is the target correlation matrix to approximate
> 6. Compute the adjusted sample matrix $X_1 = X_0 (PQ^{-1})^T$. It is still a $nk\times m$ matrix whose correlation matrix equals to $R$
> 7. Similar to step 3, get the column-rank matrix $W_1$ of $X_1$
> 8. Re-arrange each column of $X_0$ to get $X^*$. It makes the new matrix $X^*$ has the same rank matrix $W^*$ as $X_1$, i.e. $W^* = W_1$. The rearrangement is **column by column** (do not simultaneously arrange all columns together), e.g.
>     1. Now we re-arrange the 2nd column of Eq (2) which is $x_2 = [12,2,15.2,2.2]^T$ with a column-rank $[3,1,4,2]^T$
>     2. Now we have the 2nd column in $W_1$ as $[2,4,1,3]^T$
>     3. Rearrange the elements to $s^*_2 = [2.2,15.2,2,12]^T$ which has a rank vector $[2,4,1,3]^T$
> 9. Return $X^*$ as the drawn sample

```julia
# julia
import LinearAlgebra as la
import StatsBase as sb

"""
	lhsrandmvn(k::Int, fold::Int, mu::AbstractVector{<:Real}, R::AbstractMatrix{<:Real}, sigma::AbstractVector{<:Real} ; seed::Union{Int,Nothing} = nothing)

Latin Hypercube Sampling - multivariate normal distribution N(mu,Sigma)
Covariance allowed.
Returns a `(k*fold) * length(mu)` Matrix{Float64}. Shuffled.
"""
function lhsrandmvn(
    k::Int,
    fold::Int,
    mu::AbstractVector{<:Real},
    R::AbstractMatrix{<:Real},
    sigma::AbstractVector{<:Real}
    ; seed::Union{Int,Nothing} = nothing
)
    m = length(mu)
    if length(sigma) != m
		throw(ArgumentError("len(mu)!=len(sigma)")) 
    elseif m == 1
		throw(ArgumentError("dim m must be greater than 1")) 
    end
    X0 = lhsrandmvn0(k,fold,mu,sigma, seed = seed)
    W0 = reduce(hcat, [sb.ordinalrank(X0[:,j]) for j in 1:m])
    R0 = st.cor(X0)
    X1 = X0 * transpose(la.cholesky(R).L * inv(la.cholesky(R0).L))
    W1 = reduce(hcat, [sb.ordinalrank(X1[:,j]) for j in 1:m])
    for j in 1:m
        sort!(X0[:,j])
        X0[:,j] = X0[sb.ordinalrank(X1[:,j]),j]
    end
    return X0::Matrix{Float64}
end
```





## LHS on K-dim Multivariate Normal Distribution $N(\vec{\mu},\vec{\sigma},R^*)$

### Denotation

1. $\vec{\mu} = [ \mu_1,\dots,\mu_K ]$ is the mean parameter
2. $R^*$ is a the $K\times K$ correlation matrix rather than the covariance matrix $\Sigma$
3. $\vec{\sigma} = [\sigma_1,\dots,\sigma_K]$ is the vector of the standard error of each marginal distributions

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
\end{bmatrix} \xrightarrow[\text{ordinal rank}]{\text{by column}} \begin{bmatrix}
3 & 3 & 2 \\
1 & 1 & 3 \\
2 & 4 & 1 \\
4 & 2 & 4 \\
\end{bmatrix}
$$
4. Compute a sample correlation matrix $R = cor(X_0)$, use Cholesky decomposition to get the decomposed lower-triangular matrix $Q$, where $R = QQ^T$
5. Use Cholesky decomposition to get the decomposed lower-triangular matrix $P$, where $R^* = PP^T$, $R^*$ is the target correlation matrix to approximate
6. Compute the adjusted sample matrix $X_1 = X_0 (PQ^{-1})^T$. It is still a $NP\times K$ matrix whose correlation matrix equals to $R^*$
7. Similar to step 3, get the column-rank matrix $W_1$ of $X_1$
8. Re-arrange each column of $X_0$ to get $X^*$. It makes the new matrix $X^*$ has the same rank matrix $W^*$ as $X_1$, i.e. $W^* = W_1$. The rearrangement is **column by column** (do not simultaneously arrange all columns together), e.g.
   1. Now we re-arrange the 2nd column of Eq (2) which is $x_2 = [12,2,15.2,2.2]^T$ with a column-rank $[3,1,4,2]^T$
   2. Now we have the 2nd column in $W_1$ as $[2,4,1,3]^T$
   3. Rearrange the elements to $s^*_2 = [2.2,15.2,2,12]^T$ which has a rank vector $[2,4,1,3]^T$
9. Return $X^*$

### Demo

With BLAS & LAPACK, readers may find the initial sampling of $X_0$ and following linear algebra operations cost ignorable time, when the last rearrangement operations becomes the bottle neck of performance. Therefore, our demo optimizes the rearrangement for less time cost. Meanwhile, we need 4 $NP\times K$ matrices and 4 $K\times K$ matrices in the original algorithm. The memory cost become horrible when $N,P,K$ go large. Therefore, our demo also optimizes the memory allocation for less memory cost.

```julia
# julia 1.0
function LatinHyperCube( D::Distributions.AbstractMvNormal, N::Int, P::Int )
    # validation
	@assert( (N > 0) & (P > 0), "requries N,P > 0 but received: $(N) and $(P)" )

	# sampling in N divided Uniform(0,1)
	# NOTE: sampling N*P points in ONE Uniform(0,1) on EACH dimension
	local Ddim::Int = Distributions.dim( D.Σ )  # dim of D
	local Res::Matrix{Float64} = rand( Float64, N * P, Ddim )
	# NOTE: using Int for less memoery cost & easy indexing
	# NOTE: in practice, we do not need to declare a W0
	local Rnk1::Matrix{Int} = zeros( Int, N * P, Ddim )  # (row) ranks of each column for Res with correlation
	local EachDimStd = sqrt.( LinearAlgebra.diag( D.Σ ) )  # std of each marginal distribution

	# loop to re-scale & inverse to a MvNormal without correlation (each dim is independent)
	# NOTE: just use our LatinHyperCube() for univariate normal distribution which auto shuffles the results
	for z in 1:Ddim
		Res[:,z] = LatinHyperCube( Distributions.Normal( D.μ[z], EachDimStd[z] ), N, P )
	end

	# compute R (Ddim * Ddim size), the correlation matrix (not cov) of the Res without correlation
	# NOTE: when N*P is large, it is a good idea to use a eye(Ddim) to approximate R
	local Rmat::Matrix{Float64} = (N * P) > 10000 ?  LinearAlgebra.diagm( 0 => ones(Ddim) )  :  StatsBase.cor(Res)
	# get a new sample matrix Res1
	# NOTE: we do not specially declare Q,P but integrate them to the computing of X1
	# 		the complier is smart enough to optimize it for least memeory & time costs
	local Res1 = Res * transpose( LinearAlgebra.cholesky( Distributions.cor( D ) ).L * inv(LinearAlgebra.cholesky( Rmat ).L) )

	# record ranks of each column of Res1, then rearrange Res's columns (one by one) according to Res1's col-ranks
	for z in 1:Ddim
		# first, record X1's rank values
		Rnk1[:,z] = StatsBase.ordinalrank(Res1[:,z])
		# then, sort X0's column, the index is the rank value
		Res[:,z] = sort( Res[:,z] )
		# finally, rearrange indices according to Rnk1
		Res[:,z] = Res[Rnk1[:,z], z]
	end

	# return (we have already shuffled columns)
	return Res::Matrix{Float64}
end # end function LatinHyperCube
```

## Reference 

1. Iman, R. L., and W. J. Conover. 1982. A Distribution-free Approach to Inducing Rank Correlation Among Input Variables. *Communications in Statistics B* 11:311-334
2. Zhang, Y. , & Pinder, G. . (2003). Latin hypercube lattice sample selection strategy for correlated random hydraulic conductivity fields. *Water Resources Research*, 39(8).