'''Bot that mimics Andrew Liang's time-keeping
'''

import datetime
import json
import random
import time

from discord import errors
# import discord as dsc
from discord.ext import commands, tasks
from discord.message import Message

import typo_gen

bot = commands.Bot(command_prefix='$')

# JSON parsing
def json_write():
    json_file_w = open('bot_settings.json', 'w', encoding='utf8')
    json.dump({"bot_internals": bot_internals, 
               "bot_timekeeping": bot_timekeeping}, 
              json_file_w)
    print("rewrote json")

settings_file = open('bot_settings.json', encoding='utf8')
data = json.load(settings_file)

authkey_file = open('authkey.json', encoding='utf8')
authkey = json.load(authkey_file)

# global variables
bot_internals = data['bot_internals']
bot_timekeeping = data['bot_timekeeping']

andrew_intro = bot_timekeeping['intro']
andrew_outro = bot_timekeeping['outro']
day_of_week_list = bot_timekeeping['day_of_week_list']

api_key = authkey['api_key']

first_launch = True

@bot.event
async def on_ready():
    print('logged in as {0.user}'.format(bot))
    timekeeper.start()
    # deez_nuts.start()
    # random_message.start()

@bot.command(name='echo')
async def _echo(ctx, *args):
    print('command: echo | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    await ctx.send('here\'s what you told me: {}'.format(' '.join(args)))

@bot.command(name='ping')
async def _ping(ctx):
    print('command: ping | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    await ctx.send('pong')
    
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
    
    last_word = message.content.split(" ")[-1]
    last_letter_index = len(last_word)
    for i in range(len(last_word)):
        if last_word[i] != "." and last_word[i] != "?" and last_word[i] != "!" and last_word[i] != "\"":
            last_letter_index = i

    last_word = last_word[:last_letter_index + 1]
    return last_word

# def can_respond(message: Message, max_delta=6.5):
#     timestamp = message.created_at
#     now = datetime.datetime.utcnow()
#     delta = now - timestamp
#     if delta < datetime.timedelta(seconds = max_delta):
#         if not message.author.bot:
#             return True
#     return False

@bot.command(name='whattime')
async def _whattime(ctx):
    current_time = datetime.datetime.now()
    print('command: whattime | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name + " | time: " + current_time.strftime('%c'))

    # message strings
    intro = random.choice(bot_timekeeping['intro'])
    outro = random.choice(bot_timekeeping['outro'])
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
@bot.command(name='bind')
async def _bind(ctx):
    print('command: bind | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    
    print(bot_internals['bound_channel'])
    bot_internals['bound_channel'] = ctx.channel.id
    print(bot_internals['bound_channel'])
    
    bound_channel = bot.get_channel(bot_internals['bound_channel'])
    if bound_channel is None:
        await ctx.send("bind failure, ask @agent30632 to fix his bot")
    else:
        await ctx.send('bound to channel' + ' ' + bound_channel.name)
    json_write()
  
@tasks.loop(hours=3.0)
async def timekeeper():
    current_time = datetime.datetime.now()
    print('task: timekeeper | time: ' + current_time.strftime('%c'))
    bound_channel = bot.get_channel(bot_internals["bound_channel"])

    if bound_channel is None:
        print("you better start binding")
        return
    
    global first_launch
    if first_launch:
        first_launch = False
        return
    
    current_time = datetime.datetime.now()
    
    intro = random.choice(bot_timekeeping["intro"])
    time_string = get_time_string()
    outro = random.choice(bot_timekeeping["outro"])
    
    # intro text
    await bound_channel.send(intro)
    time.sleep(1)
    # what time + typo
    is_typo = random.randint(1, 50)
    print("typo choice: " + str(is_typo))
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

@bot.listen("on_message")
async def random_response(message: Message):
    print("task: random response", end="")
    
    msg_channel = message.channel
    
    # random chance to respond
    resp_rand = random.randint(1, 50)
    print(" | odds = " + str(resp_rand), end="")
    
    # failed roll and/or message is by bot
    if resp_rand != 1 or message.author.bot:
        print()
        return
    
    # choosing an adequate response
    resp_choice = random.randint(1, 100)
    if resp_choice <= 50:
        print(" | choice: deez nuts", end="")
        
        # nutsify
        last_word = get_last_word(message)
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

bot.run(api_key)
