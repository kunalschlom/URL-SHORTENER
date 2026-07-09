# URL Shortener MVP

A lightweight, production-grade URL shortener application built with FastAPI, React, TypeScript, and PostgreSQL.

## Architecture

The project follows a clean layered architecture separating concerns at every level:

1. **API Layer**: FastAPI endpoints handling requests, validating schema parameters, and returning responses.
2. **Service Layer**: Core business logic coordinator including collision resolution and short code generation.
3. **Repository Layer**: Data access layer managing database operations on SQLAlchemy models.
4. **Models Layer**: SQLAlchemy database declarations.
5. **Schemas Layer**: Pydantic models defining input and output validation.

```
┌──────────────────────────────────────────────┐
│                  React App                   │
└──────────────────────┬───────────────────────┘
                       │ HTTP Requests
┌──────────────────────▼───────────────────────┐
│              FastAPI API Router              │
└──────────────────────┬───────────────────────┘
                       │ Calls
┌──────────────────────▼───────────────────────┐
│                 URL Service                  │
└──────────────────────┬───────────────────────┘
                       │ Database Actions
┌──────────────────────▼───────────────────────┐
│                URL Repository                │
└──────────────────────┬───────────────────────┘
                       │ Executes
┌──────────────────────▼───────────────────────┐
│               PostgreSQL / DB                │
└──────────────────────────────────────────────┘
```

## Folder Structure

```
.
├── backend/
│   ├── alembic/            
│   │   └── versions/       
│   ├── app/                
│   │   ├── api/            
│   │   ├── core/           
│   │   ├── models/         
│   │   ├── repositories/   
│   │   ├── schemas/        
│   │   ├── services/       
│   │   └── main.py         
│   ├── tests/              
│   ├── alembic.ini         
│   ├── Dockerfile          
│   ├── pytest.ini          
│   └── requirements.txt    
├── frontend/
│   ├── src/                
│   │   ├── components/     
│   │   ├── App.tsx         
│   │   └── main.tsx        
│   ├── Dockerfile          
│   └── package.json        
├── docker-compose.yml      
└── README.md               
```

## Database Schema

### `urls` Table

| Field Name | Type | Constraints |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key |
| `original_url` | `VARCHAR(2048)` | Not Null |
| `short_code` | `VARCHAR(20)` | Unique, Indexed, Not Null |
| `created_at` | `TIMESTAMP` | Default: `now()`, Not Null |
| `click_count` | `INTEGER` | Default: `0`, Not Null |

## API Documentation

### Endpoints

| Method | Path | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/shorten` | Shorten a new destination URL | `201 Created` |
| `GET` | `/api/v1/urls` | Retrieve all shortened URLs | `200 OK` |
| `DELETE` | `/api/v1/urls/{id}` | Delete a shortened URL by its ID | `204 No Content` |
| `GET` | `/health` | Application status health check | `200 OK` |
| `GET` | `/{short_code}` | Redirect to the original URL | `307 Temporary Redirect` |

## How to Run

### Docker Compose

Run the entire stack with a single command:

```bash
docker compose up --build
```

Access the application:
* Frontend: `http://localhost:5173`
* Backend API: `http://localhost:8000`
* Interactive API Documentation (Swagger): `http://localhost:8000/docs`

### Running Locally

#### Backend

1. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

2. Run migrations:
```bash
alembic upgrade head
```

3. Start server:
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

## Future Improvements

* User Authentication & Authorization.
* Redis integration for caching redirection lookups.
* Link expiration date configuration.
* QR code generation for shortened links.
* Advanced redirection analytics dashboard.
* Rate limiting per IP.
