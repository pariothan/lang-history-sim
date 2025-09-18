import { LanguageEvolutionSimulation } from '../simulation/LanguageEvolutionSimulation';
import { Language } from '../simulation/Language';
import { Community } from '../types';
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
            fillColor = this.getLanguageColor(language);
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
    
    // Use stable cache based only on language ID
    if (this.stableColorCache.has(language.id)) {
      return this.stableColorCache.get(language.id)!;
    }
    
    // Generate color based on stable phoneme inventory
    const color = this.generateStableLanguageColor(language);
    this.stableColorCache.set(language.id, color);
    return color;
  }

  private generateStableLanguageColor(language: Language): string {
    // Use the first few phonemes from sorted inventory for stable color
    const sortedPhonemes = Array.from(language.phonemeInventory).sort();
    const samplePhonemes = sortedPhonemes.slice(0, 4); // Use first 4 phonemes
    
    if (samplePhonemes.length === 0) return '#666666';
    
    return this.wordToColor(samplePhonemes.join(''));
  }
  private wordToColor(word: string): string {
    if (!word) return '#666666';
    
    const phonemes = Array.from(word);
    let r = 0, g = 0, b = 0;
    let count = 0;
    
    for (const phoneme of phonemes) {
      if (!(phoneme in PHONEMES)) continue;
      
      const features = PHONEMES[phoneme];
      const featureVector = FEATURE_NAMES.map(name => features[name as keyof typeof features]);
      
      r += this.dotProduct(featureVector, RGB_PROJECTION[0]);
      g += this.dotProduct(featureVector, RGB_PROJECTION[1]);
      b += this.dotProduct(featureVector, RGB_PROJECTION[2]);
      count++;
    }
    
    if (count === 0) return '#666666';
    
    r /= count;
    g /= count;
    b /= count;
    
    // Squash to [0, 255] range
    const squash = (x: number): number => {
      x = Math.tanh(0.6 * x);
      x = 0.5 + 0.47 * x;
      return Math.max(0, Math.min(255, Math.floor(x * 255)));
    };
    
    const R = squash(r);
    const G = squash(g);
    const B = squash(b);
    
    return `rgb(${R}, ${G}, ${B})`;
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