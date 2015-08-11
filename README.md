# bot

A telegram bot.

This is the source behind the Telegram bot [@eth0]( https://telegram.me/eth0_bot ).

# Notice

This might not be a general bot that you could just setup and run,
because it uses an MQTT broker to connect with a RaspberryPi.

You might want to review the code before you use it.

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
