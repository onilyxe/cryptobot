import matplotlib.pyplot as plt
import cryptocompare
import requests
import datetime
import aiogram
import asyncio
import os
import re

from aiogram.client.bot import DefaultBotProperties
from aiogram import Bot, Dispatcher, types
from pycoingecko import CoinGeckoAPI
from aiogram.types import BotCommand
from aiogram.filters import Command
from collections import defaultdict

# Задаємо токен і створюємо об'єкт бота із зазначенням parse_mode через DefaultBotProperties
TOKEN = '0000000000:0000000000000000000000000000000000'
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))

# Створюємо Router для реєстрації обробників
router = aiogram.Router()

# Створюємо екземпляр CoinGeckoAPI
cg = CoinGeckoAPI()

# Отримуємо список криптовалют для маппінгу символів та ідентифікаторів
crypto_list = cg.get_coins_list()
symbol_to_ids = defaultdict(list)
for coin in crypto_list:
    symbol_to_ids[coin['symbol'].lower()].append(coin['id'])


# Обробник команди /start
@router.message(Command('start'))
async def send_start_message(message: types.Message):
    await message.reply("👋 Привіт. Я вмію показувати поточну ціну криптовалют, та інше. Напиши /help, щоб дізнатися, як мною користуватися")

# Обробник команди /help
@router.message(Command('help'))
async def send_help_message(message: types.Message):
    await message.reply(
        "⚙️ Список команд:\n"
        "/start — запустити бота\n"
        "/help — це повідомлення\n"
        "/p `[amount]` `[crypto]` `[fiat]` — ціна криптовалюти\n"
        "/h `[crypto]` `[repiod]` — історія ціни криптовалюти за вказаний період (7, 30, 60, 90, 365 або 'рік')\n"
        "/i `[crypto]` — інформація про криптовалюту\n"
        "/fg — індекс страху та жадібності\n"
        "\nУ команді /p не обов'язково вказувати всі три значення"
    )


# Обробник команди /fg
@router.message(Command('fg'))
async def get_fear_and_greed_index(message: types.Message):
    try:
        response = requests.get('https://api.alternative.me/fng/?limit=1')
        if response.status_code == 200:
            data = response.json()
            value = data['data'][0]['value']
            value_classification = data['data'][0]['value_classification']
            timestamp = data['data'][0]['timestamp']
            readable_date = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%Y')

            message_text = (
                f"{value_classification} - *{value}*/100\n\n"
                f"🚀 *Індекс страху і жадності*"
                f"\n⏰ Оновлено: {readable_date}"
            )

            await message.reply(message_text)
        else:
            await message.reply("⚠️ Неможливо отримати дані")
    except Exception as e:
        await message.reply(f"⚠️: {e}")
        print(f"Ошибка: {e}")


# Обробник команди /p
@router.message(Command('p'))
async def get_crypto_price(message: types.Message):
    args = message.text.split()

    symbols = {
        "USD": "$", 
        "EUR": "€", 
        "UAH": "₴"
    }

    try:
        if len(args) == 1:
            crypto_currency = "BTC"
            fiat_currency = "USD"
            amount = 1
        elif len(args) == 2:
            crypto_currency = args[1].upper()
            fiat_currency = "USD"
            amount = 1
        elif len(args) == 3:
            try:
                amount = float(args[1])
                crypto_currency = args[2].upper()
                fiat_currency = "USD"
            except ValueError:
                crypto_currency = args[1].upper()
                fiat_currency = args[2].upper()
                amount = 1
        elif len(args) == 4:
            amount = float(args[1])
            crypto_currency = args[2].upper()
            fiat_currency = args[3].upper()
        else:
            await message.reply("⚠️ Використовуй: /p [amount] [crypto] [fiat]")
            return

        price = cryptocompare.get_price(crypto_currency, currency=fiat_currency, full=False)

        if not price:
            await message.reply("⚠️ Неможливо отримати дані")
            return

        currency_symbol = symbols.get(fiat_currency, "")
        price_value = price[crypto_currency][fiat_currency] * amount
        formatted_price = f"{currency_symbol}{price_value:,.2f}"
        await message.reply(f"{amount} {crypto_currency} до {fiat_currency}\n=*{formatted_price}*")
    except ValueError:
        await message.reply("⚠️ Неможливо отримати дані")
    except Exception as e:
        await message.reply(f"⚠️: {e}")
        print(f"Ошибка: {e}")

