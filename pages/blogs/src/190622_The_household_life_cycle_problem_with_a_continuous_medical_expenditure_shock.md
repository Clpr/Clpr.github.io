# The household life-cycle problem with a continuous medical expenditure shock ($S\geq 2$)

> Author: Tianhao Zhao (@Clpr)
>
> Publish date: 19 June 24
>
> Last update: 19 June 24

[TOC]



## 1. Setup

### 1.1 Random shock

Considering a life-cycle model with **one** random shock $v$ which follows an AR(1) process like:
$$
\ln v_{s+1} = (1-\rho)m + \rho \ln v_{s} + \epsilon_s
$$
where $s$ is age denotation, $\rho < 1$ is auto-regression coefficient, and $\epsilon_s$ is i.i.d. normal-distribution error. Such a motion ensures that $v_s > 0$.

This random shock is applied on consumption $c_s$.

### 1.2 Utility function

In this problem, we consider a CRRA utility of consumption. Labor supply is assumed to be exogenous (actually, always equal to 1). The CRRA utility with relative risk aversion $\gamma$  is defined as:
$$
u(c|\gamma) = \frac{ c^{1-\gamma} - 1 }{ 1 - \gamma }
$$
where $\gamma>1$ and $\gamma\neq1$.

### 1.3 Budget constraint (unifying asset account)

Let`s consider the budget constraint of the liquid asset $a_s$. For generality, we assume $a_1 \in R$, $a_1\geq0$, and we will use general marks in our budget constraints. And, households do not intend to leave bequest, so there is $a_{S+1} = 0$, where $S$ is the maximum age to live, and $S+1$ is the moment to die.

In this Chapter, we assume that $S\geq 2$.

> Note:
>
> We assume that:
>
> 1. Households are born at the beginning of year 1, i.e. moment $s=1$.
> 2. Households die at the ending of year $S$. i.e. moment $S+1$.
> 3. Because we can use a general-form budget to simultaneously denote the working phase and retired phase, we do not distinguish the two kinds of life-time phases.

Now, we give the budget constraint:
$$
A_{s} a_{s+1} = B_{s} a_{s} - \dot{E}_{s}(v_s) c_s+ F_s, s = 1,\dots,S-1
$$
where $\dot{E}_s(v_s)$ is a random function of $v_s$.

There are some other constraints applied on these abstract parameters:

| Parameter        | Constraint                                         |
| ---------------- | -------------------------------------------------- |
| $A_s$            | $>0$                                               |
| $B_s$            | $> 0$                                              |
| $\dot{E}_s(v_s)$ | $>0$, also $\mathbb{E}\dot{E}_s(v_s)>0$ and finite |
| $F_s$            | $\in R$                                            |

## 2. Budget function

In this section, we define two budget functions which compress all $S$ inter-temporal budget constraints to one equation. Because we have done the same job in another note, here we directly write the final equations. Before that, we define a new cumulative product function:
$$
\tilde{\prod}^m_{i=n} x_i = \begin{cases}
\prod^m_n x_i, n\leq m \\
1, n>m
\end{cases}
$$

### 2.1 For liquid asset

$$
\mathbb{G} = a_1 \prod^S_{i=1} \frac{B_i}{A_i} + \sum^S_{j=1}[ ( \frac{F_j}{A_j}  - \frac{\dot{E}_j(v_j)}{A_j}c_j ) \cdot \tilde{\prod}^S_{i=j+1}\frac{B_i}{A_i} ]
$$

The derivatives are:
$$
\frac{\partial \mathbb{G}}{\partial c_s} =  -(\tilde{\prod}^S_{i=s+1}\frac{B_i}{A_i})\frac{\dot{E}_s(v_s)}{A_s}  < 0 
$$
When using expectation, we have:
$$
\frac{\partial \mathbb{E}[\mathbb{G}]}{\partial c_s} =  -(\tilde{\prod}^S_{i=s+1}\frac{B_i}{A_i})\frac{\mathbb{E}\dot{E}_s(v_s)}{A_s}  < 0   \\
$$

## 3. Setup - continue

### 3.1 Objective function

Households try to maximize the expectation of their life-time utilities`s present value:
$$
\max_{c_s} \mathbb{U} = \mathbb{E}[ \sum^S_{s=1}\beta^s u(c_s) ]
$$
where $\beta$ is the utility discounting factor. (No difference if we discount utility to time 0).

