# Lean 4 Verification Programs

## *Energy as Contradiction — Formalisation Layer*

This directory contains Lean 4 formalizations of the core mathematical
structures developed in the *[Energy as Contradiction](https://standardgalactic.github.io/library/energy_as_contradiction.pdf)* monograph.

The codebase is not a collection of isolated lemmas; it is organized as a
layered system in which:

* relational inconsistency defines energy,
* variational structure drives dynamics,
* information-theoretic quantities refine the notion of contradiction,
* and non-closure emerges as a structural theorem.

The goal is to expose the theory in a form that is mechanically checkable,
extensible, and eventually categorical.

---

## Setup

Install Lean via `elan`:

```bash
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
```

Then build the project:

```bash
lake update
lake build
```

**Requirements:**

* Lean ≥ 4.14
* Mathlib4 @ v4.14.0

---

## File Structure

### RelationalSystems.lean

**Relational ontology (Chapter 4)**

Defines graph-based systems with group-valued transports and loop holonomy.

Core results:

* Consistency = trivial holonomy
* Energy = sum of squared loop defects
* Energy ≥ 0
* Energy = 0 ↔ consistency (for monitored loops)
* Additivity of energy
* Gauge action via conjugation

This file establishes the foundational idea:

> **Energy is the norm of relational contradiction.**

---

### EnergyFunctionals.lean

**Variational structure (Chapters 5–6)**

Develops energy as a functional and proves its behavior under gradient flow.

Core results:

* Gradient flow derivative:
  d/dt F(c(t)) = −‖∇F‖²
* Non-positivity of energy derivative
* Stationary points ↔ vanishing gradient
* Compatibility energy (regularised functional)
* Diffusion and wave limits (overdamped vs inertial regimes)

Discrete dynamics are also defined, including:

* Chain energy
* Discrete gradient
* Local update rules

This file connects the relational energy to **dynamical evolution**.

---

### ConstraintDynamics.lean

**Dynamics, entropy, and causality (Chapters 6–7)**

Formalizes:

* Entropy production non-negativity
* Discrete entropy increase
* Monotonicity of total entropy
* Conservation from zero derivative
* Finite propagation → causal cones

Conceptually:

> **Entropy production is the time derivative of contradiction flow.**

---

### InformationTheoretic.lean

**Information-theoretic extension (Chapter 7 / Section III)**

Introduces finite distributions and KL divergence.

Core results:

* KL divergence ≥ 0 (Gibbs inequality)
* Information energy = sum of KL divergences
* Global non-negativity of information energy
* Vanishing energy ↔ agreement of local distributions

Also includes:

* Quadratic (Fisher) approximation of KL (structure present)

This layer shows:

> **KL divergence is a canonical local measure of inconsistency.**

---

### GradientFlow.lean

**Symmetry, equivalence, and computation**

Formalizes:

* One-parameter symmetries
* Noether-type conservation structure (framework level)
* Three computational models unified as `FamilyF`:

  * Continuous gradient flow
  * Discrete relaxation
  * NCL-style completion

Also proves:

* Parallel time ≥ DAG depth
* Sequential execution as a special case of parallel schedules

This file encodes:

> **Computation = structured descent of inconsistency.**

---

### NonClosure.lean

**The Non-Closure Theorem (central result)**

Defines abstract constraint systems and proves:

* Perturbation instability of resolved states
* Extension-induced contradiction
* Thermodynamic maintenance cost > 0

Main theorem:

> No finite thermodynamically embedded system with nontrivial extension
> admits both global resolution and perturbation stability.

Corollary:

* Metastability is the strongest achievable order.

This is the conceptual endpoint of the current formalisation.

---

## Status of Proofs

The codebase is now largely free of placeholder proofs in its core logical spine.

Remaining gaps, where present, are localized and correspond to:

* standard analytical bounds (e.g. discrete gradient descent estimates),
* Taylor expansion justifications (KL quadratic limit),
* or higher-regularity arguments (Noether-style differentiation).

Crucially:

> No central theorem depends on an unproven placeholder.

---

## Conceptual Architecture

The files are not independent; they form a progression:

```
RelationalSystems
        ↓
EnergyFunctionals
        ↓
ConstraintDynamics
        ↓
InformationTheoretic
        ↓
GradientFlow
        ↓
NonClosure
```

Each layer refines the same object:

> **Energy = structured inconsistency**

across algebraic, analytic, probabilistic, and dynamical regimes.

---

## Next Step: Categorical Dynamics

The next major step is to lift the entire framework into category theory.

### Target construction

Define a category:

```
ConstraintEnergy
```

with:

* **Objects:** constraint systems (energy functionals)
* **Morphisms:** maps that do not increase energy
* **Composition:** ordinary composition of maps

### Expected structure

Within this category:

* Gradient flow becomes a **functor**
* KL minimization becomes a **functor**
* Gauge flow becomes a **functor**

This reframes the theory as:

> **A categorical theory of energy descent and constraint resolution**

### Why this matters

This step would:

* unify continuous, discrete, and probabilistic dynamics,
* expose invariants under transformation,
* and align the framework with modern mathematical physics
  (e.g. functorial field theory, categorical thermodynamics).

### Planned files

* `ConstraintEnergyCategory.lean`
* `EnergyFunctors.lean` (or `EnergyUnification.lean`)

---

## Interpretation

This project should be read as:

* a **formal semantics of contradiction**,
* a **dynamical theory of resolution**,
* and a **computational model of consistency formation**.

The Lean code serves not as a translation of the monograph, but as:

> a verification layer where every concept is reduced to structure,
> and every claim is forced into explicit form.