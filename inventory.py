# inventory.py
from db import get_connection
from datetime import datetime

def fetch_inventory():
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("SELECT id, name, quantity, unit, threshold, supplier_id FROM raw_materials ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_material(material_id):
    conn = get_connection()
    if not conn:
        return None
    cur = conn.cursor()
    cur.execute("SELECT id, name, quantity, unit, threshold, supplier_id FROM raw_materials WHERE id = %s", (material_id,))
    row = cur.fetchone()
    conn.close()
    return row

def adjust_material_quantity(material_id, delta):
    """
    delta is negative to reduce, positive to increase.
    Returns new_quantity or None on failure.
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT quantity FROM raw_materials WHERE id = %s FOR UPDATE", (material_id,))
        r = cur.fetchone()
        if not r:
            conn.rollback()
            conn.close()
            return None
        current = float(r[0])
        new_q = current + delta
        if new_q < 0:
            new_q = 0.0
        cur.execute("UPDATE raw_materials SET quantity = %s, last_updated = %s WHERE id = %s",
                    (new_q, datetime.now(), material_id))
        conn.commit()
        conn.close()
        return new_q
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        print("adjust_material_quantity error:", e)
        return None

def add_material(name, quantity, unit, threshold, supplier_id=None):
    """Add new raw material to inventory"""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO raw_materials (name, quantity, unit, threshold, supplier_id, last_updated) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (name, quantity, unit, threshold, supplier_id, datetime.now()))
        material_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        return True, material_id
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False, str(e)

def update_material(material_id, name, quantity, unit, threshold, supplier_id=None):
    """Update existing raw material"""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE raw_materials 
            SET name = %s, quantity = %s, unit = %s, threshold = %s, supplier_id = %s, last_updated = %s 
            WHERE id = %s
        """, (name, quantity, unit, threshold, supplier_id, datetime.now(), material_id))
        if cur.rowcount == 0:
            conn.rollback()
            conn.close()
            return False, "Material not found"
        conn.commit()
        conn.close()
        return True, "Material updated successfully"
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False, str(e)

def delete_material(material_id):
    """Delete raw material from inventory"""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM raw_materials WHERE id = %s", (material_id,))
        if cur.rowcount == 0:
            conn.rollback()
            conn.close()
            return False, "Material not found"
        conn.commit()
        conn.close()
        return True, "Material deleted successfully"
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False, str(e)

def get_stock_history(material_id, limit=50):
    """Get stock transaction history for a material"""
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT st.transaction_type, st.quantity_change, st.previous_quantity, 
                   st.new_quantity, st.notes, st.created_at, rm.name as material_name
            FROM stock_transactions st 
            JOIN raw_materials rm ON st.material_id = rm.id 
            WHERE st.material_id = %s 
            ORDER BY st.created_at DESC 
            LIMIT %s
        """, (material_id, limit))
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        print("get_stock_history error:", e)
        return []

def get_low_stock_materials():
    """Get all materials that are at or below threshold"""
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT rm.*, s.name as supplier_name, s.whatsapp, s.phone 
            FROM raw_materials rm 
            LEFT JOIN suppliers s ON rm.supplier_id = s.id 
            WHERE rm.quantity <= rm.threshold
            ORDER BY (rm.quantity / rm.threshold) ASC
        """)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        print("get_low_stock_materials error:", e)
        return []

def calculate_material_cost(category_id):
    """Calculate total material cost for one unit of a category"""
    conn = get_connection()
    if not conn:
        return 0.0
    try:
        cur = conn.cursor()
        cur.execute("SELECT calculate_material_cost(%s)", (category_id,))
        result = cur.fetchone()
        conn.close()
        return float(result[0]) if result and result[0] else 0.0
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        print("calculate_material_cost error:", e)
        return 0.0

def record_sale_with_profit(category_id, quantity_sold, unit_price):
    """Record a sale with automatic profit calculation"""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    try:
        cur = conn.cursor()
        
        # Calculate material cost per unit
        material_cost = calculate_material_cost(category_id)
        profit_per_unit = unit_price - material_cost
        
        # Calculate totals
        total_revenue = unit_price * quantity_sold
        total_cost = material_cost * quantity_sold
        total_profit = profit_per_unit * quantity_sold
        
        # Insert sale record
        cur.execute("""
            INSERT INTO daily_sales (
                category_id, quantity_sold, unit_price, material_cost_per_unit,
                profit_per_unit, total_revenue, total_cost, total_profit
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (category_id, quantity_sold, unit_price, material_cost, 
              profit_per_unit, total_revenue, total_cost, total_profit))
        
        sale_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        
        return True, {
            'sale_id': sale_id,
            'material_cost': material_cost,
            'profit_per_unit': profit_per_unit,
            'total_profit': total_profit,
            'profit_margin': (profit_per_unit / unit_price * 100) if unit_price > 0 else 0
        }
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False, str(e)

def get_profit_summary(days=7):
    """Get profit summary for the last N days"""
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT summary_date, total_sales_count, total_revenue, 
                   total_cost, total_profit, profit_margin_percent
            FROM profit_summary 
            WHERE summary_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY summary_date DESC
        """, (days,))
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        print("get_profit_summary error:", e)
        return []

def get_item_profitability():
    """Get profitability analysis for each menu item"""
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.name, c.selling_price, calculate_material_cost(c.id) as material_cost,
                   (c.selling_price - calculate_material_cost(c.id)) as profit_per_unit,
                   CASE 
                       WHEN c.selling_price > 0 THEN 
                           ROUND(((c.selling_price - calculate_material_cost(c.id)) / c.selling_price) * 100, 2)
                       ELSE 0 
                   END as profit_margin_percent
            FROM categories c
            ORDER BY profit_per_unit DESC
        """)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        print("get_item_profitability error:", e)
        return []
