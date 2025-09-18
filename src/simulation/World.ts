import { Community, WorldStats } from '../types';
import { CONFIG } from '../config';

export function generateProceduralWorld(
  width: number, 
  height: number, 
  landProb: number, 
  islandBias: number, 
  smoothSteps: number
): boolean[][] {
  const cx = (width - 1) / 2;
  const cy = (height - 1) / 2;
  const maxRadius = Math.sqrt(cx * cx + cy * cy);
  
  // Initial random fill with radial bias
  let grid: boolean[][] = Array(height).fill(null).map(() => Array(width).fill(false));
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const radius = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / (maxRadius + 1e-9);
      const bias = (1 - radius) * islandBias;
      const probability = Math.max(0, Math.min(1, landProb + bias));
      grid[y][x] = Math.random() < probability;
    }
  }
  
  // Smooth with cellular automata
  for (let step = 0; step < smoothSteps; step++) {
    const newGrid: boolean[][] = Array(height).fill(null).map(() => Array(width).fill(false));
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const neighbors = countNeighbors(grid, x, y, width, height);
        
        if (grid[y][x]) {
          newGrid[y][x] = neighbors >= 3; // Survive if not too isolated
        } else {
          newGrid[y][x] = neighbors >= 5; // Birth in dense areas
        }
      }
    }
    
    grid = newGrid;
  }
  
  return grid;
}

function countNeighbors(grid: boolean[][], x: number, y: number, width: number, height: number): number {
  let count = 0;
  for (let dy = -1; dy <= 1; dy++) {
    for (let dx = -1; dx <= 1; dx++) {
      if (dx === 0 && dy === 0) continue;
      
      const nx = x + dx;
      const ny = y + dy;
      
      if (nx >= 0 && nx < width && ny >= 0 && ny < height && grid[ny][nx]) {
        count++;
      }
    }
  }
  return count;
}

export class World {
  public width: number;
  public height: number;
  public grid: (Community | null)[][];
  public communities: Community[];
  private neighborMap: Map<Community, Community[]>;
  private permutation: number[];

  constructor(mask: boolean[][]) {
    this.height = mask.length;
    this.width = mask[0]?.length || 0;
    this.grid = Array(this.height).fill(null).map(() => Array(this.width).fill(null));
    this.communities = [];
    this.neighborMap = new Map();
    this.permutation = [];

    // Create communities on land
    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        if (mask[y][x]) {
          const community: Community = {
            x,
            y,
            languageId: -1,
            population: 1.0,
            prestige: Math.random() * 0.8 + 0.1
          };
          this.grid[y][x] = community;
          this.communities.push(community);
        }
      }
    }

    this.buildNeighborMap();
    this.permutation = Array.from({ length: this.communities.length }, (_, i) => i);
  }

  private buildNeighborMap(): void {
    for (const community of this.communities) {
      const neighbors: Community[] = [];
      const directions = [[1, 0], [-1, 0], [0, 1], [0, -1]];
      
      for (const [dx, dy] of directions) {
        const nx = community.x + dx;
        const ny = community.y + dy;
        
        if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height) {
          const neighbor = this.grid[ny][nx];
          if (neighbor) {
            neighbors.push(neighbor);
          }
        }
      }
      
      this.neighborMap.set(community, neighbors);
    }
  }

  getCommunityAt(x: number, y: number): Community | null {
    if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
      return this.grid[y][x];
    }
    return null;
  }

  getNeighbors(community: Community): Community[] {
    return this.neighborMap.get(community) || [];
  }

  getRandomCommunity(): Community | null {
    if (this.communities.length === 0) return null;
    return this.communities[Math.floor(Math.random() * this.communities.length)];
  }

  getCommunitiesWithLanguage(languageId: number): Community[] {
    return this.communities.filter(c => c.languageId === languageId);
  }

  shuffleCommunities(): void {
    for (let i = this.permutation.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.permutation[i], this.permutation[j]] = [this.permutation[j], this.permutation[i]];
    }
  }

  getShuffledCommunities(): Community[] {
    return this.permutation.map(i => this.communities[i]);
  }

  calculateLanguageStats(): WorldStats {
    const languageCounts: Record<number, number> = {};
    let speakingCommunities = 0;

    for (const community of this.communities) {
      if (community.languageId >= 0) {
        languageCounts[community.languageId] = (languageCounts[community.languageId] || 0) + 1;
        speakingCommunities++;
      }
    }

    const counts = Object.values(languageCounts);
    const largestLanguage = counts.length > 0 ? Math.max(...counts) : 0;

    return {
      totalCommunities: this.communities.length,
      speakingCommunities,
      languages: Object.keys(languageCounts).length,
      largestLanguage,
      languageDistribution: languageCounts
    };
  }
}