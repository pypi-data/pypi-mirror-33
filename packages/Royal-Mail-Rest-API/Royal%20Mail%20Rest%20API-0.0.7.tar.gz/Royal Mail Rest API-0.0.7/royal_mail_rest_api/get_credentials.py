import configparser


def return_credentials():
    config = configparser.ConfigParser()
    config.read('credentials.ini')
    return config


if __name__ == '__main__':
    return_credentials()
