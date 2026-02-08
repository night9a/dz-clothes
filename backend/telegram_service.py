"""Send admin notifications to Telegram."""
import os
import requests

def get_admin_chat_id():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
    if chat_id:
        return chat_id
    if not token:
        return None
    try:
        from db import get_cursor
        with get_cursor(commit=False) as cur:
            cur.execute("SELECT value FROM admin_settings WHERE key = 'telegram_chat_id'")
            row = cur.fetchone()
            return row['value'] if row else None
    except Exception:
        return None

def send_telegram_notification(message: str) -> bool:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = get_admin_chat_id()
    if not token or not chat_id:
        return False
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False

def notify_new_order(order_number: str, total: float, email: str, items_summary: str):
    msg = (
        f"🛒 <b>Nouvelle commande DZ Clothes</b>\n"
        f"Numéro: <code>{order_number}</code>\n"
        f"Total: {total:.2f} DA\n"
        f"Client: {email}\n"
        f"Articles:\n{items_summary}"
    )
    return send_telegram_notification(msg)
