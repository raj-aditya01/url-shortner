# URL Shortener API

A FastAPI-based service that converts long URLs into short, shareable codes. Built with clean architecture principles and fully documented code.

---

## 📋 Quick Start

### 1. Set Up Virtual Environment

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
.\venv\Scripts\activate.bat
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at: **http://127.0.0.1:8000**

---

## 🏗️ Architecture Overview

### How It Works

1. **User sends a long URL** → `POST /shorten`
2. **API receives and validates** → Uses Pydantic models
3. **Service creates short code** → Uses Base62 encoding
4. **Database stores mapping** → SQLite database
5. **User gets short URL** → `http://127.0.0.1:8000/abc123`
6. **User visits short URL** → `GET /abc123`
7. **API redirects to original** → Returns the long URL

### Project Structure

```
app/
├── main.py                    # App entry point and setup
├── dependencies.py            # Singleton instances (database, service)
│
├── api/
│   └── routes/
│       └── url_routes.py      # HTTP endpoints (POST, GET)
│
├── services/
│   ├── url_service.py         # Business logic (create, resolve URLs)
│   └── base62_encoder.py      # Converts IDs to short codes
│
├── repositories/
│   └── url_repository.py      # Database operations (save, retrieve)
│
├── models/
│   └── schemas.py             # Request/response data models
│
└── core/
    └── logging_config.py      # Logging setup

data/
└── url_shortener.db           # SQLite database (created automatically)
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP Client / Browser                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │   FastAPI Application (Port 8000)    │
         │        app/main.py                    │
         └─────────────┬─────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │   API Routes & Endpoints              │
        │   api/routes/url_routes.py            │
        │                                        │
        │  POST   /shorten       - Create       │
        │  GET    /{short_hash}  - Redirect     │
        │  GET    /admin/database - View all    │
        └────────────┬──────────────────────────┘
                     │
                     ▼
      ┌──────────────────────────────────────┐
      │   Dependency Injection               │
      │   dependencies.py                    │
      │                                      │
      │  Provides:                           │
      │  - Database connection               │
      │  - URL Shortener Service             │
      └────────┬─────────────────┬───────────┘
               │                 │
       ┌───────▼──────────┐  ┌───▼──────────────────────┐
       │  Repository      │  │  Service / Business      │
       │                  │  │                          │
       │ url_repository   │  │  url_service.py          │
       │ .py              │  │                          │
       │                  │  │  - create_short_code()   │
       │ - SQLite DB      │  │  - resolve_url()         │
       │ - Mock (test)    │  │  - track_click()         │
       └───────┬──────────┘  └───┬──────────┬───────────┘
               │                  │          │
               │                  ▼          │
               │            ┌────────────────┴─┐
               │            │                  │
               │            │ base62_encoder   │
               │            │ .py              │
               │            │                  │
               │            │ Converts IDs     │
               │            │ to short codes   │
               │            └──────────────────┘
               │
               ▼
       ┌──────────────────────┐
       │  SQLite Database     │
       │  data/               │
       │  url_shortener.db    │
       │                      │
       │  Table:              │
       │  url_mappings        │
       │  - id                │
       │  - original_url      │
       │  - short_hash        │
       │  - click_count       │
       └──────────────────────┘
```

---

## 📡 API Endpoints

### 1️⃣ Create Short URL

**Endpoint:** `POST /shorten`

**Request:**
```json
{
  "original_url": "https://www.example.com/very/long/url/path"
}
```

**Response:**
```json
{
  "short_url": "http://127.0.0.1:8000/abc123",
  "original_url": "https://www.example.com/very/long/url/path"
}
```

---

### 2️⃣ Redirect to Original URL

**Endpoint:** `GET /{short_hash}`

**What happens:**
- Browser visits: `http://127.0.0.1:8000/abc123`
- API finds the original URL
- Browser is redirected to: `https://www.example.com/very/long/url/path`
- Click is recorded in the background

**Response:** HTTP 302 Redirect

---

### 3️⃣ View All Stored URLs (Admin)

**Endpoint:** `GET /admin/database`

**Response:**
```json
{
  "total_urls_stored": 5,
  "database_contents": {
    "abc123": {
      "url_id": 1000001,
      "original_url": "https://example.com/path1",
      "click_count": 3
    },
    "def456": {
      "url_id": 1000002,
      "original_url": "https://example.com/path2",
      "click_count": 1
    }
  }
}
```

---

## 📚 Code Layers Explained

### 1. **API Routes** (`api/routes/url_routes.py`)
- Receives HTTP requests from clients
- Validates input using Pydantic models
- Calls the service layer for business logic
- Returns HTTP responses

