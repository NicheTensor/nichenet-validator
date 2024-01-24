from random import randint

def get_random_seeds():

    seed_count = [1, 2]
    number_of_seeded_words = seed_count[randint(0,1)]

    filename = "categories/categories/general_chat/unique_generalchat_keywords.txt"
    unique_keywords = []
    with open(filename) as f:
        for line in f:
            unique_keywords.append(line.strip())

    random_words = []
    for _ in range(number_of_seeded_words):
        random_words.append(unique_keywords[randint(0,len(unique_keywords)-1)])
    return str(random_words)

print(get_random_seeds())