# Обробник команди /h
@router.message(Command('h'))
async def get_crypto_history(message: types.Message):
    try:
        args = message.text.split()
        crypto_currency = args[1].upper() if len(args) > 1 else "BTC"

        valid_periods = {
            '7': 7,
            '30': 30,
            '60': 60,
            '90': 90,
            '365': 365,
            'year': 365,
            'рік': 365
        }

        if len(args) > 2:
            period_arg = args[2].lower()
            period = valid_periods.get(period_arg, 365)
        else:
            period = 365

        limit = period - 1

        current_timestamp = int(datetime.datetime.now().timestamp())

        history_data = cryptocompare.get_historical_price_day(
            crypto_currency,
            currency="USD",
            limit=limit,
            toTs=current_timestamp
        )

        if not history_data:
            await message.reply("⚠️ Неможливо отримати дані")
            return

        dates = [data['time'] for data in history_data]
        prices = [data['close'] for data in history_data]

        readable_dates = [datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d') for ts in dates]

        plt.figure(figsize=(10, 6))
        plt.plot(readable_dates, prices, label=f"{crypto_currency} Price (USD)")
        plt.xlabel("Дата")
        plt.ylabel("Ціна в USD")
        plt.title(f"{crypto_currency} — Історія ціни за останні {period} днів")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(True)

        image_path = f"{crypto_currency}_history.png"
        plt.savefig(image_path)
        plt.close()

        photo = types.FSInputFile(image_path)
        caption = f"Графік {crypto_currency} за останні {period} днів"
        await message.reply_photo(photo=photo, caption=caption)

        if os.path.exists(image_path):
            os.remove(image_path)

    except Exception as e:
        await message.reply(f"⚠️: {e}")
        print(f"Ошибка: {e}")

# Обработчик команды /i
@router.message(Command('i'))
async def get_crypto_info(message: types.Message):
    try:
        args = message.text.split()
        user_input = args[1].lower() if len(args) > 1 else 'btc'

        coin_ids = symbol_to_ids.get(user_input)
        if not coin_ids:
            await message.reply("⚠️ Неможливо отримати дані")
            return

        market_data = cg.get_coins_markets(vs_currency='usd', ids=coin_ids)

        if not market_data:
            await message.reply("⚠️ Неможливо отримати дані")
            return

        coin = max(market_data, key=lambda x: x.get('market_cap', 0))

        name = coin.get('name', 'N/A')
        symbol = coin.get('symbol', 'N/A').upper()
        current_price = coin.get('current_price', 'N/A')
        market_cap = coin.get('market_cap', 'N/A')
        total_volume = coin.get('total_volume', 'N/A')

        def format_number(value):
            if isinstance(value, (int, float)):
                return f"{value:,.2f}"
            return value

        current_price = format_number(current_price)
        market_cap = format_number(market_cap)
        total_volume = format_number(total_volume)

        coin_id = coin.get('id')
        coin_details = cg.get_coin_by_id(coin_id)
        description = coin_details.get('description', {}).get('en', '')

        description = re.sub('<.*?>', '', description)

        paragraphs = description.split('\n\n')
        first_paragraph = next((p for p in paragraphs if p.strip()), '')
        description = first_paragraph.strip()

        if len(description) > 500:
            description = description[:500].rsplit(' ', 1)[0] + '...'

        message_text = (
            f"*{name} ({symbol})*\n\n"
            f"💰 *Ціна*: ${current_price}\n"
            f"💹 *Ринкова капіталізація*: ${market_cap}\n"
            f"🔄 *Обсяг торгів за 24ч*: ${total_volume}\n\n"
            f"*Опис*:\n{description}"
        )

        await message.reply(message_text)

    except Exception as e:
        await message.reply(f"⚠️: {e}")
        print(f"Ошибка: {e}")

# Запуск бота
async def main():
    dp = Dispatcher()
    dp.include_router(router)

    commands = [
    BotCommand(command="/p", description="- [amount] [crypto] [fiat] - ціна криптовалюти"),
    BotCommand(command="/h", description="- [crypto] - історія ціни криптовалюти"),
    BotCommand(command="/i", description="- [crypto] - інформація про криптовалюту"),
    BotCommand(command="/fg", description="- індекс страху та жадібності")]

    await bot.set_my_commands(commands)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
