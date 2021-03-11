import os
import math
import logging
import calendar
import datetime
import pandas as pd

from coc import ClashOfClans


logging.basicConfig(level=logging.INFO)
PATH = os.path.dirname(os.path.abspath(__file__))


def get_last_monday_of_month(year, month):
  '''
  Find the last Monday of the month of the year.

  Parameters
  ----------
  year  : int
      Year.
  month : int
      Month.

  Returns
  -------
  retval : datetime.datetime
      The datetime.datetime object of the last Monday of the month.
  '''
  calendar_month = calendar.monthcalendar(year, month)
  mondays = [week[0] for week in calendar_month if week[0]>0]
  return datetime.datetime(year, month, mondays[-1])


def get_last_month(year, month):
  ''' Find last month.

  Parameters
  ----------
  year  : int
      Year.
  month : int
      Month.

  Returns
  -------
  year  : int
      Year of last month.
  month : int
      Month of last month.
  '''
  first_day_this_month = datetime.datetime(year, month, 1)
  last_day_last_month = first_day_this_month - datetime.timedelta(days=1)
  return last_day_last_month.year, last_day_last_month.month


def get_next_month(year, month):
  ''' Find next month.

  Parameters
  ----------
  year  : int
      Year.
  month : int
      Month.

  Returns
  -------
  year  : int
      Year of next month.
  month : int
      Month of next month.
  '''
  return calendar.nextmonth(year=year, month=month)


