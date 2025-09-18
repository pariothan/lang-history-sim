import { Word, PhonotacticConstraints, SyllableType } from '../types';
import { PHONEMES, INVENTORY, PHONEME_INDEX, featureDistance, isSyllabic, isConsonant, syllableCount, ensureHasVowel } from '../data/phonemes';
import { getVocabularySubset } from '../data/vocabulary';
import { CONFIG } from '../config';

export class Language {
  private static nextId = 1;
  
  public id: number;
  public name: string;
  public generation: number;
  public phonemeInventory: Set<string>;
  public lexicon: Map<string, Word>;
  public prestige: number;
  public conservatism: number;
  public parentId: number | null;
  public children: number[];
  public phonotacticConstraints: PhonotacticConstraints;

  constructor(parent?: Language) {
    this.id = Language.nextId++;
    this.generation = parent ? parent.generation + 1 : 0;
    this.parentId = parent?.id || null;
    this.children = [];
    
    if (parent) {
      // Inherit from parent
      this.phonemeInventory = new Set(parent.phonemeInventory);
      this.phonotacticConstraints = this.copyConstraints(parent.phonotacticConstraints);
      this.driftPhonemes();
    } else {
      // Create new language
      this.phonemeInventory = this.selectInitialPhonemes();
      this.phonotacticConstraints = this.getDefaultConstraints();
    }
    
    this.prestige = Math.random() * 0.8 + 0.1;
    this.conservatism = Math.random() * 0.5 + 0.3;
    this.name = this.generateName();
    
    // Initialize lexicon
    this.lexicon = new Map();
    if (parent) {
      this.inheritLexicon(parent);
    } else {
      this.generateInitialLexicon();
    }
  }

  private selectInitialPhonemes(): Set<string> {
    const vowels = INVENTORY.filter(p => isSyllabic(p));
    const consonants = INVENTORY.filter(p => !isSyllabic(p));
    
    // Ensure minimum vowel system
    const selected = new Set<string>();
    const numVowels = Math.min(5, vowels.length);
    const selectedVowels = vowels.sort(() => Math.random() - 0.5).slice(0, numVowels);
    selectedVowels.forEach(v => selected.add(v));
    
    // Add consonants using feature dispersion
    const remaining = new Set(consonants);
    const targetSize = Math.floor(Math.random() * 10) + 15; // 15-25 phonemes
    
    while (selected.size < targetSize && remaining.size > 0) {
      let bestPhone = '';
      let maxDistance = -1;
      
      for (const phone of remaining) {
        const totalDistance = Array.from(selected).reduce((sum, existing) => {
          return sum + featureDistance(PHONEMES[phone], PHONEMES[existing]);
        }, 0);
        
        if (totalDistance > maxDistance) {
          maxDistance = totalDistance;
          bestPhone = phone;
        }
      }
      
      if (bestPhone) {
        selected.add(bestPhone);
        remaining.delete(bestPhone);
      } else {
        break;
      }
    }
    
    return selected;
  }

  private getDefaultConstraints(): PhonotacticConstraints {
    return {
      syllableTypes: {
        [SyllableType.CV]: 0.6,
        [SyllableType.CVC]: 0.3,
        [SyllableType.V]: 0.1,
        [SyllableType.VC]: 0.0,
        [SyllableType.CCV]: 0.0,
        [SyllableType.CCVC]: 0.0,
        [SyllableType.VCC]: 0.0,
        [SyllableType.CVCC]: 0.0
      },
      allowedCodas: new Set(['t', 'n', 'm', 's', 'k', 'p']),
      onsetClusters: new Set(),
      codaClusters: new Set(),
      minSyllables: 1,
      maxSyllables: 3,
      preferredSyllables: 2,
      allowGemination: false,
      geminationProbability: 0.05,
      geminableConsonants: new Set(),
      forbiddenSequences: new Set()
    };
  }

  private copyConstraints(constraints: PhonotacticConstraints): PhonotacticConstraints {
    return {
      syllableTypes: { ...constraints.syllableTypes },
      allowedCodas: new Set(constraints.allowedCodas),
      onsetClusters: new Set(constraints.onsetClusters),
      codaClusters: new Set(constraints.codaClusters),
      minSyllables: constraints.minSyllables,
      maxSyllables: constraints.maxSyllables,
      preferredSyllables: constraints.preferredSyllables,
      allowGemination: constraints.allowGemination,
      geminationProbability: constraints.geminationProbability,
      geminableConsonants: new Set(constraints.geminableConsonants),
      forbiddenSequences: new Set(constraints.forbiddenSequences)
    };
  }

