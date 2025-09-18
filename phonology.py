"""
Phonological system with distinctive features and sound inventories
"""

import math
import random
from functools import lru_cache
from typing import Dict, List, Tuple

# Distinctive features for phonological representation
FEATURES = [
    "syllabic",     # + vowel, - consonant
    "consonantal",  # + consonant, - vowel/glide
    "sonorant",     # + vowels, nasals, liquids, glides; - obstruents
    "continuant",   # + fricatives/liquids/glides, - stops/nasals
    "nasal",        # + m n ŋ, - otherwise
    "lateral",      # + l
    "voice",        # + voiced
    "labial",       # + p b f v m w, rounded vowels
    "coronal",      # + t d s z ʃ ʒ n l r
    "dorsal",       # + k g j w vowels
    "high",         # + i u, - a
    "low",          # + a
    "back",         # + u o, - i e
    "round",        # + u o w; - i e
]

def fv(**kw: int) -> List[int]:
    """Create feature vector with specified values"""
    vec = {k: 0 for k in FEATURES}
    vec.update(kw)
    return [vec[f] for f in FEATURES]

# Phoneme inventory with distinctive features
PHONEMES: Dict[str, List[int]] = {
    # Vowels
    "i":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=+1, low=-1, back=-1, round=-1),
    "e":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=0,  low=0,  back=-1, round=-1),
    "a":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=-1, low=+1, back=0,  round=-1),
    "o":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=0,  low=0,  back=+1, round=+1),
    "u":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=+1, low=-1, back=+1, round=+1),
    "ə":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=0,  low=0,  back=0,  round=-1),

    # Stops
    "p":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=+1, coronal=-1, dorsal=-1),
    "b":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1),
    "t":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1),
    "d":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),
    "k":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=-1, dorsal=+1),
    "g":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1),

    # Fricatives
    "f":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=+1, coronal=-1, dorsal=-1),
    "v":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1),
    "s":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1),
    "z":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),
    "ʃ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1),
    "ʒ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),
    "x":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=-1, dorsal=+1),
    "h":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=0,  coronal=0,  dorsal=0),

    # Nasals
    "m":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1),
    "n":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),
    "ŋ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1),

    # Liquids
    "l":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, lateral=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),
    "r":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1),

    # Glides
    "j":  fv(syllabic=-1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=+1, back=-1, round=-1),
    "w":  fv(syllabic=-1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=+1, back=+1, round=+1),
}

INVENTORY = sorted(PHONEMES.keys())
IDX = {p: i for i, p in enumerate(INVENTORY)}
SYLLABIC_IDX = FEATURES.index("syllabic")

# Color projection for visualization
RGB_PROJ = (
    [ 0.8, -0.4,  0.2,  0.3,  0.1,  0.2,  0.3,  0.6, -0.2,  0.1,  0.9, -0.3, -0.5, -0.6],  # R
    [-0.4,  0.8,  0.1,  0.5,  0.2, -0.2,  0.3,  0.1,  0.6,  0.2, -0.5,  0.7,  0.4, -0.2],  # G
    [ 0.1,  0.2,  0.8, -0.4, -0.2,  0.5, -0.3, -0.2,  0.2,  0.7,  0.3,  0.1, -0.1,  0.9],  # B
)

def feature_distance(a: List[int], b: List[int]) -> int:
    """Calculate feature distance between two phonemes"""
    d = 0
    for x, y in zip(a, b):
        if x == 0 and y == 0:
            continue
        if x == 0 or y == 0:
            d += 2
        elif x != y:
            d += 1
    return d

def is_syllabic(phon: str) -> bool:
    """Check if phoneme is syllabic (vowel)"""
    return PHONEMES[phon][SYLLABIC_IDX] > 0

def syllable_count(word: List[str]) -> int:
    """Count syllables in a word"""
    return sum(1 for p in word if is_syllabic(p))

def ensure_has_vowel(word: List[str]):
    """Ensure word has at least one vowel"""
    if syllable_count(word) == 0:
        vowels = [p for p in INVENTORY if is_syllabic(p)]
        word.insert(len(word)//2, random.choice(vowels))

# Precompute distance matrices and weights
VECS = [PHONEMES[p] for p in INVENTORY]
DIST = [[feature_distance(VECS[i], VECS[j]) for j in range(len(INVENTORY))] for i in range(len(INVENTORY))]

def compute_mutation_weights(alpha: float) -> List[List[float]]:
    """Compute mutation weights based on feature similarity"""
    weights = []
    for i in range(len(INVENTORY)):
        row = []
        for j in range(len(INVENTORY)):
            d = DIST[i][j]
            row.append(math.exp(-alpha * d))
        weights.append(row)
    return weights

def compute_addition_weights(sweet_dist: float, beta: float) -> List[List[float]]:
    """Compute addition weights with sweet spot preference"""
    weights = []
    for i in range(len(INVENTORY)):
        row = []
        for j in range(len(INVENTORY)):
            d = DIST[i][j]
            w = math.exp(-beta * (d - sweet_dist)**2)
            row.append(w)
        weights.append(row)
    return weights