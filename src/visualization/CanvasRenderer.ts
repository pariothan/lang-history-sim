import { LanguageEvolutionSimulation } from '../simulation/LanguageEvolutionSimulation';
import { Language } from '../simulation/Language';
import { Community, MapMode } from '../types';
import { PHONEMES, RGB_PROJECTION, FEATURE_NAMES } from '../data/phonemes';
import { CONFIG } from '../config';

export class CanvasRenderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private simulation: LanguageEvolutionSimulation;
  private cellWidth: number = 0;
  private cellHeight: number = 0;
  private colorCache: Map<string, string> = new Map();
  private stableColorCache: Map<number, string> = new Map();
  private currentMapMode: MapMode = MapMode.LANGUAGES;
  
  public onLanguageClick?: (language: Language) => void;

  constructor(canvas: HTMLCanvasElement, simulation: LanguageEvolutionSimulation) {
    this.canvas = canvas;
    this.simulation = simulation;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Could not get 2D context');
    this.ctx = ctx;
    
    this.setupCanvas();
    this.setupEventListeners();
  }

  private setupCanvas(): void {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    
    this.ctx.scale(dpr, dpr);
    this.canvas.style.width = rect.width + 'px';
    this.canvas.style.height = rect.height + 'px';
    
    this.calculateCellSize();
  }

  private calculateCellSize(): void {
    const rect = this.canvas.getBoundingClientRect();
    this.cellWidth = rect.width / this.simulation.world.width;
    this.cellHeight = rect.height / this.simulation.world.height;
  }

  private setupEventListeners(): void {
    this.canvas.addEventListener('click', (event) => {
      const rect = this.canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      const gridX = Math.floor(x / this.cellWidth);
      const gridY = Math.floor(y / this.cellHeight);
      
      if (gridX >= 0 && gridX < this.simulation.world.width && 
          gridY >= 0 && gridY < this.simulation.world.height) {
        
        const community = this.simulation.world.getCommunityAt(gridX, gridY);
        if (community && community.languageId >= 0) {
          const language = this.simulation.getLanguageById(community.languageId);
          if (language && this.onLanguageClick) {
            this.onLanguageClick(language);
          }
        }
      }
    });
  }

  handleResize(): void {
    this.setupCanvas();
  }

  setMapMode(mode: MapMode): void {
    this.currentMapMode = mode;
    // Clear color cache when switching modes
    this.colorCache.clear();
  }

  render(): void {
    this.ctx.fillStyle = '#000000';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
    const world = this.simulation.world;
    
    // Draw communities
    for (let y = 0; y < world.height; y++) {
      for (let x = 0; x < world.width; x++) {
        const community = world.getCommunityAt(x, y);
        if (!community) continue;
        
        const x0 = x * this.cellWidth;
        const y0 = y * this.cellHeight;
        const x1 = x0 + this.cellWidth;
        const y1 = y0 + this.cellHeight;
        
        let fillColor = '#1a1a1a';
        let text = '';
        
        if (community.languageId >= 0) {
          const language = this.simulation.getLanguageById(community.languageId);
          if (language) {
            fillColor = this.getColorForMapMode(language, community);
            text = this.getDisplayText(language);
          }
        }
        
        // Draw cell
        this.ctx.fillStyle = fillColor;
        this.ctx.fillRect(x0, y0, this.cellWidth, this.cellHeight);
        
        // Draw text
        if (text && this.cellWidth > 8 && this.cellHeight > 8) {
          this.ctx.fillStyle = this.getTextColor(fillColor);
          
          // Calculate larger, more readable font size
          const fontSize = Math.max(6, Math.min(
            this.cellWidth * 0.6, 
            this.cellHeight * 0.5, 
            18
          ));
          
          this.ctx.font = `bold ${fontSize}px 'Arial', 'Helvetica', sans-serif`;
          this.ctx.textAlign = 'center';
          this.ctx.textBaseline = 'middle';
          
          // Add stronger text shadow for better readability
          this.ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
          this.ctx.shadowBlur = 3;
          this.ctx.shadowOffsetX = 1;
          this.ctx.shadowOffsetY = 1;
          
          this.ctx.fillText(text, x0 + this.cellWidth / 2, y0 + this.cellHeight / 2);
          
          // Reset shadow
          this.ctx.shadowColor = 'transparent';
          this.ctx.shadowBlur = 0;
          this.ctx.shadowOffsetX = 0;
          this.ctx.shadowOffsetY = 0;
        }
      }
    }
    
    // Draw boundaries
    if (CONFIG.DRAW_BOUNDARIES) {
      this.drawLanguageBoundaries();
    }
  }

  private getDisplayText(language: Language): string {
    // Show more text based on cell size - be more generous with space
    if (this.cellWidth > 30 && this.cellHeight > 20) {
      return language.name.length > 8 ? language.name.substring(0, 8) : language.name;
    } else if (this.cellWidth > 20 && this.cellHeight > 15) {
      return language.name.substring(0, 6);
    } else if (this.cellWidth > 12 && this.cellHeight > 10) {
      return language.name.substring(0, 4);
    } else {
      return language.name.substring(0, 2);
    }
  }

  private drawLanguageBoundaries(): void {
    this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.6)';
    this.ctx.lineWidth = Math.max(1, Math.min(this.cellWidth, this.cellHeight) * 0.05);
    
    const world = this.simulation.world;
    
    for (let y = 0; y < world.height; y++) {
      for (let x = 0; x < world.width; x++) {
        const community = world.getCommunityAt(x, y);
        if (!community || community.languageId < 0) continue;
        
        // Check right neighbor
        const rightNeighbor = world.getCommunityAt(x + 1, y);
        if (rightNeighbor && rightNeighbor.languageId !== community.languageId) {
          const lineX = (x + 1) * this.cellWidth;
          this.ctx.beginPath();
          this.ctx.moveTo(lineX, y * this.cellHeight);
          this.ctx.lineTo(lineX, (y + 1) * this.cellHeight);
          this.ctx.stroke();
        }
        
        // Check bottom neighbor
        const bottomNeighbor = world.getCommunityAt(x, y + 1);
        if (bottomNeighbor && bottomNeighbor.languageId !== community.languageId) {
          const lineY = (y + 1) * this.cellHeight;
          this.ctx.beginPath();
          this.ctx.moveTo(x * this.cellWidth, lineY);
          this.ctx.lineTo((x + 1) * this.cellWidth, lineY);
          this.ctx.stroke();
        }
      }
    }
  }

  getLanguageColor(language: Language | undefined): string {
    if (!language) return '#333333';
    
    // This method is used by external components, default to language mode
    return this.getColorForMapMode(language, null);
  }

  private getColorForMapMode(language: Language, community: Community | null): string {
    if (!language) return '#333333';
    
    const cacheKey = `${this.currentMapMode}_${language.id}`;
    if (this.colorCache.has(cacheKey)) {
      return this.colorCache.get(cacheKey)!;
    }
    
    let color: string;
    
    switch (this.currentMapMode) {
      case MapMode.LANGUAGES:
        color = this.generateLanguageColor(language);
        break;
      case MapMode.PRESTIGE:
        color = this.generatePrestigeColor(language);
        break;
      case MapMode.AGE:
        color = this.generateAgeColor(language);
        break;
      case MapMode.PHONEME_COUNT:
        color = this.generatePhonemeCountColor(language);
        break;
      case MapMode.VOCABULARY_SIZE:
        color = this.generateVocabularyColor(language);
        break;
      case MapMode.LANGUAGE_FAMILIES:
        color = this.generateFamilyColor(language);
        break;
      default:
        color = this.generateLanguageColor(language);
    }
    
    this.colorCache.set(cacheKey, color);
    return color;
  }

  private generateLanguageColor(language: Language): string {
    // Use language ID for stable caching
    if (this.stableColorCache.has(language.id)) {
      return this.stableColorCache.get(language.id)!;
    }
    
    // Create a deterministic but diverse color based on language characteristics
    const seed = this.createLanguageSeed(language);
    const color = this.generateColorFromSeed(seed);
    this.stableColorCache.set(language.id, color);
    return color;
  }
  
  private createLanguageSeed(language: Language): number {
    // Create a stable seed from language characteristics
    const phonemes = Array.from(language.phonemeInventory).sort();
    const phonemeString = phonemes.join('');
    
    // Add language ID for uniqueness
    const seedString = `${phonemeString}_${language.id}_${language.generation}`;
    
    // Create hash
    let hash = 0;
    for (let i = 0; i < seedString.length; i++) {
      const char = seedString.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash);
  }
  
  private generateColorFromSeed(seed: number): string {
    // Use multiple hash functions to generate RGB values
    const r = this.hashToRange(seed * 1.1, 80, 255);
    const g = this.hashToRange(seed * 2.3, 80, 255);
    const b = this.hashToRange(seed * 3.7, 80, 255);
    
    // Ensure colors are vibrant by boosting the dominant component
    const max = Math.max(r, g, b);
    const boostedR = r === max ? Math.min(255, r * 1.2) : r;
    const boostedG = g === max ? Math.min(255, g * 1.2) : g;
    const boostedB = b === max ? Math.min(255, b * 1.2) : b;
    
    return `rgb(${Math.floor(boostedR)}, ${Math.floor(boostedG)}, ${Math.floor(boostedB)})`;
  }
  
  private hashToRange(seed: number, min: number, max: number): number {
    // Create a pseudo-random number in range [min, max] from seed
    const hash = Math.sin(seed) * 10000;
    const normalized = hash - Math.floor(hash);
    return min + normalized * (max - min);
  }

  private generatePrestigeColor(language: Language): string {
    // Red = high prestige, Blue = low prestige
    const prestige = language.prestige;
    const red = Math.floor(80 + prestige * 175);
    const blue = Math.floor(80 + (1 - prestige) * 175);
    const green = Math.floor(60 + Math.random() * 40); // Some variation
    return `rgb(${red}, ${green}, ${blue})`;
  }

  private generateAgeColor(language: Language): string {
    // Purple = old (high generation), Green = young (low generation)
    const maxGeneration = 10; // Assume max generation for scaling
    const ageRatio = Math.min(language.generation / maxGeneration, 1);
    
    const red = Math.floor(80 + ageRatio * 120);
    const green = Math.floor(80 + (1 - ageRatio) * 175);
    const blue = Math.floor(80 + ageRatio * 175);
    return `rgb(${red}, ${green}, ${blue})`;
  }

  private generatePhonemeCountColor(language: Language): string {
    // Orange = many phonemes, Cyan = few phonemes
    const phonemeCount = language.getPhonemeCount();
    const minPhonemes = 10;
    const maxPhonemes = 30;
    const ratio = Math.min(Math.max((phonemeCount - minPhonemes) / (maxPhonemes - minPhonemes), 0), 1);
    
    const red = Math.floor(80 + ratio * 175);
    const green = Math.floor(80 + ratio * 100);
    const blue = Math.floor(80 + (1 - ratio) * 175);
    return `rgb(${red}, ${green}, ${blue})`;
  }

  private generateVocabularyColor(language: Language): string {
    // Yellow = large vocabulary, Magenta = small vocabulary
    const vocabSize = language.getVocabularySize();
    const minVocab = 50;
    const maxVocab = 200;
    const ratio = Math.min(Math.max((vocabSize - minVocab) / (maxVocab - minVocab), 0), 1);
    
    const red = Math.floor(80 + ratio * 175);
    const green = Math.floor(80 + ratio * 175);
    const blue = Math.floor(80 + (1 - ratio) * 100);
    return `rgb(${red}, ${green}, ${blue})`;
  }

  private generateFamilyColor(language: Language): string {
    // Same color for language families (based on root ancestor)
    const rootId = this.findRootLanguage(language);
    const seed = rootId * 12345; // Deterministic seed based on root
    return this.generateColorFromSeed(seed);
  }

  private findRootLanguage(language: Language): number {
    // For now, use the language's parent chain to find root
    // In a full implementation, you'd traverse up the parent chain
    return language.parentId || language.id;
  }

  private dotProduct(a: number[], b: number[]): number {
    return a.reduce((sum, val, i) => sum + val * b[i], 0);
  }

  private getTextColor(backgroundColor: string): string {
    // Extract RGB values from color string
    const match = backgroundColor.match(/rgb\((\d+), (\d+), (\d+)\)/);
    if (!match) return '#ffffff';
    
    const r = parseInt(match[1]);
    const g = parseInt(match[2]);
    const b = parseInt(match[3]);
    
    // Calculate luminance
    const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    
    return luminance > 135 ? '#000000' : '#ffffff';
  }
}