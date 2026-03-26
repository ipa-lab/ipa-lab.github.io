---
title: "Research"
layout: default
excerpt: "Our Research Topics."
---

### Probabilistic Programming @ IPA-Lab

Probabilistic programming provides an intuitive means to specify Bayesian models as programs and to automatically perform posterior inference with general-purpose algorithms.
This makes probabilistic modelling more accessible to non-experts in Bayesian statictics, however, it comes with new challenges.
Through the lens of software engineering, we explore new approaches to improve the probabilistic programming experience.

**Highlighted Publications:**

**[Online and Interactive Bayesian Inference Debugging](https://arxiv.org/abs/2510.26579)**  
*Nathanel Nussbaumer, Markus Böck, and Jürgen Cito. To appear in ICSE 2026.*  
Introduces a new approach for debugging probabilistic programs, where diagnostic tools evaluate the quality of inference during execution.
We implemented a debugger as a VSCode extension and showed that our approach significantly reduces time and difficulty on inference debugging tasks in a user-study.

**[Language-Agnostic Static Analysis of Probabilistic Programs](https://dl.acm.org/doi/10.1145/3691620.3695031)**  
*Markus Böck, Michael Schröder, and Jürgen Cito. ASE 2024.*  
Describes a framework which allows the formulation of program analyses which target problems specific to the probabilistic programming environment in a high-level API.
The analyses can be applied to any probabilistic programming language for which light-weight bindings are implemented.