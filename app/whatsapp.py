import os
import requests
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
TOKEN = os.getenv("WHATSAPP_TOKEN")

print("PHONE_ID =", PHONE_ID)
print("TOKEN EXISTS =", bool(TOKEN))
if not PHONE_ID:
    raise ValueError("WHATSAPP_PHONE_ID missing")

if not TOKEN:
    raise ValueError("WHATSAPP_TOKEN missing")

BUSINESS_PHONE = os.getenv(
    "BUSINESS_PHONE",
    "8590012647"
)

BUSINESS_LOCATION = os.getenv(
    "BUSINESS_LOCATION",
    "Mevada, Mutholi"
)

API_URL = (
    f"https://graph.facebook.com/v19.0/"
    f"{PHONE_ID}/messages"
)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


def send_text(to: str, message: str):

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }

    try:
     r = requests.post(
        API_URL,
        json=payload,
        headers=HEADERS,
        timeout=10,
    )

     print("STATUS:", r.status_code)
     print("RESPONSE:", r.text)

     r.raise_for_status()
     return r.json()

    except requests.exceptions.RequestException as e:
     print(f"WhatsApp send failed: {e}")
     return None


def send_template(to: str, template_name: str, params: list[str]):

    components = []

    if params:
        components.append({
            "type": "body",
            "parameters": [
                {"type": "text", "text": p}
                for p in params
            ],
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en"},
            "components": components,
        },
    }

    try:

        r = requests.post(
            API_URL,
            json=payload,
            headers=HEADERS,
            timeout=10,
        )

        r.raise_for_status()

        return r.json()

    except requests.exceptions.RequestException as e:

        print(f"Template send failed: {e}")

        return None


def format_veg_list(veg_doc: dict) -> str:
    """Turn a veg list document into a readable WhatsApp message."""
    if not veg_doc or not veg_doc.get("items"):
        return "Today's list is being updated. Please check back soon!"

    lines = ["🌱 *ഹരിതം കർഷക സംഘം* | Haritham Karshaka Sangham",
             "📍 Mevada, Mutholi  ⏰ From 7:30 AM\n",
             "*Today's fresh vegetables:*"]

    for item in veg_doc["items"]:
        lines.append(f"  ✅ {item['name']} — ₹{item['price']}/{item['unit']}")

    lines += [
        "",
        "📞 Order: 8590012647",
        "Reply *Hi* to place an order or check the menu.",
    ]
    return "\n".join(lines)
