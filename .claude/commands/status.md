---
description: Show registered components and research status
allowed-tools: Read, Bash(python3:*)
---

# Research Status

Show what's registered and ready for testing.

## Task

Run this status check:

```python
import sys; sys.path.insert(0, 'src')
from core.api import list_registered, ENCODINGS, CORPORA

reg = list_registered()

print("=" * 50)
print("REGISTERED COMPONENTS")
print("=" * 50)

print(f"\nCorpora ({len(reg['corpora'])}):")
for name in reg['corpora']:
    c = CORPORA[name]
    print(f"  - {name}: {len(c.text)} chars")

print(f"\nEncodings ({len(reg['encodings'])}):")
for name in reg['encodings']:
    e = ENCODINGS[name]
    pre = "[PRE]" if e.preregistered else "[POST]"
    print(f"  - {name} {pre}: {e.description}")

print(f"\nNulls ({len(reg['nulls'])}): {', '.join(reg['nulls'])}")
print(f"Metrics ({len(reg['metrics'])}): {', '.join(reg['metrics'])}")

print("\n" + "=" * 50)
print("SYSTEM STATUS")
print("=" * 50)

if not reg['corpora']:
    print("WARNING: No corpus loaded. Run: load_quran_corpus()")
if not reg['encodings']:
    print("WARNING: No encodings registered. Use /register")
if reg['corpora'] and reg['encodings']:
    print("READY: Can run /test <encoding>")
```

## What This Shows

1. **Corpora**: Loaded text sources (quran, etc.)
2. **Encodings**: Registered f(text)->bits functions
3. **Nulls**: Available null models (word_perm, block_k, random)
4. **Metrics**: Compression functions (zlib, bz2, lzma)

## Key Questions

- Corpus loaded? → Can test
- Encoding registered? → Can run /test
- Preregistered [PRE]? → Valid for claims
