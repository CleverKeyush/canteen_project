-- PostgreSQL Database Setup for Canteen Inventory Management System

-- Create database (run this first if database doesn't exist)
-- CREATE DATABASE canteen_inventory;

-- Connect to the database and create tables

-- Raw Materials Table
CREATE TABLE IF NOT EXISTS raw_materials (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
    unit VARCHAR(50) NOT NULL,
    threshold DECIMAL(10,2) NOT NULL DEFAULT 0,
    cost_per_unit DECIMAL(10,2) DEFAULT 0, -- Cost price in Indian Rupees
    supplier_id INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    whatsapp VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories Table (for products/dishes)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    selling_price DECIMAL(10,2) DEFAULT 0, -- Selling price in Indian Rupees
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Category Materials Mapping (which materials are used in each category/dish)
CREATE TABLE IF NOT EXISTS category_materials (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    material_id INTEGER REFERENCES raw_materials(id) ON DELETE CASCADE,
    amount_per_unit DECIMAL(10,3) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, material_id)
);

-- Daily sales summary with profit tracking (Indian Rupees)
CREATE TABLE IF NOT EXISTS daily_sales (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id),
    quantity_sold INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,        -- Selling price per unit in ₹
    material_cost_per_unit DECIMAL(10,2) NOT NULL, -- Cost of materials per unit in ₹
    profit_per_unit DECIMAL(10,2) NOT NULL,   -- Profit per unit in ₹
    total_revenue DECIMAL(10,2) NOT NULL,     -- Total revenue in ₹
    total_cost DECIMAL(10,2) NOT NULL,        -- Total material cost in ₹
    total_profit DECIMAL(10,2) NOT NULL,      -- Total profit in ₹
    sale_date DATE DEFAULT CURRENT_DATE,
    sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- Profit summary table for quick reporting
CREATE TABLE IF NOT EXISTS profit_summary (
    id SERIAL PRIMARY KEY,
    summary_date DATE DEFAULT CURRENT_DATE,
    total_sales_count INTEGER DEFAULT 0,
    total_revenue DECIMAL(10,2) DEFAULT 0,
    total_cost DECIMAL(10,2) DEFAULT 0,
    total_profit DECIMAL(10,2) DEFAULT 0,
    profit_margin_percent DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(summary_date)
);

-- Stock Transactions Log (optional - for tracking all stock movements)
CREATE TABLE IF NOT EXISTS stock_transactions (
    id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES raw_materials(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL, -- 'RESTOCK', 'SALE', 'ADJUSTMENT', 'WASTE'
    quantity_change DECIMAL(10,2) NOT NULL, -- positive for additions, negative for deductions
    previous_quantity DECIMAL(10,2) NOT NULL,
    new_quantity DECIMAL(10,2) NOT NULL,
    reference_id INTEGER, -- could reference sale_id, purchase_id, etc.
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- Add foreign key constraint for supplier_id in raw_materials
ALTER TABLE raw_materials 
ADD CONSTRAINT fk_raw_materials_supplier 
FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_raw_materials_name ON raw_materials(name);
CREATE INDEX IF NOT EXISTS idx_raw_materials_supplier ON raw_materials(supplier_id);
CREATE INDEX IF NOT EXISTS idx_stock_transactions_material ON stock_transactions(material_id);
CREATE INDEX IF NOT EXISTS idx_stock_transactions_date ON stock_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_category_materials_category ON category_materials(category_id);
CREATE INDEX IF NOT EXISTS idx_category_materials_material ON category_materials(material_id);
CREATE INDEX IF NOT EXISTS idx_daily_sales_date ON daily_sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_daily_sales_category ON daily_sales(category_id);
CREATE INDEX IF NOT EXISTS idx_profit_summary_date ON profit_summary(summary_date);

-- Insert sample data for SCHOOL CANTEEN
INSERT INTO suppliers (name, whatsapp, phone, email) VALUES 
('Local Vegetable Vendor', '+919876543210', '9876543210', 'vegetables@local.com'),
('Bakery Supplier', '+919876543211', '9876543211', 'bakery@supplier.com'),
('Cold Drinks Distributor', '+919876543212', '9876543212', 'drinks@distributor.com'),
('Grocery Store', '+919876543213', '9876543213', 'grocery@store.com')
ON CONFLICT DO NOTHING;

-- Raw materials for school canteen items (with Indian Rupee prices)
INSERT INTO raw_materials (name, quantity, unit, threshold, cost_per_unit, supplier_id) VALUES 
-- For Vadapav
('Potatoes', 20.0, 'kg', 5.0, 30.00, 1),        -- ₹30 per kg
('Pav Bread', 100.0, 'pieces', 20.0, 2.50, 2),  -- ₹2.50 per piece
('Cooking Oil', 5.0, 'liters', 1.0, 120.00, 4), -- ₹120 per liter
('Onions', 10.0, 'kg', 2.0, 25.00, 1),          -- ₹25 per kg
('Green Chilies', 1.0, 'kg', 0.2, 80.00, 1),    -- ₹80 per kg
('Ginger-Garlic Paste', 2.0, 'kg', 0.5, 150.00, 4), -- ₹150 per kg
('Turmeric Powder', 0.5, 'kg', 0.1, 200.00, 4), -- ₹200 per kg
('Mustard Seeds', 0.2, 'kg', 0.05, 180.00, 4),  -- ₹180 per kg
('Curry Leaves', 0.1, 'kg', 0.02, 100.00, 1),   -- ₹100 per kg

-- For Samosa
('Samosa Sheets', 200.0, 'pieces', 50.0, 1.50, 2), -- ₹1.50 per sheet
('Cumin Seeds', 0.2, 'kg', 0.05, 300.00, 4),    -- ₹300 per kg
('Coriander Powder', 0.3, 'kg', 0.1, 250.00, 4), -- ₹250 per kg
('Red Chili Powder', 0.2, 'kg', 0.05, 280.00, 4), -- ₹280 per kg
('Garam Masala', 0.1, 'kg', 0.02, 400.00, 4),   -- ₹400 per kg

-- Cold Drinks (wholesale prices)
('Coca Cola', 48.0, 'bottles', 12.0, 18.00, 3), -- ₹18 per bottle (wholesale)
('Pepsi', 48.0, 'bottles', 12.0, 18.00, 3),     -- ₹18 per bottle (wholesale)
('Sprite', 24.0, 'bottles', 6.0, 18.00, 3),     -- ₹18 per bottle (wholesale)
('Fanta', 24.0, 'bottles', 6.0, 18.00, 3),      -- ₹18 per bottle (wholesale)
('Thumbs Up', 24.0, 'bottles', 6.0, 18.00, 3),  -- ₹18 per bottle (wholesale)
('Limca', 24.0, 'bottles', 6.0, 18.00, 3),      -- ₹18 per bottle (wholesale)

-- Common ingredients
('Salt', 2.0, 'kg', 0.5, 20.00, 4),             -- ₹20 per kg
('Sugar', 3.0, 'kg', 1.0, 45.00, 4),            -- ₹45 per kg
('Tea Powder', 1.0, 'kg', 0.2, 350.00, 4),      -- ₹350 per kg
('Milk', 10.0, 'liters', 2.0, 55.00, 4)         -- ₹55 per liter
ON CONFLICT (name) DO NOTHING;

-- School canteen product categories (with Indian Rupee selling prices)
INSERT INTO categories (name, description, selling_price) VALUES 
('Vadapav', 'Spiced potato fritter in bread bun', 15.00),      -- ₹15 per vadapav
('Only Vada', 'Potato fritter without pav', 8.00),             -- ₹8 per vada
('Only Pav', 'Plain bread bun', 3.00),                         -- ₹3 per pav
('Samosa', 'Fried pastry with spiced potato filling', 12.00),  -- ₹12 per samosa
('Cold Drinks', 'Bottled soft drinks - brand selected at sale', 25.00), -- ₹25 per bottle
('Tea/Coffee', 'Hot beverages', 10.00)                         -- ₹10 per cup
ON CONFLICT (name) DO NOTHING;

-- Material usage per school canteen item
INSERT INTO category_materials (category_id, material_id, amount_per_unit) VALUES 
-- Vadapav (1 piece uses)
(1, 1, 0.1),   -- 100g potatoes
(1, 2, 1.0),   -- 1 pav bread
(1, 3, 0.02),  -- 20ml oil
(1, 4, 0.02),  -- 20g onions
(1, 5, 0.005), -- 5g green chilies
(1, 6, 0.01),  -- 10g ginger-garlic paste
(1, 7, 0.002), -- 2g turmeric
(1, 21, 0.002), -- 2g salt

-- Only Vada (1 piece uses)
(2, 1, 0.1),   -- 100g potatoes
(2, 3, 0.02),  -- 20ml oil
(2, 4, 0.02),  -- 20g onions
(2, 5, 0.005), -- 5g green chilies
(2, 6, 0.01),  -- 10g ginger-garlic paste
(2, 7, 0.002), -- 2g turmeric
(2, 21, 0.002), -- 2g salt

-- Only Pav (1 piece uses)
(3, 2, 1.0),   -- 1 pav bread

-- Samosa (1 piece uses)
(4, 10, 1.0),  -- 1 samosa sheet
(4, 1, 0.08),  -- 80g potatoes
(4, 3, 0.015), -- 15ml oil
(4, 4, 0.015), -- 15g onions
(4, 11, 0.002), -- 2g cumin seeds
(4, 12, 0.003), -- 3g coriander powder
(4, 13, 0.002), -- 2g red chili powder
(4, 21, 0.002), -- 2g salt

-- Cold Drinks - No material mapping needed (handled by brand selection in app)
-- The brand selection in the app will directly deduct from raw materials

-- Tea/Coffee (1 cup uses)
(6, 23, 0.005), -- 5g tea powder
(6, 24, 0.1),   -- 100ml milk
(6, 22, 0.01)   -- 10g sugar
ON CONFLICT (category_id, material_id) DO NOTHING;

-- Function to automatically log stock transactions (optional)
CREATE OR REPLACE FUNCTION log_stock_transaction()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND OLD.quantity != NEW.quantity THEN
        INSERT INTO stock_transactions (
            material_id, 
            transaction_type, 
            quantity_change, 
            previous_quantity, 
            new_quantity,
            notes
        ) VALUES (
            NEW.id,
            CASE 
                WHEN NEW.quantity > OLD.quantity THEN 'RESTOCK'
                ELSE 'DEDUCTION'
            END,
            NEW.quantity - OLD.quantity,
            OLD.quantity,
            NEW.quantity,
            'Auto-logged from raw_materials update'
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Functions and Triggers (created after all tables exist)

-- Function to calculate material cost for a category
CREATE OR REPLACE FUNCTION calculate_material_cost(cat_id INTEGER)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    total_cost DECIMAL(10,2) := 0;
BEGIN
    SELECT COALESCE(SUM(rm.cost_per_unit * cm.amount_per_unit), 0)
    INTO total_cost
    FROM category_materials cm
    JOIN raw_materials rm ON cm.material_id = rm.id
    WHERE cm.category_id = cat_id;
    
    RETURN total_cost;
END;
$$ LANGUAGE plpgsql;

-- Function to update daily profit summary
CREATE OR REPLACE FUNCTION update_profit_summary()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profit_summary (
        summary_date, 
        total_sales_count, 
        total_revenue, 
        total_cost, 
        total_profit,
        profit_margin_percent
    )
    SELECT 
        NEW.sale_date,
        COUNT(*),
        SUM(total_revenue),
        SUM(total_cost),
        SUM(total_profit),
        CASE 
            WHEN SUM(total_revenue) > 0 THEN 
                ROUND((SUM(total_profit) / SUM(total_revenue)) * 100, 2)
            ELSE 0 
        END
    FROM daily_sales 
    WHERE sale_date = NEW.sale_date
    GROUP BY sale_date
    ON CONFLICT (summary_date) 
    DO UPDATE SET
        total_sales_count = EXCLUDED.total_sales_count,
        total_revenue = EXCLUDED.total_revenue,
        total_cost = EXCLUDED.total_cost,
        total_profit = EXCLUDED.total_profit,
        profit_margin_percent = EXCLUDED.profit_margin_percent;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers (after all tables and functions exist)
DROP TRIGGER IF EXISTS trigger_log_stock_changes ON raw_materials;
CREATE TRIGGER trigger_log_stock_changes
    AFTER UPDATE ON raw_materials
    FOR EACH ROW
    EXECUTE FUNCTION log_stock_transaction();

DROP TRIGGER IF EXISTS trigger_update_profit_summary ON daily_sales;
CREATE TRIGGER trigger_update_profit_summary
    AFTER INSERT ON daily_sales
    FOR EACH ROW
    EXECUTE FUNCTION update_profit_summary();

-- Useful queries for SCHOOL CANTEEN:

-- 1. Check which items can be made with current stock
-- SELECT c.name as item, 
--        MIN(FLOOR(rm.quantity / cm.amount_per_unit)) as max_units_possible
-- FROM categories c
-- JOIN category_materials cm ON c.id = cm.category_id
-- JOIN raw_materials rm ON cm.material_id = rm.id
-- GROUP BY c.id, c.name
-- HAVING MIN(FLOOR(rm.quantity / cm.amount_per_unit)) > 0;

-- 2. Get low stock items for school canteen
-- SELECT rm.name, rm.quantity, rm.unit, rm.threshold, s.name as supplier_name, s.whatsapp 
-- FROM raw_materials rm 
-- LEFT JOIN suppliers s ON rm.supplier_id = s.id 
-- WHERE rm.quantity <= rm.threshold
-- ORDER BY (rm.quantity / rm.threshold) ASC;

-- 3. Calculate how many vadapavs can be made
-- SELECT MIN(FLOOR(rm.quantity / cm.amount_per_unit)) as vadapavs_possible
-- FROM raw_materials rm
-- JOIN category_materials cm ON rm.id = cm.material_id
-- WHERE cm.category_id = 1; -- Vadapav category

-- 4. Calculate how many samosas can be made  
-- SELECT MIN(FLOOR(rm.quantity / cm.amount_per_unit)) as samosas_possible
-- FROM raw_materials rm
-- JOIN category_materials cm ON rm.id = cm.material_id
-- WHERE cm.category_id = 4; -- Samosa category

-- 5. Daily sales tracking (tables created above)

-- 6. Popular items report (Indian Rupees)
-- SELECT c.name, 
--        SUM(ds.quantity_sold) as total_sold, 
--        CONCAT('₹', SUM(ds.total_amount)) as revenue_inr,
--        CONCAT('₹', ROUND(AVG(ds.unit_price), 2)) as avg_price_inr
-- FROM daily_sales ds
-- JOIN categories c ON ds.category_id = c.id
-- WHERE ds.sale_date >= CURRENT_DATE - INTERVAL '7 days'
-- GROUP BY c.id, c.name
-- ORDER BY total_sold DESC;

-- 7. Calculate total inventory value in Indian Rupees
-- SELECT CONCAT('₹', SUM(quantity * cost_per_unit)) as total_inventory_value_inr 
-- FROM raw_materials;

-- 8. Profit calculation per item
-- SELECT c.name,
--        CONCAT('₹', c.selling_price) as selling_price_inr,
--        CONCAT('₹', calculate_material_cost(c.id)) as material_cost_inr,
--        CONCAT('₹', c.selling_price - calculate_material_cost(c.id)) as profit_per_unit_inr,
--        ROUND(((c.selling_price - calculate_material_cost(c.id)) / c.selling_price) * 100, 2) as profit_margin_percent
-- FROM categories c;

-- 9. Today's profit summary
-- SELECT 
--     CONCAT('₹', total_revenue) as revenue_inr,
--     CONCAT('₹', total_cost) as cost_inr,
--     CONCAT('₹', total_profit) as profit_inr,
--     CONCAT(profit_margin_percent, '%') as margin
-- FROM profit_summary 
-- WHERE summary_date = CURRENT_DATE;

-- 10. Weekly profit report
-- SELECT 
--     summary_date,
--     total_sales_count,
--     CONCAT('₹', total_revenue) as revenue_inr,
--     CONCAT('₹', total_profit) as profit_inr,
--     CONCAT(profit_margin_percent, '%') as margin
-- FROM profit_summary 
-- WHERE summary_date >= CURRENT_DATE - INTERVAL '7 days'
-- ORDER BY summary_date DESC;

-- 11. Most profitable items
-- SELECT 
--     c.name,
--     SUM(ds.quantity_sold) as units_sold,
--     CONCAT('₹', SUM(ds.total_profit)) as total_profit_inr,
--     CONCAT('₹', ROUND(AVG(ds.profit_per_unit), 2)) as avg_profit_per_unit_inr
-- FROM daily_sales ds
-- JOIN categories c ON ds.category_id = c.id
-- WHERE ds.sale_date >= CURRENT_DATE - INTERVAL '7 days'
-- GROUP BY c.id, c.name
-- ORDER BY SUM(ds.total_profit) DESC;

-- 7. Supplier contact list for reordering
-- SELECT DISTINCT s.name, s.whatsapp, s.phone,
--        STRING_AGG(rm.name, ', ') as materials_supplied
-- FROM suppliers s
-- JOIN raw_materials rm ON s.id = rm.supplier_id
-- WHERE rm.quantity <= rm.threshold
-- GROUP BY s.id, s.name, s.whatsapp, s.phone;