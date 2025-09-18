export interface PhonemeFeatures {
  syllabic: number;
  consonantal: number;
  sonorant: number;
  continuant: number;
  nasal: number;
  lateral: number;
  voice: number;
  labial: number;
  coronal: number;
  dorsal: number;
  high: number;
  low: number;
  back: number;
  round: number;
}

export interface Word {
  form: string[];
  meaning: string;
  originLanguageId: number;
  borrowedFrom?: number;
  generation: number;
}

export interface Community {
  x: number;
  y: number;
  languageId: number;
  population: number;
  prestige: number;
}

export interface WorldStats {
  totalCommunities: number;
  speakingCommunities: number;
  languages: number;
  largestLanguage: number;
  languageDistribution: Record<number, number>;
}

export enum SyllableType {
  V = "V",
  CV = "CV", 
  VC = "VC",
  CVC = "CVC",
  CCV = "CCV",
  CCVC = "CCVC",
  VCC = "VCC",
  CVCC = "CVCC"
}

export interface PhonotacticConstraints {
  syllableTypes: Record<SyllableType, number>;
  allowedCodas: Set<string>;
  onsetClusters: Set<string>;
  codaClusters: Set<string>;
  minSyllables: number;
  maxSyllables: number;
  preferredSyllables: number;
  allowGemination: boolean;
  geminationProbability: number;
  geminableConsonants: Set<string>;
  forbiddenSequences: Set<string>;
}