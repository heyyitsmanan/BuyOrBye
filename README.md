# BuyOrBye

BuyOrBye is a Python-first product comparison app built with FastAPI.

It helps users paste product links, compare products by price, quality, and value, and get a recommendation for the best overall choice, the best budget pick, and the best quality pick.

## Why this stack

This project now uses:

- `FastAPI` for the backend and API routes
- `Jinja2` for server-rendered HTML templates
- plain `HTML/CSS/JavaScript` for the frontend

This is a good beginner-friendly setup because it lets you learn real Python backend development without forcing you to learn a heavy frontend framework immediately.

## Project structure

```text
BuyOrBye/
  app/
    main.py         FastAPI entry point
    data.py         seeded product data
    schemas.py      request/response models
    services.py     comparison logic
  static/
    app.js          frontend logic
    styles.css      app styles
    logos/          brand assets
  templates/
    index.html      homepage template
  requirements.txt
  LOGO_GUIDE.md
  Black.zip
```

## Current MVP

The current version is still an MVP.

That means it is the smallest useful version of the product that proves the idea:

- users can paste product links or keywords
- the app compares seeded product data
- the backend returns scores and recommendations
- the frontend displays the comparison nicely

Right now the comparison uses demo catalog data. Later we can replace that with real product extraction and external data sources.

## API routes

Current endpoints:

- `GET /` renders the app
- `GET /api/health` returns a simple health check
- `GET /api/samples` returns sample product links
- `POST /api/compare` compares submitted products

## Local setup

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## What you should learn from this structure

- `app/main.py` shows how the web server is created
- `app/services.py` contains the business logic
- `app/schemas.py` defines the data shape going in and out
- `templates/index.html` is the UI shell
- `static/app.js` calls the backend API and updates the page

This separation is important because it keeps the app easier to understand as it grows.

## Suggested next steps

1. Add a Python virtual environment and install FastAPI locally.
2. Run the project and get comfortable with the file structure.
3. Replace the seeded catalog with one real product category first.
4. Add a database once you need saved comparisons or cached product data.
5. Add AI summaries only after the product data layer is reliable.
