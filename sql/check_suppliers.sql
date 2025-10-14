-- Check supplier assignments for all materials
SELECT 
    rm.id,
    rm.name as material_name,
    rm.supplier_id,
    s.name as supplier_name,
    s.whatsapp,
    s.phone
FROM raw_materials rm
LEFT JOIN suppliers s ON rm.supplier_id = s.id
ORDER BY rm.id;

-- Check materials without suppliers
SELECT 
    rm.id,
    rm.name as material_name,
    'NO SUPPLIER ASSIGNED' as issue
FROM raw_materials rm
WHERE rm.supplier_id IS NULL;

-- Check supplier summary
SELECT 
    s.id,
    s.name as supplier_name,
    s.whatsapp,
    COUNT(rm.id) as materials_count,
    STRING_AGG(rm.name, ', ') as materials_supplied
FROM suppliers s
LEFT JOIN raw_materials rm ON s.id = rm.supplier_id
GROUP BY s.id, s.name, s.whatsapp
ORDER BY s.id;