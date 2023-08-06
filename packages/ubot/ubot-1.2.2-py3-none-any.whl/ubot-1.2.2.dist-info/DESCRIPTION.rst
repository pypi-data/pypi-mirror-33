########
Microbot
########

A *very* minimal class that implements the basic Telegram bot functionalities.
Can (should) be extended depending on needs.

Quickstart
==========

To install the dependencies inside a virtualenv run ``make install`` (requires pipenv).

The webhook must be manually set with a GET to the following URL:
https://api.telegram.org:443/bot<token>/setWebhook?url=<webhook_url>
where <token> is the Telegram-given token and <webhook_url> is the url you want the webhook to point to.
In case you want to reset it, just GET to the same url without parameters.

Docs (work in progress): https://strychnide.github.io/ubot/

**TODO:** documentation, testing

