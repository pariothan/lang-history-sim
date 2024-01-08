import random

english_words = [
    "I",
    "you_singular",
    "they_singular",
    "we",
    "you_plural",
    "they_plural",
    "this",
    "that",
    "here",
    "there",
    "who",
    "what",
    "where",
    "when",
    "how",
    "not",
    "all",
    "many",
    "some",
    "few",
    "other",
    "one",
    "two",
    "three",
    "four",
    "five",
    "big",
    "long",
    "wide",
    "thick",
    "heavy",
    "small",
    "short",
    "narrow",
    "thin",
    "woman",
    "man_adult_male",
    "man_human_being",
    "child",
    "wife",
    "husband",
    "mother",
    "father",
    "animal",
    "fish",
    "bird",
    "dog",
    "louse",
    "snake",
    "worm",
    "tree",
    "forest",
    "stick",
    "fruit",
    "seed",
    "leaf",
    "root",
    "bark_of_tree",
    "flower",
    "grass",
    "rope",
    "skin",
    "meat",
    "blood",
    "bone",
    "fat_noun",
    "egg",
    "horn",
    "tail",
    "feather",
    "hair",
    "head",
    "ear",
    "eye",
    "nose",
    "mouth",
    "tooth",
    "tongue_organ",
    "fingernail",
    "foot",
    "leg",
    "knee",
    "hand",
    "wing",
    "belly",
    "guts",
    "neck",
    "back",
    "breast",
    "heart",
    "liver",
    "to_drink",
    "to_eat",
    "to_bite",
    "to_suck",
    "to_spit",
    "to_vomit",
    "to_blow",
    "to_breathe",
    "to_laugh",
    "to_see",
    "to_hear",
    "to_know",
    "to_think",
    "to_smell",
    "to_fear",
    "to_sleep",
    "to_live",
    "to_die",
    "to_kill",
    "to_fight",
    "to_hunt",
    "to_hit",
    "to_cut",
    "to_split",
    "to_stab",
    "to_scratch",
    "to_dig",
    "to_swim",
    "to_fly",
    "to_walk",
    "to_come",
    "to_lie_in_bed",
    "to_sit",
    "to_stand",
    "to_turn_intransitive",
    "to_fall",
    "to_give",
    "to_hold",
    "to_squeeze",
    "to_rub",
    "to_wash",
    "to_wipe",
    "to_pull",
    "to_push",
    "to_throw",
    "to_tie",
    "to_sew",
    "to_count",
    "to_say",
    "to_sing",
    "to_play",
    "to_float",
    "to_flow",
    "to_freeze",
    "to_swell",
    "sun",
    "moon",
    "star",
    "water",
    "rain",
    "river",
    "lake",
    "sea",
    "salt",
    "stone",
    "sand",
    "dust",
    "earth",
    "cloud",
    "fog",
    "sky",
    "wind",
    "snow",
    "ice",
    "smoke",
    "fire",
    "ash",
    "to_burn",
    "road",
    "mountain",
    "red",
    "green",
    "yellow",
    "white",
    "black",
    "night",
    "day",
    "year",
    "warm",
    "cold",
    "full",
    "new",
    "old",
    "good",
    "bad",
    "rotten",
    "dirty",
    "straight",
    "round",
    "sharp_as_knife",
    "dull_as_knife",
    "smooth",
    "wet",
    "dry",
    "correct",
    "near",
    "far",
    "right",
    "left",
    "at",
    "in",
    "with",
    "and",
    "if",
    "because",
    "name",
]

