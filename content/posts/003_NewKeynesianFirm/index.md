---
title: "Non-linear Phillips curve in NK model step-by-step"
date: 2025-08-02T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

showSummary: true
summary: "Derives the non-linear Phillips curve in NK models with Rotemberg price rigidity step by step. Helpful for students."

featureAsset: "img/feature_default.webp"
---

{{< katex >}}

## Introduction

Deriving the full non-linear Phillips curve in a New Keynesian model can take a lot of time, and it’s easy to make mistakes along the way. This post walks through the process step by step, with every stage written out clearly so that even graduate students just starting out in this literature can follow. The example here uses a heterogeneous-producer setup with Rotemberg-style price rigidity.

Consider a two-stage production structure with a continuum of differentiated intermediate producers and a final goods producer.  All producers solve their profit maximization problem. Each intermediate producer of type \(i \in [0,1]\) produces an intermediate good \(y_t(i)\) using the technology \(f(k(i),\ell(i))\), where \(k(i)\) is capital rented at the nominal interest rate \(R_t\) and \(\ell(i)\) is labor hired at the nominal wage rate \(W_t\). The final goods producer aggregates all intermediate goods into the final output \(y_t\) using the CES aggregator:

$$
y_t = \left( \int_0^1 y_t(i)^{\frac{\varepsilon-1}{\varepsilon}} \, \text{d} i \right)^{\frac{\varepsilon}{\varepsilon-1}}
$$

where \(\varepsilon\) denotes the elasticity of substitution across intermediate goods. In each period \(t\), individual intermediate producers choose how much capital \(k(i)\) and labor \(\ell(i)\) to hire, and set their own nominal prices \(P_t(i)\), while taking the nominal wage rate \(W_t\) and nominal interest rate \(R_t\) as given. The aggregate price level (or index) is defined as a CES aggregation of individual prices:

$$
P_t = \left( \int_0^1 P_t(i)^{\frac{\varepsilon-1}{\varepsilon}} \, \text{d} i \right)^{\frac{\varepsilon}{\varepsilon-1}}.
$$

At the same time, each intermediate producer faces a Rotemberg-type cost of adjusting nominal prices (nominal price rigidity):

$$
\text{AdjC}_t(i) := \varphi(i) \cdot P_t(i) y_t(i) := \frac{\theta}{2}\left( \pi_t(i) - \bar{\pi} \right)^2 \cdot P_t(i) \, y_t(i)
$$

where \(\pi_t(i) = \frac{P_t(i)}{P_{t-1}(i)}\) is the gross inflation rate and \(\bar{\pi}\) is the inflation target (e.g., \(1.02\) for the U.S. economy). Intuitively, the adjustment cost is quadratic in the nominal value of output for producer \(i\).

When we say "solving the production part," we are in fact solving the profit maximization problem of both the intermediate producers and the final goods producer. The (non-linear) Phillips curve emerges as the equilibrium Euler equation of type-\(i\) intermediate producers. In the symmetric equilibrium, where \(P_t(i) = P_t\) for all \(i \in [0,1]\), the same Phillips curve applies to all producers. However, the non-linear Phillips curve is often highly complex, so it is common to approximate it by taking a Taylor expansion around the deterministic steady state. When the expansion is truncated at first order, the result is the familiar linear Phillips curve widely used in quantitative studies.

In the following sections, we will go through this procedure:

1. Solving the final producer's profit maximization by choosing a set of intermediate goods \(\{P_t(i):i \in [0,1]\}\). Solving this problem gives the (final producer's) demand for intermediate goods
2. Solving the intermediate producer of type-\(i\)'s profit maximization
   1. Solving the cost minimization problem by choosing \((k(i),\ell(i))\) while taking the price \(P_i(t)\) and demand \(y_t(i)\) as given
   2. Plugging in the allocation, and solving the profit maximization by choosing price \(P_i(t)\) or equivalently the inflation rate \(\pi_t\), whlie taking the demand \(y_t(i)\) as given
   3. Deriving the non-linear Phillips curve
   4. (Optional) expanding the Phillips curve
