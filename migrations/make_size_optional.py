"""
Migration script to make airport size field optional.
Since we now calculate size automatically from usage_class or annual_passengers,
the size field is no longer required in the form.
"""
import sqlite3
import os
from pathlib import Path

def run_migration():
    """Make size field optional (it will be calculated automatically)."""
    db_path = Path("compliance.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first to create it.")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # SQLite doesn't support ALTER COLUMN to change nullability directly
        # We need to check if size is already nullable or if we need to handle it differently
        cursor.execute("PRAGMA table_info(airports)")
        columns = cursor.fetchall()
        
        size_column = [col for col in columns if col[1] == 'size']
        
        if size_column:
            print("✅ Campo 'size' existe na tabela")
            print("   Nota: SQLite não suporta alterar nullability diretamente.")
            print("   O campo 'size' será calculado automaticamente a partir de 'usage_class' ou 'annual_passengers'.")
            print("   Dados existentes serão preservados.")
        else:
            print("⚠️  Campo 'size' não encontrado na tabela")
        
        # Verificar se há aeroportos sem size e calcular se necessário
        cursor.execute("""
            SELECT id, usage_class, annual_passengers, size 
            FROM airports 
            WHERE size IS NULL
        """)
        
        airports_without_size = cursor.fetchall()
        
        if airports_without_size:
            print(f"\n📊 Encontrados {len(airports_without_size)} aeroporto(s) sem 'size'")
            print("   Calculando 'size' automaticamente...")
            
            for airport_id, usage_class, annual_passengers, current_size in airports_without_size:
                calculated_size = None
                
                if usage_class:
                    if usage_class in ['PRIVADO', 'I']:
                        calculated_size = 'small'
                    elif usage_class == 'II':
                        calculated_size = 'medium'
                    elif usage_class == 'III':
                        calculated_size = 'large'
                    elif usage_class == 'IV':
                        calculated_size = 'international'
                elif annual_passengers:
                    if annual_passengers < 200000:
                        calculated_size = 'small'
                    elif annual_passengers < 1000000:
                        calculated_size = 'medium'
                    elif annual_passengers < 10000000:
                        calculated_size = 'large'
                    else:
                        calculated_size = 'international'
                else:
                    calculated_size = 'small'  # Default
                
                if calculated_size:
                    cursor.execute("""
                        UPDATE airports 
                        SET size = ? 
                        WHERE id = ?
                    """, (calculated_size, airport_id))
            
            conn.commit()
            print(f"✅ {len(airports_without_size)} aeroporto(s) atualizado(s)")
        
        print(f"\n✅ Migração concluída!")
        print(f"   O campo 'size' agora é calculado automaticamente")
        print(f"   Baseado em 'usage_class' (RBAC 153) ou 'annual_passengers'")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro durante a migração: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Executando migração: make_size_optional...")
    run_migration()
