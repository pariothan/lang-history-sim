"""
Phonological system with distinctive features and sound inventories
"""

import math
import random
from functools import lru_cache
from typing import Dict, List, Tuple
from config import CONFIG

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
    "tense",        # + tense vowels, - lax vowels
    "distributed",  # + alveolar/dental, - palatal/retroflex
    "strident",     # + s z ʃ ʒ f v, - θ ð
    "anterior",     # + labial/dental/alveolar, - palatal/velar
]

def fv(**kw: int) -> List[int]:
    """Create feature vector with specified values"""
    vec = {k: 0 for k in FEATURES}
    vec.update(kw)
    return [vec[f] for f in FEATURES]

# Phoneme inventory with distinctive features
PHONEMES: Dict[str, List[int]] = {
    # Basic vowels
    "i":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=+1, low=-1, back=-1, round=-1, tense=+1),
    "ɪ":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=+1, low=-1, back=-1, round=-1, tense=-1),
    "e":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=0,  low=0,  back=-1, round=-1, tense=+1),
    "ɛ":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=-1, low=0,  back=-1, round=-1, tense=-1),
    "æ":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=-1, low=+1, back=-1, round=-1, tense=-1),
    "a":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=-1, low=+1, back=0,  round=-1, tense=+1),
    "ɑ":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=-1, low=+1, back=+1, round=-1, tense=+1),
    "ɔ":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=-1, low=0,  back=+1, round=+1, tense=-1),
    "o":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=0,  low=0,  back=+1, round=+1, tense=+1),
    "ʊ":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=+1, low=-1, back=+1, round=+1, tense=-1),
    "u":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=+1, low=-1, back=+1, round=+1, tense=+1),
    "ə":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=0,  low=0,  back=0,  round=-1, tense=-1),
    
    # Central vowels
    "ɨ":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=+1, low=-1, back=0,  round=-1, tense=+1),
    "ɯ":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=+1, low=-1, back=+1, round=-1, tense=+1),
    "ɤ":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=0,  low=0,  back=+1, round=-1, tense=+1),
    
    # Front rounded vowels
    "y":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=+1, low=-1, back=-1, round=+1, tense=+1),
    "ø":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=0,  low=0,  back=-1, round=+1, tense=+1),
    "œ":  fv(syllabic=+1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=-1, low=0,  back=-1, round=+1, tense=-1),

    # Bilabial stops
    "p":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=+1, coronal=-1, dorsal=-1, anterior=+1),
    "b":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1, anterior=+1),
    
    # Dental/alveolar stops
    "t":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1, distributed=+1, anterior=+1),
    "d":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, distributed=+1, anterior=+1),
    
    # Retroflex stops
    "ʈ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1, distributed=-1, anterior=-1),
    "ɖ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, distributed=-1, anterior=-1),
    
    # Palatal stops
    "c":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),
    "ɟ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),
    
    # Velar stops
    "k":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),
    "g":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),
    
    # Uvular stops
    "q":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),
    "ɢ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),
    
    # Glottal stop
    "ʔ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=0, coronal=0, dorsal=0, anterior=0),

    # Bilabial fricatives
    "ɸ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=+1, coronal=-1, dorsal=-1, strident=-1, anterior=+1),
    "β":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1, strident=-1, anterior=+1),
    
    # Labiodental fricatives
    "f":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=+1, coronal=-1, dorsal=-1, strident=+1, anterior=+1),
    "v":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1, strident=+1, anterior=+1),
    
    # Dental fricatives
    "θ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1, strident=-1, distributed=+1, anterior=+1),
    "ð":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, strident=-1, distributed=+1, anterior=+1),
    
    # Alveolar fricatives
    "s":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1, strident=+1, distributed=+1, anterior=+1),
    "z":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, strident=+1, distributed=+1, anterior=+1),
    
    # Postalveolar fricatives
    "ʃ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1, strident=+1, distributed=-1, anterior=-1),
    "ʒ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, strident=+1, distributed=-1, anterior=-1),
    
    # Retroflex fricatives
    "ʂ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1, strident=+1, distributed=-1, anterior=-1),
    "ʐ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, strident=+1, distributed=-1, anterior=-1),
    
    # Palatal fricatives
    "ç":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=-1, dorsal=+1, strident=-1, anterior=-1),
    "ʝ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, strident=-1, anterior=-1),
    
    # Velar fricatives
    "x":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=-1, dorsal=+1, strident=-1, anterior=-1),
    "ɣ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, strident=-1, anterior=-1),
    
    # Uvular fricatives
    "χ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=-1, coronal=-1, dorsal=+1, strident=-1, anterior=-1),
    "ʁ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, strident=-1, anterior=-1),
    
    # Pharyngeal fricatives
    "ħ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=0, coronal=0, dorsal=0, strident=-1, anterior=0),
    "ʕ":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=+1,
              labial=0, coronal=0, dorsal=0, strident=-1, anterior=0),
    
    # Glottal fricative
    "h":  fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=+1, voice=-1,
              labial=0, coronal=0, dorsal=0, strident=-1, anterior=0),
    
    # Affricates
    "ts": fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1, strident=+1, distributed=+1, anterior=+1),
    "dz": fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, strident=+1, distributed=+1, anterior=+1),
    "tʃ": fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=-1,
              labial=-1, coronal=+1, dorsal=-1, strident=+1, distributed=-1, anterior=-1),
    "dʒ": fv(syllabic=-1, consonantal=+1, sonorant=-1, continuant=-1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, strident=+1, distributed=-1, anterior=-1),

    # Nasals
    "m":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1, anterior=+1),
    "ɱ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=-1, anterior=+1),
    "n":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, distributed=+1, anterior=+1),
    "ɳ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, distributed=-1, anterior=-1),
    "ɲ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),
    "ŋ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),
    "ɴ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=-1, nasal=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),

    # Liquids
    "l":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, lateral=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, distributed=+1, anterior=+1),
    "ɭ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, lateral=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, distributed=-1, anterior=-1),
    "ʎ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, lateral=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),
    "ʟ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, lateral=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),
    "r":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, distributed=+1, anterior=+1),
    "ɾ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, distributed=+1, anterior=+1),
    "ɽ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=+1, dorsal=-1, distributed=-1, anterior=-1),
    "ʀ":  fv(syllabic=-1, consonantal=+1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, anterior=-1),

    # Glides
    "j":  fv(syllabic=-1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=+1, back=-1, round=-1, anterior=-1),
    "ɥ":  fv(syllabic=-1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=+1, back=-1, round=+1, anterior=-1),
    "ɰ":  fv(syllabic=-1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=-1, coronal=-1, dorsal=+1, high=+1, back=+1, round=-1, anterior=-1),
    "w":  fv(syllabic=-1, consonantal=-1, sonorant=+1, continuant=+1, voice=+1,
              labial=+1, coronal=-1, dorsal=+1, high=+1, back=+1, round=+1, anterior=-1),
}

