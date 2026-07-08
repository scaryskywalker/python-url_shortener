from app.core.security import generate_api_key, hash_api_key


def create_api_key_pair() -> tuple[str, str]:
    api_key = generate_api_key()
    return api_key, hash_api_key(api_key)
