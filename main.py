# main.py
import tkinter as tk
from tkinter import ttk, messagebox, font
from decimal import Decimal
import time
import os
from inventory import fetch_inventory, get_material, adjust_material_quantity, add_material, update_material, delete_material, calculate_material_cost, record_sale_with_profit, get_profit_summary, get_item_profitability, predict_tomorrow_production, generate_bill_text
from categories import fetch_categories, create_category, update_category, delete_category, set_category_material, get_category_materials
from suppliers import fetch_suppliers, get_supplier_by_id, update_supplier, get_supplier_for_material
from whatsapp_notify import send_whatsapp_twilio, open_whatsapp_web, TWILIO_ENABLED
from db import get_connection

# Main window
root = tk.Tk()
root.title("Canteen Inventory Management System")
root.geometry("1400x800")
root.configure(bg='#f0f0f0')

# Set window icon - FIXED for Windows taskbar
def setup_taskbar_icon():
    """Setup icon that appears properly in Windows taskbar"""
    import os
    
    # Method 1: Try the ICO file first (best for Windows)
    try:
        if os.path.exists('canteen_icon.ico'):
            root.iconbitmap('canteen_icon.ico')
            print("✅ ICO icon loaded - should appear in taskbar")
            return True
    except Exception as e:
        print(f"⚠️ ICO loading failed: {e}")
    
    # Method 2: Try PNG with iconphoto
    try:
        if os.path.exists('canteen_icon.png'):
            icon_img = tk.PhotoImage(file='canteen_icon.png')
            root.iconphoto(True, icon_img)
            print("✅ PNG icon loaded")
            return True
    except Exception as e:
        print(f"⚠️ PNG loading failed: {e}")
    
    print("ℹ️ No custom icon found, using default")
    return False

# Apply the icon
setup_taskbar_icon()

# Windows-specific taskbar fixes
try:
    import sys
    if sys.platform == "win32":
        # This helps Windows recognize the app properly in taskbar
        import ctypes
        myappid = 'canteen.inventory.management.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        print("✅ Windows App ID set for proper taskbar display")
except Exception as e:
    print(f"ℹ️ Windows taskbar setup skipped: {e}")

# Set window properties
root.resizable(True, True)
root.minsize(1000, 600)

# Configure styles
style = ttk.Style()
style.theme_use('clam')

# Simple Professional Colors
PRIMARY_COLOR = '#2c3e50'      # Professional dark blue
SECONDARY_COLOR = '#3498db'    # Clean blue
SUCCESS_COLOR = '#27ae60'      # Professional green
WARNING_COLOR = '#f39c12'      # Clear orange
DANGER_COLOR = '#e74c3c'       # Clean red
LIGHT_BG = '#f8f9fa'          # Light gray background
DARK_TEXT = '#2c3e50'         # Dark text
CARD_BG = '#ffffff'           # White cards

# Simple professional styles
style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground=PRIMARY_COLOR, background=LIGHT_BG)
style.configure('Heading.TLabel', font=('Arial', 11, 'bold'), foreground=PRIMARY_COLOR, background=CARD_BG)
style.configure('Custom.Treeview', font=('Arial', 9), rowheight=22)
style.configure('Custom.Treeview.Heading', font=('Arial', 10, 'bold'), foreground='white', background=PRIMARY_COLOR)

# Simple notebook style
style.configure('TNotebook', background=LIGHT_BG)
style.configure('TNotebook.Tab', padding=[12, 8], font=('Arial', 10, 'bold'))

# Simple professional button styles
style.configure('Primary.TButton', 
                font=('Arial', 10, 'bold'), 
                foreground='white', 
                background=SECONDARY_COLOR,
                padding=(10, 6))
style.configure('Success.TButton', 
                font=('Arial', 10, 'bold'), 
                foreground='white', 
                background=SUCCESS_COLOR,
                padding=(10, 6))
style.configure('Warning.TButton', 
                font=('Arial', 10, 'bold'), 
                foreground='white', 
                background=WARNING_COLOR,
                padding=(10, 6))
style.configure('Danger.TButton', 
                font=('Arial', 10, 'bold'), 
                foreground='white', 
                background=DANGER_COLOR,
                padding=(10, 6))

# Simple hover effects
style.map('Primary.TButton', background=[('active', '#2980b9')])
style.map('Success.TButton', background=[('active', '#229954')])
style.map('Warning.TButton', background=[('active', '#d68910')])
style.map('Danger.TButton', background=[('active', '#cb4335')])

# Simple professional header with icon
header_frame = tk.Frame(root, bg=PRIMARY_COLOR, height=70)
header_frame.pack(fill="x")
header_frame.pack_propagate(False)

# Header content with icon and title
header_content = tk.Frame(header_frame, bg=PRIMARY_COLOR)
header_content.pack(expand=True, fill="both")

# Title with icon emoji
title_label = tk.Label(header_content, text="🍽️ Canteen Inventory Management", 
                      font=('Arial', 18, 'bold'), fg='white', bg=PRIMARY_COLOR)
title_label.pack(pady=20)

# Clean main content frame
main_frame = tk.Frame(root, bg=LIGHT_BG)
main_frame.pack(fill="both", expand=True, padx=15, pady=15)

# Simple notebook
notebook = ttk.Notebook(main_frame)
notebook.pack(fill="both", expand=True)

# Inventory tab
inventory_tab = ttk.Frame(notebook)
notebook.add(inventory_tab, text="📦 Inventory Management")

# Categories tab  
categories_tab = ttk.Frame(notebook)
notebook.add(categories_tab, text="📋 Categories & Sales")

# Simple clean frames
inv_left = tk.Frame(inventory_tab, bg=CARD_BG, relief='solid', bd=1)
inv_left.pack(side="left", fill="both", expand=True, padx=(10,5), pady=10)

inv_right = tk.Frame(inventory_tab, bg=CARD_BG, relief='solid', bd=1, width=300)
inv_right.pack(side="right", fill="y", padx=(5,10), pady=10)
inv_right.pack_propagate(False)

# Simple clean frames
cat_left = tk.Frame(categories_tab, bg=CARD_BG, relief='solid', bd=1)
cat_left.pack(side="left", fill="both", expand=True, padx=(10,5), pady=10)

cat_right = tk.Frame(categories_tab, bg=CARD_BG, relief='solid', bd=1, width=300)
cat_right.pack(side="right", fill="y", padx=(5,10), pady=10)
cat_right.pack_propagate(False)

# Simple inventory section
inv_title_frame = tk.Frame(inv_left, bg=CARD_BG)
inv_title_frame.pack(fill="x", padx=15, pady=(15,10))

inv_title = tk.Label(inv_title_frame, text="Raw Materials Inventory", 
                    font=('Arial', 12, 'bold'), fg=PRIMARY_COLOR, bg=CARD_BG)
inv_title.pack(side="left")

# Modern status indicator with badge style
status_frame = tk.Frame(inv_title_frame, bg=CARD_BG)
status_frame.pack(side="right")

# Simple inventory tree
inv_tree_frame = tk.Frame(inv_left, bg=CARD_BG)
inv_tree_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))

inv_cols = ("ID", "Name", "Quantity", "Unit", "Threshold", "Cost/Unit (₹)", "Supplier ID", "Status")
inv_tree = ttk.Treeview(inv_tree_frame, columns=inv_cols, show="headings", height=15, style='Custom.Treeview')

# Configure column widths and headings
column_widths = {"ID": 60, "Name": 180, "Quantity": 80, "Unit": 60, "Threshold": 80, "Cost/Unit (₹)": 100, "Supplier ID": 80, "Status": 100}
for c in inv_cols:
    inv_tree.heading(c, text=c)
    inv_tree.column(c, anchor="center", width=column_widths.get(c, 100))

# Add scrollbars
inv_v_scroll = ttk.Scrollbar(inv_tree_frame, orient="vertical", command=inv_tree.yview)
inv_h_scroll = ttk.Scrollbar(inv_tree_frame, orient="horizontal", command=inv_tree.xview)
inv_tree.configure(yscrollcommand=inv_v_scroll.set, xscrollcommand=inv_h_scroll.set)

inv_tree.pack(side="left", fill="both", expand=True)
inv_v_scroll.pack(side="right", fill="y")
inv_h_scroll.pack(side="bottom", fill="x")

def load_inventory():
    for i in inv_tree.get_children():
        inv_tree.delete(i)
    
    low_stock_count = 0
    total_items = 0
    
    for r in fetch_inventory():
        total_items += 1
        # r = (id, name, quantity, unit, threshold, cost_per_unit, supplier_id)
        quantity = float(r[2]) if r[2] else 0
        threshold = float(r[4]) if r[4] else 0
        
        if quantity <= 0:
            status = "❌ Out of Stock"
            tag = "out_of_stock"
        elif quantity <= threshold:
            status = "⚠️ Low Stock"
            tag = "low_stock"
            low_stock_count += 1
        else:
            status = "✅ In Stock"
            tag = "in_stock"
        
        values = list(r) + [status]
        item = inv_tree.insert("", "end", values=values, tags=(tag,))
    
    # Configure row colors
    inv_tree.tag_configure("out_of_stock", background="#ffebee", foreground="#c62828")
    inv_tree.tag_configure("low_stock", background="#fff3e0", foreground="#ef6c00")
    inv_tree.tag_configure("in_stock", background="#e8f5e8", foreground="#2e7d32")
    
    # Simple status indicator
    for widget in status_frame.winfo_children():
        widget.destroy()
    
    if low_stock_count > 0:
        status_label = tk.Label(status_frame, text=f"⚠️ {low_stock_count} items low", 
                               fg=WARNING_COLOR, bg=CARD_BG, font=('Arial', 10, 'bold'))
    else:
        status_label = tk.Label(status_frame, text="✅ All items stocked", 
                               fg=SUCCESS_COLOR, bg=CARD_BG, font=('Arial', 10, 'bold'))
    status_label.pack()

