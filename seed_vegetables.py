from app.database import update_veg_list

update_veg_list([
    {"name": "Vendakka", "price": 40, "unit": "kg"},
    {"name": "Cheera", "price": 30, "unit": "bunch"},
    {"name": "Cucumber", "price": 25, "unit": "kg"}
])

print("Vegetables added successfully!")