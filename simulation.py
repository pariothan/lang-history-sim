"""
Main simulation engine for language evolution and spread
"""

import random
from typing import Dict, List, Set, Optional, Tuple
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
        
        # Contiguity tracking
        self.dirty_languages: Set[int] = set()
        
        # Initialize with starter languages
        self._initialize_languages()
        
        # Add additional seeding for better island population
        self._seed_distant_regions()
        
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
    
    def _seed_distant_regions(self):
        """Seed a few distant communities with existing languages"""
        empty_communities = [c for c in self.world.communities if c.language_id == -1]
        existing_languages = list(self.languages.values())
        
        if not existing_languages or not empty_communities:
            return
        
        # Only seed 2-3 additional communities to keep it minimal
        num_seeds = min(3, len(empty_communities), len(existing_languages))
        if num_seeds > 0:
            selected_communities = random.sample(empty_communities, num_seeds)
            for i, community in enumerate(selected_communities):
                # Assign to an existing language (cycling through them)
                language = existing_languages[i % len(existing_languages)]
                community.language_id = language.id
                self.dirty_languages.add(language.id)
    
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
            
            # Long-distance spread (maritime migration, trade routes, etc.)
            if random.random() < CONFIG.P_LONG_DISTANCE_SPREAD:
                self._attempt_long_distance_spread(community, language)
            
            # Prestige drift
            if random.random() < CONFIG.P_PRESTIGE_DRIFT:
                speaker_count = len(self.world.get_communities_with_language(language.id))
                language._drift_prestige(speaker_count)
        
        # Enforce language contiguity if enabled
        if CONFIG.CONTIGUITY_STRICT and self.tick_count % CONFIG.CONTIGUITY_ENFORCE_INTERVAL == 0:
            self._enforce_contiguity()
    
    def _apply_language_change(self, language: Language):
        """Apply internal language change"""
        # Apply phonological evolution with contact influence
        contact_languages = self._get_contact_languages(language.id)
        language.evolve(self.tick_count, contact_languages)
        
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
                # Track language changes for contiguity
                self.dirty_languages.add(source_community.language_id)
                if old_lang_id >= 0:
                    self.dirty_languages.add(old_lang_id)
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
        
        # Find connected components to choose a contiguous cluster
        components = self.world.find_connected_components(language.id)
        if len(components) <= 1:
            return  # Already contiguous, can't split meaningfully
        
        # Choose a smaller component to split off (not the largest)
        components.sort(key=len, reverse=True)
        split_candidates = components[1:]  # All except the largest
        
        if not split_candidates:
            return
        
        # Select a component to split off
        component_to_split = random.choice(split_candidates)
        
        # Only proceed if the component is substantial enough
        if len(component_to_split) < 2:
            return
        
        # Create daughter language
        daughter = language.split()
        self.languages[daughter.id] = daughter
        
        # Assign the entire connected component to daughter language
        for comm in component_to_split:
            comm.language_id = daughter.id
        
        # Track language changes for contiguity
        self.dirty_languages.add(language.id)
        self.dirty_languages.add(daughter.id)
    
    def _enforce_contiguity(self):
        """Enforce language contiguity by splitting non-contiguous languages"""
        # Work on a copy since we'll be modifying the dict
        languages_to_check = list(self.dirty_languages)
        self.dirty_languages.clear()
        
        for lang_id in languages_to_check:
            if lang_id not in self.languages:
                continue
                
            language = self.languages[lang_id]
            components = self.world.find_connected_components(lang_id)
            
            if len(components) <= 1:
                continue  # Language is contiguous or extinct
            
            # Keep the largest component as the original language
            largest_component = max(components, key=len)
            
            # Create new languages for other components
            for i, component in enumerate(components):
                if component == largest_component:
                    continue
                
                # Create a geographic branch
                branch = language.branch_geographic()
                self.languages[branch.id] = branch
                
                # Assign communities to the new language
                for community in component:
                    community.language_id = branch.id
    
    def _attempt_long_distance_spread(self, source_community: Community, language: Language):
        """Attempt long-distance spread to distant islands/regions"""
        # Only spread from communities that already have this language
        if source_community.language_id != language.id:
            return
            
        # Find distant communities
        distant_communities = self.world.get_distant_communities(
            source_community, 
            CONFIG.LONG_DISTANCE_MIN, 
            CONFIG.LONG_DISTANCE_RANGE
        )
        
        if not distant_communities:
            return
        
        # Calculate long-distance spread probability (much lower than local spread)
        spread_strength = language.prestige * source_community.prestige
        
        # Choose a random distant community
        target = random.choice(distant_communities)
        
        # Distance-based probability reduction (farther = less likely)
        distance = abs(target.x - source_community.x) + abs(target.y - source_community.y)
        distance_factor = max(0.1, 1.0 - (distance - CONFIG.LONG_DISTANCE_MIN) / CONFIG.LONG_DISTANCE_RANGE)
        
        # Lower probability for long-distance spread
        spread_prob = spread_strength * 0.03 * distance_factor
        
        if random.random() < spread_prob:
            # Long-distance language spread occurs
            old_lang_id = target.language_id
            target.language_id = language.id
            
            # Track language changes for contiguity
            self.dirty_languages.add(language.id)
            if old_lang_id >= 0:
                self.dirty_languages.add(old_lang_id)
            
            # If target had a different language, it might be lost
            if old_lang_id >= 0:
                remaining_speakers = self.world.get_communities_with_language(old_lang_id)
                if len(remaining_speakers) == 0:
                    # Language went extinct
                    if old_lang_id in self.languages:
                        del self.languages[old_lang_id]
    
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
    
    def _get_contact_languages(self, language_id: int) -> List[Language]:
        """Get languages in contact with the given language"""
        contact_languages = []
        
        # Find communities speaking this language
        speaking_communities = self.world.get_communities_with_language(language_id)
        contact_lang_ids = set()
        
        # Find neighboring languages
        for community in speaking_communities:
            neighbors = self.world.get_neighbors(community)
            for neighbor in neighbors:
                if neighbor.language_id != language_id and neighbor.language_id >= 0:
                    contact_lang_ids.add(neighbor.language_id)
        
        # Get Language objects for contact languages
        for lang_id in contact_lang_ids:
            if lang_id in self.languages:
                contact_languages.append(self.languages[lang_id])
        
        # Sort by prestige (most influential first)
        contact_languages.sort(key=lambda lang: lang.prestige, reverse=True)
        
        return contact_languages[:5]  # Limit to top 5 contact languages