def initLogger(path):
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s[%(levelname)s]> %(message)s", datefmt="[%Y-%m-%d][%H:%M:%S]")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def isDiscordID(name):
    # Discord IDs are the same for servers, users, channels, ...
    if (len(name := str(name)) == 17 or 18) and name.isdigit():
        return True
    return False
