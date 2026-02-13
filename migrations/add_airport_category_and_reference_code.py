"""
Migration script to add category and reference_code columns to airports table.

This migration adds:
- category: ANAC airport category (1C-9C) based on annual passenger volume
- reference_code: Airport reference code (e.g., 3C)

Run this script with:
    python migrations/add_airport_category_and_reference_code.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.database import engine, DATABASE_URL

def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def run_migration():
    """Run the migration to add category and reference_code columns."""
    print("=" * 60)
    print("Migration: Add category and reference_code to airports")
    print("=" * 60)
    
    # Check if using SQLite
    if "sqlite" not in DATABASE_URL:
        print(f"⚠️  Warning: This migration is designed for SQLite.")
        print(f"   Current database: {DATABASE_URL}")
        print(f"   You may need to adjust the SQL syntax for your database.")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("❌ Migration cancelled.")
            return False
    
    table_name = "airports"
    
    # Check if columns already exist
    category_exists = column_exists(table_name, "category")
    reference_code_exists = column_exists(table_name, "reference_code")
    
    if category_exists and reference_code_exists:
        print(f"✅ Columns 'category' and 'reference_code' already exist in '{table_name}' table.")
        print("   No migration needed.")
        return True
    
    try:
        with engine.connect() as conn:
            # Add category column
            if not category_exists:
                print(f"📋 Adding column 'category' to '{table_name}' table...")
                if "sqlite" in DATABASE_URL:
                    sql = text(f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN category TEXT
                    """)
                else:
                    sql = text(f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN category VARCHAR(10) NULL
                    """)
                conn.execute(sql)
                conn.commit()
                print(f"✅ Successfully added column 'category'.")
            else:
                print(f"⏭️  Column 'category' already exists, skipping...")
            
            # Add reference_code column
            if not reference_code_exists:
                print(f"📋 Adding column 'reference_code' to '{table_name}' table...")
                if "sqlite" in DATABASE_URL:
                    sql = text(f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN reference_code TEXT
                    """)
                else:
                    sql = text(f"""
                        ALTER TABLE {table_name}
                        ADD COLUMN reference_code VARCHAR(10) NULL
                    """)
                conn.execute(sql)
                conn.commit()
                print(f"✅ Successfully added column 'reference_code'.")
            else:
                print(f"⏭️  Column 'reference_code' already exists, skipping...")
            
            print("\n📝 Migration completed successfully!")
            print("\n   The new columns will store:")
            print("   - category: ANAC airport category (1C-9C) based on annual passenger volume")
            print("   - reference_code: Airport reference code (e.g., 3C, 4C, 5C)")
            print("\n   Note: The 'annual_passengers' column is kept for compatibility.")
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        print("\n   If the error persists, you may need to:")
        print("   1. Backup your database")
        print("   2. Recreate the database (if in development)")
        print("   3. Or manually add the columns using your database client")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
