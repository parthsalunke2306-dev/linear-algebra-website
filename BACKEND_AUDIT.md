# Backend Audit Report

## Framework
- **Framework**: Django 6.0.7 (Python 3.12 / 3.14 compatible)
- **Application Structure**: `math_ds_project` (core config) + `linear_algebra` (app)

## Mathematical Engine
- **Symbolic Math**: SymPy 1.14.0 (for exact fractions, limits, roots, eigenvalues)
- **Numerical Library**: NumPy 2.5.1 (for arrays, dot/cross products, norms)
- **Geometry & Graphics**: Plotly 5.20.0 (Argand diagrams, function curves, bipartite graphs)

## Database
- **Current**: SQLite3 (`db.sqlite3` locally, `/tmp/db.sqlite3` on serverless Vercel)
- **Target**: PostgreSQL with Supabase connection pooling for production

## Authentication & Security
- **Current**: Supabase Auth client (`linear_algebra/supabase_client.py`) with fallback demo session tokens.
- **Session Backend**: `django.contrib.sessions.backends.signed_cookies` (Serverless compatible).

## PDF & Document Generation
- **PDF**: `xhtml2pdf` (with Base64 MathML/LaTeX math rendering)
- **Images**: `Pillow` (avatar thumbnail cropping)

## API Architecture
- **Current**: Direct Django Form POST views returning rendered HTML templates.
- **Target**: Clean JSON REST API layer rooted at `/api/v1/` allowing decoupled frontend interaction.

## Security Audit Checklist
- [x] **SECRET_KEY**: Uses fallback string in development; refactored to read from `.env` via `python-dotenv`.
- [x] **DEBUG**: Environment variable dependent (`DEBUG=True` local, `DEBUG=False` prod).
- [x] **ALLOWED_HOSTS**: Set to `['*']` currently; should restrict to exact domains in production `.env`.
- [x] **Database Credentials**: SQLite local, PostgreSQL ready via `DATABASE_URL`.
- [x] **CSRF / Session Security**: CSRF middleware active, signed cookie session storage.
- [x] **Email Whitelist**: Active domain/email restrictions implemented in `is_email_authorized()`.

## Code & Architecture Issues Identified
- [x] **Calculations inside Views**: Previously, some views directly handled mathematical parsing and formatting.
- [x] **Need for Pure Math Engine**: All mathematics extracted into standalone functions completely decoupled from Django `HttpRequest` / `HttpResponse`.
- [x] **Inconsistent Responses**: Transitioning all solvers to a standardized response contract (`success`, `solver`, `result`, `latex`, `steps`, `error`).
- [x] **Validation**: Need dedicated matrix validation prior to executing compute-heavy SymPy routines.
