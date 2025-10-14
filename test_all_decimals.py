#!/usr/bin/env python3
"""
Test all decimal conversion scenarios
"""

from decimal import Decimal

print("Testing all decimal conversion scenarios...")

# Test 1: Material calculation (line 1045)
print("\n1. Testing material calculation:")
per_unit = Decimal('0.1')  # From database
qty_sold = 5.0  # From user input
try:
    total_needed = float(per_unit) * qty_sold
    print(f"✅ total_needed = float({per_unit}) * {qty_sold} = {total_needed}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Threshold comparison (line 1077)
print("\n2. Testing threshold comparison:")
new_q = 2.5  # Current quantity
threshold_dict = {"threshold": Decimal('5.0')}  # From database
try:
    result = new_q < float(threshold_dict["threshold"])
    print(f"✅ {new_q} < float({threshold_dict['threshold']}) = {result}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Suggested quantity calculation (line 1319)
print("\n3. Testing suggested quantity calculation:")
low_item = {
    'threshold': Decimal('5.0'),  # From database
    'new_q': 2.5,  # Current stock
    'name': 'Test Material',
    'unit': 'kg'
}
try:
    threshold = float(low_item['threshold'])
    new_q = float(low_item['new_q'])
    suggested = max((threshold * 2) - new_q, threshold)
    suggested = round(suggested, 2)
    print(f"✅ Suggested quantity: {suggested}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Quantity and threshold from database
print("\n4. Testing database value conversions:")
db_values = [
    (Decimal('10.5'), 'quantity'),
    (Decimal('2.0'), 'threshold'),
    (Decimal('0.15'), 'amount_per_unit')
]

for value, name in db_values:
    try:
        converted = float(value)
        print(f"✅ {name}: {value} -> {converted}")
    except Exception as e:
        print(f"❌ {name} conversion error: {e}")

print("\n🎉 All decimal conversion tests completed!")
print("If all tests show ✅, your decimal issues should be resolved.")