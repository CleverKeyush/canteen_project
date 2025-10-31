# 🍽️ Canteen Management System v2.0

A comprehensive inventory and sales management system for canteens with **direct bill printing** and **WhatsApp e-bill integration**.

## 🎉 Latest Features (v2.0)

### 📱 E-Bill WhatsApp Integration
- **Send bills directly to customers via WhatsApp**
- **One-click e-bill sending** after sales
- **Automatic phone formatting** (+91 prefix handling)
- **Professional bill formatting** for WhatsApp
- **Twilio API + WhatsApp Web fallback**

### 🖨️ Direct Bill Printing
- **One-click printing** - No notepad needed!
- **Instant printing** to default printer
- **Perfect for busy vendors** - Super fast operation
- **Unicode support** - Handles ₹ symbol correctly
- **Always works** - Multiple fallback methods

### 🎨 Modern UI Design
- **Professional bill popup** with clean design
- **Action buttons**: Print Bill, Send E-Bill, View Profit
- **Better visibility** - Larger, clearer buttons
- **Vendor-friendly interface** - Easy to use

## 🏪 Core Features
- **Raw materials inventory tracking** with low stock alerts
- **Sales recording** with automatic profit calculation
- **Category management** with material mapping
- **Supplier management** with WhatsApp notifications
- **Production prediction** for tomorrow's capacity
- **Profit analysis** and detailed reporting
- **Professional bill generation** with customer details

## 🚀 Quick Start

### Prerequisites
```bash
pip install tkinter mysql-connector-python pywin32
# Optional for WhatsApp API:
pip install twilio
```

### Setup
1. **Clone repository**
   ```bash
   git clone https://github.com/CleverKeyush/canteen_project.git
   cd canteen_project
   ```

2. **Setup database**
   ```bash
   # Execute sql/database.sql in your MySQL/PostgreSQL
   ```

3. **Run application**
   ```bash
   python main.py
   ```

## 📱 How to Use E-Bill Feature

### For Vendors:
1. **Record sale** - Enter items and customer phone number
2. **Click "Send E-Bill"** - One button click
3. **Customer receives bill** - Instantly on WhatsApp!

### Phone Number Format:
- `9876543210` (10 digits)
- `+919876543210` (with country code)
- System auto-formats to `+91` prefix

## 🖨️ How to Use Direct Printing

### Super Simple:
1. **Ensure printer connected** and set as default
2. **Click "Print Bill"** button
3. **Bill prints immediately** - Done!

### No More:
- ❌ Opening notepad
- ❌ Pressing Ctrl+P
- ❌ Multiple steps

### Just:
- ✅ Click button → Bill prints!

## 📊 Screenshots

### Bill Popup with E-Bill Feature
- Professional popup design
- Bill details display
- Action buttons: Print, E-Bill, Profit Analysis

### Direct Printing
- One-click operation
- Instant printer output
- Perfect for busy canteens

## 🛠️ Technical Details

### Architecture:
- **Frontend**: Tkinter (Python GUI)
- **Database**: MySQL/PostgreSQL
- **Printing**: Windows Print API (pywin32)
- **WhatsApp**: Twilio API + Web fallback

### Key Files:
- `main.py` - Core application
- `inventory.py` - Inventory management
- `categories.py` - Category operations
- `whatsapp_notify.py` - WhatsApp integration
- `db.py` - Database connections

## 🎯 Perfect For:
- **School canteens** - Fast student service
- **Office cafeterias** - Professional receipts
- **Small restaurants** - Complete management
- **Food stalls** - Quick operations

## 📞 Support
- **Issues**: Create GitHub issue
- **Features**: Submit pull request
- **Questions**: Check documentation

## 📄 License
MIT License - Feel free to use and modify!

---

**Made with ❤️ for efficient canteen management**

*Version 2.0 - Now with direct printing and WhatsApp e-bills!* 🎉