# MATERIAL MANAGEMENT FUNCTIONS
def add_material_popup():
    win = tk.Toplevel(root)
    win.title("➕ Add New Material")
    win.geometry("500x450")
    win.configure(bg='white')
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    # Header
    header = tk.Frame(win, bg=SUCCESS_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="➕ Add New Raw Material", font=('Arial', 14, 'bold'), 
             fg='white', bg=SUCCESS_COLOR).pack(pady=20)
    
    # Form frame
    form_frame = tk.Frame(win, bg='white')
    form_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    tk.Label(form_frame, text="Material Name *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=0, column=0, sticky="w", pady=(0,5))
    e_name = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_name.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,15))
    
    tk.Label(form_frame, text="Initial Quantity *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=2, column=0, sticky="w", pady=(0,5))
    e_qty = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_qty.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0,15))
    
    tk.Label(form_frame, text="Unit (kg, liters, pieces, etc.) *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=4, column=0, sticky="w", pady=(0,5))
    e_unit = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_unit.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0,15))
    
    tk.Label(form_frame, text="Low Stock Threshold *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=6, column=0, sticky="w", pady=(0,5))
    e_threshold = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_threshold.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0,15))
    
    tk.Label(form_frame, text="Cost per Unit (₹) *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=8, column=0, sticky="w", pady=(0,5))
    e_cost = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_cost.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0,15))
    
    tk.Label(form_frame, text="Supplier ID (optional)", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=10, column=0, sticky="w", pady=(0,5))
    e_supplier = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_supplier.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(0,20))
    
    form_frame.columnconfigure(0, weight=1)
    
    def save_material():
        name = e_name.get().strip()
        try:
            quantity = float(e_qty.get())
            threshold = float(e_threshold.get())
            cost_per_unit = float(e_cost.get())
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter valid numbers for quantity, threshold, and cost!")
            return
        
        unit = e_unit.get().strip()
        supplier_id = e_supplier.get().strip() or None
        
        if not name or not unit:
            messagebox.showerror("❌ Error", "Name and unit are required!")
            return
        
        if cost_per_unit < 0:
            messagebox.showerror("❌ Error", "Cost per unit cannot be negative!")
            return
        
        if supplier_id:
            try:
                supplier_id = int(supplier_id)
            except ValueError:
                messagebox.showerror("❌ Error", "Supplier ID must be a number!")
                return
        
        ok, result = add_material(name, quantity, unit, threshold, cost_per_unit, supplier_id)
        if ok:
            messagebox.showinfo("✅ Success", f"Material '{name}' added successfully with ID: {result}")
            load_inventory()
            update_stats()
            win.destroy()
        else:
            messagebox.showerror("❌ Error", f"Failed to add material: {result}")
    
    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=12, column=0, columnspan=2, pady=10)
    
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="✅ Add Material", command=save_material, style='Success.TButton').pack(side="left")
    
    e_name.focus_set()

def edit_material_popup():
    sel = inv_tree.selection()
    if not sel:
        messagebox.showerror("❌ Error", "Please select a material to edit!")
        return
    
    material_data = inv_tree.item(sel[0])['values']
    material_id = material_data[0]
    
    win = tk.Toplevel(root)
    win.title("✏️ Edit Material")
    win.geometry("500x450")
    win.configure(bg='white')
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    # Header
    header = tk.Frame(win, bg=SECONDARY_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text=f"✏️ Edit Material - ID: {material_id}", font=('Arial', 14, 'bold'), 
             fg='white', bg=SECONDARY_COLOR).pack(pady=20)
    
    # Form frame
    form_frame = tk.Frame(win, bg='white')
    form_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    tk.Label(form_frame, text="Material Name *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=0, column=0, sticky="w", pady=(0,5))
    e_name = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_name.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,15))
    e_name.insert(0, material_data[1])
    
    tk.Label(form_frame, text="Current Quantity *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=2, column=0, sticky="w", pady=(0,5))
    e_qty = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_qty.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0,15))
    e_qty.insert(0, material_data[2])
    
    tk.Label(form_frame, text="Unit *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=4, column=0, sticky="w", pady=(0,5))
    e_unit = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_unit.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0,15))
    e_unit.insert(0, material_data[3])
    
    tk.Label(form_frame, text="Low Stock Threshold *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=6, column=0, sticky="w", pady=(0,5))
    e_threshold = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_threshold.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0,15))
    e_threshold.insert(0, material_data[4])
    
    tk.Label(form_frame, text="Cost per Unit (₹) *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=8, column=0, sticky="w", pady=(0,5))
    e_cost = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_cost.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0,15))
    e_cost.insert(0, material_data[5] if material_data[5] else "0")
    
    tk.Label(form_frame, text="Supplier ID", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=10, column=0, sticky="w", pady=(0,5))
    e_supplier = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_supplier.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(0,20))
    e_supplier.insert(0, material_data[6] if material_data[6] else "")
    
    form_frame.columnconfigure(0, weight=1)
    
    def update_material_data():
        name = e_name.get().strip()
        try:
            quantity = float(e_qty.get())
            threshold = float(e_threshold.get())
            cost_per_unit = float(e_cost.get())
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter valid numbers for quantity, threshold, and cost!")
            return
        
        unit = e_unit.get().strip()
        supplier_id = e_supplier.get().strip() or None
        
        if not name or not unit:
            messagebox.showerror("❌ Error", "Name and unit are required!")
            return
        
        if cost_per_unit < 0:
            messagebox.showerror("❌ Error", "Cost per unit cannot be negative!")
            return
        
        if supplier_id:
            try:
                supplier_id = int(supplier_id)
            except ValueError:
                messagebox.showerror("❌ Error", "Supplier ID must be a number!")
                return
        
        ok, result = update_material(material_id, name, quantity, unit, threshold, cost_per_unit, supplier_id)
        if ok:
            messagebox.showinfo("✅ Success", f"Material updated successfully!")
            load_inventory()
            update_stats()
            win.destroy()
        else:
            messagebox.showerror("❌ Error", f"Failed to update material: {result}")
    
    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=12, column=0, columnspan=2, pady=10)
    
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="✅ Update Material", command=update_material_data, style='Primary.TButton').pack(side="left")
    
    e_name.focus_set()

def restock_material_popup():
    sel = inv_tree.selection()
    if not sel:
        messagebox.showerror("❌ Error", "Please select a material to restock!")
        return
    
    material_data = inv_tree.item(sel[0])['values']
    material_id = material_data[0]
    material_name = material_data[1]
    current_qty = material_data[2]
    unit = material_data[3]
    
    win = tk.Toplevel(root)
    win.title("📈 Restock Material")
    win.geometry("450x300")
    win.configure(bg='white')
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    # Header
    header = tk.Frame(win, bg=WARNING_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="📈 Restock Material", font=('Arial', 14, 'bold'), 
             fg='white', bg=WARNING_COLOR).pack(pady=20)
    
    # Info frame
    info_frame = tk.LabelFrame(win, text="📦 Material Information", font=('Arial', 10, 'bold'), 
                              fg=PRIMARY_COLOR, bg='white', bd=2, relief='groove')
    info_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Label(info_frame, text=f"Material: {material_name}", font=('Arial', 10), 
             fg=DARK_TEXT, bg='white').pack(anchor="w", padx=10, pady=5)
    tk.Label(info_frame, text=f"Current Stock: {current_qty} {unit}", font=('Arial', 10), 
             fg=DARK_TEXT, bg='white').pack(anchor="w", padx=10, pady=5)
    
    # Form frame
    form_frame = tk.Frame(win, bg='white')
    form_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    tk.Label(form_frame, text=f"Quantity to Add ({unit}) *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=0, column=0, sticky="w", pady=(0,5))
    e_qty = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_qty.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,20))
    
    form_frame.columnconfigure(0, weight=1)
    
    def add_stock():
        try:
            add_qty = float(e_qty.get())
            if add_qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter a valid positive quantity!")
            return
        
        new_qty = adjust_material_quantity(material_id, add_qty)
        if new_qty is not None:
            messagebox.showinfo("✅ Success", f"Added {add_qty} {unit} to {material_name}!\nNew stock: {new_qty} {unit}")
            load_inventory()
            update_stats()
            win.destroy()
        else:
            messagebox.showerror("❌ Error", "Failed to update stock. Please try again.")
    
    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
    
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="📈 Add Stock", command=add_stock, style='Warning.TButton').pack(side="left")
    
    e_qty.focus_set()

def delete_material_popup():
    sel = inv_tree.selection()
    if not sel:
        messagebox.showerror("❌ Error", "Please select a material to delete!")
        return
    
    material_data = inv_tree.item(sel[0])['values']
    material_id = material_data[0]
    material_name = material_data[1]
    
    result = messagebox.askyesno("⚠️ Confirm Delete", 
                                f"Are you sure you want to delete '{material_name}'?\n\nThis action cannot be undone!")
    if result:
        ok, message = delete_material(material_id)
        if ok:
            messagebox.showinfo("✅ Success", f"Material '{material_name}' deleted successfully!")
            load_inventory()
            update_stats()
        else:
            messagebox.showerror("❌ Error", f"Failed to delete material: {message}")

def show_item_profitability():
    """Show profitability analysis for each menu item"""
    win = tk.Toplevel(root)
    win.title("📊 Item Profitability Analysis")
    win.geometry("800x500")
    win.configure(bg='white')
    win.transient(root)
    
    # Header
    header = tk.Frame(win, bg=SUCCESS_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="📊 Item Profitability Analysis", font=('Arial', 14, 'bold'), 
             fg='white', bg=SUCCESS_COLOR).pack(pady=20)
    
    # Content frame
    content_frame = tk.Frame(win, bg='white')
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Create treeview for profitability data
    profit_cols = ("Item", "Selling Price (₹)", "Material Cost (₹)", "Profit/Unit (₹)", "Margin %")
    profit_tree = ttk.Treeview(content_frame, columns=profit_cols, show="headings", height=15, style='Custom.Treeview')
    
    for c in profit_cols:
        profit_tree.heading(c, text=c)
        profit_tree.column(c, anchor="center", width=150)
    
    # Add scrollbar
    profit_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=profit_tree.yview)
    profit_tree.configure(yscrollcommand=profit_scroll.set)
    
    profit_tree.pack(side="left", fill="both", expand=True)
    profit_scroll.pack(side="right", fill="y")
    
    # Populate data
    items = get_item_profitability()
    for item in items:
        name, selling_price, material_cost, profit_per_unit, margin = item
        values = (
            name,
            f"₹{selling_price:.2f}",
            f"₹{material_cost:.2f}",
            f"₹{profit_per_unit:.2f}",
            f"{margin:.1f}%"
        )
        
        # Color code based on profitability
        if profit_per_unit > 5:
            tag = "high_profit"
        elif profit_per_unit > 2:
            tag = "medium_profit"
        else:
            tag = "low_profit"
        
        profit_tree.insert("", "end", values=values, tags=(tag,))
    
    # Configure row colors
    profit_tree.tag_configure("high_profit", background="#e8f5e8", foreground="#2e7d32")
    profit_tree.tag_configure("medium_profit", background="#fff3e0", foreground="#ef6c00")
    profit_tree.tag_configure("low_profit", background="#ffebee", foreground="#c62828")
    
    # Close button
    ttk.Button(content_frame, text="Close", command=win.destroy).pack(pady=(10,0))

