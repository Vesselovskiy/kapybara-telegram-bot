import os
import requests
from telegram import Bot
from urllib.parse import urlparse, parse_qs

TELEGRAM_BOT_TOKEN = "7806138706:AAG53Jhb0GGHFY27DhkVHW6z1Xu1fW2VX6E"#os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS = "409897409" #os.getenv("TELEGRAM_CHAT_IDS", "").split(",")

URLS = [
    'https://prs-cdp-prod-webapiproxy.azurewebsites.net/api/v2/kdp/webshop/product/10583/menu/timeslots?date=2025-07-08',
    'https://prs-cdp-prod-webapiproxy.azurewebsites.net/api/v2/kdp/webshop/product/10583/menu/timeslots?date=2025-07-09',
]

def extract_date_from_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('date', ['неизвестно'])[0]

def check_slots():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    for url in URLS:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data:
                date = extract_date_from_url(url)
                message = f"Найден слот для даты: {date}"
                for chat_id in CHAT_IDS:
                    if chat_id.strip():
                        bot.send_message(chat_id=chat_id.strip(), text=message)

        except Exception as e:
            print(f"Ошибка при запросе {url}: {e}")

if __name__ == "__main__":
    check_slots()