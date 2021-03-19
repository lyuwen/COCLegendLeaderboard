import os
import math
import random
import logging
import textwrap

import discord
from discord.ext import commands
from dotenv import load_dotenv

from legends_leaderboard import (
    LegendsLeagueLeaderboard,
    format_leaderboard,
    format_leaderboard_title,
    load_leaderboard,
    save_leaderboard,
    )

PATH = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO)

# Load tokens
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
COC_API_TOKEN = os.getenv("COC_TOLEN")


# bot command prefix
bot = commands.Bot(command_prefix='!')


# Load up legend leaderboard
lll = LegendsLeagueLeaderboard(
    filename=os.path.join(PATH, 'list_of_tags.txt'),
    api_token=COC_API_TOKEN,
)

max_lines = 10
global page_no
page_no = 0
lll.load_player_tags()

global current_leaderboard
global season
current_leaderboard, season = load_leaderboard(lll.dbname)
#  current_leaderboard = lll.get_current_season_trophies()


def check_adimin_perm(ctx):
    channel = ctx.message.channel
    user = ctx.author
    perm = channel.permissions_for(user)
    return perm.administrator


@bot.event
async def on_ready():
    ''' When the bot is loaded and ready.
    '''
    for guild in bot.guilds:
        if guild.id == GUILD:
            break

    logging.info(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


# test command
@bot.command(name='test')
async def test_command(ctx):
    ''' A test command.
    '''
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)


# show the ranking board
@bot.command(name='rankings')
async def rankings(ctx, *args):
    ''' Show leaderboard.
    '''
    if ('-h' in args) or ('--help' in args):
        await ctx.send(textwrap.dedent('''\
            ```
            Usage !rankings [-h|--help] [-r|--refresh] [-l|--last-season]

              -h, --help          show this help message.
              -r, --refresh       refresh the leaderboard before show ranking.
              -l, --last-season   load last season's end-of-season leaderboard.
            ```
        '''))
        return
    elif ('-r' in args) or ('--refresh' in args):
        logging.info('Refreshing leaderboard.')
        current_leaderboard = await lll.get_current_season_trophies()
        season = lll.current_season
        save_leaderboard(lll.dbname, current_leaderboard, season)
    elif ('-l' in args) or ('--last-season' in args):
        logging.info('Refreshing leaderboard.')
        current_leaderboard = await lll.get_last_season_trophies()
        season = lll.last_season
        save_leaderboard(lll.dbname, current_leaderboard, season)
    page_no = 0
    current_leaderboard, season = load_leaderboard(lll.dbname)
    content = format_leaderboard(
        data=current_leaderboard,
        title=format_leaderboard_title(season=season),
        page_no=page_no,
        max_lines=max_lines,
        center=1,
        season_countdown=lll.get_countdown_current_season() if season == lll.current_season else None,
    )
    message_sent = await ctx.send(content)
    for emoji in '⏮ ⏪ ⏩ ⏭ 🔄'.split():
      logging.info('react with {}'.format(emoji))
      await message_sent.add_reaction(emoji)


# turning pages
@bot.event
async def on_reaction_add(reaction, user):
    ''' Flip pages in the leaderboard.
    '''
    emoji = reaction.emoji
    message = reaction.message

    if user.bot:
        return

    logging.info('received reaction from {} with {}'.format(user.name, emoji))
    logging.info('message id: {}'.format(message.id))

    global page_no
    global current_leaderboard
    global season

    current_leaderboard, season = load_leaderboard(lll.dbname)

    page_max = math.ceil(len(current_leaderboard) / max_lines)

    if emoji == '⏮':
      page_no = 0
    elif emoji == '⏪':
      page_no -= 1
      if page_no < 0:
        page_no = 0
    elif emoji == '⏩':
      page_no += 1
      if page_no >= page_max:
        page_no = page_max - 1
    elif emoji == '⏭':
        page_no = page_max - 1
    elif emoji == '🔄':
      page_no = 0
      current_leaderboard = await lll.get_current_season_trophies()
      season = lll.current_season
      save_leaderboard(lll.dbname, current_leaderboard, season)
    else:
      return
    content = format_leaderboard(
        data=current_leaderboard,
        title=format_leaderboard_title(season=season),
        page_no=page_no,
        max_lines=max_lines,
        center=1,
        season_countdown=lll.get_countdown_current_season() if season == lll.current_season else None,
    )
    await message.edit(content=content)
    await reaction.remove(user)


