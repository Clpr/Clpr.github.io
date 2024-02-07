# Precautionary saving in a continuous time economy

> This blog gives a toy example about how to analyze the precautionary saving in continuous time economies. It is for illustration only.

---------------------------------

### Setup

Suppose the economy starts from $t=0$. Consider a household who maximizes his/her lifetime utility by choose $c_t$ which is a function of time $t$:
$$
\begin{aligned}
& \max_{c_{[0,\infty)}} \mathbb{E}\int_0^\infty e^{-\rho t} \log c_t dt \\
\text{s.t. }& da_t = r a_t + z_t - c_t \\
& dz_t = \xi(\bar{z} - z_t)dt + \sigma dW_t
\end{aligned}
$$
where $a_t$ is the holding of liquid asset, $z_t$ that follows an Ornstein–Uhlenbeck process is the income uncertainty, and $W_t$ is a one-dimension Brownian motion. Let $(a_0,z_0)$ be the initial condition of the system.

Before giving its stochastic maximum principle, one may notice that:

* Time homogeneous
* The volatility $\sigma_u$ is independent from the control $c_t$
    * $\implies$ No second-order adjoint pair needed
    * $\implies$ Maximum condition simplified to maximizing the Hamiltonian
* The feasible set of $c_t$ is convex and we can assume that $c_t$ is $C^1$
    * $\implies$ Extended stochastic Hamiltonian system

Now, let’s go. Firstly, let’s define Hamiltonian:
$$
\begin{aligned}
& \mathcal{H}(a_t,z_t;c_t;\vec{p}_t,\vec{q}_t) := \log{c}_t \\
& + p_{a,t}\cdot(ra_t+z_t-c_t) + p_{z,t}\cdot \xi(\bar{z}-z_t) \\
& + q_{a,t}\cdot 0 + q_{z,t}\cdot \sigma \\
=& \log{c_t} + p_{a,t}\cdot(ra_t+z_t-c_t) + p_{z,t}\cdot \xi(\bar{z}-z_t) + q_{z,t}\cdot \sigma
\end{aligned}
$$
where $\vec{p}_t := (p_{a,t},p_{z,t})\in\mathbb{R}^{2}$ and $\vec{q}_t := \begin{bmatrix} q_{a,t} & q_{az,t} \\ q_{za,t} & q_{z,t} \end{bmatrix}\in\mathbb{R}^{2\times 2}$ are the first-order adjoint variables.

> One may notice that only $q_{z,t}$ is used. Because $z_t$ is the only uncertainty source of  the system.

