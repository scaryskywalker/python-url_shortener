import re
import base62
import string
def is_sha256(value):
    if not isinstance(value, str):
        return False
    # SHA-256 is exactly 64 hex characters long
    return bool(re.fullmatch(r'[0-9a-fA-F]{64}', value))


BASE62_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
# '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

def base62_decode(s: str, alphabet: str = BASE62_ALPHABET) -> int:
    if not s:
        raise ValueError("Input string must not be empty")

    base = len(alphabet)
    char_to_index = {char: idx for idx, char in enumerate(alphabet)}

    result = 0
    for char in s:
        if char not in char_to_index:
            raise ValueError(f"Invalid character '{char}' for base62 decoding")
        result = result * base + char_to_index[char]

    return result


if __name__ == "__main__":
    # quick tests
    print(base62_decode("0"))       
    print(base62_decode("1z"))    
    print(base62_decode("LygHa16"))  