3. Computing the aggregate variables (e.g. aggregate output, aggregate capital/labor demand) by specifying the function form of the technology \(f(k,\ell)\)

## Final producer's profit maximization

The final producer takes all prices as given and solve the following problem by choosing a set of intermediate goods \(\{y_t(i):i \in[0,1]\}\):

$$
\begin{aligned}
\max_{\{ y_t(i):i\in[0,1] \}} & P_t y_t - \int_0^1 P_t(i) \cdot y_t(i) \text{d} i  \\
& y_t = \left( \int_0^1 y_t(i)^\frac{\varepsilon-1}{\varepsilon} \text{d} i  \right)^\frac{\varepsilon}{\varepsilon-1}
\end{aligned}
$$

The idea of solving this problem is standard: take the first order condition (FOC) and solve for the optimal \(y_t(i)\) and denote it with _aggregate_ variables \(y_t\). But, one must pay attention that there are _inifinite number of_ FOC as \(i\) is continuous in range \([0,1]\). Step-by-step, taking FOC for type-\(i\) goods:

$$
\begin{aligned}
& P_t \cdot \left[  \int_0^1 y_t(i)^\frac{\varepsilon-1}{\varepsilon} \text{d} i \right]^\frac{1}{\varepsilon-1} \cdot y_t(i)^{-\frac{1}{\varepsilon}} = P_t(i) \\
\implies& P_t \cdot y_t^\frac{1}{\varepsilon} \cdot y_t(i)^{-\frac{1}{\varepsilon}} = P_t(i) \\
\implies& y_t(i) = \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon}\cdot y_t
\end{aligned}
$$

In this way, we can uniformly denote the demand of every single type of intermediate producer as a fraction of the aggregate output. The fraction form gives extra convenience when we do aggregation later.

## Intermediate producer's profit maximization

The intermediate producer of type \(i\) solves the following dynamic programming problem while taking all prices, including their own price \(P_{t-1}(i)\) from the last period:

$$
\begin{aligned}
& \omega_i(P_{t-1}(i);\mathcal{S}_t) := \max_{P_t(i),k_t(i),\ell_t(i)} \Pi_t(i) + \beta \mathbb{E}\left\{ \omega_i(P_{t}(i);\mathcal{S}_{t+1}) | \mathcal{S}_{t} \right\} \\
& \Pi_t(i) := P_t(i) \cdot y_t(i) - \text{AdjC}_t(i) - \left\{ W_t \ell_t(i) + R_t k_t(i)  \right\}  \\
& \text{AdjC}_t(i) := \varphi(i) \cdot P_t(i) y_t(i) := \frac{\theta}{2}\left( \pi_t(i) - \bar{\pi} \right)^2 \cdot P_t(i) \, y_t(i) \\
& \pi_t(i) := P_t(i) / P_{t-1}(i)
\end{aligned}
$$

where \(\Pi_t(i)\) is the flow profit of the producer, \(\text{AdjC}_t(i)\) is the adjustment cost of Rotemberg type, and \(\mathcal{S}_t\) is the information set for decision making. Solving the problem is a multivariable optimization in which, in general, all three controls must be considered simultaneously. However, notice that the costs of the input factors enter the objective function in a linear and separable way. This allows us to first isolate the cost-minimization problem of choosing \((k_t(i), \ell_t(i))\), and then substitute the solution back into the objective function to simplify the remaining price-adjustment choice by leaving only one control \(P_t(i)\).

> **Comment**: here we assume the inflation target \(\overline\pi\) is the same across all types of producers which gives us some nice aggregation results. In quantitative models, this target can be different and the algebra follows this post's spirit.


### Cost minimization step

The intermediate producer of type \(i\) solves the following cost minimization problem:

$$
\begin{aligned}
& \min_{k_t(i),\ell_t(i)} W_t \ell_t(i) + R_t k_t(i) \\
& \text{s.t. }
y_t (i) = f(k_t(i),\ell_t(i))
\end{aligned}
$$

To move on, let's assume a function form of \(f(\cdot)\):

