---
title: "A Python module for partially monotonic MLP"
date: 2026-04-13T00:00:01-07:00

showAuthor: true
showAuthorsBadges : true

tags: ["Python","Code"]

showSummary: true
summary: "A PyTorch-based python module for defining, training, auto fine-tuning prediction and I/O of partially monotonic multi-layer perceptron (MLP) function approximator."

featureAsset: "img/feature_code.webp"
---

{{< katex >}}


In quantitative economic modeling, we are often approximating high dimensional mappings such as policy functions of individual households:

$$
y = f(x): \mathbb{R}^n \to \mathbb{R}^m
$$

where \(m\geq 1\) and \(n\) is usually moderate or large (e.g. 5 ~ 10 in some general equilibrium models).

Meanwhile, in many cases esp. continuous time models, analytical policy functions often requires monotonicity along some dimension(s) of the value function. e.g. in a standard growth model with CRRA utility, optimal interior consumption look like:

$$
c(k) = \left(\frac{\partial v}{\partial k}\right)^{-\gamma}
$$

where \(\gamma\geq 1\) for risk-averse households. One can instantly realize that \(v(k)\) must be strictly increasing along dimension \(k\) everywhere to avoid failing to define the consumption.

However, standard numerical approximators/interplations are not guaranteed to keep the monotonicity as iterations move ahead[^1]. Thus, monotonic numerical approximations/interpolations become ideal in this case.

So far, within in the framework of traditional numerical analysis, monotonic interpolation methods are still available only for low dimenisons (e.g. 1 or 2) and it is hard to manage the underlying math and do programming jobs. Also, sometimes we do not want \(y\)  to be monotonic along _all_ dimensions of \(x\), but only specific dimension(s) to be monotonic, and even "increasing along this, decreasing along that, and no restriction otherwise". The property of anisotropic monotonicity restrictions is called **partial monotonicity constraints**.

Neural network is a great choice to approximate a high-dimensional object like \(f(x)\) above, where multi-layer perceptron (MLP), though simple and ABC-like, is very powerful and good enough for most of our demands. The real challenge is to apply partial monotonicity constraints onto the neural network.

There are two major ideas:

- Option A: modifying the neural network's architechture to put "hard" constraint.
- Option B: adding "soft" penalty terms of monotonicity to the loss function.

Option A can totally avoid invalid or undefined behavior of \(f(x)\) on the training and predction stages, but it requires advanced machine learning knowledge. Option B is cheap to use and would eventually converge to a valid solution, but it cannot guarantee violation-free and requires good fine-tuning.

In our applications, policy functions such as \(c(k)\) above need to be evaluated for many many times even during computing the loss function. Thus, Option A emerges as the only admissible option.


There has been a large literature about Option A. Implementations under popular frameworks such as TensorFlow and PyTorch have already been available. What we need to do is wrapping everything up.


Here is a wrapper module that follows standard syntax and interface, which is my resulf of trying ChatGPT Codex:


- [README.md](EasyMLP/README.md)
- [easymlp.py](EasyMLP/easymlp.py): main module file
    - OOP, `EasyMLP` class as main entrance
    - training, auto fine-tuning with advanced controls, summary, prediction, I/O, and Jacobian/Hessian evaluation
    - supports GPU acceleration
    - supports custom partial monotonicity specifications for every output dimenison against every input dimension
    - supports standard interface like running regressions
- [test.py](EasyMLP/test.py): unit testings
- [demo_easymlp.ipynb](EasyMLP/demo_easymlp.ipynb): interactive illustration with visualizations




> **Copyright**: All programs linked to this post were generated using OpenAI's ChatGPT Codex subscribed by the author.




[^1]: Monotonic finite difference schemes are available for low-dimensional continuous time models, but not feasible for high-dimensional continuous time models. And, there is less options for discrete time models where Barles-Souganidis theorem not really applies.
