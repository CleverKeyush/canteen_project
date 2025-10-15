# main.py
import tkinter as tk
from tkinter import ttk, messagebox, font
from decimal import Decimal
from inventory import fetch_inventory, get_material, adjust_material_quantity, add_material, update_material, delete_material, calculate_material_cost, record_sale_with_profit, get_profit_summary, get_item_profitability
from categories import fetch_categories, create_category, set_category_material, get_category_materials
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

inv_cols = ("ID", "Name", "Quantity", "Unit", "Threshold", "Supplier ID", "Status")
inv_tree = ttk.Treeview(inv_tree_frame, columns=inv_cols, show="headings", height=15, style='Custom.Treeview')

# Configure column widths and headings
column_widths = {"ID": 60, "Name": 200, "Quantity": 100, "Unit": 80, "Threshold": 100, "Supplier ID": 100, "Status": 100}
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
        # Add status column
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
    win.geometry("500x400")
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
    
    tk.Label(form_frame, text="Supplier ID (optional)", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=8, column=0, sticky="w", pady=(0,5))
    e_supplier = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_supplier.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0,20))
    
    form_frame.columnconfigure(0, weight=1)
    
    def save_material():
        name = e_name.get().strip()
        try:
            quantity = float(e_qty.get())
            threshold = float(e_threshold.get())
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter valid numbers for quantity and threshold!")
            return
        
        unit = e_unit.get().strip()
        supplier_id = e_supplier.get().strip() or None
        
        if not name or not unit:
            messagebox.showerror("❌ Error", "Name and unit are required!")
            return
        
        if supplier_id:
            try:
                supplier_id = int(supplier_id)
            except ValueError:
                messagebox.showerror("❌ Error", "Supplier ID must be a number!")
                return
        
        ok, result = add_material(name, quantity, unit, threshold, supplier_id)
        if ok:
            messagebox.showinfo("✅ Success", f"Material '{name}' added successfully with ID: {result}")
            load_inventory()
            update_stats()
            win.destroy()
        else:
            messagebox.showerror("❌ Error", f"Failed to add material: {result}")
    
    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=10, column=0, columnspan=2, pady=10)
    
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
    win.geometry("500x400")
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
    
    tk.Label(form_frame, text="Supplier ID", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=8, column=0, sticky="w", pady=(0,5))
    e_supplier = tk.Entry(form_frame, width=40, font=('Arial', 10), relief='solid', bd=1)
    e_supplier.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0,20))
    e_supplier.insert(0, material_data[5] if material_data[5] else "")
    
    form_frame.columnconfigure(0, weight=1)
    
    def update_material_data():
        name = e_name.get().strip()
        try:
            quantity = float(e_qty.get())
            threshold = float(e_threshold.get())
        except ValueError:
            messagebox.showerror("❌ Error", "Please enter valid numbers for quantity and threshold!")
            return
        
        unit = e_unit.get().strip()
        supplier_id = e_supplier.get().strip() or None
        
        if not name or not unit:
            messagebox.showerror("❌ Error", "Name and unit are required!")
            return
        
        if supplier_id:
            try:
                supplier_id = int(supplier_id)
            except ValueError:
                messagebox.showerror("❌ Error", "Supplier ID must be a number!")
                return
        
        ok, result = update_material(material_id, name, quantity, unit, threshold, supplier_id)
        if ok:
            messagebox.showinfo("✅ Success", f"Material updated successfully!")
            load_inventory()
            update_stats()
            win.destroy()
        else:
            messagebox.showerror("❌ Error", f"Failed to update material: {result}")
    
    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=10, column=0, columnspan=2, pady=10)
    
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

cat_cols = ("ID", "Name", "Description")
cat_tree = ttk.Treeview(cat_tree_frame, columns=cat_cols, show="headings", height=12, style='Custom.Treeview')