def show_sales_history():
    """Show individual sales records"""
    win = tk.Toplevel(root)
    win.title("📋 Sales History")
    win.geometry("900x500")
    win.configure(bg='white')
    win.transient(root)
    
    # Header
    header = tk.Frame(win, bg=SECONDARY_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="📋 Individual Sales Records", font=('Arial', 14, 'bold'), 
             fg='white', bg=SECONDARY_COLOR).pack(pady=20)
    
    # Content frame
    content_frame = tk.Frame(win, bg='white')
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Create treeview for sales history
    sales_cols = ("Date", "Item", "Qty", "Unit Price (₹)", "Revenue (₹)", "Cost (₹)", "Profit (₹)")
    sales_tree = ttk.Treeview(content_frame, columns=sales_cols, show="headings", height=15, style='Custom.Treeview')
    
    for c in sales_cols:
        sales_tree.heading(c, text=c)
        sales_tree.column(c, anchor="center", width=120)
    
    # Add scrollbar
    sales_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=sales_tree.yview)
    sales_tree.configure(yscrollcommand=sales_scroll.set)
    
    sales_tree.pack(side="left", fill="both", expand=True)
    sales_scroll.pack(side="right", fill="y")
    
    # Get sales data from database
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT ds.sale_date, c.name, ds.quantity_sold, ds.unit_price, 
                       ds.total_revenue, ds.total_cost, ds.total_profit
                FROM daily_sales ds
                JOIN categories c ON ds.category_id = c.id
                ORDER BY ds.sale_date DESC, ds.sale_time DESC
                LIMIT 100
            """)
            sales_data = cur.fetchall()
            conn.close()
            
            # Populate data
            for sale in sales_data:
                date, item, qty, unit_price, revenue, cost, profit = sale
                values = (
                    date.strftime("%Y-%m-%d"),
                    item,
                    qty,
                    f"₹{unit_price:.2f}",
                    f"₹{revenue:.2f}",
                    f"₹{cost:.2f}",
                    f"₹{profit:.2f}"
                )
                sales_tree.insert("", "end", values=values)
                
        except Exception as e:
            tk.Label(content_frame, text=f"Error loading sales data: {e}", 
                     font=('Arial', 12), fg='red', bg='white').pack(expand=True)
    else:
        tk.Label(content_frame, text="Database connection failed", 
                 font=('Arial', 12), fg='red', bg='white').pack(expand=True)
    
    # Close button
    ttk.Button(content_frame, text="Close", command=win.destroy).pack(pady=(10,0))

def show_profit_summary():
    """Show daily profit summary"""
    win = tk.Toplevel(root)
    win.title("💹 Profit Summary")
    win.geometry("700x400")
    win.configure(bg='white')
    win.transient(root)
    
    # Header
    header = tk.Frame(win, bg=PRIMARY_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="💹 Daily Profit Summary (Last 7 Days)", font=('Arial', 14, 'bold'), 
             fg='white', bg=PRIMARY_COLOR).pack(pady=20)
    
    # Content frame
    content_frame = tk.Frame(win, bg='white')
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Create treeview for profit summary
    summary_cols = ("Date", "Sales Count", "Revenue (₹)", "Cost (₹)", "Profit (₹)", "Margin %")
    summary_tree = ttk.Treeview(content_frame, columns=summary_cols, show="headings", height=10, style='Custom.Treeview')
    
    for c in summary_cols:
        summary_tree.heading(c, text=c)
        summary_tree.column(c, anchor="center", width=110)
    
    # Add scrollbar
    summary_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=summary_tree.yview)
    summary_tree.configure(yscrollcommand=summary_scroll.set)
    
    summary_tree.pack(side="left", fill="both", expand=True)
    summary_scroll.pack(side="right", fill="y")
    
    # Populate data
    summaries = get_profit_summary(7)
    total_profit = 0
    total_revenue = 0
    
    for summary in summaries:
        date, sales_count, revenue, cost, profit, margin = summary
        total_profit += float(profit)
        total_revenue += float(revenue)
        
        values = (
            date.strftime("%Y-%m-%d"),
            sales_count,
            f"₹{revenue:.2f}",
            f"₹{cost:.2f}",
            f"₹{profit:.2f}",
            f"{margin:.1f}%"
        )
        summary_tree.insert("", "end", values=values)
    
    # Summary stats
    stats_frame = tk.Frame(content_frame, bg='white')
    stats_frame.pack(fill="x", pady=(10,0))
    
    tk.Label(stats_frame, text=f"Total 7-Day Profit: ₹{total_profit:.2f}", 
             font=('Arial', 12, 'bold'), fg=SUCCESS_COLOR, bg='white').pack()
    tk.Label(stats_frame, text=f"Average Daily Profit: ₹{total_profit/7:.2f}", 
             font=('Arial', 10), fg=DARK_TEXT, bg='white').pack()
    
    # Close button
    ttk.Button(content_frame, text="Close", command=win.destroy).pack(pady=(10,0))


# Simple categories section
cat_title_frame = tk.Frame(cat_left, bg=CARD_BG)
cat_title_frame.pack(fill="x", padx=15, pady=(15,10))

cat_title = tk.Label(cat_title_frame, text="Product Categories", 
                    font=('Arial', 12, 'bold'), fg=PRIMARY_COLOR, bg=CARD_BG)
cat_title.pack(side="left")

# Simple categories tree
cat_tree_frame = tk.Frame(cat_left, bg=CARD_BG)
cat_tree_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))

cat_cols = ("ID", "Name", "Description", "Price (₹)")
cat_tree = ttk.Treeview(cat_tree_frame, columns=cat_cols, show="headings", height=12, style='Custom.Treeview')

# Configure column widths
cat_column_widths = {"ID": 60, "Name": 150, "Description": 250, "Price (₹)": 100}
for c in cat_cols:
    cat_tree.heading(c, text=c)
    cat_tree.column(c, anchor="w" if c == "Description" else "center", width=cat_column_widths.get(c, 150))

# Add scrollbars for categories
cat_v_scroll = ttk.Scrollbar(cat_tree_frame, orient="vertical", command=cat_tree.yview)
cat_h_scroll = ttk.Scrollbar(cat_tree_frame, orient="horizontal", command=cat_tree.xview)
cat_tree.configure(yscrollcommand=cat_v_scroll.set, xscrollcommand=cat_h_scroll.set)

cat_tree.pack(side="left", fill="both", expand=True)
cat_v_scroll.pack(side="right", fill="y")
cat_h_scroll.pack(side="bottom", fill="x")

def load_categories():
    for i in cat_tree.get_children():
        cat_tree.delete(i)
    for c in fetch_categories():
        cat_tree.insert("", "end", values=c)
    
    # Add alternating row colors
    for i, item in enumerate(cat_tree.get_children()):
        if i % 2 == 0:
            cat_tree.item(item, tags=("even",))
        else:
            cat_tree.item(item, tags=("odd",))
    
    cat_tree.tag_configure("even", background="#f8f9fa")
    cat_tree.tag_configure("odd", background="white")

# INVENTORY CONTROLS PANEL
inv_controls_title = tk.Label(inv_right, text="🔧 Inventory Controls", 
                             font=('Arial', 12, 'bold'), fg=PRIMARY_COLOR, bg='white')
inv_controls_title.pack(pady=(15,10))

# Simple Quick Stats
stats_frame = tk.LabelFrame(inv_right, text="Quick Stats", font=('Arial', 10, 'bold'), 
                           fg=PRIMARY_COLOR, bg=CARD_BG, bd=2, relief='groove')
stats_frame.pack(fill="x", padx=15, pady=10)

def update_stats():
    inventory = fetch_inventory()
    total_items = len(inventory)
    low_stock = sum(1 for item in inventory if float(item[2] or 0) <= float(item[4] or 0))
    out_of_stock = sum(1 for item in inventory if float(item[2] or 0) <= 0)
    
    for widget in stats_frame.winfo_children():
        widget.destroy()
    
    # Simple clean stats
    tk.Label(stats_frame, text=f"Total Items: {total_items}", bg=CARD_BG, font=('Arial', 9)).pack(anchor="w", padx=10, pady=2)
    tk.Label(stats_frame, text=f"Low Stock: {low_stock}", bg=CARD_BG, font=('Arial', 9), 
             fg=WARNING_COLOR if low_stock > 0 else 'black').pack(anchor="w", padx=10, pady=2)
    tk.Label(stats_frame, text=f"Out of Stock: {out_of_stock}", bg=CARD_BG, font=('Arial', 9), 
             fg=DANGER_COLOR if out_of_stock > 0 else 'black').pack(anchor="w", padx=10, pady=2)

# Simple Material Management
material_frame = tk.LabelFrame(inv_right, text="Material Management", font=('Arial', 10, 'bold'), 
                              fg=PRIMARY_COLOR, bg=CARD_BG, bd=2, relief='groove')
material_frame.pack(fill="x", padx=15, pady=10)

ttk.Button(material_frame, text="Add Material", command=lambda: add_material_popup(), 
          style='Success.TButton').pack(fill="x", padx=10, pady=5)
ttk.Button(material_frame, text="Edit Material", command=lambda: edit_material_popup(), 
          style='Primary.TButton').pack(fill="x", padx=10, pady=5)
ttk.Button(material_frame, text="Restock Material", command=lambda: restock_material_popup(), 
          style='Warning.TButton').pack(fill="x", padx=10, pady=5)
ttk.Button(material_frame, text="Delete Material", command=lambda: delete_material_popup(), 
          style='Danger.TButton').pack(fill="x", padx=10, pady=5)

# Simple Profit Tracking
profit_frame = tk.LabelFrame(inv_right, text="Profit Tracking", font=('Arial', 10, 'bold'), 
                            fg=SUCCESS_COLOR, bg=CARD_BG, bd=2, relief='groove')
profit_frame.pack(fill="x", padx=15, pady=10)

ttk.Button(profit_frame, text="Item Profitability", command=lambda: show_item_profitability(), 
          style='Success.TButton').pack(fill="x", padx=10, pady=5)
ttk.Button(profit_frame, text="Profit Summary", command=lambda: show_profit_summary(), 
          style='Primary.TButton').pack(fill="x", padx=10, pady=5)
ttk.Button(profit_frame, text="View Sales History", command=lambda: show_sales_history(), 
          style='Warning.TButton').pack(fill="x", padx=10, pady=5)

# Simple category controls
cat_controls_title = tk.Label(cat_right, text="Category Controls", 
                             font=('Arial', 12, 'bold'), fg=PRIMARY_COLOR, bg=CARD_BG)
cat_controls_title.pack(pady=(15,10))

# Right: Controls
def add_category_popup():
    win = tk.Toplevel(root)
    win.title("➕ Add New Category")
    win.geometry("450x320")
    win.configure(bg='white')
    win.resizable(False, False)
    
    # Center the window
    win.transient(root)
    win.grab_set()
    
    # Header
    header = tk.Frame(win, bg=SECONDARY_COLOR, height=50)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="➕ Create New Category", font=('Arial', 14, 'bold'), 
             fg='white', bg=SECONDARY_COLOR).pack(pady=15)
    
    # Form frame
    form_frame = tk.Frame(win, bg='white')
    form_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    tk.Label(form_frame, text="Category Name *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=0, column=0, sticky="w", pady=(0,5))
    e_name = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_name.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,15))
    
    tk.Label(form_frame, text="Description", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=2, column=0, sticky="w", pady=(0,5))
    e_desc = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_desc.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0,15))
    
    tk.Label(form_frame, text="Selling Price (₹) *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=4, column=0, sticky="w", pady=(0,5))
    e_price = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_price.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0,20))
    
    form_frame.columnconfigure(0, weight=1)
    
    def save():
        name = e_name.get().strip()
        desc = e_desc.get().strip()
        price_str = e_price.get().strip()
        
        if not name:
            messagebox.showerror("❌ Error", "Category name is required!")
            return
        
        if not price_str:
            messagebox.showerror("❌ Error", "Selling price is required!")
            return
        
        try:
            selling_price = float(price_str)
            if selling_price <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter a valid selling price!")
            return
        
        ok, res = create_category(name, desc, selling_price)
        if ok:
            messagebox.showinfo("✅ Success", f"Category '{name}' created successfully with price ₹{selling_price}!")
            load_categories()
            win.destroy()
        else:
            messagebox.showerror("❌ Error", res)
    
    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
    
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="✅ Save Category", command=save, style='Success.TButton').pack(side="left")
    
    e_name.focus_set()

def edit_category_popup():
    sel = cat_tree.selection()
    if not sel:
        messagebox.showerror("❌ Error", "Please select a category to edit!")
        return
    
    # Get current category data
    cat_id = cat_tree.item(sel[0])['values'][0]
    cat_name = cat_tree.item(sel[0])['values'][1]
    cat_desc = cat_tree.item(sel[0])['values'][2]
    cat_price = cat_tree.item(sel[0])['values'][3]
    
    win = tk.Toplevel(root)
    win.title("✏️ Edit Category")
    win.geometry("450x320")
    win.configure(bg='white')
    win.resizable(False, False)
    
    # Center the window
    win.transient(root)
    win.grab_set()
    
    # Header
    header = tk.Frame(win, bg=SECONDARY_COLOR, height=50)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="✏️ Edit Category", font=('Arial', 14, 'bold'), 
             fg='white', bg=SECONDARY_COLOR).pack(pady=15)
    
    # Form frame
    form_frame = tk.Frame(win, bg='white')
    form_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    tk.Label(form_frame, text="Category Name *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=0, column=0, sticky="w", pady=(0,5))
    e_name = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_name.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,15))
    e_name.insert(0, cat_name)
    
    tk.Label(form_frame, text="Description", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=2, column=0, sticky="w", pady=(0,5))
    e_desc = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_desc.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0,15))
    e_desc.insert(0, cat_desc)
    
    tk.Label(form_frame, text="Selling Price (₹) *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=4, column=0, sticky="w", pady=(0,5))
    e_price = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_price.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0,20))
    e_price.insert(0, str(cat_price))
    
    form_frame.columnconfigure(0, weight=1)
    
    def update():
        name = e_name.get().strip()
        desc = e_desc.get().strip()
        price_str = e_price.get().strip()
        
        if not name:
            messagebox.showerror("❌ Error", "Category name is required!")
            return
        
        if not price_str:
            messagebox.showerror("❌ Error", "Selling price is required!")
            return
        
        try:
            selling_price = float(price_str)
            if selling_price <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter a valid selling price!")
            return
        
        ok, res = update_category(cat_id, name, desc, selling_price)
        if ok:
            messagebox.showinfo("✅ Success", f"Category '{name}' updated successfully!")
            load_categories()
            win.destroy()
        else:
            messagebox.showerror("❌ Error", res)
    
    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
    
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="✅ Update Category", command=update, style='Warning.TButton').pack(side="left")
    
    e_name.focus_set()

def delete_category_confirm():
    sel = cat_tree.selection()
    if not sel:
        messagebox.showerror("❌ Error", "Please select a category to delete!")
        return
    
    cat_id = cat_tree.item(sel[0])['values'][0]
    cat_name = cat_tree.item(sel[0])['values'][1]
    
    # Confirm deletion
    result = messagebox.askyesno("⚠️ Confirm Delete", 
                                f"Are you sure you want to delete category '{cat_name}'?\n\n"
                                "This will also remove all material mappings for this category.\n"
                                "This action cannot be undone!")
    
    if result:
        ok, res = delete_category(cat_id)
        if ok:
            messagebox.showinfo("✅ Success", f"Category '{cat_name}' deleted successfully!")
            load_categories()
        else:
            messagebox.showerror("❌ Error", f"Failed to delete category: {res}")

def map_material_popup():
    sel = cat_tree.selection()
    if not sel:
        messagebox.showerror("❌ Error", "Please select a category first!")
        return
    cat_id = cat_tree.item(sel[0])['values'][0]
    cat_name = cat_tree.item(sel[0])['values'][1]
    
    win = tk.Toplevel(root)
    win.title("🔗 Map Material to Category")
    win.geometry("600x320")
    win.configure(bg='white')
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    # Header
    header = tk.Frame(win, bg=SECONDARY_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text=f"🔗 Map Material to '{cat_name}'", font=('Arial', 14, 'bold'), 
             fg='white', bg=SECONDARY_COLOR).pack(pady=20)
    
    # Form frame
    form_frame = tk.Frame(win, bg='white')
    form_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    tk.Label(form_frame, text="Select Material *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=0, column=0, sticky="w", pady=(0,5))
    
    # Get all materials for dropdown
    materials = fetch_inventory()
    material_options = []
    material_map = {}  # To map display text to material ID
    
    if not materials:
        tk.Label(form_frame, text="⚠️ No materials available. Please add materials to inventory first.", 
                font=('Arial', 10), fg='red', bg='white').grid(row=1, column=0, columnspan=2, pady=20)
        ttk.Button(form_frame, text="Close", command=win.destroy).grid(row=2, column=0, columnspan=2, pady=10)
        return
    
    for material in materials:
        # material = (id, name, quantity, unit, threshold, cost_per_unit, supplier_id)
        display_text = f"{material[1]} - {material[2]} {material[3]} available (₹{material[5]}/unit)"
        material_options.append(display_text)
        material_map[display_text] = material[0]
    
    material_combo = ttk.Combobox(form_frame, values=material_options, width=50, font=('Arial', 10), state="readonly")
    material_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,5))
    
    # Add helpful instruction
    tk.Label(form_frame, text="💡 Choose the raw material used in this category", 
             font=('Arial', 9), fg='gray', bg='white').grid(row=2, column=0, columnspan=2, sticky="w", pady=(0,15))
    
    tk.Label(form_frame, text="Amount used per unit *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=3, column=0, sticky="w", pady=(0,5))
    e_amt = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_amt.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0,5))
    
    # Add helpful instruction for amount
    tk.Label(form_frame, text="💡 Example: If 1 burger uses 0.2 kg of flour, enter 0.2", 
             font=('Arial', 9), fg='gray', bg='white').grid(row=5, column=0, columnspan=2, sticky="w", pady=(0,20))
    
    form_frame.columnconfigure(0, weight=1)
    
    def save_map():
        selected_material = material_combo.get()
        if not selected_material:
            messagebox.showerror("❌ Error", "Please select a material!")
            return
        
        try:
            mid = material_map[selected_material]
            amt = float(e_amt.get())
            if amt <= 0:
                raise ValueError("Amount must be positive")
        except ValueError as e:
            if "Amount must be positive" in str(e):
                messagebox.showerror("❌ Error", "Amount per unit must be greater than 0!")
            else:
                messagebox.showerror("❌ Error", "Please enter a valid amount!")
            return
        except Exception:
            messagebox.showerror("❌ Error", "Please enter valid values!")
            return
        
        ok, err = set_category_material(cat_id, mid, amt)
        if ok:
            material_name = selected_material.split(' - ')[0]
            messagebox.showinfo("✅ Success", f"Material mapping saved successfully!\n\nCategory: {cat_name}\nMaterial: {material_name}\nAmount per unit: {amt}")
            win.destroy()
        else:
            messagebox.showerror("❌ Error", err)
    
    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
    
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="✅ Save Mapping", command=save_map, style='Success.TButton').pack(side="left")
    
    material_combo.focus_set()

def view_category_materials():
    sel = cat_tree.selection()
    if not sel:
        messagebox.showerror("❌ Error", "Please select a category first!")
        return
    cat_id = cat_tree.item(sel[0])['values'][0]
    cat_name = cat_tree.item(sel[0])['values'][1]
    
    win = tk.Toplevel(root)
    win.title(f"👁️ Materials in '{cat_name}'")
    win.geometry("800x500")
    win.configure(bg='white')
    win.transient(root)
    
    # Header
    header = tk.Frame(win, bg=SECONDARY_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text=f"👁️ Materials in Category '{cat_name}'", font=('Arial', 14, 'bold'), 
             fg='white', bg=SECONDARY_COLOR).pack(pady=20)
    
    # Content frame
    content_frame = tk.Frame(win, bg='white')
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    rows = get_category_materials(cat_id)
    
    if not rows:
        tk.Label(content_frame, text="📭 No materials mapped to this category yet.", 
                font=('Arial', 12), fg=DARK_TEXT, bg='white').pack(expand=True)
        ttk.Button(content_frame, text="Close", command=win.destroy).pack(pady=20)
        return
    
    # Create treeview for materials
    mat_cols = ("ID", "Name", "Amount/Unit", "Current Stock", "Unit", "Threshold", "Supplier")
    mat_tree = ttk.Treeview(content_frame, columns=mat_cols, show="headings", height=15, style='Custom.Treeview')
    
    for c in mat_cols:
        mat_tree.heading(c, text=c)
        mat_tree.column(c, anchor="center", width=100)
    
    # Add scrollbar
    mat_scroll = ttk.Scrollbar(content_frame, orient="vertical", command=mat_tree.yview)
    mat_tree.configure(yscrollcommand=mat_scroll.set)
    
    mat_tree.pack(side="left", fill="both", expand=True)
    mat_scroll.pack(side="right", fill="y")
    
    # Populate data
    for r in rows:
        values = (r[0], r[1], r[2], r[3], r[4], r[5], r[6] or "Not assigned")
        mat_tree.insert("", "end", values=values)
    
    # Close button
    ttk.Button(content_frame, text="Close", command=win.destroy).pack(pady=(10,0))

# Sale popup and deduction logic
def sale_popup():
    sel = cat_tree.selection()
    if not sel:
        messagebox.showerror("❌ Error", "Please select a category first!")
        return
    cat_id = cat_tree.item(sel[0])['values'][0]
    cat_name = cat_tree.item(sel[0])['values'][1]

    win = tk.Toplevel(root)
    win.title(f"🛒 Record Sale - {cat_name}")
    
    # Make window larger to accommodate customer details and brand selection
    if cat_name.lower() == "cold drinks":
        win.geometry("450x450")
    else:
        win.geometry("450x350")
        
    win.configure(bg='white')
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    
    # Header
    header = tk.Frame(win, bg=WARNING_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text=f"🛒 Record Sale - {cat_name}", font=('Arial', 14, 'bold'), 
             fg='white', bg=WARNING_COLOR).pack(pady=20)
    
    # Form frame
    form_frame = tk.Frame(win, bg='white')
    form_frame.pack(fill="both", expand=True, padx=30, pady=20)
    
    current_row = 0
    
    # Brand selection for cold drinks
    brand_combo = None
    if cat_name.lower() == "cold drinks":
        tk.Label(form_frame, text="Select Brand *", font=('Arial', 10, 'bold'), 
                 fg=DARK_TEXT, bg='white').grid(row=current_row, column=0, sticky="w", pady=(0,5))
        current_row += 1
        
        # Get available cold drink brands from inventory
        cold_drink_brands = []
        try:
            conn = get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT name, quantity, unit FROM raw_materials 
                    WHERE name IN ('Coca Cola', 'Pepsi', 'Sprite', 'Fanta', 'Thumbs Up', 'Limca')
                    ORDER BY name
                """)
                brands = cur.fetchall()
                conn.close()
                
                for brand_name, qty, unit in brands:
                    qty = float(qty)
                    if qty > 0:
                        cold_drink_brands.append(f"{brand_name} (Stock: {qty} {unit})")
                    else:
                        cold_drink_brands.append(f"{brand_name} (Out of Stock)")
        except Exception as e:
            cold_drink_brands = ["Coca Cola", "Pepsi", "Sprite", "Fanta", "Thumbs Up", "Limca"]
        
        brand_combo = ttk.Combobox(form_frame, values=cold_drink_brands, state="readonly", 
                                  width=32, font=('Arial', 10))
        brand_combo.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(0,15))
        current_row += 1
    
    tk.Label(form_frame, text="Customer Name (optional)", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=current_row, column=0, sticky="w", pady=(0,5))
    current_row += 1
    e_customer = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_customer.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(0,15))
    current_row += 1
    
    tk.Label(form_frame, text="Customer Phone (optional)", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=current_row, column=0, sticky="w", pady=(0,5))
    current_row += 1
    e_phone = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_phone.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(0,5))
    current_row += 1
    
    # Add phone format instruction
    tk.Label(form_frame, text="💡 Enter 10-digit number (e.g., 9876543210) for WhatsApp bill", 
             font=('Arial', 9), fg='gray', bg='white').grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(0,15))
    current_row += 1
    
    tk.Label(form_frame, text="Quantity Sold *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=current_row, column=0, sticky="w", pady=(0,5))
    current_row += 1
    e_qty = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_qty.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(0,20))
    current_row += 1
    
    form_frame.columnconfigure(0, weight=1)

    def process_sale():
        try:
            qty_sold = float(e_qty.get())
            if qty_sold <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Error", "Enter valid positive quantity")
            return

        # Special handling for cold drinks
        if cat_name.lower() == "cold drinks":
            if not brand_combo or not brand_combo.get():
                messagebox.showerror("Error", "Please select a brand!")
                return
            
            # Extract brand name from selection (remove stock info)
            selected_brand = brand_combo.get().split(" (Stock:")[0].split(" (Out of Stock)")[0]
            
            # Check if brand is out of stock
            if "Out of Stock" in brand_combo.get():
                messagebox.showerror("Error", f"{selected_brand} is out of stock!")
                return
            
            # For cold drinks, directly deduct from the selected brand's inventory
            conn = get_connection()
            if not conn:
                messagebox.showerror("Error", "DB connection failed")
                return
            
            try:
                cur = conn.cursor()
                # Get current stock of selected brand
                cur.execute("SELECT quantity FROM raw_materials WHERE name = %s FOR UPDATE", (selected_brand,))
                result = cur.fetchone()
                
                if not result:
                    conn.rollback()
                    conn.close()
                    messagebox.showerror("Error", f"{selected_brand} not found in inventory")
                    return
                
                current_stock = float(result[0])
                if current_stock < qty_sold:
                    conn.rollback()
                    conn.close()
                    messagebox.showerror("Error", f"Not enough {selected_brand} in stock! Available: {current_stock}")
                    return
                
                # Deduct the stock
                new_stock = current_stock - qty_sold
                cur.execute("UPDATE raw_materials SET quantity = %s, last_updated = NOW() WHERE name = %s", 
                           (new_stock, selected_brand))
                
                # Get selling price for cold drinks
                cur.execute("SELECT selling_price FROM categories WHERE id = %s", (cat_id,))
                price_row = cur.fetchone()
                selling_price = float(price_row[0]) if price_row and price_row[0] else 25.0  # Default price for cold drinks
                
                # Calculate profit for cold drinks (cost is the material cost)
                cur.execute("SELECT cost_per_unit FROM raw_materials WHERE name = %s", (selected_brand,))
                cost_row = cur.fetchone()
                material_cost = float(cost_row[0]) if cost_row and cost_row[0] else 0.0
                
                conn.commit()
                conn.close()
                
                profit_per_unit = selling_price - material_cost
                total_profit = profit_per_unit * qty_sold
                profit_margin = (profit_per_unit / selling_price * 100) if selling_price > 0 else 0
                
                profit_msg = f"""Sale recorded successfully! 

📊 PROFIT ANALYSIS:
• Units Sold: {qty_sold}
• Selling Price: ₹{selling_price} per unit
• Material Cost: ₹{material_cost:.2f} per unit
• Profit per Unit: ₹{profit_per_unit:.2f}
• Total Profit: ₹{total_profit:.2f}
• Profit Margin: {profit_margin:.1f}%"""
                
                # Generate bill for cold drinks
                customer_name = e_customer.get().strip()
                customer_phone = e_phone.get().strip()
                items = [(f"{selected_brand} ({cat_name})", qty_sold, selling_price)]
                bill_text, total_amount = generate_bill_text(items, customer_name, customer_phone)
                
                # Show bill and offer WhatsApp sending
                show_bill_popup(bill_text, customer_phone, f"{selected_brand} sale", profit_msg)
                
                load_inventory()
                update_stats()
                win.destroy()
                return
                
            except Exception as e:
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
                messagebox.showerror("Error", f"Failed to process sale: {e}")
                return

        # Regular processing for non-cold drinks
        mats = get_category_materials(cat_id)
        if not mats:
            messagebox.showerror("Error", "No materials mapped to this category")
            return

        deductions = []
        for mat in mats:
            mid, name, per_unit, stock, unit, threshold, supplier_id = mat
            total_needed = float(per_unit) * qty_sold
            deductions.append({
                "material_id": mid,
                "name": name,
                "total_needed": total_needed,
                "unit": unit,
                "threshold": threshold,
                "stock": stock,
                "supplier_id": supplier_id
            })

        # Apply deductions in a transaction
        conn = get_connection()
        if not conn:
            messagebox.showerror("Error", "DB connection failed")
            return
        try:
            cur = conn.cursor()
            low_items = []
            for d in deductions:
                cur.execute("SELECT quantity, threshold FROM raw_materials WHERE id = %s FOR UPDATE", (d["material_id"],))
                row = cur.fetchone()
                if not row:
                    conn.rollback()
                    conn.close()
                    messagebox.showerror("Error", f"Material id {d['material_id']} not found")
                    return
                current_q = float(row[0])
                new_q = current_q - d["total_needed"]
                if new_q < 0:
                    new_q = 0.0
                cur.execute("UPDATE raw_materials SET quantity=%s, last_updated=NOW() WHERE id=%s", (new_q, d["material_id"]))
                if new_q < float(d["threshold"]):
                    low_items.append({
                        "material_id": d["material_id"],
                        "name": d["name"],
                        "new_q": new_q,
                        "unit": d["unit"],
                        "threshold": d["threshold"],
                        "supplier_id": d["supplier_id"]
                    })
            conn.commit()
            conn.close()
        except Exception as ex:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            messagebox.showerror("Error", f"Failed to record sale: {ex}")
            return

        # Calculate and record profit
        # cat_id is already available from the parent scope
        
        # Get selling price from categories table
        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT selling_price FROM categories WHERE id = %s", (cat_id,))
                price_row = cur.fetchone()
                selling_price = float(price_row[0]) if price_row else 0.0
                conn.close()
                
                # Record sale with profit calculation
                ok, profit_info = record_sale_with_profit(cat_id, qty_sold, selling_price)
                
                # Generate bill
                customer_name = e_customer.get().strip()
                customer_phone = e_phone.get().strip()
                items = [(cat_name, qty_sold, selling_price)]
                bill_text, total_amount = generate_bill_text(items, customer_name, customer_phone)
                
                if ok:
                    profit_msg = f"""Sale recorded successfully! 

📊 PROFIT ANALYSIS:
• Units Sold: {qty_sold}
• Selling Price: ₹{selling_price} per unit
• Material Cost: ₹{profit_info['material_cost']:.2f} per unit
• Profit per Unit: ₹{profit_info['profit_per_unit']:.2f}
• Total Profit: ₹{profit_info['total_profit']:.2f}
• Profit Margin: {profit_info['profit_margin']:.1f}%"""
                    
                    # Show bill popup
                    show_bill_popup(bill_text, customer_phone, f"{cat_name} sale", profit_msg)
            except Exception as e:
                messagebox.showinfo("✅ Success", f"Sale recorded successfully! Deducted materials for {qty_sold} units.")
        else:
            messagebox.showinfo("✅ Success", f"Sale recorded successfully! Deducted materials for {qty_sold} units.")
        
        load_inventory()
        update_stats()
        win.destroy()

        # For each low item, notify associated supplier (auto-select) via popup (edit allowed)
        for li in low_items:
            supplier = None
            if li["supplier_id"]:
                supplier = get_supplier_by_id(li["supplier_id"])
            # if there is no supplier assigned, choose first supplier in supplier list if any
            if not supplier:
                suppliers = fetch_suppliers(limit=3)
                supplier = suppliers[0] if suppliers else None

            show_supplier_notify_popup(li, supplier)

    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=current_row, column=0, columnspan=2, pady=10)
    
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="🛒 Confirm Sale", command=process_sale, style='Warning.TButton').pack(side="left")
    
    e_qty.focus_set()

