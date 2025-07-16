---
title: "BoxDomains.jl"
description: "A Julia implementation of box domains."
date: 2025-04-30
tags: ["Julia","Code"]
cascade:
  showSummary: true
  summary: "A Julia implementation of box domains like [a1,b1]*[a2,b2].... which are everywhere in economic modeling. The package allows users to define, manipulate, slice, transform, and discretize such spaces. In particular, most of the operations overload Julia Base such that users can have a native coding experience. Project URL: `https://github.com/Clpr/BoxDomains.jl`"

featureAsset: "img/feature_code.webp"
---

{{< katex >}}

Project URL: [`https://github.com/Clpr/BoxDomains.jl`](https://github.com/Clpr/BoxDomains.jl)

`BoxDomains.jl` provides convenient abstractions of mutli-dimensional bounded space like

$$
\mathcal{X} := \prod_{j=1}^D [\underline{x}_j, \bar{x}_j]
$$

which are everywhere in economic modeling. The package allows users to define, manipulate, slice, transform, and discretize such spaces. The data structures are lazy. In particular, most of the operations overload Julia Base such that users can have a native coding experience.

This package has been registered at Julia's general registry. To install it, simply run:

```julia
pkg> add BoxDomains.jl
```
