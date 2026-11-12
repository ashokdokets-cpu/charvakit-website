import os
from dotenv import load_dotenv
load_dotenv()

import psycopg2

PROD_DB_URL = "postgresql://vouchai_v4:GQVxhRPlK4qqvIXIDyw1HxDBhx3bDD3K@dpg-d9m92j0ae00c73blvoq0-a.singapore-postgres.render.com/vouchai"

try:
    conn = psycopg2.connect(PROD_DB_URL)
    cur = conn.cursor()
    
    # Delete fetched jobs older than 30 days
    cur.execute("DELETE FROM charvak_radar_fetched WHERE fetched_at < NOW() - INTERVAL '30 days'")
    deleted = cur.rowcount
    conn.commit()
    print(f"✅ Deleted {deleted} old jobs (older than 30 days)")
    
    # Delete alerts older than 30 days
    cur.execute("DELETE FROM charvak_radar_alerts WHERE created_at < NOW() - INTERVAL '30 days'")
    deleted_alerts = cur.rowcount
    conn.commit()
    print(f"✅ Deleted {deleted_alerts} old alerts")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
