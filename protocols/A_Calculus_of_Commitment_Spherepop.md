# A Calculus of Commitment: Event-Historical Aggregation with Spherepop

Distributed data aggregation is a cornerstone of modern computing, enabling the synthesis of vast, decentralized datasets into coherent results. Dominant paradigms, from the foundational map-reduce framework to the more recent development of Conflict-free Replicated Data Types (CRDTs), have been tremendously successful. Yet, they share a foundational worldview: they are **value-centric**, treating aggregation as a mathematical function that maps a collection of input values to a final summary value.

This model, while powerful, is becoming strategically insufficient. Modern systems demand more than just results; they require provenance, auditable lineage, and the ability to enforce complex policies as intrinsic properties of computation, not as afterthoughts.

The value-centric approach suffers from a conceptual thinness that obscures the true nature of aggregation. By treating the final aggregate value as primary, it commits a **reification error**: mistaking the result for the process. In any system of consequence, aggregation is not merely a calculation; it is the construction of a durable, auditable **commitment** about which inputs were accepted and which alternatives were ruled out.

The **Spherepop calculus** offers a robust alternative grounded in an **event-historical semantics**. Its central thesis is simple but radical: the identity of a computed object is not its final state but the irreversible history of authorized events that brought it into being.

---

## 2. The Spherepop Calculus: Core Concepts

Spherepop inverts the state-based worldview. Objects are defined not by mutable values but by immutable histories.

### Event Histories
An **event history** `H = ⟨e₁, e₂, …, eₙ⟩` is a finite, totally ordered, prefix-closed sequence of events. Histories are append-only; the past is immutable.

### Authorization
Authorization is a primitive predicate `auth(H, e)` that determines whether an event `e` may extend a history `H`. This is the semantic core of Spherepop, enabling policy enforcement and domain invariants to depend on full history, not just current state.

### pop — Irreversible Commitment
A `pop` event asserts an object or fact as irrevocably true. Once committed, it cannot be undone—only built upon.

### Refusal
If `auth(H, e)` is false, the event is **refused**. Refusal is not an error; it is a structural impossibility. The forbidden event cannot occur in any admissible future.

### collapse — Controlled Forgetting
A `collapse` event explicitly forgets irrelevant distinctions between histories while preserving chosen invariants. This enables principled abstraction without silent loss of meaning.

---

## 3. Re-engineering Map-Reduce as Commitment

### Mapping Phase: Local Commitments
Each mapper processes a shard and produces a committed summary via `pop`, permanently linking the summary to its shard provenance.

### Reduction Phase: Authorized Merge
Reducer objects take the form `(v, P)` where `v` is the payload and `P` is a provenance set.

A merge is authorized **iff** provenance sets are disjoint:

```
auth((v₁, P₁), (v₂, P₂)) ⇔ P₁ ∩ P₂ = ∅
```

If authorized:
```
(v₁, P₁) ⊕ (v₂, P₂) = (v₁ ⊗ v₂, P₁ ∪ P₂)
```

### Emergent Algebraic Properties

- **Idempotence via Refusal**  
  Duplicate merges are refused, not absorbed.

- **Associativity & Commutativity up to Collapse**  
  Different merge orders produce distinct histories, which may be explicitly collapsed while preserving invariants.

---

## 4. Comparison with Classical Frameworks

### Classical Map-Reduce
Spherepop embeds provenance and policy enforcement directly into computation, rather than relegating them to logging or validation layers.

### CRDTs

**Theorem (CRDT Embedding):**  
Any CRDT can be represented as a Spherepop reducer by:
- disabling refusal,
- ignoring provenance,
- collapsing history after each merge.

**Theorem (Strict Extension):**  
Spherepop strictly generalizes CRDTs by supporting refusal, provenance-guarded merges, and history-sensitive policies.

---

## 5. Neural Attention as Event-Historical Aggregation

Attention mechanisms can be reinterpreted as event-historical reducers:

- **Weighted merge:** attention weights define authorization strength.
- **Masking:** attention masks correspond to refusal rules.
- **Multi-head attention:** parallel reducer histories with distinct policies.

Standard transformers immediately collapse this rich history, erasing auditability and semantic structure that Spherepop makes explicit and optional.

---

## 6. Architectural Implications

1. **Guaranteed Auditability** — lineage is intrinsic.
2. **Structural Policy Enforcement** — invalid actions are ill-formed, not handled.
3. **Streaming-Native Design** — append-only histories support incremental aggregation.
4. **Principled Abstraction** — collapse provides controlled forgetting.

---

## 7. Conclusion

Spherepop reframes aggregation as **world-building through irreversible commitment**. Map-reduce and CRDTs emerge as special cases where history is aggressively forgotten.

By making history first-class, Spherepop enables systems where accountability, policy, and meaning are not retrofits—but foundations.
