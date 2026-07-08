# Merchant URL Shortener Backend

Backend-only FastAPI project for a merchant-based URL shortener. It uses MySQL for persistence, Redis for cache and rate limiting, SQLAlchemy ORM, Pydantic validation, Alembic migrations, Docker Compose, and API-key authentication.

## Features

- Merchant registration with one-time API key return
- SHA-256 API key hashing, never plain-text storage
- API key rotation for authenticated merchants
- Multiple shortening strategies per merchant through merchant configurations
- Strategy support for `BASE62_RANDOM`, `HASH_SHA256`, `RANDOM_ALPHANUMERIC`, plus 128-bit and 256-bit style names
- Redis short-code cache with TTL capped by configuration expiry
- Redis rate limiting per API key hash, default `100` requests per minute
- Public redirect endpoint with merchant and configuration validity checks
- Validation endpoint for debugging short-code status without redirecting
- Optional URL access logging

## Project Structure

```text
url-shortener-backend/
|-- app/
|   |-- main.py
|   |-- core/
|   |-- database/
|   |-- models/
|   |-- schemas/
|   |-- services/
|   |-- dependencies/
|   `-- routes/
|-- alembic/
|-- scripts/
|-- alembic.ini
|-- docker-compose.yml
|-- requirements.txt
|-- .env.example
`-- README.md
```

## Setup

Python.org lists Python `3.14.6` as the latest stable Python 3 release. This dependency set targets Python `3.14` and has been locally verified with Python `3.14.5`.

Create a local environment file:

```bash
cp .env.example .env
```

Start MySQL and Redis:

```bash
docker compose up -d
```

Install Python dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run migrations:

```bash
alembic upgrade head
```

Seed default strategies:

```bash
python scripts/seed.py
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://localhost:8000/docs
```

## Environment Variables

```env
APP_NAME=Merchant URL Shortener
APP_ENV=development
BASE_URL=http://localhost:8000

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=url_shortener_db

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

API_RATE_LIMIT_PER_MINUTE=100
REDIS_SHORT_URL_CACHE_SECONDS=3600
```

## Full API Testing Flow

### 1. Start infrastructure

```bash
docker compose up -d
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Start server

```bash
uvicorn app.main:app --reload
```

### 5. Open Swagger UI

```text
http://localhost:8000/docs
```

### 6. Create merchant

`POST /api/v1/merchants`

```json
{
  "merchant_code": "AMAZON01",
  "name": "Amazon",
  "account_details": "Demo merchant account"
}
```

Copy the returned `api_key`. It is shown only once.

### 7. Create strategy

`POST /api/v1/strategies`

```json
{
  "name": "BASE62_8",
  "output_length": 8,
  "description": "Base62 short code with 8 characters"
}
```

You can also run `python scripts/seed.py` to create:

- `BASE62_8`
- `SHA256_10`
- `RANDOM_6`

### 8. Create merchant config

`POST /api/v1/configs`

Header:

```text
X-API-Key: copied-api-key
```

Body:

```json
{
  "strategy_id": "uuid-here",
  "valid_until": "2027-07-07T00:00:00Z",
  "is_active": true
}
```

### 9. Generate short URL

`POST /api/v1/urls/shorten`

Header:

```text
X-API-Key: copied-api-key
```

Body:

```json
{
  "original_url": "https://example.com/products/mobile",
  "config_id": "uuid-here"
}
```

Response:

```json
{
  "url_id": "uuid",
  "short_code": "AbC123xy",
  "short_url": "http://localhost:8000/AbC123xy",
  "original_url": "https://example.com/products/mobile"
}
```

### 10. Validate short URL

`GET /api/v1/urls/{short_code}/validate`

This returns validation details without redirecting.

### 11. Open short URL

`GET /{short_code}`

If valid, the API returns a `302` redirect to `original_url`.

## Expected Results

- Merchant creation works
- API key generation works
- API key authentication works
- API key rotation works for the authenticated merchant
- Strategy creation and listing work
- Merchant configuration creation and listing work
- URL shortening works
- Redis cache uses keys like `shorturl:{short_code}`
- Redis rate limiting uses keys like `rate_limit:{api_key_hash}`
- Redirect works
- Expired or inactive configurations return proper errors

## Error Handling

- `400`: invalid request
- `401`: missing or invalid API key
- `403`: inactive merchant, inactive config, expired config, or config ownership mismatch
- `404`: strategy/config/short URL not found
- `409`: duplicate merchant code, strategy name, or short code conflict
- `429`: rate limit exceeded
- `500`: unhandled server error
