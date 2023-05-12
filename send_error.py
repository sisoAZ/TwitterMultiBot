import requests
import traceback

discord_webhook = "https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxxx"

def send_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                json = {"content": f"Error\n```{traceback.format_exc()}```"}
                requests.post(discord_webhook, data=json)
                print("Error" + traceback.format_exc())
            except Exception as e:
                pass
    return wrapper

def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__: # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate