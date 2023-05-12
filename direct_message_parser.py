import re
import tweepy
import tweepy.models


class DirectMessageParser():
    def __init__(self, tweet: tweepy.models.DirectMessage) -> None:
        self.tweet = tweet 

    def clean_tweet_text(self):
        text = self.tweet.message_create['message_data']['text']
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

    # return list
    def get_urls(self):
        attachment = self.tweet.message_create['message_data']['attachment']
        #IF IMAGE
        if attachment['media']['type'] == "photo":
            media_url = attachment['media']['media_url_https']
            return media_url

        #IF VIDEO
        if attachment['media']['type'] == "video":
            bitrate_array = []
            video_variants = attachment["media"]['video_info']['variants']
            for video in video_variants:
                bitrate_array.append(video.get('bitrate',0)) #keyにbitrateが存在しない場合 0 が追加される
            max_index = bitrate_array.index(max(bitrate_array))
            video_url = video_variants[max_index]['url']
            video_url = video_url.split('?')[0]
            return video_url
        
        #IF GIF
        if attachment['media']['type'] == "animated_gif":
            gif_url = attachment["media"]['video_info']['variants'][0]["url"]
            return gif_url
        
        #Except
        return None

    def get_media_type(self):
        attachment = self.tweet.message_create['message_data']['attachment']

        if attachment['media']['type'] == "photo":
            return "IMAGE"

        if attachment['media']['type'] == "video":
            return "VIDEO"

        if attachment['media']['type'] == "animated_gif":
            return "GIF"
    
    def get_source_tweet_id(self):
        if self.tweet.in_reply_to_status_id != None:
            return self.tweet.in_reply_to_status_id
        elif hasattr(self.tweet, "quoted_status_id") == True:
            return self.tweet.quoted_status_id
        else:
            return self.tweet.id