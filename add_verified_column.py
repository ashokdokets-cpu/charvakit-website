from database import db

conn = db.get_connection()
cursor = conn.cursor()

try:
    # Add verified column if not exists
    cursor.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS verified BOOLEAN DEFAULT FALSE
    """)
    conn.commit()
    print("✅ verified column added to users table")
except Exception as e:
    print(f"Note: {e}")

cursor.close()
conn.close()
