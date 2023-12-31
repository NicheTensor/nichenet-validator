import random
from random import randint

famous_people_names = [
    "Leonardo da Vinci",
    "William Shakespeare",
    "Albert Einstein",
    "Isaac Newton",
    "Galileo Galilei",
    "Nelson Mandela",
    "Winston Churchill",
]

common_words=[
    'time',
'year',
'people',
'way',
'day',
'man',
'government',
'work',
'life',
'part',
'world',
'case',
'point',
'company',
'problem',
'fact',
'hand',
'place',
'end',
'group',
'child',
'number',
'reason',
'woman',
'family',
'government',
'fact',
'money',
'study',
'result',
'night',
'name',
'morning',
'person',
'room',
'body',
'information',
'way',
'fact',
'friend',
'government',
'week',
'month',
'information',
'woman',
'job',
'work',
'problem',
'man',
'report',
'girl',
'law',
'school',
'idea',
'money',
'system',
'report',
'end',
'family',
'research',
'book',
'order',
'development',
'industry',
'market',
'health',
'plan',
'interest',
'sense',
'effect',
'charge',
'knowledge',
'purpose',
'night',
'law',
'process',
'analysis',
'job',
'success',
'problem',
'team',
'nature',
'society',
'level',
'control',
'member',
'society',
'future',
'form',
'knowledge',
'amount',
'moment',
'education',
'room',
'student',
'practice',
'research',
'sense',
'success',
'goal',
'building',
'action',
'process',
'idea',
'record',
'effort',
'market',
'approach',
'care',
'support',
'management',
'study',
'table',
'experience',
'process',
'event',
'condition',
'opportunity',
'father',
'organization',
'death',
'series',
'knowledge',
'situation',
'mind',
'support',
'teacher',
'report',
'research',
'theory',
'issue',
'girl',
'husband',
'friend',
'community',
'effect',
'quality',
'rule',
'difference',
'season',
'price',
'practice',
'review',
'health',
'relation',
'land',
'tax',
'partner',
'couple',
'equipment',
'perspective',
'friend',
'range',
'model',
'media',
'manager',
'officer',
'figure',
'dog',
'film',
'program',
'response',
'article',
'glass',
'player',
'issue',
'plant',
'energy',
'trade',
'rock',
'effort',
'education',
'fire',
'address',
'situation',
'price',
'child',
'glass',
'action',
'policy',
'death',
'document',
'evidence',
'media',
'century',
'writer',
'speech',
'author',
'world',
'bed',
'analysis',
'hospital',
'industry',
'approach',
'film',
'development',
'evidence',
'war',
'analysis',
'resource',
]

def get_random_seeds(number_of_seeded_words = 1):
    random_seed = []
    for i in range(number_of_seeded_words):
        if random.random() > 0.8:
            random_seed = random_seed + get_random_full_name()
        else:
            random_seed = random_seed + get_random_words()
    random_seed = ", ".join(random_seed)
    return random_seed


def get_random_words(n=1):
    random_common_words = []
    # Generate a random word
    for i in range(n):
        # Choose a random index and get a word from the common words set
        word = list(common_words)[randint(0, len(common_words) - 1)]
        random_common_words.append(word)
    return random_common_words

def get_random_full_name(n=1):
    selected_names = random.sample(famous_people_names, n)
    return selected_names

