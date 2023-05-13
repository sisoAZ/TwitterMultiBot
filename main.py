import datetime
import threading
from urllib.parse import urlparse

import tweepy.models
from config import load_config
from auth import auth
import tweepy
import os
from tweet_stream import StreamingClient
from direct_message_stream import DirectMessageStream
import wario.image, wario.video
import packager.process
from tweet_parser import TweetParser
from direct_message_parser import DirectMessageParser
from utils import file_download, make_download_link, init
from sus_account_ban import SusAccountBan
import json
from send_error import send_exception, for_all_methods


@for_all_methods(send_exception)
class TweetCatch(StreamingClient):
    def __init__(self, api: tweepy.API, interval=10):
        super().__init__(api, interval)
        self.me = api.verify_credentials()
        self.SusAccountBan = SusAccountBan(api)
        self.config = load_config(match=self.me.screen_name)
        self.accept_media_type = [
            media_type.lower()
            for media_type in json.loads(self.config["accept_media_types"])
        ]

    def on_tweet(self, data):
        print(data.full_text)

        # スパムアカウントは弾く
        if self.SusAccountBan.check_user_limit(data.user.id):
            return
        # 　アカウント登録からまだ一か月経っていないアカウントは弾く
        if self.SusAccountBan.created_at(data.user.id) > datetime.datetime.now(
            tz=datetime.timezone.utc
        ) - datetime.timedelta(days=30):
            return
        # メンションが3つ以上あるツイートは弾く
        if self.SusAccountBan.multiple_mentions(data.full_text):
            return

        threading.Thread(target=self.processer, args=(data,)).start()

    def processer(self, data: tweepy.models.Status):
        tweet_text = ""
        media_path = None

        # ツイートをパースする
        tweet = TweetParser(data)
        source_tweet = self.api.get_status(
            tweet.get_source_tweet_id(), tweet_mode="extended"
        )
        if source_tweet.user.id == self.me.id:
            return
        source_tweet = TweetParser(source_tweet)
        media_url, media_type = source_tweet.fetch_media_urls()
        text = tweet.clean_tweet_text()

        if media_url != None:
            if media_type.lower() not in self.accept_media_type:
                return
            process_media_path = file_download(media_url[0])

        if "@MadeInWarioBot".lower() in tweet.tweet.full_text.lower():
            if media_url == None:
                return
            if text == "":
                text = None
            if media_type == "IMAGE":
                media_path = wario.image.mergeImage(process_media_path, text)
            elif media_type == "VIDEO":
                media_path = wario.video.makeVideo(process_media_path, text)
            in_reply_to_tweet_id = data.id

        if "@NintendoPackage".lower() in tweet.tweet.full_text.lower():
            if media_url == None:
                return
            if media_type == "IMAGE":
                media_path = packager.process.mergeImage(process_media_path, text)
            in_reply_to_tweet_id = data.id
        if media_path is not None:
            media_category = (
                f"tweet_{media_type.lower()}" if media_type is not None else None
            )
            media_id = self.api.media_upload(
                media_path, chunked=True, media_category=media_category
            ).media_id

        if tweet_text == "" and media_path is None:
            return
        if in_reply_to_tweet_id is not None:
            if media_id is not None:
                self.api.update_status(
                    tweet_text,
                    media_ids=[media_id],
                    in_reply_to_status_id=in_reply_to_tweet_id,
                    auto_populate_reply_metadata=True,
                )
                os.remove(media_path)
                os.remove(process_media_path)


@for_all_methods(send_exception)
class CatchDirectMessage(DirectMessageStream):
    def __init__(self, api: tweepy.API, interval=30):
        super().__init__(api, interval)
        self.me = api.verify_credentials()
        self.SusAccountBan = SusAccountBan(api)
        self.config = load_config(match=self.me.screen_name)
        self.accept_media_type = [
            media_type.lower()
            for media_type in json.loads(self.config["accept_media_types"])
        ]

    def on_message(self, data: tweepy.models.DirectMessage):
        print(data.message_create["message_data"]["text"])
        # スパムアカウントは弾く
        if self.SusAccountBan.check_user_limit(data.message_create["sender_id"]):
            return
        if data.message_create["sender_id"] == self.me.id_str:
            return
        threading.Thread(target=self.processer, args=(data,)).start()

    def processer(self, data: tweepy.models.DirectMessage):
        tweet_text = ""
        media_path = None
        media_type = None
        media_url = None

        # ツイートをパースする
        tweet = DirectMessageParser(data)
        if "attachment" in data.message_create["message_data"]:
            media_type = tweet.get_media_type()
            media_url = tweet.get_urls()
        sender_id = data.message_create["sender_id"]

        if media_url != None:
            if media_type.lower() not in self.accept_media_type:
                return
            process_media_path = file_download(
                media_url, auth=self.api.auth.apply_auth()
            )
        text = tweet.clean_tweet_text()

        if media_url != None:
            if self.me.screen_name.lower() in "@MadeInWarioBot".lower():
                if media_url == None:
                    return
                if text == "":
                    text = None
                if media_type == "IMAGE":
                    media_path = wario.image.mergeImage(process_media_path, text)
                elif media_type == "VIDEO":
                    media_path = wario.video.makeVideo(process_media_path, text)

            if self.me.screen_name.lower() in "@NintendoPackage".lower():
                if media_url == None:
                    return
                if media_type == "IMAGE":
                    media_path = packager.process.mergeImage(process_media_path, text)

            link = make_download_link(media_path)
            tweet_text = f"Download Link: {link}"
        if tweet_text == "" and media_path is None:
            return
        if media_path is not None:
            media_id = self.api.media_upload(
                media_path, chunked=True, media_category=f"dm_{media_type.lower()}"
            ).media_id_string
            self.api.send_direct_message(
                sender_id,
                tweet_text,
                attachment_type="media",
                attachment_media_id=media_id,
            )
            os.remove(media_path)
            os.remove(process_media_path)
        else:
            self.api.send_direct_message(sender_id, tweet_text)


def main():
    auth_list = load_config()
    for auth_dict in auth_list:
        auth_handler = auth(auth_dict["screen_name"])

        api = tweepy.API(auth_handler)

        print(f"Logged in as {auth_dict['screen_name']}")

        stream = TweetCatch(api)
        #stream.interval = 1  # debug
        thread = threading.Thread(
            target=stream.filter, args=(auth_dict["screen_name"],)
        )
        thread.start()

        direct_message_stream = CatchDirectMessage(api)
        #direct_message_stream.interval = 1  # debug
        thread_dm = threading.Thread(target=direct_message_stream.filter)
        thread_dm.start()


if __name__ == "__main__":
    init()
    main()
