import os
import json
import requests
from urllib.parse import quote


PATH = os.path.dirname(os.path.abspath(__file__))


class ClashOfClans:
  """
  Generic Clash of Clans API wrapper.

  This wrapper can handle all the requests to the Clash of Clans API.

  Paremeters
  ----------
  api_token : str
      The API token for authentication.
  """


  base_url = "https://api.clashofclans.com/v1"


  def __init__(self, api_token):
      self.api_token = api_token


  @property
  def headers(self):
      """ The request headers.
      """
      headers = {
          "Accept": "application/json",
          "authorization": "Bearer {api_token}".format(api_token=self.api_token),
          }
      return headers


  def get_player_info(self, player_tag):
      """ Get player info from player tag.
      """
      url = self.base_url + "/players/" + quote(player_tag)
      respond = requests.get(url, headers=self.headers)
      if respond.status_code == 200:
          return respond.json()
      else:
          raise RuntimeError("Failed to obtain player information.")


  def get_clan_info(self, clan_tag):
      """ Get clan info from clan tag.
      """
      url = self.base_url + "/clans/" + quote(clan_tag)
      respond = requests.get(url, headers=self.headers)
      if respond.status_code == 200:
          return respond.json()
      else:
          raise RuntimeError("Failed to obtain clan information.")


  def get_league_info(self):
      """ Get league info.
      """
      url = self.base_url + "/leagues"
      respond = requests.get(url, headers=self.headers)
      if respond.status_code == 200:
          return respond.json()
      else:
          raise RuntimeError("Failed to obtain clan information.")
          
 	
  def get_sccwl_group_info(self, clan_tag):
      url = self.base_url + '/clans/{clan_tag}/currentwar/leaguegroup'.format(clan_tag=quote(clan_tag))
      respond = requests.get(url, headers=self.headers)
      if respond.status_code == 200:
          return respond.json()
      else:
          raise RuntimeError("Failed to obtain sccwl group information.")
          
          
  def get_sccwl_lineup(self, clan_tag):
      info = self.get_sccwl_group_info(clan_tag=clan_tag)
      for clan in info['clans']:
        if clan['tag'] == clan_tag:
          current_clan = clan
      return  current_clan['members']


  def check_clan_pass_sccwl_scan(self, clan_tag, verbose=False):
      lineup = self.get_sccwl_lineup(clan_tag=clan_tag)
      for player in lineup:
        try:
          self.get_player_info(player['tag'])
        except RuntimeError:
          if verbose:
            print('player {} ({}) not found, th{}'.format(player['name'], player['tag'], player['townHallLevel']))
          return False
      return True
       


if __name__ == "__main__":
  api_token_file = "apitoken.in"
  with open(os.path.join(PATH, api_token_file), "r") as f:
    api_token = f.read().strip()
  coc = ClashOfClans(api_token)
