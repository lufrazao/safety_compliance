"""
Migration script to add document_attachments table.
Run this script to add the document_attachments table to the database.
"""
import sqlite3
import os
from pathlib import Path

def run_migration():
    """Add document_attachments table to the database."""
    db_path = Path("compliance.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first to create it.")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='document_attachments'
        """)
        
        if cursor.fetchone():
            print("✅ Table 'document_attachments' already exists.")
            return
        
        # Create table
        cursor.execute("""
            CREATE TABLE document_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compliance_record_id INTEGER NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER NOT NULL,
                file_type VARCHAR(100),
                document_type VARCHAR(50),
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                uploaded_by VARCHAR(100),
                description TEXT,
                FOREIGN KEY (compliance_record_id) REFERENCES compliance_records (id) ON DELETE CASCADE
            )
        """)
        
        # Create index
        cursor.execute("""
            CREATE INDEX idx_document_compliance_record 
            ON document_attachments(compliance_record_id)
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   Table 'document_attachments' created.")
        print("   Index created on compliance_record_id.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Running migration: add_document_attachments...")
    run_migration()
