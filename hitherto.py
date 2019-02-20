from argparse import ArgumentParser
from configparser import ConfigParser
from contextlib import contextmanager
import discord
import random
import sqlite3


GREETING_STRINGS = ["Hi!", "Hello!", "Hey!", "Wassup?",
                    "Ayyyy :point_right: :sunglasses: :point_right:"]
COUNT_Q = ("SELECT COUNT(*) "
           "FROM `servers` "
           "WHERE `id` = :server_id")
CREATE_SERVERS = ("CREATE TABLE IF NOT EXISTS `servers` "
                  "(`id` INTEGER, `name` TEXT, `prefix` TEXT, "
                  "  `channel_id` INTEGER)")
CREATE_DAYS = ("CREATE TABLE IF NOT EXISTS `days_since` "
               "(`server_id` INTEGER, `category` INTEGER, `days` INTEGER)")
ADD_SERVER = ("INSERT INTO `servers` "
              "(`id`, `name`, `prefix`, `channel_id`)"
              "VALUES (?, ?, '+', 0)")
ADD_DAYS = ("INSERT INTO `days_since` "
            "(`server_id`, `category`, `days`) "
            "VALUES (?, ?, 0)")


# parse arguments and config
arg_parser = ArgumentParser(description='Start the discord bot')
arg_parser.add_argument('-i', '--identity-file', help='identity file',
                        default='id.cfg')
arg_parser.add_argument('-d', '--database', help='database file',
                        default='hitherto.db')
args = arg_parser.parse_args()
cfg_parser = ConfigParser()
cfg_parser.read(args.identity_file)


@contextmanager
def get_db():
    # TODO: maybe refactor to use cache
    connection = sqlite3.connect(args.database)
    cursor = connection.cursor()
    yield cursor
    connection.commit()
    connection.close()


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
            await report_days(message)


async def reset_days(server, ban=False):
    """Reset the days since kick/ban."""
    if ban:
        pass
    else:
        pass


async def report_days(server, channel, category=None):
    if category == 'kick':
        days = 0
    elif category == 'ban':
        days = 1
    else:
        category = 'kick/ban'
        days = 2

    msg = ('It has been {days} day(s) since the last {category}.'
           .format(days=days, category=category))
    await client.send_message(channel, msg)


def init_db():
    with get_db() as db:
        db.execute(CREATE_SERVERS)
        db.execute(CREATE_DAYS)


def in_db(server):
    with get_db() as db:
        server_count = db.execute(COUNT_Q, (server.id,)).fetchone()[0]
    return server_count > 0


def add_to_db(server):
    with get_db() as db:
        db.execute(ADD_SERVER, (server.id, server.name,))
        db.executemany(ADD_DAYS, ((server.id, 0,), (server.id, 1,),))


@client.event
async def on_ready():
    init_db()
    for s in client.servers:
        if not in_db(s):
            add_to_db(s)
    print('ready')

# start client
print('starting client...')
client.run(cfg_parser.get('DISCORD', "TOKEN"))
