# Python URL Shortener

A simple and stylish URL shortener built with FastAPI, Jinja2, Pydantic, and MySQL. The app accepts a long URL, validates it, stores it in a database, and returns a short link that redirects users to the original destination.

## Features

- Create short links from long URLs
- Validate URLs before saving
- Automatically add https:// to URLs that do not include a scheme
- Serve a clean frontend with a modern landing page
- Redirect short links back to the original URL
- Store links in a MySQL database

## Project Structure

- [basev2.py](basev2.py) - Main FastAPI application with routes for the home page, link generation, and redirect handling
- [templates/index.html](templates/index.html) - Homepage template for the shortener UI
- [static/index.css](static/index.css) - Styling for the frontend
- [README.md](README.md) - Project documentation

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Jinja2
- Pydantic
- MySQL Connector for Python

## Requirements

Install the required packages with:

```bash
pip install fastapi uvicorn jinja2 pydantic mysql-connector-python
```

If you prefer to manage dependencies in a requirements file, you can create one like this:

```txt
fastapi
uvicorn
jinja2
pydantic
mysql-connector-python
```

## Database Setup

This project currently uses a MySQL database connection in [basev2.py](basev2.py). It inserts records into a table named `users` with at least these columns:

```sql
CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY,
    originalLink VARCHAR(2048) NOT NULL
);
```

> Important: The app currently uses hardcoded database credentials. For real-world use, move these into environment variables or a secure configuration file.

## Running the Application

From the project root, run:

```bash
uvicorn basev2:api --reload
```

Or, if you are using the FastAPI CLI:

```bash
fastapi dev basev2.py
```

Then open your browser at:

```text
http://127.0.0.1:8000/
```

## How It Works

1. Open the homepage.
2. Paste a long URL into the form.
3. The app validates the URL and adds `https://` if needed.
4. A random short ID is generated.
5. The original URL is stored in MySQL along with the generated ID.
6. The app displays a short link such as:

```text
http://127.0.0.1:8000/<short_id>
```

7. Visiting that short link redirects the user to the original URL.

## API Endpoints

### GET /
Returns the homepage HTML interface.

### POST /genlink
Accepts a form field named `original` containing the long URL.

- Validates the input
- Saves it to the database
- Returns the generated short link in the page context

### GET /{retrieve_link}
Redirects the user to the original URL associated with the short ID.

If the ID does not exist, the app returns an error response.

## Frontend

The UI is built with:

- an HTML form for entering URLs
- Jinja templates for rendering the response
- CSS styling in [static/index.css](static/index.css)

The page includes:

- a friendly hero section
- a prominent input field
- a generate button
- a result area that shows the generated short URL

## Notes and Improvements

This is a beginner-friendly example project. Some improvements you could add next are:

- move database credentials to environment variables
- add a proper `requirements.txt`
- improve error handling and user feedback
- add custom short aliases
- add link expiration or analytics
- add a proper database abstraction layer
- add tests

## Example Usage

```bash
curl -X POST http://127.0.0.1:8000/genlink \
  -d "original=https://example.com/some/very/long/path"
```

You should receive a page containing the generated short link.

## License

This project is open for learning and personal use.
