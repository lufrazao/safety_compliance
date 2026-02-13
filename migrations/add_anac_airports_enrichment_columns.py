"""
Migration: Adiciona colunas de enriquecimento em anac_airports.
usage_class, avsec_classification, aircraft_size_category, number_of_runways

Execute: python migrations/add_anac_airports_enrichment_columns.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine

def run_migration():
    cols = [
        ("usage_class", "VARCHAR(20)"),
        ("avsec_classification", "VARCHAR(10)"),
        ("aircraft_size_category", "VARCHAR(5)"),
        ("number_of_runways", "INTEGER DEFAULT 1"),
    ]
    with engine.connect() as conn:
        for col_name, col_type in cols:
            try:
                conn.execute(text(f"ALTER TABLE anac_airports ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                print(f"Coluna {col_name} adicionada.")
            except Exception as e:
                err = str(e).lower()
                if "duplicate" in err or "already exists" in err or "exist" in err:
                    print(f"Coluna {col_name} já existe.")
                else:
                    raise
    print("Migração concluída.")

if __name__ == "__main__":
    run_migration()