  private driftPhonemes(): void {
    // Small chance to gain or lose phonemes
    if (Math.random() < 0.1) {
      const available = INVENTORY.filter(p => !this.phonemeInventory.has(p));
      if (available.length > 0 && Math.random() < 0.5) {
        const newPhone = available[Math.floor(Math.random() * available.length)];
        this.phonemeInventory.add(newPhone);
      }
    }
    
    if (Math.random() < 0.05 && this.phonemeInventory.size > 10) {
      const vowelsInInventory = Array.from(this.phonemeInventory).filter(p => isSyllabic(p));
      if (vowelsInInventory.length > 2) {
        const phones = Array.from(this.phonemeInventory);
        const toRemove = phones[Math.floor(Math.random() * phones.length)];
        if (!isSyllabic(toRemove) || vowelsInInventory.length > 3) {
          this.phonemeInventory.delete(toRemove);
        }
      }
    }
  }

  private generateWord(): string[] {
    const numSyllables = Math.random() < 0.6 
      ? this.phonotacticConstraints.preferredSyllables
      : Math.floor(Math.random() * (this.phonotacticConstraints.maxSyllables - this.phonotacticConstraints.minSyllables + 1)) + this.phonotacticConstraints.minSyllables;
    
    const word: string[] = [];
    const vowels = Array.from(this.phonemeInventory).filter(p => isSyllabic(p));
    const consonants = Array.from(this.phonemeInventory).filter(p => !isSyllabic(p));
    
    if (vowels.length === 0) vowels.push('a');
    if (consonants.length === 0) consonants.push('t');
    
    for (let i = 0; i < numSyllables; i++) {
      // Simple CV structure for now
      if (Math.random() < 0.8 && consonants.length > 0) {
        word.push(consonants[Math.floor(Math.random() * consonants.length)]);
      }
      word.push(vowels[Math.floor(Math.random() * vowels.length)]);
    }
    
    return word;
  }

  private generateName(): string {
    const nameForm = this.generateWord();
    return nameForm.join('').charAt(0).toUpperCase() + nameForm.join('').slice(1);
  }

  private generateInitialLexicon(): void {
    const meanings = getVocabularySubset(120);
    for (const meaning of meanings) {
      const wordForm = this.generateWord();
      const word: Word = {
        form: wordForm,
        meaning,
        originLanguageId: this.id,
        generation: 0
      };
      this.lexicon.set(meaning, word);
    }
  }

  private inheritLexicon(parent: Language): void {
    for (const [meaning, parentWord] of parent.lexicon) {
      const newForm = [...parentWord.form];
      if (Math.random() < 0.1) {
        this.applySoundChange(newForm);
      }
      
      const word: Word = {
        form: newForm,
        meaning,
        originLanguageId: parentWord.originLanguageId,
        borrowedFrom: parentWord.borrowedFrom,
        generation: parentWord.generation + 1
      };
      this.lexicon.set(meaning, word);
    }
  }

  private applySoundChange(wordForm: string[]): void {
    if (wordForm.length === 0) return;
    
    const changeType = Math.random();
    
    if (changeType < 0.5 && wordForm.length > 0) {
      // Substitution
      const idx = Math.floor(Math.random() * wordForm.length);
      const oldPhone = wordForm[idx];
      const candidates = Array.from(this.phonemeInventory).filter(p => {
        if (!(oldPhone in PHONEMES) || !(p in PHONEMES)) return false;
        return featureDistance(PHONEMES[oldPhone], PHONEMES[p]) <= 2;
      });
      
      if (candidates.length > 0) {
        wordForm[idx] = candidates[Math.floor(Math.random() * candidates.length)];
      }
    } else if (changeType < 0.75 && wordForm.length > 1) {
      // Deletion
      const idx = Math.floor(Math.random() * wordForm.length);
      if (!isSyllabic(wordForm[idx]) || syllableCount(wordForm) > 1) {
        wordForm.splice(idx, 1);
      }
    } else {
      // Insertion
      const idx = Math.floor(Math.random() * (wordForm.length + 1));
      const phones = Array.from(this.phonemeInventory);
      const newPhone = phones[Math.floor(Math.random() * phones.length)];
      wordForm.splice(idx, 0, newPhone);
    }
  }

