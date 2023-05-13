import datetime
import tweepy




class SusAccountBan():
    def __init__(self, api: tweepy.API):
        self.api = api
        self.user_limit = []
        self.created_at_cache = {}
        self.date = datetime.datetime.now()

    def created_at(self, user_id):
        if user_id in self.created_at_cache:
            return self.created_at_cache[user_id]
        user = self.api.get_user(user_id=user_id)
        self.created_at_cache[user_id] = user.created_at
        return user.created_at

    def check_user_limit(self, user_id):
        delta = datetime.datetime.now() - self.date
        # ○○分以上経過していたらリセット
        if delta.total_seconds() / 60 >= 15:
            self.date = datetime.datetime.now()
            self.user_limit.clear()
            return False
        for user in self.user_limit:
            if user_id in user:
                if user[user_id] >= 5:
                    self.api.create_block(user_id=user_id)
                    print("BANNED to " + str(user_id) + " because of spamming")
                    return True
                user[user_id] += 1
                return False
        self.user_limit.append({user_id: 1})
        return False

    def multiple_mentions(self, text):
        if text.count("@") >= 3:
            return True
        return False


if __name__ == "__main__":
    from config import load_config
    from auth import auth
    auth_list = load_config()
    accounts = []
    for auth_dict in auth_list:
        auth_handler = auth(auth_dict["screen_name"])

        api = tweepy.API(auth_handler)

        rate_limit = api.rate_limit_status()['resources']['direct_messages']['/direct_messages/events/list']

        # レートリミット情報の表示
        print("リセットまでの時間（秒）:", rate_limit['reset'])
        print("残りのリクエスト可能回数:", rate_limit['remaining'])
        print("リクエスト制限の総数:", rate_limit['limit'])
        sus = SusAccountBan(api)
        
        if sus.created_at(1653616672820051969) > datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=30):
            print("BAN")
        else:
            print("OK")
        messages = api.get_direct_messages(count=10)

        # 受信したダイレクトメッセージを表示
        #api.send_direct_message(recipient_id=1492114414413434880, text="test YOOO")
        for message in messages:
            sender = message.message_create['sender_id']
            text = message.message_create['message_data']['text']
            print(f"Sender: {sender}")
            print(f"Message: {text}")
            print("--------------------")