def show_bill_popup(bill_text, customer_phone="", sale_type="", profit_msg=""):
    """Show bill popup with e-bill option"""
    win = tk.Toplevel(root)
    win.title("🧾 Bill Generated")
    win.geometry("500x600")
    win.configure(bg='white')
    win.resizable(True, True)
    win.transient(root)
    
    # Header
    header = tk.Frame(win, bg=SUCCESS_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="🧾 Bill Generated Successfully", font=('Arial', 14, 'bold'), 
             fg='white', bg=SUCCESS_COLOR).pack(pady=20)
    
    # Main frame
    main_frame = tk.Frame(win, bg='white')
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Bill Details Label
    tk.Label(main_frame, text="📄 Bill Details:", font=('Arial', 12, 'bold'), 
             fg=DARK_TEXT, bg='white').pack(anchor="w", pady=(0,10))
    
    # Bill text area with border
    bill_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
    bill_frame.pack(fill="both", expand=True, pady=(0,20))
    
    bill_display = tk.Text(bill_frame, font=('Courier', 10), bg='#f8f9fa', 
                          relief='flat', wrap='word', height=12)
    bill_display.pack(fill="both", expand=True, padx=10, pady=10)
    bill_display.insert('1.0', bill_text)
    bill_display.config(state='disabled')
    
    # Choose Action Label
    tk.Label(main_frame, text="📋 Choose Action:", font=('Arial', 12, 'bold'), 
             fg=DARK_TEXT, bg='white').pack(anchor="w", pady=(10,10))
    
    # Action buttons frame with border
    action_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
    action_frame.pack(fill="x", pady=(0,20))
    
    btn_container = tk.Frame(action_frame, bg='white')
    btn_container.pack(pady=15, padx=15)
    
    # Print Bill button
    print_btn = tk.Button(btn_container, text="🖨️ Print Bill", 
                         font=('Arial', 10, 'bold'), bg='#3498db', fg='white',
                         relief='flat', padx=20, pady=8, cursor='hand2',
                         command=lambda: print_bill_text(bill_text))
    print_btn.pack(side="left", padx=(0,10))
    
    # Send E-Bill button
    def send_ebill():
        if not customer_phone or not customer_phone.strip():
            messagebox.showerror("❌ Error", "No customer phone number provided!\nCannot send E-Bill without phone number.")
            return
        
        try:
            # Format phone number for WhatsApp
            phone = customer_phone.strip()
            
            # Add +91 if not present and number is 10 digits
            if not phone.startswith('+'):
                if len(phone) == 10 and phone.isdigit():
                    phone = '+91' + phone
                elif not phone.startswith('91') and len(phone) == 10:
                    phone = '+91' + phone
                elif phone.startswith('91') and len(phone) == 12:
                    phone = '+' + phone
                else:
                    phone = '+91' + phone.lstrip('0')
            
            # Format message for WhatsApp
            whatsapp_msg = f"🧾 *Your Bill from Canteen*\n\n{bill_text}\n\nThank you for your purchase! 😊"
            
            if TWILIO_ENABLED:
                success, result = send_whatsapp_twilio(phone, whatsapp_msg)
                if success:
                    messagebox.showinfo("✅ E-Bill Sent!", 
                                      f"E-Bill sent successfully via WhatsApp!\n\n"
                                      f"📞 To: {phone}\n"
                                      f"📧 Message ID: {result}")
                else:
                    messagebox.showerror("❌ Send Failed", f"Failed to send E-Bill via Twilio:\n{result}")
            else:
                # Open WhatsApp Web as fallback
                success, url = open_whatsapp_web(phone, whatsapp_msg)
                if success:
                    messagebox.showinfo("📱 WhatsApp Opened", 
                                      f"WhatsApp Web opened with E-Bill!\n\n"
                                      f"📞 To: {phone}\n\n"
                                      f"Please click 'Send' in WhatsApp to deliver the E-Bill.")
                else:
                    messagebox.showerror("❌ Error", "Failed to open WhatsApp Web")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to send E-Bill: {e}")
    
    if customer_phone and customer_phone.strip():
        ebill_btn = tk.Button(btn_container, text="📱 Send E-Bill to Customer", 
                             font=('Arial', 10, 'bold'), bg='#27ae60', fg='white',
                             relief='flat', padx=20, pady=8, cursor='hand2',
                             command=send_ebill)
        ebill_btn.pack(side="left", padx=(0,10))
    else:
        # Disabled button with explanation
        disabled_btn = tk.Button(btn_container, text="📱 Send E-Bill (No Phone)", 
                               font=('Arial', 10), bg='#bdc3c7', fg='#7f8c8d',
                               relief='flat', padx=20, pady=8, state='disabled')
        disabled_btn.pack(side="left", padx=(0,10))
    
    # View Profit button
    def show_profit_analysis():
        if profit_msg:
            show_profit_popup(profit_msg, sale_type)
        else:
            messagebox.showinfo("ℹ️ Info", "No profit analysis available for this sale.")
    
    profit_btn = tk.Button(btn_container, text="📊 View Profit", 
                          font=('Arial', 10, 'bold'), bg='#f39c12', fg='white',
                          relief='flat', padx=20, pady=8, cursor='hand2',
                          command=show_profit_analysis)
    profit_btn.pack(side="left")
    