features = {
    "syllabic",
    "consonantal",
    "high",
    "back",
    "low",
    "anterior",
    "coronal",
    "coronal",
    "round",
    "tense",
    "voice",
    "continuant",
    "nasal",
    "strident",
    "lateral",
}
states = {"+", "-", "0"}
phonemes = dict()
phonemes["i"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["u"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "+",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["e"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["ɑ"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "-",
    "back": "+",
    "low": "+",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "+",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["ɪ"] = {
    "syllabic": "+",
    "consonantal": "-",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "-",
    "tense": "-",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["w"] = {
    "syllabic": "-",
    "consonantal": "-",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "+",
    "tense": "-",
    "voice": "0",
    "continuant": "0",
    "nasal": "0",
    "strident": "0",
    "lateral": "0",
}
phonemes["r"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["l"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "+",
}
phonemes["p"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["b"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["t"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["d"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["θ"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["ð"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["n"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "-",
    "nasal": "+",
    "strident": "-",
    "lateral": "-",
}
phonemes["s"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "+",
    "nasal": "-",
    "strident": "+",
    "lateral": "-",
}
phonemes["z"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "-",
    "back": "-",
    "low": "-",
    "anterior": "+",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "+",
    "lateral": "-",
}
phonemes["ʃ"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "+",
    "nasal": "-",
    "strident": "+",
    "lateral": "-",
}
phonemes["ʒ"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "-",
    "low": "-",
    "anterior": "-",
    "coronal": "+",
    "round": "0",
    "tense": "0",
    "voice": "+",
    "continuant": "+",
    "nasal": "-",
    "strident": "+",
    "lateral": "-",
}
phonemes["k"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["g"] = {
    "syllabic": "-",
    "consonantal": "+",
    "high": "+",
    "back": "+",
    "low": "-",
    "anterior": "-",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "-",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}
phonemes["h"] = {
    "syllabic": "-",
    "consonantal": "-",
    "high": "-",
    "back": "-",
    "low": "+",
    "anterior": "-",
    "coronal": "-",
    "round": "0",
    "tense": "0",
    "voice": "-",
    "continuant": "+",
    "nasal": "-",
    "strident": "-",
    "lateral": "-",
}

import random

global_parameters = [
    ("head_order", ["head_initial", "head_final"]),
    ("EPP", ["true", "false"]),
]


class Language:
    def __init__(self, phonemes):
        self.phonemes = phonemes
        self.selected_phonemes = self.select_phonemes()
        self.onset_consonant_range = random.randint(1, 3)
        self.name = self.generate_word()
        self.vocabulary = []
        for word in english_words:
            self.vocabulary.append((self.generate_word(), word))
        self.parameters = []
        for parameter in global_parameters:
            self.parameters.append((parameter[0], random.choice(parameter[1])))

    def dissimilarity(self, phoneme1, phoneme2):
        score = 0
        for feature in phoneme1:
            if phoneme1[feature] != phoneme2[feature]:
                score += 1
        return score

    def total_dissimilarity(self, phoneme, phoneme_set):
        total_score = 0
        for p in phoneme_set:
            total_score += self.dissimilarity(phoneme, self.phonemes[p])
        return total_score

    def select_phonemes(self):
        selected_phonemes = {random.choice(list(self.phonemes.keys()))}
        remaining_phonemes = set(self.phonemes.keys()) - selected_phonemes

        while len(selected_phonemes) < 10:
            next_phoneme = max(
                remaining_phonemes,
                key=lambda p: self.total_dissimilarity(
                    self.phonemes[p], selected_phonemes
                ),
            )
            selected_phonemes.add(next_phoneme)
            remaining_phonemes.remove(next_phoneme)
        return selected_phonemes

    def generate_word(self):
        print(self.onset_consonant_range)
        syllable_count = random.choice(range(2, 4))
        consonants = []
        vowels = []
        word = []
        for phoneme in self.selected_phonemes:
            if self.phonemes[phoneme]["syllabic"] == "+":
                vowels.append(phoneme)
            else:
                consonants.append(phoneme)
        for i in range(syllable_count):
            onset_count = random.randint(1, self.onset_consonant_range)
            onset = []
            for j in range(onset_count):
                onset.append(random.choice(consonants))
            onset = "".join(onset)
            nucleus = random.choice(vowels)
            word.append(onset + nucleus)
        return "".join(word)

    def phonetic_repair(self, word):
        repaired_word = ""
        consonant_cluster = ""

        for phoneme in word:
            # Check if the phoneme is a consonant
            if phoneme in self.phonemes and self.phonemes[phoneme]["syllabic"] == "-":
                consonant_cluster += phoneme
                # Check if the consonant cluster exceeds the onset consonant range
                if len(consonant_cluster) > self.onset_consonant_range:
                    # Trim the consonant cluster from the end
                    consonant_cluster = consonant_cluster[: self.onset_consonant_range]
            else:
                # Add the legal consonant cluster to the repaired word
                repaired_word += consonant_cluster
                consonant_cluster = ""  # Reset the consonant cluster

                # Check if the phoneme is in the language's selected phonemes
                if phoneme in self.selected_phonemes:
                    repaired_word += phoneme
                else:
                    # If not, find the most similar phoneme from the selected ones
                    similar_phoneme = min(
                        self.selected_phonemes,
                        key=lambda p: self.dissimilarity(
                            self.phonemes[phoneme], self.phonemes[p]
                        ),
                    )
                    repaired_word += similar_phoneme

        # Add any remaining consonant cluster to the repaired word
        repaired_word += consonant_cluster

        return repaired_word


languages = []
for i in range(10):
    languages.append(Language(phonemes))

print(f"Language name: {languages[0].name}")
print(f"Selected Phonemes: {languages[0].selected_phonemes}")
print(languages[0].vocabulary)
print(languages[0].parameters)

# ok, we can generate C(C)(C)V languages of arbitrary size here. the phonotactics are threadbare, but its enough to model language change if we want to. derivational morphology could be a fun way to move foreward from this, but waht we really want to get at is language change along with grammar and borrowing.

# things we need to move into the language change stage
# words need a life of their own. this means phonetic repair ADDED@
# phonetic repair along with extensive loaning system. the likelihood of loans occurring should be relative to social prestige virus sim time for this part
# along with that we need language internal change, and larger language spread
# likewise we need languages to spread without overtaking all vocabulary
# so
# everything has its own spread parameters
# language spread has non-spread along parameters
# or perhaps retention parameters
# this means we can get form divergence and that should make up for old forms being wiped out by random drift
# theoretically this shoudl replicate my hypothesis of branches growing to become new trees such that a relatively uniform level of diversity is maintained while still haivng large families and language/wanderwort sweeps
# essentially the diversity of the system should be due to the parameters of the game, not really much of anything non arbitrary to do with the starting state
# language diversity is inherent nature, not heritage
# bold statement
