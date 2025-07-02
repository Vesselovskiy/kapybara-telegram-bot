import os
import asyncio
import aiohttp
from telegram import Bot
from urllib.parse import urlparse, parse_qs

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",")

URLS = [
    'https://prs-cdp-prod-webapiproxy.azurewebsites.net/api/v2/kdp/webshop/product/10583/menu/timeslots?date=2025-07-08',
    'https://prs-cdp-prod-webapiproxy.azurewebsites.net/api/v2/kdp/webshop/product/10583/menu/timeslots?date=2025-07-09',
]

def extract_date_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parse_qs(parsed.query).get("date", ["неизвестно"])[0]

async def check_slots():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    async with aiohttp.ClientSession() as session:
        for url in URLS:
            try:
                async with session.get(url, timeout=10) as resp:
                    if resp.status != 200:
                        print(f"Ошибка: статус {resp.status} для URL {url}")
                        continue

                    data = await resp.json()
                    if data:
                        date = extract_date_from_url(url)
                        message = f"Найден слот для даты: {date}"
                        print (message)
                        for chat_id in CHAT_IDS:
                            if chat_id.strip():
                                await bot.send_message(chat_id=chat_id.strip(), text=message)
            except Exception as e:
                print(f"Ошибка при запросе {url}: {e}")

if __name__ == "__main__":
        asyncio.run(check_slots())