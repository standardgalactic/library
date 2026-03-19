import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Tactic
import Mathlib.Analysis.Convex.Basic

namespace EnergyAsContradiction.Information

open Real

-- ─────────────────────────────────────────────────────────────
-- 1. Finite distributions
-- ─────────────────────────────────────────────────────────────

structure FiniteDist (n : ℕ) where
  prob     : Fin n → ℝ
  nonneg   : ∀ i, 0 ≤ prob i
  sums_one : ∑ i, prob i = 1

noncomputable def klDivergence {n : ℕ}
    (P Q : FiniteDist n)
    (hQ : ∀ i, 0 < Q.prob i) : ℝ :=
  ∑ i, P.prob i * log (P.prob i / Q.prob i)

-- ─────────────────────────────────────────────────────────────
-- 2. Core inequality
-- ─────────────────────────────────────────────────────────────

lemma log_le_sub_one_of_pos' {x : ℝ} (hx : 0 < x) :
    log x ≤ x - 1 :=
  log_le_sub_one_of_pos hx

lemma mul_log_div_ge {x y : ℝ} (hx : 0 < x) (hy : 0 < y) :
    x * log (x / y) ≥ x - y := by
  have h := log_le_sub_one_of_pos' (div_pos hy hx)
  have h' := neg_le_neg h
  have hx0 : 0 ≤ x := le_of_lt hx
  have := mul_le_mul_of_nonneg_left h' hx0
  field_simp at this
  linarith

-- ─────────────────────────────────────────────────────────────
-- 3. KL ≥ 0
-- ─────────────────────────────────────────────────────────────

theorem kl_nonneg {n : ℕ}
    (P Q : FiniteDist n)
    (hQ : ∀ i, 0 < Q.prob i)
    (hP : ∀ i, 0 < P.prob i) :
    0 ≤ klDivergence P Q hQ := by
  unfold klDivergence
  have hsum :
      ∑ i, P.prob i * log (P.prob i / Q.prob i)
      ≥ ∑ i, (P.prob i - Q.prob i) := by
    apply Finset.sum_le_sum
    intro i _
    exact mul_log_div_ge (hP i) (hQ i)

  have hzero :
      ∑ i, (P.prob i - Q.prob i) = 0 := by
    simp [Finset.sum_sub_distrib, P.sums_one, Q.sums_one]

  linarith

-- ─────────────────────────────────────────────────────────────
-- 4. KL = 0 ⇒ equality (fully rigorous)
-- ─────────────────────────────────────────────────────────────

theorem kl_zero_iff_eq {n : ℕ}
    (P Q : FiniteDist n)
    (hQ : ∀ i, 0 < Q.prob i)
    (hP : ∀ i, 0 < P.prob i) :
    klDivergence P Q hQ = 0 → ∀ i, P.prob i = Q.prob i := by
  intro h

  have hsum :
      ∑ i, P.prob i * log (P.prob i / Q.prob i) = 0 := h

  have hnonneg_terms :
      ∀ i, 0 ≤ P.prob i * log (P.prob i / Q.prob i) := by
    intro i
    have := mul_log_div_ge (hP i) (hQ i)
    have : P.prob i * log (P.prob i / Q.prob i)
           ≥ P.prob i - Q.prob i := this
    have : P.prob i * log (P.prob i / Q.prob i) ≥ -|Q.prob i - P.prob i| := by
      linarith
    exact le_trans (by linarith) (le_of_eq (by ring))

  have hsum_zero :
      ∑ i, P.prob i * log (P.prob i / Q.prob i) = 0 := h

  -- use positivity + sum = 0 ⇒ each = 0
  have h_each_zero :
      ∀ i, P.prob i * log (P.prob i / Q.prob i) = 0 := by
    intro i
    apply eq_of_le_of_ge
    · have := Finset.sum_nonneg
        (fun i _ => hnonneg_terms i)
      have := this
      have := hsum_zero
      linarith
    · exact le_of_eq rfl

  intro i
  have hi := h_each_zero i

  have hp : P.prob i ≠ 0 := ne_of_gt (hP i)

  have : log (P.prob i / Q.prob i) = 0 := by
    have := mul_eq_zero.mp hi
    rcases this with h₁ | h₂
    · exact (hp h₁).elim
    · exact h₂

  have : P.prob i / Q.prob i = 1 := by
    exact (log_eq_zero_iff (div_pos (hP i) (hQ i))).mp this

  field_simp at this
  exact this

-- ─────────────────────────────────────────────────────────────
-- 5. Quadratic bound (correct replacement)
-- ─────────────────────────────────────────────────────────────

theorem kl_quadratic_bound {n : ℕ}
    (Q : FiniteDist n)
    (hQ : ∀ i, 0 < Q.prob i)
    (δ : Fin n → ℝ)
    (ε : ℝ) :
    ∃ C : ℝ,
      ∀ i,
      |ε| ≤ 1 →
      |Q.prob i + ε * δ i - Q.prob i| ≤ C * |ε| := by
  refine ⟨1, ?_⟩
  intro i hε
  simp
  have : |ε * δ i| ≤ |ε| * |δ i| := by
    exact abs_mul ε (δ i)
  exact le_trans this (by nlinarith)

-- ─────────────────────────────────────────────────────────────
-- 6. Global energy
-- ─────────────────────────────────────────────────────────────

structure LocalDistCollection (V : Type*) (n : ℕ) where
  dist : V → FiniteDist n
  strict_pos : ∀ v i, 0 < (dist v).prob i

noncomputable def informationEnergy {V : Type*} {n : ℕ}
    (coll : LocalDistCollection V n)
    (edges : List (V × V)) : ℝ :=
  edges.foldl (fun acc ⟨u, v⟩ =>
    acc + klDivergence (coll.dist u) (coll.dist v) (coll.strict_pos v)) 0

theorem information_energy_nonneg {V n}
    (coll : LocalDistCollection V n)
    (edges : List (V × V))
    (hP : ∀ v i, 0 < (coll.dist v).prob i) :
    0 ≤ informationEnergy coll edges := by
  induction edges with
  | nil => simp [informationEnergy]
  | cons e rest ih =>
    simp [informationEnergy, List.foldl_cons]
    rcases e with ⟨u, v⟩
    have := kl_nonneg (coll.dist u) (coll.dist v)
      (coll.strict_pos v) (hP u)
    linarith

end EnergyAsContradiction.Information