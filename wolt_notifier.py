import json
import os
import requests
import threading

from flask import Flask
from flask import request
from slack import WebClient

CHECK_INTERVAL = 5.0

SLACK_TOKEN = os.getenv('SLACK_TOKEN')

if SLACK_TOKEN is None:
    print('SLACK_TOKEN is not defined in environment variables')
    exit(1)

SLACK_CLIENT = WebClient(SLACK_TOKEN)

URL_SEARCH = 'https://restaurant-api.wolt.com/v1/search?sort=releveancy&q=%s/'
URL_REST_INFO = 'https://restaurant-api.wolt.com/v3/venues/slug/%s/'

SCHEDULED_CHECKS = {}

app = Flask(__name__)

def send_message(user_id, text):
    SLACK_CLIENT.chat_postMessage(
        channel=user_id,
        text=text,
        response_type="in_channel"
    )

def check():
    users_to_delete = []

    for user_id in SCHEDULED_CHECKS:
        slug = SCHEDULED_CHECKS[user_id]
        response = requests.get(URL_REST_INFO % SCHEDULED_CHECKS[user_id])

        if response.status_code != 200:
            continue

        result = response['results'][0]

        # Prefer Hebrew name
        try:
            rest_name = list(filter(lambda x: x["lang"] == "he", result["name"]))[
                0]["value"]
        except:
            rest_name = list(filter(lambda x: x["lang"] == "en", result["name"]))[
                0]["value"]

        is_online = result['online']
        order_url = result['public_url']

        if is_online:
            send_message(
                user_id,
                f'Yay! :sunglasses: *{rest_name}* is available for orders <{order_url}|here>.'
            )

            users_to_delete.append(user_id)

    for user_id in users_to_delete:
        del SCHEDULED_CHECKS[user_id]

    t = threading.Timer(CHECK_INTERVAL, check)
    t.daemon = True
    t.start()

def find_restaurant(query):
    response = requests.get(URL_SEARCH % query)

    if response.status_code != 200:
        return 'Unable to contact Wolt servers; please try again in a few minutes.'

    results = response.json()['results']

    ret = []

    for result in results[:10]:
        # Prefer Hebrew name
        try:
            rest_name = list(filter(lambda x: x["lang"] == "he", result["value"]["name"]))[
                0]["value"]
        except:
            rest_name = list(filter(lambda x: x["lang"] == "en", result["value"]["name"]))[
                0]["value"]

        slug = result['value']['slug']

        ret.append((rest_name, slug))

    return ret

@app.route('/', methods=['POST'])
def hello_world():
    user_id = request.form['user_id']
    command = request.form['command']
    text = request.form['text']
    channel_id = request.form['channel_id']

    if command == '/wolt':
        if text == 'cancel':
            if user_id in SCHEDULED_CHECKS:
                del SCHEDULED_CHECKS[user_id]

            return 'I removed your scheduled notification! :smile: Type `/wolt [restaurant_name]` to start again!'
        
        if user_id in SCHEDULED_CHECKS:
            return 'It seems there is already a scheduled notification set for you :cry:. Type `/wolt cancel` to cancel it!'

        try:
            results = find_restaurant(text)
        except:
            return "I didn't find any results matching this restaurant name :cry:. Try to be more specific!"

        attachments = [
                {
                    "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "callback_id": "game_selection",
                    "actions": [
                        {
                            "name": "rest_list",
                            "text": "Pick a restaurant...",
                            "type": "select",
                            "options": [

                            ]
                        }
                    ]
                }
            ]

        for result in results:
            attachments[0]['actions'][0]['options'].append(
                {
                    "text": result[0],
                    "value": f'{result[0]};{result[1]}'
                },
            )

        return {
            'text': "Choose a restaurant from the list and I will notify you when it's available for orders!",
            'attachments': attachments
        }

@app.route("/interactive_callback", methods=["POST"])
def interactive_callback():
    print('Got interactive!', flush=True)
    payload = json.loads(request.form['payload'])
    user_id = payload['user']['id']
    user_name = payload['user']['name']
    pair = payload['actions'][0]['selected_options'][0]['value'].split(';')
    rest_name = pair[0]
    slug = pair[1]

    SCHEDULED_CHECKS[user_id] = slug

    return f'Awesome! I will notify you as soon as {rest_name} is available for orders! :smile:'

if __name__ == '__main__':
    check()
    app.run(debug=True, host='0.0.0.0', port=80)
