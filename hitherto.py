from argparse import ArgumentParser
from configparser import ConfigParser
from contextlib import contextmanager
import discord
import sqlite3


@contextmanager
def get_db():
    connection = sqlite3.connect(args.database)
    cursor = connection.cursor()
    yield cursor
    connection.commit()
    connection.close()


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
        await client.send_message(message.channel, "I'm Here!")


# start client
print('starting client...')
client.run(cfg_parser.get('DISCORD', "TOKEN"))
