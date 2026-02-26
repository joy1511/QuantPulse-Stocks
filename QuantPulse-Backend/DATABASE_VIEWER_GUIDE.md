# Database Viewer Guide 🔍

## Quick View - Command Line

### Option 1: Use the Inspector Script (Easiest)
```bash
cd QuantPulse-Backend
python inspect_db.py
```

This shows:
- All tables in the database
- Schema for each table (columns, types, constraints)
- Sample data from each table
- Indexes

### Option 2: Direct SQLite Commands
```bash
cd QuantPulse-Backend
sqlite3 quantpulse.db
```

Then run these commands:
```sql
-- List all tables
.tables

-- Show schema for users table
.schema users

-- View all users
SELECT * FROM users;

-- View specific columns
SELECT id, email, full_name, created_at FROM users;

-- Count users
SELECT COUNT(*) FROM users;

-- Exit
.quit
```

---

## GUI Tools (Visual Database Browsers)

### Option 1: DB Browser for SQLite (Recommended - Free)

**Download**: https://sqlitebrowser.org/dl/

**Features**:
- Visual table browser
- Execute SQL queries
- Edit data directly
- View schema visually
- Export data

**How to use**:
1. Download and install DB Browser for SQLite
2. Open the application
3. Click "Open Database"
4. Navigate to `QuantPulse-Backend/quantpulse.db`
5. Browse tables, run queries, view data

### Option 2: SQLite Viewer (VS Code Extension)

**Install**:
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "SQLite Viewer" or "SQLite"
4. Install "SQLite Viewer" by Florian Klampfer

**How to use**:
1. In VS Code, navigate to `QuantPulse-Backend/quantpulse.db`
2. Right-click the file
3. Select "Open Database"
4. Browse tables and data visually

### Option 3: DBeaver (Professional - Free Community Edition)

**Download**: https://dbeaver.io/download/

**Features**:
- Professional database tool
- Supports many databases
- ER diagrams
- SQL editor with autocomplete
- Data export/import

**How to use**:
1. Download and install DBeaver Community
2. Create new connection → SQLite
3. Browse to `QuantPulse-Backend/quantpulse.db`
4. Connect and explore

### Option 4: Online SQLite Viewer

**Website**: https://sqliteviewer.app/

**How to use**:
1. Go to https://sqliteviewer.app/
2. Click "Choose File"
3. Select `QuantPulse-Backend/quantpulse.db`
4. View tables and data in browser

⚠️ **Note**: Be careful with sensitive data when using online tools!

---

## Python Script to Query Database

Create a file `query_db.py`:

```python
import sqlite3
from tabulate import tabulate  # pip install tabulate

def query_users():
    conn = sqlite3.connect('quantpulse.db')
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("""
        SELECT 
            id,
            email,
            full_name,
            is_active,
            is_verified,
            created_at,
            last_login
        FROM users
        ORDER BY created_at DESC
    """)
    
    users = cursor.fetchall()
    headers = ['ID', 'Email', 'Full Name', 'Active', 'Verified', 'Created', 'Last Login']
    
    print("\n=== ALL USERS ===")
    print(tabulate(users, headers=headers, tablefmt='grid'))
    print(f"\nTotal Users: {len(users)}")
    
    conn.close()

if __name__ == "__main__":
    query_users()
```

Run it:
```bash
cd QuantPulse-Backend
pip install tabulate
python query_db.py
```

---

## Useful SQL Queries

### View All Users
```sql
SELECT id, email, full_name, is_active, created_at 
FROM users 
ORDER BY created_at DESC;
```

### Count Active Users
```sql
SELECT COUNT(*) as active_users 
FROM users 
WHERE is_active = 1;
```

### Find User by Email
```sql
SELECT * FROM users 
WHERE email = 'test@example.com';
```

### Recent Logins
```sql
SELECT email, full_name, last_login 
FROM users 
WHERE last_login IS NOT NULL 
ORDER BY last_login DESC 
LIMIT 10;
```

### Users Created Today
```sql
SELECT email, full_name, created_at 
FROM users 
WHERE DATE(created_at) = DATE('now');
```

---

## Current Database Schema

### Users Table

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INTEGER | NO | Primary key (auto-increment) |
| `email` | VARCHAR(255) | NO | User email (unique, indexed) |
| `hashed_password` | VARCHAR(255) | NO | Bcrypt hashed password |
| `full_name` | VARCHAR(255) | YES | User's full name |
| `is_active` | BOOLEAN | YES | Account active status |
| `is_verified` | BOOLEAN | YES | Email verified status |
| `is_admin` | BOOLEAN | YES | Admin privileges |
| `preferences` | TEXT | YES | JSON preferences |
| `created_at` | DATETIME | YES | Account creation timestamp |
| `updated_at` | DATETIME | YES | Last update timestamp |
| `last_login` | DATETIME | YES | Last login timestamp |

**Indexes**:
- `ix_users_id` - Primary key index
- `ix_users_email` - Email lookup index (for fast login queries)

---

## Sample Data View

Current database contains:

```
ID: 1
Email: test@example.com
Full Name: Test User
Active: Yes
Verified: No
Admin: No
Created: 2026-02-17 06:08:41
Last Login: 2026-02-17 06:11:31
```

---

## Tips

1. **Backup Before Editing**: Always backup `quantpulse.db` before making manual changes
2. **Use Transactions**: When editing data, use transactions to prevent corruption
3. **Don't Edit Passwords**: Never manually edit `hashed_password` - use the API
4. **Check Indexes**: The email index makes login queries fast
5. **Monitor Size**: SQLite is great for development, but consider PostgreSQL for production

---

## Troubleshooting

### Can't Open Database
- Make sure the server is not running (it locks the file)
- Check file permissions
- Verify the file exists: `dir quantpulse.db`

### Database Locked Error
- Stop the FastAPI server first
- Close any other tools accessing the database

### Want to Reset Database
```bash
# Backup first
copy quantpulse.db quantpulse.db.backup

# Delete database
del quantpulse.db

# Restart server - it will create a new database
python run.py
```

---

## Next Steps

1. ✅ View database schema - Use `python inspect_db.py`
2. ✅ Install DB Browser for SQLite - Visual exploration
3. 🔄 Add more tables as needed (portfolios, watchlists, etc.)
4. 🔄 Set up database migrations with Alembic
5. 🔄 Add database backups for production

---

**Your database is working perfectly! Use any of these tools to explore it.** 🎉
