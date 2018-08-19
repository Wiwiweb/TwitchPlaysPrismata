from multiprocessing import Process, SimpleQueue
import os

from globals import config, log, test_mode
from twitch_bot import TwitchBot
from prismata_controller import PrismataController

command_queue = SimpleQueue()

def start_twitch_bot(queue):
    bot = TwitchBot(queue)
    bot.start()

def process_commands():
    while True:
        command = command_queue.get()
        log.debug("Processing command: {} {}".format(command.method, command.arguments))
        method = command.method
        if method == 'press':
            PrismataController.press(command.arguments)


if __name__ == '__main__':
    log.info('=== Starting TwitchPlaysPrismata ===')
    # os.system(config['Files']['prismata_exe_path'])

    bot_process = Process(target=start_twitch_bot, args=(command_queue,))
    bot_process.start()

    process_commands()
