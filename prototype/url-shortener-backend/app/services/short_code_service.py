import hashlib
import secrets
import string
import base64
import zlib
from uuid import uuid4, uuid5, NAMESPACE_URL

from sqlalchemy.orm import Session

from app.models.strategy import ShorteningStrategy
from app.models.url import Url

BASE62_ALPHABET = string.ascii_letters + string.digits
ALPHANUMERIC_ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits


def _random_from_alphabet(length: int, alphabet: str) -> str:
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _hash_algo(algo_name: str, length: int, original_url: str) -> str:
    salt = secrets.token_urlsafe(16)
    data = f"{original_url}:{salt}".encode("utf-8")
    h = hashlib.new(algo_name)
    h.update(data)
    return h.hexdigest()[:length]


def _base64_encode(length: int, original_url: str) -> str:
    salt = secrets.token_urlsafe(8)
    data = f"{original_url}:{salt}".encode("utf-8")
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip("=")[:length]


def _crc32_hash(length: int, original_url: str) -> str:
    salt = secrets.token_urlsafe(8)
    data = f"{original_url}:{salt}".encode("utf-8")
    crc = zlib.crc32(data) & 0xffffffff
    return f"{crc:08x}"[:length]


def _uuid_style(length: int, bits: int) -> str:
    token_bytes = 16 if bits <= 128 else 32
    return secrets.token_hex(token_bytes)[:length]


def generate_candidate(strategy: ShorteningStrategy, original_url: str) -> str:
    strategy_name = strategy.name.upper()
    length = strategy.output_length

    if "BASE62" in strategy_name:
        return _random_from_alphabet(length, BASE62_ALPHABET)
    if "MD5" in strategy_name:
        return _hash_algo("md5", length, original_url)
    if "SHA1" in strategy_name or "SHA_1" in strategy_name:
        return _hash_algo("sha1", length, original_url)
    if "SHA256" in strategy_name or "HASH_SHA256" in strategy_name:
        return _hash_algo("sha256", length, original_url)
    if "SHA512" in strategy_name:
        return _hash_algo("sha512", length, original_url)
    if "BLAKE2B" in strategy_name:
        return _hash_algo("blake2b", length, original_url)
    if "BASE64" in strategy_name:
        return _base64_encode(length, original_url)
    if "CRC32" in strategy_name:
        return _crc32_hash(length, original_url)
    if "RANDOM" in strategy_name or "ALPHANUMERIC" in strategy_name:
        return _random_from_alphabet(length, ALPHANUMERIC_ALPHABET)
    if "UUIDV5" in strategy_name:
        return uuid5(NAMESPACE_URL, original_url + secrets.token_urlsafe(8)).hex[:length]
    if "UUIDV4" in strategy_name:
        return uuid4().hex[:length]
    if "256" in strategy_name:
        return _uuid_style(length, 256)
    if "128" in strategy_name:
        return _uuid_style(length, 128)

    return uuid4().hex[:length]


def generate_unique_short_code(db: Session, strategy: ShorteningStrategy, original_url: str) -> str:
    for _ in range(10):
        candidate = generate_candidate(strategy, original_url)
        exists = db.query(Url).filter(Url.short_code == candidate).first()
        if not exists:
            return candidate

    raise ValueError("Could not generate a unique short code")
