'''A python module for basic typo generation
'''

import random

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