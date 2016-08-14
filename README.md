# bot

A telegram bot.

This is the source behind the Telegram bot [@eth0]( https://telegram.me/eth0_bot ).

**The above statement is not true anymore since 2015.12.15. This project is left here in the hope that it would be helpful, it will not receive any update anymore, and the source code might be (or have already been) out dated. If you want examples and tutorials about Telegram bot in Python, please refer to [the python-telegram-bot project](https://github.com/python-telegram-bot/python-telegram-bot/) .**

# Notice

* Due to the evolution of upstream package `python-telegram-bot`, most of the code is no longer following best practice, and will be refactored once I have time.
* This project is under construction on `x-develop` branch.

If you've got some inspirations from it, it would be nice to
have them shared publicly (of course it's up to you).

# Usage

```bash
# git clone this project
[sudo] pip install -r requirements.txt
cp config.json.default config.json
# and edit config.json for your real configuration
python -u worker.py # this starts the rq worker
python app.py # this starts the flask webserver
# and you might want to put the flask webserver behind nginx or something
```

# License

BSD license, see LICENSE file.
