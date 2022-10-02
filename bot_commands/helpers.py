'''Helper functions for andrewBOT'''

import datetime
import json
import random
from calendar import monthrange

import discord

settings_file = open('bot_settings.json', encoding='utf8')
settings = json.load(settings_file)
bot_data = settings["bot_data"]
extra_nut_messages = bot_data["extra_nut_messages"]
dow_day_list = bot_data["dow_day_list"]

def make_typo(string: str, min_typos = 2) -> str:
    '''Creates typos in a string by randomly swapping letters. 
    Limits the number of typos to one-third of the length of the provided string.

    Args:
        string (str): The string to add typos to
        min_typos (int, optional): The minimum number of typos to add. Defaults to 3.

    Returns:
        str: The typo-ridden string
    '''
    max_typos = len(string) // 3
    if max_typos < min_typos:
        max_typos, min_typos = min_typos, max_typos
    target_typos = random.randint(min_typos, max_typos)
    print(target_typos)
    
    i = 0
    string_list = list(string)
    
    # loops left-aligned
    while i < target_typos // 2:
        index = random.randint(0, len(string_list) - 2)
        string_list[index], string_list[index + 1] = string_list[index + 1], string_list[index]
        i += 1
    # loops right-aligned
    while i < target_typos:
        index = random.randint(1, len(string) - 1)
        string_list[index], string_list[index - 1] = string_list[index - 1], string_list[index]
        i += 1
        
    string = "".join(string_list)
        
    return string

def find_next_saturday():
    '''Finds the next 9-o'clock on a Saturday'''
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
            
    # check if the next saturday is out of range for this month
    saturday_nineoclock = None
    try:
        saturday_nineoclock = datetime.datetime(current_time.year,
                                                current_time.month,
                                                current_time.day + days_until_saturday,
                                                hour=21,
                                                tzinfo=current_time.tzinfo)
    except ValueError:
        # out of range for this month; move to the next one!
        days_in_month = monthrange(current_time.year, current_time.month)[1]
        days_left_in_month = days_in_month - current_time.day
        next_month_days_till_saturday = days_until_saturday - days_left_in_month
        
        # in case the next month is january
        if current_time.month == 12:
            saturday_nineoclock = datetime.datetime(current_time.year + 1,
                                                1,
                                                next_month_days_till_saturday,
                                                hour=21,
                                                tzinfo=current_time.tzinfo)
        else:
            saturday_nineoclock = datetime.datetime(current_time.year,
                                                    current_time.month + 1,
                                                    next_month_days_till_saturday,
                                                    hour=21,
                                                    tzinfo=current_time.tzinfo)
    
    time_until_saturday_nineoclock = saturday_nineoclock - current_time
    
    return time_until_saturday_nineoclock

def get_time_string() -> str:
    '''Gets a string that represents the current date and time (as written by Andrew Liang)

    Returns:
        str: Andrew Liang compliant time string
    '''

    current_time = datetime.datetime.now()

    hour = current_time.hour
    day_of_week = dow_day_list[current_time.weekday()]

    time_of_day = ''
    if hour >= 0 and hour < 3:
        time_of_day = ' already'
    elif hour >= 3 and hour < 12:
        time_of_day = ' morning'
    elif hour >= 12 and hour < 17:
        time_of_day = ' afternoon'
    elif hour >= 17 and hour < 20:
        time_of_day = ' evening'
    elif hour >= 20 and hour < 24:
        time_of_day = ' night'
        
    return "it's " + day_of_week + time_of_day

def get_last_word(message: discord.message.Message) -> str:
    '''Gets the last word from a message, filtering for punctuation.

    Args:
        message (Message): Discord message to scan

    Returns:
        str: the last word in the Message
    '''

    message_content = message.content.strip()
    last_word = message_content.split(" ")[-1]
    last_letter_index = len(last_word)
    
    punc_list = [".", "?", "!", "\""]
    
    for i, char in enumerate(last_word):
        if char not in punc_list:
            last_letter_index = i

    last_word = last_word[:last_letter_index + 1]
    return last_word

def these_nuts(last_word):
    '''adds "these nuts" to the end of a message (in the context of the bot anyways)

    Args:
        last_word (string): last word of the message
    '''
    if last_word == "":
        return
    if len(last_word) >= 2:
        if last_word[-2:] == "ma":
            nutsified_message = last_word + " nuts."
        else:
            nutsified_message = last_word + " these nuts"
    else:
        nutsified_message = last_word + " these nuts"
        
    extra_nut_choice = random.randint(1, 5)
    if extra_nut_choice == 1:
        num_extra = random.randint(1, len(extra_nut_messages))
        random_list = random.sample(extra_nut_messages, num_extra)
        
        for word in random_list:
            nutsified_message += " " + word
    else:
        nutsified_message += "."
        
    return nutsified_message