### 3.2 Constraints

$$
\text{s.t. }\begin{cases}
a_1 \geq 0 \\
A_{s} a_{s+1} = B_{s} a_{s} - \dot{E}_{s}(v_s) c_s + F_s  \\
a_{S+1} = 0, \Phi_{S+1} = 0  \\
c_s \geq 0\\
S \geq 2 \\
\end{cases}
$$

### 3.3 New constraints

Using the results of Section 2, we rewrite the constraints as:
$$
\text{s.t. }\begin{cases}
a_1 \geq 0 \\
\mathbb{G}(\cdot) = 0  \\
c_s \geq 0 \\
S \geq 2 \\
\end{cases}
$$

## 4. Solving

In this section, we use conventional Lagrange multiplier method to solve the optimization problem, then adjust the results to meet both endowment & budget constraints.

### 4.1 Lagrange function

$$
\max_{c_s} \mathbb{L} = \mathbb{E}[  \sum^S_{s=1}\beta^s u(c_s) - \lambda \mathbb{G}   ]
$$

### 4.2 FOCs

Please note that the expectation $\mathbb{E}$ is a linear operator.
$$
\begin{cases}
\frac{\partial \mathbb{L}}{\partial c_s} = \beta^s c_s^{-\gamma} - \lambda \frac{\partial \mathbb{E}[\mathbb{G}]}{\partial c_s}   = 0 , s= 1,\dots,S \\
\frac{\partial \mathbb{L}}{\partial \lambda} = \mathbb{E}[\mathbb{G}] = 0 \\
\end{cases}
$$

### 4.3 Dynamics (Euler equation)

With equation 12.a, we can get the consumption dynamics:
$$
\begin{aligned}
\frac{ \beta^{s}c_{s}^{-\gamma} }{ \partial\mathbb{E}[\mathbb{G}]/\partial{c_{s}} } & = \frac{ \beta^{s+1}c_{s+1}^{-\gamma} }{ \partial\mathbb{E}[\mathbb{G}]/\partial{c_{s+1}} }  \\
c_{s+1} &= \Big{[} \beta \frac{ \partial\mathbb{E}[\mathbb{G}]/\partial{c_{s}} }{ \partial\mathbb{E}[\mathbb{G}]/\partial{c_{s+1}} }   \Big{]}^{-\gamma} c_{s} , s = 1,\dots,S-1  \\
c_{s+1} &= \bar{H}_{s,s+1} c_s, s = 1,\dots,S-1
\end{aligned}
$$
where we use a top bar to mark that there are expectations in $\bar{H}_{s,s+1}$. And, according to our assumptions, $\bar{H}_{s,s+1}$ is ensured to be greater than 0.

Meanwhile, for aesthetics, we define a “cumulative” Euler equation which clearly define each $c_s$ with $c_1$.
$$
c_s = \bar{M}_s c_1,s=1,\dots,S
$$
where
$$
\bar{M}_s = \begin{cases}
1,s=1  \\
\prod^s_{i=2} \bar{H}_{i-1,i}  , s=2,\dots,S
\end{cases}
$$

### 4.4 Solving $c_1$