$$
\begin{aligned}
f(k,\ell|Z) := Z_t k^{\alpha_1} \ell^{\alpha_2}
\end{aligned}
$$

where \(Z_t\) is the (separable) productivity, and \(\alpha_1 + \alpha_2\) may or may not equal to 1 (even though we will work with the case \(\alpha_1+\alpha_2=1\) almost through this post). The product structure allows us to simplify the algebra greatly to get a clean analytical solution, while the relaxed assumption on the scale to returns alows us to explore the impact of price dispersion across the intermediate producers later.

To solve the problem, let's define the Lagrangian for type-\(i\) producer:

$$
L(i) := W_t \ell_t(i) + R_t k_t(i) + M_t(i) \cdot ( y_t(i) - Z_t(i) k_t(i)^{\alpha_1} \ell_t(i)^{\alpha_2} )
$$

where \(M_t(i)\) is the _marginal cost_ (MC), i.e. the real unit cost of producing more output \(y_t(i)\). The FOC is then:

$$
\begin{aligned}
R_t =& M_t(i) \cdot Z_t(i) \cdot \alpha_1 k_t(i)^{\alpha_1-1} \ell_t(i)^{\alpha_2} \\
=& M_t(i) \cdot \alpha_1 \cdot y_t(i) / k_t(i)   \\
W_t =& M_t(i) \cdot Z_t(i) \cdot \alpha_2 k_t(i)^{\alpha_1} \ell_t(i)^{\alpha_2-1} \\
=& M_t(i) \cdot \alpha_2 \cdot y_t(i) / \ell_t(i)   \\
\end{aligned}
$$

From standard textbooks we know that the first-order conditions (FOC) of the above problem do not yield a unique optimal point \((k_t(i), \ell_t(i))\) to substitute directly. Instead, they characterize a straight line along which the ratio of the optimal inputs is proportional to the relative price \(R_t/W_t\). This raises the question: how can we proceed? An intuitive approach is to construct the average cost (AC) of producing one unit of output \(y_t(i)\) without explicitly involving either \(k_t(i)\) or \(\ell_t(i)\). Since our goal is to eliminate the input allocation from the profit maximization by separating the process into two stages, this allows us to write the profit as

$$
\left( P_t(i) - \text{AC}_t(i) \right) \cdot y_t(i).
$$

Intuitively, expressing AC independently of \((k_t(i), \ell_t(i))\) requires specific assumptions about returns to scale. A common and standard choice is a Cobb–Douglas technology with constant returns to scale, which in this case implies \(\alpha_1 + \alpha_2 = 1\). The Cobb–Douglas form also provides a useful property: the average cost is equal to the marginal cost. To explore this idea, we apply the following algebraic trick. First, denote \(M_t(i)\) using the two first-order conditions:

$$
\begin{aligned}
& M_t(i) = \frac{R_t\cdot k_t(i) }{\alpha_1 y_t(i)} = \frac{W_t\cdot \ell_t(i) }{\alpha_2 y_t(i)}
\end{aligned}
$$

Then, the key step is to further combine the two equations by raising \(M_t(i)\) to its Cobb-Douglas share respectively:

$$
\begin{aligned}
M_t(i) =& M_t(i)^{\alpha_1} \cdot M_t(i)^{\alpha_2} = \left[ \frac{R_t\cdot k_t(i) }{\alpha_1 y_t(i)} \right]^{\alpha_1} \cdot \left[ \frac{W_t\cdot \ell_t(i) }{\alpha_2 y_t(i)} \right]^{\alpha_2} \\
=& \left[ \frac{R_t\cdot  }{\alpha_1} \right]^{\alpha_1} \cdot \left[ \frac{W_t\cdot }{\alpha_2} \right]^{\alpha_2} \cdot \frac{k_t(i)^{\alpha_1} \ell_t(i)^{\alpha_2} }{y_t(i)^{\alpha_1 + \alpha_2}} \\
=& \frac{1}{Z_t(i)} \cdot \left[ \frac{R_t }{\alpha_1} \right]^{\alpha_1} \cdot \left[ \frac{W_t }{\alpha_2} \right]^{\alpha_2}
\end{aligned}
$$