def print_bill_text(bill_text):
    """Direct print function - prints immediately to default printer"""
    try:
        import win32print
        import win32api
        import tempfile
        import os
        
        # Get default printer
        default_printer = win32print.GetDefaultPrinter()
        
        if not default_printer:
            messagebox.showerror("❌ No Printer", "No default printer found!\nPlease set up a printer first.")
            return
        
        # Create temporary file for printing
        try:
            # Try UTF-8 first
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(bill_text)
                temp_file = f.name
        except UnicodeEncodeError:
            # Fallback to ASCII-safe version
            safe_bill_text = bill_text.replace('₹', 'Rs.').replace('🧾', '').replace('📅', '').replace('👤', '').replace('📱', '').replace('💰', '')
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='ascii', errors='ignore') as f:
                f.write(safe_bill_text)
                temp_file = f.name
        
        # Print directly to printer
        win32api.ShellExecute(0, "print", temp_file, None, ".", 0)
        
        # Clean up temp file after a short delay
        import threading
        def cleanup():
            import time
            time.sleep(3)  # Wait 3 seconds for printing to start
            try:
                os.unlink(temp_file)
            except:
                pass
        
        threading.Thread(target=cleanup, daemon=True).start()
        
        messagebox.showinfo("🖨️ Printing...", 
                          f"✅ Bill sent to printer: {default_printer}\n\n"
                          f"📄 Printing in progress...\n"
                          f"Please wait for the bill to print!")
        
    except ImportError:
        # Fallback if win32print not available - use notepad method
        try:
            import tempfile
            import os
            
            # Create temp file
            safe_bill_text = bill_text.replace('₹', 'Rs.')
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8', errors='ignore') as f:
                f.write(safe_bill_text)
                temp_file = f.name
            
            # Open and auto-print via notepad
            os.system(f'notepad /p "{temp_file}"')
            
            messagebox.showinfo("🖨️ Print Dialog", 
                              "Print dialog opened!\n\n"
                              "✅ Select your printer\n"
                              "✅ Click Print")
        except Exception as e:
            messagebox.showerror("❌ Print Error", f"Could not print: {e}")
    
    except Exception as e:
        messagebox.showerror("❌ Print Error", f"Printing failed: {e}\n\nPlease check if printer is connected and try again.")

