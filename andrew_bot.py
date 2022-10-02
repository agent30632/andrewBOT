'''Bot that mimics Andrew Liang's time-keeping
'''

import asyncio
import datetime
import json
import os
import os.path
import random

import discord
import discord.ext
from discord import errors
# import discord as dsc
from discord.ext import commands, tasks
from discord.message import Message

from bot_commands import helpers, on_messages, looped

###################################################################################################
# Bot variables

bot = commands.Bot(command_prefix='$')

# json files
settings_file = open('bot_settings.json', encoding='utf8')
settings = json.load(settings_file)
authkey_file = open('authkey.json', encoding='utf8')
authkey = json.load(authkey_file)

# data vars
bot_internals = settings["bot_internals"]
bot_data = settings["bot_data"]

andrew_intro = bot_data["dow_intro"]
andrew_outro = bot_data["dow_outro"]
dow_day_list = bot_data["dow_day_list"]

mention_responses = bot_data["mention_responses"]
extra_nut_messages = bot_data["extra_nut_messages"]

voice_lines = bot_data["voice_lines"]
# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
voice_clips = [f for f in os.listdir("audio") if os.path.isfile(os.path.join("audio", f))]

# settings
api_key = authkey['api_key']

ffmpeg_path = bot_internals["ffmpeg_path"]

first_launch_timekeeper = True
first_launch_injuries = True

###################################################################################################
# Helper Functions

def json_write():
    '''Rewrites the bot's JSON properties (mainly the internals)
    '''
    json_file_w = open('bot_settings.json', 'w', encoding='utf8')
    json.dump({"bot_internals": bot_internals,
               "bot_data": bot_data},
              json_file_w)
    print("rewrote json")

def log(command: str, server="", channel="", newline=True):
    '''Logs commands to the terminal.

    Args:
        command (str): name of the command that was run
        server (str, optional): what server the command was run from. Defaults to "".
        channel (str, optional): the channel the command was run from. Defaults to "".
        newline (bool, optional): whether to add a new line at the end. Defaults to True.
    '''
    time_str = datetime.datetime.now().strftime("%X")
    
    if server == "":
        if channel == "":
            if newline:
                print(f"[{time_str}] task: {command}")
            else:
                print(f"[{time_str}] task: {command}", end="")
    else:
        if newline:
            print(f"[{time_str}] task: {command} | location: \"{server}\" - \"{channel}\"")
        else:
            print(f"[{time_str}] task: {command} | location: \"{server}\" - \"{channel}\"", end="")

###################################################################################################
# Text commands

@bot.command(name="echo", description="echoes your message (whatever comes after the command)")
async def echo(ctx, *args):
    '''echoes whatever you type after the command

    Args:
        ctx ([type]): [description]
    '''
    log("echo", server=ctx.guild.name, channel=ctx.channel.name)
    # print('command: echo | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    message = ' '.join(args)
    await ctx.send(f'here\'s what you told me: {message}')

@bot.command(name="ping", description="pong")
async def ping(ctx):
    '''pong

    Args:
        ctx ([type]): [description]
    '''
    log("ping", server=ctx.guild.name, channel=ctx.channel.name)
    # print('command: ping | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    await ctx.send('pong')

@bot.command(name="whattime", description="tells you the time (very vaguely)")
async def whattime(ctx):
    '''Tells you the time (very vaguely)

    Args:
        ctx ([type]): [description]
    '''
    log("whattime", server=ctx.guild.name, channel=ctx.channel.name)

    # message strings
    intro = random.choice(bot_data['dow_intro'])
    outro = random.choice(bot_data['dow_outro'])
    time_string = helpers.get_time_string()

    # intro
    await ctx.send(intro)
    await asyncio.sleep(1)
    # what time + typo choice
    is_typo = random.randint(1, 50)
    print("typo choice: " + str(is_typo))
    if is_typo != 1:
        await ctx.send(time_string)
    else:
        typo_time_string = helpers.make_typo(time_string)
        await ctx.send(typo_time_string)
        await asyncio.sleep(0.5)
        await ctx.send("oops")
        await asyncio.sleep(0.5)
        await ctx.send(time_string)
    # wait
    await asyncio.sleep(1)
    await ctx.send(outro)

# binds the bot to a specific channel
@bot.command(name="bind", description="binds the automated timekeeping feature to the current channel")
async def bind(ctx):
    '''Binds the timekeeping feature to a certain channel

    Args:
        ctx ([type]): [description]
    '''
    log("bind", server=ctx.guild.name, channel=ctx.channel.name)
    # print('command: bind | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    
    print(bot_internals['bound_channel'])
    bot_internals['bound_channel'] = ctx.channel.id
    print(bot_internals['bound_channel'])
    
    bound_channel = bot.get_channel(bot_internals['bound_channel'])
    if bound_channel is None:
        await ctx.send("bind failure, ask @agent30632 to fix his bot")
    else:
        await ctx.send('bound to channel' + ' ' + bound_channel.name)
    json_write()
    
