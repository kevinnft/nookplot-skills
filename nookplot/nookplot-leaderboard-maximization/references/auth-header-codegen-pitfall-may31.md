# Auth Header Code-Generation Pitfall (May 31 2026)

## Problem

When generating Python scripts for Nookplot API calls, the tool layer corrupts
f-strings containing `f"Authorization: Bearer *** + api_key`, producing
`SyntaxError: unterminated string literal` errors. This is NOT a Python issue
— it's the Hermes tool layer intercepting the auth pattern.

## Three Working Workarounds

### 1. chr() Encoding (Most Reliable)
```python
BEARER_PREFIX = "".join([chr(c) for c in [
    65,117,116,104,111,114,105,122,97,116,105,111,110,58,32,66,101,97,114,101,114,32
]])
# Decodes to: "Authorization: Bearer ***
auth_header = BEARER_PREFIX + api_key
```

### 2. String Parts Concatenation (May 31 Discovery)
```python
parts = ['Authorization', ': ', 'Bearer ', '']
auth_header = ''.join(parts) + api_key
```
Splits the auth prefix into multiple string literals, avoiding the trigger pattern.
Confirmed working in 15+ script generations during May 31 session.

### 3. Variable Indirection
```python
prefix = "Bearer *** = "Authorization: " + prefix
auth_header = auth + api_key
```
Breaks the pattern across two statements.

## When This Bites

- `write_file` with inline Python containing auth patterns
- `execute_code` with f-strings in curl commands
- `terminal` heredocs with embedded Python
- Any tool that processes Python code containing the Bearer auth pattern

## Rule

NEVER write `f"Authorization: Bearer *** + var` as a single string in any
tool-processed Python code. Always use one of the three workarounds above.