def removed_pdf_function():
    """Generate PDF bill using reportlab or fallback methods"""
    try:
        # Try using reportlab for professional PDF
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Create filename with timestamp
        timestamp = int(time.time())
        filename = f"canteen_bill_{timestamp}.pdf"
        
        # Try to save in Documents folder, fallback to current directory
        try:
            import os
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            if not os.path.exists(documents_path):
                documents_path = os.getcwd()
            pdf_path = os.path.join(documents_path, filename)
        except:
            pdf_path = filename
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        bill_style = ParagraphStyle(
            'BillText',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Courier',
            spaceAfter=12,
            leftIndent=20,
            rightIndent=20
        )
        
        # Build PDF content
        story = []
        
        # Title
        story.append(Paragraph("🧾 CANTEEN BILL RECEIPT", title_style))
        story.append(Spacer(1, 12))
        
        # Bill content - convert to HTML-safe format
        bill_lines = bill_text.split('\n')
        for line in bill_lines:
            # Replace special characters for HTML
            safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(safe_line, bill_style))
        
        # Build PDF
        doc.build(story)
        
        return pdf_path
        
    except ImportError:
        # Reportlab not available, try alternative method
        return generate_simple_pdf(bill_text, customer_phone)
    except Exception as e:
        print(f"PDF generation error: {e}")
        return None

