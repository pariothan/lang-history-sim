"""
Core vocabulary and semantic concepts for language generation
"""

import random

# Swadesh-inspired basic vocabulary
CORE_VOCABULARY = [
    # Pronouns
    "I",
    "you",
    "he",
    "she",
    "we",
    "they",
    "this",
    "that",

    # Question words
    "who",
    "what",
    "where",
    "when",
    "how",
    "why",

    # Numbers
    "one",
    "two",
    "three",
    "four",
    "five",
    "many",
    "all",
    "some",
    "few",

    # Body parts
    "head",
    "eye",
    "ear",
    "nose",
    "mouth",
    "tooth",
    "tongue",
    "hand",
    "foot",
    "leg",
    "arm",
    "back",
    "belly",
    "neck",
    "heart",
    "blood",

    # Family
    "mother",
    "father",
    "child",
    "man",
    "woman",
    "husband",
    "wife",

    # Animals
    "dog",
    "cat",
    "bird",
    "fish",
    "snake",
    "horse",
    "cow",
    "pig",

    # Nature
    "tree",
    "leaf",
    "root",
    "bark",
    "flower",
    "grass",
    "water",
    "fire",
    "earth",
    "stone",
    "sand",
    "sun",
    "moon",
    "star",
    "sky",
    "cloud",
    "rain",
    "snow",
    "wind",
    "mountain",
    "river",
    "sea",
    "lake",

    # Actions
    "eat",
    "drink",
    "sleep",
    "walk",
    "run",
    "sit",
    "stand",
    "come",
    "go",
    "see",
    "hear",
    "know",
    "think",
    "say",
    "give",
    "take",
    "make",
    "kill",
    "die",
    "live",
    "love",
    "fear",
    "laugh",
    "cry",
    "sing",
    "dance",

    # Qualities
    "big",
    "small",
    "long",
    "short",
    "wide",
    "narrow",
    "thick",
    "thin",
    "heavy",
    "light",
    "hot",
    "cold",
    "warm",
    "cool",
    "wet",
    "dry",
    "good",
    "bad",
    "new",
    "old",
    "young",
    "right",
    "wrong",
    "clean",
    "dirty",

    # Colors
    "red",
    "green",
    "blue",
    "yellow",
    "black",
    "white",

    # Time
    "day",
    "night",
    "morning",
    "evening",
    "year",
    "today",
    "tomorrow",
    "yesterday",

    # Basic concepts
    "name",
    "house",
    "road",
    "food",
    "meat",
    "bone",
    "egg",
    "fat",
    "salt",
    "knife",
    "rope",
    "skin",
    "feather",
    "hair",
    "horn",
    "tail",

    # Abstract
    "life",
    "death",
    "dream",
    "fear",
    "love",
    "anger",
    "peace",
    "war",
    "truth",
    "lie",
    "hope",
    "pain",
    "joy",
    "work",
    "play",
    "hunt",
]


def get_random_meaning() -> str:
    """Get a random meaning from the core vocabulary"""
    return random.choice(CORE_VOCABULARY)


def get_vocabulary_subset(size: int = 100) -> list[str]:
    """Get a random subset of the vocabulary"""
    import random
    return random.sample(CORE_VOCABULARY, min(size, len(CORE_VOCABULARY)))
