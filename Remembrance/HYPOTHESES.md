# HYPOTHESES

## The Core Question

```
∃ f: Quran → Binary such that f reveals a non-random message?
```

Where message = pattern of 1 (to be / wujud) and 0 (not to be / adam).

---

## H0: The Existence Hypothesis (Meta)

```
CLAIM: There exists at least one encoding function f such that
       f(Quran) produces a bitstring with non-random structure
       that carries interpretable meaning.

TEST: Try multiple f candidates. If any reveals structure
      significantly different from null (random text → f → random bits),
      H0 is supported.

STATUS: ACTIVE — all other hypotheses are instances of this
```

---

## H1: f_dot — Morphological Encoding

**Owner:** project_alpha_thinker

```
f_dot(letter) = 1 if letter has dots, else 0

CLAIM: Dot-presence encodes semantic weight.
       Dotted letters mark "existence" (action, specificity).
       Undotted letters mark "void" (abstraction, divine).

TEST: Apply f_dot to Quran. Analyze:
      - Density by verse type (divine vs human)
      - Runs of 0s and 1s (what contexts?)
      - Compare with shuffled text

STATUS: PRELIMINARY DATA — Al-Fatiha shows pattern
```

---

## H2: f_muqatta — Key Encoding

**Owner:** project_beta_thinker

```
f_muqatta(surah) = binary signature of opening letters

CLAIM: Muqatta'at letters are keys that predict surah structure.
       Their binary encoding correlates with surah statistics.

TEST: Encode 29 muqatta'at surahs.
      Predict: letter frequencies, entropy, thematic markers.
      Compare predictions with actuals.

STATUS: UNTESTED
```

---

## H3: f_phonetic — Articulatory Encoding

**Owner:** project_gamma_thinker

```
f_voice(letter) = 1 if voiced, else 0
f_emphasis(letter) = 1 if emphatic, else 0
f_place(letter) = binary for articulation place

CLAIM: Phonetic features encode embodied meaning.
       Voiced = presence, agency.
       Voiceless = absence, passivity.

TEST: Apply phonetic encodings. Correlate with semantic roles.
      Cross-validate with cognitive linguistics predictions.

STATUS: UNTESTED
```

---

## H4: f_semantic — Direct Semantic Encoding

**Owner:** project_delta_thinker

```
f_divine(word) = 1 if refers to God/divine, else 0
f_command(verb) = 1 if imperative, else 0
f_negation(particle) = 1 if negative, else 0

CLAIM: Direct semantic categories map to binary.
       The resulting bitstring IS the message.
       Reading: sequence of divine/worldly, command/description, yes/no.

TEST: Apply semantic encodings at word level.
      Analyze resulting bitstream as message.
      What does it say?

STATUS: UNTESTED — requires morphological parsing
```

---

## H5: f_position — Structural Encoding

**Owner:** project_epsilon_thinker

```
f_odd(verse) = 1 if odd-numbered, else 0
f_begin(word) = 1 if at sentence start, else 0
f_prime(abjad) = 1 if abjad value is prime, else 0

CLAIM: Positional/numerical structure encodes hidden layer.
       Prime positions mark emphasis.
       Odd/even encodes duality.

TEST: Apply positional encodings.
      Look for non-random patterns.
      Compare with null model.

STATUS: UNTESTED
```

---

## The Method

For each f:

```
1. Define f precisely
2. Apply: f(Quran) → bitstring B
3. Analyze B:
   - Entropy (randomness)
   - Runs (clustering)
   - Autocorrelation (patterns)
   - Compression ratio (structure)
4. Compare with null:
   - f(shuffled_Quran) → B_null
   - Is B significantly different from B_null?
5. If different: interpret the message
6. Validate interpretation
```

---

## The Binary Message

If f exists, what form might the message take?

```
Sequence of:   1 1 0 1 0 0 1 1 1 0 ...
Meaning:       be be void be void void be be be void ...
Pattern:       existence asserts, withdraws, returns

Or: chunks as numbers
    1101 0011 = 13, 3 = ?

Or: runs as emphasis
    111 = strong existence
    000 = strong void
    101 = oscillation
```

The message format is itself a hypothesis.

---

*işte tek mesele bu — to be or not to be*
