"""
Run this once to add sample data to MongoDB for local testing.
Usage:  python scripts/seed_db.py
"""
from dotenv import load_dotenv
load_dotenv()

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import update_veg_list, upsert_customer

# Sample vegetable list
sample_vegs = [
    {"name": "Vendakka (Okra)",     "price": 40,  "unit": "kg"},
    {"name": "Cheera (Amaranth)",   "price": 30,  "unit": "bunch"},
    {"name": "Cucumber",            "price": 25,  "unit": "kg"},
    {"name": "Kovakka (Ivy gourd)", "price": 35,  "unit": "kg"},
    {"name": "Thannimathan (Watermelon)", "price": 20, "unit": "kg"},
]

# Sample customers (use real numbers later)
sample_customers = [
    {"phone": "919999999991", "name": "Test Customer 1"},
    {"phone": "919999999992", "name": "Test Customer 2"},
]

update_veg_list(sample_vegs)
print("✅ Vegetable list seeded")

for c in sample_customers:
    upsert_customer(c["phone"], c["name"])
print(f"✅ {len(sample_customers)} test customers added")

print("\nDone! Run:  python main.py")
