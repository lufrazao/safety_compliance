"""
Migration: Add COE (Centro de Operações de Emergências) fields to airports table.
PRAI capacity, COE phone, Recovery Kit - para mapeamento das tarefas COE.

Run: python migrations/add_coe_fields.py
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
    cols = [
        ("prai_capacity_model", "TEXT"),
        ("prai_capacity_weight_kg", "INTEGER"),
        ("coe_phone", "TEXT"),
        ("has_recovery_kit", "INTEGER"),  # SQLite boolean
    ]
    with engine.connect() as conn:
        for col_name, col_type in cols:
            if column_exists("airports", col_name):
                print(f"✅ {col_name} already exists.")
            else:
                conn.execute(text(f"ALTER TABLE airports ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"✅ Added {col_name} to airports.")

if __name__ == "__main__":
    run_migration()
