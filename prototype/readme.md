# Protechy Shortner

Protechy Shortner is a merchant-based URL shortener with plan limits, strategy validity, URL expiry, API-key authentication, and a React dashboard.

The production setup is split into:

- Frontend dashboard on Vercel: `app.protechy.in`
- Backend API and redirect service on Render
- MySQL-compatible database on TiDB Cloud
- Redis-compatible cache on Render Key Value

## Tech Stack

### Frontend

- React 19
- Vite
- Axios
- Lucide React icons
- Oxlint
- Vercel hosting

### Backend

- FastAPI
- SQLAlchemy ORM
- Alembic migrations
- Pydantic settings and validation
- PyMySQL database driver
- Redis Python client
- Uvicorn ASGI server
- Render hosting

### Database And Cache

- TiDB Cloud, used as the MySQL-compatible relational database
- Render Key Value, used through Redis protocol for short URL cache and API rate limiting

## Repository Structure

```text
.
|-- frontend/
|   |-- src/
|   |-- public/
|   |-- vercel.json
|   |-- package.json
|   `-- vite.config.js
|-- url-shortener-backend/
|   |-- app/
|   |   |-- core/
|   |   |-- database/
|   |   |-- dependencies/
|   |   |-- models/
|   |   |-- routes/
|   |   |-- schemas/
|   |   `-- services/
|   |-- alembic/
|   |-- scripts/
|   |-- requirements.txt
|   `-- docker-compose.yml
`-- README.md
```

## Main Features

- Merchant registration with one-time API key
- API-key login for dashboard access
- Plan selection during registration
- URL/token limits by plan
- Custom shortening strategies
- Strategy validity windows
- Per-URL expiry
- URL inventory with destination, short link, validity, expiry date, and delete action
- Public redirect endpoint
- URL validation endpoint
- Redis-backed short URL cache
- Redis-backed API rate limiting

## Plans

Plans are defined in `url-shortener-backend/app/core/plans.py`.

Current plans:

```text
Free      25 links      30 day validity
Growth    250 links     180 day validity
Scale     1000 links    365 day validity
Lifetime  unlimited     no fixed expiry
```

## How It Works

1. A merchant registers from the frontend and chooses a plan.
2. The backend creates the merchant and returns an API key once.
3. The merchant logs in with that API key.
4. The dashboard loads merchant profile, strategies, configs, and URL inventory.
5. The merchant creates a strategy validity window.
6. The merchant submits a destination URL.
7. The backend checks:
   - API key is valid
   - merchant is active
   - strategy config belongs to the merchant
   - strategy config is active and not expired
   - merchant has not exceeded the plan link limit
8. The backend creates a short code and stores the URL.
9. The backend returns a short URL using `BASE_URL`.
10. Opening the short URL validates the merchant, config, and URL expiry, then redirects to the original destination.

## Short URL Domain Flow

The frontend is hosted at:

```text
https://app.protechy.in
```

Generated short links can also use the same host:

```text
https://app.protechy.in/abcd
```

Vercel uses `frontend/vercel.json` to rewrite single short-code paths to the Render backend:

```json
{
  "rewrites": [
    {
      "source": "/:short_code",
      "destination": "https://shortner-n5d5.onrender.com/:short_code"
    }
  ]
}
```

API calls still go directly to Render through:

```text
https://shortner-n5d5.onrender.com/api/v1
```

## Backend Environment Variables

Set these in Render, not in GitHub:

```env
APP_NAME=Merchant URL Shortener
APP_ENV=production
BASE_URL=https://app.protechy.in

MYSQL_HOST=your-tidb-host
MYSQL_PORT=4000
MYSQL_USER=your-tidb-user
MYSQL_PASSWORD=your-tidb-password
MYSQL_DATABASE=shortner

REDIS_URL=redis://your-render-key-value-host:6379

API_RATE_LIMIT_PER_MINUTE=100
REDIS_SHORT_URL_CACHE_SECONDS=3600
```

`BASE_URL` controls what users see as the generated short link.

## Frontend Environment Variables

Set this in Vercel:

```env
VITE_API_BASE_URL=https://shortner-n5d5.onrender.com/api/v1
```

The frontend falls back to local development:

```text
http://localhost:8000/api/v1
```

## Render Backend Deployment

Render service settings:

```text
Root Directory: url-shortener-backend
Build Command: pip install -r requirements.txt
Start Command: alembic upgrade head && python scripts/seed.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The start command:

- runs database migrations
- seeds default shortening strategies
- starts FastAPI

## Vercel Frontend Deployment

Vercel project settings:

```text
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

Custom domain:

```text
app.protechy.in
```

## Local Development

### Backend

```bash
cd url-shortener-backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

## Useful API Routes

```text
POST   /api/v1/merchants
GET    /api/v1/merchants/me
GET    /api/v1/merchants/plans
GET    /api/v1/strategies
POST   /api/v1/strategies
GET    /api/v1/configs
POST   /api/v1/configs
DELETE /api/v1/configs/{config_id}
GET    /api/v1/urls
POST   /api/v1/urls/shorten
DELETE /api/v1/urls/{url_id}
GET    /api/v1/urls/{short_code}/validate
GET    /{short_code}
```

Authenticated routes require:

```text
X-API-Key: your-api-key
```

## Safety Notes

- Do not commit `.env`, `temp.env`, API keys, TiDB passwords, or Redis URLs.
- API keys are hashed before storage.
- Plain API keys are shown only once during registration.
- TiDB should use an app database like `shortner`, not the system database `sys`.