in which the marginal cost is only about the factor prices, income share, and inverse to the technology level.

> **Hint**: showing AC = MC with Cobb-Douglas technology
>
> Represent the optimal allocation with FOC, then:
$$
\begin{aligned}
\text{AC}_t(i) =& (W_t \ell_t(i) + R_t k_t(i))/y_t(i) \\
=& \frac{1}{y_t(i)}\left[ W_t \cdot \frac{M_t(i)}{W_t} \alpha_2 y_t(i) + R_t \cdot \frac{M_t(i)}{R_t} \alpha_1 y_t(i)  \right] \\
=& \frac{M_t(i) y_t(i)}{y_t(i)} = M_t(i)
\end{aligned}
$$

> **Hint**: In many applications, \(Z_t(i)\) is the same across all the intermediate producers, and/or is normalized to 1. This simplifies the algebra further.

So far, the cost minimization problem has been solved: the cost of production is \(M_t(i) y_t(i)\) and \(M_t(i)\) is represented without the allocation of \((k_t(i),\ell_t(i))\).

### Profit maximization step

Plugging the minimized cost function, the solved demand for type-\(i\) intermediate goods, and plugging in the price adjustment cost into the type-\(i\) producer's profit maximization problem, there is:

$$
\begin{aligned}
& \omega_i(P_{t-1}(i);\mathcal{S}_t) := \max_{P_t(i)} \Pi_t(i) + \beta \mathbb{E}\left\{ \omega_i(P_{t}(i);\mathcal{S}_{t+1}) | \mathcal{S}_{t} \right\}  \\
& \Pi_t(i) := [  (1 - \varphi_t(i))P_t(i) - M_t(i) ] \cdot \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon}\cdot y_t \\
& \varphi_t(i) := \frac{\theta}{2} (\pi_t(i) - \bar{\pi})^2  \\
& \pi_t(i) := P_t(i) / P_{t-1}(i)
\end{aligned}
$$

The only control variable left is \(P_t(i)\), or equivalently the inflation \(\pi_t(i)\).The type-\(i\) producer takes \((P_{t-1}(i),P_t,M_t(i),y_t)\) as given.
To solve this problem, let's derive the FOC by taking the derivatives of the Lagrangian \(L_t(i)\) wrt \(P_t(i)\) 

$$
\begin{aligned}
& \frac{\partial L_t(i)}{\partial P_t(i)} = \frac{\partial \Pi_t(i)}{\partial P_t(i)} + \beta \mathbb{E}\left\{  \frac{\partial}{\partial P_t(i)}  \omega_i(P_{t}(i);\mathcal{S}_{t+1}) \right\} = 0
\end{aligned}
$$

Let's derive the two terms separately.

#### Derivatives of flow profit

$$
\begin{aligned}
& \frac{\partial \Pi_t(i)}{\partial P_t(i)} = y_t \cdot \Big\{
[(1-\varphi_t(i))P_t(i) - M_t(i)] \cdot \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon} \cdot (-\varepsilon) P_t(i)^{-1} \\
& + \left[ 1 - \varphi_t(i) - \frac{\partial \varphi_t(i)}{\partial P_t(i)} P_t(i)  \right] \cdot \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon}
\Big\}  \\
% ---------------
& =  \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon} \cdot y_t \cdot \Big\{
-\varepsilon\cdot(1-\varphi_t(i)) + \varepsilon\cdot M_t(i)\cdot P_t(i)^{-1} \\
& + 1 - \varphi_t(i) - \frac{\partial \varphi_t(i)}{\partial P_t(i)} P_t(i)  
\Big\} \\
% ---------------
& = \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon} \cdot y_t \cdot \Big\{  
(1 - \varepsilon)(1 - \varphi_t(i)) + \varepsilon \cdot M_t(i) \cdot P_t(i)^{-1} - \frac{\partial \varphi_t(i)}{\partial P_t(i)} P_t(i)  
\Big\} \\
\end{aligned}
$$

