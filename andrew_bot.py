'''Bot that mimics Andrew Liang's time-keeping
'''

import datetime
import time
import json
import random

# import discord as dsc
from discord.ext import tasks, commands

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
authkey = json.load(settings_file)

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

@bot.command(name='echo')
async def _echo(ctx, *args):
    print('command: echo | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    await ctx.send('here\'s what you told me: {}'.format(' '.join(args)))

@bot.command(name='ping')
async def _ping(ctx):
    print('command: ping | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name)
    await ctx.send('pong')

@bot.command(name='whattime')
async def _whattime(ctx):
    current_time = datetime.datetime.now()
    print('command: whattime | server: ' + ctx.guild.name + " | channel: " + ctx.channel.name + " | time: " + current_time.strftime('%c'))
    
    hour = current_time.hour
    day_of_week = day_of_week_list[current_time.weekday()]
    time_of_day = ''
    if hour >= 3 and hour < 12:
        time_of_day = ' morning'
    elif hour >= 12 and hour < 13:
        time_of_day = ' lunchtime'
    elif hour >= 13 and hour < 17:
        time_of_day = ' afternoon'
    elif hour >= 17 and hour < 19:
        time_of_day = ' evening'
    elif hour >= 19 and hour < 20:
        time_of_day = ' evening, brb dinner 1 min'
    elif hour >= 20 and hour < 24:
        time_of_day = ' night'
    else:
        time_of_day = ' already'

    intro = random.choice(bot_timekeeping['intro'])
    outro = random.choice(bot_timekeeping['outro'])

    await ctx.send(intro)
    time.sleep(1)
    await ctx.send('it\'s ' + day_of_week + time_of_day)
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

async def timegiver(hour):
    print('command: timegiver')
    bound_channel = bot.get_channel(bot_internals['bound_channel'])
    
    if bound_channel is None:
        print("you better start binding")
        return
    
    intro = random.choice(bot_timekeeping['intro'])
    current_time = datetime.datetime.now()
    day_of_week = day_of_week_list[current_time.weekday()]
    outro = random.choice(bot_timekeeping['outro'])
    time_of_day = ''
    if hour == 8:
        time_of_day = 'morning'
    elif hour == 14:
        time_of_day = 'afternoon'
    elif hour == 17:
        time_of_day = 'evening'
    elif hour == 22:
        time_of_day = 'night'
        
    if time_of_day == '':
        return
    
    await bound_channel.send(intro)
    time.sleep(1)
    await bound_channel.send('it\'s ' + day_of_week + ' ' + time_of_day)
    time.sleep(1)
    await bound_channel.send(outro)
    
@tasks.loop(hours=1.0)
async def timekeeper():
    current_time = datetime.datetime.now()
    print('command: timekeeper | time: ' + current_time.strftime('%c'))
    global first_launch
    if first_launch:
        first_launch = False
    else:
        await timegiver(current_time.hour)

bot.run(api_key)