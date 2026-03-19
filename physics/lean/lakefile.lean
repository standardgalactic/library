import Lake
open Lake DSL

package «EnergyAsContradiction» where
  name := `EnergyAsContradiction

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.14.0"

lean_lib «EnergyAsContradiction» where
  roots := #[
    `RelationalSystems,
    `EnergyFunctionals,
    `ConstraintDynamics,
    `InformationTheoretic,
    `NonClosure,
    `GradientFlow,
    `ConstraintEnergyCategory,
    `EnergyUnification
  ]