# TwitterSA

BC CSCI339 (Natural Language Processing) Final Project

A Twitter sentiment analysis web app written with Flask.

## Setup

The standalone app can be run on localhost with `python TwitterSA.py` and
requires just Flask and Tweepy.

This is a heroku app, using gunicorn as the web server.

    pip install -r requirements.txt

`python TwitterSA.py` or `foreman start`

Either specify Twitter keys manually with the `--keys` argument, declare them
as environment variables (`CONSUMER_KEY` and `CONSUMER_SECRET`), or set them in
`.env` and run with `foreman` or Heroku.
