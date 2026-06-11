# Execute_code F-String Redaction Pitfall — June 4 2026

**CRITICAL**: When using `execute_code`, f-strings with `*** patterns get the `*** redacted/stripped by Hermes, leaving unterminated string literals.

## The Bug

```python
# BROKEN — causes SyntaxError: unterminated string literal
key = "my_secret_key"
hdr = f"Authorization: Bearer ***
# Hermes sees: hdr = f"Authorization: Bearer "  (curly brace stripped, string broken)
```

## The Fix

Use string concatenation instead:

```python
# WORKS
key = "my_secret_key"
hdr = "Authorization: Bearer *** + key
# Result: "Authorization: Bearer my_secret_key"
```

Or build the header dict:

```python
headers = {"Authorization": "Bearer " + key}
```

## Why This Happens

Hermes has content filtering that strips certain patterns from tool inputs. The `*** looks like an incomplete placeholder/secret reference, so the filter removes it before the code reaches the sandbox.

## Related Patterns

Also affects:
- `f"{variable}"` inside strings that look like secrets (e.g., `f"***- Any f-string where the variable immediately follows `***

## Verification

If you see `SyntaxError: unterminated string literal` in execute_code output, check for f-strings with `{variable}` patterns immediately after special characters.
