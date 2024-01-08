import random
import copy

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


# Global unique ID counter
unique_id_counter = 0
is_paused = False
transfer_log = []


class Language:
    def __init__(self, phonemes):
        global unique_id_counter
        self.max_syl = random.choice(range(2, 6))
        self.min_syl = random.choice(range(1, 2))
        self.phonemes = phonemes
        self.selected_phonemes = self.select_phonemes()
        self.onset_consonant_range = random.randint(1, 2)
        self.name = self.generate_word()
        self.unique_id = unique_id_counter
        unique_id_counter += 1
        self.vocabulary = []
        for word in english_words:
            generated_word = self.generate_word()
            unique_word_id = unique_id_counter
            unique_id_counter += 1
            self.vocabulary.append((generated_word, word, unique_word_id))
        self.parameters = []
        for parameter in global_parameters:
            self.parameters.append((parameter[0], random.choice(parameter[1])))
        self.repair_strategy = random.choice(["deletion", "epenthesis"])

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
        syllable_count = random.choice(range(self.min_syl, self.max_syl))
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

    def phonetic_repair(self, word, strategy="deletion"):
        repaired_word = ""
        consonant_cluster = ""

        # Create a list of vowels from the selected phonemes
        vowels = [
            phoneme
            for phoneme in self.selected_phonemes
            if self.phonemes[phoneme]["syllabic"] == "+"
        ]

        for phoneme in word:
            # Check if the phoneme is a consonant
            if phoneme in self.phonemes and self.phonemes[phoneme]["syllabic"] == "-":
                consonant_cluster += phoneme
                # Check if the consonant cluster exceeds the onset consonant range
                if len(consonant_cluster) > self.onset_consonant_range:
                    if strategy == "deletion":
                        # Trim the consonant cluster from the end
                        consonant_cluster = consonant_cluster[
                            : self.onset_consonant_range
                        ]
                    elif strategy == "epenthesis":
                        # Insert a vowel between the consonants
                        vowel = random.choice(vowels)  # Choose a vowel for epenthesis
                        consonant_cluster = (
                            consonant_cluster[: self.onset_consonant_range]
                            + vowel
                            + consonant_cluster[self.onset_consonant_range :]
                        )
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


import tkinter as tk
import random
from PIL import Image


def toggle_pause():
    global is_paused
    is_paused = not is_paused


class Host:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.prestige = random.randint(1, 1)
        self.prev_prestige = self.prestige
        self.neighbors = []
        self.language = Language(phonemes)
        self.language.last_saved_vocabulary = copy.deepcopy(self.language.vocabulary)


