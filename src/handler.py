import config
import responses
import logging

from collections import namedtuple
from threading import Lock
from pokemon import Pokemon

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

@report_errors
def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=responses.start)

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

TIME_TO_SOLVE = 5 # time 3 == 15 seconds

class PokemonEntry:
    def __init__(self, pokemon, time_left=TIME_TO_SOLVE):
        self.pokemon = pokemon
        self.time_left = time_left

    def __repr__(self):
        return '<PokemonEntry (pokemon={}, time_left={}) at {}>'.format(
                    self.pokemon, self.time_left, id(self))

class GameManager:
    def __init__(self):
        self.games = {}
        self.mutex = Lock()

    def new(self, bot, update, gen=6):
        try:
            if update.message.chat_id in self.games:
                bot.sendMessage(chat_id=update.message.chat_id,
                                text=responses.already_active)
                return

            p = Pokemon.random(gen)

            print(p)

            with self.mutex:
                self.games[update.message.chat_id] = PokemonEntry(p, TIME_TO_SOLVE)

            with open(p.shadow, 'rb') as photo:
                bot.sendPhoto(chat_id=update.message.chat_id,
                              photo=photo,
                              caption=responses.new)

        except Exception as e:
            error(bot, update, e)

    def default(self, bot, update):
        try:
            word = update.message.text.lower()

            entry = self.games.get(update.message.chat_id)

            if entry and word == entry.pokemon.name:
                with self.mutex:
                    del self.games[update.message.chat_id]

                if update.message.chat_id > 0: # user
                    resp = responses.reveal(entry.pokemon)
                else:
                    resp = responses.revealgroup(entry.pokemon, update.message.from_user.first_name)

                with open(entry.pokemon.artwork, 'rb') as photo:
                    bot.sendPhoto(chat_id=update.message.chat_id,
                                  photo=photo,
                                  caption=resp)

        except Exception as e:
            error(bot, update, e)

    def job(self, bot):
        try:
            times_up = []

            with self.mutex:
                for k in self.games.keys():
                    self.games[k].time_left -= 1

                    if self.games[k].time_left == 0:
                        times_up.append((k, self.games[k]))

                for k, _ in times_up:
                    del self.games[k]

            for chat_id, entry in times_up:
                with open(entry.pokemon.artwork, 'rb') as photo:
                    bot.sendPhoto(chat_id=chat_id,
                                  photo=photo,
                                  caption=responses.times_up(entry.pokemon))

        except Exception as e:
            error(bot, None, e)

