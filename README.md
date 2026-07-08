# Python URL Shortener

A simple and stylish URL shortener built with FastAPI, Jinja2, Pydantic, and MySQL. The app accepts a long URL, validates it, stores it in a database, and returns a short link that redirects users to the original destination.

The app is deployed on Render at:

https://python-url-shortener.onrender.com

## Features

- Create short links from long URLs
- Validate URLs before saving
- Automatically add `https://` to URLs that do not include a scheme
- Optional Base62 or SHA-256 hash encoding for short link IDs
- Serve a clean frontend with a modern landing page
- Redirect short links back to the original URL
- Store links in a MySQL database

## Project Structure

- `basev2.py` - Main FastAPI application with routes for the home page, link generation, and redirect handling
- `templates/index.html` - Homepage template for the shortener UI
- `static/index.css` - Styling for the frontend
- `README.md` - Project documentation

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Jinja2
- Pydantic
- mysql-connector-python

## Requirements

Install the required packages with:

```bash
pip install fastapi uvicorn jinja2 pydantic mysql-connector-python base62
```

If you prefer to manage dependencies in a requirements file, add:

```txt
fastapi
uvicorn
jinja2
pydantic
mysql-connector-python
base62
```

## Database Setup

This project uses a MySQL database connection in `basev2.py`. It inserts records into a table named `users` with at least these columns:

```sql
CREATE TABLE users (
    id VARCHAR(128) PRIMARY KEY,
    originalLink VARCHAR(2048) NOT NULL,
    encoding VARCHAR(32)
);
```

> Important: The app currently uses hardcoded database credentials. For production, move these into environment variables or a secure configuration file.

## Running Locally

From the project root, run:

```bash
uvicorn basev2:api --reload
```

Then open your browser at:

```text
http://127.0.0.1:8000/
```

## How It Works

1. Open the homepage.
2. Paste a long URL into the form.
3. The app validates the URL and adds `https://` if needed.
4. Choose an optional encoding type:
   - default hex token
   - Base62 token
   - SHA-256 hash
5. A short ID is generated and stored in the database.
6. The app displays the generated short link.
7. Visiting that short link redirects the user to the original URL.

## API Endpoints

### GET /
Returns the homepage HTML interface.

### POST /genlink
Accepts a form field named `original` containing the long URL.

- Validates the input
- Saves the URL to the database
- Returns the generated short link in the page context

### GET /{retrieve_link}
Redirects the user to the original URL associated with the short ID.

If the ID does not exist, the app returns an error response.

## Frontend

The UI is built with:

- an HTML form for entering URLs
- Jinja templates for rendering the response
- CSS styling in `static/index.css`

The page includes:

- a friendly hero section
- a prominent input field
- optional encoding controls
- copy-to-clipboard support for the generated link

## Example Usage

```bash
curl -X POST https://python-url-shortener.onrender.com/genlink \
  -d "original=https://example.com/some/very/long/path"
```

The page will display a shortened URL such as:

```text
https://python-url-shortener.onrender.com/<short_id>
```

## Notes and Improvements

This project is a simple demo with a working Render deployment. Future improvements include:

- moving database credentials to environment variables
- adding a requirements file and dependency management
- improving error handling and user feedback
- adding custom short aliases
- adding link expiration or analytics
- adding tests

## License

This project is open for learning and personal use.
