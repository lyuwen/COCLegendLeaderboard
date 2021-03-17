# Discord bot to make COC Legends League Leaderboard


This bot can take a group of player and create a Legends League Leaderboard for competition.


## Clash of Clans API

As part of the project, a python wrapper of the Clash of Clans API is developed to facilitate
all the API requets.


## Development guide

After cloning the repository, create a virtual environment and install all required python
packages

```python
python -m virtualenv venv && . ./venv/bin/activate
pip install -U -r requirements.txt
```

and go into the `coc_legends_leaderboard` directory and create an `.venv` file from the example
file `dotenv_example`, and put all the API tokens and the discord guild id for the bot.


## Bot command guide

* `!rankings`: Show the leaderboard.

    ```
        Usage !rankings [-h|--help] [-r|--refresh] [-l|--last-season]

          -h, --help          show this help message.
          -r, --refresh       refresh the leaderboard before show ranking.
          -l, --last-season   load last season's end-of-season leaderboard.
    ```
    
* `!refresh`: Refresh the leaderboard.
* `!register`: Register player(s) to the leaderboard
* `!remove`: Remove player(s) from the leaderboard
* `!players`: Show the players that are participating the leaderboard. 


## Available features

Here are the features available with the bot:

* Add and remove players into legend leaderboard. (The removal of player requires admin privilege)
* Add clans to the database so that only players in the registered clans can be added to the leaderboard. 
  This feature is restricted to admin privilege.
* Show legend leaderboard of current and last season. For leaderboards that are too long, reaction buttons
  can be used to flip between pages.
* Show players that are registered in the leaderboard.
* Show clans that players must be in when register.
* The leaderboard is stored into database and does not refresh unless requested. This shortens the time
  it takes to post the leaderboard.
  
Here are features available in COC python API module:
* Request player information through player tag.
* Verify a player's account through in-game API token.
* Request clan information via clan tag.
* Get current war of a clan and show war stats (total stars and percent, time remaining, attacks done,
  stars and percentages of attacks).
* Check if a clan's last SCCWL roster has players that got banned since SCCWL concluded.
  
## Features to be added

Features for bot:

* Add a daemon to refresh the leaderboard regularly in the background.
* Make the max number of lines for each page configurable.
* Make prefix of the command configurable.

Features for COC python API:

* Add the rest of the API request types that are supported by Clash of Clans API.

Currently the support for multipld discord servers (guilds) are not considered.
As the current project is intended for smaller scales.
