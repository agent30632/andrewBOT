'''Bot that mimics Andrew Liang's time-keeping
'''

import datetime
import json
import os
import os.path
import random
import time

import discord
import discord.ext
from discord import errors
# import discord as dsc
from discord.ext import commands, tasks
from discord.message import Message

import typo_gen

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

andrew_intro = bot_data["intro"]
andrew_outro = bot_data["outro"]
day_of_week_list = bot_data["day_of_week_list"]

mention_resposes = bot_data["mention_responses"]

voice_lines = bot_data["voice_lines"]
# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
voice_clips = [f for f in os.listdir("audio") if os.path.isfile(os.path.join("audio", f))]

# settings
api_key = authkey['api_key']

ffmpeg_path = bot_internals["ffmpeg_path"]

first_launch = True

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

def get_time_string() -> str:
    '''Gets a string that represents the current date and time (as written by Andrew Liang)

    Returns:
        str: Andrew Liang compliant time string
    '''
    
    current_time = datetime.datetime.now()
    
    hour = current_time.hour
    day_of_week = day_of_week_list[current_time.weekday()]
    
    time_of_day = ''
    if hour >= 0 and hour < 3:
        time_of_day = ' already'
    if hour >= 3 and hour < 12:
        time_of_day = ' morning'
    elif hour >= 12 and hour < 13:
        time_of_day = ' lunchtime'
    elif hour >= 13 and hour < 17:
        time_of_day = ' afternoon'
    elif hour >= 17 and hour < 20:
        time_of_day = ' evening'
    elif hour >= 20 and hour < 24:
        time_of_day = ' night'
        
    return "it's " + day_of_week + time_of_day

def get_last_word(message: Message) -> str:
    '''Gets the last word from a message, filtering for punctuation.

    Args:
        message (Message): Discord message to scan

    Returns:
        str: the last word in the Message
    '''

    message_content = message.content.strip()
    last_word = message_content.split(" ")[-1]
    last_letter_index = len(last_word)
    for i, char in enumerate(last_word):
        if char != "." and char != "?" and char != "!" and char != "\"":
            last_letter_index = i

    last_word = last_word[:last_letter_index + 1]
    return last_word

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
    await ctx.send('here\'s what you told me: {}'.format(' '.join(args)))

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
    # current_time = datetime.datetime.now()
    # print('command: whattime | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name + " | time: " + current_time.strftime('%c'))

    # message strings
    intro = random.choice(bot_data['intro'])
    outro = random.choice(bot_data['outro'])
    time_string = get_time_string()

    # intro
    await ctx.send(intro)
    time.sleep(1)
    # what time + typo choice
    is_typo = random.randint(1, 50)
    print("typo choice: " + str(is_typo))
    if is_typo != 1:
        await ctx.send(time_string)
    else:
        typo_time_string = typo_gen.make_typo(time_string)
        await ctx.send(typo_time_string)
        time.sleep(0.5)
        await ctx.send("oops")
        time.sleep(0.5)
        await ctx.send(time_string)
    # wait
    time.sleep(1)
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
    
@bot.command(name="nut")
async def nut(ctx):
    '''[blank] these nuts.

    Args:
        ctx (_type_): _description_
    '''
    try:
        msg_list = await ctx.channel.history(limit=3).flatten()
    except discord.Forbidden:
        await ctx.send("forbidden: need history permissions!")
        return
    except discord.HTTPException as err:
        await ctx.send(f"http error {err.status}")
        return
        
    await ctx.send(get_last_word(msg_list[1]) + " these nuts.")
    
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
        
# @bot.command(name="speak", description="says a random Andrew voice clip")
# async def speak(ctx):
#     '''Say a random voice clip

#     Args:
#         ctx ([type]): [description]
#     '''
#     log("speak", server=ctx.guild.name, channel=ctx.channel.name, newline=False)
    
#     vc_client_list = bot.voice_clients
    
#     # getting the voice client that matches the context
#     ctx_client = None
#     for client in vc_client_list:
#         if client.guild == ctx.guild:
#             ctx_client = client
    
#     # if the bot is not in a vc
#     if ctx_client is None:
#         await ctx.send("bot is not in a call!")
#         print()
#     else:
#         # pick a certain line
#         random_line = random.choice(list(voice_lines.keys()))
#         matching_clips = [file for file in voice_clips if file[:file.rfind("_")] == random_line]
#         andrew_voice_clip = random.choice(matching_clips)
#         clip_path = os.path.join(os.getcwd(), "audio", andrew_voice_clip)
#         print(" | line: " + random_line + " | clip: " + andrew_voice_clip)
        
