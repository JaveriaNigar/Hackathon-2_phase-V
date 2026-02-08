import sqlite3
import os

databases = ["backend/test.db", "backend/todo_app.db"]

for db_path in databases:
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found, skipping.")
        continue
    
    print(f"Checking database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if due_date and priority exist in tasks table
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'due_date' not in columns:
            print(f"Adding due_date column to {db_path}")
            cursor.execute("ALTER TABLE tasks ADD COLUMN due_date DATETIME")
            
        if 'priority' not in columns:
            print(f"Adding priority column to {db_path}")
            cursor.execute("ALTER TABLE tasks ADD COLUMN priority VARCHAR(20)")
            
        if 'status' not in columns:
            print(f"Adding status column to {db_path}")
            cursor.execute("ALTER TABLE tasks ADD COLUMN status VARCHAR(20) DEFAULT 'active'")

        if 'tags' not in columns:
            print(f"Adding tags column to {db_path}")
            cursor.execute("ALTER TABLE tasks ADD COLUMN tags VARCHAR(1000)")

        if 'recurrence_pattern' not in columns:
            print(f"Adding recurrence_pattern column to {db_path}")
            cursor.execute("ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(1000)")

        if 'next_occurrence' not in columns:
            print(f"Adding next_occurrence column to {db_path}")
            cursor.execute("ALTER TABLE tasks ADD COLUMN next_occurrence DATETIME")

        conn.commit()
        print(f"Database {db_path} checked and updated successfully.")
    except sqlite3.Error as e:
        print(f"Error updating {db_path}: {e}")
    finally:
        conn.close()
