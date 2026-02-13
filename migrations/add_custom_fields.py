"""
Migration script to add custom_fields column to compliance_records table.

This migration adds support for SESCINC-specific custom fields stored as JSON.

Run this script with:
    python migrations/add_custom_fields.py
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
    """Run the migration to add custom_fields column."""
    print("=" * 60)
    print("Migration: Add custom_fields to compliance_records")
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
    
    table_name = "compliance_records"
    column_name = "custom_fields"
    
    # Check if column already exists
    if column_exists(table_name, column_name):
        print(f"✅ Column '{column_name}' already exists in '{table_name}' table.")
        print("   No migration needed.")
        return True
    
    print(f"📋 Adding column '{column_name}' to '{table_name}' table...")
    
    try:
        with engine.connect() as conn:
            # SQLite doesn't support ALTER TABLE ADD COLUMN with DEFAULT in all versions
            # So we'll add it as nullable TEXT (which is fine for JSON strings)
            if "sqlite" in DATABASE_URL:
                # SQLite syntax
                sql = text(f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN {column_name} TEXT
                """)
            else:
                # PostgreSQL/MySQL syntax
                sql = text(f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN {column_name} TEXT NULL
                """)
            
            conn.execute(sql)
            conn.commit()
            
            print(f"✅ Successfully added column '{column_name}' to '{table_name}' table.")
            print("\n📝 Migration completed successfully!")
            print("\n   The custom_fields column will store JSON strings with SESCINC-specific data:")
            print("   - fire_category (CAT 1-9)")
            print("   - response_time_minutes")
            print("   - team composition (BA-CE, BA-LR, BA-MC, BA-RE)")
            print("   - CCI specifications")
            print("   - Extinguisher quantities")
            print("   - Certification counts")
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        print("\n   If the error persists, you may need to:")
        print("   1. Backup your database")
        print("   2. Recreate the database (if in development)")
        print("   3. Or manually add the column using your database client")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
