/-
  ConstraintDynamics.lean
-/

import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Topology.Algebra.Order.Monotone
import Mathlib.Tactic

namespace EnergyAsContradiction.Dynamics

-- ─────────────────────────────────────────────────────────────
-- 1. Gradient flow energy monotonicity
-- ─────────────────────────────────────────────────────────────

/-- Derivative of energy along gradient flow. -/
theorem energy_derivative_eq
    {X : Type*} [NormedAddCommGroup X] [InnerProductSpace ℝ X]
    (E : X → ℝ)
    (∇E : X → X)
    (hE : ∀ x, HasFDerivAt E (innerSL ℝ (∇E x)) x)
    (c : ℝ → X)
    (hc : ∀ t, HasDerivAt c (-∇E (c t)) t)
    (t : ℝ) :
    HasDerivAt (fun t => E (c t)) (-‖∇E (c t)‖ ^ 2) t := by
  have hFct := hE (c t)
  have hct  := hc t
  have chain := hFct.comp t hct.hasDerivAt
  convert chain using 1
  simp [innerSL, ContinuousLinearMap.comp_apply,
        inner_neg_right, real_inner_self_eq_norm_sq]

/-- Energy is non-increasing along gradient flow. -/
theorem gradient_flow_monotone
    {X : Type*} [NormedAddCommGroup X] [InnerProductSpace ℝ X]
    (E : X → ℝ)
    (∇E : X → X)
    (hE : ∀ x, HasFDerivAt E (innerSL ℝ (∇E x)) x)
    (c : ℝ → X)
    (hc : ∀ t, HasDerivAt c (-∇E (c t)) t) :
    Monotone (fun t => -(E (c t))) := by

  -- Use derivative sign ⇒ monotonicity
  apply monotone_of_deriv_nonneg
  intro t

  have hderiv := energy_derivative_eq E ∇E hE c hc t

  -- derivative of -(E(c t)) is ‖∇E‖² ≥ 0
  have h' : HasDerivAt (fun t => -(E (c t))) (‖∇E (c t)‖ ^ 2) t := by
    simpa using hderiv.neg

  have : 0 ≤ ‖∇E (c t)‖ ^ 2 := by positivity

  exact ⟨h', this⟩

/-- Critical points ↔ zero gradient. -/
theorem critical_point_iff_gradient_zero
    {X : Type*} [NormedAddCommGroup X] [InnerProductSpace ℝ X]
    (∇E : X → X) (c : ℝ → X) (t : ℝ) :
    (- ‖∇E (c t)‖ ^ 2 = 0) ↔ (∇E (c t) = 0) := by
  constructor
  · intro h
    have : ‖∇E (c t)‖ = 0 := by
      have := sq_nonneg ‖∇E (c t)‖
      nlinarith
    exact norm_eq_zero.mp this
  · intro h
    simp [h]

-- ─────────────────────────────────────────────────────────────
-- 2. Entropy production
-- ─────────────────────────────────────────────────────────────

theorem entropy_production_nonneg
    {H : Type*} [SeminormedAddCommGroup H] [InnerProductSpace ℝ H]
    (A : H →L[ℝ] H)
    (hA : ∀ ξ : H, 0 ≤ inner (A ξ) ξ)
    (ξ : H) :
    0 ≤ inner (A ξ) ξ := hA ξ

theorem discrete_entropy_increase
    (S_old S_new : ℝ)
    (flux_in flux_out : ℝ)
    (σ : ℝ)
    (hσ : 0 ≤ σ)
    (hbal : S_new = S_old - flux_out + flux_in + σ)
    (hclosed : flux_in = flux_out) :
    S_old ≤ S_new := by
  rw [hbal, hclosed]
  linarith

/-- Simpler and more robust version using derivative ≥ 0. -/
theorem total_entropy_nondecreasing
    (S : ℝ → ℝ)
    (σ : ℝ → ℝ)
    (hσ : ∀ t, 0 ≤ σ t)
    (hderiv : ∀ t, HasDerivAt S (σ t) t) :
    Monotone S := by
  apply monotone_of_deriv_nonneg
  intro t
  have h := hderiv t
  exact ⟨h, hσ t⟩

-- ─────────────────────────────────────────────────────────────
-- 3. Conservation law
-- ─────────────────────────────────────────────────────────────

theorem conservation_from_zero_derivative
    (ρ : ℝ → ℝ)
    (hρ : ∀ t, HasDerivAt ρ 0 t) :
    ∀ s t : ℝ, ρ s = ρ t := by
  intro s t
  have hconst := isConst_of_hasDerivAt_zero ρ hρ
  exact hconst.eq_of_mem ⟨⟩ ⟨⟩

theorem energy_conserved_closed_system
    (E : ℝ → ℝ)
    (hE : ∀ t, HasDerivAt E 0 t) :
    Monotone E ∧ Antitone E := by
  constructor
  · intro s t _
    exact le_of_eq (conservation_from_zero_derivative E hE s t)
  · intro s t _
    exact le_of_eq (conservation_from_zero_derivative E hE t s).symm

-- ─────────────────────────────────────────────────────────────
-- 4. Finite propagation
-- ─────────────────────────────────────────────────────────────

structure PropagationSystem where
  speed : ℝ
  speed_pos : 0 < speed

def causalCone (sys : PropagationSystem) (x₀ t₀ : ℝ) (t : ℝ) : Set ℝ :=
  { x : ℝ | |x - x₀| ≤ sys.speed * (t - t₀) }

theorem causal_cone_nonempty
    (sys : PropagationSystem) (x₀ t₀ t : ℝ) (ht : t₀ ≤ t) :
    x₀ ∈ causalCone sys x₀ t₀ t := by
  simp [causalCone]
  have : 0 ≤ sys.speed * (t - t₀) := by
    have := sub_nonneg.mpr ht
    positivity
  simpa using this

theorem global_consistency_lower_bound
    (sys : PropagationSystem)
    (diameter : ℝ) (hd : 0 < diameter) :
    ∃ t_min : ℝ, t_min = diameter / sys.speed ∧ 0 < t_min := by
  refine ⟨diameter / sys.speed, rfl, ?_⟩
  positivity

theorem finite_propagation_no_instant_action
    (sys : PropagationSystem)
    (x y : ℝ) (hxy : x ≠ y) :
    ∀ t₀ : ℝ, ¬ (y ∈ causalCone sys x t₀ t₀) := by
  intro t₀ hy
  simp [causalCone] at hy
  have : |y - x| > 0 := by
    have h : y - x ≠ 0 := sub_ne_zero.mpr hxy
    simpa using abs_pos.mpr h
  have rhs : sys.speed * (t₀ - t₀) = 0 := by ring
  have : |y - x| ≤ 0 := by simpa [rhs] using hy
  exact lt_irrefl _ (lt_of_le_of_lt this this)

end EnergyAsContradiction.Dynamics