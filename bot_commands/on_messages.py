'''Commands that run when messages are sent by users in a server'''

import json
import random

import discord

from . import helpers

settings_file = open('bot_settings.json', encoding='utf8')
settings = json.load(settings_file)
bot_data = settings["bot_data"]
mention_responses = bot_data["mention_responses"]

async def random_response(message: discord.message.Message):
    '''Random response to a message

    Args:
        message (Message): the message to respond to
    '''
    msg_channel = message.channel
    
    resp_rand = random.randint(1, 50)
    print(" | odds = " + str(resp_rand), end="")
    
    # failed roll and/or message is by bot
    if resp_rand != 1:
        print()
        return
    
    # choosing an adequate response
    resp_choice = random.randint(1, 100)
    if resp_choice <= 50:
        print(" | choice: deez nuts")
        
        # nutsify
        last_word = helpers.get_last_word(message)
        nut_message = helpers.these_nuts(last_word)
        await msg_channel.send(nut_message)
    elif resp_choice <= 75:
        print(" | choice: you're my (blank)")
        last_word = helpers.get_last_word(message)
        youre_my_message = message.author.mention + ", _you're_ my " + last_word
        await msg_channel.send(youre_my_message)
    else:
        print(" | choice: poggers")
        await msg_channel.send("poggers")
    
async def mention_response(message: discord.message.Message):
    '''Responds when mentioned

    Args:
        message (Message): [description]
    ''' 
    rand_resp = random.choice(mention_responses)
    print(f" | response: \"{rand_resp}\"")
    
    msg_channel = message.channel
    await msg_channel.send(rand_resp)
    