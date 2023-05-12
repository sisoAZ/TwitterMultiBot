import pickle
import tweepy
from pathlib import Path
from tweepy_authlib import CookieSessionUserHandler
from getpass import getpass


def auth(screen_name):
    # Cookie を保存するファイルが存在する場合
    if Path(f"{screen_name}_COOKIE.pickle").exists():

        # 保存した Cookie を読み込む
        with open(f"{screen_name}_COOKIE.pickle", 'rb') as f:
            cookies = pickle.load(f)

        # 読み込んだ RequestCookieJar オブジェクトを CookieSessionUserHandler に渡す
        auth_handler = CookieSessionUserHandler(cookies=cookies)

        return auth_handler

    # スクリーンネームとパスワードを指定して認証
    else:

        # スクリーンネームとパスワードを渡す
        # スクリーンネームとパスワードを指定する場合は初期化時に認証のための API リクエストが多数行われるため、完了まで数秒かかる
        try:
            password = getpass(f"Enter password for {screen_name}:")
            auth_handler = CookieSessionUserHandler(
                screen_name=screen_name, password=password)
        except tweepy.HTTPException as ex:
            # パスワードが間違っているなどの理由で認証に失敗した場合
            if len(ex.api_codes) > 0 and len(ex.api_messages) > 0:
                error_message = f'Code: {ex.api_codes[0]}, Message: {ex.api_messages[0]}'
            else:
                error_message = 'Unknown Error'
            raise Exception(
                f'Failed to authenticate with password ({error_message})')
        except tweepy.TweepyException as ex:
            # 認証フローの途中で予期せぬエラーが発生し、ログインに失敗した
            error_message = f'Message: {ex}'
            raise Exception(
                f'Unexpected error occurred while authenticate with password ({error_message})')

        # 現在のログインセッションの Cookie を取得
        cookies = auth_handler.get_cookies()

        # Cookie を pickle 化して保存
        with open(f"{screen_name}_COOKIE.pickle", 'wb') as f:
            pickle.dump(cookies, f)

        return auth_handler
