from random import randint

def get_random_seeds():

    filename = "categories/categories/storytelling/unique_story_titles.txt"
    unique_keywords = []
    with open(filename) as f:
        for line in f:
            unique_keywords.append(line.strip())

    random_seed = unique_keywords[randint(0,len(unique_keywords)-1)]
    
    word_count = ["100 to 200 words", "200 to 300 words"]

    if randint(0,4) == 0:
        words_length = word_count[1]
    else:
        words_length = word_count[0]

    return random_seed, words_length