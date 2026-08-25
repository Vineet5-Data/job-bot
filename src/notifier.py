import requests
import time
from typing import Dict, Any

def send_telegram_alert(token: str, chat_id: str, job: Dict[str, Any]):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    text = f"""🎯 <b>New Student Role Found!</b>

📌 <b>Title:</b> {job.get('title', 'N/A')}
🏢 <b>Company:</b> {job.get('company', 'N/A')}
📍 <b>Location:</b> {job.get('location', 'N/A')}
📡 <b>Source:</b> {job.get('source', 'N/A')}

🔗 <a href="{job.get('url', '#')}">Apply Directly</a>"""

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")

    time.sleep(0.5)
