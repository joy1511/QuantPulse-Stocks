"""
Simple Database Query Tool
Run: python query_db.py
"""
import sqlite3
from datetime import datetime

def format_datetime(dt_str):
    """Format datetime string for display"""
    if not dt_str:
        return "Never"
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str

def query_users():
    conn = sqlite3.connect('quantpulse.db')
    cursor = conn.cursor()
    
    print("\n" + "=" * 100)
    print("USER DATABASE QUERY")
    print("=" * 100)
    
    # Get all users
    cursor.execute("""
        SELECT 
            id,
            email,
            full_name,
            is_active,
            is_verified,
            is_admin,
            created_at,
            last_login
        FROM users
        ORDER BY created_at DESC
    """)
    
    users = cursor.fetchall()
    
    if not users:
        print("\n❌ No users found in database")
        conn.close()
        return
    
    print(f"\n📊 Total Users: {len(users)}")
    print("\n" + "-" * 100)
    
    for user in users:
        user_id, email, full_name, is_active, is_verified, is_admin, created_at, last_login = user
        
        print(f"\n👤 USER #{user_id}")
        print(f"   Email:        {email}")
        print(f"   Name:         {full_name or 'Not set'}")
        print(f"   Status:       {'✅ Active' if is_active else '❌ Inactive'}")
        print(f"   Verified:     {'✅ Yes' if is_verified else '❌ No'}")
        print(f"   Admin:        {'✅ Yes' if is_admin else '❌ No'}")
        print(f"   Created:      {format_datetime(created_at)}")
        print(f"   Last Login:   {format_datetime(last_login)}")
        print("-" * 100)
    
    # Statistics
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    active_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_verified = 1")
    verified_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
    admin_count = cursor.fetchone()[0]
    
    print("\n📈 STATISTICS")
    print(f"   Active Users:    {active_count}")
    print(f"   Verified Users:  {verified_count}")
    print(f"   Admin Users:     {admin_count}")
    print(f"   Total Users:     {len(users)}")
    
    print("\n" + "=" * 100)
    
    conn.close()

def show_schema():
    conn = sqlite3.connect('quantpulse.db')
    cursor = conn.cursor()
    
    print("\n" + "=" * 100)
    print("DATABASE SCHEMA")
    print("=" * 100)
    
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    print("\n📋 USERS TABLE COLUMNS:")
    print("-" * 100)
    print(f"{'Column':<20} {'Type':<15} {'Nullable':<10} {'Primary Key':<12}")
    print("-" * 100)
    
    for col in columns:
        col_id, name, col_type, not_null, default_val, pk = col
        nullable = "NO" if not_null else "YES"
        is_pk = "✓" if pk else ""
        print(f"{name:<20} {col_type:<15} {nullable:<10} {is_pk:<12}")
    
    print("\n" + "=" * 100)
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "schema":
        show_schema()
    else:
        query_users()
        print("\n💡 Tip: Run 'python query_db.py schema' to see table structure")
        print()
