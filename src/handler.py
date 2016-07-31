import config
import responses
import logging
import operator

from collections import namedtuple
from threading import Lock
from pokemon import Pokemon

# Botfather /setcommands
# pokemon - inicia uma rodada de "Quem é esse Pokémon"
# pokemon1 - inicia uma rodada de "Quem é esse Pokémon" (geração 1)
# pokemon2 - inicia uma rodada de "Quem é esse Pokémon" (geração 2)
# pokemon3 - inicia uma rodada de "Quem é esse Pokémon" (geração 3)
# pokemon4 - inicia uma rodada de "Quem é esse Pokémon" (geração 4)
# pokemon5 - inicia uma rodada de "Quem é esse Pokémon" (geração 5)
# pokemon6 - inicia uma rodada de "Quem é esse Pokémon" (geração 6)
# p - inicia uma rodada de "Quem é esse Pokémon"
# p1 - inicia uma rodada de "Quem é esse Pokémon" (geração 1)
# p2 - inicia uma rodada de "Quem é esse Pokémon" (geração 2)
# p3 - inicia uma rodada de "Quem é esse Pokémon" (geração 3)
# p4 - inicia uma rodada de "Quem é esse Pokémon" (geração 4)
# p5 - inicia uma rodada de "Quem é esse Pokémon" (geração 5)
# p6 - inicia uma rodada de "Quem é esse Pokémon" (geração 6)
# score - mostra a pontuação
# clear - limpa a pontuação
# help - informações sobre o bot

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

    if isinstance(e, OSError):
        text += '\nErrno: {}\nStrerror: {}'.format(e.errno, e.strerror)

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

TIME_TO_SOLVE = 5 # times 3 == 15 seconds

class PokemonEntry:
    def __init__(self, pokemon, time_left=TIME_TO_SOLVE):
        self.pokemon = pokemon
        self.time_left = time_left

    def __repr__(self):
        return '<PokemonEntry (pokemon={}, time_left={}) at {}>'.format(
                    self.pokemon, self.time_left, id(self))

class ScoreEntry:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __repr__(self):
        return '<ScoreEntry (name={}, score={}) at {}>'.format(
                    self.name, self.score, id(self))

class GameManager:
    def __init__(self):
        self.games = {}
        self.mutex = Lock()

        self.score_dict = {}
        self.mutex_score = Lock()

    def new(self, bot, update, gen=6):
        try:
            if update.message.chat_id in self.games:
                bot.sendMessage(chat_id=update.message.chat_id,
                                text=responses.already_active)
                return

            p = Pokemon.random(gen)

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

                with self.mutex_score:
                    group_dict = self.score_dict.get(update.message.chat_id, {})

                    score_entry = group_dict.get(update.message.from_user.id,
                                                 ScoreEntry(update.message.from_user.first_name, 0))

                    score_entry.score += 1

                    group_dict[update.message.from_user.id] = score_entry

                    self.score_dict[update.message.chat_id] = group_dict

        except Exception as e:
            error(bot, update, e)

    def score(self, bot, update):
        try:
            text = responses.score

            with self.mutex_score:
                if update.message.chat_id not in self.score_dict:
                    bot.sendMessage(chat_id=update.message.chat_id,
                                    text=responses.score_not_found)
                    return

                for p in sorted(self.score_dict[update.message.chat_id].items(),
                                key=lambda x: x[1].score,
                                reverse=True):

                    text += '\n{}: {}'.format(p[1].name, p[1].score)

                bot.sendMessage(chat_id=update.message.chat_id,
                                text=text)
        except Exception as e:
            error(bot, update, e)

    def clear(self, bot, update):
        try:
            with self.mutex_score:
                if update.message.chat_id in self.score_dict:
                    del self.score_dict[update.message.chat_id]
                    bot.sendMessage(chat_id=update.message.chat_id,
                                    text=responses.clear)
                else:
                    bot.sendMessage(chat_id=update.message.chat_id,
                                    text=responses.score_not_found)
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

