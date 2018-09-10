from collections import namedtuple

import irc.bot

from globals import config, log, chat_log

Command = namedtuple('Command', ['method', 'arguments'])

DISPLAY_USERNAME_MAX_LENGTH = int(config['Stream']['display_username_max_length'])
DISPLAY_COMMAND_MAX_LENGTH = int(config['Stream']['display_command_max_length'])

class TwitchBot(irc.bot.SingleServerIRCBot):

    valid_keys = {'q', 'space', 'backspace', 'escape',
                  'e', 'd', 'c', 'b', 'a', 'f', 'g', 's', 'w', 't' , 'r',
                  '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'}

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
        chat_log.info('{}: {}'.format(username, text))

        if text in TwitchBot.valid_keys:
            command_method = 'press'
            command = Command(command_method, text)
            self.command_queue.put(command)
            log.info("New command: {} {}".format(command_method, text))
            with open(config['Files']['stream_display_usernames'], 'a') as file:
                truncated_username = username[0:DISPLAY_USERNAME_MAX_LENGTH]
                file.write(truncated_username + '\n')
            with open(config['Files']['stream_display_commands'], 'a') as file:
                truncated_command = text[0:DISPLAY_COMMAND_MAX_LENGTH]
                file.write(truncated_command + '\n')

    def on_disconnect(self, connection, event):
        log.info('Disconnected (channel {})'.format(self.channel))
        log.debug(event)

    def chat(self, message):
        self.connection.privmsg(self.channel, message)
