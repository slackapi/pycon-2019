import json
import os
from flask import Flask
from slackeventsapi import SlackEventAdapter
import slack

# In order for our application to verify the authenticity
# of requests from Slack, we'll compare the request signature
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]

# Create an instance of SlackEventAdapter, passing in our Flask server so it can bind the
# Slack specific routes. The `endpoint` param specifies where to listen for Slack event traffic.
slack_events_adapter = SlackEventAdapter(
  slack_signing_secret,
  endpoint="/slack/events"
)

# Create an instance of SlackClient for your bot to make Web API requests,
# passing your app's Bot Token.
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_client = slack.WebClient(token=slack_bot_token)


# When someone posts a message saying `hi` to our bot, we'll
# have the bot respond with "Hello @user! :tada:"
@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    # Get the message metadata from the `event` portion of the request.
    message = event_data["event"]

    # We're logging out the payload so you can see it's anatomy
    print(json.dumps(message, indent=4, sort_keys=True))

    # If the incoming message contains "hi", then respond with a "Hello" message
    # the `subtype` check filters out messages from other bot users.
    if message.get("subtype") is None and "hi" in message['text']:
        channel = message["channel"]
        message = "Hello <@%s>! :tada:" % message["user"]
        slack_client.chat_postMessage(channel=channel, text=message)


# Echo the user's reaction back in a thread
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]

    channel = event["item"]["channel"]
    thread_ts = event['item']['ts']

    # Get the reactji name from the event payload
    emoji_name = event["reaction"]

    # Reply to the message on which the reaction was added, in a thread, with the ractji as the message.
    text = ":{}:".format(emoji_name)
    slack_client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=text)


slack_events_adapter.start(port=3000)
