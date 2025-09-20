"""
Configuration settings for the Language Evolution Simulator
"""


class CONFIG:
    # World generation
    GRID_W = 50
    GRID_H = 40

    LAND_PROB_INIT = 0.15  # initial random land probability
    ISLAND_BIAS = 0.4  # pushes land toward center (0..1)
    SMOOTH_STEPS = 6  # cellular automata smoothing passes

    # Display
    CANVAS_W = 1400
    CANVAS_H = 900

    # Language evolution
    STARTER_WORDS = [["k", "i", "t"], ["b", "o", "k"], ["k", "a", "a", "p"],
                     ["k", "i", "t"], ["k", "i", "t"]]

    # Probabilities
    P_MUTATE = 0.05
    P_SPREAD = 0.24  # Increased from 0.12 for faster spread
    P_BORROW = 0.12
    P_LANGUAGE_SPLIT = 0.03
    P_LONG_DISTANCE_SPREAD = 0.002  # New: probability of long-distance spread
    P_PRESTIGE_DRIFT = 0.15  # Probability of prestige change per tick

    # Mutation weights (mutate / delete / add)
    MUTATE_OP_WEIGHTS = (0.5, 0.25, 0.25)

    # Feature distance parameters
    ADD_SWEET_DIST = 2.5
    ADD_SWEET_BETA = 0.8
    MUTATE_ALPHA = 0.6

    # Borrowing parameters
    PRESTIGE_THRESHOLD = 0.7
    ADAPTATION_STRENGTH = 0.8

    # Prestige drift parameters
    PRESTIGE_DRIFT_MAGNITUDE = 0.08  # Maximum change per drift event
    PRESTIGE_DRIFT_BIAS = 0.5  # Bias toward middle value (0.5)
    PRESTIGE_MIDDLE_BIAS_STRENGTH = 0.01  # Strength of pull toward middle value

    # Long-distance interaction parameters
    LONG_DISTANCE_RANGE = 8  # Maximum distance for long-distance spread
    LONG_DISTANCE_MIN = 3  # Minimum distance to be considered long-distance

    # Language contiguity parameters
    CONTIGUITY_STRICT = True  # Enforce strict contiguity for languages
    CONTIGUITY_ENFORCE_INTERVAL = 100  # Check contiguity every N ticks

    # Phonological inventory drift parameters
    P_PHONEME_ADD = 0.7  # Probability of adding phonemes to inventory
    P_PHONEME_REMOVE = 0.7  # Probability of removing phonemes from inventory
    P_PHONEME_SUBSTITUTE = 0.5  # Probability of substituting phonemes in inventory
    MIN_PHONEME_INVENTORY_SIZE = 12  # Minimum inventory size before allowing removal
    MIN_VOWEL_COUNT = 3  # Minimum number of vowels to maintain

    # Phoneme inventory optimization biases
    P_OPTIMIZE_ADD = 0.7  # Probability of optimization when adding phonemes
    P_OPTIMIZE_REMOVE = 0.8  # Probability of optimization when removing phonemes
    DISPERSION_WEIGHT = 0.7  # Weight for dispersion in substitution (vs similarity)
    SIMILARITY_WEIGHT = 0.3  # Weight for similarity in substitution
    DISPERSION_TOLERANCE = -0.1  # Minimum allowed dispersion change in substitution

    # Phonotactic constraint drift parameters
    P_CONSTRAINT_DRIFT = 0.15  # Overall probability of constraint changes
    P_SYLLABLE_DRIFT = 0.5  # Probability of syllable preference changes
    P_GEMINATION_DRIFT = 0.3  # Probability of gemination setting changes
    P_WORD_LENGTH_DRIFT = 0.4  # Probability of word length preference changes
    GEMINATION_PROB_RANGE = (0.02, 0.15)  # Range for gemination probability
    SYLLABLE_COUNT_RANGE = (1, 4)  # Range for preferred syllable count

    # Language evolution timing parameters
    EVOLUTION_INTERVAL = 50  # Minimum ticks between evolution cycles
    SAMPLE_SIZE_LEXICON = 20  # Number of words to sample for sound changes

    # Constraint evolution parameters
    P_SYLLABLE_EVOLUTION = 0.05  # Probability of syllable structure evolution
    P_CLUSTER_EVOLUTION = 0.03  # Probability of consonant cluster evolution
    P_CODA_EVOLUTION = 0.04  # Probability of coda restriction evolution

    # Name evolution parameters
    P_NAME_MUTATION = 0.05  # Probability of random name mutation per cycle

    # Phonological rule system parameters
    P_RULE_GENERATION_BASE = 0.05  # Base probability for generating new rules
    RULE_PRODUCTIVITY_THRESHOLD = 0.001  # Minimum productivity before rule removal
    RULE_DECAY_RATE_DEFAULT = 0.0  # Default decay rate for new rules
    RULE_STRENGTH_DEFAULT = 1.0  # Default strength for new rules
    RULE_PRODUCTIVITY_DEFAULT = 1.0  # Default productivity for new rules

    # Sound change application parameters
    SOUND_CHANGE_CONSERVATISM_FACTOR = 1.0  # Multiplier for conservatism effects
    CONTACT_PRESSURE_CAP = 0.5  # Maximum contact pressure influence
    CONTACT_INFLUENCE_FACTOR = 0.1  # Base contact influence per language
    MAX_CONTACT_LANGUAGES = 3  # Maximum number of contact languages considered

    # Phonological weight and distance parameters
    SUBSTITUTION_FEATURE_THRESHOLD = 0.7  # Threshold for feature-based substitution
    PHONEME_DISTANCE_SCALING = 1.0  # Scaling factor for phonological distances

    # Initial language generation parameters
    MIN_INITIAL_VOWELS = 3  # Minimum vowels in initial phoneme inventory
    INITIAL_INVENTORY_SIZE_RANGE = (15, 25)  # Range for initial inventory size
    CONSTRAINT_PROFILE_WEIGHTS = [0.5, 0.3, 0.2
                                  ]  # Weights for constraint profile selection
    EPENTHETIC_VOWEL_CHOICES = ["ə", "i", "a"]  # Available epenthetic vowels
    PRESTIGE_RANGE = (0.1, 0.9)  # Range for initial language prestige
    CONSERVATISM_RANGE = (0.3, 0.8)  # Range for initial language conservatism

    # Display
    DRAW_BOUNDARIES = True
    MAX_FONT_PX = 8
    MIN_FONT_PX = 3

    # Console output
    PRINT_STATS = True
    STATS_INTERVAL = 50
    LEADERBOARD_TOPK = 8
