# MovieScrapingBot

`MovieScrapingBot` is a library for Python, which provide API to scrape count of sold seats for theprojector.sg and gv.com.sg websites.
It was designed as a simple, lightweight data collection library with the ability to control via telegram chat.

Installation
============

```
git clone https://github.com/T-Ivaniuk/MovieScrapingBot.git
```

Usage
=======


If you have `Gmail account with 3rd party API usage permission`, `telegram bot token`, which are minimum of requirements to start telegram bot,
you can replace suggested values in `configfile_utilits.py`
```python
telegramtoken = "TELEGRAM BOT TOKEN"
gmail_sender = "GMAIL ACCOUNT LOGIN"
gmail_password = "GMAIL 3RD PARTY PASSWORD"
telegramwhitelist = {
    telegram_user_id: "telegram_user@gmail.com",
}

folder_for_tg = "tg_files/"
```

