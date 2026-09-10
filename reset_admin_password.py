from auth import hash_password
from database import db

new_password = "Charvak@2026"
hashed = hash_password(new_password)

conn = db.get_connection()
cursor = conn.cursor()
cursor.execute(
    "UPDATE users SET password_hash = %s WHERE email = %s",
    (hashed, "hr@charvakit.com")
)
conn.commit()
print(f"✅ Password set to: {new_password}")
print(f"Email: hr@charvakit.com")
cursor.close()
conn.close()
