"""
Configuration settings for the Language Evolution Simulator
"""

class CONFIG:
    # World generation
    GRID_W = 60
    GRID_H = 60
    
    LAND_PROB_INIT = 0.3    # initial random land probability
    ISLAND_BIAS = 0.4       # pushes land toward center (0..1)
    SMOOTH_STEPS = 6        # cellular automata smoothing passes
    
    # Display
    CANVAS_W = 1400
    CANVAS_H = 900
    
    # Language evolution
    STARTER_WORDS = [
        ["k", "i", "t"],
        ["m", "a", "n"],
        ["w", "a", "t", "e", "r"]
    ]
    
    # Probabilities
    P_MUTATE = 0.004
    P_SPREAD = 0.12
    P_BORROW = 0.08
    P_LANGUAGE_SPLIT = 0.001
    
    # Mutation weights (mutate / delete / add)
    MUTATE_OP_WEIGHTS = (0.5, 0.25, 0.25)
    
    # Feature distance parameters
    ADD_SWEET_DIST = 2.5
    ADD_SWEET_BETA = 0.8
    MUTATE_ALPHA = 0.6
    
    # Borrowing parameters
    PRESTIGE_THRESHOLD = 0.7
    ADAPTATION_STRENGTH = 0.8
    
    # Display
    DRAW_BOUNDARIES = True
    MAX_FONT_PX = 18
    MIN_FONT_PX = 6
    
    # Console output
    PRINT_STATS = True
    STATS_INTERVAL = 50
    LEADERBOARD_TOPK = 8