@bot.command(name="nut", aliases=["nuts"])
async def nut(ctx):
    '''[blank] these nuts.

    Args:
        ctx (_type_): _description_
    '''
    
    log("nut", server=ctx.guild.name, channel=ctx.channel.name, newline=False)
    
    try:
        msg_list = await ctx.channel.history(limit=3).flatten()
    except discord.Forbidden:
        print(" | error: invalid perms")
        await ctx.send("forbidden: need history permissions!")
        return
    except discord.HTTPException as err:
        print(f" | error: http error {err.status}")
        await ctx.send(f"http error {err.status}")
        return
    
    nut_string = helpers.these_nuts(helpers.get_last_word(msg_list[1]))
    await ctx.send(nut_string)
    print()
    
@bot.command(name="pianoman")
async def pianoman(ctx):
    '''time until piano man

    Args:
        ctx (_type_): _description_
    '''
    log(command="pianoman", server=ctx.guild.name, channel=ctx.channel.name)
    
    current_time = datetime.datetime.now()
    date = current_time.date()
    weekday = date.isoweekday()
    days_until_saturday = 6 - weekday
    
    # condition check: past or equal to saturday
    if days_until_saturday < 0:
        days_until_saturday += 7
    elif days_until_saturday == 0:
        if current_time.hour >= 21:
            # it's past 9 o'clock (or somehow exactly 9 o'clock); wait until the next one
            days_until_saturday += 7
        
    saturday_nineoclock = datetime.datetime(current_time.year,
                                            current_time.month,
                                            current_time.day + days_until_saturday,
                                            hour=21,
                                            tzinfo=current_time.tzinfo)
    
    t_minus = saturday_nineoclock - current_time
    
    # https://stackoverflow.com/a/775075
    m, s = divmod(t_minus.seconds, 60)
    h, m = divmod(m, 60)
    await ctx.send(f"t-: {t_minus.days} days, {h} hours, {m} minutes, {s} seconds")
    
###################################################################################################
# Voice commands

@bot.command(name="join", description="joins whatever voice call you're in")
async def join(ctx):
    '''Join a specific voice server

    Args:
        ctx ([type]): [description]
    '''
    log("join", server=ctx.guild.name, channel=ctx.channel.name, newline=False)
    # print('command: join | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    if ctx.author.voice is not None:        
        vc_channel = ctx.author.voice.channel
        
        # leaving whatever vc the bot is already in (if any)
        vc_client_list = bot.voice_clients
        for client in vc_client_list:
            if client.guild == ctx.guild:
                if client.channel == vc_channel:
                    return
                else:
                    await client.disconnect()
        
        # trying to join a vc
        # vc_client = None
        try:
            # vc_client = await vc_channel.connect()
            await vc_channel.connect()
        except (TimeoutError, errors.ClientException, discord.opus.OpusNotLoaded):
            # vc_client = None
            await ctx.send("error: contact bot owner for support")
    else:
        await ctx.send("please join a channel")
    
    print()
        
@bot.command(name="say", description=f"list of all voice lines: {voice_lines}")
async def say(ctx, *, line=None):
    '''Says a voice line

    Args:
        ctx (_type_): Command context
        line (_type_, optional): Says a specific voice line. Defaults to None.
    '''
    log("say", server=ctx.guild.name, channel=ctx.channel.name, newline=False)
    
    if line == "" or line is None:
        # no args
        vc_client_list = bot.voice_clients

        # getting the voice client that matches the context
        ctx_client = None
        for client in vc_client_list:
            if client.guild == ctx.guild:
                ctx_client = client

        # if the bot is not in a vc
        if ctx_client is None:
            await ctx.send("bot is not in a call!")
            print()
        else:
            # pick a certain line
            random_line = random.choice(list(voice_lines.keys()))
            matching_clips = [file for file in voice_clips if file[:file.rfind("_")] == random_line]
            andrew_voice_clip = random.choice(matching_clips)
            clip_path = os.path.join(os.getcwd(), "audio", andrew_voice_clip)
            print(" | line: " + random_line + " | clip: " + andrew_voice_clip)
            
            # play the clip
            ctx_client.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=clip_path))
    else:
        match = None
        # matching to available voice lines
        for key in voice_lines:
            for alias in voice_lines[key]:
                if alias == line and match is None:
                    match = key
                    
        if match is None:
            print()
            await ctx.send("no such voice line exists!")
        else:
            vc_client_list = bot.voice_clients
    
            # getting the voice client that matches the context
            ctx_client = None
            for client in vc_client_list:
                if client.guild == ctx.guild:
                    ctx_client = client
            
            # if the bot is not in a vc
            if ctx_client is None:
                await ctx.send("bot is not in a call!")
                print()
            else:
                # get all clips that match the line id
                matching_clips = [file for file in voice_clips if file[:file.rfind("_")] == match]
                andrew_voice_clip = random.choice(matching_clips)
                clip_path = os.path.join(os.getcwd(), "audio", andrew_voice_clip)
                print(" | clip: " + andrew_voice_clip)
                
                # play the clip
                ctx_client.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=clip_path))

@say.error
async def say_error(ctx, error):
    '''Error handling for $say

    Args:
        ctx ([type]): [description]
        error ([type]): [description]
    '''
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("please specify a voice line!")

