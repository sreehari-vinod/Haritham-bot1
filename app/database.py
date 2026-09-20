from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime
from pymongo import MongoClient

# --------------------------------------------------
# MONGODB CONNECTION
# --------------------------------------------------

client = MongoClient(os.getenv("MONGO_URI"))

db = client["haritham"]

customers_col = db["customers"]
vegetables_col = db["vegetables"]
orders_col = db["orders"]

# --------------------------------------------------
# INDEXES
# --------------------------------------------------

customers_col.create_index(
    "phone",
    unique=True
)

orders_col.create_index(
    "created_at"
)

vegetables_col.create_index(
    "active"
)

# --------------------------------------------------
# CUSTOMERS
# --------------------------------------------------

def get_all_active_customers():
    """
    Return all customers who haven't opted out.
    """
    return list(
        customers_col.find(
            {"opted_out": False}
        )
    )


def get_customer(phone: str):
    return customers_col.find_one(
        {"phone": phone}
    )


def upsert_customer(
    phone: str,
    name: str = None,
    tag: str = "new"
):
    existing = customers_col.find_one(
        {"phone": phone}
    )

    if existing:
        customers_col.update_one(
            {"phone": phone},
            {
                "$set": {
                    "opted_out": False
                }
            }
        )
        return

    customers_col.insert_one({
        "phone": phone,
        "name": name or "",
        "tag": tag,
        "opted_out": False,
        "joined_at": datetime.utcnow()
    })


def set_customer_name(
    phone: str,
    name: str
):
    customers_col.update_one(
        {"phone": phone},
        {
            "$set": {
                "name": name
            }
        },
        upsert=True
    )


def customer_has_name(
    phone: str
):
    customer = customers_col.find_one(
        {"phone": phone}
    )

    if not customer:
        return False

    return bool(
        customer.get("name")
    )


def opt_out_customer(
    phone: str
):
    customers_col.update_one(
        {"phone": phone},
        {
            "$set": {
                "opted_out": True
            }
        }
    )

# --------------------------------------------------
# VEGETABLE LIST
# --------------------------------------------------

def get_todays_list():
    """
    Return currently active vegetable list.
    """
    return vegetables_col.find_one(
        {"active": True},
        sort=[("updated_at", -1)]
    )


def update_veg_list(
    items: list[dict]
):
    """
    Example:

    [
        {
            "name": "Cheera",
            "price": 30,
            "unit": "bunch"
        },
        {
            "name": "Tomato",
            "price": 40,
            "unit": "kg"
        }
    ]
    """

    vegetables_col.update_many(
        {},
        {"$set": {"active": False}}
    )

    vegetables_col.insert_one({
        "active": True,
        "updated_at": datetime.utcnow(),
        "items": items
    })

# --------------------------------------------------
# ORDERS
# --------------------------------------------------

def save_order(
    phone: str,
    name: str,
    items: list,
    pickup: bool = True
):
    """
    items:

    [
        {
            "veg": "Cheera",
            "qty": "500g"
        }
    ]
    """

    order = {
        "phone": phone,
        "customer_name": name,
        "items": items,
        "pickup": pickup,
        "status": "new",
        "created_at": datetime.utcnow()
    }

    result = orders_col.insert_one(
        order
    )

    return str(
        result.inserted_id
    )


def get_todays_orders():
    today = datetime.utcnow().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    return list(
        orders_col.find({
            "created_at": {
                "$gte": today
            }
        })
    )


def get_customer_orders(
    phone: str
):
    return list(
        orders_col.find(
            {"phone": phone}
        ).sort(
            "created_at",
            -1
        )
    )

# --------------------------------------------------
# ORDER TOTAL CALCULATION
# --------------------------------------------------

def calculate_order_total(
    items
):
    veg_doc = get_todays_list()

    if not veg_doc:
        return 0

    prices = {}

    for item in veg_doc["items"]:
        try:
            prices[
                item["name"].lower()
            ] = float(
                item["price"]
            )
        except Exception:
            continue

    total = 0

    for item in items:

        veg = item["veg"].lower()

        if veg in prices:
            total += prices[veg]

    return round(total, 2)

    def customer_has_name(phone: str):
     customer = customers_col.find_one({"phone": phone})

    if not customer:
        return False

    return bool(customer.get("name"))


def set_customer_name(phone: str, name: str):
    customers_col.update_one(
        {"phone": phone},
        {"$set": {"name": name}},
        upsert=True
    )