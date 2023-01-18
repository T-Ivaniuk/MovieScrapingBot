# MovieScrapingBot

`MovieScrapingBot` is a telegram bot, which allows you to scrape count of sold seats for theprojector.sg and gv.com.sg websites on specific day, create and recive report via Telegram and email.


[Obtaining Telegram bot token]( https://core.telegram.org/bots#how-do-i-create-a-bot )

[Obtaining Gmail 3rd party password]( https://www.youtube.com/watch?v=IWxwWFTlTUQ )

## Deploy Locally

- Clone the repo. 
`git clone https://github.com/T-Ivaniuk/MovieScrapingBot.git`

- Open Cloned Folder
`cd MovieScrapingBot`

- Create VirtualEnv
`python -m venv venv`

- Activate virtualenv
`.\venv\Scripts\activate`

- Install Requirements
`pip install -r requirements.txt`

- Fill configfile_utilits.py file

- Start MovieScrapingBot By
`python telegram.py`


Usage
=======


If you have `Gmail account with 3rd party API usage permission`, `telegram bot token`, which are minimum of requirement variables to start telegram bot,
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

