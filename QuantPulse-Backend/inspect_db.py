"""
Database Inspector - View schema and data in quantpulse.db
"""
import sqlite3
from datetime import datetime

def inspect_database():
    conn = sqlite3.connect('quantpulse.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("DATABASE INSPECTION - quantpulse.db")
    print("=" * 80)
    print()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("📋 TABLES IN DATABASE:")
    print("-" * 80)
    for table in tables:
        print(f"  • {table[0]}")
    print()
    
    # Inspect each table
    for table in tables:
        table_name = table[0]
        print("=" * 80)
        print(f"TABLE: {table_name}")
        print("=" * 80)
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("\n📊 SCHEMA:")
        print("-" * 80)
        print(f"{'Column':<20} {'Type':<15} {'Nullable':<10} {'Default':<15} {'PK'}")
        print("-" * 80)
        for col in columns:
            col_id, name, col_type, not_null, default_val, pk = col
            nullable = "NO" if not_null else "YES"
            default = str(default_val) if default_val else "-"
            is_pk = "✓" if pk else ""
            print(f"{name:<20} {col_type:<15} {nullable:<10} {default:<15} {is_pk}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        print(f"\n📈 TOTAL ROWS: {count}")
        
        # Show sample data
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            
            print("\n📝 SAMPLE DATA (First 5 rows):")
            print("-" * 80)
            
            # Print column headers
            col_names = [col[1] for col in columns]
            header = " | ".join([f"{name:<15}" for name in col_names])
            print(header)
            print("-" * 80)
            
            # Print rows
            for row in rows:
                row_str = " | ".join([f"{str(val):<15}" for val in row])
                print(row_str)
        
        print()
    
    # Show indexes
    print("=" * 80)
    print("INDEXES")
    print("=" * 80)
    cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index'")
    indexes = cursor.fetchall()
    if indexes:
        for idx in indexes:
            print(f"  • {idx[0]} on table {idx[1]}")
    else:
        print("  No indexes found")
    
    print()
    conn.close()

if __name__ == "__main__":
    inspect_database()