Knowing that:

$$
\begin{aligned}
\frac{\partial \varphi_t(i)}{\partial P_t(i)} P_t(i)  =& \theta \left[ \frac{P_t(i)}{P_{t-1}(i)} - \bar{\pi} \right] \cdot \frac{1}{P_{t-1}(i)} \cdot P_t(i) 
= \theta ( \pi_t(i) - \bar{\pi} ) \cdot \pi_t(i)
\end{aligned}
$$

The re-arranged equation is:

$$
\begin{aligned}
& \frac{\partial \Pi_t(i)}{\partial P_t(i)} = \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon}  y_t \cdot \\&\Big\{  
(1 - \varepsilon)(1 - \varphi_t(i)) + \varepsilon \cdot \frac{M_t(i)}{P_t(i)} - \theta ( \pi_t(i) - \bar{\pi} ) \cdot \pi_t(i)
\Big\} 
\end{aligned}
$$


#### Derivatives of the expected value

$$
\Pi_t(i) := [  (1 - \varphi_t(i))P_t(i) - M_t(i) ] \cdot \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon}\cdot y_t
$$

Applying envelope theorem to the value function, there is:

$$
\begin{aligned}
& \frac{\partial}{\partial P_{t-1}(i)}  \omega_i(P_{t-1}(i);\mathcal{S}_{t}) = \frac{\partial}{\partial P_{t-1}(i)}  \Pi_t(i) \\
=& \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon}\cdot y_t \cdot P_t(i) \cdot (-1) \cdot \frac{\partial \varphi_t(i)}{\partial P_{t-1}(i)}
\end{aligned}
$$

Knowing that:


$$
\begin{aligned}
& \frac{\partial \varphi_t(i)}{\partial P_{t-1}(i)} = -\theta (\pi_t(i) - \bar{\pi}) \cdot \frac{\pi_t(i)}{P_{t-1}(i)}
\end{aligned}
$$

Re-arrange the derivatives and get:

$$
\begin{aligned}
& \frac{\partial}{\partial P_{t-1}(i)}  \omega_i(P_{t-1}(i);\mathcal{S}_{t}) =  \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon}\cdot y_t \cdot P_t(i) \cdot \theta (\pi_t(i) - \bar{\pi}) \cdot \frac{\pi_t(i)}{P_{t-1}(i)}  \\
&= \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon}\cdot y_t \cdot \theta (\pi_t(i) - \bar{\pi}) \cdot \pi_t(i)^2
\end{aligned}
$$

Moving forward for one period and get:

$$
\frac{\partial}{\partial P_{t}(i)}  \omega_i(P_{t}(i);\mathcal{S}_{t+1}) = \left( \frac{P_{t+1}(i)}{P_{t+1}} \right)^{-\varepsilon}\cdot y_{t+1} \cdot \theta (\pi_{t+1}(i) - \bar{\pi}) \cdot \pi_{t+1}(i)^2
$$


## Non-linear Phillips curve

The non-linear Phillips curve is obtianed by re-arranging the FOC of type-\(i\) producer after plugging the above terms back. The equations may be very long and readers may have to move the slider.

$$
\begin{aligned}
& \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon}  y_t \cdot \Big\{  
(1 - \varepsilon)(1 - \varphi_t(i)) + \varepsilon \cdot \frac{M_t(i)}{P_t(i)} - \theta ( \pi_t(i) - \bar{\pi} ) \cdot \pi_t(i)
\Big\} \\
&+ \beta \mathbb{E} \left\{ \left( \frac{P_{t+1}(i)}{P_{t+1}} \right)^{-\varepsilon}\cdot y_{t+1} \cdot \theta (\pi_{t+1}(i) - \bar{\pi}) \cdot \pi_{t+1}(i)^2   \right\} = 0
\end{aligned}
$$

Move the flow profit derivatives to another side of the equation while flipping the term signs:

