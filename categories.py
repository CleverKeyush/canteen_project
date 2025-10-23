# categories.py
from db import get_connection

def fetch_categories():
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT id, name, description, selling_price FROM categories ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def create_category(name, description="", selling_price=0.0):
    conn = get_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO categories (name, description, selling_price) VALUES (%s, %s, %s) RETURNING id", 
                   (name, description, selling_price))
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

def update_category(category_id, name, description="", selling_price=0.0):
    conn = get_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cur = conn.cursor()
        cur.execute("UPDATE categories SET name = %s, description = %s, selling_price = %s WHERE id = %s", 
                   (name, description, selling_price, category_id))
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

def delete_category(category_id):
    conn = get_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cur = conn.cursor()
        # First delete category materials mappings
        cur.execute("DELETE FROM category_materials WHERE category_id = %s", (category_id,))
        # Then delete the category
        cur.execute("DELETE FROM categories WHERE id = %s", (category_id,))
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
