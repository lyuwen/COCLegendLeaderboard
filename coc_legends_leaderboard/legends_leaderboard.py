import calendar
import datetime


def get_last_monday_of_month(year, month):
  """
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
  """
  calendar_month = calendar.monthcalendar(year, month)
  mondays = [week[0] for week in calendar_month if week[0]>0]
  return datetime.datetime(year, month, mondays[-1])


def get_last_month(year, month):
  """ Find last month.

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
  """
  first_day_this_month = datetime.datetime(year, month, 1)
  last_day_last_month = first_day_this_month - datetime.timedelta(days=1)
  return last_day_last_month.year, last_day_last_month.month


def get_next_month(year, month):
  """ Find next month.

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
  """
  return calendar.nextmonth(year=year, month=month)


class LegendsLeagueLeaderboard:
  """
  Make a Legends League leaderboard

  Parameters
  ----------
  filename : the file to 
  """


  def __init__(self, filename):
    self.filename = filename


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
    hours = getattr(timedelta, "hours", timedelta.seconds // 3600)
    return (days, hours)


  @property
  def current_season(self):
    year, month = self._get_current_season()
    return "{year}-{month}".format(year=year, month=month)


  @property
  def last_season(self):
    year, month = self._get_current_season()
    last_month_year, last_month_month = get_last_month(year, month)
    return "{year}-{month}".format(year=last_month_year, month=last_month_month)
