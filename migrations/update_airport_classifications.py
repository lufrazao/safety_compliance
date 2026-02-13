"""
Migration script to update airport classifications to ANAC standards.
This script adds new classification fields and migrates existing data.
"""
import sqlite3
import os
from pathlib import Path

def run_migration():
    """Update airport classifications to ANAC standards."""
    db_path = Path("compliance.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first to create it.")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(airports)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add new classification columns if they don't exist
        if 'usage_class' not in columns:
            cursor.execute("""
                ALTER TABLE airports 
                ADD COLUMN usage_class VARCHAR(20)
            """)
            print("✅ Added 'usage_class' column")
        
        if 'avsec_classification' not in columns:
            cursor.execute("""
                ALTER TABLE airports 
                ADD COLUMN avsec_classification VARCHAR(10)
            """)
            print("✅ Added 'avsec_classification' column")
        
        if 'aircraft_size_category' not in columns:
            cursor.execute("""
                ALTER TABLE airports 
                ADD COLUMN aircraft_size_category VARCHAR(5)
            """)
            print("✅ Added 'aircraft_size_category' column")
        
        # Migrate existing data from 'category' to new fields
        # Note: Old category field (1C-9C) will be kept for compatibility
        cursor.execute("""
            SELECT id, annual_passengers, max_aircraft_weight, category 
            FROM airports 
            WHERE annual_passengers IS NOT NULL
        """)
        
        airports = cursor.fetchall()
        migrated = 0
        
        for airport_id, passengers, max_weight, old_category in airports:
            if passengers is None:
                continue
            
            # Calculate usage_class (RBAC 153)
            if passengers < 200000:
                usage_class = 'I'
            elif passengers < 1000000:
                usage_class = 'II'
            elif passengers < 5000000:
                usage_class = 'III'
            else:
                usage_class = 'IV'
            
            # Calculate AVSEC classification
            if passengers < 600000:
                avsec = 'AP-1'
            elif passengers < 5000000:
                avsec = 'AP-2'
            else:
                avsec = 'AP-3'
            
            # Calculate aircraft_size_category
            aircraft_category = None
            if max_weight:
                weight_kg = max_weight * 1000  # Convert tons to kg
                if weight_kg <= 5700:
                    aircraft_category = 'A/B'
                elif weight_kg <= 136000:
                    aircraft_category = 'C'
                else:
                    aircraft_category = 'D'
            
            # Update airport
            cursor.execute("""
                UPDATE airports 
                SET usage_class = ?, avsec_classification = ?, aircraft_size_category = ?
                WHERE id = ?
            """, (usage_class, avsec, aircraft_category, airport_id))
            
            migrated += 1
        
        conn.commit()
        
        print(f"✅ Migration completed successfully!")
        print(f"   Migrated {migrated} airport(s) with passenger data")
        print(f"   New classification fields added:")
        print(f"     - usage_class (RBAC 153: I, II, III, IV, PRIVADO)")
        print(f"     - avsec_classification (AP-0, AP-1, AP-2, AP-3)")
        print(f"     - aircraft_size_category (A/B, C, D)")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Running migration: update_airport_classifications...")
    run_migration()
