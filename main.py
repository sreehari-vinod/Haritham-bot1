from dotenv import load_dotenv
load_dotenv()

import os
import logging

from flask import Flask, request, jsonify

from app.scheduler import start_scheduler, run_morning_broadcast

from app.database import (
    upsert_customer,
    opt_out_customer,
    get_all_active_customers,
    get_todays_orders,
    get_todays_list,
    customer_has_name,
    set_customer_name
)

from app.whatsapp import send_text

from app.handlers import (
    send_veg_list,
    start_order,
    send_prices,
    handle_admin_update,
    process_order
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

OWNER_NUMBERS = {
    os.getenv("OWNER_PHONE_1", ""),
    os.getenv("OWNER_PHONE_2", "")
}

GREETINGS = {
    "hi",
    "hello",
    "hai",
    "start",
    "ഹലോ"
}

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# --------------------------------------------------
# FLASK APP
# --------------------------------------------------

app = Flask(__name__)

# --------------------------------------------------
# WEBHOOK VERIFICATION
# --------------------------------------------------

@app.get("/webhook")
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verified by Meta")
        return challenge, 200

    logger.warning("Webhook verification failed")
    return "Forbidden", 403


# --------------------------------------------------
# INCOMING MESSAGES
# --------------------------------------------------

@app.post("/webhook")
def receive_message():

    data = request.get_json(silent=True) or {}

    try:

        entry = data["entry"][0]
        changes = entry["changes"][0]["value"]

        if "messages" not in changes:
            return jsonify({"status": "ignored"}), 200

        msg = changes["messages"][0]

        sender = msg["from"]
        msg_type = msg["type"]

        logger.info(
            f"Incoming message | From={sender} | Type={msg_type}"
        )

        if msg_type != "text":

            send_text(
                sender,
                "⚠️ Please send a text message only."
            )

            return jsonify({"status": "ok"}), 200

        text = msg["text"]["body"].strip()

        upsert_customer(sender)

        handle_message(sender, text)

    except (KeyError, IndexError) as e:

        logger.error(
            f"Unexpected WhatsApp payload structure: {e}"
        )

    except Exception as e:

        logger.exception(
            f"Unhandled error: {e}"
        )

    return jsonify({"status": "ok"}), 200


# --------------------------------------------------
# MESSAGE ROUTER
# --------------------------------------------------

def handle_message(phone: str, text: str):

    lower = text.lower().strip()
        # First-time customer name collection

    if not customer_has_name(phone):

        # Ignore greetings

        if lower not in GREETINGS:

            set_customer_name(phone, text.strip())

            send_text(
                phone,
                f"🙏 Thank you {text.strip()}!\n\n"
                "Welcome to Haritham Karshaka Sangham 🌱"
            )

            send_menu(phone)
            return

        send_text(
            phone,
            "🌱 Welcome to Haritham!\n\n"
            "Please enter your name:"
        )
        return
    # ------------------------------------
    # NATURAL ORDER DETECTION
    # ------------------------------------

    veg_doc = get_todays_list()

    if veg_doc and veg_doc.get("items"):

        veg_names = [
            item["name"].lower()
            for item in veg_doc["items"]
        ]

        if lower.startswith("order:") or any(
            veg_name in lower
            for veg_name in veg_names
        ):
            process_order(phone, text)
            return

    # ------------------------------------
    # UNSUBSCRIBE
    # ------------------------------------

    if lower in ("stop", "unsubscribe", "opt out"):
        opt_out_customer(phone)

        send_text(
            phone,
            "✅ You have been unsubscribed.\n\nReply HI anytime to join again."
        )

        return

    # ------------------------------------
    # GREETING
    # ------------------------------------

    if lower in GREETINGS:
        send_menu(phone)
        return

    # ------------------------------------
    # ADMIN COMMANDS
    # ------------------------------------

    if lower.startswith("update:"):

        if phone not in OWNER_NUMBERS:

            send_text(
                phone,
                "❌ You are not authorized."
            )

            return

        handle_admin_update(phone, text)
        return

    # MANUAL BROADCAST

    if lower == "broadcast":

        if phone not in OWNER_NUMBERS:

            send_text(
                phone,
                "❌ Not authorized."
            )

            return

        run_morning_broadcast()

        send_text(
            phone,
            "✅ Broadcast sent successfully."
        )

        return

    # STATS

    if lower == "stats":

        if phone not in OWNER_NUMBERS:

            send_text(
                phone,
                "❌ Not authorized."
            )

            return

        customers = get_all_active_customers()
        orders = get_todays_orders()
        vegetables = get_todays_list() or {"items": []}

        send_text(
            phone,
            f"📊 Haritham Stats\n\n"
            f"👥 Customers: {len(customers)}\n"
            f"📦 Today's Orders: {len(orders)}\n"
            f"🥬 Vegetables: {len(vegetables['items'])}"
        )

        return

    # ORDERS REPORT

    if lower == "orders":

        if phone not in OWNER_NUMBERS:

            send_text(
                phone,
                "❌ Not authorized."
            )

            return

        orders = get_todays_orders()

        if not orders:

            send_text(
                phone,
                "📦 No orders today."
            )

            return

        msg = "📦 Today's Orders\n\n"

        for i, order in enumerate(orders, start=1):

            msg += f"{i}. {order['phone']}\n"

            for item in order["items"]:
                msg += f"   • {item['veg']} - {item['qty']}\n"

            msg += "\n"

        send_text(phone, msg[:4000])

        return

    # ------------------------------------
    # CUSTOMER MENU OPTIONS
    # ------------------------------------

    if lower == "1":
        send_veg_list(phone)
        return

    if lower == "2":
        start_order(phone)
        return

    if lower == "3":
        send_prices(phone)
        return

    if lower == "4":

        send_text(
            phone,
            "📍 Location: Mevada, Mutholi, Kerala\n"
            "⏰ Timings: 7:30 AM onwards (Mon-Sat)\n"
            "📞 8590012647\n"
            "📞 9946754725"
        )

        return

    if lower == "5":

        send_text(
            phone,
            "👨‍🌾 Talk to Owner\n\n"
            "📞 8590012647\n"
            "📞 9946754725"
        )

        return

    # ------------------------------------
    # UNKNOWN INPUT
    # ------------------------------------

    send_text(
        phone,
        "❓ Sorry, I didn't understand that."
    )

    send_menu(phone)


# --------------------------------------------------
# MENU
# --------------------------------------------------

def send_menu(phone: str):

    send_text(
        phone,
        "🌱 Haritham Karshaka Sangham\n\n"
        "Please reply with a number:\n\n"
        "1️⃣ Today's Vegetables\n"
        "2️⃣ Place Order\n"
        "3️⃣ Prices / Rates\n"
        "4️⃣ Location & Timings\n"
        "5️⃣ Talk to Owner\n\n"
        "Reply STOP anytime to unsubscribe."
    )


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def health():

    return {
        "status": "running",
        "service": "Haritham WhatsApp Bot"
    }, 200


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":

    scheduler = start_scheduler()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )