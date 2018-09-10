from multiprocessing import Process, SimpleQueue
from time import sleep

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
        elif method == 'hotkey':
            modifier, key = command.arguments
            PrismataController.hotkey(modifier, key)

def check_and_restart_match():
    while True:
        PrismataController.check_and_restart_match()
        sleep(2)

if __name__ == '__main__':
    log.info('=== Starting TwitchPlaysPrismata ===')
    # os.system(config['Files']['prismata_exe_path'])

    # Clear display files
    open(config['Files']['stream_display_usernames'], 'w').close()
    open(config['Files']['stream_display_commands'], 'w').close()

    bot_process = Process(target=start_twitch_bot, args=(command_queue,))
    bot_process.start()

    PrismataController.post_startup()
    PrismataController.vs_computer()
    sleep(1)
    PrismataController.split_unit_tab()

    check_and_restart = Process(target=check_and_restart_match)
    check_and_restart.start()

    process_commands()
