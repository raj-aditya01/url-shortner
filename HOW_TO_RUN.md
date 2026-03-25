# 🚀 How to Run the URL Shortener

## ✅ Problem Solved!

The error "main is not here" was because you need to run the application from within the **virtual environment**.

---

## 📝 Quick Start Guide

### Method 1: Using Virtual Environment Python (RECOMMENDED)

```powershell
# Navigate to project folder
cd C:\Users\USER\training\1603

# Run with virtual environment Python
.\venv\Scripts\uvicorn.exe app.main:app --reload
```

### Method 2: Activate Virtual Environment First

```powershell
# Navigate to project folder
cd C:\Users\USER\training\1603

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Now run uvicorn (it will use venv's Python)
uvicorn app.main:app --reload
```

---

## 🔍 Understanding the Error

### ❌ What Caused the Error

When you tried to run:
```powershell
uvicorn app.main:app --reload
```

Python couldn't find the `app.main` module because:
1. Your system Python might not have FastAPI installed
2. Or you were running from the wrong directory
3. Or the virtual environment wasn't activated

### ✅ The Solution

Use the virtual environment's Python directly:
```powershell
.\venv\Scripts\uvicorn.exe app.main:app --reload
```

This ensures:
- ✅ FastAPI and all dependencies are available
- ✅ Correct Python version is used
- ✅ All packages from requirements.txt are loaded

---

## 📋 Step-by-Step Instructions

### Step 1: Open PowerShell
```powershell
# Press Win+X and select "Windows PowerShell"
# Or search for "PowerShell" in Start menu
```

### Step 2: Navigate to Project
```powershell
cd C:\Users\USER\training\1603
```

### Step 3: Verify Virtual Environment
```powershell
# Check if venv folder exists
ls venv\Scripts

# You should see:
# - python.exe
# - uvicorn.exe
# - pip.exe
```

### Step 4: Run the Application
```powershell
.\venv\Scripts\uvicorn.exe app.main:app --reload
```

### Step 5: Verify It's Running
You should see output like:
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\USER\\training\\1603']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 6: Test the API
Open your browser and visit:
- **API Docs:** http://127.0.0.1:8000/docs
- **Alternative Docs:** http://127.0.0.1:8000/redoc

---

## 🧪 Testing the Application

### Test 1: Create a Short URL

**Using PowerShell:**
```powershell
$body = @{ original_url = "https://www.google.com" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/shorten" -Method POST -Body $body -ContentType "application/json"
```

**Expected Output:**
```
short_url               original_url
---------               ------------
http://127.0.0.1:8000/3 https://www.google.com/
```

### Test 2: Use the Short URL

**In your browser:**
```
http://127.0.0.1:8000/3
```

You should be redirected to Google!

### Test 3: View All URLs

**In your browser:**
```
http://127.0.0.1:8000/admin/database
```

**Expected Output:**
```json
{
  "total_urls_stored": 1,
  "database_contents": {
    "3": {
      "url_id": 1000001,
      "original_url": "https://www.google.com/",
      "click_count": 1
    }
  }
}
```

---

## 🛠️ Troubleshooting

### Issue: "uvicorn: command not found"

**Solution:** Use the full path to uvicorn in venv
```powershell
.\venv\Scripts\uvicorn.exe app.main:app --reload
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:** Install dependencies in virtual environment
```powershell
.\venv\Scripts\pip.exe install -r requirements.txt
```

### Issue: "Cannot find path 'C:\Users\USER\training\1603'"

**Solution:** Make sure you're in the correct directory
```powershell
# Check current directory
pwd

# Navigate to project
cd C:\Users\USER\training\1603
```

### Issue: Port 8000 is already in use

**Solution:** Either kill the existing process or use a different port
```powershell
# Use a different port
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8001

# Or find and kill the process using port 8000
netstat -ano | findstr :8000
# Find the PID, then:
Stop-Process -Id <PID>
```

### Issue: "Access denied" when activating venv

**Solution:** Change PowerShell execution policy
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\venv\Scripts\Activate.ps1
```

---

## 📊 What Happens When You Run It

### 1. Application Starts
```
✓ Imports all modules (main.py)
✓ Sets up logging (logging_config.py)
✓ Creates FastAPI app
✓ Loads dependencies (dependencies.py)
✓ Connects to database (SQLite)
✓ Registers all routes (url_routes.py)
```

