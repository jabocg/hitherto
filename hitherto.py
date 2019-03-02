from argparse import ArgumentParser
from configparser import ConfigParser
from contextlib import contextmanager
import datetime
import discord
import random
import sqlite3
import threading
import time


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
GET_DAYS = ("SELECT `days` "
            "FROM `days_since` "
            "WHERE `server_id` = ? "
            "AND `category` = ?")
SET_DAYS = ("UPDATE `days_since` "
            "SET `days` = ? "
            "WHERE `server_id` = ? "
            "AND `category` = ?")


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
    channel = message.channel
    server = channel.server
    if client.user.mentioned_in(message):
        if 'status' in message.content:
            await client.send_message(channel, "I'm Here!")
        elif 'hi' in message.content or 'hello' in message.content:
            await client.send_message(channel, random.choice(GREETING_STRINGS))
        elif 'kick' in message.content:
            await report_days(server, channel, category='kick')
        elif 'ban' in message.content:
            await report_days(server, channel, category='ban')
        else:
            await report_days(server, channel)
    elif (message.content.startswith('+k')
          and message.author.permissions_in(channel).kick_members):
        # we just kicked someone, reset value
        await reset_days(message.server, category='kick')
        await report_days(server, channel, category='kick')


async def reset_days(server, category='kick'):
    """Reset the days since kick/ban."""
    with get_db() as db:
        db.execute(SET_DAYS, (0, server.id, 0 if category == 'kick' else 1,))


async def report_days(server, channel, category='all'):
    if category == 'kick':
        with get_db() as db:
            days = db.execute(GET_DAYS, (server.id, 0)).fetchone()[0]
    elif category == 'ban':
        with get_db() as db:
            days = db.execute(GET_DAYS, (server.id, 1)).fetchone()[0]
    elif category == 'all':
        category = 'kick/ban'
        with get_db() as db:
            kick_days = db.execute(GET_DAYS, (server.id, 0)).fetchone()[0]
            ban_days = db.execute(GET_DAYS, (server.id, 1)).fetchone()[0]
        days = min(kick_days, ban_days)

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


def increment_days():
    while True:
        now = datetime.datetime.utcnow()
        if now.hour == 0:
            with get_db() as db:
                for s in client.servers:
                    kick_days = db.execute(GET_DAYS, (s.id, 0,)).fetchone()[0]
                    ban_days = db.execute(GET_DAYS, (s.id, 1,)).fetchone()[0]
                    db.execute(SET_DAYS, (kick_days + 1, s.id, 0,))
                    db.execute(SET_DAYS, (ban_days + 1, s.id, 1,))
        time.sleep(3600)


@client.event
async def on_ready():
    init_db()
    for s in client.servers:
        if not in_db(s):
            add_to_db(s)
    print('ready')

# start day incrementor
t = threading.Thread(target=increment_days, daemon=True)
t.start()

# start client
print('starting client...')
while True:
    try:
        client.run(cfg_parser.get('DISCORD', "TOKEN"))
    except ConnectionResetError:
        pass
