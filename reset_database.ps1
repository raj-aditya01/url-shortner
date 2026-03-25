# ============================================================================
# RESET_DATABASE.PS1 - Reset the database to start fresh
# ============================================================================
# This script deletes the existing database and lets you start fresh
# with IDs starting at 1,000,000 (which gives nice Base62 codes)
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "   Reset Database" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

$dbPath = "data\url_shortener.db"

if (Test-Path $dbPath) {
    Write-Host "Found existing database: $dbPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Current database contents:" -ForegroundColor Cyan
    
    # Show current database contents
    $result = .\venv\Scripts\python.exe -c @"
import sqlite3
conn = sqlite3.connect('$dbPath')
cursor = conn.execute('SELECT id, short_hash, original_url FROM url_mappings')
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f'  ID: {row[0]:8} -> short_hash: {row[1]:10} -> {row[2][:50]}')
else:
    print('  (empty)')
print(f'Total URLs: {len(rows)}')
"@
    
    Write-Host $result
    Write-Host ""
    
    # Ask for confirmation
    $confirm = Read-Host "Do you want to DELETE this database and start fresh? (yes/no)"
    
    if ($confirm -eq "yes" -or $confirm -eq "y") {
        try {
            Remove-Item $dbPath -Force
            Write-Host ""
            Write-Host "✓ Database deleted successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next time you create a URL, IDs will start at 1,000,000" -ForegroundColor Green
            Write-Host "  - ID 1,000,001 -> Base62: 4c93" -ForegroundColor Cyan
            Write-Host "  - ID 1,000,002 -> Base62: 4c94" -ForegroundColor Cyan
            Write-Host "  - ID 1,000,003 -> Base62: 4c95" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Now run the server and create a new short URL!" -ForegroundColor Yellow
        } catch {
            Write-Host ""
            Write-Host "ERROR: Could not delete database: $_" -ForegroundColor Red
            Write-Host "Make sure the server is not running!" -ForegroundColor Yellow
        }
    } else {
        Write-Host ""
        Write-Host "Database reset cancelled." -ForegroundColor Yellow
    }
} else {
    Write-Host "No database found at: $dbPath" -ForegroundColor Yellow
    Write-Host "Database will be created automatically when you start the server." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "IDs will start at 1,000,000:" -ForegroundColor Green
    Write-Host "  - ID 1,000,001 -> Base62: 4c93" -ForegroundColor Cyan
    Write-Host "  - ID 1,000,002 -> Base62: 4c94" -ForegroundColor Cyan
    Write-Host "  - ID 1,000,003 -> Base62: 4c95" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Read-Host "Press Enter to exit"
