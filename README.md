# Slack Wolt Notifier

A Slack bot that notifies you when a Wolt restaurant or venue is available for orders.

## How does it work?

Slack supports bots that can automate tasks and run code, so why not use this awesome feature to notify users when their favorite restaurant on Wolt is available for orders?

The bot is simply a Flask server that processes slash commands received from Slack to a pre-defined endpoint. When a user types `/wolt [restaurant_name]`, the bot will work against Wolt's public API to search for the name and send back the results. Once the user selects a restaurant from the list, the bot will periodically poll Wolt's API again to check whether or not the requested restaurant is open for orders or not. Once it's available for orders, the bot will notify the user in a direct message.
## Installation 

* Create a [basic Slack app](https://api.slack.com/authentication/basics) named `Wolt`, or whatever you choose.
* Generate a `Bot User OAuth Token` for the app (requires administrative permissions).
* Create a new "Slash Command" `/wolt` and input the URL of the server you plan to host this bot on (e.g. http://1.3.3.7/).
* Enable the "Interactivity" feature on your Slack app and use the same URL you used for the slash command for the `Request URL` field, but with a different endpoint (e.g. http://1.3.3.7/interactive_callback).
* Install the app in your organization's Slack (requires administrative permissions).
* Export the bot token to your environment variables under the key `SLACK_TOKEN`.
* Run the script anywhere you want (for security reasons, you might want to run it on a different port and [verify that the HTTP requests are coming from Slack](https://api.slack.com/authentication/verifying-requests-from-slack)).
## Screenshots

![App Screenshot](https://i.ibb.co/gwz14qH/wolt-demo.png)

  
