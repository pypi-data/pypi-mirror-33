import os


def _hook_url(chat_id):
    return '{protocol}://{host}/hooks/{chat_id}/{hash}'.format(
        protocol='http',
        host=os.environ['CATCHBOT_GLOBAL_HOST'],
        chat_id=chat_id,
        hash='kljgfvgerf'
    )


def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='\n'.join([
            'Hi!',
            '',
            "I'm the bot to catch your hooks",
            '',
            'Send your hooks here: {}'.format(
                _hook_url(update.message.chat_id)
            ),
        ]),
    )