# Configure column widths
cat_column_widths = {"ID": 60, "Name": 200, "Description": 300}
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
    win.geometry("450x250")
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
    e_desc.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0,20))
    
    form_frame.columnconfigure(0, weight=1)
    
    def save():
        name = e_name.get().strip()
        desc = e_desc.get().strip()
        if not name:
            messagebox.showerror("❌ Error", "Category name is required!")
            return
        ok, res = create_category(name, desc)
        if ok:
            messagebox.showinfo("✅ Success", f"Category '{name}' created successfully!")
            load_categories()
            win.destroy()
        else:
            messagebox.showerror("❌ Error", res)
    
    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
    
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="✅ Save Category", command=save, style='Success.TButton').pack(side="left")
    
    e_name.focus_set()

def map_material_popup():
    sel = cat_tree.selection()
    if not sel:
        messagebox.showerror("❌ Error", "Please select a category first!")
        return
    cat_id = cat_tree.item(sel[0])['values'][0]
    cat_name = cat_tree.item(sel[0])['values'][1]
    
    win = tk.Toplevel(root)
    win.title("🔗 Map Material to Category")
    win.geometry("500x300")
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
    
    tk.Label(form_frame, text="Material ID (from inventory) *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=0, column=0, sticky="w", pady=(0,5))
    e_mid = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_mid.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,15))
    
    tk.Label(form_frame, text="Amount used per unit *", font=('Arial', 10, 'bold'), 
             fg=DARK_TEXT, bg='white').grid(row=2, column=0, sticky="w", pady=(0,5))
    e_amt = tk.Entry(form_frame, width=35, font=('Arial', 10), relief='solid', bd=1)
    e_amt.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0,20))
    
    form_frame.columnconfigure(0, weight=1)
    
    def save_map():
        try:
            mid = int(e_mid.get())
            amt = float(e_amt.get())
        except Exception:
            messagebox.showerror("❌ Error", "Please enter valid numeric values!")
            return
        ok, err = set_category_material(cat_id, mid, amt)
        if ok:
            messagebox.showinfo("✅ Success", "Material mapping saved successfully!")
            win.destroy()
        else:
            messagebox.showerror("❌ Error", err)
    
    # Buttons frame
    btn_frame = tk.Frame(form_frame, bg='white')
    btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
    
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=(0,10))
    ttk.Button(btn_frame, text="✅ Save Mapping", command=save_map, style='Success.TButton').pack(side="left")
    
    e_mid.focus_set()

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
    
    # Make window larger if it's cold drinks to accommodate brand selection
    if cat_name.lower() == "cold drinks":
        win.geometry("450x350")
    else:
        win.geometry("450x250")
        
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
                conn.commit()
                conn.close()
                
                # Show success message with brand info
                messagebox.showinfo("✅ Success", 
                    f"Sale recorded successfully!\n\n"
                    f"Brand: {selected_brand}\n"
                    f"Quantity Sold: {qty_sold}\n"
                    f"Remaining Stock: {new_stock}")
                
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
                if ok:
                    profit_msg = f"""Sale recorded successfully! 

📊 PROFIT ANALYSIS:
• Units Sold: {qty_sold}
• Selling Price: ₹{selling_price} per unit
• Material Cost: ₹{profit_info['material_cost']:.2f} per unit
• Profit per Unit: ₹{profit_info['profit_per_unit']:.2f}
• Total Profit: ₹{profit_info['total_profit']:.2f}
• Profit Margin: {profit_info['profit_margin']:.1f}%"""
                    messagebox.showinfo("✅ Sale Recorded", profit_msg)
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
ttk.Button(cat_btn_frame, text="🔗 Map Material to Category", command=map_material_popup, 
           style='Primary.TButton').pack(fill="x", pady=5)
ttk.Button(cat_btn_frame, text="👁️ View Category Materials", command=view_category_materials, 
           style='Primary.TButton').pack(fill="x", pady=5)

# Sales section
sales_frame = tk.LabelFrame(cat_right, text="💰 Sales Operations", font=('Arial', 10, 'bold'), 
                           fg=PRIMARY_COLOR, bg='white', bd=2, relief='groove')
sales_frame.pack(fill="x", padx=15, pady=10)

ttk.Button(sales_frame, text="Record Sale & Deduct Stock", command=sale_popup, 
           style='Warning.TButton').pack(fill="x", padx=10, pady=10)

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
