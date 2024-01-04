import apex_info
import asyncio
import datetime
import discord
import league_info
import shlex

from datetime import datetime, timedelta, time
from discord.ext import commands, tasks
from dotenv import dotenv_values
from zoneinfo import ZoneInfo

# Read API keys, tokens, guild ID from config file
config = dotenv_values('.env')
token = config.get('DISCORD_TOKEN')
# guild_id = config['Credentials']['SERVER_ID']

# set up intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# set up timezones
tz = [ZoneInfo('US/Pacific'), ZoneInfo('US/Eastern'), ZoneInfo('GMT'), ZoneInfo('Asia/Shanghai')]

# global variables for guild and channels
# guild = None
# time_channels = None
channels = {}


@bot.event
async def on_ready():
    # get channel IDs
    # global guild
    # guild = bot.get_guild(int(guild_id))
    global channels
    channels = {
        'world_clock': discord.utils.get(bot.get_all_channels(), name='world-clock'),
        'crafting': discord.utils.get(bot.get_all_channels(), name='crafting-rotation'),
        'map': discord.utils.get(bot.get_all_channels(), name='map-rotation'),
        'status': discord.utils.get(bot.get_all_channels(), name='server-status'),
        'bot-commands': discord.utils.get(bot.get_all_channels(), name='bot-commands')
    }
    # global time_channels
    # time_channels = discord.utils.get(guild.categories, name='time')

    # Start tasks at the top of each minute (0th second)
    now = datetime.now()
    await asyncio.sleep(60 - now.second)
    update_time.start()
    update_crafting.start()
    update_maps.start()
    update_status.start()
    # update_channel_time.start()

    print('Bot is running.')


# Updates the name of voice channels to reflect the current time in certain timezones.
# This function is commented out and not used due to Discord's rate limits on editing voice channels.
@tasks.loop(minutes=1)
async def update_channel_time():
    # Update PT
    time1 = datetime.now(tz=pst)
    pst_channel = time_channels.voice_channels[0]
    await pst_channel.edit(name='PT - ' + str(time1.hour) + ':' + str(time1.minute))
    # Update GMT
    time2 = datetime.now(tz=gmt)
    gmt_channel = time_channels.voice_channels[1]
    await gmt_channel.edit(name='GMT - ' + str(time2.hour) + ':' + str(time2.minute))
    # Update CST (China time)
    time3 = datetime.now(tz=cst)
    cst_channel = time_channels.voice_channels[2]
    await cst_channel.edit(name='CST - ' + str(time3.hour) + ':' + str(time3.minute))


# Posts an embed message containing the current date + time of various timezones in the world.
# Timezones are provided via the tz list above.
@tasks.loop(minutes=1)
async def update_time():
    # Delete bot's previous message in channel
    # limit=1 assumes the channel will not have any other messages.
    await channels['world_clock'].purge(limit=1)

    # Create embed message
    embed = discord.Embed(
        title='World Clock',
        description='Current time of day of various timezones in the world.',
        color=discord.Colour.light_gray())

    for t in tz:
        td = datetime.now(tz=t)
        day = td.date().strftime('%A')  # get weekday in English
        date = td.date().strftime('%B') + ' ' + str(td.day) + ', ' + str(td.year)  # get month's name
        time = str(td.hour) + ':' + td.time().strftime('%M')  # get HH:MM
        hour_offset = int(td.utcoffset().total_seconds()/3600)  # convert UTC offset to hours only
        offset = ' (UTC'  # build utc offset string
        if (hour_offset != 0):
            if (hour_offset > 0):
                offset = offset + '+'
            offset = offset + str(hour_offset)
        offset = offset + ')'
        embed.add_field(
            name=str(td.tzinfo) + offset,
            value=day + ', ' + date + ', ' + time,
            inline=False)

    # Time debugging
    now = datetime.now()
    print('World clock updated at ' + str(now).split('.')[0])

    await channels['world_clock'].send(embed=embed)


# Posts an embed mesage containing the current crafting rotation in Apex Legends.
# Daily rotations update at 10 AM PT, while weekly rotations update on Sundays.
@tasks.loop(time=time(hour=10, minute=1, tzinfo=ZoneInfo('US/Pacific')))
async def update_crafting():
    # Delete bot's previous message in channel
    # limit=1 assumes the channel will not have any other messages.
    await channels['crafting'].purge(limit=1)

    crafting = await apex_info.get_crafting()

    # Get unix timestamp 24 hours from now
    next = (datetime.now() + timedelta(hours=24)).timestamp()
    next = '<t:' + str(next).split('.')[0] + ':R>'

    # Create embed message
    embed = discord.Embed(
        title='Current Crafting Rotation',
        description='Next rotation ' + next + '\n' +
            'Information provided by [Apex Legends Status](https://apexlegendsstatus.com/).',
        color = discord.Colour.orange())

    for item in crafting:
        embed.add_field(name=item, value=crafting[item], inline=False)

    embed.timestamp = datetime.now()

    # Time debugging
    now = datetime.now()
    print('Crafting rotation updated at ' + str(now).split('.')[0])

    await channels['crafting'].send(embed=embed)


