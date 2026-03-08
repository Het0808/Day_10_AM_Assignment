# 💼 Interview Answers — Dicts, Hash Tables & Anagrams

---

## Q1 — Dict Time Complexity & Hash Tables

### Operation Complexity

| Operation | Average Case | Worst Case |
|-----------|-------------|------------|
| Lookup `d[k]` | **O(1)** | O(n) |
| Insert `d[k] = v` | **O(1)** | O(n) |
| Delete `del d[k]` | **O(1)** | O(n) |

### Why Average O(1)?

A Python dict is a **hash table**. When you write `d[key]`, Python:
1. Calls `hash(key)` → produces an integer in O(1)
2. Uses `hash % table_size` to compute a bucket index
3. Looks directly at that memory slot — **no searching**

The slot is found in a fixed number of steps regardless of how many items are in the dict, giving O(1) average time.

### What Causes Worst-Case O(n)?

**Hash collisions.** When two keys hash to the same bucket, Python uses **open addressing with pseudo-random probing** to find the next free slot. In theory, if every key collides (e.g., a deliberately crafted adversarial input), every insertion and lookup degrades to scanning all n slots → O(n).

Python 3.6+ mitigates this with **hash randomisation** (enabled by default via `PYTHONHASHSEED`), making it practically impossible for real-world code to hit O(n) accidentally.

### Hash Function: Strings vs Integers

- **Integers:** `hash(n) == n` for small ints (the value IS the hash). Very fast.
- **Strings:** Python hashes all characters using a polynomial rolling algorithm with a random seed (SipHash-1-3 on CPython 3.4+). The seed changes per process run so `hash("abc")` differs between interpreter restarts — this is the hash randomisation that prevents DoS attacks.

```python
# Integers: hash equals value (for small ints)
hash(42)   # → 42

# Strings: computed from all characters + random seed
hash("hello")  # → some large int, changes each run
```

### Dict vs List — When to Choose Which

| Scenario | Choose |
|----------|--------|
| Lookup by *key* (name, id, SKU) | **dict** — O(1) vs O(n) for list |
| Ordered sequence, access by *index* | **list** — lower memory overhead |
| Counting frequencies | **dict / Counter** |
| Deduplication while preserving mapping | **dict** |
| Simple iteration, append-heavy | **list** |
| Membership test on large dataset | **dict/set** (O(1)) vs list (O(n)) |

**Rule of thumb:** if you ever write `for item in list: if item.id == target`, replace the list with a dict keyed by `id`.

---

## Q2 — Group Anagrams

### Solution

```python
from collections import defaultdict

def group_anagrams(words: list[str]) -> dict[str, list[str]]:
    """
    Group words that are anagrams of each other.
    Signature key: sorted characters of the word joined as a string.

    Args:
        words: List of lowercase strings.

    Returns:
        Dict mapping anagram signature → list of matching words.

    Example:
        >>> group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])
        {'aet': ['eat', 'tea', 'ate'], 'ant': ['tan', 'nat'], 'abt': ['bat']}

    Time complexity:  O(n · k·log k)  where n = number of words, k = max word length
    Space complexity: O(n · k)
    """
    groups: defaultdict[str, list[str]] = defaultdict(list)

    for word in words:
        key = "".join(sorted(word))   # e.g. 'eat' → 'aet'
        groups[key].append(word)

    return dict(groups)
```

### Tests

```python
print(group_anagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat']))
# {'aet': ['eat', 'tea', 'ate'], 'ant': ['tan', 'nat'], 'abt': ['bat']}

print(group_anagrams([]))                 # → {}  (empty input)
print(group_anagrams(['abc']))            # → {'abc': ['abc']}  (single word)
print(group_anagrams(['a', 'b', 'a']))    # → {'a': ['a', 'a'], 'b': ['b']}  (dupes)
print(group_anagrams(['', '']))           # → {'': ['', '']}  (empty strings)
```

### Why `sorted(word)` Works as a Key

Two words are anagrams iff their sorted character sequences are identical.
`"eat"` → `['a','e','t']` → `"aet"` and `"tea"` → `"aet"` — same key, so they land in the same bucket. `defaultdict(list)` means we never need to check whether the key already exists; it initialises an empty list automatically.

---

## Q3 — Debug: Character Frequency Counter

### Buggy Code

```python
def char_freq(text):
    freq = {}
    for char in text:
        freq[char] += 1       # Bug 1
    sorted_freq = sorted(freq, key=freq.get, reverse=True)
    return sorted_freq        # Bug 2
```

### Bug 1 — `KeyError` on First Occurrence

**Why it fails:** `freq[char] += 1` expands to `freq[char] = freq[char] + 1`.
When `char` is seen for the first time, `freq[char]` on the right-hand side tries to read a key that doesn't exist yet → `KeyError`.

**Fix options (three ways):**
```python
# Option A: dict.get() with default
freq[char] = freq.get(char, 0) + 1      # ✅ safe access

# Option B: setdefault
freq.setdefault(char, 0)
freq[char] += 1

# Option C: defaultdict(int)
from collections import defaultdict
freq = defaultdict(int)
freq[char] += 1
```

### Bug 2 — Returns Keys Only, Not (key, count) Pairs

**Why it's wrong:** `sorted(freq, ...)` iterates over the **keys** of the dict (not key-value pairs). The return value is just a sorted list of characters with no associated counts.

**Fix:** iterate over `.items()` to get pairs:
```python
sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
# or equivalently:
sorted_freq = sorted(freq.items(), key=freq.get.__class__... )  # use items()
```

### Fixed Function

```python
def char_freq(text: str) -> list[tuple[str, int]]:
    """
    Count character frequencies in text, sorted by count descending.

    Args:
        text: Input string (any characters, including spaces).

    Returns:
        List of (character, count) tuples, highest count first.

    Example:
        >>> char_freq("hello")
        [('l', 2), ('h', 1), ('e', 1), ('o', 1)]
    """
    freq: dict[str, int] = {}

    for char in text:
        freq[char] = freq.get(char, 0) + 1    # Fix 1: safe .get() with default

    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return sorted_freq                         # Fix 2: return (key, count) pairs


# Tests
print(char_freq("hello"))          # [('l', 2), ('h', 1), ('e', 1), ('o', 1)]
print(char_freq(""))               # []  (empty string — no KeyError)
print(char_freq("aaa"))            # [('a', 3)]
print(char_freq("ab ba"))          # [(' ', 2), ('a', 2), ('b', 2)]  (includes spaces)
```
