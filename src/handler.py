import config
import responses
import logging

from pokemon import Pokemon
from threading import Lock


def report_errors(func):
    def catcher(bot, update):
        try:
            func(bot, update)
        except Exception as e:
            error(bot, update, e)
    return catcher

def maintainer_only(func):
    def assert_maintainer(bot, update):
        if str(update.message.chat_id) != config.MAINTAINER_ID:
            unknown(bot, update)
            return

        func(bot, update)
    return assert_maintainer

def error(bot, update, e):
    text = 'Error on @whoisthatpokemonbot\nUpdate: {}\nError type: {}'.format(update, type(e))

    if str(e):
        text += '\nError: {}'.format(e)

    logging.getLogger().error(text)

    bot.sendMessage(chat_id=config.MAINTAINER_ID,
                    text=text)

# @report_errors
# def start(bot, update):
#     bot.sendMessage(chat_id=update.message.chat_id,
#                     text=responses.start)

@report_errors
def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=responses.help,
                    disable_web_page_preview=True)

@report_errors
def unknown(bot, update):
    if update.message.chat_id > 0: # user
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=responses.unknown_command)

class GameManager:
    def __init__(self):
        self.games = {}
        self.mutex = Lock()

    def new(self, bot, update, gen=None):
        try:
            p = Pokemon.random(gen)

            print(p)

            with self.mutex:
                self.games[update.message.chat_id] = p

            with open(p.shadow, 'rb') as photo:
                bot.sendPhoto(chat_id=update.message.chat_id,
                              photo=photo,
                              caption=responses.new)

        except Exception as e:
            error(bot, update, e)

    def default(self, bot, update):
        try:
            word = update.message.text.lower()

            p = None

            with self.mutex:
                for k in self.games.keys():
                    if word == self.games[k].name:
                        p = self.games[k]
                        del self.games[k]
                        break

            if p:
                if update.message.chat_id > 0: # user
                    resp = responses.reveal(p)
                else:
                    resp = responses.revealgroup(p, update.message.from_user.first_name)

                with open(p.artwork, 'rb') as photo:
                    bot.sendPhoto(chat_id=update.message.chat_id,
                                  photo=photo,
                                  caption=resp)

        except Exception as e:
            error(bot, update, e)

    def job(self, bot):
        pass

if __name__ == '__main__':
    pass
