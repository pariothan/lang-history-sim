import { World, generateProceduralWorld } from './World';
import { Language } from './Language';
import { Community } from '../types';
import { CONFIG } from '../config';
import { CORE_VOCABULARY } from '../data/vocabulary';

export class LanguageEvolutionSimulation {
  public world: World;
  public languages: Map<number, Language>;
  public tickCount: number;

  constructor() {
    // Generate world
    const mask = generateProceduralWorld(
      CONFIG.GRID_W,
      CONFIG.GRID_H,
      CONFIG.LAND_PROB_INIT,
      CONFIG.ISLAND_BIAS,
      CONFIG.SMOOTH_STEPS
    );
    
    this.world = new World(mask);
    this.languages = new Map();
    this.tickCount = 0;
    
    this.initializeLanguages();
  }

  private initializeLanguages(): void {
    // Create initial languages
    for (const starterWord of CONFIG.STARTER_WORDS) {
      const language = new Language();
      this.languages.set(language.id, language);
      
      // Place in random community
      const community = this.world.getRandomCommunity();
      if (community) {
        community.languageId = language.id;
        
        // Add starter word to vocabulary if meaning exists
        if (CORE_VOCABULARY.length > 0) {
          const meaning = CORE_VOCABULARY[Math.floor(Math.random() * CORE_VOCABULARY.length)];
          if (!language.lexicon.has(meaning)) {
            language.lexicon.set(meaning, {
              form: starterWord,
              meaning,
              originLanguageId: language.id,
              generation: 0
            });
          }
        }
      }
    }
  }

  step(): void {
    this.tickCount++;
    
    // Shuffle communities for random processing order
    this.world.shuffleCommunities();
    
    // Process each community
    for (const community of this.world.getShuffledCommunities()) {
      if (community.languageId < 0) continue;
      
      const language = this.languages.get(community.languageId);
      if (!language) continue;
      
      // Language internal change
      this.applyLanguageChange(language);
      
      // Language spread
      if (Math.random() < CONFIG.P_SPREAD) {
        this.attemptLanguageSpread(community, language);
      }
      
      // Word borrowing
      if (Math.random() < CONFIG.P_BORROW) {
        this.attemptWordBorrowing(community, language);
      }
      
      // Language splitting
      if (Math.random() < CONFIG.P_LANGUAGE_SPLIT) {
        this.attemptLanguageSplit(community, language);
      }
    }
  }

  private applyLanguageChange(language: Language): void {
    // Mutate random words
    if (Math.random() < CONFIG.P_MUTATE) {
      const words = Array.from(language.lexicon.values());
      if (words.length > 0) {
        const word = words[Math.floor(Math.random() * words.length)];
        language.mutateWord(word);
      }
    }
  }

  private attemptLanguageSpread(sourceCommunity: Community, language: Language): void {
    const neighbors = this.world.getNeighbors(sourceCommunity);
    if (neighbors.length === 0) return;
    
    // Calculate spread probability based on prestige
    const spreadStrength = language.prestige * sourceCommunity.prestige;
    
    for (const neighbor of neighbors) {
      if (neighbor.languageId === sourceCommunity.languageId) continue;
      
      const spreadProb = spreadStrength * 0.1;
      
      if (Math.random() < spreadProb) {
        const oldLanguageId = neighbor.languageId;
        neighbor.languageId = sourceCommunity.languageId;
        
        // Check if old language went extinct
        if (oldLanguageId >= 0) {
          const remainingSpeakers = this.world.getCommunitiesWithLanguage(oldLanguageId);
          if (remainingSpeakers.length === 0) {
            this.languages.delete(oldLanguageId);
          }
        }
        
        return; // Only spread to one neighbor per step
      }
    }
  }

  private attemptWordBorrowing(community: Community, language: Language): void {
    const neighbors = this.world.getNeighbors(community);
    if (neighbors.length === 0) return;
    
    // Find neighbors with different languages
    const sourceNeighbors = neighbors.filter(n => 
      n.languageId !== community.languageId && n.languageId >= 0
    );
    
    if (sourceNeighbors.length === 0) return;
    
    // Choose source based on prestige
    const sourceCommunity = sourceNeighbors.reduce((best, current) => 
      current.prestige > best.prestige ? current : best
    );
    
    const sourceLanguage = this.languages.get(sourceCommunity.languageId);
    if (!sourceLanguage) return;
    
    // Borrow a random word
    const sourceMeanings = Array.from(sourceLanguage.lexicon.keys());
    if (sourceMeanings.length > 0) {
      const meaning = sourceMeanings[Math.floor(Math.random() * sourceMeanings.length)];
      if (Math.random() < CONFIG.PRESTIGE_THRESHOLD * sourceCommunity.prestige) {
        language.borrowWord(sourceLanguage, meaning);
      }
    }
  }

  private attemptLanguageSplit(community: Community, language: Language): void {
    // Only split if language has enough speakers
    const speakers = this.world.getCommunitiesWithLanguage(language.id);
    if (speakers.length < 5) return;
    
    // Create daughter language
    const daughter = language.split();
    this.languages.set(daughter.id, daughter);
    
    // Assign some speakers to daughter language
    const splitSize = Math.floor(Math.random() * Math.min(3, Math.floor(speakers.length / 2))) + 1;
    const communitiesToSplit = speakers.sort(() => Math.random() - 0.5).slice(0, splitSize);
    
    for (const comm of communitiesToSplit) {
      comm.languageId = daughter.id;
    }
  }

  getLanguageById(languageId: number): Language | undefined {
    return this.languages.get(languageId);
  }

  getAllLanguages(): Language[] {
    return Array.from(this.languages.values());
  }

  getCommunityLanguageName(community: Community): string {
    if (community.languageId < 0) return '';
    const language = this.languages.get(community.languageId);
    return language?.name || `Lang${community.languageId}`;
  }
}