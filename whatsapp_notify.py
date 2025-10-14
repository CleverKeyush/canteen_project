# whatsapp_notify.py
import os
import urllib.parse
import webbrowser
from db import get_connection

TWILIO_ENABLED = os.getenv("TWILIO_ENABLED", "false").lower() == "true"
if TWILIO_ENABLED:
    try:
        from twilio.rest import Client
        TWILIO_SID = os.getenv("TWILIO_SID")
        TWILIO_AUTH = os.getenv("TWILIO_AUTH")
        TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")  # e.g. whatsapp:+1415...
        client = Client(TWILIO_SID, TWILIO_AUTH)
    except Exception as e:
        print("Twilio init error:", e)
        TWILIO_ENABLED = False

def log_notification(supplier_id, message, via):
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO notification_log (supplier_id, message, via) VALUES (%s, %s, %s)",
                    (supplier_id, message, via))
        conn.commit()
        conn.close()
    except Exception:
        try:
            conn.rollback()
            conn.close()
        except:
            pass

def send_whatsapp_twilio(supplier_whatsapp, message_text, supplier_id=None):
    """
    supplier_whatsapp: '+919876543210'
    Returns (True, sid) or (False, error)
    """
    if not TWILIO_ENABLED:
        return False, "Twilio not enabled"
    try:
        to = "whatsapp:" + supplier_whatsapp.lstrip('+')
        from_ = os.getenv("TWILIO_WHATSAPP_FROM")
        msg = client.messages.create(body=message_text, from_=from_, to=to)
        log_notification(supplier_id, message_text, 'twilio')
        return True, msg.sid
    except Exception as e:
        return False, str(e)

def open_whatsapp_web(supplier_whatsapp, message_text, supplier_id=None):
    """
    Opens wa.me URL in browser — user must press Send.
    """
    number = supplier_whatsapp.lstrip('+').replace(' ', '')
    encoded = urllib.parse.quote(message_text)
    url = f"https://wa.me/{number}?text={encoded}"
    try:
        webbrowser.open(url)
    except Exception as e:
        print("Failed to open browser:", e)
    log_notification(supplier_id, message_text, 'wa.me')
    return True, url
