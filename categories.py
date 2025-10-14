# categories.py
from db import get_connection

def fetch_categories():
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT id, name, description FROM categories ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def create_category(name, description=""):
    conn = get_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO categories (name, description) VALUES (%s, %s) RETURNING id", (name, description))
        cid = cur.fetchone()[0]
        conn.commit()
        conn.close()
        return True, cid
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False, str(e)

def set_category_material(category_id, material_id, amount_per_unit):
    conn = get_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO category_materials (category_id, material_id, amount_per_unit)
            VALUES (%s, %s, %s)
            ON CONFLICT (category_id, material_id)
            DO UPDATE SET amount_per_unit = EXCLUDED.amount_per_unit
        """, (category_id, material_id, amount_per_unit))
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False, str(e)

def get_category_materials(category_id):
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT cm.material_id, rm.name, cm.amount_per_unit, rm.quantity, rm.unit, rm.threshold, rm.supplier_id
        FROM category_materials cm
        JOIN raw_materials rm ON cm.material_id = rm.id
        WHERE cm.category_id = %s
    """, (category_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