# Posts an embed mesage containing the current map rotation in Apex Legends.
@tasks.loop(minutes=15)
async def update_maps():
    # Delay task until 0/15/30/45 mins after the hour
    cur_time = datetime.now()
    delay = (15 - (cur_time.minute % 15)) % 15
    await asyncio.sleep(delay * 60)

    # Delete bot's previous message in channel
    # limit=1 assumes the channel will not have any other messages.
    await channels['map'].purge(limit=1)

    # Get unix timestamp 15 minutes from now
    next = (datetime.now() + timedelta(minutes=15)).timestamp()
    next = '<t:' + str(next).split('.')[0] + ':R>'

    maps = await apex_info.get_maps()

    # Create embed message
    embed = discord.Embed(
        title='Current Map Rotation',
        description='Next rotation ' + next + '\n' +
            'Information provided by [Apex Legends Status](https://apexlegendsstatus.com/).',
        color=discord.Colour.blue())

    for mode in maps:
        embed.add_field(name=mode + ':', value=maps[mode], inline=False)
    embed.timestamp = datetime.now()

    # Time debugging
    now = datetime.now()
    print('Map rotation updated at ' + str(now).split('.')[0])

    await channels['map'].send(embed=embed)


# Posts an embed message containing the current matchmaking server status in Apex Legends.
@tasks.loop(minutes=60)
async def update_status():
    # Delay task until top of the hour
    cur_time = datetime.now()
    delay = 60 - cur_time.minute
    await asyncio.sleep(delay * 60)

    # Delete bot's previous message in channel
    # limit=1 assumes the channel will not have any other messages.
    await channels['status'].purge(limit=1)

    status = await apex_info.get_status()

    # Create embed message
    embed = discord.Embed(
        title='Current Matchmaking Server Status',
        description='Information provided by [Apex Legends Status](https://apexlegendsstatus.com/).',
        color=discord.Colour.green())

    for server in status:
        embed.add_field(name=server + ':', value=status[server], inline=False)
    embed.timestamp = datetime.now()

    # Time debugging
    now = datetime.now()
    print('Server status updated at ' + str(now).split('.')[0])

    await channels['status'].send(embed=embed)


# Posts an embed message containing a list of what user(s) are ingame in League of Legends.
@bot.command(brief='Checks whether certain user(s) are ingame in League of Legends.')
async def check(ctx, *,
                args = commands.parameter(default=None, description='A sequence of Riot ID(s) to look up,'
                                           + ' each separated by a space.')):
    """
        Checks whether certain user(s), denoted by Riot ID, are currently ingame in League of Legends.
        Riot IDs are made up of a game name + a tagline preceded by a "#" (i.e. "Example#NA1").
        IDs containing spaces should be enclosed in quotes to be recognized as a single name (i.e. "Test Example#NA1").
        If a tagline is not specified, it will default to NA1.
        A minimum of 1 Riot ID is required to use the command, up to a max of 20.
    """
    if not ctx.channel == channels['bot-commands']:
        return
    else:
        if args == None:
            await ctx.send('At least one valid Riot ID is required in order to retrieve information.')
            return
        arglist = shlex.split(args)  # keeps id's in quotes intact
        if len(arglist) >= 20:
            await ctx.send('Too many Riot IDs - found '
                           + str(len(arglist)) + '. Try again with 20 or fewer IDs.')
            return
        else:
            # Create embed message
            embed = discord.Embed(
                title='Player In-Game Status and Gametime',
                color=discord.Colour.light_gray())
            embed.add_field(name='Name:', value='', inline=True)
            embed.add_field(name='Status:', value='', inline=True)
            embed.add_field(name='Gametime:', value='', inline=True)
            # Look up status for each given player
            for arg in arglist:
                id = arg.split('#', 1)
                name = id[0]
                if len(id) == 1:
                    tag = 'NA1'  # default tagline to #NA1 if one is not given
                else:
                    tag = id[1]
                result = await league_info.request_status(name, tag)
                embed.add_field(name='', value=name + '#' + tag, inline=True)
                embed.add_field(name='', value=result['status'], inline=True)
                embed.add_field(name='', value=result['gameTime'], inline=True)
            embed.timestamp = datetime.now()
            await ctx.send(embed=embed)


# Behavior when a user posts a non-command message.
@bot.event
async def on_message(message):
    # Ignore messages from bot to prevent looping
    if message.author.bot:
        return

    # ignore messages that start with command symbol
    if not message.content.startswith('!'):
        pass

    # Allows compatibility with commands
    await bot.process_commands(message)


def run_bot():
    bot.run(token)