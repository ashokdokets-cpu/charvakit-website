from auth import hash_password
from database import db

# Choose your password
new_password = "Charvak@2026"

hashed = hash_password(new_password)

conn = db.get_connection()
cursor = conn.cursor()
cursor.execute(
    "UPDATE users SET password_hash = %s WHERE email = %s",
    (hashed, "hr@charvakit.com")
)
conn.commit()

print(f"✅ Password set for hr@charvakit.com")
print(f"Password: {new_password}")
cursor.close()
conn.close()