  mutateWord(word: Word): boolean {
    if (word.form.length === 0) return false;
    
    const weights = CONFIG.MUTATE_OP_WEIGHTS;
    const rand = Math.random();
    let operation: string;
    
    if (rand < weights[0]) {
      operation = 'mutate';
    } else if (rand < weights[0] + weights[1]) {
      operation = 'delete';
    } else {
      operation = 'add';
    }
    
    if (operation === 'mutate') {
      const idx = Math.floor(Math.random() * word.form.length);
      const oldPhone = word.form[idx];
      
      if (oldPhone in PHONEMES) {
        const candidates = Array.from(this.phonemeInventory).filter(p => {
          if (!(p in PHONEMES)) return false;
          return featureDistance(PHONEMES[oldPhone], PHONEMES[p]) <= 3;
        });
        
        if (candidates.length > 0) {
          word.form[idx] = candidates[Math.floor(Math.random() * candidates.length)];
          word.generation++;
          return true;
        }
      }
    } else if (operation === 'delete' && word.form.length > 1) {
      const vowelPositions = word.form.map((p, i) => isSyllabic(p) ? i : -1).filter(i => i >= 0);
      
      if (vowelPositions.length > 1) {
        const idx = Math.floor(Math.random() * word.form.length);
        word.form.splice(idx, 1);
        word.generation++;
        return true;
      } else {
        const consonantPositions = word.form.map((p, i) => !isSyllabic(p) ? i : -1).filter(i => i >= 0);
        if (consonantPositions.length > 0) {
          const idx = consonantPositions[Math.floor(Math.random() * consonantPositions.length)];
          word.form.splice(idx, 1);
          word.generation++;
          return true;
        }
      }
    } else if (operation === 'add' && word.form.length < 6) {
      const idx = Math.floor(Math.random() * (word.form.length + 1));
      const phones = Array.from(this.phonemeInventory);
      const newPhone = phones[Math.floor(Math.random() * phones.length)];
      word.form.splice(idx, 0, newPhone);
      word.generation++;
      return true;
    }
    
    return false;
  }

  borrowWord(sourceLanguage: Language, meaning: string): boolean {
    const sourceWord = sourceLanguage.lexicon.get(meaning);
    if (!sourceWord) return false;
    
    const adaptedWord = this.adaptBorrowedWord(sourceWord, sourceLanguage);
    this.lexicon.set(meaning, adaptedWord);
    return true;
  }

  private adaptBorrowedWord(sourceWord: Word, donorLanguage: Language): Word {
    const adaptedForm: string[] = [];
    
    for (const phoneme of sourceWord.form) {
      if (this.phonemeInventory.has(phoneme)) {
        adaptedForm.push(phoneme);
      } else {
        // Find closest phoneme
        let closestPhone = phoneme;
        let minDistance = Infinity;
        
        for (const phone of this.phonemeInventory) {
          if (phoneme in PHONEMES && phone in PHONEMES) {
            const distance = featureDistance(PHONEMES[phoneme], PHONEMES[phone]);
            if (distance < minDistance) {
              minDistance = distance;
              closestPhone = phone;
            }
          }
        }
        
        adaptedForm.push(closestPhone);
      }
    }
    
    ensureHasVowel(adaptedForm);
    
    return {
      form: adaptedForm,
      meaning: sourceWord.meaning,
      originLanguageId: sourceWord.originLanguageId,
      borrowedFrom: donorLanguage.id,
      generation: sourceWord.generation + 1
    };
  }

  split(): Language {
    const daughter = new Language(this);
    this.children.push(daughter.id);
    return daughter;
  }

  getWordForMeaning(meaning: string): Word | undefined {
    return this.lexicon.get(meaning);
  }

  getVocabularySize(): number {
    return this.lexicon.size;
  }

  getPhonemeCount(): number {
    return this.phonemeInventory.size;
  }

  getVowels(): string[] {
    return Array.from(this.phonemeInventory).filter(p => isSyllabic(p)).sort();
  }

  getConsonants(): string[] {
    return Array.from(this.phonemeInventory).filter(p => !isSyllabic(p)).sort();
  }

  getStableColorSeed(): string {
    // Return a stable, unique string based on phoneme inventory for color generation
    const sortedPhonemes = Array.from(this.phonemeInventory).sort();
    
    // Use a mix of phonemes from different parts of the inventory for uniqueness
    const samplePhonemes: string[] = [];
    if (sortedPhonemes.length >= 1) samplePhonemes.push(sortedPhonemes[0]);
    if (sortedPhonemes.length >= 3) samplePhonemes.push(sortedPhonemes[Math.floor(sortedPhonemes.length / 3)]);
    if (sortedPhonemes.length >= 2) samplePhonemes.push(sortedPhonemes[Math.floor(sortedPhonemes.length / 2)]);
    if (sortedPhonemes.length >= 4) samplePhonemes.push(sortedPhonemes[Math.floor(sortedPhonemes.length * 2 / 3)]);
    if (sortedPhonemes.length >= 2) samplePhonemes.push(sortedPhonemes[sortedPhonemes.length - 1]);
    
    return samplePhonemes.join('');
  }
}