Now, substitute Equation (14) into our budget constraint $\mathbb{E}[\mathbb{G}]$ to solve $c_1$, the initial consumption.
$$
\begin{aligned}
a_1 \prod^S_{i=1} \frac{B_i}{A_i} + \sum^S_{j=1}[ ( \frac{F_j}{A_j}  - \frac{\mathbb{E}[\dot{E}_j(v_j)]  }{A_j}c_j ) \cdot \tilde{\prod}^S_{i=j+1}\frac{B_i}{A_i} ]  & = 0   \\
a_1 \prod^S_{i=1} \frac{B_i}{A_i} + \sum^S_{j=1}[  \frac{F_j}{A_j}  \cdot \tilde{\prod}^S_{i=j+1}\frac{B_i}{A_i} ] - \sum^S_{j=1}[   \frac{\mathbb{E}[\dot{E}_j(v_j)]  }{A_j}c_j  \cdot \tilde{\prod}^S_{i=j+1}\frac{B_i}{A_i} ]  & = 0   \\
a_1 \prod^S_{i=1} \frac{B_i}{A_i} + \sum^S_{j=1}[  \frac{F_j}{A_j}  \cdot \tilde{\prod}^S_{i=j+1}\frac{B_i}{A_i} ] &= \sum^S_{j=1}[   \frac{\mathbb{E}[\dot{E}_j(v_j)]  }{A_j}c_j  \cdot \tilde{\prod}^S_{i=j+1}\frac{B_i}{A_i} ]   \\
a_1 \prod^S_{i=1} \frac{B_i}{A_i} + \sum^S_{j=1}[  \frac{F_j}{A_j}  \cdot \tilde{\prod}^S_{i=j+1}\frac{B_i}{A_i} ] &= c_1 \sum^S_{j=1}[   \frac{\mathbb{E}[\dot{E}_j(v_j)]  }{A_j} \bar{M}_j   \cdot \tilde{\prod}^S_{i=j+1}\frac{B_i}{A_i} ]   \\
X &= c_{1} \bar{Y}  \\
c_1 &= X/\bar{Y}
\end{aligned}
$$
With $c_1$, we can easily get all $c_s$ via the Euler equation.

### 4.5 Discussion about domain

In Equation (15), the value of $c_1$ relies on $X$ and $Y$. According to our assumptions in Section 1.3 and Section 4.3, we learn some facts that:

1. $\prod^S_{i=1}\frac{B_i}{A_i} > 0$
2. $\frac{\mathbb{E}[\dot{E}(v_j)]}{A_j} \cdot \bar{M}_j >0, j=1,\dots,S$

The second item ensures that $c_1$ is well defined. However, because $F_s\in R$, it is not ensured that $c_1\geq 0$. In practice, we treat this case as no solution.

## 5. Computing $\mathbb{E}[\dot{E}_s(v_s)]$

The biggest challenge is how to compute the expectation of the random component $\dot{E}_s(v_s)$ which is a function of our assumed random shock $v_s,s=1,\dots,S$.

In Section 1, we assume that $v_s$ follows an AR(1) process $\ln v_{s+1} = (1-\rho)m + \rho \ln v_s + \epsilon_s$ where $v_{s+1}$ only depends on $v_s$, the first-lag information (Markov process). With generality, we now assume that $|\rho|<1$. It is essential for a steady state economy.

### 5.1 A special case

Let`s consider a special case that:
$$
\dot{E}_s(v_s) = (1+\mu_s)\Big{[} 1 + I(v_s)\cdot \text{cp}_s\cdot v_s + (1-I(v_s))\cdot v_s   \Big{]}, s=1,\dots,S
$$
where $\mu_s,\text{cp}_s>0$ are known parameters, and $I(v_s)$ is an indicator function that
$$
I(v) = \begin{cases}
1, v>\underline{v}  \\
0, v\leq \underline{v}
\end{cases}
$$
where $\underline{v}\in R^+$ is a given threshold.

Define a random function:
$$
\dot{f}(v_s) = \Big{[}  I(v_s)\cdot \text{cp}_s + (1-I(v_s))  \Big{]} v_s
$$
where $\dot{f}$ is a random variable following a compound distribution that:
$$
\begin{cases}
\Pr(\dot{f}=v) = \Pr(v_s\leq\underline{v},v_s=v)  \\
\Pr(\dot{f}=\text{cp}_sv) = \Pr(v_s>\underline{v},v_s=v)  \\
\end{cases}
$$
Following common treatment, we use a $q$-state discrete Markov Chain to approximate this AR(1) process:
$$
\tilde{v}_s \sim \text{MC}(\mathbf{w},\mathbf{P}), s>1
$$
where $\bf{q}$ is state (value) vector, $\bf{P}$ is transition matrix.
$$
\begin{aligned}
\mathbf{w} &= [w_1,\dots,w_q]_{1\times q}   \\
\mathbf{P} &= [p_{i,j}]_{q\times q}
\end{aligned}
$$
For generality, the distribution of $v_{s=1}$ (also called initial distribution) is separately discussed. But when assuming that $v_1$ follows (or has reached) the stationary distribution $\mathbf{\pi_v} = [\pi_1,\dots,\pi_q]_{1\times q},\sum^i \pi_i=1$, we have:
$$
\mathbb{E}[ \tilde{v}_s ] \equiv \bar{v} = \mathbf{w}(\mathbf{\pi_v})^T,s=1,\dots,S
$$
According to [(Heer & Maussner, 2015)](http://link.springer.com/978-3-540-85685-6), we have $\bar{v} \approx \mathbb{E}[v_{s+1}|v_{s}],s=1,\dots,S-1$.

### 5.2 Special case after discretization

Now, let`s use the discrete Markov Chain to replace the AR(1) process and compute the expectation of $\dot{f}$.

