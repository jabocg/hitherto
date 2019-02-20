from argparse import ArgumentParser
from configparser import ConfigParser
from contextlib import contextmanager
import discord
import random
import sqlite3


@contextmanager
def get_db():
    connection = sqlite3.connect(args.database)
    cursor = connection.cursor()
    yield cursor
    connection.commit()
    connection.close()


GREETING_STRINGS = ["Hi!", "Hello!", "Hey!", "Wassup?",
                    "Ayyyy :point_right: :sunglasses: :point_right:"]


# parse arguments and config
arg_parser = ArgumentParser(description='Start the discord bot')
arg_parser.add_argument('-i', '--identity-file', help='identity file',
                        default='id.cfg')
arg_parser.add_argument('-d', '--database', help='database file',
                        default='hitherto.db')
args = arg_parser.parse_args()
cfg_parser = ConfigParser()
cfg_parser.read(args.identity_file)

# create client
client = discord.Client()


# client shenanigans
@client.event
async def on_member_ban(member):
    """Reset the "days since ban" value for the server."""


@client.event
async def on_message(message):
    """Either check for kick or respond to a ping."""
    if client.user.mentioned_in(message):
        if 'status' in message.content:
            await client.send_message(message.channel, "I'm Here!")
        elif 'hello' in message.content:
            await client.send_message(message.channel,
                                      random.choice(GREETING_STRINGS))
        elif 'kick' in message.content:
            await report_days(message, category='kick')
        elif 'ban' in message.content:
            await report_days(message, category='ban')
        else:
            await report_days(message.server.id)


async def report_days(message, category=None):
    server_id = message.server.id
    channel = message.channel
    if category == 'kick':
        days = 0
    elif category == 'ban':
        days = 1
    else:
        category = 'kick/ban'
        days = 2

    msg = ('It has been {days} since the last {category}'
           .format(days=days, category=category))
    await client.send_message(channel, msg)


@client.event
async def on_ready():
    pass


# start client
print('starting client...')
client.run(cfg_parser.get('DISCORD', "TOKEN"))
