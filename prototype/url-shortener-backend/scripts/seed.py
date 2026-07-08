import sys
from pathlib import Path

from sqlalchemy.exc import IntegrityError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.database.mysql import SessionLocal  # noqa: E402
from app.models.strategy import ShorteningStrategy  # noqa: E402


SEED_STRATEGIES = [
    ("BASE62_8", 8, "Base62 random short code with 8 characters"),
    ("SHA256_10", 10, "SHA-256 hash based short code with 10 hexadecimal characters"),
    ("RANDOM_6", 6, "Random alphanumeric short code with 6 characters"),
    ("MD5_8", 8, "MD5 hash based short code with 8 characters"),
    ("SHA1_12", 12, "SHA-1 hash based short code with 12 characters"),
    ("SHA512_16", 16, "SHA-512 hash based short code with 16 characters"),
    ("BLAKE2B_10", 10, "BLAKE2b hash based short code with 10 characters"),
    ("BASE64_8", 8, "Base64 encoded string based short code with 8 characters"),
    ("CRC32_8", 8, "CRC32 checksum based short code with 8 characters"),
    ("UUIDV4_8", 8, "UUIDv4 (Random) based short code with 8 characters"),
    ("UUIDV5_12", 12, "UUIDv5 (Named) based short code with 12 characters"),
]


def seed() -> None:
    db = SessionLocal()
    try:
        for name, output_length, description in SEED_STRATEGIES:
            exists = db.query(ShorteningStrategy).filter(ShorteningStrategy.name == name).first()
            if exists:
                print(f"exists: {name}")
                continue
            db.add(ShorteningStrategy(name=name, output_length=output_length, description=description))
            print(f"created: {name}")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
