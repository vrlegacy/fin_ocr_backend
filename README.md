# Neuberg Testing App

Monorepo containing a FastAPI backend and a Vite React frontend used for testing and development.

## Repository layout

- `neuberg-backend/` — FastAPI backend (Python).
- `neuberg-frontend/` — Vite + React frontend (TypeScript/JS).

## Prerequisites

- Python 3.10+ (for backend)
- Node 18+ and a package manager (`pnpm`, `npm`, or `yarn`) (for frontend)
- Optional: PostgreSQL or another DB if you replace the default SQLite URL

## Backend (neuberg-backend)

1. Create and activate a virtual environment, then install dependencies:

```bash
cd neuberg-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configuration

- The backend reads settings from a `.env` file by default. See `app/config.py` for available environment variables and defaults. Common variables:

- `DATABASE_URL` (default: `sqlite:///./finch_local.db`)
- `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET`
- `GEMINI_API_KEY`

Create a `.env` file in `neuberg-backend/` or export environment variables before running.

3. Run the development server:

```bash
# recommended (uses the project run entrypoint)
python run.py

# or directly with uvicorn
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

4. Open the API docs at: `http://127.0.0.1:8000/docs`

## Frontend (neuberg-frontend)

1. Install dependencies and start the dev server:

```bash
cd ../neuberg-frontend
# using pnpm
pnpm install
pnpm dev

# or using npm
npm install
npm run dev
```

2. The dev server (Vite) will typically run on `http://localhost:5173` — check the terminal output when starting.

## Notes

- The backend defaults to an SQLite database for local development. Change `DATABASE_URL` in `.env` to point to a production DB as needed.
- Auth0-related defaults are present in `app/config.py`; provide proper credentials in `.env` for authenticated flows.
- The frontend expects an available backend for full functionality; update API base URLs in the frontend if necessary.

## Quick start (two terminals)

Terminal 1 — backend:

```bash
cd neuberg-backend
source .venv/bin/activate
python run.py
```

Terminal 2 — frontend:

```bash
cd neuberg-frontend
pnpm install
pnpm dev
```

---

If you want, I can: add example `.env`, add a Makefile for common commands, or wire up a Docker Compose configuration. Which would you like next?
