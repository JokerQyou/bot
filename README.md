# bot

A telegram bot.

This is the source behind the Telegram bot [@eth0]( https://telegram.me/eth0_bot ).

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
