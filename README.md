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

