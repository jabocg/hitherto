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
client = discord.Discord()

# client shenanigans

# start client
print('starting client...')
client.start(cfg_parser.get('DISCORD', "TOKEN"))
