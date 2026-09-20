import os
from app.database import (
    get_todays_list,
    update_veg_list,
    save_order,
    get_todays_orders,
    get_customer
)
from app.whatsapp import send_text, format_veg_list

OWNER_PHONE = os.getenv("OWNER_PHONE")


# ── Option 1: Today's vegetable list ──────────────────────────────

def send_veg_list(phone: str):
    veg_doc = get_todays_list()
    send_text(phone, format_veg_list(veg_doc))


# ── Option 3: Price list ──────────────────────────────────────────

def send_prices(phone: str):
    veg_doc = get_todays_list()
    if not veg_doc or not veg_doc.get("items"):
        send_text(phone, "Price list is being updated. Please call 8590012647.")
        return

    lines = ["💰 *Today's Prices — Haritham*\n"]
    for item in veg_doc["items"]:
        lines.append(f"  {item['name']}: ₹{item['price']}/{item['unit']}")
    lines.append("\nPrices may vary. Reply *2* to place an order.")
    send_text(phone, "\n".join(lines))


# ── Option 2: Order flow ──────────────────────────────────────────
#
# Simple stateless approach: ask customer to list their items in one
# message in the format:  "Vendakka 1kg, Cheera 500g, Cucumber 2"
# Then confirm and forward to owner.
#
# (A full multi-step stateful flow can be added later with a
#  sessions collection in MongoDB.)

# ── Option 2: Order flow ──────────────────────────────────────────

def start_order(phone: str):

    veg_doc = get_todays_list()

    if not veg_doc or not veg_doc.get("items"):

        send_text(
            phone,
            "Sorry, today's list isn't ready yet. Please call 8590012647."
        )
        return

    lines = ["🛒 *Place Your Order*\n"]

    for item in veg_doc["items"]:

        stock = item.get("stock", "Available")

        lines.append(
            f"• {item['name']} - ₹{item['price']}/{item['unit']}"
        )

        lines.append(
            f"  Available: {stock}"
        )

        lines.append("")

    lines.append("Simply type your order like:")
    lines.append("Cheera 500g")
    lines.append("Vendakka 1kg")
    lines.append("")
    lines.append("Multiple items:")
    lines.append("Cheera 500g, Vendakka 1kg")

    send_text(phone, "\n".join(lines))


def process_order(phone: str, text: str):

    veg_doc = get_todays_list()

    if not veg_doc or not veg_doc.get("items"):
        send_text(
            phone,
            "Sorry, today's vegetable list is not available."
        )
        return

    # Accept both:
    # ORDER: Cheera 500g
    # Cheera 500g

    raw = text.strip()

    if raw.lower().startswith("order:"):
        raw = raw[6:].strip()

    item_strings = [
        s.strip()
        for s in raw.split(",")
        if s.strip()
    ]

    if not item_strings:
        send_text(
            phone,
            "Please send your order like:\n\nCheera 500g"
        )
        return

    items = []

    for s in item_strings:

        parts = s.split()

        if len(parts) < 2:

            send_text(
                phone,
                f"❌ Couldn't understand: {s}\n\nExample:\nCheera 500g"
            )
            return

        items.append({
            "veg": " ".join(parts[:-1]),
            "qty": parts[-1]
        })

    valid_products = {
        item["name"].lower()
        for item in veg_doc["items"]
    }

    for item in items:

        if item["veg"].lower() not in valid_products:

            send_text(
                phone,
                f"❌ {item['veg']} is not available today."
            )
            return

    customer = get_customer(phone)

    customer_name = (
        customer.get("name")
        if customer and customer.get("name")
        else phone
    )

    order_id = save_order(
        phone=phone,
        name=customer_name,
        items=items
    )

    order_id = str(order_id)

    item_lines = "\n".join(
        f"• {i['veg']} — {i['qty']}"
        for i in items
    )

    send_text(
    phone,
    f"✅ *Order Confirmed, {customer_name}!*\n\n"
    f"{item_lines}\n\n"
    f"📍 Pickup from Mevada from 7:30 AM\n"
    f"📞 Questions? Call 8590012647\n\n"
    f"Order ID: #{order_id[-6:].upper()}"
)

    if OWNER_PHONE:

     send_text(
        OWNER_PHONE,
        f"🔔 *New Order*\n\n"
        f"Customer: {customer_name}\n"
        f"Phone: {phone}\n\n"
        f"{item_lines}\n\n"
        f"Order ID: #{order_id[-6:].upper()}"
    )


# ── Admin: update today's veg list ───────────────────────────────
#
# Owner sends:  UPDATE: Vendakka 40/kg, Cheera 30/bunch, Cucumber 20/pc
#

def handle_admin_update(phone: str, text: str):

    if phone != OWNER_PHONE:
        send_text(
            phone,
            "Sorry, admin commands are only for the owner."
        )
        return

    raw = text[len("update:"):].strip()

    entries = [
        e.strip()
        for e in raw.split(",")
        if e.strip()
    ]

    items = []

    for entry in entries:

        parts = entry.split(maxsplit=1)

        if len(parts) != 2:
            continue

        veg_name = parts[0]
        details = parts[1]

        values = details.split("/")

        items.append({
            "name": veg_name,
            "price": values[0] if len(values) > 0 else "0",
            "unit": values[1] if len(values) > 1 else "kg",
            "stock": values[2] if len(values) > 2 else ""
        })

    update_veg_list(items)

    print(items)  # temporary debug

    names = ", ".join(i["name"] for i in items)

    send_text(
        phone,
        f"✅ List updated!\n\n{names}\n\nBroadcast will go out at 7:00 AM tomorrow."
    )