@bot.command(name="leave", description="leaves the current voice call")
async def leave(ctx):
    '''Leave the current voice channel

    Args:
        ctx ([type]): [description]
    '''
    log("leave", server=ctx.guild.name, channel=ctx.channel.name)
    
    vc_client_list = bot.voice_clients
    
    call_left = False
    
    for client in vc_client_list:
        if client.guild == ctx.guild:
            call_left = True
            await client.disconnect()
            await ctx.send(":(")
            
    if not call_left:
        await ctx.send("not connected to a call!")

###################################################################################################
# Looping/concurrent tasks

@tasks.loop(hours=3, minutes=8, seconds=24)
async def timekeeper():
    '''Time keeping
    '''
    bound_channel = bot.get_channel(bot_internals["bound_channel"])
    if bound_channel is not None:
        log("timekeeper", server=bound_channel.guild.name, channel=bound_channel.name, newline=False)

    if bound_channel is None:
        print("you better start binding")
        return
    
    global first_launch_timekeeper
    if first_launch_timekeeper:
        print()
        first_launch_timekeeper = False
        return
    
    messages = await looped.timekeeper()
    
    # intro text
    await bound_channel.send(messages[1])
    await asyncio.sleep(1)
    # what time + typo
    if not messages[0]:
        await bound_channel.send(messages[2])
    else:
        await bound_channel.send(messages[2])
        await asyncio.sleep(0.5)
        await bound_channel.send("oops")
        await asyncio.sleep(0.5)
        await bound_channel.send(messages[3])
    # outro text
    await asyncio.sleep(1)
    await bound_channel.send(messages[-1])
    
@tasks.loop(hours=7, minutes=36)
async def injuries():
    '''randomly injures andrew'''
    bound_channel = bot.get_channel(bot_internals["bound_channel"])
    if bound_channel is not None:
        log("injury", server=bound_channel.guild.name, channel=bound_channel.name, newline=False)
    else:
        print("you better start binding")
        return
    
    global first_launch_injuries
    if first_launch_injuries:
        print(" | first launch ignore")
        first_launch_injuries = False
        return

    rand_choice = random.randint(0, 1)
    if rand_choice != 0:
        print(f" | odds: {rand_choice}")
        return

    messages = await looped.injuries()
    
    print(f" | choices: {messages}")
    
    await bound_channel.send(messages[0])
    await asyncio.sleep(1)
    await bound_channel.send(messages[1])
    await asyncio.sleep(1)
    await bound_channel.send(messages[2])
    
async def saturday_nine_oclock_init():
    '''initializes the saturday_nine_oclock function
    '''
    log(command="saturday 9 o'clock initialize")
    
    time_until_saturday_nineoclock = helpers.find_next_saturday()
    
    # wait until it's saturday wooo
    await asyncio.sleep(time_until_saturday_nineoclock.total_seconds())
    await saturday_nine_oclock()
    
async def saturday_nine_oclock():
    '''it's nine o'clock on a saturday
    '''
    
    bound_channel = bot.get_channel(bot_internals["bound_channel"])
    if bound_channel is not None:
        log("timekeeper", server=bound_channel.guild.name, channel=bound_channel.name, newline=False)
    else:
        print("no bound channel for \"nine-o'clock on a saturday\" function!")
        return

    await bound_channel.send("it's nine o'clock on a saturday")
    await asyncio.sleep(0.3)
    await bound_channel.send("https://www.youtube.com/watch?v=gxEPV4kolz0")
    
    # wait a day until the next iteration (assuming the bot can actually run for a day lol)
    await saturday_nine_oclock_init()

@tasks.loop(minutes=30)
async def idle_dc():
    '''Disconnect when idle
    '''
    vc_client_list = bot.voice_clients
    
    for client in vc_client_list:
        if len(client.channel.members) <= 1:
            await client.disconnect()
            log("voice idle dc", server=client.guild.name, channel=client.channel.name)
            
###################################################################################################
# On message commands

@bot.listen("on_message")
async def random_response(message: Message):
    '''Random response to a message

    Args:
        message (Message): the message to respond to
    '''
    log("random response", server=message.guild.name, channel=message.channel.name, newline=False)
    
    await on_messages.random_response(message)
    
@bot.listen("on_message")
async def mention_response(message: Message):
    '''Responds when mentioned

    Args:
        message (Message): [description]
    '''
    if bot.user.mentioned_in(message):
        log("mention response", server=message.guild.name, channel=message.channel.name, newline=False)
        
        await on_messages.mention_response(message)
               
@bot.event
async def on_command_error(ctx, error):
    '''CommandNotFound handler

    Args:
        ctx ([type]): [description]
        error ([type]): [description]
    '''
    if isinstance(error, commands.CommandNotFound):
        ctx.send("not a real command!")

###################################################################################################
# bot startup
@bot.event
async def on_ready():
    '''Runs when the bot is ready
    '''
    print(f'logged in as {bot.user}')
    timekeeper.start()
    injuries.start()
    
    game = discord.Game("these nuts.")
    await bot.change_presence(activity=game)
    
    await saturday_nine_oclock_init()

bot.run(api_key)
