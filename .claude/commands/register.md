---
description: Register encoding or corpus in research system
argument-hint: <type> <name> <description>
allowed-tools: Read, Write, Bash(python3:*)
---

# Register Component

Register an encoding or corpus for hypothesis testing.

## Arguments

- `$1` = type: `encoding` or `corpus`
- `$2` = name: identifier (e.g., `E_dot`)
- `$3` = description or filepath

## Task

Based on the arguments provided ($ARGUMENTS):

1. If registering an **encoding**:
   - Create file `src/encoding_functions/$2.py`
   - Implement encoding function based on description
   - Function must: `text -> bitstring` (only 0s and 1s)
   - Add registration call to the file

2. If registering a **corpus**:
   - Verify file exists at the path
   - Add corpus loading code

## Example Encoding Template

```python
# src/encoding_functions/$2.py
"""$3"""

from core.api import register_encoding

# Define letter sets based on property
SET_1 = set('...')  # Letters that map to 1
SET_0 = set('...')  # Letters that map to 0

def encode(text: str) -> str:
    """$3"""
    result = []
    for char in text:
        if '\u0621' <= char <= '\u064A':  # Arabic letter range
            result.append('1' if char in SET_1 else '0')
    return ''.join(result)

# Register with pre-registration
register_encoding(
    name="$2",
    fn=encode,
    description="$3",
    hypothesis="Structure in this encoding indicates...",
    preregistered=True
)
```

## Validation

After creating, verify with:
```python
import sys; sys.path.insert(0, 'src')
from core.api import list_registered
print(list_registered()['encodings'])
```
