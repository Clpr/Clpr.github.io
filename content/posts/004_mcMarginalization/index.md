---
title: "Marginalization of multivariate Markov chains"
date: 2025-10-08T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

showSummary: true
summary: "Discusses the marginalization operation of a multivariate Markov chain."

featureAsset: "img/feature_default.webp"
---

{{< katex >}}

## Math

Let's consider a \(D\)-dimensional Markov chain \(\text{MC}_{X,Y}\)

$$
\text{MC}_{X,Y} := \left( \mathbf{X} \times \mathbf{Y}, \mathbf{P}_{X,Y}   \right)
$$

where \(\mathbf{X}\) and \(\mathbf{Y}\) denote the finite discrete state spaces of \(X \in \mathbb{R}^{D_X}\) and \(Y \in \mathbb{R}^{D_Y}\), respectively, and \(\mathbf{P}_{X,Y}\) is the transition matrix in which its $i$-th row $j$-th column element represents the transition probability from state $i$ to state $j$. The state space is constructed using the tensor (Cartesian) product to ensure complete coverage of all possible states and to facilitate programming implementation by leveraging properties of the Cartesian product. Our target is then to obtain a _marginalized_ Markov chain \(\text{MC}_Y\) in which the new Markov chains summarizes the motion of the (partial) state \(Y\).

$$
\text{MC}_Y := \left( \mathbf{Y}, \mathbf{P}_Y \right)
$$

However, it is usually not apparent to marginalize a Markov chain. By definition, disaggregating the conditional probability \(\Pr\{Y'|Y\}\) gives:

$$
\begin{aligned}
   & \begin{cases}
      \Pr\{Y'|Y\} = \sum_{X_j} \Pr\{ X_j,Y'|Y \} \\
      \Pr\{ X_j,Y'|Y \} = \sum_{X_i} \Pr\{ X_j,Y'|X_i,Y \} \cdot \color{red}\Pr\{ X_i | Y \} \color{black} \\
   \end{cases} \\
   \implies & \Pr\{Y'|Y\} = \sum_{X_j} \sum_{X_i} \Pr\{ X_j,Y'|X_i,Y \} \cdot \color{red}\Pr\{ X_i | Y \} \color{black}
\end{aligned}
$$

where the red-font term represents the information required to infer the current value of the reduced partial state \(X\) given the current \(Y\). This information is not contained within the Markov chain \(\text{MC}_{X,Y}\) itself. The absence of this information is the primary reason why marginalization is generally not feasible.



## Fill the gap


**We econometricians, now have to fill the gap.**


However, caution is required: not every \(\Pr\{ X_i | Y \}\) works. To ensure that \(\text{MC}_Y\) is well defined, for every state \(Y\), there must exist at least one state \(Y'\) with positive probability in the final \(\text{MC}_Y\). That is, for any pair \((Y', Y)\), the conditional distribution \(\Pr\{ X_j, Y' | Y \}\) over \(X_j\) must exist. Intuitively, this requires that the mapping (which need not be a function and may be set-valued) implied by \(\Pr\{ X_i | Y \}\) from \(Y\) to \(X\) is injective in a generalized sense, such that \(\{ X \in \mathbf{X} : \Pr\{ X | Y \} > 0 \} \neq \emptyset\) for any given \(Y \in \mathbf{Y}\). In practice, it is often challenging to directly construct a \(\Pr\{ X_i | Y \}\) that satisfies this property. To further illustrate this point, consider a specific case where there exists a surjective function \(Y = f(X)\). In this situation, the equation above is valid only if \(f\) is also injective. When this condition is met, \(\Pr\{ X | Y \}\) takes values of either 1 or 0.



In practical applications, the grid spaces \(\mathbf{X}\) and \(\mathbf{Y}\) are typically predetermined, while the mapping \(Y = f(X)\) may vary over time. For example, suppose \(X\) represents the current state of the economy and \(Y\) denotes the government's policy; in this context, \(f\) corresponds to the optimal policy rule that may evolve by time. The objective is to summarize the dynamics of the policy variables based on their joint evolution with the economic states. The grid spaces are often constructed to be sufficiently large to encompass all possible scenarios of \(f\). However, if the actual optimal policy rule today is stationary, meaning \(Y\) remains constant (e.g., a fixed foreign exchange rate), the mapping \(f\) is inherently not injective, which prevents the above marginalization from being valid. (In most cases, we do not adapt the state space)




In such cases, it becomes necessary to specify \(\Pr\{ X | Y \}\) in a way that is robust to any original \(\text{MC}_{X,Y}\), since it is generally not possible to precisely predict or control how the Markov chain evolves over time or across iterations. Even if this belief is potentially inaccurate, the specification can still embody particular economic intuitions or rationality assumptions. A natural choice is a **"no-information"** prior, where \(\Pr\{ X | Y \}\) is uniform, that is, \(\Pr\{ X | Y \} = 1 / |\mathbf{X}|\), with \(|\mathbf{X}|\) denoting the cardinality of the grid space. The uniform distribution has its state space equal to its support, which enforces the injection property of \(\Pr\{ X_j,Y'|Y \}\).



## Implementation


Implementing the marginalization operation above is straightforward in the low-dimensional case, i.e., when \(N := |\mathbf{X}| \times |\mathbf{Y}|\) is relatively small. However, the computation becomes nontrivial as the number of states \(N\) grows to millions or even billions: on the one hand, the very large transition matrix necessitates sparse-matrix data structures and specialized algorithms to achieve good performance; on the other hand, the marginalization, by definition, has \(\mathcal{O}(N^2)\) time complexity because it must scan every \((X', Y', X, Y)\) tuple at least once. This section assumes a compressed sparse column (CSC) matrix representation in memory and presents and explains an algorithm for the marginalization operation. The example code is in Julia language and uses some of my packages.


**Performance tips**:
For efficient implementation, it is advantageous to scan the transition matrix by columns, corresponding to the "future" states, as this approach optimizes the aggregation of each column and allows for parallelization since columns can be processed independently. It is also important to establish a consistent ordering of states in the new Markov chain \(\Pr\{Y'|Y\}\) and to understand how \((X, Y)\) states are indexed in the original chain \(\Pr\{ X', Y' | X, Y \}\). Utilizing the tensor (Cartesian) product to join the spaces of \(X\) and \(Y\) provides the necessary indexing information for efficient memory access and state queries.


```julia
# TODO (will be updated later)
```


P.S.: The API `marginalize` will be added to `MultivariateMarkovChains.jl`.