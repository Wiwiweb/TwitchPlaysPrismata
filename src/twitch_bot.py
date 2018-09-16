from collections import namedtuple
import re

import irc.bot

from globals import config, log, chat_log

Command = namedtuple('Command', ['method', 'arguments'])

DISPLAY_USERNAME_MAX_LENGTH = int(config['Stream']['display_username_max_length'])
DISPLAY_COMMAND_MAX_LENGTH = int(config['Stream']['display_command_max_length'])

VALID_REPEATABLE_KEYS = 'e|d|c|b|a|f|g|s|w|t|r|1|2|3|4|5|6|7|8|9|10|11'
VALID_NON_REPEATABLE_KEYS = 'q|backspace|space|escape'
VALID_CTRL_KEYS = 'x|z'

VALID_NON_REPEATABLE_COMMAND = '({})'.format(VALID_NON_REPEATABLE_KEYS)
VALID_COMMAND_REGEX = '({})+'.format(VALID_REPEATABLE_KEYS)
VALID_COMMAND_INDIVIDUAL_REGEX = '({})'.format(VALID_REPEATABLE_KEYS)
VALID_HOTKEY_COMMAND_REGEX = '(?:shift[+-](?:{})|ctrl[+-](?:{}))'.format(VALID_REPEATABLE_KEYS, VALID_CTRL_KEYS)

class TwitchBot(irc.bot.SingleServerIRCBot):

    def __init__(self, queue):
        nickname = config['Twitch']['nickname']
        server = config['Twitch']['server']
        port = int(config['Twitch']['port'])
        password = config['Secrets']['IRC_password']
        channel = '#' + config['Twitch']['channel']
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, password)], nickname, nickname)
        self.channel = channel
        self.command_queue = queue

    def on_welcome(self, connection, event):
        log.debug('Connected (channel {})'.format(self.channel))
        connection.cap('REQ', ':twitch.tv/tags')  # Request display-names in messages
        connection.cap('REQ', ':twitch.tv/commands')  # Request ROOMSTATE and CLEARCHAT updates
        connection.join(self.channel)

    def on_join(self, connection, event):
        log.debug('Joined channel ' + event.target)

    def on_pubmsg(self, connection, event):
        text = event.arguments[0].lower()
        username = ''
        for tag in event.tags:  # Iterating through to find the key because this gives us a list instead of a dict...
            if tag['key'] == 'display-name':
                username = tag['value']
        chat_log.debug('{}: {}'.format(username, text))

        valid_command = False
        if text.startswith('click'):
            valid_command = self.command_click(text)
        if text.startswith('emote'):
            valid_command = self.command_emote(text)
        else:
            command_non_repeatable_match = re.fullmatch(VALID_NON_REPEATABLE_COMMAND, text)
            if command_non_repeatable_match is not None:
                command_text = command_non_repeatable_match.group(0)
                self.queue_command('press', command_text)
                valid_command = True
            else:
                command_repeatable_match = re.fullmatch(VALID_COMMAND_REGEX, text)
                if command_repeatable_match is not None:
                    commands_text = command_repeatable_match.group(0)
                    commands_text = re.findall(VALID_COMMAND_INDIVIDUAL_REGEX, commands_text)
                    log.info("New combo command: {}".format(text))
                    for command_text in commands_text:
                        self.queue_command('press', command_text)
                    valid_command = True
                else:
                    command_hotkey_match = re.fullmatch(VALID_HOTKEY_COMMAND_REGEX, text)
                    if command_hotkey_match is not None:
                        command_text = command_hotkey_match.group(0)
                        command_text = command_text.replace('+', '-')
                        hotkey, key = command_text.split('-')
                        self.queue_command('hotkey', [hotkey, key])

        if valid_command:  # Add command to the stream screen
            with open(config['Files']['stream_display_usernames'], 'a') as file:
                truncated_username = username[0:DISPLAY_USERNAME_MAX_LENGTH]
                file.write(truncated_username + '\n')
            with open(config['Files']['stream_display_commands'], 'a') as file:
                truncated_command = text[0:DISPLAY_COMMAND_MAX_LENGTH]
                file.write(truncated_command + '\n')

    def command_click(self, text):
        split = text.split()
        if len(split) != 3:
            return False
        _, column, horizontal = text.split()
        try:
            column = int(column)
            horizontal = int(horizontal)
        except ValueError:
            return False
        if 1 <= column <= 6 and 0 <= horizontal <= 1000:
            self.queue_command('click', [column, horizontal])
            return True
        else:
            return False

    def command_emote(self, text):
        split = text.split(' ', 1)
        if len(split) != 2:
            return False
        _, emote_text = split
        self.queue_command('emote', emote_text)
        return True

    def queue_command(self, command_method, args):
        command = Command(command_method, args)
        log.info("New command: {} {}".format(command_method, args))
        self.command_queue.put(command)

    def on_disconnect(self, connection, event):
        log.info('Disconnected (channel {})'.format(self.channel))
        log.debug(event)

    def chat(self, message):
        self.connection.privmsg(self.channel, message)
