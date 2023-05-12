import re
import tweepy
import tweepy.models


class TweetParser():
    def __init__(self, tweet: tweepy.models.Status) -> None:
        self.tweet = tweet    

    def clean_tweet_text(self):
        text = self.tweet.full_text
        # テキストからURLを削除する正規表現
        url_pattern = re.compile(r'https?://\S+')

        # テキストからユーザー名を削除する正規表現
        username_pattern = re.compile(r'@[^\s]+')

        # URLを削除
        text = re.sub(url_pattern, '', text)

        # ユーザー名を削除
        text = re.sub(username_pattern, '', text)

        # テキストのみを返す
        return text.strip()

    # Media url, Media type (IMAGE|VIDEO|GIF)
    def fetch_media_urls(self):
        tweet = self.tweet
        # ただのリツイートだった場合
        if f"RT" in tweet.full_text:
            return None, None
        # 画像が添付されていた場合
        if hasattr(tweet, "extended_entities") == True:
            urls = self.get_urls()
            media_type = self.get_media_type()
            return urls, media_type
        # Mediaがなかった場合
        else:
            return None, None

    # return list
    def get_urls(self):
        tweet = self.tweet
        # IF IMAGE
        if tweet.extended_entities["media"][0]["type"] == "photo":
            media_urls = []
            for media in tweet.extended_entities["media"]:
                media_urls.append(media["media_url_https"])
            return media_urls

        # IF VIDEO
        if tweet.extended_entities["media"][0]["type"] == "video":
            bitrate_array = []
            video_variants = tweet.extended_entities["media"][0]['video_info']['variants']
            for video in video_variants:
                # keyにbitrateが存在しない場合 0 が追加される
                bitrate_array.append(video.get('bitrate', 0))
            max_index = bitrate_array.index(max(bitrate_array))
            video_url = video_variants[max_index]['url']
            video_url = video_url.split('?')[0]
            return [video_url]

        # IF GIF
        if tweet.extended_entities["media"][0]["type"] == "animated_gif":
            gif_url = tweet.extended_entities["media"][0]['video_info']['variants'][0]["url"]
            return [gif_url]

        # Except
        return None

    def get_media_type(self):
        tweet = self.tweet
        if tweet.extended_entities["media"][0]["type"] == "photo":
            return "IMAGE"

        if tweet.extended_entities["media"][0]["type"] == "video":
            return "VIDEO"

        if tweet.extended_entities["media"][0]["type"] == "animated_gif":
            return "GIF"
    
    def get_source_tweet_id(self):
        if self.tweet.in_reply_to_status_id != None:
            return self.tweet.in_reply_to_status_id
        elif hasattr(self.tweet, "quoted_status_id") == True:
            return self.tweet.quoted_status_id
        else:
            return self.tweet.id