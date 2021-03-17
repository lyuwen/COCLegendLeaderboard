import os
import pandas as pd
import sqlite3 as sql

from legends_leaderboard import LegendsLeagueLeaderboard


PATH = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    empty_players = pd.Series([], dtype=str)
    empty_clans = pd.Series([], dtype=str)
    empty_leaderboard = pd.DataFrame(columns = ['player_tag', 'name', 'trophies', 'timestamp'])
    empty_season = pd.Series("")

    if os.path.exists(os.path.join(PATH, LegendsLeagueLeaderboard.dbname)):
      raise OSError("Database file already exists.")

    with sql.connect(os.path.join(PATH, LegendsLeagueLeaderboard.dbname)) as con:
        empty_players.to_sql("player_tags", con=con)
        empty_clans.to_sql("qualified_clans", con=con)
        empty_leaderboard.to_sql('leaderboard', con=con)
        empty_season.to_sql('season', con=con)