> 1. We assume that $\mathbf{w}$ is **increasingly** ordered, i.e. $w_i < w_{i+1},i=1,\dots,q-1$
> 2. We assume that $w_1 < \underline{v} < w_q $, where $i=1,\dots,q$.
> 3. For generality, we assume that $w_i \neq \underline{v},\forall w_i \in \mathbf{w}$. 

We assume that the first $x$ states of $\mathbf{w}$ are less than $\underline{v}$, and the last $q-x$ states are greater than $\underline{v}$. Also, $1\leq x < q$.
$$
\begin{aligned}
& \mathbf{w} = [ \mathbf{w}_{x},\mathbf{w}_{-x} ]_{1\times q}  \\
& w_i < \underline{v}, \forall w_i\in \mathbf{w}_{x}  \\
& w_i > \underline{v}, \forall w_i\in \mathbf{w}_{-x}  \\
\end{aligned}
$$
Therefore, the expectation of $\dot{f}$ is:
$$
\begin{aligned}
\mathbb{E}[\dot{f}(v_s)] &= \sum^{x}_{i} w_i \pi_i + \text{cp}_s\sum^{q-x}_{i}w_i\pi_i  \\
\end{aligned}
$$
Finally, we get the expectation of $\dot{E}(v_s)$ as:
$$
\mathbb{E}[\dot{E}(v_j)] =  (1+\mu_s)\Big{[} 1 + \mathbb{E}[\dot{f}(v_s)]  \Big{]}
$$

## 6. Solution

The solution of our household life-cycle model (of course, under our special case in Section 5) can be denoted as:
$$
\begin{cases}
c_1 = X/\bar{Y}  \\
c_s = \bar{M}_s c_1,s=1,\dots,S  \\
\mathbb{E}[\dot{E}(v_j)] =  (1+\mu_s)\Big{[} 1 + \mathbb{E}[\dot{f}(v_s)]  \Big{]}  \\
\mathbb{E}[\dot{f}(v_s)] = \sum^{x}_{i} w_i \pi_i + \text{cp}_s\sum^{q-x}_{i}w_i\pi_i  \\
\end{cases}
$$
When computing $c_1$, one can extend the whole path with the second formula in Equation (22).

