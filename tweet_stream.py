import tweepy
import tweepy.models
import time


class StreamingClient:
    def __init__(self, api: tweepy.API, interval=5):
        self.api = api
        self.interval = interval
        self.tweets = []
        self.api.wait_on_rate_limit = True

    def on_tweet(self, data: tweepy.models.Status):
        return data

    def filter(self, query):
        first = False
        while True:
            tweets = []
            # 最新のツイートを取得
            new_tweets = tweepy.Cursor(
                self.api.search_tweets, q=query, result_type="recent", count=5, tweet_mode="extended").items(5)

            # 初回のみツイートを取得
            if first == False:
                self.tweets = list((tweet for tweet in new_tweets))
                first = True
                time.sleep(self.interval)
                continue

            for tweet in new_tweets:
                if len(self.tweets) != 0:
                    # 既に取得済みのツイートは無視
                    if tweet in self.tweets:
                        break
                tweets.append(tweet)

            for tweet in tweets:
                self.on_tweet(tweet)
            # 更新があった場合はツイートを更新
            if len(tweets) > 0:
                self.tweets = tweets

            time.sleep(self.interval)