$$
\begin{aligned}
& \left( \frac{P_t(i)}{P_t} \right)^{-\varepsilon}  y_t \cdot \Big\{  
\color{red}(\varepsilon - 1)\color{black}(1 - \varphi_t(i)) \color{red}-\color{black} \varepsilon \cdot \frac{M_t(i)}{P_t(i)} \color{red}+\color{black} \theta ( \pi_t(i) - \bar{\pi} ) \cdot \pi_t(i)
\Big\} \\
&= \beta \mathbb{E} \left\{ \left( \frac{P_{t+1}(i)}{P_{t+1}} \right)^{-\varepsilon}\cdot y_{t+1} \cdot \theta (\pi_{t+1}(i) - \bar{\pi}) \cdot \pi_{t+1}(i)^2   \right\}
\end{aligned}
$$

Then, move the demand term to the RHS and convert some price changes to inflation for convenience:

$$
\begin{aligned}
&(\varepsilon - 1)(1 - \varphi_t(i)) - \varepsilon \cdot \frac{M_t(i)}{P_t(i)} + \theta ( \pi_t(i) - \bar{\pi} ) \cdot \pi_t(i) \\
&= \beta \mathbb{E}\left\{ 
   \left( \frac{P_{t+1}(i)/P_t(i)}{P_{t+1}/P_t} \right)^{-\varepsilon}\cdot \frac{y_{t+1}}{y_t} \cdot \theta (\pi_{t+1}(i) - \bar{\pi}) \cdot \pi_{t+1}(i)^2  
\right\}
\end{aligned}
$$

Define aggregate inflation \(\pi_t := P_t / P_{t-1}\). Re-arrange some terms (terms in red color need special attention in each step):

$$
\begin{aligned}
&\color{red} \varepsilon-1 -\frac{\theta(\varepsilon-1)}{2}(\pi_t(i) - \bar{\pi})^2 \color{black} - \varepsilon \cdot \frac{M_t(i)}{P_t(i)} + \theta ( \pi_t(i) - \bar{\pi} ) \cdot \pi_t(i) \\
&= \beta \mathbb{E}\left\{
   \color{red} \left(\frac{\pi_{t+1}(i)}{\pi_{t+1}}\right)^{-\varepsilon} \color{black} \cdot \frac{y_{t+1}}{y_t} \cdot \theta (\pi_{t+1}(i) - \bar{\pi}) \cdot \pi_{t+1}(i)^2  
\right\}  \\
% -----------
\implies&\color{red} \varepsilon \left[ 1 - \frac{M_t(i)}{P_t(i)} \right] \color{black} - 1 - \frac{\theta(\varepsilon-1)}{2}(\pi_t(i) - \bar{\pi})^2  + \theta ( \pi_t(i) - \bar{\pi} ) \cdot \pi_t(i) \\
&= \beta \mathbb{E}\left\{
   \left(\frac{\pi_{t+1}(i)}{\pi_{t+1}}\right)^{-\varepsilon}  \cdot \frac{y_{t+1}}{y_t} \cdot \theta (\pi_{t+1}(i) - \bar{\pi}) \cdot \pi_{t+1}(i)^2  
\right\} 
\end{aligned}
$$

Finally, extracting the price deviation \(\frac{P_t}{P_t(i)}\) out of the first term on the LHS, we get the **_(non-linear) Phillips curve_** that charaterizes how type-\(i\) producer's optimal inflation evolves across time. It is easy to realize that the Phillips curve is nothing else but the Euler equation of type-\(i\) producer's profit maximization problem.

$$
\begin{aligned}
& \varepsilon\frac{P_t}{P_t(i)} \left[ \frac{P_t(i)}{P_t} - \frac{M_t(i)}{P_t} \right] - 1 - \frac{\theta(\varepsilon-1)}{2}(\pi_t(i) - \bar{\pi})^2  + \theta ( \pi_t(i) - \bar{\pi} ) \cdot \pi_t(i) \\
&= \beta \mathbb{E}\left\{
   \left(\frac{\pi_{t+1}(i)}{\pi_{t+1}}\right)^{-\varepsilon}  \cdot \frac{y_{t+1}}{y_t} \cdot \theta (\pi_{t+1}(i) - \bar{\pi}) \cdot \pi_{t+1}(i)^2  
\right\} 
\end{aligned}
$$

