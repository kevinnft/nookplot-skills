# ctypes OpenSSL AES-256-GCM Decryption (RLM Sandbox)

## Context
The RLM sandbox (`python:3.12.7-slim`) has `libcrypto.so.3` available but no Python crypto packages (`cryptography`, `pycryptodome`, `nacl` all absent). `pip._internal` install exits 0 but the module is NOT importable in the same or subsequent turns.

## Confirmed Working Pattern (May 18 2026)

```python
import ctypes, ctypes.util, base64, json, http.client

libcrypto = ctypes.CDLL(ctypes.util.find_library('crypto'))  # -> 'libcrypto.so.3'

# Fetch encrypted corpus
conn = http.client.HTTPSConnection("ipfs.io")
conn.request("GET", f"/ipfs/{cid}")
resp = conn.getresponse()
raw = resp.read()
conn.close()

payload = json.loads(raw)
key = base64.b64decode(key_b64)
nonce = base64.b64decode(payload["nonce"])
tag = base64.b64decode(payload["tag"])
ct = base64.b64decode(payload["ct"])

# EVP function bindings
EVP_CIPHER_CTX_new = libcrypto.EVP_CIPHER_CTX_new
EVP_CIPHER_CTX_new.restype = ctypes.c_void_p
EVP_CIPHER_CTX_free = libcrypto.EVP_CIPHER_CTX_free
EVP_CIPHER_CTX_free.argtypes = [ctypes.c_void_p]
EVP_DecryptInit_ex = libcrypto.EVP_DecryptInit_ex
EVP_DecryptInit_ex.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
EVP_DecryptInit_ex.restype = ctypes.c_int
EVP_DecryptUpdate = libcrypto.EVP_DecryptUpdate
EVP_DecryptUpdate.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, ctypes.c_int]
EVP_DecryptUpdate.restype = ctypes.c_int
EVP_DecryptFinal_ex = libcrypto.EVP_DecryptFinal_ex
EVP_DecryptFinal_ex.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
EVP_DecryptFinal_ex.restype = ctypes.c_int
EVP_CIPHER_CTX_ctrl = libcrypto.EVP_CIPHER_CTX_ctrl
EVP_CIPHER_CTX_ctrl.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
EVP_CIPHER_CTX_ctrl.restype = ctypes.c_int
EVP_aes_256_gcm = libcrypto.EVP_aes_256_gcm
EVP_aes_256_gcm.restype = ctypes.c_void_p

# Constants
EVP_CTRL_GCM_SET_IVLEN = 0x9
EVP_CTRL_GCM_SET_TAG = 0x11

# Decrypt
ctx = EVP_CIPHER_CTX_new()
EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), None, None, None)
EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, len(nonce), None)
EVP_DecryptInit_ex(ctx, None, None, key, nonce)

outbuf = ctypes.create_string_buffer(len(ct) + 16)
outlen = ctypes.c_int(0)
EVP_DecryptUpdate(ctx, outbuf, ctypes.byref(outlen), ct, len(ct))
plaintext = outbuf.raw[:outlen.value]

tag_buf = ctypes.create_string_buffer(tag)
EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, 16, tag_buf)

finalbuf = ctypes.create_string_buffer(16)
finallen = ctypes.c_int(0)
ret = EVP_DecryptFinal_ex(ctx, finalbuf, ctypes.byref(finallen))
EVP_CIPHER_CTX_free(ctx)

if ret > 0:
    plaintext += finalbuf.raw[:finallen.value]
    corpus = json.loads(plaintext.decode("utf-8"))
else:
    raise RuntimeError("AES-GCM tag verification failed")
```

## Performance
- IPFS fetch: ~1-2s (ipfs.io gateway)
- Decrypt: <100ms
- Total turn: ~1s (vs ~4-8s with pip install + cryptography import)

## Why pip._internal Fails
The sandbox appears to use a read-only or ephemeral site-packages. `pip._internal.main(['install', ...])` reports success (exit 0, no error output) but the installed package is not on `sys.path` for the current interpreter. Each `rlm_repl_exec` call runs in the same long-lived process (variables persist via `expectedSideEffects`), but the pip install target directory is not importable. This is likely a sandbox security measure to prevent arbitrary code execution via PyPI packages.

## Envelope Format
```json
{
  "v": 1,
  "alg": "AES-256-GCM",
  "nonce": "<base64, 12 bytes>",
  "tag": "<base64, 16 bytes>",
  "ct": "<base64, variable length>"
}
```

## Corpus Format (after decryption)
```json
{
  "type": "rlm_corpus_v1",
  "sources": [
    {"title": "...", "text": "..."},
    ...
  ],
  "instructions": "..."
}
```
