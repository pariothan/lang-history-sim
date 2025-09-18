import { PhonemeFeatures } from '../types';

// Feature vector helper
const fv = (features: Partial<PhonemeFeatures>): PhonemeFeatures => ({
  syllabic: 0,
  consonantal: 0,
  sonorant: 0,
  continuant: 0,
  nasal: 0,
  lateral: 0,
  voice: 0,
  labial: 0,
  coronal: 0,
  dorsal: 0,
  high: 0,
  low: 0,
  back: 0,
  round: 0,
  ...features
});

export const PHONEMES: Record<string, PhonemeFeatures> = {
  // Vowels
  "i": fv({ syllabic: 1, consonantal: -1, sonorant: 1, continuant: 1, voice: 1, dorsal: 1, high: 1, low: -1, back: -1, round: -1 }),
  "e": fv({ syllabic: 1, consonantal: -1, sonorant: 1, continuant: 1, voice: 1, dorsal: 1, high: 0, low: 0, back: -1, round: -1 }),
  "a": fv({ syllabic: 1, consonantal: -1, sonorant: 1, continuant: 1, voice: 1, dorsal: 1, high: -1, low: 1, back: 0, round: -1 }),
  "o": fv({ syllabic: 1, consonantal: -1, sonorant: 1, continuant: 1, voice: 1, labial: 1, dorsal: 1, high: 0, low: 0, back: 1, round: 1 }),
  "u": fv({ syllabic: 1, consonantal: -1, sonorant: 1, continuant: 1, voice: 1, labial: 1, dorsal: 1, high: 1, low: -1, back: 1, round: 1 }),
  "ə": fv({ syllabic: 1, consonantal: -1, sonorant: 1, continuant: 1, voice: 1, dorsal: 1, high: 0, low: 0, back: 0, round: -1 }),

  // Stops
  "p": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: -1, voice: -1, labial: 1 }),
  "b": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: -1, voice: 1, labial: 1 }),
  "t": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: -1, voice: -1, coronal: 1 }),
  "d": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: -1, voice: 1, coronal: 1 }),
  "k": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: -1, voice: -1, dorsal: 1 }),
  "g": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: -1, voice: 1, dorsal: 1 }),

  // Fricatives
  "f": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: 1, voice: -1, labial: 1 }),
  "v": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: 1, voice: 1, labial: 1 }),
  "s": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: 1, voice: -1, coronal: 1 }),
  "z": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: 1, voice: 1, coronal: 1 }),
  "ʃ": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: 1, voice: -1, coronal: 1 }),
  "ʒ": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: 1, voice: 1, coronal: 1 }),
  "x": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: 1, voice: -1, dorsal: 1 }),
  "h": fv({ syllabic: -1, consonantal: 1, sonorant: -1, continuant: 1, voice: -1 }),

  // Nasals
  "m": fv({ syllabic: -1, consonantal: 1, sonorant: 1, continuant: -1, nasal: 1, voice: 1, labial: 1 }),
  "n": fv({ syllabic: -1, consonantal: 1, sonorant: 1, continuant: -1, nasal: 1, voice: 1, coronal: 1 }),
  "ŋ": fv({ syllabic: -1, consonantal: 1, sonorant: 1, continuant: -1, nasal: 1, voice: 1, dorsal: 1 }),

  // Liquids
  "l": fv({ syllabic: -1, consonantal: 1, sonorant: 1, continuant: 1, lateral: 1, voice: 1, coronal: 1 }),
  "r": fv({ syllabic: -1, consonantal: 1, sonorant: 1, continuant: 1, voice: 1, coronal: 1 }),

  // Glides
  "j": fv({ syllabic: -1, consonantal: -1, sonorant: 1, continuant: 1, voice: 1, dorsal: 1, high: 1, back: -1, round: -1 }),
  "w": fv({ syllabic: -1, consonantal: -1, sonorant: 1, continuant: 1, voice: 1, labial: 1, dorsal: 1, high: 1, back: 1, round: 1 }),
};

export const INVENTORY = Object.keys(PHONEMES).sort();
export const PHONEME_INDEX = Object.fromEntries(INVENTORY.map((p, i) => [p, i]));

export const FEATURE_NAMES = [
  "syllabic", "consonantal", "sonorant", "continuant", "nasal", "lateral", 
  "voice", "labial", "coronal", "dorsal", "high", "low", "back", "round"
];

// Color projection matrix for visualization
export const RGB_PROJECTION = [
  [0.8, -0.4, 0.2, 0.3, 0.1, 0.2, 0.3, 0.6, -0.2, 0.1, 0.9, -0.3, -0.5, -0.6], // R
  [-0.4, 0.8, 0.1, 0.5, 0.2, -0.2, 0.3, 0.1, 0.6, 0.2, -0.5, 0.7, 0.4, -0.2], // G
  [0.1, 0.2, 0.8, -0.4, -0.2, 0.5, -0.3, -0.2, 0.2, 0.7, 0.3, 0.1, -0.1, 0.9], // B
];

export function featureDistance(a: PhonemeFeatures, b: PhonemeFeatures): number {
  let distance = 0;
  for (const feature of FEATURE_NAMES) {
    const aVal = a[feature as keyof PhonemeFeatures];
    const bVal = b[feature as keyof PhonemeFeatures];
    
    if (aVal === 0 && bVal === 0) continue;
    if (aVal === 0 || bVal === 0) distance += 2;
    else if (aVal !== bVal) distance += 1;
  }
  return distance;
}

export function isSyllabic(phoneme: string): boolean {
  return PHONEMES[phoneme]?.syllabic > 0;
}

export function isConsonant(phoneme: string): boolean {
  return PHONEMES[phoneme]?.consonantal > 0;
}

export function syllableCount(word: string[]): number {
  return word.filter(p => isSyllabic(p)).length;
}

export function ensureHasVowel(word: string[]): void {
  if (syllableCount(word) === 0) {
    const vowels = INVENTORY.filter(p => isSyllabic(p));
    const vowel = vowels[Math.floor(Math.random() * vowels.length)];
    word.splice(Math.floor(word.length / 2), 0, vowel);
  }
}