# register a player
@bot.command(name='register')
async def register(ctx, *args):
    ''' Added player(s) to the leaderboard.
    '''
    logging.info("registering following players: {}".format(", ".join(args)))
    successful_players, unqualified_players, failed_tags = await lll.register_players(player_tags=args)
    content = []
    if successful_players:
      msg1 = '\n'.join(['{} ({})'.format(name, tag) for tag, name in successful_players.items()])
      content.append(textwrap.dedent('''\
          Successfully register players:
            ```
            {}
            ```
      ''').format(msg1))
    if unqualified_players:
      msg1 = '\n'.join(['{} ({})'.format(name, tag) for tag, name in unqualified_players.items()])
      content.append(textwrap.dedent('''\
          Unqualified players due to not in qualified clans:
            ```
            {}
            ```
      ''').format(msg1))
    if failed_tags:
      msg2 = ', '.join(failed_tags)
      content.append(textwrap.dedent('''\
          Failed to register players:
            ```
            {}
            ```
      '''.format(msg2)))
    await ctx.send("\n".join(content))


# remove a player
@bot.command(name='remove')
async def remove(ctx, *args):
    ''' Remove player(s) from the leaderboard.
    '''
    logging.info("removing following players: {}".format(", ".join(args)))
    removed_players = lll.remove_players(args)
    content = 'No player tag was removed.'
    if removed_players:
      msg = ', '.join(removed_players)
      content = textwrap.dedent('''\
          Removed players:
            ```
            {}
            ```
      '''.format(msg))
    await ctx.send(content)


# register a clan
@bot.command(name='register_clan')
async def register_clan(ctx, arg):
    ''' Added a clan into database.

    If not empty, players who are in the registered
    clans can register for the leaderboard.
    '''
    if not check_adimin_perm(ctx):
        ctx.send("User does not have sufficient permission to register a clan.")
    if await lll.register_clan(arg):
        await ctx.send("CLan {} added.".format(arg))
    else:
        await ctx.send("Failed to add cLan {}.".format(arg))


# remove a clan
@bot.command(name='remove_clan')
async def remove_clan(ctx, arg):
    ''' Remove a clan from database.
    '''
    if not check_adimin_perm(ctx):
        ctx.send("User does not have sufficient permission to remove a clan.")
    if lll.remove_clan(arg):
        await ctx.send("CLan {} added.".format(arg))
    else:
        await ctx.send("Failed to add cLan {}.".format(arg))


# refresh leaderboard
@bot.command(name='refresh')
async def refresh(ctx):
    ''' Refresh the leaderboard.
    '''
    logging.info("Refreshing leaderboard")
    current_leaderboard = await lll.get_current_season_trophies()
    save_leaderboard(lll.dbname, current_leaderboard, lll.current_season)
    await ctx.send("Leaderboard has been refreshed.")


# list player tags
@bot.command(name='players')
async def players(ctx):
    ''' Show the list of all players.
    '''
    lll.load_player_tags()
    players = []
    for player_tag in lll.player_tags:
        try:
            player_info = lll.coc.get_player_info(player_tag)
            players.append("{} ({})".format(player_info['name'], player_info['tag']))
        except RuntimeError:
            logging.warning("Failed to find player info for tag: {}".format(player_tag))
    content = textwrap.dedent("""\
        Players registered:
        ```
        {}
        ```
    """).format("\n".join(players))
    await ctx.send(content)


# list clan tags
@bot.command(name='clans')
async def clans(ctx):
    ''' Show the list of all clans.
    '''
    lll.load_qualified_clans()
    clans = []
    for clan_tag in lll.qualified_clans:
        try:
            clan_info = lll.coc.get_clan_info(clan_tag)
            clans.append("{} ({})".format(clan_info['name'], clan_info['tag']))
        except RuntimeError:
            logging.warning("Failed to find clan info for tag: {}".format(clan_tag))
    content = textwrap.dedent("""\
        Clan registered:
        ```
        {}
        ```
    """).format("\n".join(clans))
    await ctx.send(content)


# list player tags
@bot.command(name='credit')
async def credit(ctx):
    ''' Credit the author.
    '''
    content = textwrap.dedent('''\
        ```
        This package includes a discord bot, a python interface to Clash of Clans API,
        and a set of algorithms that make the legend league leaderboard.
        -
        Created by MrFu
        ```
    ''')
    await ctx.send(content)


if __name__ == '__main__':
  bot.run(TOKEN)
