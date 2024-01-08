alveolar = ["t", "d", "n", "s", "z", "r", "l"]
postalveolar = ["sh", "zh"]
palatal = ["j"]
velar = ["k", "g", "ng"]
glottal = ["h"]
voiced = ["b", "m", "v", "TH", "d", "n", "z", "r", "l", "zh", "j", "g", "ng"]
voiceless = ["p", "f", "th", "t", "s", "k", "h"]
consonants = (
    bilabial
    + labiodental
    + dental
    + alveolar
    + postalveolar
    + palatal
    + velar
    + glottal
)
front = ["i", "I", "e", "E", "ae"]
central = ["eu", "uh"]
back = ["u", "U", "o", "C", "a"]
lax = ["I", "E", "ae", "eu", "uh", "U", "C", "a"]
tense = ["i", "e", "u", "o"]
vowels = front + central + back

# now we go through each set of features and make a dictionary that lists each phoneme and its features

phonemes = dict()
phonemes["p"] = {"voiceless", "bilabial", "stop", "consonant"}
phonemes["b"] = {"voiced", "bilabial", "stop", "consonant"}
phonemes["m"] = {"voiced", "bilabial", "nasal", "consonant"}
phonemes["f"] = {"voiceless", "labiodental", "fricative", "consonant"}
phonemes["v"] = {"voiced", "labiodental", "fricative", "consonant"}
phonemes["Θ"] = ["voiceless", "dental", "fricative", "consonant"]
phonemes["δ"] = ["voiced", "dental", "fricative", "consonant"]
phonemes["t"] = {"voiceless", "alveolar", "stop", "consonant"}
phonemes["d"] = {"voiced", "alveolar", "stop", "consonant"}
phonemes["n"] = {"voiced", "alveolar", "nasal", "consonant"}
phonemes["s"] = {"voiceless", "alveolar", "fricative", "consonant"}
phonemes["z"] = {"voiced", "alveolar", "fricative", "consonant"}
phonemes["r"] = {"voiced", "alveolar", "rhotic", "approximant", "consonant"}
phonemes["l"] = {"voiced", "alveolar", "lateral", "approximant", "consonant"}
phonemes["ʃ"] = {"voiceless", "post-alveolar", "fricative", "consonant"}
phonemes["ʒ"] = {"voiced", "post-alveolar", "fricative", "consonant"}
phonemes["j"] = {"voiced", "palatal", "glide", "consonant"}
phonemes["k"] = {"voiceless", "velar", "stop", "consonant"}
phonemes["g"] = {"voiced", "velar", "stop", "consonant"}
phonemes["ng"] = {"voiced", "velar", "nasal", "consonant"}
phonemes["h"] = {"voiceless", "glottal", "fricative", "consonant"}
phonemes["a"] = {"low", "back", "lax", "vowel"}
phonemes["æ"] = {"low", "front", "lax", "vowel"}
phonemes["i"] = {"high", "front", "tense", "vowel"}
phonemes["u"] = {"high", "back", "tense", "vowel"}
phonemes["ʊ"] = {"high", "back", "lax", "vowel"}
phonemes["o"] = {"mid", "back", "tense", "vowel"}
phonemes["ɔ"] = {"mid", "back", "lax", "vowel"}
phonemes["e"] = {"mid", "front", "tense", "vowel"}
phonemes["ɛ"] = {"mid", "front", "lax", "vowel"}
phonemes["ʌ"] = {"mid", "central", "lax", "vowel"}


def readFeatures(phoneme):
    return phonemes[phoneme]
