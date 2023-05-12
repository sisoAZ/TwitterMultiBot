import configparser

config = configparser.ConfigParser(interpolation=None)

def load_config(file="config.ini", *, match=None):
    auth_list = []
    config.read(file)
    for section in config.sections():
        if match is not None:
            if match.lower() in section.lower():
                return dict(config[section])
            for value in config[section].values():
                if match.lower() in value.lower():
                    return dict(config[section])
        auth = dict(config[section])
        auth_list.append(auth)
    return auth_list

load_config()
