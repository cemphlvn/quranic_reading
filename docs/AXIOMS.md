# Axioms

Minimal assumptions. Each must be necessary and unfalsifiable-by-design.

See also: [METHODOLOGY.md](METHODOLOGY.md) for application.

---

## A1: Discrete Encoding

```
Letters are discrete symbols.
Discrete symbols can be mapped to binary.
∴ Letters → {0,1} is well-defined.
```

*Justification: Mathematical fact, not empirical claim.*

## A2: Non-Uniqueness of Encoding

```
∀ letter set L, ∃ multiple functions f: L → {0,1}
No f is privileged a priori.
```

*Justification: Combinatorial fact.*

## A3: Falsifiability Requirement

```
Claim C is valid ⟺ ∃ test T where:
  - T can reject C
  - T was applied
  - C survived T
```

*Justification: Popperian criterion for science.*

## A4: Null Hypothesis Priority

```
H₀ (no structure) is assumed until rejected.
Rejection requires: p < α after multiple-comparison correction.
```

*Justification: Standard statistical practice.*

---

## Rejected/Deferred Principles

These are **hypotheses**, not axioms:

- ~~A3: Pattern-Meaning Correlation~~ → Empirical claim, needs testing
- ~~A5: Language as Functor~~ → Metaphorical, not operational