def generate_map_from_png(file_path):
    img = Image.open(file_path).convert("L")
    width, height = img.size
    pixels = list(img.getdata())
    threshold = 128
    hosts = [
        Host(x, y)
        for y in range(height)
        for x in range(width)
        if pixels[y * width + x] < threshold
    ]
    host_dict = {(host.x, host.y): host for host in hosts}
    for host in hosts:
        neighbor_positions = [
            (host.x + dx, host.y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
        ]
        host.neighbors = [
            host_dict[pos] for pos in neighbor_positions if pos in host_dict
        ]
    return hosts


def update_hosts(hosts):
    for host in hosts:
        neighbors_prev_prestige_avg = (
            sum(neighbor.prev_prestige for neighbor in host.neighbors)
            / len(host.neighbors)
            if host.neighbors
            else 0
        )
        new_mean = (
            host.prev_prestige + host.prev_prestige + neighbors_prev_prestige_avg
        ) / 3

        host.prestige = max(1, min(int(random.gauss(new_mean, 15)), 100))
        host.prev_prestige = host.prestige
    for host in hosts:
        if host.prestige > 95:
            for neighbor in host.neighbors:
                if neighbor.prestige < 5:
                    # Create a new language for the neighbor, copying all attributes from the host's language except for the phonemes
                    # this is a crude model of retention when a new language is mostly adopted
                    phoneme_storage = neighbor.language.selected_phonemes
                    neighbor.language = copy.deepcopy(host.language)
                    neighbor.language.selected_phonemes = phoneme_storage

                    # Repair each word in the neighbor's vocabulary to fit the phonology of the neighbor's original language
                    for i, (word, english_word, ID) in enumerate(
                        neighbor.language.vocabulary
                    ):
                        neighbor.language.vocabulary[i] = (
                            neighbor.language.phonetic_repair(
                                word, host.language.repair_strategy
                            ),
                            english_word,
                            ID,
                        )
        # below is an attempt to crudely model word loaning
        if host.prestige > 60:
            for neighbor in host.neighbors:
                if neighbor.prestige < 30:
                    # Randomly select a vocabulary item from the high-prestige host
                    word_pair = random.choice(host.language.vocabulary)
                    english_word = word_pair[1]
                    # Find the index of the vocabulary item in the neighbor's language with the same English translation
                    index_to_replace = next(
                        (
                            i
                            for i, v in enumerate(neighbor.language.vocabulary)
                            if v[1] == english_word
                        ),
                        None,
                    )
                    donor_name = host.language.name
                    donor_ID = host.language.unique_id
                    recipient_name = neighbor.language.name
                    recipient_ID = neighbor.language.unique_id
                    donor_word_ID = word_pair[2]
                    recipient_word_ID = neighbor.language.vocabulary[index_to_replace][
                        2
                    ]
                    word_def = word_pair[1]
                    donor_word_form = word_pair[0]
                    recipient_word_form = neighbor.language.vocabulary[
                        index_to_replace
                    ][0]

                    transfer_log.append(
                        (
                            (donor_word_form, word_def, donor_word_ID, donor_ID),
                            (
                                recipient_word_form,
                                word_def,
                                recipient_word_ID,
                                recipient_ID,
                            ),
                        )
                    )
                    # If the word exists in the neighbor's vocabulary
                    if index_to_replace is not None:
                        # Adapt the word to the neighbor's phonotactics
                        adapted_word = neighbor.language.phonetic_repair(
                            word_pair[0], host.language.repair_strategy
                        )
                        # Replace the existing word with the adapted word
                        neighbor.language.vocabulary[index_to_replace] = (
                            adapted_word,
                            english_word,
                            donor_word_ID,
                        )
                    # create the transfer log content
                    with open(
                        f"/Users/sam/Documents/Sam-Code/language_history_sim/save/transfer_log.txt",
                        "a",
                    ) as transfer:
                        transfer.write(
                            f"{donor_word_form},{adapted_word},{donor_word_ID},{donor_ID},{recipient_ID},{donor_name},{recipient_name}\n"
                        )


def draw_hosts(canvas, hosts):
    canvas.delete("all")
    for host in hosts:
        x, y = host.x * 10, host.y * 10  # Scale positions for better visibility
        gray_value = 255 - int(
            host.prestige * 2.55
        )  # Scale the host value to the range 0-255
        color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"  # Convert to hexadecimal
        canvas.create_rectangle(
            x - 5, y - 5, x + 5, y + 5, fill=color, outline=""
        )  # Draw a square with the specified color


tick_count = 0  # Add this line to initialize a tick counter


def tick():
    global tick_count  # Existing line
    if not is_paused:
        for host in hosts:
            if (
                host.language.vocabulary != host.language.last_saved_vocabulary
                or tick_count == 0
            ):
                with open(
                    f"/Users/sam/Documents/Sam-Code/language_history_sim/save/{host.language.name}.txt",
                    "a",
                ) as f:
                    f.write(f"At tick count: {tick_count}\n")
                    for word, english_word, ID in host.language.vocabulary:
                        f.write(f"\t{word}: {english_word}\n")
                host.language.last_saved_vocabulary = copy.deepcopy(
                    host.language.vocabulary
                )
        tick_count += 1  # Existing line
        # print(f"Ticks passed: {tick_count}")  # Existing line
        update_hosts(hosts)
        draw_hosts(canvas, hosts)

        # New lines to calculate and print the average value of all hosts
        total_value = sum(host.prestige for host in hosts)
        average_value = total_value / len(hosts) if hosts else 0
        # print(f"Average value of all hosts: {average_value}")

        louse_words = set()
        total_letter_count = 0
        for host in hosts:
            total_letter_count += sum(
                len(word_pair[0]) for word_pair in host.language.vocabulary
            )
            louse_word_pair = next(
                (
                    word_pair
                    for word_pair in host.language.vocabulary
                    if word_pair[1] == "louse"
                ),
                None,
            )
            if louse_word_pair:
                louse_words.add(louse_word_pair[0])
        print(random.choice(list(louse_words)))

        print(f"Total different ways to say 'louse': {len(louse_words)}")
        print(f"Total number of langs:: {len(hosts)}")
        print(
            f"Total number of letters in all words of every language: {total_letter_count}"
        )

    root.after(1, tick)  # Existing line


hosts = generate_map_from_png(
    "/Users/sam/Documents/Sam-Code/language_history_sim/world.png"
)


root = tk.Tk()
canvas = tk.Canvas(root, width=1000, height=1000)  # Adjust canvas size as needed
canvas.pack()
root.bind("<space>", lambda event: toggle_pause())

tick()  # Start simulation

root.mainloop()
# orders of business
# we want a way to mutate languages themsevlves
# eventually we want to split languages and hosts so that multilingualism acn be simulated. this is essential to completing the program
# maybe the sonority heirarchy
# language tracking and splitting

# we need a way to track superstrates and substrates advancing through the model
# and a much more advanced way to model retention than just not changing phonemes
# the issue here is that I want to add langauge mutation
# but its hard to think about it without visualization
# currently I don't have a way to visualize anythign thats happening
# I guess that should be priority 1 then
# maybe I should make a smaller model to work with so visualization is easier
# than doing all this shit

# make toy model of toy model
# visualization method for that
# reimplement here into big fast model
