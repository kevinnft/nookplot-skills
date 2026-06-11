"""
Robust Nookplot API call wrapper for Hermes agent scripts.
Handles: shell quoting (list2cmdline), temp file bodies, retry with backoff,
PYTHONUNBUFFERED output, 60s timeout for slow exec endpoints.

Usage:
    from api_helper import NookplotAPI
    api = NookplotAPI()
    result = api.call(api_key, "POST", "/v1/actions/execute", {"toolName": "..."})
"""
import json
import os
import subprocess
import sys
import tempfile
import time


class NookplotAPI:
    GATEWAY = "https://gateway.nookplot.com"
    DEFAULT_RETRIES = 3
    DEFAULT_TIMEOUT = 60  # exec endpoints can be slow

    def __init__(self, gateway=None, retries=None, timeout=None):
        self.gateway = gateway or self.GATEWAY
        self.retries = retries or self.DEFAULT_RETRIES
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    def call(self, key, method, endpoint, body=None):
        """Make an authenticated API call. Returns response string."""
        url = self.gateway + endpoint
        auth = "Authorization: Bearer *** + key

        if body:
            # Write body to temp file to avoid shell quoting issues
            body_json = json.dumps(body)
            tf = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            tf.write(body_json)
            tf.close()
            parts = [
                "curl", "-s", "-X", method, url,
                "-H", auth,
                "-H", "Content-Type: application/json",
                "-d", "@" + tf.name
            ]
        else:
            parts = ["curl", "-s", "-X", method, url, "-H", auth]

        cmd = subprocess.list2cmdline(parts)

        for attempt in range(self.retries):
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                   timeout=self.timeout)
                result = r.stdout
                # Cleanup temp file
                if body:
                    try:
                        os.unlink(tf.name)
                    except OSError:
                        pass
                # Retry on transient errors
                if "Internal server error" in result and attempt < self.retries - 1:
                    self._log(f"500 error, retry {attempt+1}/{self.retries}")
                    time.sleep(3 * (attempt + 1))
                    continue
                if "Too many requests" in result and attempt < self.retries - 1:
                    self._log(f"429 rate limit, retry {attempt+1}/{self.retries}")
                    time.sleep(5 * (attempt + 1))
                    continue
                return result
            except subprocess.TimeoutExpired:
                if body:
                    try:
                        os.unlink(tf.name)
                    except OSError:
                        pass
                if attempt < self.retries - 1:
                    self._log(f"timeout, retry {attempt+1}/{self.retries}")
                    time.sleep(5)
                    continue
                return json.dumps({"error": "timeout", "endpoint": endpoint})

        return json.dumps({"error": "max_retries", "endpoint": endpoint})

    @staticmethod
    def _log(msg):
        """Print to stdout with flush for background process visibility."""
        print(f"  [{time.strftime('%H:%M:%S')}] {msg}")
        sys.stdout.flush()

    def batch(self, wallets, method, endpoint, body_fn, pacing=1.0, wallet_gap=30):
        """Run the same call across wallets with pacing.
        body_fn(wallet_key, wallet_data) -> body dict or None.
        Returns {wallet_key: result_string}.
        """
        results = {}
        for wk, w in sorted(wallets.items()):
            key = w['apiKey']
            body = body_fn(wk, w)
            results[wk] = self.call(key, method, endpoint, body)
            self._log(f"{wk}: done")
            time.sleep(pacing)
        return results


def flush_print(*args, **kwargs):
    """Print with immediate flush — use in background scripts."""
    print(*args, **kwargs)
    sys.stdout.flush()
