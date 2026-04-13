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
import asyncio
import aiohttp
from telegram import Bot
from urllib.parse import urlparse

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS = [chat_id.strip() for chat_id in os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if chat_id.strip()]

URLS = [
    "https://www.arla.se/event-sponsring/koslapp/stockholm/backa-karsta-vallentuna/",
    "https://www.arla.se/event-sponsring/koslapp/stockholm/finngarne-gard-norrtalje/",
    "https://www.arla.se/event-sponsring/koslapp/gotland/gotland-gront-centrum-roma/",
    "https://www.arla.se/event-sponsring/koslapp/uppsala/lovsta-lantbruksforskning/",
    "https://www.arla.se/event-sponsring/koslapp/uppsala/yrkesgymnasium-jalla/",
]

FULLY_BOOKED_TEXT = "Fullbokat!"


def extract_place_from_url(url: str) -> str:
    """
    Берет часть URL после /koslapp/ и до следующего /.
    Пример:
    https://www.arla.se/event-sponsring/koslapp/stockholm/backa-karsta-vallentuna/
    -> stockholm
    """
    path_parts = [part for part in urlparse(url).path.split("/") if part]

    # Ожидается примерно:
    # ["event-sponsring", "koslapp", "stockholm", "backa-karsta-vallentuna"]
    try:
        koslapp_index = path_parts.index("koslapp")
        return path_parts[koslapp_index + 1]
    except (ValueError, IndexError):
        return "unknown"


async def send_message_to_all(bot: Bot, text: str) -> None:
    for chat_id in CHAT_IDS:
        try:
            await bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            print(f"Ошибка отправки в chat_id={chat_id}: {e}")


async def check_page(session: aiohttp.ClientSession, bot: Bot, url: str) -> None:
    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=20),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            },
        ) as response:
            if response.status != 200:
                print(f"Ошибка: статус {response.status} для URL {url}")
                return

            html = await response.text()

            if FULLY_BOOKED_TEXT not in html:
                place = extract_place_from_url(url)
                message = f"Есть слоты: {place}\n{url}"
                print(message)
                await send_message_to_all(bot, message)
            else:
                print(f"Все занято: {url}")

    except Exception as e:
        print(f"Ошибка при проверке {url}: {e}")


async def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("Не задан TELEGRAM_BOT_TOKEN")
    if not CHAT_IDS:
        raise ValueError("Не задан TELEGRAM_CHAT_IDS")

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    async with aiohttp.ClientSession() as session:
        tasks = [check_page(session, bot, url) for url in URLS]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())