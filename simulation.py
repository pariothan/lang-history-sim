"""
Main simulation engine for language evolution and spread
"""

import random
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from config import CONFIG
from language import Language, Word
from world import World, Community
from vocabulary import CORE_VOCABULARY

class LanguageEvolutionSimulation:
    """Main simulation managing languages, communities, and evolution"""
    
    def __init__(self, world: World):
        self.world = world
        self.languages: Dict[int, Language] = {}
        self.tick_count = 0
        
        # Initialize with starter languages
        self._initialize_languages()
        
        # Statistics tracking
        self.stats_history = []
        
    def _initialize_languages(self):
        """Initialize the simulation with starter languages"""
        # Create initial languages
        for starter_word in CONFIG.STARTER_WORDS:
            lang = Language()
            self.languages[lang.id] = lang
            
            # Place in random community
            community = self.world.get_random_community()
            if community:
                community.language_id = lang.id
                # Add the starter word to vocabulary if meaning exists
                if len(CORE_VOCABULARY) > 0:
                    meaning = random.choice(CORE_VOCABULARY)
                    starter_word_obj = Word(starter_word, meaning, lang.id)
                    lang.lexicon[meaning] = starter_word_obj
    
    def step(self):
        """Execute one simulation step"""
        self.tick_count += 1
        
        # Print statistics periodically
        if CONFIG.PRINT_STATS and (self.tick_count % CONFIG.STATS_INTERVAL == 0):
            self._print_statistics()
        
        # Shuffle communities for random processing order
        self.world.shuffle_communities()
        
        # Process each community
        for community in self.world.get_shuffled_communities():
            if community.language_id < 0:
                continue
                
            language = self.languages.get(community.language_id)
            if not language:
                continue
            
            # Language internal change
            self._apply_language_change(language)
            
            # Language spread
            if random.random() < CONFIG.P_SPREAD:
                self._attempt_language_spread(community, language)
            
            # Word borrowing
            if random.random() < CONFIG.P_BORROW:
                self._attempt_word_borrowing(community, language)
            
            # Language splitting
            if random.random() < CONFIG.P_LANGUAGE_SPLIT:
                self._attempt_language_split(community, language)
    
    def _apply_language_change(self, language: Language):
        """Apply internal language change"""
        # Mutate random words
        if random.random() < CONFIG.P_MUTATE:
            meanings = list(language.lexicon.keys())
            if meanings:
                meaning = random.choice(meanings)
                word = language.lexicon[meaning]
                language.mutate_word(word)
    
    def _attempt_language_spread(self, source_community: Community, language: Language):
        """Attempt to spread language to neighboring communities"""
        neighbors = self.world.get_neighbors(source_community)
        if not neighbors:
            return
        
        # Calculate spread probability based on prestige
        spread_strength = language.prestige * source_community.prestige
        
        for neighbor in neighbors:
            if neighbor.language_id == source_community.language_id:
                continue
                
            # Distance-based probability (already neighbors, so base probability)
            spread_prob = spread_strength * 0.1
            
            if random.random() < spread_prob:
                # Language spreads
                old_lang_id = neighbor.language_id
                neighbor.language_id = source_community.language_id
                
                # If neighbor had a different language, it might be lost
                if old_lang_id >= 0:
                    remaining_speakers = self.world.get_communities_with_language(old_lang_id)
                    if len(remaining_speakers) == 0:
                        # Language went extinct
                        if old_lang_id in self.languages:
                            del self.languages[old_lang_id]
                
                return  # Only spread to one neighbor per step
    
    def _attempt_word_borrowing(self, community: Community, language: Language):
        """Attempt to borrow words from neighboring languages"""
        neighbors = self.world.get_neighbors(community)
        if not neighbors:
            return
        
        # Find neighbors with different languages
        source_neighbors = [n for n in neighbors 
                          if n.language_id != community.language_id and n.language_id >= 0]
        
        if not source_neighbors:
            return
        
        # Choose source based on prestige
        source_community = max(source_neighbors, key=lambda c: c.prestige)
        source_language = self.languages.get(source_community.language_id)
        
        if not source_language:
            return
        
        # Borrow a random word
        source_meanings = list(source_language.lexicon.keys())
        if source_meanings:
            meaning = random.choice(source_meanings)
            if random.random() < CONFIG.PRESTIGE_THRESHOLD * source_community.prestige:
                language.borrow_word(source_language, meaning)
    
    def _attempt_language_split(self, community: Community, language: Language):
        """Attempt to split a language into daughter languages"""
        # Only split if language has enough speakers
        speakers = self.world.get_communities_with_language(language.id)
        if len(speakers) < 5:
            return
        
        # Create daughter language
        daughter = language.split()
        self.languages[daughter.id] = daughter
        
        # Assign some speakers to daughter language
        split_size = random.randint(1, min(3, len(speakers) // 2))
        communities_to_split = random.sample(speakers, split_size)
        
        for comm in communities_to_split:
            comm.language_id = daughter.id
    
    def _print_statistics(self):
        """Print simulation statistics"""
        world_stats = self.world.calculate_language_stats()
        
        print(f"\n=== Tick {self.tick_count} ===")
        print(f"Communities: {world_stats['speaking_communities']}/{world_stats['total_communities']}")
        print(f"Languages: {world_stats['languages']}")
        print(f"Largest language: {world_stats['largest_language']} speakers")
        
        # Show top languages
        if world_stats['language_distribution']:
            sorted_langs = sorted(world_stats['language_distribution'].items(), 
                                key=lambda x: x[1], reverse=True)
            
            print(f"Top {min(CONFIG.LEADERBOARD_TOPK, len(sorted_langs))} languages:")
            for i, (lang_id, count) in enumerate(sorted_langs[:CONFIG.LEADERBOARD_TOPK]):
                language = self.languages.get(lang_id)
                name = language.name if language else f"Lang{lang_id}"
                print(f"  {i+1}. {name}: {count} speakers")
        
        # Show sample words
        if self.languages:
            sample_lang = random.choice(list(self.languages.values()))
            sample_words = list(sample_lang.lexicon.items())[:3]
            print(f"Sample words from {sample_lang.name}:")
            for meaning, word in sample_words:
                print(f"  {word.string_form} = '{meaning}'")
    
    def get_language_by_id(self, lang_id: int) -> Optional[Language]:
        """Get language by ID"""
        return self.languages.get(lang_id)
    
    def get_all_languages(self) -> List[Language]:
        """Get all active languages"""
        return list(self.languages.values())
    
    def get_community_language_name(self, community: Community) -> str:
        """Get the name of the language spoken by a community"""
        if community.language_id < 0:
            return ""
        language = self.languages.get(community.language_id)
        return language.name if language else f"Lang{community.language_id}"