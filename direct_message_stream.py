import time
import tweepy
import tweepy.models


class DirectMessageStream():
    def __init__(self, api: tweepy.API, interval=60):
        self.api = api
        self.interval = interval
        self.messages = []
        api.wait_on_rate_limit = True

    def on_message(self, data: tweepy.models.DirectMessage):
        return data

    def filter(self):
        first = False
        while True:
            messages = self.api.get_direct_messages(count=10)
            if first == False:
                self.messages = list((message for message in messages))
                first = True
                time.sleep(self.interval)
                continue
            for message in messages:
                if len(self.messages) != 0:
                    if self.messages[0].id == message.id:
                        break
                self.on_message(message)
            if len(messages) > 0:
                self.messages = messages

            time.sleep(self.interval)
