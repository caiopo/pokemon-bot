#! /usr/bin/env python3

import logging
import handler
import argparse
import config

from telegram import Updater
from functools import partial

def resolve_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    resolve_args()

    updater = Updater(token=config.BOT_TOKEN)

    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    print(updater.bot.getMe())

    gm = handler.GameManager()

    dispatcher.addTelegramCommandHandler('start', handler.help)
    dispatcher.addTelegramCommandHandler('help', handler.help)

    dispatcher.addTelegramCommandHandler('pokemon', gm.new)
    dispatcher.addTelegramCommandHandler('pokemon1', lambda bot, update: gm.new(bot, update, 1))
    dispatcher.addTelegramCommandHandler('pokemon2', lambda bot, update: gm.new(bot, update, 2))
    dispatcher.addTelegramCommandHandler('pokemon3', lambda bot, update: gm.new(bot, update, 3))
    dispatcher.addTelegramCommandHandler('pokemon4', lambda bot, update: gm.new(bot, update, 4))
    dispatcher.addTelegramCommandHandler('pokemon5', lambda bot, update: gm.new(bot, update, 5))
    dispatcher.addTelegramCommandHandler('pokemon6', lambda bot, update: gm.new(bot, update, 6))

    dispatcher.addTelegramCommandHandler('p', gm.new)
    dispatcher.addTelegramCommandHandler('p1', lambda bot, update: gm.new(bot, update, 1))
    dispatcher.addTelegramCommandHandler('p2', lambda bot, update: gm.new(bot, update, 2))
    dispatcher.addTelegramCommandHandler('p3', lambda bot, update: gm.new(bot, update, 3))
    dispatcher.addTelegramCommandHandler('p4', lambda bot, update: gm.new(bot, update, 4))
    dispatcher.addTelegramCommandHandler('p5', lambda bot, update: gm.new(bot, update, 5))
    dispatcher.addTelegramCommandHandler('p6', lambda bot, update: gm.new(bot, update, 6))

    dispatcher.addTelegramCommandHandler('score', gm.score)
    dispatcher.addTelegramCommandHandler('clear', gm.clear)

    dispatcher.addTelegramMessageHandler(gm.default)

    job_queue.put(gm.job, 3)

    updater.start_polling()

if __name__ == '__main__':
    main()
