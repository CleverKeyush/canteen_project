# suppliers.py
from db import get_connection

def fetch_suppliers(limit=3):
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT id, name, whatsapp, phone, notes FROM suppliers ORDER BY id LIMIT %s", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_supplier_by_id(supplier_id):
    conn = get_connection()
    if not conn:
        return None
    cur = conn.cursor()
    cur.execute("SELECT id, name, whatsapp, phone, notes FROM suppliers WHERE id = %s", (supplier_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_supplier(supplier_id, name, whatsapp, phone, notes=""):
    conn = get_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cur = conn.cursor()
        cur.execute("UPDATE suppliers SET name=%s, whatsapp=%s, phone=%s, notes=%s WHERE id=%s",
                    (name, whatsapp, phone, notes, supplier_id))
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

def get_supplier_for_material(material_id):
    """
    Auto-select supplier for a material using raw_materials.supplier_id.
    Returns supplier row (id, name, whatsapp, phone, notes) or None.
    """
    conn = get_connection()
    if not conn:
        return None
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.name, s.whatsapp, s.phone, s.notes
        FROM raw_materials r
        JOIN suppliers s ON r.supplier_id = s.id
        WHERE r.id = %s
        LIMIT 1
    """, (material_id,))
    row = cur.fetchone()
    conn.close()
    return row
