# Text as Substrate

### Semantic Compression and the Future of Media

A framework for moving beyond signal-based compression (MP3, H.265) toward **semantic compression**, where media is represented as structured descriptions that can be generatively reconstructed.

---

## Overview

Traditional media systems treat signals (audio waveforms, pixel arrays) as the primary object.

This project explores a different model:

> Media is not stored as a signal.
> Media is stored as a description of how to generate the signal.

This shift turns files into programs and transforms compression into an interpretive process.

---

## Core Idea

At the center of this framework is **entropy redistribution**:

```
H_total ≈ H_description + H_model
```

Instead of sending all information through bandwidth, part of it is stored in a shared generative model.

* Small description → transmitted
* Large prior knowledge → already known by decoder

**Result:** massive compression without losing perceived meaning.

---

## Key Concepts

### 1. Signal vs Meaning

| Traditional Compression | Semantic Compression  |
| ----------------------- | --------------------- |
| Stores signals          | Stores descriptions   |
| Removes redundancy      | Encodes structure     |
| Decoder reconstructs    | Decoder generates     |
| Artifact errors         | Interpretation errors |

---

### 2. Audio as Structured Text

Audio is decomposed into:

* T = text (words)
* P = prosody (timing, pitch)
* V = voice identity
* E = emotion

  Audio → (T, P, V, E)

---

### 3. Video as Scenario Graph

Video is no longer frames. It becomes:

* Agents
* Actions
* Environment
* Camera motion

  Video → (Scene, Environment, Camera)

---

### 4. Prototype + Deviation Encoding

Instead of storing everything:

1. Pick a prototype
2. Encode the difference

Example:

* "chair" (prototype)
* "red, broken, tilted" (deviation)

---

### 5. Global Coherence

All parts of a scene must agree.

Example:

* Lighting
* Identity
* Physical consistency

This prevents contradictions in generated output.

---

## Real-World Example: ASL

American Sign Language naturally uses semantic compression.

| ASL Feature   | Equivalent      |
| ------------- | --------------- |
| Handshapes    | Prototypes      |
| Motion        | Deviations      |
| Face          | Global context  |
| Dominant hand | Reference frame |

ASL encodes meaning, not sound.

---

## System Effects

### Rendering Bottleneck

* Transmission becomes cheap
* Compute becomes expensive

Quality depends on device capability.

---

### Semantic Drift

Risks include:

* Collapse into generic outputs
* Loss of diversity
* Model self-reinforcement

Mitigation:

* Real-world data injection
* Expanding prototype sets

---

## Implications

### Media

* Files → programs
* Video → simulation
* Audio → structured intent

### Infrastructure

* Less bandwidth needed
* More local compute required

### Epistemology

* Harder to verify authenticity
* Easier to modify causality
* Reality becomes reconstructible

---

## Summary

Semantic compression changes everything:

* We stop storing signals
* We start storing meaning
* We reconstruct reality instead of recording it

> The most efficient way to transmit a world
> is not to send its signal,
> but to send how to generate it.
