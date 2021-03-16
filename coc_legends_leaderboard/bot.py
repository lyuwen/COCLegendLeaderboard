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
current_leaderboard = load_leaderboard(lll.dbname)
#  current_leaderboard = lll.get_current_season_trophies()


@bot.event
async def on_ready():
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
async def rankings(ctx):
    page_no = 0
    current_leaderboard = load_leaderboard(lll.dbname)
    content = format_leaderboard(
        data=current_leaderboard,
        title=format_leaderboard_title(season=lll.current_season),
        page_no=page_no,
        max_lines=max_lines,
        center=1,
        season_countdown=lll.get_countdown_current_season()
    )
    message_sent = await ctx.send(content)
    for emoji in '⏮ ⏪ ⏩ ⏭ 🔄'.split():
      logging.info('react with {}'.format(emoji))
      await message_sent.add_reaction(emoji)


# turning pages
@bot.event
async def on_reaction_add(reaction, user):
    emoji = reaction.emoji
    message = reaction.message

    if user.bot:
        return

    logging.info('received reaction from {} with {}'.format(user.name, emoji))
    logging.info('message id: {}'.format(message.id))

    global page_no
    global current_leaderboard

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
      current_leaderboard = lll.get_current_season_trophies()
      save_leaderboard(lll.dbname, current_leaderboard)
    else:
      return
    content = format_leaderboard(
        data=current_leaderboard,
        title=format_leaderboard_title(season=lll.current_season),
        page_no=page_no,
        max_lines=max_lines,
        center=1,
        season_countdown=lll.get_countdown_current_season()
    )
    await message.edit(content=content)
    await reaction.remove(user)


# register a player
@bot.command(name='register')
async def register(ctx, *args):
    logging.info("registering following players: {}".format(", ".join(args)))
    successful_players, failed_tags = lll.register_players(player_tags=args)
    content = []
    if successful_players:
      msg1 = '\n'.join(['{} ({})'.format(name, tag) for tag, name in successful_players.items()])
      content.append(textwrap.dedent('''\
          Successfully remove players:
            ```
            {}
            ```
      '''.format(msg1)))
    if failed_tags:
      msg2 = ', '.join(failed_tags)
      content.append(textwrap.dedent('''\
          Failed to remove players:
            ```
            {}
            ```
      '''.format(msg2)))
    await ctx.send("\n".join(content))



# remove a player
@bot.command(name='remove')
async def remove(ctx, *args):
    logging.info("removing following players: {}".format(", ".join(args)))
    removed_players = lll.remove_players(args)
    content = 'No player tag was removed.'
    if removed_players:
      msg = ', '.join(removed_players)
      content = textwrap.dedent('''\
          Failed to remove players:
            ```
            {}
            ```
      '''.format(msg1))
    await ctx.send(content)


# refresh leaderboard
@bot.command(name='refresh')
async def remove(ctx):
    logging.info("Refreshing leaderboard")
    current_leaderboard = lll.get_current_season_trophies()
    save_leaderboard(lll.dbname, current_leaderboard)
    await ctx.send("Leaderboard has been refreshed.")


if __name__ == '__main__':
  bot.run(TOKEN)