where:
- \(P_t(i) - M_t(i)\) is the unit _nominal_ profit; \(\frac{P_t(i) - M_t(i)}{P_t(i)}\) is the nominal profit rate; \(P_t(i)/P_t\) is the real price of type-\(i\) producer's intermediate goods; and \(M_t(i)/P_t\) is the real marginal cost
- \(\pi_t(i)/\pi_t\) is the inflation dispersion
- \(y_{t+1}/y_{t}\) is the real growth


> **Remark**: Even though we have been sticking to the notation of marginal cost \(M_t(i)\), one must realize that it is average cost that should be considered. The nice substitution here is due to the property of constant returns to scale (CRS) of the Cobb-Douglas technology, which isolates the inflation policy making from choosing the allocation. In a general setup, it might be essential to jointly solve the optimal inflaiton and allocation.


In stationary equilibrium (no-trend or detrended, basically \(\overline\pi=1\)), type-$i$ producer's price level \(P_t(i) \equiv \bar{P}(i)\) such that \(\pi_t(i)\equiv \bar\pi(i)\); the marginal cost \(M_t(i) \equiv \bar{M}(i)\). Meanwhile, all the aggregate quantities are the same. Plugging the conditions to the Phillips curve and eliminate almost all terms:

$$
\begin{aligned}
& \varepsilon \frac{\bar{P}}{\bar{P}(i)} \left( \frac{\bar{P}(i)}{\bar{P}} - \frac{\bar{M}(i)}{\bar{P}} \right) - 1 = 0  \\
% ------
\implies& \underbrace{ \bar{p}(i) - \bar{m}(i) }_{\text{real premium (unit profit)}} = \frac{\bar{p}(i)}{\varepsilon} \\
% ------
\implies& \bar{m}(i) = \frac{\varepsilon-1}{\varepsilon} \overline{p}(i)
\end{aligned}
$$

where the notations in lower case mean the values in real term (deflated by the aggregate price level \(P_t\)).





## Linearized Phillips curve


The non-linear Phillips curve captures the exact dynamics of a type-\(i\) producer's optimal pricing and inflation decisions, but the resulting equation is often complex and difficult to interpret. For empirical applications, economists typically rely on its linear approximation around the stationary equilibrium, which yields a much more transparent and tractable form.

It is known that log linearization is equivalent to 1st order Taylor expansion, such that we'll do log linearization for convenience. Define log-deviation \(\hat{x}:= \log{x} - \log\overline{x}\) for a _positive-valued_ variable \(x\) where $\overline{x}$ is the point where to do the approximation/expansion. Around the point to expand, there are approximations: 


$$
\begin{aligned}
& x \approx \overline{x}(1+\hat{x}) \\
& x^\alpha \approx \overline{x}(1 + \alpha \hat{x}) \\
& \frac{x}{y} \approx \frac{\overline{x}}{\overline{y}}(1 + \hat{x} - \hat{y}) \\
& \hat{x}\cdot \hat{y} \approx 0
\end{aligned}
$$

> **Hint**: Some common terms in the Phillips curve has:
$$
\begin{aligned}
& \pi_t(i) - \overline\pi \approx \overline\pi(1+\hat\pi_t(i)) - \overline\pi = \overline\pi \cdot \hat\pi_t(i)  \\
& (\pi_t(i) - \overline\pi)^2 \approx \overline\pi^2 \cdot \hat\pi_t(i)^2 \approx 0  \\
& \frac{\pi_t(i)}{\pi_t} \approx 1+\hat\pi_t(i) -\hat\pi_t \\
& \frac{y_{t+1}}{y_t} \approx 1 + \hat{y}_{t+1} - \hat{y}_t
\end{aligned}
$$

> **Hint**: The whole RHS of the Phillips curve is approximately zero due to the higher-order terms of \(\pi_{t+1}(i)\).

The algebra is then left for exercises.










