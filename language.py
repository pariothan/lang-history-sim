"""
Language class representing a linguistic system with phonology and lexicon
"""

import random
import math
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass

from phonology import (
    PHONEMES, INVENTORY, IDX, is_syllabic, syllable_count, 
    ensure_has_vowel, compute_mutation_weights, compute_addition_weights
)
from vocabulary import get_vocabulary_subset
from config import CONFIG

@dataclass
class Word:
    """Represents a word with form, meaning, and history"""
    form: List[str]  # phoneme sequence
    meaning: str     # semantic content
    origin_lang_id: int  # language of origin
    borrowed_from: Optional[int] = None  # source language if borrowed
    generation: int = 0  # how many changes from original
    
    @property
    def string_form(self) -> str:
        return "".join(self.form)

class Language:
    """A linguistic system with phonology, lexicon, and evolution rules"""
    
    _next_id = 0
    
    def __init__(self, parent: Optional['Language'] = None):
        Language._next_id += 1
        self.id = Language._next_id
        self.generation = 0 if parent is None else parent.generation + 1
        
        # Phonological system
        if parent is None:
            self.phoneme_inventory = self._select_initial_phonemes()
        else:
            self.phoneme_inventory = parent.phoneme_inventory.copy()
            self._drift_phonemes()
        
        # Precompute phonological weights
        self._update_phonological_weights()
        
        # Lexicon
        self.lexicon: Dict[str, Word] = {}
        if parent is None:
            self._generate_initial_lexicon()
        else:
            self._inherit_lexicon(parent)
        
        # Language properties
        self.prestige = random.uniform(0.1, 0.9)
        self.conservatism = random.uniform(0.3, 0.8)  # resistance to change
        self.name = self._generate_name()
        
        # Evolution tracking
        self.parent_id = parent.id if parent else None
        self.children: List[int] = []
        
    def _select_initial_phonemes(self) -> Set[str]:
        """Select initial phoneme inventory using maximum dispersion"""
        vowels = [p for p in INVENTORY if is_syllabic(p)]
        consonants = [p for p in INVENTORY if not is_syllabic(p)]
        
        # Ensure minimum vowel system
        selected = set(random.sample(vowels, min(5, len(vowels))))
        
        # Add consonants using feature dispersion
        remaining = set(consonants)
        while len(selected) < random.randint(15, 25) and remaining:
            if not selected:
                next_phone = random.choice(list(remaining))
            else:
                # Choose phoneme most different from current inventory
                best_phone = max(remaining, 
                    key=lambda p: sum(self._feature_distance(p, s) for s in selected))
                next_phone = best_phone
            
            selected.add(next_phone)
            remaining.remove(next_phone)
            
        return selected
    
    def _drift_phonemes(self):
        """Apply phonological drift when splitting from parent"""
        # Small chance to lose or gain phonemes
        if random.random() < 0.1:
            available = set(INVENTORY) - self.phoneme_inventory
            if available and random.random() < 0.5:
                self.phoneme_inventory.add(random.choice(list(available)))
        
        if random.random() < 0.05 and len(self.phoneme_inventory) > 10:
            # Don't remove all vowels
            vowels_in_inv = [p for p in self.phoneme_inventory if is_syllabic(p)]
            if len(vowels_in_inv) > 2:
                to_remove = random.choice(list(self.phoneme_inventory))
                if not is_syllabic(to_remove) or len(vowels_in_inv) > 3:
                    self.phoneme_inventory.remove(to_remove)
    
    def _feature_distance(self, p1: str, p2: str) -> int:
        """Calculate feature distance between phonemes"""
        from phonology import DIST
        return DIST[IDX[p1]][IDX[p2]]
    
    def _update_phonological_weights(self):
        """Update mutation and addition weights for current inventory"""
        self.mut_weights = compute_mutation_weights(CONFIG.MUTATE_ALPHA)
        self.add_weights = compute_addition_weights(CONFIG.ADD_SWEET_DIST, CONFIG.ADD_SWEET_BETA)
    
    def _generate_initial_lexicon(self):
        """Generate initial vocabulary"""
        meanings = get_vocabulary_subset(120)
        for meaning in meanings:
            word_form = self._generate_word()
            word = Word(word_form, meaning, self.id)
            self.lexicon[meaning] = word
    
    def _inherit_lexicon(self, parent: 'Language'):
        """Inherit lexicon from parent with some changes"""
        for meaning, parent_word in parent.lexicon.items():
            # Copy with potential sound change
            new_form = parent_word.form.copy()
            if random.random() < 0.1:  # 10% chance of sound change
                self._apply_sound_change(new_form)
            
            word = Word(new_form, meaning, parent_word.origin_lang_id, 
                       generation=parent_word.generation + 1)
            self.lexicon[meaning] = word
    
    def _generate_word(self) -> List[str]:
        """Generate a phonologically valid word"""
        vowels = [p for p in self.phoneme_inventory if is_syllabic(p)]
        consonants = [p for p in self.phoneme_inventory if not is_syllabic(p)]
        
        if not vowels:
            vowels = ["a"]  # emergency vowel
        if not consonants:
            consonants = ["t"]  # emergency consonant
            
        syllables = random.randint(1, 3)
        word = []
        
        for _ in range(syllables):
            # Simple CV or CVC structure
            if consonants and random.random() < 0.8:
                word.append(random.choice(consonants))
            word.append(random.choice(vowels))
            if consonants and random.random() < 0.3:
                word.append(random.choice(consonants))
                
        return word
    
    def _generate_name(self) -> str:
        """Generate a name for this language"""
        name_form = self._generate_word()
        return "".join(name_form).title()
    
    def _apply_sound_change(self, word_form: List[str]):
        """Apply a random sound change to a word"""
        if not word_form:
            return
            
        change_type = random.choice(["substitute", "delete", "insert"])
        
        if change_type == "substitute" and word_form:
            idx = random.randint(0, len(word_form) - 1)
            old_phone = word_form[idx]
            if old_phone in self.phoneme_inventory:
                # Find similar phoneme
                candidates = [p for p in self.phoneme_inventory 
                            if self._feature_distance(old_phone, p) <= 2]
                if candidates:
                    word_form[idx] = random.choice(candidates)
        
        elif change_type == "delete" and len(word_form) > 1:
            # Don't delete if it would remove all vowels
            idx = random.randint(0, len(word_form) - 1)
            if not is_syllabic(word_form[idx]) or syllable_count(word_form) > 1:
                del word_form[idx]
        
        elif change_type == "insert":
            idx = random.randint(0, len(word_form))
            new_phone = random.choice(list(self.phoneme_inventory))
            word_form.insert(idx, new_phone)
    
    def mutate_word(self, word: Word) -> bool:
        """Mutate a word's phonological form"""
        if not word.form:
            return False
            
        op = random.choices(["mutate", "delete", "add"], 
                          weights=CONFIG.MUTATE_OP_WEIGHTS, k=1)[0]
        
        if op == "mutate":
            idx = random.randint(0, len(word.form) - 1)
            old_phone = word.form[idx]
            if old_phone in INVENTORY:
                old_idx = IDX[old_phone]
                weights = self.mut_weights[old_idx]
                new_idx = random.choices(range(len(INVENTORY)), weights=weights, k=1)[0]
                new_phone = INVENTORY[new_idx]
                if new_phone in self.phoneme_inventory:
                    word.form[idx] = new_phone
                    word.generation += 1
                    return True
        
        elif op == "delete" and len(word.form) > 1:
            # Preserve at least one vowel
            vowel_positions = [i for i, p in enumerate(word.form) if is_syllabic(p)]
            if len(vowel_positions) > 1:
                idx = random.randint(0, len(word.form) - 1)
                del word.form[idx]
                word.generation += 1
                return True
            else:
                # Only delete consonants
                cons_positions = [i for i, p in enumerate(word.form) if not is_syllabic(p)]
                if cons_positions:
                    idx = random.choice(cons_positions)
                    del word.form[idx]
                    word.generation += 1
                    return True
        
        elif op == "add" and len(word.form) < 6:
            anchor_idx = random.randint(0, len(word.form) - 1) if word.form else 0
            anchor = word.form[anchor_idx] if word.form else random.choice(list(self.phoneme_inventory))
            
            if anchor in INVENTORY:
                anchor_idx_global = IDX[anchor]
                weights = self.add_weights[anchor_idx_global]
                new_idx = random.choices(range(len(INVENTORY)), weights=weights, k=1)[0]
                new_phone = INVENTORY[new_idx]
                
                if new_phone in self.phoneme_inventory:
                    pos = random.randint(0, len(word.form))
                    word.form.insert(pos, new_phone)
                    word.generation += 1
                    return True
        
        return False
    
    def adapt_borrowed_word(self, source_word: Word) -> Word:
        """Adapt a borrowed word to this language's phonology"""
        adapted_form = []
        
        for phone in source_word.form:
            if phone in self.phoneme_inventory:
                adapted_form.append(phone)
            else:
                # Find closest phoneme in our inventory
                if phone in INVENTORY:
                    phone_idx = IDX[phone]
                    distances = [self._feature_distance(phone, p) for p in self.phoneme_inventory]
                    closest = min(self.phoneme_inventory, 
                                key=lambda p: self._feature_distance(phone, p))
                    adapted_form.append(closest)
                else:
                    # Fallback to random phoneme
                    adapted_form.append(random.choice(list(self.phoneme_inventory)))
        
        ensure_has_vowel(adapted_form)
        
        return Word(adapted_form, source_word.meaning, source_word.origin_lang_id,
                   borrowed_from=source_word.origin_lang_id, 
                   generation=source_word.generation + 1)
    
    def borrow_word(self, source_lang: 'Language', meaning: str) -> bool:
        """Borrow a word from another language"""
        if meaning not in source_lang.lexicon:
            return False
            
        source_word = source_lang.lexicon[meaning]
        adapted_word = self.adapt_borrowed_word(source_word)
        
        # Replace existing word
        self.lexicon[meaning] = adapted_word
        return True
    
    def split(self) -> 'Language':
        """Create a daughter language through splitting"""
        daughter = Language(parent=self)
        self.children.append(daughter.id)
        return daughter
    
    def get_word_for_meaning(self, meaning: str) -> Optional[Word]:
        """Get word for a given meaning"""
        return self.lexicon.get(meaning)
    
    def get_vocabulary_size(self) -> int:
        """Get size of lexicon"""
        return len(self.lexicon)
    
    def get_phoneme_count(self) -> int:
        """Get size of phoneme inventory"""
        return len(self.phoneme_inventory)
    
    def __str__(self) -> str:
        return f"Language({self.name}, ID={self.id}, Gen={self.generation})"