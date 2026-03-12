"""
Migration: Add fire_category (CAT CIVIL) to airports table.
CAT CIVIL 1-10 do eAIS - usado para SESCINC/RBAC-153.

Run: python migrations/add_fire_category.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.database import engine, DATABASE_URL

def column_exists(table_name, column_name):
    inspector = inspect(engine)
    return column_name in [c['name'] for c in inspector.get_columns(table_name)]

def run_migration():
    if "sqlite" not in DATABASE_URL:
        print("⚠️  Migration for SQLite. Skipping if using other DB.")
        return
    if column_exists("airports", "fire_category"):
        print("✅ fire_category already exists.")
        return
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE airports ADD COLUMN fire_category INTEGER"))
        conn.commit()
    print("✅ Added fire_category to airports.")

if __name__ == "__main__":
    run_migration()