INVENTORY = sorted(PHONEMES.keys())
IDX = {p: i for i, p in enumerate(INVENTORY)}
SYLLABIC_IDX = FEATURES.index("syllabic")

# Color projection for visualization
RGB_PROJ = (
    [ 0.8, -0.4,  0.2,  0.3,  0.1,  0.2,  0.3,  0.6, -0.2,  0.1,  0.9, -0.3, -0.5, -0.6,  0.4, -0.3,  0.5, -0.2],  # R
    [-0.4,  0.8,  0.1,  0.5,  0.2, -0.2,  0.3,  0.1,  0.6,  0.2, -0.5,  0.7,  0.4, -0.2, -0.3,  0.6, -0.1,  0.4],  # G
    [ 0.1,  0.2,  0.8, -0.4, -0.2,  0.5, -0.3, -0.2,  0.2,  0.7,  0.3,  0.1, -0.1,  0.9, -0.5,  0.2,  0.7, -0.4],  # B
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

# Phonological constraint classes
from dataclasses import dataclass, field
from typing import Set, Dict, List as TypingList, Tuple
from enum import Enum

class SyllableType(Enum):
    """Syllable structure types"""
    V = "V"           # Vowel only
    CV = "CV"         # Consonant-Vowel
    VC = "VC"         # Vowel-Consonant 
    CVC = "CVC"       # Consonant-Vowel-Consonant
    CCV = "CCV"       # Consonant-Consonant-Vowel
    CCVC = "CCVC"     # Consonant-Consonant-Vowel-Consonant
    VCC = "VCC"       # Vowel-Consonant-Consonant
    CVCC = "CVCC"     # Consonant-Vowel-Consonant-Consonant

@dataclass 
class ClusterConstraint:
    """Defines which phonemes can cluster together"""
    position: str  # "onset" or "coda"
    allowed_combinations: Set[Tuple[str, ...]]  # tuples of phonemes that can appear together
    
@dataclass
class PhonotacticConstraints:
    """Phonotactic constraint system for a language"""
    # Syllable structure preferences (probabilities sum to 1.0)
    syllable_types: Dict[SyllableType, float]
    
    # Consonant cluster constraints
    onset_clusters: ClusterConstraint
    coda_clusters: ClusterConstraint
    
    # Coda restrictions - which consonants can appear in coda position
    allowed_codas: Set[str]
    
    # Word length preferences (min, max, preferred)
    min_syllables: int = 1
    max_syllables: int = 4
    preferred_syllables: int = 2
    
    # Mora constraints (if using mora-based phonology)
    use_mora: bool = False
    min_mora: int = 1
    max_mora: int = 6
    
    # Gemination rules
    allow_gemination: bool = False
    gemination_probability: float = 0.05
    geminable_consonants: Set[str] = field(default_factory=set)
    
    # Phoneme sequence constraints
    forbidden_sequences: Set[Tuple[str, ...]] = field(default_factory=set)
    required_sequences: Dict[str, TypingList[str]] = field(default_factory=dict)  # context -> required following phonemes

def get_default_constraints() -> PhonotacticConstraints:
    """Get default phonotactic constraints (simple CV system)"""
    return PhonotacticConstraints(
        syllable_types={
            SyllableType.CV: 0.6,
            SyllableType.CVC: 0.3,
            SyllableType.V: 0.1
        },
        onset_clusters=ClusterConstraint("onset", set()),
        coda_clusters=ClusterConstraint("coda", set()),
        allowed_codas=set(["t", "n", "m", "s", "k", "p"]),
        min_syllables=1,
        max_syllables=3,
        preferred_syllables=2,
        forbidden_sequences=set(),
        required_sequences={}
    )

def get_complex_constraints() -> PhonotacticConstraints:
    """Get more complex phonotactic constraints with clusters"""
    return PhonotacticConstraints(
        syllable_types={
            SyllableType.CV: 0.4,
            SyllableType.CVC: 0.25, 
            SyllableType.CCV: 0.15,
            SyllableType.CCVC: 0.1,
            SyllableType.V: 0.05,
            SyllableType.VC: 0.05
        },
        onset_clusters=ClusterConstraint("onset", {
            ("p", "r"), ("t", "r"), ("k", "r"), ("b", "r"), ("d", "r"), ("g", "r"),
            ("p", "l"), ("t", "l"), ("k", "l"), ("b", "l"), ("d", "l"), ("g", "l"),
            ("f", "r"), ("f", "l"), ("s", "t"), ("s", "p"), ("s", "k"), ("s", "m"), ("s", "n"),
            ("ʃ", "t"), ("ʃ", "p"), ("ʃ", "k")
        }),
        coda_clusters=ClusterConstraint("coda", {
            ("n", "t"), ("m", "p"), ("ŋ", "k"), ("l", "t"), ("r", "t"), ("s", "t"),
            ("l", "s"), ("r", "s"), ("n", "s")
        }),
        allowed_codas=set(["t", "n", "m", "s", "k", "p", "l", "r", "ŋ"]),
        min_syllables=1,
        max_syllables=4,
        preferred_syllables=2,
        allow_gemination=True,
        gemination_probability=0.08,
        geminable_consonants=set(["t", "k", "p", "s", "n", "m", "l", "r"]),
        forbidden_sequences={("h", "h"), ("j", "j"), ("w", "w")},
        required_sequences={}
    )

def get_mora_constraints() -> PhonotacticConstraints:
    """Get mora-based phonotactic constraints (Japanese-style)"""
    return PhonotacticConstraints(
        syllable_types={
            SyllableType.CV: 0.7,
            SyllableType.V: 0.2,
            SyllableType.CVC: 0.1  # Only with moraic consonants
        },
        onset_clusters=ClusterConstraint("onset", set()),
        coda_clusters=ClusterConstraint("coda", set()),
        allowed_codas=set(["n", "m", "ŋ"]),  # Only moraic consonants
        min_syllables=1,
        max_syllables=5,
        preferred_syllables=3,
        use_mora=True,
        min_mora=2,
        max_mora=8,
        allow_gemination=True,
        gemination_probability=0.12,
        geminable_consonants=set(["t", "k", "p", "s"]),
        forbidden_sequences={("j", "j"), ("w", "w")},
        required_sequences={}
    )

def is_consonant(phon: str) -> bool:
    """Check if phoneme is a consonant"""
    return not is_syllabic(phon)

def is_voiced(phon: str) -> bool:
    """Check if phoneme is voiced"""
    if phon not in PHONEMES:
        return False
    voice_idx = FEATURES.index("voice")
    return PHONEMES[phon][voice_idx] > 0

def is_nasal(phon: str) -> bool:
    """Check if phoneme is nasal"""
    if phon not in PHONEMES:
        return False
    nasal_idx = FEATURES.index("nasal")
    return PHONEMES[phon][nasal_idx] > 0

def is_liquid(phon: str) -> bool:
    """Check if phoneme is a liquid (l, r)"""
    return phon in ["l", "r"]

def is_fricative(phon: str) -> bool:
    """Check if phoneme is a fricative"""
    if phon not in PHONEMES:
        return False
    continuant_idx = FEATURES.index("continuant")
    consonantal_idx = FEATURES.index("consonantal")
    sonorant_idx = FEATURES.index("sonorant")
    return (PHONEMES[phon][continuant_idx] > 0 and 
            PHONEMES[phon][consonantal_idx] > 0 and 
            PHONEMES[phon][sonorant_idx] <= 0)

def is_obstruent(phon: str) -> bool:
    """Check if phoneme is an obstruent (stop or fricative)"""
    if phon not in PHONEMES:
        return False
    consonantal_idx = FEATURES.index("consonantal")
    sonorant_idx = FEATURES.index("sonorant")
    return (PHONEMES[phon][consonantal_idx] > 0 and 
            PHONEMES[phon][sonorant_idx] <= 0)

def is_sonorant(phon: str) -> bool:
    """Check if phoneme is a sonorant"""
    if phon not in PHONEMES:
        return False
    sonorant_idx = FEATURES.index("sonorant")
    return PHONEMES[phon][sonorant_idx] > 0

class PhonologicalGenerator:
    """Generates words according to phonotactic constraints"""
    
    def __init__(self, phoneme_inventory: Set[str], constraints: PhonotacticConstraints):
        self.phoneme_inventory = phoneme_inventory
        self.constraints = constraints
        
        # Categorize phonemes
        self.vowels = [p for p in phoneme_inventory if is_syllabic(p)]
        self.consonants = [p for p in phoneme_inventory if not is_syllabic(p)]
        
        # Emergency fallbacks
        if not self.vowels:
            self.vowels = ["a"]
        if not self.consonants:
            self.consonants = ["t"]
    
    def generate_word(self) -> TypingList[str]:
        """Generate a word according to constraints"""
        if self.constraints.use_mora:
            return self._generate_mora_word()
        else:
            return self._generate_syllable_word()
    
    def _generate_syllable_word(self) -> TypingList[str]:
        """Generate word based on syllable structure"""
        # Choose number of syllables
        if random.random() < 0.6:
            num_syllables = self.constraints.preferred_syllables
        else:
            num_syllables = random.randint(self.constraints.min_syllables, 
                                         self.constraints.max_syllables)
        
        word = []
        for i in range(num_syllables):
            syllable = self._generate_syllable(i == 0, i == num_syllables - 1)
            word.extend(syllable)
            
            # Add gemination between syllables
            if (i < num_syllables - 1 and 
                self.constraints.allow_gemination and 
                random.random() < self.constraints.gemination_probability):
                self._add_gemination(word)
        
        return self._filter_forbidden_sequences(word)
    
    def _generate_mora_word(self) -> TypingList[str]:
        """Generate word based on mora count"""
        target_mora = random.randint(self.constraints.min_mora, self.constraints.max_mora)
        word = []
        current_mora = 0
        
        while current_mora < target_mora:
            remaining_mora = target_mora - current_mora
            
            # Choose syllable type that fits remaining mora
            if remaining_mora >= 2:
                # Can use CV (2 mora) or V (1 mora)
                if random.random() < 0.7:
                    syllable = self._generate_cv_syllable()
                    current_mora += 2
                else:
                    syllable = self._generate_v_syllable()
                    current_mora += 1
            else:
                # Only 1 mora left, must use V
                syllable = self._generate_v_syllable()
                current_mora += 1
            
            word.extend(syllable)
        
        return self._filter_forbidden_sequences(word)
    
    def _generate_syllable(self, is_first: bool, is_last: bool) -> TypingList[str]:
        """Generate a single syllable"""
        # Choose syllable type based on probabilities
        syllable_types = list(self.constraints.syllable_types.keys())
        probabilities = list(self.constraints.syllable_types.values())
        
        syll_type = random.choices(syllable_types, weights=probabilities, k=1)[0]
        
        if syll_type == SyllableType.V:
            return self._generate_v_syllable()
        elif syll_type == SyllableType.CV:
            return self._generate_cv_syllable()
        elif syll_type == SyllableType.VC:
            return self._generate_vc_syllable()
        elif syll_type == SyllableType.CVC:
            return self._generate_cvc_syllable()
        elif syll_type == SyllableType.CCV:
            return self._generate_ccv_syllable()
        elif syll_type == SyllableType.CCVC:
            return self._generate_ccvc_syllable()
        elif syll_type == SyllableType.VCC:
            return self._generate_vcc_syllable()
        elif syll_type == SyllableType.CVCC:
            return self._generate_cvcc_syllable()
        else:
            # Fallback to CV
            return self._generate_cv_syllable()
    
    def _generate_v_syllable(self) -> TypingList[str]:
        """Generate V syllable"""
        return [random.choice(self.vowels)]
    
    def _generate_cv_syllable(self) -> TypingList[str]:
        """Generate CV syllable"""
        onset = self._generate_onset(1)
        vowel = random.choice(self.vowels)
        return onset + [vowel]
    
    def _generate_vc_syllable(self) -> TypingList[str]:
        """Generate VC syllable"""
        vowel = random.choice(self.vowels)
        coda = self._generate_coda(1)
        return [vowel] + coda
    
    def _generate_cvc_syllable(self) -> TypingList[str]:
        """Generate CVC syllable"""
        onset = self._generate_onset(1)
        vowel = random.choice(self.vowels)
        coda = self._generate_coda(1)
        return onset + [vowel] + coda
    
    def _generate_ccv_syllable(self) -> TypingList[str]:
        """Generate CCV syllable"""
        onset = self._generate_onset(2)
        vowel = random.choice(self.vowels)
        return onset + [vowel]
    
    def _generate_ccvc_syllable(self) -> TypingList[str]:
        """Generate CCVC syllable"""
        onset = self._generate_onset(2)
        vowel = random.choice(self.vowels)
        coda = self._generate_coda(1)
        return onset + [vowel] + coda
    
    def _generate_vcc_syllable(self) -> TypingList[str]:
        """Generate VCC syllable"""
        vowel = random.choice(self.vowels)
        coda = self._generate_coda(2)
        return [vowel] + coda
    
    def _generate_cvcc_syllable(self) -> TypingList[str]:
        """Generate CVCC syllable"""
        onset = self._generate_onset(1)
        vowel = random.choice(self.vowels)
        coda = self._generate_coda(2)
        return onset + [vowel] + coda
    
    def _generate_onset(self, size: int) -> TypingList[str]:
        """Generate onset cluster"""
        if size == 1:
            return [random.choice(self.consonants)]
        elif size == 2:
            # Try to use allowed onset clusters
            available_clusters = [
                cluster for cluster in self.constraints.onset_clusters.allowed_combinations
                if len(cluster) == 2 and all(c in self.consonants for c in cluster)
            ]
            
            if available_clusters:
                cluster = random.choice(available_clusters)
                return list(cluster)
            else:
                # Fallback to single consonant
                return [random.choice(self.consonants)]
        else:
            # Fallback for larger clusters
            return [random.choice(self.consonants)]
    
    def _generate_coda(self, size: int) -> TypingList[str]:
        """Generate coda cluster"""
        if size == 1:
            # Use allowed codas if specified
            allowed = [c for c in self.consonants if c in self.constraints.allowed_codas]
            if allowed:
                return [random.choice(allowed)]
            else:
                return [random.choice(self.consonants)]
        elif size == 2:
            # Try to use allowed coda clusters
            available_clusters = [
                cluster for cluster in self.constraints.coda_clusters.allowed_combinations
                if len(cluster) == 2 and all(c in self.consonants for c in cluster)
            ]
            
            if available_clusters:
                cluster = random.choice(available_clusters)
                return list(cluster)
            else:
                # Fallback to single consonant
                allowed = [c for c in self.consonants if c in self.constraints.allowed_codas]
                if allowed:
                    return [random.choice(allowed)]
                else:
                    return [random.choice(self.consonants)]
        else:
            # Fallback
            return [random.choice(self.consonants)]
    
    def _add_gemination(self, word: TypingList[str]):
        """Add gemination at the end of current word"""
        if not word:
            return
        
        last_phone = word[-1]
        if (is_consonant(last_phone) and 
            last_phone in self.constraints.geminable_consonants):
            word.append(last_phone)
    
    def _filter_forbidden_sequences(self, word: TypingList[str]) -> TypingList[str]:
        """Remove forbidden phoneme sequences"""
        if not self.constraints.forbidden_sequences:
            return word
        
        # Check for forbidden sequences and try to repair
        filtered_word = word.copy()
        
        for forbidden in self.constraints.forbidden_sequences:
            seq_len = len(forbidden)
            i = 0
            while i <= len(filtered_word) - seq_len:
                if tuple(filtered_word[i:i+seq_len]) == forbidden:
                    # Replace middle phoneme with a safe alternative
                    if seq_len >= 2:
                        middle_idx = i + seq_len // 2
                        if is_syllabic(forbidden[seq_len // 2]):
                            filtered_word[middle_idx] = random.choice(self.vowels)
                        else:
                            filtered_word[middle_idx] = random.choice(self.consonants)
                    i += seq_len
                else:
                    i += 1
        
        return filtered_word


# Dynamic phonological rule system
import re
from typing import Optional, Callable, Union

@dataclass
class PhonologicalRule:
    """
    A phonological rule that can transform phoneme sequences
    Format: A → B / X _ Y (A becomes B in environment X_Y)
    """
    name: str
    source: str  # source phoneme or pattern
    target: str  # target phoneme or pattern  
    left_context: str = ""   # left environment (X in X_Y)
    right_context: str = ""  # right environment (Y in X_Y)
    
    # Rule metadata
    productivity: float = 1.0  # How actively the rule applies (0.0-1.0)
    strength: float = 1.0      # How strongly the rule applies when triggered
    start_tick: int = 0        # When the rule became active
    decay_rate: float = 0.0    # How quickly productivity decreases over time
    
    def __post_init__(self):
        """Compile token-based patterns for efficient matching"""
        # Compile source pattern
        self.source_predicate = self._compile_token_pattern(self.source)
        
        # Compile context patterns
        self.left_predicate = self._compile_context_pattern(self.left_context, is_left=True)
        self.right_predicate = self._compile_context_pattern(self.right_context, is_left=False)
        
        # Parse target for feature-based transformations
        self.target_type, self.target_data = self._parse_target(self.target)
    
    def _compile_token_pattern(self, pattern: str) -> Callable[[str], bool]:
        """Convert pattern to token predicate function"""
        if pattern in PHONEMES:
            # Literal phoneme
            return lambda p: p == pattern
        elif pattern == "V":
            # Any vowel
            return lambda p: is_syllabic(p)
        elif pattern == "C":
            # Any consonant
            return lambda p: not is_syllabic(p)
        elif pattern == "[obstruent]":
            # Any obstruent
            return lambda p: is_obstruent(p)
        elif pattern == "[sonorant]":
            # Any sonorant
            return lambda p: is_sonorant(p)
        elif pattern.startswith("[") and pattern.endswith("]"):
            # Feature class
            feature_conditions = self._parse_feature_class(pattern)
            return lambda p: self._matches_features(p, feature_conditions)
        else:
            # Fallback to literal
            return lambda p: p == pattern
    
    def _compile_context_pattern(self, context: str, is_left: bool) -> Optional[Callable[[TypingList[str], int], bool]]:
        """Convert context pattern to boundary checker"""
        if not context:
            return None
        elif context == "#":
            # Word boundary
            if is_left:
                return lambda word, pos: pos == 0
            else:
                return lambda word, pos: pos == len(word) - 1
        else:
            # Pattern context
            pattern_pred = self._compile_token_pattern(context)
            if is_left:
                return lambda word, pos: pos > 0 and pattern_pred(word[pos - 1])
            else:
                return lambda word, pos: pos < len(word) - 1 and pattern_pred(word[pos + 1])
    
    def _parse_feature_class(self, feature_class: str) -> TypingList[Tuple[str, int]]:
        """Parse feature class like [+voice,-nasal] into conditions"""
        content = feature_class[1:-1]  # Remove [ ]
        conditions = []
        
        # Split on commas for multiple features
        parts = [part.strip() for part in content.split(",")]
        
        for part in parts:
            if part.startswith("+"):
                feature = part[1:]
                value = 1
            elif part.startswith("-"):
                feature = part[1:]
                value = -1
            else:
                feature = part
                value = 1
            
            if feature in FEATURES:
                conditions.append((feature, value))
        
        return conditions
    
    def _matches_features(self, phoneme: str, conditions: TypingList[Tuple[str, int]]) -> bool:
        """Check if phoneme matches all feature conditions"""
        if phoneme not in PHONEMES:
            return False
        
        phoneme_features = PHONEMES[phoneme]
        
        for feature, value in conditions:
            feature_idx = FEATURES.index(feature)
            if phoneme_features[feature_idx] != value:
                return False
        
        return True
    
    def _parse_target(self, target: str) -> Tuple[str, Union[str, TypingList[Tuple[str, int]], None]]:
        """Parse target into type and data"""
        if target in ["∅", "Ø", ""]:
            return ("deletion", None)
        elif target in PHONEMES:
            return ("literal", target)
        elif target.startswith("[") and target.endswith("]"):
            # Feature modification like [+voice]
            feature_changes = self._parse_feature_class(target)
            return ("feature", feature_changes)
        else:
            # Fallback to literal
            return ("literal", target)
    
    def apply(self, word: TypingList[str], tick: int = 0) -> TypingList[str]:
        """Apply this rule to a word"""
        # Check if rule is active
        if not self.is_active(tick):
            return word
        
        result = []
        i = 0
        
        while i < len(word):
            # Check if current position matches source pattern
            if self.source_predicate(word[i]):
                # Check context conditions
                left_ok = self.left_predicate is None or self.left_predicate(word, i)
                right_ok = self.right_predicate is None or self.right_predicate(word, i)
                
                if left_ok and right_ok:
                    # Apply rule with probability
                    if random.random() < self.productivity * self.strength:
                        # Apply transformation
                        transformed = self._apply_transformation(word[i])
                        result.extend(transformed)
                        # Skip the source phoneme
                        i += 1
                        continue
            
            # No transformation applied, keep original
            result.append(word[i])
            i += 1
        
        return result
    
    def _apply_transformation(self, source_phoneme: str) -> TypingList[str]:
        """Apply the transformation to a source phoneme"""
        if self.target_type == "deletion":
            return []  # Delete the phoneme
        elif self.target_type == "literal":
            if isinstance(self.target_data, str):
                return [self.target_data]
            else:
                return [source_phoneme]  # Fallback
        elif self.target_type == "feature":
            # Apply feature changes and find nearest phoneme
            if source_phoneme not in PHONEMES:
                return [source_phoneme]  # Fallback
            
            if not isinstance(self.target_data, list):
                return [source_phoneme]  # Fallback
            
            source_features = PHONEMES[source_phoneme][:]
            
            # Apply feature changes
            for feature, value in self.target_data:
                if feature in FEATURES:
                    feature_idx = FEATURES.index(feature)
                    source_features[feature_idx] = value
            
            # Find closest phoneme with these features
            best_phoneme = source_phoneme
            min_distance = float('inf')
            
            for phoneme, phoneme_features in PHONEMES.items():
                distance = feature_distance(source_features, phoneme_features)
                if distance < min_distance:
                    min_distance = distance
                    best_phoneme = phoneme
            
            return [best_phoneme]
        else:
            # Fallback
            return [source_phoneme]
    
    def is_active(self, tick: int) -> bool:
        """Check if rule is active at given time"""
        if tick < self.start_tick:
            return False
        
        # Apply decay
        age = tick - self.start_tick
        current_productivity = self.productivity * (1.0 - self.decay_rate * age)
        return current_productivity > 0.01  # Minimum threshold
    
    def get_current_productivity(self, tick: int) -> float:
        """Get current productivity considering decay"""
        if tick < self.start_tick:
            return 0.0
        
        age = tick - self.start_tick
        current_productivity = self.productivity * (1.0 - self.decay_rate * age)
        return max(0.0, current_productivity)


@dataclass
class PhonologicalRuleSet:
    """Collection of phonological rules for a language"""
    rules: TypingList[PhonologicalRule] = field(default_factory=list)
    last_updated_tick: int = 0
    version: int = 1  # Incremented when rules change
    
    def add_rule(self, rule: PhonologicalRule, tick: int = 0):
        """Add a new rule to the set"""
        rule.start_tick = tick
        self.rules.append(rule)
        self.last_updated_tick = tick
        self.version += 1
    
    def remove_rule(self, rule_name: str, tick: int = 0) -> bool:
        """Remove a rule by name"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                self.last_updated_tick = tick
                self.version += 1
                return True
        return False
    
    def apply_rules(self, word: TypingList[str], tick: int = 0) -> TypingList[str]:
        """Apply all active rules to a word in order"""
        result = word.copy()
        
        # Apply rules in order
        for rule in self.rules:
            if rule.is_active(tick):
                result = rule.apply(result, tick)
        
        return result
    
    def get_active_rules(self, tick: int = 0) -> TypingList[PhonologicalRule]:
        """Get all currently active rules"""
        return [rule for rule in self.rules if rule.is_active(tick)]
    
    def evolve(self, tick: int, conservatism: float = 0.5, contact_pressure: float = 0.0):
        """Evolve the rule set over time"""
        # Add new rules occasionally
        if random.random() < (1.0 - conservatism) * CONFIG.P_RULE_GENERATION_BASE:
            new_rule = self._generate_random_rule(tick)
            if new_rule:
                self.add_rule(new_rule, tick)
        
        # Remove rules that have decayed too much
        self.rules = [rule for rule in self.rules if rule.get_current_productivity(tick) > CONFIG.RULE_PRODUCTIVITY_THRESHOLD]
        
        # Update version if rules changed
        if len(self.get_active_rules(tick)) != len(self.get_active_rules(tick - 1)):
            self.version += 1
    
    def _generate_random_rule(self, tick: int) -> Optional[PhonologicalRule]:
        """Generate a random phonological rule from common patterns"""
        rule_templates = [
            # Lenition rules
            {"name": "stop_lenition", "source": "p", "target": "f", "left_context": "V", "right_context": "V"},
            {"name": "stop_lenition", "source": "t", "target": "s", "left_context": "V", "right_context": "V"},
            {"name": "stop_lenition", "source": "k", "target": "x", "left_context": "V", "right_context": "V"},
            
            # Voicing assimilation (obstruents only)
            {"name": "voicing_assimilation", "source": "[-voice,+consonantal,-sonorant]", "target": "[+voice]", "right_context": "[+voice]"},
            
            # Final devoicing (obstruents only)
            {"name": "final_devoicing", "source": "[+voice,+consonantal,-sonorant]", "target": "[-voice]", "right_context": "#"},
            
            # Vowel reduction in unstressed positions
            {"name": "vowel_reduction", "source": "a", "target": "ə", "left_context": "C", "right_context": "C"},
            {"name": "vowel_reduction", "source": "o", "target": "ə", "left_context": "C", "right_context": "C"},
            
            # Palatalization before front vowels
            {"name": "palatalization", "source": "t", "target": "ʃ", "right_context": "i"},
            {"name": "palatalization", "source": "k", "target": "ʃ", "right_context": "i"},
            
            # Cluster simplification
            {"name": "cluster_simplification", "source": "t", "target": "∅", "left_context": "s", "right_context": "C"},
            
            # Vowel deletion in weak positions (simplified - single consonant context)
            {"name": "syncope", "source": "V", "target": "∅", "left_context": "C", "right_context": "C"},
            
            # Liquid deletion (not metathesis)
            {"name": "liquid_deletion", "source": "r", "target": "∅", "left_context": "V", "right_context": "C"},
        ]
        
        template = random.choice(rule_templates)
        
        return PhonologicalRule(
            name=f"{template['name']}_{tick}",
            source=template["source"],
            target=template["target"],
            left_context=template.get("left_context", ""),
            right_context=template.get("right_context", ""),
            productivity=random.uniform(0.3, 0.8),
            strength=random.uniform(0.5, 1.0),
            start_tick=tick,
            decay_rate=random.uniform(0.0001, 0.001)  # Very slow decay
        )


# Syllabification and phonotactic repair utilities
def syllabify_word(word: TypingList[str], constraints: PhonotacticConstraints) -> TypingList[TypingList[str]]:
    """Break word into syllables according to constraints"""
    if not word:
        return []
    
    syllables = []
    current_syllable = []
    
    i = 0
    while i < len(word):
        if is_syllabic(word[i]):
            # Found vowel - start new syllable or continue current one
            current_syllable.append(word[i])
            i += 1
            
            # Collect any following consonants
            consonants = []
            while i < len(word) and not is_syllabic(word[i]):
                consonants.append(word[i])
                i += 1
            
            if i >= len(word):
                # End of word - all consonants go to current syllable
                current_syllable.extend(consonants)
            else:
                # More vowels ahead - distribute consonants
                if len(consonants) == 0:
                    # No consonants to distribute
                    pass
                elif len(consonants) == 1:
                    # Single consonant - goes to next syllable as onset
                    syllables.append(current_syllable)
                    current_syllable = consonants
                else:
                    # Multiple consonants - split according to constraints
                    split_point = _find_syllable_boundary(consonants, constraints)
                    current_syllable.extend(consonants[:split_point])
                    syllables.append(current_syllable)
                    current_syllable = consonants[split_point:]
        else:
            # Consonant without preceding vowel
            current_syllable.append(word[i])
            i += 1
    
    if current_syllable:
        syllables.append(current_syllable)
    
    return syllables


def _find_syllable_boundary(consonants: TypingList[str], constraints: PhonotacticConstraints) -> int:
    """Find where to split consonant cluster between syllables"""
    if len(consonants) <= 1:
        return 0
    
    # Try different split points and pick the best one
    best_split = 1  # Default: first consonant goes to coda, rest to onset
    
    for split in range(1, len(consonants)):
        coda_part = consonants[:split]
        onset_part = consonants[split:]
        
        # Check if this split creates valid coda and onset
        coda_valid = _is_valid_coda(coda_part, constraints)
        onset_valid = _is_valid_onset(onset_part, constraints)
        
        if coda_valid and onset_valid:
            best_split = split
            break
    
    return best_split


def _is_valid_coda(coda: TypingList[str], constraints: PhonotacticConstraints) -> bool:
    """Check if consonant sequence can form a valid coda"""
    if len(coda) == 1:
        return coda[0] in constraints.allowed_codas
    elif len(coda) == 2:
        return tuple(coda) in constraints.coda_clusters.allowed_combinations
    else:
        return False


def _is_valid_onset(onset: TypingList[str], constraints: PhonotacticConstraints) -> bool:
    """Check if consonant sequence can form a valid onset"""
    if len(onset) == 1:
        return True  # Single consonants are generally allowed as onsets
    elif len(onset) == 2:
        return tuple(onset) in constraints.onset_clusters.allowed_combinations
    else:
        return False


def repair_phonotactics(word: TypingList[str], constraints: PhonotacticConstraints, 
                       epenthetic_vowel: str = "ə") -> TypingList[str]:
    """Repair phonotactic violations in a word"""
    if not word:
        return word
    
    # First, syllabify the word
    syllables = syllabify_word(word, constraints)
    
    # Repair each syllable
    repaired_syllables = []
    for syllable in syllables:
        repaired = _repair_syllable(syllable, constraints, epenthetic_vowel)
        repaired_syllables.append(repaired)
    
    # Flatten back to word
    result = []
    for syllable in repaired_syllables:
        result.extend(syllable)
    
    return result


def _repair_syllable(syllable: TypingList[str], constraints: PhonotacticConstraints, 
                    epenthetic_vowel: str) -> TypingList[str]:
    """Repair phonotactic violations in a single syllable"""
    if not syllable:
        return syllable
    
    result = syllable[:]
    
    # Find vowel nucleus
    vowel_pos = -1
    for i, phone in enumerate(result):
        if is_syllabic(phone):
            vowel_pos = i
            break
    
    if vowel_pos == -1:
        # No vowel - add epenthetic vowel
        result.insert(len(result) // 2, epenthetic_vowel)
        vowel_pos = len(result) // 2
    
    # Check onset cluster
    onset = result[:vowel_pos]
    if len(onset) > 2:
        # Too many onset consonants - use epenthesis to break cluster
        new_onset = onset[:1]  # Keep only first consonant
        remaining = onset[1:]
        # Insert epenthetic vowels
        for i, cons in enumerate(remaining):
            new_onset.extend([epenthetic_vowel, cons])
        result = new_onset + result[vowel_pos:]
        vowel_pos = len(new_onset) - 1
    elif len(onset) == 2:
        # Check if cluster is allowed
        if tuple(onset) not in constraints.onset_clusters.allowed_combinations:
            # Break cluster with epenthesis
            result = [onset[0], epenthetic_vowel, onset[1]] + result[vowel_pos:]
            vowel_pos = 2
    
    # Check coda
    coda = result[vowel_pos + 1:]
    if coda:
        # Remove forbidden coda consonants
        valid_coda = []
        for cons in coda:
            if cons in constraints.allowed_codas:
                valid_coda.append(cons)
        
        # Check cluster validity
        if len(valid_coda) > 2:
            valid_coda = valid_coda[:2]  # Limit coda size
        elif len(valid_coda) == 2:
            if tuple(valid_coda) not in constraints.coda_clusters.allowed_combinations:
                valid_coda = valid_coda[:1]  # Keep only first consonant
        
        result = result[:vowel_pos + 1] + valid_coda
    
    return result