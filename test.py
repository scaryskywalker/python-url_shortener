import string
import base62
import secrets

import hashlib


# token = secrets.token_hex(3)
# print(token)

# code = bytes.fromhex(token)
# print(code)
 

token_bytes = secrets.token_bytes(8)
print(token_bytes)

print(hashlib.sha256(token_bytes).hexdigest())







