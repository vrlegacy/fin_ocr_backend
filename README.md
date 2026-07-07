# Fin OCR Backend

Live Application Frontend URL: [https://fin-ocr-frontend.pages.dev](https://fin-ocr-frontend.pages.dev)  
Backend API URL (Render): [https://finocr.onrender.com](https://finocr.onrender.com)

A robust backend API for the financial OCR application. Built with FastAPI, this service handles user authentication via Auth0, database interactions using SQLAlchemy (with support for SQLite locally and Supabase PostgreSQL in production), and AI-driven receipt extraction using the Google Gemini API.

## Features

- **FastAPI Framework**: High-performance asynchronous API backend.
- **Auth0 Authentication**: Secure login, signup, and token verification integration (`/auth/login`, `/auth/signup`).
- **Google Gemini OCR**: AI-powered extraction of expense details from receipts and invoices.
- **Expense Management**: Endpoints to create, read, update, and manage verified expenses.
- **Database agnostic**: Configured to work seamlessly with SQLite for local development and PostgreSQL (Supabase) for production.
- **CORS Configured**: Readily accepts requests from the frontend application out-of-the-box.

## Tech Stack

- **Python 3.x**
- **FastAPI**: Core API framework
- **SQLAlchemy**: ORM for database modeling and interactions
- **Auth0**: Identity provider
- **Google Generative AI (Gemini)**: For OCR and data extraction
- **Uvicorn**: ASGI web server

## Project Structure

```
.
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── config.py        # Environment variables and configuration (Pydantic Settings)
│   ├── database.py      # SQLAlchemy engine and session management
│   ├── models.py        # Database schema definitions
│   ├── schemas.py       # Pydantic models for request/response validation
│   ├── auth.py          # Auth0 token verification and user context
│   ├── routers/         # API Route definitions (auth, expenses, ocr)
│   └── services/        # Third-party integrations (e.g., Gemini OCR)
├── .env.example         # Example environment variables
├── requirements.txt     # Python dependencies
├── run.py               # Local development server runner
└── seed_user.py         # Utility script to seed the database with mock users and expenses
```

## Getting Started (Local Development)

### 1. Clone & Setup Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory. You can use `.env.example` as a template:

```ini
# Database configuration
DATABASE_URL=sqlite:///./finch_local.db

# Auth0 configurations
AUTH0_DOMAIN=your_auth0_domain
AUTH0_AUDIENCE=your_auth0_audience
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret

# Google Gemini API key for OCR
GEMINI_API_KEY=your_gemini_api_key

# CORS allowed origins
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

### 3. Run the Development Server

You can run the server using the provided runner script:

```bash
python run.py
```

Alternatively, run with Uvicorn directly:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive API documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

### 4. Database Seeding

To quickly populate the local database with a test user (`testuser@mail.com`) and demo expense records, run:

```bash
python seed_user.py
```

## Deployment

This backend is designed to be deployed to platforms like **Render**.

When deploying, ensure you have set all required environment variables, notably:
- `DATABASE_URL` (pointing to your production database, e.g., Supabase)
- `AUTH0_CLIENT_ID` & `AUTH0_CLIENT_SECRET`
- `AUTH0_DOMAIN` & `AUTH0_AUDIENCE`
- `GEMINI_API_KEY`
- `ALLOWED_ORIGINS` (pointing to your live frontend URL)

The start command for production deployment typically looks like:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
