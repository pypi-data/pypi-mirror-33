import telegram.ext as tg

from .commands import commands


def create_updater(token):
    updater = tg.Updater(token=token)

    for command in commands:
        handler = tg.CommandHandler(command.__name__, command)
        updater.dispatcher.add_handler(handler)

    return updater