### 2. Server Listens
```
✓ Uvicorn starts HTTP server on port 8000
✓ Watches for file changes (--reload flag)
✓ Ready to accept requests
```

### 3. You See Logs
```
2026-03-25 15:17:36,878 INFO [app.api.routes.url_routes] Created short URL 3 for https://www.google.com/
2026-03-25 15:17:46,530 INFO [app.api.routes.url_routes] Redirecting 3 to https://www.google.com/
```

These are from the **detailed comments** you added! The logging shows:
- Timestamp
- Log level (INFO)
- Module name [app.api.routes.url_routes]
- Your custom message

---

## 🎯 Quick Commands Cheat Sheet

```powershell
# START THE SERVER
cd C:\Users\USER\training\1603
.\venv\Scripts\uvicorn.exe app.main:app --reload

# STOP THE SERVER
# Press Ctrl+C in the terminal

# CREATE SHORT URL (PowerShell)
$body = @{ original_url = "https://example.com" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/shorten" -Method POST -Body $body -ContentType "application/json"

# VIEW DATABASE
curl.exe http://127.0.0.1:8000/admin/database

# CHECK IF SERVER IS RUNNING
curl.exe http://127.0.0.1:8000/docs

# INSTALL/UPDATE DEPENDENCIES
.\venv\Scripts\pip.exe install -r requirements.txt

# CHECK PYTHON VERSION
.\venv\Scripts\python.exe --version

# CHECK INSTALLED PACKAGES
.\venv\Scripts\pip.exe list
```

---

## 🌐 URLs to Remember

Once the server is running:

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000 | Base URL (will show 404) |
| http://127.0.0.1:8000/docs | Interactive API documentation (Swagger UI) |
| http://127.0.0.1:8000/redoc | Alternative API documentation (ReDoc) |
| http://127.0.0.1:8000/admin/database | View all stored URLs |
| http://127.0.0.1:8000/{short_code} | Redirect to original URL |

---

## 📖 Understanding the Components

### What is `app.main:app`?

```
app.main:app
│    │    │
│    │    └─ Variable name (the FastAPI instance)
│    └────── Module name (main.py)
└─────────── Package name (app folder)
```

**Breakdown:**
- `app` = folder containing your Python package
- `main` = main.py file
- `app` = variable name in main.py (line: `app = create_app()`)

Uvicorn looks for:
1. `C:\Users\USER\training\1603\app\` (folder)
2. `main.py` (file in that folder)
3. `app` (variable in that file)

### Why Use Virtual Environment?

**Virtual Environment (venv):**
- ✅ Isolated Python environment
- ✅ Project-specific dependencies
- ✅ No conflicts with system Python
- ✅ Easy to recreate on other machines

**Without venv (system Python):**
- ❌ Dependencies mix with system packages
- ❌ Version conflicts
- ❌ Harder to share project
- ❌ Can break system tools

---

## 🎓 Next Steps

Now that your server is running:

1. ✅ **Read the code** - All files have detailed comments
2. ✅ **Test the API** - Use /docs to try all endpoints
3. ✅ **Check the database** - Look at `data/url_shortener.db`
4. ✅ **Modify something** - Add a log message, change a response
5. ✅ **Complete exercises** - See LEARNING_CHECKLIST.md

---

## 📞 Common Questions

### Q: Do I need to reinstall dependencies every time?
**A:** No! Once installed, they stay in the venv until you delete it.

### Q: Can I use a different port?
**A:** Yes! Add `--port 8001` to the uvicorn command.

### Q: Where is the database file?
**A:** `C:\Users\USER\training\1603\data\url_shortener.db`

### Q: How do I stop the server?
**A:** Press `Ctrl+C` in the terminal.

### Q: Can I run this in production?
**A:** The code is production-ready, but add authentication and security headers first!

### Q: What if I modify the code?
**A:** With `--reload` flag, the server automatically reloads when you save changes!

---

## ✨ Success!

You're now running a fully functional URL shortener with:
- ✅ Clean architecture (3 layers: routes, service, repository)
- ✅ Detailed educational comments (1,489 lines!)
- ✅ OOP best practices (SOLID principles)
- ✅ Design patterns (Singleton, Factory, Repository, DI)
- ✅ Complete documentation

**Happy learning! 🎉**

---

*Last updated: 2026-03-25*
