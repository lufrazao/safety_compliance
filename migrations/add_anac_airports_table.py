"""
Migration: Cria tabela anac_airports para cache da lista oficial ANAC.

Execute: python migrations/add_anac_airports_table.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db
from app.models import Base, ANACAirport
from app.database import engine

def run_migration():
    print("Criando tabela anac_airports...")
    ANACAirport.__table__.create(engine, checkfirst=True)
    print("Tabela anac_airports criada com sucesso.")

if __name__ == "__main__":
    run_migration()
