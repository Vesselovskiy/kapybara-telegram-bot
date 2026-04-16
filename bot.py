#import os 
#import asyncio
#import aiohttp
#from telegram import Bot
#from urllib.parse import urlparse, parse_qs
#
#TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
#CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",")
#
#URLS = [
#    'https://prs-cdp-prod-webapiproxy.azurewebsites.net/api/v2/kdp/webshop/product/10583/menu/timeslots?date=2025-07-08',
#    'https://prs-cdp-prod-webapiproxy.azurewebsites.net/api/v2/kdp/webshop/product/10583/menu/timeslots?date=2025-07-09',
#]
#
#def extract_date_from_url(url: str) -> str:
#    parsed = urlparse(url)
#    return parse_qs(parsed.query).get("date", ["неизвестно"])[0]
#
#async def check_slots():
#    bot = Bot(token=TELEGRAM_BOT_TOKEN)
#
#    async with aiohttp.ClientSession() as session:
#        for url in URLS:
#            try:
#                async with session.get(url, timeout=10) as resp:
#                    if resp.status != 200:
#                        print(f"Ошибка: статус {resp.status} для URL {url}")
#                        continue
#
#                    data = await resp.json()
#                    if data:
#                        date = extract_date_from_url(url)
#                        message = f"Найден слот для даты: {date}"
#                        print (message)
#                        for chat_id in CHAT_IDS:
#                            if chat_id.strip():
#                                await bot.send_message(chat_id=chat_id.strip(), text=message)
#            except Exception as e:
#                print(f"Ошибка при запросе {url}: {e}")
#
#if __name__ == "__main__":
#        asyncio.run(check_slots())

import os
import requests
from urllib.parse import urlparse

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS = [chat_id.strip() for chat_id in os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if chat_id.strip()]

URLS = [
    "https://www.arla.se/event-sponsring/koslapp/stockholm/backa-karsta-vallentuna/",
]

FULLY_BOOKED_TEXT = "Fullbokat!"


def extract_place_from_url(url: str) -> str:
    parts = [p for p in urlparse(url).path.split("/") if p]
    try:
        idx = parts.index("koslapp")
        return parts[idx + 1]
    except (ValueError, IndexError):
        return "unknown"


def send_telegram_message(text: str) -> None:
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    for chat_id in CHAT_IDS:
        try:
            response = requests.post(
                telegram_url,
                json={
                    "chat_id": chat_id,
                    "text": text,
                },
                timeout=15,
            )
            response.raise_for_status()
            print(f"Сообщение отправлено в chat_id={chat_id}")
        except Exception as e:
            print(f"Ошибка отправки в chat_id={chat_id}: {e}")


def check_slots() -> None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    for url in URLS:
        try:
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code != 200:
                print(f"Ошибка {response.status_code}: {url}")
                continue

            html = response.text

            if FULLY_BOOKED_TEXT not in html:
                place = extract_place_from_url(url)
                message = f"Есть слоты: {place}\n{url}"
                print(message)
                send_telegram_message(message)
            else:
                print(f"Все занято: {url}")

        except Exception as e:
            print(f"Ошибка при запросе {url}: {e}")


if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("Не задан TELEGRAM_BOT_TOKEN")
    if not CHAT_IDS:
        raise ValueError("Не задан TELEGRAM_CHAT_IDS")

    check_slots()
