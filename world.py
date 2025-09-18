"""
World generation and geographic modeling for language spread
"""

import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass

from config import CONFIG

def generate_procedural_world(w: int, h: int, land_prob: float, 
                            island_bias: float, smooth_steps: int) -> List[List[bool]]:
    """Generate a procedural world using cellular automata"""
    # Initial random fill with radial bias toward center
    cx, cy = (w-1)/2.0, (h-1)/2.0
    maxr = math.hypot(cx, cy)
    grid = [[False for _ in range(w)] for _ in range(h)]
    
    for y in range(h):
        for x in range(w):
            r = math.hypot(x - cx, y - cy) / (maxr + 1e-9)
            bias = (1.0 - r) * island_bias
            p = max(0.0, min(1.0, land_prob + bias))
            grid[y][x] = (random.random() < p)

    def count_neighbors8(xx: int, yy: int) -> int:
        c = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = xx + dx, yy + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx]:
                    c += 1
        return c

    # Smooth with cellular automata rules
    for _ in range(smooth_steps):
        newg = [[False for _ in range(w)] for _ in range(h)]
        for y in range(h):
            for x in range(w):
                n = count_neighbors8(x, y)
                if grid[y][x]:
                    newg[y][x] = (n >= 3)   # survive if not too isolated
                else:
                    newg[y][x] = (n >= 5)   # birth in dense areas
        grid = newg

    return grid

@dataclass
class Community:
    """A community that speaks a language"""
    x: int
    y: int
    language_id: int
    population: float = 1.0
    prestige: float = 0.5
    
    def __post_init__(self):
        self.prestige = random.uniform(0.1, 0.9)
    
    def __hash__(self):
        # Hash based on coordinates since they uniquely identify a community
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        if not isinstance(other, Community):
            return False
        return self.x == other.x and self.y == other.y

class World:
    """Geographic world with communities and language spread"""
    
    def __init__(self, mask: List[List[bool]]):
        self.height = len(mask)
        self.width = len(mask[0]) if self.height else 0
        self.grid: List[List[Optional[Community]]] = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]
        self.communities: List[Community] = []
        
        # Create communities on land
        for y in range(self.height):
            for x in range(self.width):
                if mask[y][x]:
                    community = Community(x, y, -1)  # -1 = no language yet
                    self.grid[y][x] = community
                    self.communities.append(community)
        
        # Build neighbor relationships
        self._build_neighbor_map()
        
        # Permutation array for efficient random iteration
        self._perm: List[int] = list(range(len(self.communities)))
    
    def _build_neighbor_map(self):
        """Build neighbor relationships between communities"""
        self.neighbors = {}
        for community in self.communities:
            neighbors = []
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = community.x + dx, community.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbor = self.grid[ny][nx]
                    if neighbor is not None:
                        neighbors.append(neighbor)
            self.neighbors[community] = neighbors
    
    def get_community_at(self, x: int, y: int) -> Optional[Community]:
        """Get community at coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
    
    def get_neighbors(self, community: Community) -> List[Community]:
        """Get neighboring communities"""
        return self.neighbors.get(community, [])
    
    def get_random_community(self) -> Optional[Community]:
        """Get a random community"""
        if not self.communities:
            return None
        return random.choice(self.communities)
    
    def get_communities_with_language(self, language_id: int) -> List[Community]:
        """Get all communities speaking a specific language"""
        return [c for c in self.communities if c.language_id == language_id]
    
    def shuffle_communities(self):
        """Shuffle the permutation for random iteration"""
        random.shuffle(self._perm)
    
    def get_shuffled_communities(self) -> List[Community]:
        """Get communities in random order"""
        return [self.communities[i] for i in self._perm]
    
    def calculate_language_stats(self) -> dict:
        """Calculate statistics about language distribution"""
        lang_counts = {}
        total_communities = len(self.communities)
        
        for community in self.communities:
            if community.language_id >= 0:
                lang_counts[community.language_id] = lang_counts.get(community.language_id, 0) + 1
        
        return {
            'total_communities': total_communities,
            'speaking_communities': sum(lang_counts.values()),
            'languages': len(lang_counts),
            'largest_language': max(lang_counts.values()) if lang_counts else 0,
            'language_distribution': lang_counts
        }