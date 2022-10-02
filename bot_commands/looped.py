'''Commands that run on a loop'''

import json
import random

from . import helpers

settings_file = open('bot_settings.json', encoding='utf8')
settings = json.load(settings_file)
bot_internals = settings["bot_internals"]
bot_data = settings["bot_data"]

injury_data = bot_data["injuries"]
injury_verbs = injury_data["injury_verbs"]
injury_bodyparts = injury_data["injury_bodyparts"]
injury_final = injury_data["injury_final"]

async def timekeeper():
    '''Time keeping
    '''
    # current_time = datetime.datetime.now()
    # print('task: timekeeper | time: ' + current_time.strftime('%c'))
    
    # current_time = datetime.datetime.now()
    
    dow_intro_choice = random.choice(bot_data["dow_intro"])
    
    time_string = helpers.get_time_string()
    time_string_typo = None
    
    is_typo = random.randint(1, 50)
    print(" | typo choice: " + str(is_typo))
    if is_typo == 1:
        time_string_typo = helpers.make_typo(time_string)
    
    dow_outro_choice = random.choice(bot_data["dow_outro"])
    
    if time_string_typo is not None:
        return (True, dow_intro_choice, time_string, time_string_typo, dow_outro_choice)
    else: 
        return (False, dow_intro_choice, time_string, dow_outro_choice)
    
async def injuries():
    '''Injuries
    '''
    
    injury_verb_rand = random.choice(injury_verbs)
    injury_bodypart_rand = random.choice(injury_bodyparts)
    injury_final_rand = random.choice(injury_final)
    
    line_2 = f"i've {injury_verb_rand} my {injury_bodypart_rand}"
    
    return ("fellas", line_2, injury_final_rand)