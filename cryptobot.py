import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import cryptocompare

TOKEN = '0000000000:0000000000000000000000000000000000'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

#/start-----
@dp.message_handler(commands=['start'])
async def send_message(message: types.Message):
    await message.reply("👋Привіт. Я вмію показувати поточну ціну криптовалют.\n✍️Напиши */help* щоб дізнатися як мною користуватися.", parse_mode="Markdown")

#/help-----
@dp.message_handler(commands=['help'])
async def send_message(message: types.Message):
    await message.reply("⚙️*Список команд:*"+
    "\n*/start* — _запустити бота._"+
    "\n*/help* — _це повідомлення._"+
    "\n*/p* — _ціна BTC у $_"+
    "\n*/p* BTC — _ціна BTC у $_"+
    "\n*/p* BTC USD — _ціна BTC к USD_"+
    "\n\nℹ️*BTC* та *USD* - були використані для прикладу. Боту доступні всі звичайні валюти та криптовалюти.", parse_mode="Markdown")

#/p-----
@dp.message_handler(commands=['p'])
async def p(message: types.Message):
    args = message.text.split()
    crypto_currency = args[1].upper() if len(args) > 1 else "BTC"
    fiat_currency = args[2].upper() if len(args) > 2 else "USD"
    sUSD = "$"
    sEUR = "€"
    sUAH = "₴"
    symbols = {"USD": sUSD, "EUR": sEUR, "UAH": sUAH}
    price = cryptocompare.get_price(crypto_currency, currency=fiat_currency, full=False)

    if not price:
        await message.reply("⚙️Ця пара валют не підтримується або сталася помилка під час отримання курсу.")
        return

    currency_symbol = symbols.get(fiat_currency, "")
    await message.reply(f"— *{crypto_currency} к {fiat_currency}:*\n— *{currency_symbol} {price[crypto_currency][fiat_currency]}*", parse_mode="Markdown")

if __name__ == '__main__':
    executor.start_polling(dp)
