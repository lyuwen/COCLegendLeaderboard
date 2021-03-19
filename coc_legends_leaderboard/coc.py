import os
import json
import aiohttp
import asyncio
import logging
import datetime
import dateutil.parser
from urllib.parse import quote
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
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

    async def get_player_info(self, player_tag):
        """ Get player info from player tag.

        Parameters
        ----------
        player_tag : str, starts with '#'
            The player tag '#...'.

        Returns
        -------
        player_info : dict
            A dictionary of the JSON data returned from the request.
        """
        url = self.base_url + "/players/" + quote(player_tag)
        async with aiohttp.ClientSession() as session:
          async with session.get(url, headers=self.headers) as respond:
            if respond.status == 200:
                return await respond.json()
            else:
                raise RuntimeError("Failed to obtain player information.")

    async def get_clan_info(self, clan_tag):
        """ Get clan info from clan tag.

        Parameters
        ----------
        clan_tag : str, starts with '#'
            The clan tag '#...'.

        Returns
        -------
        clan_info : dict
            A dictionary of the JSON data returned from the request.
        """
        url = self.base_url + "/clans/" + quote(clan_tag)
        async with aiohttp.ClientSession() as session:
          async with session.get(url, headers=self.headers) as respond:
            if respond.status == 200:
                return await respond.json()
            else:
                raise RuntimeError("Failed to obtain clan information.")

    async def get_league_info(self):
        """ Get home village trophy league info.

        Returns
        -------
        leagues : dict
            A dictionary of the JSON data returned from the request.
        """
        url = self.base_url + "/leagues"
        async with aiohttp.ClientSession() as session:
          async with session.get(url, headers=self.headers) as respond:
            if respond.status == 200:
                return await respond.json()
            else:
                raise RuntimeError("Failed to obtain clan information.")

    async def get_sccwl_group_info(self, clan_tag):
        """ Get the league group info of current SCCWL season of the clan.

        Parameters
        ----------
        clan_tag : str, starts with '#'
            The clan tag '#...'.

        Returns
        -------
        sccwl_group_info : dict
            A dictionary of the JSON data returned from the request.
        """
        url = self.base_url + \
            '/clans/{clan_tag}/currentwar/leaguegroup'.format(
                clan_tag=quote(clan_tag))
        async with aiohttp.ClientSession() as session:
          async with session.get(url, headers=self.headers) as respond:
            if respond.status == 200:
                return await respond.json()
            else:
                raise RuntimeError("Failed to obtain sccwl group information.")

    async def get_sccwl_lineup(self, clan_tag):
        """ Get the SCCWL lineup of the clan of the current season.

        Parameters
        ----------
        clan_tag : str, starts with '#'
            The clan tag '#...'.

        Returns
        -------
        lineup : list
            List of members that are in the SCCWL spin.
        """
        info = await self.get_sccwl_group_info(clan_tag=clan_tag)
        for clan in info['clans']:
            if clan['tag'] == clan_tag:
                current_clan = clan
        return current_clan['members']

    async def check_clan_pass_sccwl_scan(self, clan_tag, verbose=False):
        """ Check if clan has banned members after SCCWL.

        Parameters
        ----------
        clan_tag : str, starts with '#'
            The clan tag '#...'.
        verbose  : bool, optional, default to Fase
            Whether to print out players that got banned.

        Returns
        -------
        flag : bool
            If True, clan does not have banned members, vice versa.
        """
        lineup = await self.get_sccwl_lineup(clan_tag=clan_tag)
        for player in lineup:
            try:
                await self.get_player_info(player['tag'])
            except RuntimeError:
                if verbose:
                    logging.warning('player {} ({}) not found, th{}'.format(
                        player['name'], player['tag'], player['townHallLevel']))
                return False
        return True

    async def get_current_war_info(self, clan_tag):
        """ Get current war info from clan tag.

        Parameters
        ----------
        clan_tag : str, starts with '#'
            The clan tag '#...'.

        Returns
        -------
        current_war_info : dict
            A dictionary of the JSON data returned from the request.
        """
        url = self.base_url + "/clans/" + quote(clan_tag) + "/currentwar"
        async with aiohttp.ClientSession() as session:
          async with session.get(url, headers=self.headers) as respond:
            if respond.status == 200:
                return await respond.json()
            else:
                raise RuntimeError(
                    "Failed to obtain clan current war information.")

    async def print_current_war(self, clan_tag):
        """ Print out the status of the current war of the clan.

        Parameters
        ----------
        clan_tag : str, starts with '#'
            The clan tag '#...'.
        """
        war_info = await self.get_current_war_info(clan_tag)
        player_names = {}
        clan_name = war_info['clan']['name']
        opponent_name = war_info['opponent']['name']
        # at most 2 hits each player
        attacks = [None, ] * war_info['teamSize'] * 4 
        clan_stars = war_info['clan']['stars']
        clan_percent = war_info['clan']['destructionPercentage']
        opponent_stars = war_info['opponent']['stars']
        opponent_percent = war_info['opponent']['destructionPercentage']

        for member in war_info['clan']['members'] + war_info['opponent']['members']:
            player_names[member['tag']] = member['name']

        def format_stars(stars):
            return '⭐️' * stars + '   ' * (3 - stars)

        for member in war_info['clan']['members']:
            for attack in member.get('attacks', []):
                stars = format_stars(attack['stars'])
                percent = '{:>3.2f}%'.format(attack['destructionPercentage'])
                attacks[attack['order']] = '{:<15s} -- {} {} -> {:>15s}'.format(
                    player_names[attack['attackerTag']],
                    stars,
                    percent,
                    player_names[attack['defenderTag']],
                )

        for member in war_info['opponent']['members']:
            for attack in member.get('attacks', []):
                stars = format_stars(attack['stars'])
                percent = '{:>3.2f}%'.format(attack['destructionPercentage'])
                attacks[attack['order']] = '{:<15s} <- {} {} -- {:>15s}'.format(
                    player_names[attack['defenderTag']],
                    stars,
                    percent,
                    player_names[attack['attackerTag']],
                )

        clan_percent_str = '{:>3.2f}%'.format(clan_percent)
        opponent_percent_str = '{:>3.2f}%'.format(opponent_percent)
        linewidth = 53
        separation = '-' * linewidth
        output = [
            separation,
            str.center('{:<15s} v {:>15s}'.format(
                clan_name, opponent_name), linewidth),
            str.center('{:<15d} - {:>15d}'.format(clan_stars,
                                                  opponent_stars), linewidth),
            str.center('{:<15s} - {:>15s}'.format(clan_percent_str,
                                                  opponent_percent_str), linewidth),
            separation,
        ]
        for attack in attacks:
            if attack is not None:
                output.append(attack)
        output.append(separation)
        # output.append(war_info['state'])

        if war_info['state'] == 'preparation':
            now = datetime.datetime.utcnow().replace(microsecond=0)
            starttime = dateutil.parser.parse(
                war_info['startTime']).replace(tzinfo=None)
            delta = starttime - now
            output.append(
                'Preperation day. Battle day starts in {!s}.'.format(delta))
        elif war_info['state'] == 'inWar':
            now = datetime.datetime.utcnow().replace(microsecond=0)
            endtime = dateutil.parser.parse(
                war_info['endTime']).replace(tzinfo=None)
            delta = endtime - now
            output.append('Battle day. Battle day ends in {!s}.'.format(delta))

        print('\n'.join(output))


    async def verify_player(self, player_tag, token):
        """ Verify player's account with in-game API token.

        Parameters
        ----------
        player_tag : str, starts with '#'
            The player tag '#...'.
        token      : str
            The API token.

        Returns
        -------
        verification : bool
            Whether the player is verified with the API token.
        """
        url = self.base_url + "/players/" + quote(player_tag) + "/verifytoken"
        body = {
            "token": token,
        }
        async with aiohttp.ClientSession() as session:
          async with session.get(url, headers=self.headers) as respond:
            if respond.status == 200:
                status = await respond.json()['status']
                return status.lower() == "ok"
            else:
                raise RuntimeError("Failed to obtain player information.")
            
            
if __name__ == "__main__":
    load_dotenv()
    api_token = os.getenv("COC_TOLEN")
    coc = ClashOfClans(api_token)
