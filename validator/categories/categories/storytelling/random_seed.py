import random

moods = [
    "Enigmatic",
    "Whimsical",
    "Tense",
    "Serene",
    "Melancholic",
    "Mysterious",
    "Playful",
    "Hopeful",
    "Eerie",
    "Exciting"
]

setting = [
    "Ancient Forest",
    "Cyberpunk City",
    "Deserted Island",
    "Victorian Mansion",
    "Space Station",
    "Medieval Village",
    "Underwater Cave",
    "Dystopian Society",
    "Futuristic Mars Colony",
    "Tropical Paradise"
]

protagonist = [
    "Brilliant Scientist",
    "Orphaned Teenager",
    "Cynical Detective",
    "Adventurous Archaeologist",
    "Aspiring Musician",
    "Elderly Storyteller",
    "Reluctant Hero",
    "Reclusive Artist",
    "Time Traveler",
    "Amnesiac Wanderer"
]

conflict = [
    "Man vs. Nature",
    "Betrayal by a Friend",
    "Moral Dilemma",
    "Quest for Revenge",
    "Struggle for Survival",
    "Overcoming Fear",
    "Social Injustice",
    "Battle for Power",
    "Internal vs. External Conflict",
    "Unraveling a Mystery"
]

resolution = [
    "Rediscovering Trust",
    "Sacrifice for the Greater Good",
    "Finding Inner Peace",
    "Redemption through Selflessness",
    "Unveiling Hidden Truths",
    "Embracing Change",
    "Forgiving the Unforgivable",
    "Building Unexpected Alliances",
    "Reuniting Long Lost Family",
    "Transforming a Community"
]

communication_style = [
    "Witty Banter",
    "Poetic Dialogue",
    "Nonverbal Communication",
    "Miscommunication",
    "Monologues",
    "Socratic Questioning",
    "Cryptic Clues",
    "Telepathic Connection",
    "Letters and Correspondence",
    "Cultural Language Barriers"
]

def get_random_story_seeds(number_of_seeded_words=1):
    mood_ = random.sample(moods, number_of_seeded_words)
    setting_ = random.sample(setting, number_of_seeded_words)
    protagonist_ = random.sample(protagonist, number_of_seeded_words)
    conflict_ = random.sample(conflict, number_of_seeded_words)
    resolution_ = random.sample(resolution, number_of_seeded_words)
    communication_style_ = random.sample(communication_style, number_of_seeded_words)

    random_seed = []
    if mood_:
        random_seed.append(f"Mood: {', '.join(mood_)}")
    if setting_:
        random_seed.append(f"Setting: {', '.join(setting_)}")
    if protagonist_:
        random_seed.append(f"Protagonist: {', '.join(protagonist_)}")
    if conflict_:
        random_seed.append(f"Conflict: {', '.join(conflict_)}")
    if resolution_:
        random_seed.append(f"Resolution: {', '.join(resolution_)}")
    if communication_style_:
        random_seed.append(f"Communication Style: {', '.join(communication_style_)}")

    return "\n".join(random_seed)