def generate_simple_pdf(bill_text, customer_phone=""):
    """Simple PDF generation using built-in libraries"""
    try:
        # Try using weasyprint or other alternatives
        # For now, create an HTML file and suggest conversion
        timestamp = int(time.time())
        html_filename = f"canteen_bill_{timestamp}.html"
        
        # Try to save in Documents folder
        try:
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            if not os.path.exists(documents_path):
                documents_path = os.getcwd()
            html_path = os.path.join(documents_path, html_filename)
        except:
            html_path = html_filename
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Canteen Bill</title>
            <style>
                body {{ font-family: 'Courier New', monospace; margin: 40px; }}
                .bill {{ background: white; padding: 20px; border: 1px solid #ccc; }}
                .header {{ text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 20px; }}
                .content {{ white-space: pre-line; line-height: 1.4; }}
                @media print {{ body {{ margin: 0; }} .bill {{ border: none; }} }}
            </style>
        </head>
        <body>
            <div class="bill">
                <div class="header">🧾 CANTEEN BILL RECEIPT</div>
                <div class="content">{bill_text}</div>
            </div>
            <script>
                // Auto-print when opened
                window.onload = function() {{
                    if (confirm('Would you like to print this bill now?')) {{
                        window.print();
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        # Write HTML file
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
        
    except Exception as e:
        print(f"Simple PDF generation error: {e}")
        return None

# Printable bill function removed - using e-bill only
def removed_printable_function():
    """Show bill in a separate window for easy copying and printing"""
    win = tk.Toplevel(root)
    win.title("🖨️ Printable Bill")
    win.geometry("600x500")
    win.configure(bg='white')
    win.resizable(True, True)
    win.transient(root)
    
    # Header
    header = tk.Frame(win, bg=PRIMARY_COLOR, height=50)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="🖨️ Bill Ready for Printing", font=('Arial', 14, 'bold'), 
             fg='white', bg=PRIMARY_COLOR).pack(pady=15)
    
    # Instructions
    inst_frame = tk.Frame(win, bg='#f0f8ff')
    inst_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(inst_frame, text="📋 Instructions: Select all text (Ctrl+A), Copy (Ctrl+C), then paste in any text editor and print (Ctrl+P)", 
             font=('Arial', 10), bg='#f0f8ff', fg='#333', wraplength=550).pack(pady=8)
    
    # Bill text area
    text_frame = tk.Frame(win, bg='white')
    text_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Text widget with scrollbar
    text_widget = tk.Text(text_frame, font=('Courier', 10), bg='white', 
                         relief='solid', bd=1, wrap='none')
    scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)
    
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Insert bill text
    text_widget.insert('1.0', bill_text)
    text_widget.focus_set()
    text_widget.select_range('1.0', 'end')  # Select all text
    
    # Buttons
    btn_frame = tk.Frame(win, bg='white')
    btn_frame.pack(fill="x", padx=10, pady=10)
    
    def copy_and_close():
        try:
            root.clipboard_clear()
            root.clipboard_append(bill_text)
            messagebox.showinfo("✅ Copied", "Bill copied to clipboard! You can now paste and print.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to copy: {e}")
    
    ttk.Button(btn_frame, text="📋 Copy & Close", command=copy_and_close, 
              style='Success.TButton').pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="✅ Close", command=win.destroy).pack(side="right")

def show_profit_popup(profit_msg, sale_type=""):
    """Show profit analysis in separate popup"""
    win = tk.Toplevel(root)
    win.title("📊 Profit Analysis")
    win.geometry("500x400")
    win.configure(bg='white')
    win.resizable(True, True)
    win.transient(root)
    
    # Header
    header = tk.Frame(win, bg=WARNING_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="📊 Profit Analysis Report", font=('Arial', 14, 'bold'), 
             fg='white', bg=WARNING_COLOR).pack(pady=20)
    
    # Main frame
    main_frame = tk.Frame(win, bg='white')
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Sale info
    if sale_type:
        tk.Label(main_frame, text=f"Sale Type: {sale_type}", font=('Arial', 11, 'bold'), 
                 fg=DARK_TEXT, bg='white').pack(anchor="w", pady=(0,10))
    
    # Profit analysis display
    profit_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
    profit_frame.pack(fill="both", expand=True, pady=(0,20))
    
    profit_display = tk.Text(profit_frame, font=('Arial', 11), bg='#f0f8f0', 
                           relief='flat', wrap='word')
    profit_display.pack(fill="both", expand=True, padx=15, pady=15)
    profit_display.insert('1.0', profit_msg)
    profit_display.config(state='disabled')
    
    # Buttons
    btn_frame = tk.Frame(main_frame, bg='white')
    btn_frame.pack(fill="x")
    
    ttk.Button(btn_frame, text="📋 Copy Analysis", 
              command=lambda: copy_to_clipboard(profit_msg)).pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="✅ Close", command=win.destroy).pack(side="right")

def copy_to_clipboard(text):
    """Copy text to clipboard"""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        messagebox.showinfo("✅ Copied", "Text copied to clipboard!")
    except Exception as e:
        messagebox.showerror("❌ Error", f"Failed to copy: {e}")

def show_production_prediction():
    """Show tomorrow's production prediction popup"""
    win = tk.Toplevel(root)
    win.title("📊 Tomorrow's Production Prediction")
    win.geometry("800x600")
    win.configure(bg='white')
    win.resizable(True, True)
    win.transient(root)
    
    # Header
    header = tk.Frame(win, bg=PRIMARY_COLOR, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="📊 Tomorrow's Production Prediction", font=('Arial', 14, 'bold'), 
             fg='white', bg=PRIMARY_COLOR).pack(pady=20)
    
    # Main frame
    main_frame = tk.Frame(win, bg='white')
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Instructions
    tk.Label(main_frame, text="📈 Based on current inventory levels and material requirements:", 
             font=('Arial', 12), fg=DARK_TEXT, bg='white').pack(anchor="w", pady=(0,15))
    
    # Prediction table
    pred_frame = tk.Frame(main_frame, bg='white')
    pred_frame.pack(fill="both", expand=True)
    
    # Table headers
    pred_cols = ("Category", "Max Units", "Limiting Factor")
    pred_tree = ttk.Treeview(pred_frame, columns=pred_cols, show="headings", height=15, style='Custom.Treeview')
    
    # Configure columns
    pred_tree.heading("Category", text="📋 Category")
    pred_tree.heading("Max Units", text="🔢 Max Units Tomorrow")
    pred_tree.heading("Limiting Factor", text="⚠️ Limiting Factor")
    
    pred_tree.column("Category", width=200, anchor="w")
    pred_tree.column("Max Units", width=150, anchor="center")
    pred_tree.column("Limiting Factor", width=400, anchor="w")
    
    # Add scrollbars
    pred_v_scroll = ttk.Scrollbar(pred_frame, orient="vertical", command=pred_tree.yview)
    pred_h_scroll = ttk.Scrollbar(pred_frame, orient="horizontal", command=pred_tree.xview)
    pred_tree.configure(yscrollcommand=pred_v_scroll.set, xscrollcommand=pred_h_scroll.set)
    
    pred_tree.pack(side="left", fill="both", expand=True)
    pred_v_scroll.pack(side="right", fill="y")
    pred_h_scroll.pack(side="bottom", fill="x")
    
    # Load predictions
    predictions = predict_tomorrow_production()
    
    total_possible = 0
    for category_name, max_units, limiting_factor in predictions:
        if max_units > 0:
            total_possible += max_units
            tag = "can_produce"
        else:
            tag = "cannot_produce"
        
        pred_tree.insert("", "end", values=(category_name, max_units, limiting_factor), tags=(tag,))
    
    # Configure tags for color coding
    pred_tree.tag_configure("can_produce", background="#e8f5e8")
    pred_tree.tag_configure("cannot_produce", background="#ffe8e8")
    
    # Summary
    summary_frame = tk.Frame(main_frame, bg='white')
    summary_frame.pack(fill="x", pady=(20,0))
    
    tk.Label(summary_frame, text=f"📊 Summary: {len([p for p in predictions if p[1] > 0])} categories can be produced tomorrow", 
             font=('Arial', 12, 'bold'), fg=SUCCESS_COLOR, bg='white').pack(anchor="w")
    
    tk.Label(summary_frame, text=f"🔢 Total possible units across all categories: {total_possible}", 
             font=('Arial', 11), fg=DARK_TEXT, bg='white').pack(anchor="w", pady=(5,0))
    
    # Buttons - with more spacing to make them prominent
    btn_frame = tk.Frame(main_frame, bg='white')
    btn_frame.pack(fill="x", pady=(30,20))
    
    def refresh_predictions():
        # Clear existing items
        for item in pred_tree.get_children():
            pred_tree.delete(item)
        
        # Reload predictions
        new_predictions = predict_tomorrow_production()
        new_total = 0
        
        for category_name, max_units, limiting_factor in new_predictions:
            if max_units > 0:
                new_total += max_units
                tag = "can_produce"
            else:
                tag = "cannot_produce"
            
            pred_tree.insert("", "end", values=(category_name, max_units, limiting_factor), tags=(tag,))
        
        # Update summary
        for widget in summary_frame.winfo_children():
            widget.destroy()
        
        tk.Label(summary_frame, text=f"📊 Summary: {len([p for p in new_predictions if p[1] > 0])} categories can be produced tomorrow", 
                 font=('Arial', 12, 'bold'), fg=SUCCESS_COLOR, bg='white').pack(anchor="w")
        
        tk.Label(summary_frame, text=f"🔢 Total possible units across all categories: {new_total}", 
                 font=('Arial', 11), fg=DARK_TEXT, bg='white').pack(anchor="w", pady=(5,0))
    
    # Make buttons MUCH bigger and more visible
    refresh_btn = tk.Button(btn_frame, text="🔄 REFRESH PREDICTIONS", 
                           font=('Arial', 16, 'bold'), bg='#2980b9', fg='white',
                           relief='raised', bd=3, padx=40, pady=20, cursor='hand2',
                           width=20, height=2, command=refresh_predictions)
    refresh_btn.pack(side="left", padx=20, pady=10)
    
    close_btn = tk.Button(btn_frame, text="✅ CLOSE", 
                         font=('Arial', 16, 'bold'), bg='#7f8c8d', fg='white',
                         relief='raised', bd=3, padx=40, pady=20, cursor='hand2',
                         width=15, height=2, command=win.destroy)
    close_btn.pack(side="right", padx=20, pady=10)

def show_supplier_notify_popup(low_item, supplier):
    """
    low_item: dict with keys material_id, name, new_q, unit, threshold, supplier_id
    supplier: tuple (id, name, whatsapp, phone, notes) or None
    """
    # Check if a popup is already open for this material
    for child in root.winfo_children():
        if isinstance(child, tk.Toplevel) and low_item['name'] in child.title():
            child.lift()  # Bring existing popup to front
            return
    
    win = tk.Toplevel(root)
    win.title(f"⚠️ Low Stock Alert - {low_item['name']}")
    win.geometry("700x650")  # Made larger to accommodate buttons
    win.configure(bg='white')
    win.resizable(True, True)  # Allow resizing to see content
    win.transient(root)
    win.grab_set()
    
    # Header
    header = tk.Frame(win, bg=DANGER_COLOR, height=80)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text=f"⚠️ Low Stock Alert", font=('Arial', 16, 'bold'), 
             fg='white', bg=DANGER_COLOR).pack(pady=10)
    tk.Label(header, text=f"Material: {low_item['name']}", font=('Arial', 12), 
             fg='white', bg=DANGER_COLOR).pack()
    
    # Alert info frame
    info_frame = tk.LabelFrame(win, text="📊 Stock Information", font=('Arial', 10, 'bold'), 
                              fg=DANGER_COLOR, bg='white', bd=2, relief='groove')
    info_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Label(info_frame, text=f"Current Stock: {low_item['new_q']} {low_item['unit']}", 
             font=('Arial', 10), fg=DANGER_COLOR, bg='white').pack(anchor="w", padx=10, pady=5)
    tk.Label(info_frame, text=f"Threshold Level: {low_item['threshold']} {low_item['unit']}", 
             font=('Arial', 10), fg=DARK_TEXT, bg='white').pack(anchor="w", padx=10, pady=5)

    # Supplier selection frame
    supplier_frame = tk.LabelFrame(win, text="👤 Supplier Selection", font=('Arial', 10, 'bold'), 
                                  fg=PRIMARY_COLOR, bg='white', bd=2, relief='groove')
    supplier_frame.pack(fill="x", padx=20, pady=10)
    
    suppliers = fetch_suppliers(limit=10)  # Increased limit
    
    if suppliers:
        tk.Label(supplier_frame, text="Select Supplier:", font=('Arial', 10, 'bold'), 
                fg=DARK_TEXT, bg='white').pack(anchor="w", padx=10, pady=(10,5))
        
        opt_menu = ttk.Combobox(supplier_frame, values=[f"{s[0]}: {s[1]}" for s in suppliers], 
                               state="readonly", width=50, font=('Arial', 10))
        opt_menu.pack(fill="x", padx=10, pady=(0,10))
        
        # Set default selection
        if supplier:
            for idx, s in enumerate(suppliers):
                if s[0] == supplier[0]:
                    opt_menu.current(idx)
                    break
        else:
            opt_menu.current(0)
    else:
        tk.Label(supplier_frame, text="⚠️ No suppliers configured. Please add suppliers in database.", 
                font=('Arial', 10), fg=WARNING_COLOR, bg='white').pack(padx=10, pady=10)

    # Supplier details frame
    details_frame = tk.LabelFrame(win, text="✏️ Supplier Details (Editable)", font=('Arial', 10, 'bold'), 
                                 fg=PRIMARY_COLOR, bg='white', bd=2, relief='groove')
    details_frame.pack(fill="x", padx=20, pady=10)
    
    # Create grid layout for supplier details
    detail_grid = tk.Frame(details_frame, bg='white')
    detail_grid.pack(fill="x", padx=10, pady=10)
    
    tk.Label(detail_grid, text="Supplier Name:", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=0, column=0, sticky="w", pady=5)
    e_name = tk.Entry(detail_grid, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_name.grid(row=0, column=1, padx=(10,0), pady=5, sticky="ew")

    tk.Label(detail_grid, text="WhatsApp (+91...):", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=1, column=0, sticky="w", pady=5)
    e_wh = tk.Entry(detail_grid, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_wh.grid(row=1, column=1, padx=(10,0), pady=5, sticky="ew")

    tk.Label(detail_grid, text="Phone Number:", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=2, column=0, sticky="w", pady=5)
    e_phone = tk.Entry(detail_grid, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_phone.grid(row=2, column=1, padx=(10,0), pady=5, sticky="ew")
    
    detail_grid.columnconfigure(1, weight=1)

    # Fill with selected supplier info if present
    def fill_supplier_fields_by_index(event=None):
        # event: combo selection
        if not suppliers:
            return
        sel_text = opt_menu.get()
        # find supplier by parsing sel_text like "1: Supplier One"
        try:
            sid = int(sel_text.split(":")[0])
        except Exception:
            sid = None
        chosen = None
        for s in suppliers:
            if s[0] == sid:
                chosen = s
                break
        if chosen:
            e_name.delete(0, tk.END); e_name.insert(0, chosen[1] or "")
            e_wh.delete(0, tk.END); e_wh.insert(0, chosen[2] or "")
            e_phone.delete(0, tk.END); e_phone.insert(0, chosen[3] or "")

    if suppliers:
        opt_menu.bind("<<ComboboxSelected>>", fill_supplier_fields_by_index)
        # initial fill
        fill_supplier_fields_by_index()

    def update_supplier_db():
        if not suppliers:
            messagebox.showerror("❌ Error", "No supplier selected to update!")
            return
        sel_text = opt_menu.get()
        try:
            sid = int(sel_text.split(":")[0])
        except Exception:
            messagebox.showerror("❌ Error", "Invalid supplier selection!")
            return
        name = e_name.get().strip()
        whatsapp = e_wh.get().strip()
        phone = e_phone.get().strip()
        ok, err = update_supplier(sid, name, whatsapp, phone)
        if ok:
            messagebox.showinfo("✅ Success", "Supplier details updated successfully!")
            load_inventory()
            update_stats()
            win.destroy()
        else:
            messagebox.showerror("❌ Error", err)

    def send_message_to_selected():
        if not suppliers:
            messagebox.showerror("❌ Error", "No supplier available to send message!")
            return
        sel_text = opt_menu.get()
        try:
            sid = int(sel_text.split(":")[0])
        except Exception:
            messagebox.showerror("❌ Error", "Invalid supplier selection!")
            return
        chosen = None
        for s in suppliers:
            if s[0] == sid:
                chosen = s
                break
        if not chosen:
            messagebox.showerror("❌ Error", "Supplier not found!")
            return
        sup_id, sup_name, sup_whatsapp, sup_phone, _notes = chosen
        # allow using edited fields (not yet saved)
        sup_name_edit = e_name.get().strip() or sup_name
        sup_whatsapp_edit = e_wh.get().strip() or sup_whatsapp
        sup_phone_edit = e_phone.get().strip() or sup_phone

        # Build order message
        threshold = float(low_item['threshold'])
        new_q = float(low_item['new_q'])
        suggested = max((threshold * 2) - new_q, threshold)
        suggested = round(suggested, 2)
        message = f"Hello {sup_name_edit},\n\n🚨 URGENT SUPPLY REQUEST 🚨\n\nWe require immediate supply for:\n📦 {low_item['name']}: {suggested} {low_item['unit']}\n📊 Current stock: {low_item['new_q']} {low_item['unit']}\n⚠️ Below threshold level\n\nPlease arrange delivery ASAP.\n\nThanks,\nCanteen Management"

        # If the user edited supplier details but didn't update DB, we still use edited number to send.
        if TWILIO_ENABLED:
            ok, info = send_whatsapp_twilio(sup_whatsapp_edit, message, supplier_id=sup_id)
            if ok:
                messagebox.showinfo("✅ Message Sent", f"WhatsApp message sent successfully via Twilio!\nMessage ID: {info}")
                win.destroy()
                load_inventory()
                update_stats()
            else:
                messagebox.showwarning("⚠️ Twilio Failed", f"Twilio failed: {info}\nOpening WhatsApp Web as fallback...")
                open_whatsapp_web(sup_whatsapp_edit, message, supplier_id=sup_id)
                win.destroy()
                load_inventory()
                update_stats()
        else:
            open_whatsapp_web(sup_whatsapp_edit, message, supplier_id=sup_id)
            win.destroy()
            load_inventory()
            update_stats()

    # Action buttons frame
    action_frame = tk.Frame(win, bg='white')
    action_frame.pack(fill="x", padx=20, pady=20)
    
    # FINAL FIX: Create large, visible buttons with contrasting colors
    
    # Create a button frame with better spacing
    button_container = tk.Frame(action_frame, bg='white', relief='sunken', bd=2)
    button_container.pack(fill="x", pady=10)
    
    # Update Supplier Button - Large and visible
    update_btn = tk.Button(button_container, 
                          text="UPDATE SUPPLIER", 
                          command=update_supplier_db,
                          font=('Arial', 14, 'bold'),
                          fg='white', 
                          bg='#1f4e79',  # Dark blue
                          activeforeground='white',
                          activebackground='#2c5aa0',
                          relief='raised',
                          bd=5,
                          padx=25,
                          pady=12,
                          width=15)
    update_btn.pack(side="left", padx=10, pady=5)
    
    # WhatsApp Button - Large and visible
    whatsapp_btn = tk.Button(button_container, 
                            text="SEND WHATSAPP", 
                            command=send_message_to_selected,
                            font=('Arial', 14, 'bold'),
                            fg='white', 
                            bg='#0d7377',  # Dark green
                            activeforeground='white',
                            activebackground='#14a085',
                            relief='raised',
                            bd=5,
                            padx=25,
                            pady=12,
                            width=15)
    whatsapp_btn.pack(side="left", padx=10, pady=5)
    
    # Cancel Button - Large and visible
    cancel_btn = tk.Button(button_container, 
                          text="CANCEL", 
                          command=win.destroy,
                          font=('Arial', 14, 'bold'),
                          fg='black', 
                          bg='#e8e8e8',  # Light gray
                          activeforeground='black',
                          activebackground='#d0d0d0',
                          relief='raised',
                          bd=5,
                          padx=25,
                          pady=12,
                          width=10)
    cancel_btn.pack(side="right", padx=10, pady=5)

# Inventory action buttons
inv_btn_frame = tk.Frame(inv_right, bg='white')
inv_btn_frame.pack(fill="x", padx=15, pady=10)

ttk.Button(inv_btn_frame, text="🔄 Refresh Inventory", command=lambda: [load_inventory(), update_stats()], 
           style='Primary.TButton').pack(fill="x", pady=5)

# Category action buttons  
cat_btn_frame = tk.Frame(cat_right, bg='white')
cat_btn_frame.pack(fill="x", padx=15, pady=10)

ttk.Button(cat_btn_frame, text="➕ Add Category", command=add_category_popup, 
           style='Success.TButton').pack(fill="x", pady=5)
ttk.Button(cat_btn_frame, text="✏️ Edit Category", command=edit_category_popup, 
           style='Warning.TButton').pack(fill="x", pady=5)
ttk.Button(cat_btn_frame, text="🗑️ Delete Category", command=delete_category_confirm, 
           style='Danger.TButton').pack(fill="x", pady=5)
ttk.Button(cat_btn_frame, text="🔗 Map Material to Category", command=map_material_popup, 
           style='Primary.TButton').pack(fill="x", pady=5)
ttk.Button(cat_btn_frame, text="👁️ View Category Materials", command=view_category_materials, 
           style='Primary.TButton').pack(fill="x", pady=5)

# Sales section
sales_frame = tk.LabelFrame(cat_right, text="💰 Sales Operations", font=('Arial', 10, 'bold'), 
                           fg=PRIMARY_COLOR, bg='white', bd=2, relief='groove')
sales_frame.pack(fill="x", padx=15, pady=10)

ttk.Button(sales_frame, text="Record Sale & Deduct Stock", command=sale_popup, 
           style='Warning.TButton').pack(fill="x", padx=10, pady=5)

ttk.Button(sales_frame, text="📊 Tomorrow's Production Prediction", command=show_production_prediction, 
           style='Primary.TButton').pack(fill="x", padx=10, pady=5)

ttk.Button(cat_btn_frame, text="🔄 Refresh Categories", command=load_categories, 
           style='Primary.TButton').pack(fill="x", pady=5)

# Initial load
load_inventory()
load_categories()
update_stats()

# Add some keyboard shortcuts
def on_key_press(event):
    if event.state & 0x4:  # Ctrl key
        if event.keysym == 'r':  # Ctrl+R for refresh
            current_tab = notebook.index(notebook.select())
            if current_tab == 0:  # Inventory tab
                load_inventory()
                update_stats()
            else:  # Categories tab
                load_categories()
        elif event.keysym == 'n':  # Ctrl+N for new category
            if notebook.index(notebook.select()) == 1:  # Categories tab
                add_category_popup()

root.bind('<KeyPress>', on_key_press)
root.focus_set()

root.mainloop()
