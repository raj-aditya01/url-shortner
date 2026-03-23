# Quick Reference: Code Connections

## 🎯 Which Files Work Together

### When You Create a Short URL

```
YOU: Post URL to /shorten endpoint
     ↓
→ app/api/routes/url_routes.py (create_short_url function)
  • Receives the request
  • Uses URLCreateRequest schema to validate
  
  ↓
→ app/dependencies.py (get_url_service)
  • Provides the service instance
  
  ↓
→ app/services/url_service.py (create_short_code method)
  • The business logic
  • Calls repository to save URL
  • Calls encoder to make short code
  
  ↓
→ app/repositories/url_repository.py (save_and_get_id & update_short_hash)
  • Does the database work
  • Creates ID
  • Stores mapping
  
  ↓
→ app/services/base62_encoder.py (encode method)
  • Converts numeric ID to short code
  • Example: 1000001 → "abc123"
  
  ↓
→ Database (data/url_shortener.db)
  • Data is saved here
  
  ↓
YOU: Receive back {"short_url": "...", "original_url": "..."}
```

---

## 🔄 When You Use a Short URL

```
YOU: Visit /abc123 in browser
     ↓
→ app/api/routes/url_routes.py (redirect_to_original function)
  • Receives the request
  • Calls service to find original URL
  
  ↓
→ app/services/url_service.py (resolve_url method)
  • Asks repository to find the URL
  
  ↓
→ app/repositories/url_repository.py (get_original_url)
  • Searches database for the short code
  • Returns the original URL
  
  ↓
→ YOU: Redirected to original URL (302 redirect)

BACKGROUND:
→ background_tasks (from FastAPI)
  • Calls service.track_click("abc123")
  
  ↓
→ app/services/url_service.py (track_click method)
  • Calls repository to increment counter
  
  ↓
→ app/repositories/url_repository.py (increment_click_count)
  • Updates database with new click count
```

---

## 📦 What Each File Does

### `app/main.py`
- **Purpose:** Starts the whole app
- **Creates:** FastAPI application
- **Uses:** logging_config.py, url_routes.py

### `app/dependencies.py`
- **Purpose:** Provides singleton instances
- **Creates:** The service and repository (only once)
- **Used By:** url_routes.py (to get service/database)

### `app/api/routes/url_routes.py`
- **Purpose:** HTTP endpoints
- **Has:** 3 endpoints (POST /shorten, GET /{hash}, GET /admin/database)
- **Uses:** dependencies.py, url_service.py, schemas.py, url_repository.py
- **Returns:** JSON responses or redirects

### `app/services/url_service.py`
- **Purpose:** Business logic (the "thinking" part)
- **Has:** 3 methods (create_short_code, resolve_url, track_click)
- **Uses:** url_repository.py, base62_encoder.py
- **Used By:** url_routes.py

### `app/repositories/url_repository.py`
- **Purpose:** Database operations (the "storage" part)
- **Has:** 3 implementations (interface, mock, SQLite)
- **Used By:** url_service.py, dependencies.py, url_routes.py

### `app/services/base62_encoder.py`
- **Purpose:** Utility for encoding numbers
- **Has:** 1 static method (encode)
- **Uses:** Nothing
- **Used By:** url_service.py

### `app/models/schemas.py`
- **Purpose:** Request/response data structure
- **Has:** 2 classes (URLCreateRequest, URLCreateResponse)
- **Used By:** url_routes.py (for validation)

### `app/core/logging_config.py`
- **Purpose:** Logging setup
- **Has:** 1 function (setup_logging)
- **Used By:** main.py

---

## 🔌 Dependency Flow

```
main.py
  ├─→ creates FastAPI app
  └─→ includes router from url_routes.py
       └─→ url_routes.py
            ├─→ imports from dependencies.py
            │    ├─→ creates url_repository (database)
            │    └─→ creates url_service (business logic)
            │         ├─→ needs url_repository
            │         └─→ needs base62_encoder
            ├─→ imports schemas for validation
            ├─→ imports url_service for endpoints
            └─→ imports url_repository (optional type hint)

core/logging_config.py
  └─→ called by main.py at startup
```

---

## 🎲 Data Types Passed Between Files

### Request comes in
```json
{
  "original_url": "https://example.com"
}
```
↓ Validated by `URLCreateRequest` (schemas.py)

### Service processes it
```python
url_id = 1000001  # From database
short_hash = "abc123"  # From encoder
```

### Response sent back
```json
{
  "short_url": "http://127.0.0.1:8000/abc123",
  "original_url": "https://example.com"
}
```
↓ Formatted by `URLCreateResponse` (schemas.py)

---

## ✅ How to Read the Code

1. **Start at** `app/main.py` - See how app starts
2. **Look at** `app/api/routes/url_routes.py` - See the endpoints
3. **Follow** `app/dependencies.py` - See what gets provided
4. **Read** `app/services/url_service.py` - Understand the logic
5. **Check** `app/repositories/url_repository.py` - See database work
6. **Notice** `app/services/base62_encoder.py` - Simple utility
7. **Review** `app/models/schemas.py` - Data structure
8. **Understand** `app/core/logging_config.py` - Setup stuff

---

## 🐛 If Something Breaks

| Problem | Look In | Check For |
|---------|----------|-----------|
| Endpoint not found | `url_routes.py` | Is route defined? |
| Wrong response format | `schemas.py` | Are fields correct? |
| Database error | `url_repository.py` | Is SQL correct? |
| Short code looks weird | `base62_encoder.py` | Is encoding working? |
| Service throws error | `url_service.py` | Are methods called right? |
| App won't start | `main.py` | Is FastAPI setup right? |
| Logging not showing | `logging_config.py` | Is it called in main.py? |
| Dependencies not injected | `dependencies.py` | Are singletons created? |

---

## 💡 Remember

- **Routes** handle HTTP (receiving requests, sending responses)
- **Services** handle business logic (the "thinking")
- **Repositories** handle databases (the "storage")
- **Models** validate data (the "structure")
- **Dependencies** provide instances (the "plumbing")
- **Encoder** converts data (the "utility")

Each file has a specific job. Keep them separate and the code stays clean! ✨