Readers can go to my [GitHub page](https://github.com/Clpr/EconToolBox/blob/master/190623_LifeCycleWithOneShockOnConsumption/Untitled.ipynb) for a complete demo of this life-cycle model.



## 7. (Interlude) Analytical method with borrowing constraint

In a **deterministic** life-cycle model (or the case in Section 5.1), The above solution does not consider borrowing constraints(s), i.e. requiring $a_s\geq \underline{a}$ where $\underline{a}\in R$ and the lower bound is usually 0.

**<u>So, can we get an analytical answer to this problem?</u>** 

Yes, Dynamic Programming can handle this problem well (in fact, it has to embody borrowing constraints because DP does state space discretization), but it is much time-costing.

Therefore, in this section, I introduce an algorithm which uses KKT conditions.

This section is useful, esp. when you are reading Section 8 later.

### 7.1 Setup

Let\`s consider the following **deterministic** life-cycle model with borrowing constraints:
$$
\begin{aligned}
\max_{c_s} \mathbb{U} &= \mathbb{E}[ \sum^S_{s=1}\beta^s u(c_s) ]  \\
\text{s.t.}&\begin{cases}
a_s\geq \underline{a},s=2,\dots,S  \\
A_{s} a_{s+1} = B_{s} a_{s} - E_{s} c_s + F_s  \\
a_1 \in R^+  \\
a_{S+1} = 0  \\
\underline{a}\in R \\
S\geq 2  \\
\end{cases}

\end{aligned}
$$
where $A_s,B_s,E_s,F_s$ are given deterministic parameters, $\underline{a}$ is the lower bound of asset level (usually be 0).

Households have to decide their life-time asset path with the limit that they are not allowed to borrow from a perfect annuity market when they are young.

### 7.2 Solving

Now, we assume that households will borrow if there are no borrowing constraint. We use KKT conditions to solve this problem. To do so, we re-write the problem in standard KKT form:
$$
\begin{aligned}
\max_{c_s} \mathbb{U} &= \mathbb{E}[ \sum^S_{s=1}\beta^s u(c_s) ]  \\
\text{s.t.}&\begin{cases}
\mathbb{G} = 0  \\
\underline{a} - a_s\leq 0 ,s=2,\dots,S  \\
\end{cases}
\end{aligned}
$$
The generalized Lagrange function & KKT conditions are:
$$
\begin{aligned}
\max_{c_s} \mathbb{L} &= \mathbb{U} + \lambda_{S+1}\mathbb{G} + \sum^S_{s=2}\lambda_sa_s   \\
\to\text{KKT}&\begin{cases}
\nabla_{c_s,\lambda_{S+1}}\mathbb{L} = 0    \\
\lambda_s(\underline{a} - a_s) = 0 ,s=2,\dots,S  \\
\lambda_s\geq 0,s=2,\dots,S+1
\end{cases}
\end{aligned}
$$

The 1st condition is FOCs, the 2nd is complementary slackness, the 3rd is the constraints on Lagrange multipliers. Our task becomes to solve the non-linear equations.

> Please note that: $\mathbb{G} = a_{S+1}$

#### 7.2.1 FOCs

To solve the non-linear equations, one essential task is to compute the FOCs, i.e. $\nabla_{c_s}\mathbb{L}$. Please note that we have got the following conclusion:
$$
a_{s+1} = a_1\prod^s_{i=1}\frac{B_i}{A_i} + \sum^s_{j=1}\Big{[} (\frac{F_j}{A_j} - \frac{E_j}{A_j}c_j)\cdot\prod^s_{i=j+1}\frac{B_i}{A_i}     \Big{]}, s=1,\dots,S
$$
where $a_{s+1} = f( c_1,\dots,c_s ) $, and the derivatives of $a_{m},m> s$ on $c_s$ is:
$$
\frac{\partial a_{m}}{\partial c_s} = -\frac{E_s}{A_s}\cdot\prod^{m}_{i=s+1}\frac{B_i}{A_i},s+1\leq m\leq S+1
$$
Therefore, in case $S\geq2$, we have FOCs as:
$$
\frac{\partial \mathbb{L}}{\partial c_s} = \begin{cases}
\beta^s\frac{\partial u}{\partial c_s} + \lambda_{S+1}\frac{\partial \mathbb{G}}{\partial c_s} + \sum^{S}_{i=s+1}\lambda_{i}\frac{\partial a_{i}}{\partial c_s}, s=1,\dots,S-1  \\
\beta^s\frac{\partial u}{\partial c_s} + \lambda_{S+1}\frac{\partial \mathbb{G}}{\partial c_s}, s= S
\end{cases}
$$

Here readers may find that $\frac{\partial a_{S+1}}{\partial c_s}=\partial\mathbb{G}/\partial c_s$. The FOCs can also be denoted in:
$$
\frac{\partial \mathbb{L}}{\partial c_s} = \beta^s\frac{\partial u}{\partial c_s} +  \sum^{S+1}_{i=s+1}\lambda_{i}\frac{\partial a_{i}}{\partial c_s}, s=1,\dots,S
$$

#### 7.2.2 Algorithm

Now, we talk about the algorithm steps.

> 1. Solve the life-cycle problem with the conclusions in Section 4 which does not hold borrowing constraints.
> 2. Is there any $a_s,s=1,\dots,S$ violating borrowing constraints? If not, use current $a_s,c_s$ as final solutions.
> 3. If there is at least one $a_s$ violating our borrowing constraints $a_s\geq \underline{a}$, solve the non-linear equations above Section 7.2.1. Both gradient-required or gradient-free methods are allowed. Please note that we need to use the guess that $\lambda_1,\lambda_s = 0$ or there may be convergence problems. 
> 4. If the algorithm cannot converge, then use dynamic programming.

In practice, I recommend gradient-free iterations which is more convenient.




## 8. Solving with Dynamic Programming (DP)

The solution in Section 4 is zero-time-costing but has one disadvantage: **there is no borrowing limit so households are allowed to over-consume when they are young**.

A natural solution is using Dynamic Programming, the most-general way to solve a life-cycle model. In spite of the significant optimality loss raised by state space discretization, DP is still one of the most convenient solutions.

Now, let\`s re-start from Section 4. But this time we use DP to solve the life-cycle model set up in Section 1 and Section 3.

### 8.1 Bellman equation

The whole life-cycle problem can be denoted with the following Bellman equation:
$$
\begin{aligned}
V_s(a_s) &= \max_{c_s\geq0} \mathbb{E}\Big{[} u(c_s) + \beta V_{s+1}(k_{s+1}|v_{s})    \Big{]}   \\
\text{s.t.}&\begin{cases}
a_s\in[\underline{a},\bar{a}],s=1,\dots,S  \\
A_{s} a_{s+1} = B_{s} a_{s} - \dot{E}_{s}(v_s) c_s + F_s  \\
a_1 \in R^+  \\
a_{S+1} = 0  \\
S\geq 2  \\
\end{cases}
\end{aligned}
$$
The largest difference between this optimization and Section 3 is that now $k_s$ is bounded in range $[\underline{k},\bar{k}]$. Because the expectation is linear operator and $u(c)$ has no random component, the Bellman equation can be written as:
$$
V_s(k_s) = \max_{c_s\geq0} \Big{[} u(c_s) + \beta\cdot \mathbb{E}[ V_{s+1}(k_{s+1}) |v_{s} ]    \Big{]}
$$
The key task is to compute the conditional expectation of $V_{s+1}$ on $v_{s}$.

### 8.2 Case: when $v_1\sim\pi_{\mathbb{v}}$

In this case, the initial distribution, i.e. the distribution of $v_1$ follows the stationary distribution $\pi_{\mathbb{v}}$ of the given discretized Markov Chain. The most important conclusion is that $v_s\sim\pi_{\mathbb{v}}$ for all $s$ and it now actually does not depend on $v_{s-1}$ anymore. The problem becomes a **deterministic** DP which can be solved with the standard solver. (I provided a [demo here](https://github.com/Clpr/EconToolBox/tree/master/190623_LifeCycleWithOneShockOnConsumption))

### 8.3 Case when $v_1 \sim \tilde{\pi}_{\mathbb{v}}$ where $\tilde{\pi}_{\mathbb{v}} \neq \pi_{\mathbb{v}}$

In this case, the dependency between $v_s,v_{s+1}$ cannot be ignored because the system has not reached stationary state. This is a generalized case where we have to explicitly compute $\mathbb{E}[V_{s+1}|v_s]$.

#### 8.3.1 Understanding policy function

To better understand the algorithm here, let\`s have a look at the policy function first. With one Markov-style random shock, the policy function can be defined as the following mapping:
$$
f: (k_s,v_s) \to (k^*_{s+1}|v_s)
$$
It means that: given current capital $k_s$ and the shock $v_s$ in this period $s$, the policy function $f$ gives the optimal capital $k^*_{s+1}$ in the next period conditional on $v_s$.



​	

























