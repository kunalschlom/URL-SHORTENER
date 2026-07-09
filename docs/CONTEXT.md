# URL Shortener - MVP Specification

## Objective

Build a minimal but production-style URL Shortener using FastAPI.

This project should focus on clean architecture rather than features. The goal is to create a maintainable codebase that can easily be extended with authentication, analytics, Redis, rate limiting, and other advanced features later.

Only implement the minimum functionality required for a working URL shortener.

---

# Tech Stack

Backend
- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Alembic
- Pydantic
- Uvicorn

Frontend
- React
- TypeScript
- Vite

---

# Folder Structure

Use the following architecture.

backend/

app/

api/

models/

schemas/

services/

repositories/

core/

main.py

Frontend should remain inside the frontend folder.

Keep every layer independent.

---

# Layer Responsibilities

### API

Contains only FastAPI routes.

Routes should

- receive request
- validate input
- call service
- return response

No business logic.

No SQL queries.

---

### Services

Contains business logic.

Responsible for

- validating operations
- generating short codes
- handling collisions
- coordinating repositories

No HTTP code.

---

### Repository

Contains only database operations.

Responsible for

- create
- read
- delete
- update

No business logic.

---

### Models

SQLAlchemy ORM models.

---

### Schemas

Pydantic request and response models.

---

### Core

Application configuration.

Database session.

Settings.

Shared dependencies.

---

# MVP Features

The application only needs the following functionality.

## Create Short URL

Input

Long URL

Output

Generated short URL

---

## Redirect

Opening


/{short_code}

should redirect to the original URL.

---

## List URLs

Return every stored URL.

---

## Delete URL

Delete an existing URL by ID.

---

## Health Check

GET /health

Returns

{
    "status": "ok"
}

---

# Database

Create a single table.

urls

Fields

- id
- original_url
- short_code
- created_at
- click_count

Requirements

short_code must be unique.

click_count starts at zero.

created_at generated automatically.

---

# Short Code Generation

Generate random Base62 strings.

Length

6 characters.

If collision occurs,

generate another code.

Do not use hashing of the URL.

---

# API Endpoints

POST /api/v1/shorten

GET /{short_code}

GET /api/v1/urls

DELETE /api/v1/urls/{id}

GET /health

Document every endpoint using FastAPI's OpenAPI support.

---

# Frontend

Keep the UI simple.

Page contains

- Title
- URL input
- Shorten button
- Generated short URL
- Copy button
- Table showing created URLs
- Delete button

No authentication.

No dashboard.

No analytics.

---

# Coding Standards

- Use async endpoints where appropriate.
- Use dependency injection.
- Use type hints everywhere.
- Separate concerns properly.
- Avoid duplicate code.
- Keep functions small.
- Use descriptive names.
- Follow SOLID principles whenever practical.
- Write clean, readable code over clever code.

---

# Out of Scope

Do NOT implement

- Authentication
- Redis
- QR codes
- Analytics
- Custom aliases
- Expiration dates
- Rate limiting
- Background workers
- Docker optimizations
- Caching

Those will be added in later iterations.

---

# Deliverable

The result should be a working MVP with:

- Clean folder structure
- Production-style architecture
- Fully working backend
- Minimal React frontend
- PostgreSQL integration
- API documentation
- Readable, maintainable code

Prioritize correctness, readability, and extensibility over adding unnecessary features.