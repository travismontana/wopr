#!/usr/bin/env python3
"""
Load schema.sql into wopr config database
"""
import psycopg
import sys

# Database connection
DATABASE_URL = "postgresql://wopr:changeme-in-production@wopr-config-service-db-0.wopr-config-service-db.wopr.svc.cluster.local:5432/config_db"

# Read schema file
schema_file = "schema.sql"

try:
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
    
    print(f"Read {len(schema_sql)} characters from {schema_file}")
    
    # Connect and execute
    print("Connecting to database...")
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Executing schema...")
    cur.execute(schema_sql)
    
    conn.commit()
    print("✅ Schema loaded successfully")
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM settings")
    count = cur.fetchone()[0]
    print(f"✅ Settings table has {count} rows")
    
    cur.close()
    conn.close()
    
except FileNotFoundError:
    print(f"❌ File not found: {schema_file}")
    sys.exit(1)
except psycopg2.Error as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)