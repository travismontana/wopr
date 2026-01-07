#!/usr/bin/env python3
# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
except psycopg.Error as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
