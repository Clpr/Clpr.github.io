---
title: "ConstrainedSimplexSearch.jl"
description: "A Julia implementation of constrained Nelder-Mead simplex search algorithm."
date: 2025-04-29
tags: ["Julia","Code"]
cascade:
  showSummary: true
  summary: "This repository implements the Constrained Nelder-Mead (simplex) Search algorithm. It handles generic non-linear equality and inequality constraints using penalty which guides the simplex to move towards the admissible space. Project URL: `https://github.com/Clpr/ConstrainedSimplexSearch.jl`"

featureAsset: "img/feature_code.webp"
---

Project URL: [`https://github.com/Clpr/ConstrainedSimplexSearch.jl`](https://github.com/Clpr/ConstrainedSimplexSearch.jl)

This repository implements the Constrained Nelder-Mead (simplex) Search algorithm which is generalized from the unconstrained Nelder-Mead search method. It handles generic non-linear equality and inequality constraints using penalty which guides the simplex to move towards the admissible space. This package provides a robust solver for high-dimensional quantitative macroeconomic models where: 1. endogeneous constraints are imposed; 2. boundary bindingness are important; 3. High-dimensional numerical approximations are oscilliating.

This package has been registered at Julia's general registry. To install it, simply run:

```julia
pkg> add ConstrainedSimplexSearch.jl
```
