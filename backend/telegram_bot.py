#!/usr/bin/env python3
"""
Simple Telegram bot for DZ Clothes admin.
Run: python telegram_bot.py
When admin sends /start, the bot replies with their chat_id.
"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    print("Set TELEGRAM_BOT_TOKEN in .env (from @BotFather)")
    exit(1)

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    r = requests.get(url, params=params, timeout=35)
    return r.json()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)

def save_chat_id(chat_id):
    try:
        from db import get_cursor
        with get_cursor(commit=True) as cur:
            cur.execute(
                """INSERT INTO admin_settings (key, value, updated_at) VALUES ('telegram_chat_id', %s, CURRENT_TIMESTAMP)
                   ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP""",
                (str(chat_id),),
            )
        return True
    except Exception as e:
        print("Could not save to DB:", e)
        return False

def main():
    print("DZ Clothes Telegram bot running. Send /start to your bot to get your chat_id.")
    offset = None
    while True:
        try:
            data = get_updates(offset=offset)
            if not data.get("ok"):
                continue
            for u in data.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message") or u.get("edited_message")
                if not msg:
                    continue
                chat_id = msg["chat"]["id"]
                text = (msg.get("text") or "").strip()
                if text == "/start":
                    save_chat_id(chat_id)
                    send_message(
                        chat_id,
                        f"✅ DZ Clothes – Notifications activées.\n\n"
                        f"Votre chat_id: {chat_id}\n"
                        f"Vous recevrez une notification à chaque nouvelle commande.",
                    )
        except Exception as e:
            print("Error:", e)
        import time
        time.sleep(1)

if __name__ == "__main__":
    main()
