# 🌱 Haritham WhatsApp Bot

WhatsApp bot for Haritham Karshaka Sangham — daily vegetable broadcasts,
interactive menu, and order collection.

---

## Setup (local)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Fill in your .env file
Edit `.env` and add your real values:
- `WHATSAPP_TOKEN` — from Meta Developer dashboard (permanent token)
- `WHATSAPP_PHONE_ID` — the Phone Number ID (not the number itself)
- `VERIFY_TOKEN` — any secret string you choose
- `MONGO_URI` — from MongoDB Atlas → Connect → Drivers
- `OWNER_PHONE` — your WhatsApp number with country code, no + (e.g. 919946754725)

### 3. Seed the database with sample data
```bash
python scripts/seed_db.py
```

### 4. Run the bot
```bash
python main.py
```
Server starts at http://localhost:5000

### 5. Expose to the internet (for Meta webhook)
Meta needs a public HTTPS URL to call your webhook.
Use ngrok for local testing:
```bash
# Install ngrok from https://ngrok.com, then:
ngrok http 5000
```
Copy the `https://xxxx.ngrok.io` URL.

### 6. Set webhook in Meta dashboard
- Go to developers.facebook.com → your app → WhatsApp → Configuration
- Webhook URL: `https://xxxx.ngrok.io/webhook`
- Verify token: same string as VERIFY_TOKEN in your .env
- Subscribe to: `messages`

---

## How the admin updates the daily vegetable list

The owner sends a WhatsApp message to the bot number:

```
UPDATE: Vendakka 40/kg, Cheera 30/bunch, Cucumber 25/kg, Watermelon 20/kg
```

The bot saves it and confirms. The 7 AM broadcast will use this list.

---

## File structure

```
haritham_bot/
├── main.py              ← Flask webhook server (start here)
├── requirements.txt
├── .env                 ← your secrets (never commit this)
├── app/
│   ├── database.py      ← MongoDB helpers
│   ├── whatsapp.py      ← API sender + message formatter
│   ├── handlers.py      ← menu options, order flow, admin commands
│   └── scheduler.py     ← 7 AM broadcast cron job
└── scripts/
    └── seed_db.py       ← add sample data for testing
```

---

## Next steps (when ready to deploy)
1. Push to GitHub
2. Create Railway.app project → connect repo → add env vars
3. Railway auto-deploys on every git push