### 2. **Service Layer** (`services/url_service.py`)
- Contains the business logic
- Creates short codes, resolves URLs, tracks clicks
- Never directly handles HTTP or database SQL
- Easy to test and reuse

### 3. **Repository Layer** (`repositories/url_repository.py`)
- Handles all database operations
- Can use SQLite, MongoDB, PostgreSQL, etc.
- Service doesn't need to know which database is used
- Uses the Repository interface pattern

### 4. **Utilities** (`services/base62_encoder.py`)
- Helper class for encoding IDs to short codes
- Converts numbers to Base62 format (0-9, a-z, A-Z)
- Example: `1000001` → `abc123`

### 5. **Models** (`models/schemas.py`)
- Define request and response data structures
- Pydantic automatically validates input
- Documents what data the API accepts/returns

### 6. **Dependency Injection** (`dependencies.py`)
- Creates single instances of service and database
- Ensures they're reused across all requests
- FastAPI automatically provides these to route functions

---

## 🗄️ Database

### Location
```
C:\Users\USER\training\1603\data\url_shortener.db
```

### Override Database Path
```bash
# Set environment variable before running
$env:SQLITE_DB_PATH = "C:\custom\path\urls.db"
uvicorn app.main:app --reload
```

### Database Schema
```sql
CREATE TABLE url_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_url TEXT NOT NULL,
    short_hash TEXT UNIQUE,
    click_count INTEGER NOT NULL DEFAULT 0
)
```

| Column | Purpose |
|--------|---------|
| `id` | Unique numeric ID (encoded to short code) |
| `original_url` | The full URL user wants to shorten |
| `short_hash` | The short code (e.g., 'abc123') |
| `click_count` | How many times this URL was accessed |

---

## 📖 How the Code Connects

### Example: Creating a Short URL

```
1. Browser sends: POST /shorten {"original_url": "https://example.com/long"}
   
2. url_routes.py receives it
   - Validates using URLCreateRequest model
   
3. Calls service.create_short_code("https://example.com/long")
   
4. url_service.py processes it:
   - repository.save_and_get_id() → Database returns ID: 1000001
   - Base62Encoder.encode(1000001) → Returns "abc123"
   - repository.update_short_hash(1000001, "abc123", url)
   
5. Database stores the mapping
   
6. Returns to url_routes.py
   
7. Creates response: {"short_url": "http://127.0.0.1:8000/abc123", ...}
   
8. Browser receives the response
```

### Example: Using a Short URL

```
1. Browser visits: http://127.0.0.1:8000/abc123

2. url_routes.py receives it
   - Calls service.resolve_url("abc123")

3. url_service.py processes it:
   - repository.get_original_url("abc123") → Finds "https://example.com/long"
   - Returns the original URL

4. url_routes.py redirects to it
   - Tracks click in background (doesn't slow down redirect)

5. Browser is redirected to https://example.com/long
```

---

## 🧪 Testing

### Test Endpoints with curl

```bash
# Create a short URL
curl -X POST http://127.0.0.1:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.google.com"}'

# Visit a short URL (will redirect)
curl -L http://127.0.0.1:8000/abc123

# View all URLs
curl http://127.0.0.1:8000/admin/database
```

### Interactive API Docs
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## 🔑 Key Concepts

| Concept | What It Means | Why We Use It |
|---------|---------------|---------------|
| **Dependency Injection** | Pass objects into functions instead of creating them | Easy to test, easy to swap implementations |
| **Repository Pattern** | Hide database details behind an interface | Can change database without changing service code |
| **Layered Architecture** | Separate HTTP handling, business logic, and database | Each part is focused and testable |
| **Base62 Encoding** | Convert numbers to short letters/numbers | Makes IDs much shorter and URL-friendly |
| **Locks/Threading** | Ensure multiple requests don't corrupt data | Safe concurrent access to shared data |

---

## ⚙️ Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `SQLITE_DB_PATH` | Path to database file | `data/url_shortener.db` |
| `BASE_URL` | Base URL for short links | `http://127.0.0.1:8000` |

---

## 📝 File Comments Guide

All files now have **simple, clear comments** that explain:
- **What** the class/function does
- **Why** it's needed
- **How** to use it
- **Examples** where helpful

Comments avoid complex terminology and are easy to understand.

---

## 🎯 Next Steps

1. **Explore the API** → Visit http://127.0.0.1:8000/docs
2. **Create short URLs** → Send `POST /shorten` requests
3. **Test a short URL** → Visit a short link in your browser
4. **View all URLs** → Check `/admin/database`
5. **Read the code** → Each file has clear comments explaining everything

---

## 📄 License

This is a training project for learning FastAPI and clean code architecture.