#         # play the clip
#         ctx_client.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=clip_path))
        
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

@tasks.loop(hours=2.0)
async def timekeeper():
    '''Time keeping
    '''
    # current_time = datetime.datetime.now()
    # print('task: timekeeper | time: ' + current_time.strftime('%c'))
    bound_channel = bot.get_channel(bot_internals["bound_channel"])
    if bound_channel is not None:
        log("timekeeper", server=bound_channel.guild.name, channel=bound_channel.name, newline=False)

    if bound_channel is None:
        print("you better start binding")
        return
    
    global first_launch
    if first_launch:
        print()
        first_launch = False
        return
    
    # current_time = datetime.datetime.now()
    
    intro = random.choice(bot_data["intro"])
    time_string = get_time_string()
    outro = random.choice(bot_data["outro"])
    
    # intro text
    await bound_channel.send(intro)
    time.sleep(1)
    # what time + typo
    is_typo = random.randint(1, 50)
    print(" | typo choice: " + str(is_typo))
    if is_typo != 1:
        await bound_channel.send(time_string)
    else:
        typo_time_string = typo_gen.make_typo(time_string)
        await bound_channel.send(typo_time_string)
        time.sleep(0.5)
        await bound_channel.send("oops")
        time.sleep(0.5)
        await bound_channel.send(time_string)
    # outro text
    time.sleep(1)
    await bound_channel.send(outro)

@tasks.loop(minutes=30)
async def idle_dc():
    '''Disconnect when idle
    '''
    vc_client_list = bot.voice_clients
    
    for client in vc_client_list:
        if len(client.channel.members) <= 1:
            await client.disconnect()
            log("voice idle dc", server=client.guild.name, channel=client.channel.name)
            

@bot.listen("on_message")
async def random_response(message: Message):
    '''Random response to a message

    Args:
        message (Message): the message to respond to
    '''
    msg_channel = message.channel
    
    # ignore mentions
    if bot.user.mentioned_in(message):
        return
    
    # ignore bot messages
    if message.author.bot:
        return
    
    # ignore commands
    if len(message.content) > 0:
        if message.content[0] == "$":
            return
    
    # log to console
    log("random response", server=message.guild.name, channel=message.channel.name, newline=False)
    
    # random chance to respond
    resp_rand = random.randint(1, 50)
    print(" | odds = " + str(resp_rand), end="")
    
    # failed roll and/or message is by bot
    if resp_rand != 1:
        print()
        return
    
    # choosing an adequate response
    resp_choice = random.randint(1, 100)
    if resp_choice <= 50:
        print(" | choice: deez nuts", end="")
        
        # nutsify
        last_word = get_last_word(message)
        if last_word == "":
            return
        if len(last_word) >= 2:
            if last_word[-2:] == "ma":
                nutsified_message = last_word + " nuts."
            else:
                nutsified_message = last_word + " these nuts."
        else:
            nutsified_message = last_word + " these nuts."
        await msg_channel.send(nutsified_message)

        # boom roasted
        roast_chance = random.randint(1, 10)
        if roast_chance == 1:
            time.sleep(0.5)
            await msg_channel.send("boom roasted")
        
        # no kyap
        kyap_chance = random.randint(1, 10)
        if kyap_chance == 1:
            time.sleep(0.5)
            await msg_channel.send("no kyap")
    elif resp_choice <= 75:
        print(" | choice: you're my (blank)", end="")
        last_word = get_last_word(message)
        youre_my_message = message.author.mention + ", _you're_ my " + last_word
        await msg_channel.send(youre_my_message)
    else:
        print(" | choice: poggers", end="")
        await msg_channel.send("poggers")
    
    print()
    
@bot.listen("on_message")
async def mention_response(message: Message):
    '''Responds when mentioned

    Args:
        message (Message): [description]
    '''
    if bot.user.mentioned_in(message):
        log("mention response", server=message.guild.name, channel=message.channel.name, newline=False)
        
        rand_resp = random.choice(mention_resposes)
        print(f" | response: \"{rand_resp}\"")
        
        msg_channel = message.channel
        await msg_channel.send(rand_resp)
               
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
    print('logged in as {0.user}'.format(bot))
    timekeeper.start()
    
    game = discord.Game("these nuts.")
    await bot.change_presence(activity=game)

bot.run(api_key)
