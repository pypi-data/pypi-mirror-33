import random
from .dictionaries import LEFT, CENTER, RIGHT

def generateNameArr(count = 1,
                    repeatParts = False,
                    uniqueList = True,
                    separator = '-',
                    lists = (LEFT, CENTER, RIGHT)
                    ):
    names = []
    for i in range(count):
        name = None
        while not name or (name in names and not uniqueList):
            name = generateName(repeatParts, separator, lists)
        names.append(name)
    return names

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
