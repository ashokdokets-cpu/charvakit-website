"""
Admin cleanup endpoint - run once to remove suspicious users
"""
from database import db

def cleanup_suspicious_users():
    """Remove suspicious users from production database."""
    suspicious_emails = [
        "f.o.xuyufir.7.1.5@gmail.com",
        "ogid.igir.e5.15@gmail.com",
        "f.r.an.cisw.ill.ia.m.s6000@gmail.com",
        "vi.b.e.c.e.s.20.3@gmail.com",
        "vi.bec.e.s.20.3@gmail.com",
        "charvak707258@gmail.com",
        "charvak910754@gmail.com",
        "charvak411600@gmail.com",
        "charvak387455@gmail.com"
    ]
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        removed = 0
        removed_list = []
        for email in suspicious_emails:
            cursor.execute("DELETE FROM users WHERE email = %s", (email,))
            if cursor.rowcount > 0:
                removed += 1
                removed_list.append(email)
        
        conn.commit()
        
        # Show remaining users
        cursor.execute("SELECT user_id, email, name FROM users ORDER BY created_at DESC")
        remaining = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "removed_count": removed,
            "removed_emails": removed_list,
            "remaining_count": len(remaining),
            "remaining_users": [{"user_id": u[0], "email": u[1], "name": u[2]} for u in remaining]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
