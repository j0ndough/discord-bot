# discord-bot
Personal Discord Bot that contains features I find interesting and/or useful.

## Current Features

* World clock: displays the current time in various timezones around the world. Updates every minute.
* Apex Legends: displays the current crafting and map rotations, as well as the current matchmaking server status.
* League of Legends: a command to check if a player is currently ingame. Useful if you want to queue for a game
while avoiding specific player(s).

## Commands
Commands can only be used in the `#bot-commands` channel.

`!check <RiotID1> <RiotID2> ...` checks whether certain player(s) (denoted by Riot ID) is currently ingame.
If the player is currently ingame, it also lists the current game time of their match. Accepts a min of 1 Riot ID
per command, and a max of 20 Riot IDs per command.

## Requirements

Rename `config.cfg` to `api_config.cfg` and add the following variables:

```
APEX_API_KEY =

DISCORD_TOKEN =

LEAGUE_API_KEY =
```

These variables should be filled with their respective API keys/tokens.

**What the variables do**

`APEX_API_KEY` - can be obtained through [Apex Legends Status](https://portal.apexlegendsapi.com/).
Provides endpoints for querying Apex related information (map rotation, server status, crafting rotation, etc).

`DISCORD_TOKEN` - can be obtained through [Discord's Developer Portal](https://discord.com/developers/applications).
To get a new token, click the **New Application** button at the top right of the page.

`LEAGUE_API_KEY` - can be obtained through [Riot's Developer Portal](https://developer.riotgames.com/).
Developer keys are handed out freely but refresh every 24 hours, but a production key can be obtained via
My Account -> Dashboard -> Register Product.