Then, let’s write down the stochastic Hamiltonian system as a FBSDE:
$$
\begin{aligned}
& c_t = 1/ p_{a,t} \\
& da_t = (ra_t + z_t - c_t)dt \\
& dz_t = \xi(\bar{z}-z_t)dt + \sigma dW_t \\
& dp_{a,t} = p_{a,t}(\rho - r)dt \\
& dp_{z,t} = \left[ \rho p_{z,t} - (p_{a,t} - p_{z,t})  \right]dt + q_{z,t}dW_t \\
& \lim_{t\to\infty}e^{-\rho t} p_{a,t}a_t = 0
\end{aligned}
$$
Combining the 1st and the 4th SDE, we can get the Euler equation:
$$
\begin{aligned}
& c_t = \frac{1}{p_{a,t}}  & \text{cite} \\
& dc_t = d\left(\frac{1}{p_{a,t}}\right)   \\
& \frac{dc_t}{c_t} = p_{a,t}\cdot d\left(\frac{1}{p_{a,t}}\right) \\
& \text{applying Ito's lemma} \\
& \frac{dc_t}{c_t} = p_{a,t}\cdot \left\{ \left[ 0 + p_{a,t}(\rho-r)\left(-\frac{1}{p_{a,t}^2}\right) + 0  \right]dt + 0\cdot dW_t       \right\} \\
& \frac{dc_t}{c_t} = (r-\rho)dt
\end{aligned}
$$

> **FYI**: cp. the Euler equation of a discrete time counterpart: $\mathbb{E}\left\{ \frac{c_t}{c_{t+1}} | z_t \right\} = \frac{1+\rho}{1+r}$

> **FYI**: One may notice that the SDE about the shadow value $p_{a,t}$ degenerates to an ODE about time $t$. Thus, here we can take log on both sides of the 1st condition then take time derivatives. This is a common trick in deterministic economies.

> **FYI**: This Euler equation is separable so we can solve the dynamics of the optimal consumption: $c_{t+\Delta t} = c_t e^{(r-\rho)\Delta t} $

If we look at a deterministic economy by shutting down $z_t$ to any constant (typically $\bar{z}$), we can get a similar Euler equation $\dot{c}_t/c_t=r-\rho$.

### Size of the precautionary saving

In discrete time models, we measure the precautionary saving motive by prudence but it is usually hard to measure the size of precautionary saving. But this could be done in a continuous time setting under specific settings.

Let $\Delta t$ be a small enough time period. Given state $(a_t,z_t)$ at time $t$, we define the saving (as a random variable) from time $t$ to time $t+\Delta t$:
$$
\begin{aligned}
\Delta a_{t+\Delta t} :=& a_{t+\Delta t} - a_{t} = \int_t^{t+\Delta t}( ra_s + z_s - c_s )ds \\
\approx& ra_t\cdot \Delta t - \int_t^{t+\Delta t}c_s ds + \int_t^{t+\Delta t} z_s ds \\
\end{aligned}
$$
Because of log utility, the consumption is a fraction of $a_t$ such that $c_t = \rho a_t$. Thus,
$$
\begin{aligned}
\int_t^{t+\Delta t}c_s ds \approx& \rho a_t \cdot \Delta t
\end{aligned}
$$

> **FYI**: this property allows us to properly compare this model and its deterministic counterpart.

Let’s do trapezoid approximation:
$$
\begin{aligned}
\int_t^{t+\Delta t} z_s ds \approx& \frac{\Delta t}{2}(z_t + z_{t+\Delta t}) \\
=&\frac{1}{2}[2z_t + (z_{t+\Delta t} - z_t)] \cdot \Delta t
\end{aligned}
$$
> **FYI**: strictly, we need the continuity property of OU process to perform the above approximation.

Let $\mathcal{Z}_{\Delta t} := z_{t+\Delta t} - z_{t}$ be income growth. By the property of OU process, this income growth follows a normal distribution:
$$
\mathcal{Z}_{\Delta t} \sim N\left( \xi(\bar{z}-z_t)\cdot \Delta t, \sigma^2\cdot \Delta t  \right)
$$
Plugging the above approximations back to the saving:
$$
\begin{aligned}
\Delta a_{t+\Delta t} \approx& (r-\rho)a_t \Delta t + z_t \Delta t + \frac{1}{2}\Delta t\cdot \mathcal{Z}_{\Delta t} \\
=& [(r-\rho)a_t + z_t]\cdot \Delta t + \frac{1}{2}\mathcal{Z}_{\Delta t} \cdot \Delta t
\end{aligned}
$$
which follows a normal distribution:
$$
\begin{aligned}
& \Delta a_{t+\Delta t} \sim N(\mu^a_{t,\Delta t}, \Sigma^a_{t,\Delta t}) \\
& \mu^a_{t,\Delta t} := [(r-\rho)a_t + wz_t ]\cdot \Delta t + \frac{1}{2}\xi(\mu-z_t)\cdot \Delta t  \\
& \Sigma^a_{t,\Delta t} := \frac{\sigma^2}{4}(\Delta t)^3
\end{aligned}
$$
To measure the size of precautionary saving, we need to compare $\Delta a_{t+\Delta t}$ with its deterministic counterpart. Let $\Delta a^{deter}_{t+\Delta t}$ be the saving amount in such an economy without uncertainty (the derivation is left for practice). One can get:
$$
\Delta a^{deter}_{t+\Delta t} \approx [(r-\rho)a_t + wz_t ]\cdot \Delta t
$$
Thus, we can define a statistics of the expected size of precautionary saving:
$$
\mathbb{E}_t\Delta a_{t+\Delta t} - \Delta a^{deter}_{t+\Delta t} \approx \frac{1}{2}\xi(\bar{z}-z_t)\Delta t
$$
The interpretation is that: when facing a bad income shock ($z_t < \bar{z}$), the household, cp. with a deterministic world, extraly saves a fraction of the expected income growth.