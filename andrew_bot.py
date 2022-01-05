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
    random_message.start()

@bot.command(name='echo')
async def _echo(ctx, *args):
    print('command: echo | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    await ctx.send('here\'s what you told me: {}'.format(' '.join(args)))

@bot.command(name='ping')
async def _ping(ctx):
    print('command: ping | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    await ctx.send('pong')
    
def get_time_string() -> str:
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
    last_word = message.content.split(" ")[-1]
    last_letter_index = len(last_word)
    for i in range(len(last_word)):
        if last_word[i] == "." or last_word[i] == "?" or last_word[i] == "!":
            last_letter_index = i

    last_word = last_word[:last_letter_index]
    return last_word

def can_respond(message: Message, max_delta=6.5):
    timestamp = message.created_at
    now = datetime.datetime.utcnow()
    delta = now - timestamp
    if delta < datetime.timedelta(seconds = max_delta):
        if not message.author.bot:
            return True
    return False

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
        
# @tasks.loop(seconds=3.0)
# async def deez_nuts():
#     bound_channel = bot.get_channel(bot_internals["bound_channel"])
#     # print(bound_channel)
#     print("task: deez nuts", end="")
#     if bound_channel == None:
#         print(" | failed: no bound channel")
#         return
#     else:
#         # 1/20 chance per second for each message within the past 5 seconds
#         random_odds = random.randint(1, 100)
#         if random_odds != 1:
#             print(" | odds = " + str(random_odds))
#             return
#         else:
#             print(" | odds successful", end="")
#             last_message = None
#             try:
#                 last_message = await bound_channel.fetch_message(bound_channel.last_message_id)
#             except errors.NotFound:
#                 last_message = None
            
#             if last_message != None:
#                 if len(last_message.content) > 40:
#                     print(" | last message: \"" + last_message.content[:41] + "...\"", end="")
#                 else:
#                     print(" | last message: \"" + last_message.content + "\"", end="")
#                 if last_message != None and not last_message.author.bot:
#                     timestamp = last_message.created_at
#                     now = datetime.datetime.utcnow()
#                     delta = now - timestamp
#                     print(" | time delta = " + str(delta))
#                     if delta < datetime.timedelta(seconds=6.5):
#                         # in case the message ends in a bunch of punctuation
#                         last_word = last_message.content.split(" ")[-1]
#                         last_letter_index = len(last_word)
#                         for i in range(len(last_word)):
#                             if last_word[i] == "." or last_word[i] == "?" or last_word[i] == "!":
#                                 last_letter_index = i

#                         last_word = last_word[:last_letter_index]
#                         nutsified_message = last_word + " these nuts."
#                         await bound_channel.send(nutsified_message)
#                 else:
#                     print()
#             else:
#                 print()
                
@tasks.loop(seconds=3.0)
async def random_message():
    bound_channel = bot.get_channel(bot_internals["bound_channel"])
    print("task: random response", end="")
    
    if bound_channel == None:
        print(" | failed: no bound channel")
        return
    else:
        # random chance to respond
        random_chance = random.randint(1, 100)
        if random_chance > 1:
            print(" | odds = " + str(random_chance))
            return
        else:
            print(" | odds success", end="")
            response_choice = random.randint(1, 100)
            
            # getting the last message
            last_message = None
            try:
                last_message = await bound_channel.fetch_message(bound_channel.last_message_id)
            except errors.NotFound:
                last_message = None
            
            if last_message is not None:
                if len(last_message.content) > 40:
                    print(" | last message: \"" + last_message.content[:41] + "...\"", end="")
                else:
                    print(" | last message: \"" + last_message.content + "\"", end="")
            
            # choosing a response
            if response_choice <= 50:
                print(" | choice: deez nuts", end="")
                # if no error for last message
                if last_message is not None:
                    # if not last_message.author.bot:
                        # timestamp = last_message.created_at
                        # now = datetime.datetime.utcnow()
                        # delta = now - timestamp
                        # print(" | time delta = " + str(delta))
                        # if delta < datetime.timedelta(seconds=6.5):
                            # in case the message ends in a bunch of punctuation
                    if can_respond(last_message):
                        print(" | can respond")
                        
                        # nuts
                        last_word = get_last_word(last_message)
                        nutsified_message = last_word + " these nuts."
                        await bound_channel.send(nutsified_message)
                        
                        # boom roasted
                        roast_chance = random.randint(1, 10)
                        if roast_chance == 1:
                            time.sleep(0.5)
                            await bound_channel.send("boom roasted")
                        
                        # no kyap
                        kyap_chance = random.randint(1, 10)
                        if kyap_chance == 1:
                            time.sleep(0.5)
                            await bound_channel.send("no kyap")
                        
                    else:
                        print(" | cannot respond!")
            elif response_choice > 50 and response_choice <= 75:
                print(" | choice: you're my (blank)", end="")
                if last_message is not None:
                    # if not last_message.author.bot:
                    #     timestamp = last_message.created_at
                    #     now = datetime.datetime.utcnow()
                    #     delta = now - timestamp
                    #     print(" | time delta = " + str(delta))
                    #     if delta < datetime.timedelta(seconds=6.5):
                    # in case the message ends in a bunch of punctuation
                    if can_respond(last_message):
                        print(" | can respond")
                        
                        last_word = get_last_word(last_message)
                        youre_my_message = last_message.author.mention + ", _you're_ my " + last_word
                        await bound_channel.send(youre_my_message)
                    else:
                        print(" | cannot respond!")
                else:
                    print(" | no last message!")
            else:
                print(" | choice: poggers")
                if last_message is not None:
                    if can_respond(last_message):
                        await bound_channel.send("poggers")
    
bot.run(api_key)
