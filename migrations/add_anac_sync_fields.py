"""
Migration script to add ANAC synchronization fields to airports table.

This migration adds fields for:
- Tracking synchronization with ANAC data
- Storing additional ANAC-provided information (IATA code, coordinates, etc.)

Run this script with:
    python migrations/add_anac_sync_fields.py
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
    """Run the migration to add ANAC sync fields."""
    print("=" * 60)
    print("Migration: Add ANAC synchronization fields to airports")
    print("=" * 60)
    
    # Check if using SQLite
    if "sqlite" not in DATABASE_URL:
        print(f"⚠️  Warning: This migration is designed for SQLite.")
        print(f"   Current database: {DATABASE_URL}")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("❌ Migration cancelled.")
            return False
    
    table_name = "airports"
    
    # Fields to add
    fields = [
        ("data_sincronizacao_anac", "TEXT", "DateTime for last ANAC sync"),
        ("origem_dados", "TEXT DEFAULT 'manual'", "Data source: 'manual' or 'anac'"),
        ("versao_dados_anac", "TEXT", "ANAC dataset version"),
        ("codigo_iata", "TEXT", "IATA code (3 letters)"),
        ("latitude", "REAL", "Latitude coordinate"),
        ("longitude", "REAL", "Longitude coordinate"),
        ("cidade", "TEXT", "City name"),
        ("estado", "TEXT", "State (UF)"),
        ("status_operacional", "TEXT", "Operational status from ANAC"),
    ]
    
    try:
        with engine.connect() as conn:
            for field_name, field_type, description in fields:
                if column_exists(table_name, field_name):
                    print(f"⏭️  Column '{field_name}' already exists, skipping...")
                    continue
                
                print(f"📋 Adding column '{field_name}' ({description})...")
                sql = text(f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN {field_name} {field_type}
                """)
                conn.execute(sql)
                conn.commit()
                print(f"✅ Successfully added column '{field_name}'.")
            
            print("\n📝 Migration completed successfully!")
            print("\n   The new columns will store:")
            print("   - Synchronization metadata (timestamp, source, version)")
            print("   - Additional ANAC data (IATA code, coordinates, location)")
            print("   - Operational status from ANAC")
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
