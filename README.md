# 🪙 CryptoBot for Telegram
Telegram bot that shows price of cryptocurrencies

[Try the my bot](https://t.me/CCryptoBBot)

About
------------
**A simple telegram bot that shows the price of cryptocurrencies. Used by the Cryptocompare API. The bot also works in group chats.**

Installation
------------
```shell
# Clone the repository
$ git clone https://github.com/onilyxe/CryptoBot.git

# Change the working directory to CryptoBot
$ cd CryptoBot
```

Configuring
------------
**Open the `cryptobot.py` configuration file with a text editor and set the token on line 7**
```ini
TOKEN = '0000000000:0000000000000000000000000000000000'
```
* `TOKEN` is token for your Telegram bot. You can get it here: [BotFather](https://t.me/BotFather)

Running
------------
Using Python
```shell
# Install requirements
$ python3 -m pip install -r requirements.txt

# Run script
$ python3 cryptobot.py
```