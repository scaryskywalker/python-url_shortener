import re

def is_sha256(value):
    if not isinstance(value, str):
        return False
    # SHA-256 is exactly 64 hex characters long
    return bool(re.fullmatch(r'[0-9a-fA-F]{64}', value))