class LegendsLeagueLeaderboard:
  '''
  Make a Legends League leaderboard

  Parameters
  ----------
  filename : the file to 
  '''


  def __init__(self, filename, api_token):
    self.filename = filename
    self.coc = ClashOfClans(api_token=api_token)
    self.player_tags = []


  def load_player_tags(self):
    ''' Load player tags into a txt file.
    '''
    with open(self.filename, 'r') as f:
      self.player_tags = f.read().strip().split()


  def save_player_tags(self):
    ''' Save player tags into a txt file.
    '''
    with open(self.filename, 'w') as f:
      f.write('\n'.join(self.player_tags))


  def _get_legends_day_cutoff(self, year, month):
    last_monday_this_month = get_last_monday_of_month(year, month)

    legends_cutoff = datetime.datetime(last_monday_this_month.year, last_monday_this_month.month, last_monday_this_month.day, 5)
    return legends_cutoff


  def _get_current_season(self, date=datetime.datetime.utcnow()):
    legends_cutoff = self._get_legends_day_cutoff(year=date.year, month=date.month)

    if date < legends_cutoff:
      return (date.year, date.month)
    else:
      next_month_year, next_month_month = get_next_month(date.year, date.month)
      return (next_month_year, next_month_month)


  def get_countdown_current_season(self, date=datetime.datetime.utcnow()):
    month, year = self._get_current_season(date=date)
    legends_cutoff = self._get_legends_day_cutoff(month, year)
    timedelta = legends_cutoff - date
    days = timedelta.days
    hours = getattr(timedelta, 'hours', timedelta.seconds // 3600)
    return (days, hours)


  @property
  def current_season(self):
    year, month = self._get_current_season()
    return '{year:04}-{month:02}'.format(year=year, month=month)


  @property
  def last_season(self):
    year, month = self._get_current_season()
    last_month_year, last_month_month = get_last_month(year, month)
    return '{year:04}-{month:02}'.format(year=last_month_year, month=last_month_month)


  def _get_last_season_trophies(self):
    last_season = self.last_season

    legend_player_trophies = []
    legend_player_names = []
    legend_player_tags = []

    legend_id = 29000022

    logging.info('Last season is: {}'.format(last_season))

    for player_tag in self.player_tags:
      player_info = self.coc.get_player_info(player_tag)
      if ('legendStatistics' not in player_info) \
          or ('previousSeason' not in player_info['legendStatistics']) \
          or (player_info['legendStatistics']['previousSeason']['id'] != last_season):
        # player is not in legend league
        logging.warning('Player {player_tag} not in Legend League last season, skip.'.format(player_tag=player_tag))
      else:
        # player is in legend league
        legend_player_trophies.append(player_info['legendStatistics']['previousSeason']['trophies'])
        legend_player_names.append(player_info['name'])
        legend_player_tags.append(player_info['tag'])
    return legend_player_tags, legend_player_names, legend_player_trophies


  def get_last_season_trophies(self):
    '''
    Get last season legend leaderboard.

    This is the accurate statitic to show end of season legend league trophy count.

    Returns
    -------
    dataframe  :  pandas.DataFrame
        A Pandas DataFrame of the last season leaderboard, sorted.
    '''
    legend_player_tags, legend_player_names, legend_player_trophies = self._get_last_season_trophies()
    dataframe = pd.DataFrame({
      'player_tag': legend_player_tags,
      'name': legend_player_names,
      'trophies': legend_player_trophies,
      'timestamp' : datetime.datetime.utcnow(),
      })
    return dataframe.sort_values(by='trophies', ascending=False).reset_index(drop=True)


  def _get_current_season_trophies(self):
    legend_player_trophies = []
    legend_player_names = []
    legend_player_tags = []

    legend_id = 29000022

    for player_tag in self.player_tags:
      player_info = self.coc.get_player_info(player_tag)
      if not player_info.get('league', {}).get('id', 0) == legend_id:
        # player is not in legend league
        logging.warning('Player {player_tag} not in Legend League, skip.'.format(player_tag=player_tag))
      else:
        # player is in legend league
        legend_player_trophies.append(player_info['trophies'])
        legend_player_names.append(player_info['name'])
        legend_player_tags.append(player_info['tag'])
    return legend_player_tags, legend_player_names, legend_player_trophies


  def get_current_season_trophies(self):
    '''
    Get current season legend leaderboard.

    Returns
    -------
    dataframe  :  pandas.DataFrame
        A Pandas DataFrame of the current season leaderboard, sorted.
    '''
    legend_player_tags, legend_player_names, legend_player_trophies = self._get_current_season_trophies()
    dataframe = pd.DataFrame({
      'player_tag': legend_player_tags,
      'name': legend_player_names,
      'trophies': legend_player_trophies,
      'timestamp' : datetime.datetime.utcnow(),
      })
    return dataframe.sort_values(by='trophies', ascending=False).reset_index(drop=True)


def format_timedelta(timedelta, seconds=True, hms=True):
  hours, remainder = divmod(timedelta.seconds, 3600)
  minutes, seconds = divmod(remainder, 60)
  if seconds:
    if hms:
      return '{:02}h {:02}m {:02}s'.format(int(hours), int(minutes), int(seconds))
    else:
      return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
  else:
    if hms:
      return '{:02}h {:02}m'.format(int(hours), int(minutes), int(seconds))
    else:
      return '{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


def format_leaderboard_title(season):
  return 'Legend League Leaderboard for {season} Season'.format(season=season)


def format_leaderboard(
    data,
    title,
    page_no=0,
    max_lines=None,
    name_pading=20,
    season_countdown=None,
    seperator='-',
    center=False,
    ):
  nlines = len(data)
  line_format = '{{rank:>{index_pad}}}. {{name:{name_pad}}} {gap} 🏆 {{trophies:>4}}'.format(
      index_pad=len(str(nlines)),
      name_pad=name_pading,
      gap='\t',
      #  gap=' ' * 11,
      )
  if max_lines is None:
    max_lines = nlines
  linewidth = len(str(nlines)) + name_pading + 6 + 4
  if center:
    linewidth = max(linewidth, len(title))
  content = [
      title.center(linewidth) if center else title,
      seperator * linewidth,
      ]
  for index, line in data.iloc[page_no * max_lines: (page_no + 1) * max_lines].T.items():
    rank = index + 1 # start rank with 1
    line_content = line_format.format(
      rank=rank,
      name=line['name'],
      trophies=line['trophies'],
      )
    #  if center:
    #    line_content = line_content.center(linewidth)
    content.append(line_content)
  content.append(seperator * linewidth)
  if max_lines < nlines:
    content.append('Page {page_no}/{total_pages}'.format(
      page_no=page_no + 1, # start from 1
      total_pages=math.ceil(nlines / max_lines),
      ))
  content.append('Last refreshed: {} ago.'.format(format_timedelta(datetime.datetime.utcnow() - data.iloc[0]['timestamp'])))
  if season_countdown is not None:
    content.append('Current season ends in {days} days {hours} hours.'.format(days=season_countdown[0], hours=season_countdown[1]))
  return '```\n{}\n```'.format('\n'.join(content))


if __name__ == '__main__':
  api_token_file = 'apitoken.in'
  with open(os.path.join(PATH, api_token_file), 'r') as f:
    api_token = f.read().strip()

  lll = LegendsLeagueLeaderboard(
      filename='list_of_tags.txt',
      api_token=api_token,
      )

  lll.load_player_tags()

  current_leaderboard = lll.get_current_season_trophies()

  print(format_leaderboard(
    data=current_leaderboard,
    title=format_leaderboard_title(season=lll.current_season),
    page_no=0,
    max_lines=10,
    center=1,
    season_countdown=lll.get_countdown_current_season()
    ))


  last_leaderboard = lll.get_last_season_trophies()

  print(format_leaderboard(
    data=last_leaderboard,
    title=format_leaderboard_title(season=lll.last_season),
    page_no=0,
    max_lines=10,
    center=1,
    ))


