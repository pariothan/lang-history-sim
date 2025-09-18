export const CONFIG = {
  // World generation
  GRID_W: 60,
  GRID_H: 45,
  LAND_PROB_INIT: 0.35,
  ISLAND_BIAS: 0.4,
  SMOOTH_STEPS: 6,
  
  // Display
  CANVAS_W: 1200,
  CANVAS_H: 800,
  
  // Language evolution probabilities
  P_MUTATE: 0.006,
  P_SPREAD: 0.15,
  P_BORROW: 0.10,
  P_LANGUAGE_SPLIT: 0.002,
  
  // Mutation weights
  MUTATE_OP_WEIGHTS: [0.5, 0.25, 0.25] as const, // [mutate, delete, add]
  
  // Feature distance parameters
  ADD_SWEET_DIST: 2.5,
  ADD_SWEET_BETA: 0.8,
  MUTATE_ALPHA: 0.6,
  
  // Borrowing parameters
  PRESTIGE_THRESHOLD: 0.7,
  ADAPTATION_STRENGTH: 0.8,
  
  // Display settings
  DRAW_BOUNDARIES: true,
  MAX_FONT_SIZE: 14,
  MIN_FONT_SIZE: 8,
  
  // Statistics
  PRINT_STATS: false,
  STATS_INTERVAL: 100,
  LEADERBOARD_TOPK: 8,
  
  // Starter words
  STARTER_WORDS: [
    ["k", "i", "t"],
    ["m", "a", "n"], 
    ["w", "a", "t", "e", "r"],
    ["f", "i", "r"],
    ["s", "u", "n"]
  ]
};