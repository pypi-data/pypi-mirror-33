import random
from .dictionaries import LEFT, CENTER, RIGHT

def generateName(repeatParts = False,
                 separator = '-',
                 lists = (LEFT, CENTER, RIGHT)
                 ):
    name = []
    for word in lists:
        part = None
        while not part or (part in name and not repeatParts):
            part = random.choice(word)
        name.append(part)
    return separator.join(name)
