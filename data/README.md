# Data — Source of Truth

The Quran is the research object. Everything else is hypothesis.

## Source

```
quran/quran.json
```

- 114 surahs, 6236 verses
- Uthmani script (UTF-8)
- Source: [quran-json](https://github.com/risan/quran-json)

## Structure

```json
{
  "id": 1,
  "name": "الفاتحة",
  "transliteration": "Al-Fatihah",
  "type": "meccan|medinan",
  "total_verses": 7,
  "verses": [
    {"id": 1, "text": "بِسۡمِ ٱللَّهِ..."}
  ]
}
```

## The Question

```
∃ f: Text → Binary such that f(Quran) reveals hidden message?
```

Where "message" = pattern of 1s (existence) and 0s (non-existence).

## What f Could Be

Any function mapping semantic/structural features to binary:

| f | Mapping | Domain |
|---|---------|--------|
| f_dot | letter has dots → 1 | morphological |
| f_voice | voiced phoneme → 1 | phonetic |
| f_emphasis | emphatic consonant → 1 | phonetic |
| f_connect | letter connects → 1 | structural |
| f_abjad | odd abjad value → 1 | numerical |
| f_root | root letter → 1 | morphological |
| f_divine | divine name → 1 | semantic |
| f_command | imperative verb → 1 | grammatical |
| ... | ... | ... |

## The Method

1. Hypothesize f
2. Apply f(Quran) → bitstring
3. Analyze bitstring for non-random structure
4. If structure found: what does it say?
5. Validate: could this be chance?

The data speaks. We listen.
