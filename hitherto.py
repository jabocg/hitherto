from argparse import ArgumentParser
from configparser import ConfigParser
from contestlib import contextmanager
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
cfg_parser = ConfigParser()
cfg_parser.read(arg_parser.identity_file)

args = arg_parser.parse_args()

# create client
client = discord.Discord()

# client shenanigans

# start client
client.start(cfg_parser.get('DISCORD', "TOKEN"))
