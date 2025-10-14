# db.py
import os
import psycopg2

def get_connection():
    """
    Returns a new psycopg2 connection or None on failure.
    Configure DB via environment variables:
      PGHOST (default: localhost)
      PGPORT (default: 5432)
      PGDATABASE (default: canteen_db)
      PGUSER (default: postgres)
      PGPASSWORD
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", "localhost"),
            port=int(os.getenv("PGPORT", 5432)),
            database=os.getenv("PGDATABASE", "canteen_db"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD", "123456789")
        )
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None
