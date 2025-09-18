"""
Language class representing a linguistic system with phonology and lexicon
"""

import random
import math
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass

from phonology import (
    PHONEMES, INVENTORY, IDX, is_syllabic, syllable_count, 
    ensure_has_vowel, compute_mutation_weights, compute_addition_weights,
    PhonotacticConstraints, PhonologicalGenerator, get_default_constraints,
    get_complex_constraints, get_mora_constraints, PhonologicalRuleSet, 
    repair_phonotactics
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
            self.phonotactic_constraints = self._select_initial_constraints()
        else:
            self.phoneme_inventory = parent.phoneme_inventory.copy()
            # Deep copy constraints to avoid sharing references
            import copy
            self.phonotactic_constraints = copy.deepcopy(parent.phonotactic_constraints)
            self._drift_phonemes()
            self._drift_constraints()
        
        # Initialize phonological generator
        self.phonological_generator = PhonologicalGenerator(
            self.phoneme_inventory, self.phonotactic_constraints)
        
        # Phonological rules and evolution
        self.phonological_rules = PhonologicalRuleSet()
        self.epenthetic_vowel = random.choice(["ə", "i", "a"])  # Language-specific epenthetic vowel
        self.last_evolution_tick = 0
        
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
    
    def _select_initial_constraints(self) -> PhonotacticConstraints:
        """Select initial phonotactic constraints for the language"""
        constraint_types = [get_default_constraints, get_complex_constraints, get_mora_constraints]
        weights = [0.5, 0.3, 0.2]  # Favor simpler systems
        constraint_func = random.choices(constraint_types, weights=weights, k=1)[0]
        return constraint_func()
    
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
        
        # Update phonological generator after inventory changes
        self.phonological_generator = PhonologicalGenerator(
            self.phoneme_inventory, self.phonotactic_constraints)
    
    def _drift_constraints(self):
        """Apply small changes to phonotactic constraints when splitting from parent"""
        # Small chance to modify constraints
        if random.random() < 0.15:  # 15% chance of constraint change
            
            # Modify syllable type preferences slightly
            if random.random() < 0.5:
                self._modify_syllable_preferences()
            
            # Change gemination settings
            if random.random() < 0.3:
                self.phonotactic_constraints.allow_gemination = not self.phonotactic_constraints.allow_gemination
                if self.phonotactic_constraints.allow_gemination:
                    self.phonotactic_constraints.gemination_probability = random.uniform(0.02, 0.15)
            
            # Modify word length preferences
            if random.random() < 0.4:
                self.phonotactic_constraints.preferred_syllables = random.randint(1, 4)
                self.phonotactic_constraints.max_syllables = max(
                    self.phonotactic_constraints.preferred_syllables + 1, 
                    self.phonotactic_constraints.max_syllables
                )
        
        # Update phonological generator with new constraints
        self.phonological_generator = PhonologicalGenerator(
            self.phoneme_inventory, self.phonotactic_constraints)
    
    def _modify_syllable_preferences(self):
        """Slightly modify syllable type preferences"""
        from phonology import SyllableType
        
        # Add some randomness to syllable preferences
        current_prefs = self.phonotactic_constraints.syllable_types
        new_prefs = current_prefs.copy()
        
        # Randomly increase or decrease some preferences
        for syll_type in current_prefs:
            if random.random() < 0.3:
                change = random.uniform(-0.1, 0.1)
                new_prefs[syll_type] = max(0.01, current_prefs[syll_type] + change)
        
        # Normalize to sum to 1.0
        total = sum(new_prefs.values())
        if total > 0:
            for syll_type in new_prefs:
                new_prefs[syll_type] /= total
        
        self.phonotactic_constraints.syllable_types = new_prefs
    
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
        """Generate a phonologically valid word using constraints"""
        return self.phonological_generator.generate_word()
    
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
        """Borrow a word from another language using advanced adaptation"""
        if meaning not in source_lang.lexicon:
            return False
            
        source_word = source_lang.lexicon[meaning]
        adapted_word = self.borrow_word_advanced(source_word, source_lang)
        
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
    
    def get_phonotactic_info(self) -> Dict[str, Any]:
        """Get information about phonotactic constraints for display"""
        constraints = self.phonotactic_constraints
        
        info = {
            'syllable_types': constraints.syllable_types,
            'word_length': {
                'min_syllables': constraints.min_syllables,
                'max_syllables': constraints.max_syllables,
                'preferred_syllables': constraints.preferred_syllables
            },
            'allowed_codas': list(constraints.allowed_codas),
            'onset_clusters': len(constraints.onset_clusters.allowed_combinations),
            'coda_clusters': len(constraints.coda_clusters.allowed_combinations),
            'gemination': {
                'allowed': constraints.allow_gemination,
                'probability': constraints.gemination_probability if constraints.allow_gemination else 0,
                'geminable_consonants': list(constraints.geminable_consonants) if constraints.allow_gemination else []
            },
            'mora_based': constraints.use_mora,
            'forbidden_sequences': len(constraints.forbidden_sequences)
        }
        
        if constraints.use_mora:
            info['mora_constraints'] = {
                'min_mora': constraints.min_mora,
                'max_mora': constraints.max_mora
            }
        
        return info
    
    def get_constraint_summary(self) -> str:
        """Get a human-readable summary of phonotactic constraints"""
        constraints = self.phonotactic_constraints
        
        # Determine system type
        if constraints.use_mora:
            system_type = "Mora-based"
        elif any(len(cluster) > 1 for cluster in constraints.onset_clusters.allowed_combinations):
            system_type = "Complex (with consonant clusters)"
        else:
            system_type = "Simple (basic syllable structure)"
        
        # Most common syllable types
        top_syllables = sorted(constraints.syllable_types.items(), 
                             key=lambda x: x[1], reverse=True)[:3]
        syll_summary = ", ".join([f"{syll.value} ({prob:.1%})" 
                                for syll, prob in top_syllables])
        
        parts = [
            f"System: {system_type}",
            f"Common syllables: {syll_summary}",
            f"Word length: {constraints.min_syllables}-{constraints.max_syllables} syllables"
        ]
        
        if constraints.allow_gemination:
            parts.append(f"Gemination: {constraints.gemination_probability:.1%} chance")
        
        if constraints.forbidden_sequences:
            parts.append(f"Forbidden sequences: {len(constraints.forbidden_sequences)}")
        
        return "; ".join(parts)
    
    def evolve(self, tick: int, contact_languages: Optional[List['Language']] = None):
        """Evolve the language's phonological system over time"""
        # Don't evolve too frequently
        if tick - self.last_evolution_tick < 50:
            return
        
        self.last_evolution_tick = tick
        
        # Calculate contact pressure from other languages
        contact_pressure = 0.0
        if contact_languages:
            for lang in contact_languages[:3]:  # Limit influence to top 3 languages
                # More prestigious languages have more influence
                influence = lang.prestige / (self.prestige + 0.1)
                contact_pressure += influence * 0.1
        
        contact_pressure = min(contact_pressure, 0.5)  # Cap at 50%
        
        # Evolve phonological rules
        self.phonological_rules.evolve(tick, self.conservatism, contact_pressure)
        
        # Apply phonological changes to a sample of the lexicon
        self._apply_sound_changes(tick)
        
        # Evolve constraints based on contact and internal drift
        self._evolve_constraints(tick, contact_pressure)
        
        # Update phonological generator if constraints changed
        self.phonological_generator = PhonologicalGenerator(
            self.phoneme_inventory, self.phonotactic_constraints)
    
    def _apply_sound_changes(self, tick: int):
        """Apply active phonological rules to a sample of words"""
        if not self.phonological_rules.get_active_rules(tick):
            return
        
        # Apply changes to a random sample of words to avoid computational explosion
        sample_size = min(20, len(self.lexicon))
        if sample_size == 0:
            return
        
        sample_meanings = random.sample(list(self.lexicon.keys()), sample_size)
        
        for meaning in sample_meanings:
            word = self.lexicon[meaning]
            old_form = word.form[:]
            
            # Apply all active rules
            new_form = self.phonological_rules.apply_rules(word.form, tick)
            
            if new_form != old_form:
                # Repair phonotactic violations after sound changes
                repaired_form = repair_phonotactics(
                    new_form, self.phonotactic_constraints, self.epenthetic_vowel
                )
                
                # Create evolved word
                evolved_word = Word(
                    form=repaired_form,
                    meaning=meaning,
                    origin_lang_id=word.origin_lang_id,
                    borrowed_from=word.borrowed_from,
                    generation=word.generation + 1
                )
                self.lexicon[meaning] = evolved_word
    
    def _evolve_constraints(self, tick: int, contact_pressure: float):
        """Evolve phonotactic constraints over time"""
        # Gradually shift syllable structure preferences
        if random.random() < 0.05:  # 5% chance per evolution cycle
            self._shift_syllable_preferences(contact_pressure)
        
        # Expand or contract consonant clusters
        if random.random() < 0.03:
            self._evolve_clusters(contact_pressure)
        
        # Change coda restrictions
        if random.random() < 0.04:
            self._evolve_codas(contact_pressure)
    
    def _shift_syllable_preferences(self, contact_pressure: float):
        """Shift syllable structure preferences"""
        # Get current preferences
        syllable_types = self.phonotactic_constraints.syllable_types
        
        # Apply small random changes
        for syll_type in syllable_types:
            change = random.uniform(-0.05, 0.05) * (1.0 - self.conservatism)
            # Contact pressure can bias toward more complex structures
            if contact_pressure > 0.2 and syll_type.value in ["CCV", "CCVC", "CVCC"]:
                change += contact_pressure * 0.1
            
            syllable_types[syll_type] = max(0.01, syllable_types[syll_type] + change)
        
        # Renormalize
        total = sum(syllable_types.values())
        if total > 0:
            for syll_type in syllable_types:
                syllable_types[syll_type] /= total
    
    def _evolve_clusters(self, contact_pressure: float):
        """Evolve consonant cluster constraints"""
        consonants = [p for p in self.phoneme_inventory if not is_syllabic(p)]
        
        if len(consonants) < 2:
            return
        
        # Small chance to add new onset cluster
        if random.random() < 0.3 and len(consonants) >= 2:
            c1, c2 = random.sample(consonants, 2)
            new_cluster = (c1, c2)
            if new_cluster not in self.phonotactic_constraints.onset_clusters.allowed_combinations:
                self.phonotactic_constraints.onset_clusters.allowed_combinations.add(new_cluster)
        
        # Small chance to add new coda cluster
        if random.random() < 0.2 and len(consonants) >= 2:
            c1, c2 = random.sample(consonants, 2)
            new_cluster = (c1, c2)
            if new_cluster not in self.phonotactic_constraints.coda_clusters.allowed_combinations:
                self.phonotactic_constraints.coda_clusters.allowed_combinations.add(new_cluster)
    
    def _evolve_codas(self, contact_pressure: float):
        """Evolve coda constraints"""
        consonants = [p for p in self.phoneme_inventory if not is_syllabic(p)]
        
        # Small chance to allow new coda
        if random.random() < 0.1 and consonants:
            new_coda = random.choice(consonants)
            self.phonotactic_constraints.allowed_codas.add(new_coda)
        
        # Very small chance to remove coda (more conservative)
        if random.random() < 0.02 and len(self.phonotactic_constraints.allowed_codas) > 3:
            removed_coda = random.choice(list(self.phonotactic_constraints.allowed_codas))
            self.phonotactic_constraints.allowed_codas.remove(removed_coda)
    
    def borrow_word_advanced(self, source_word: Word, donor_language: 'Language') -> Word:
        """Borrow and adapt a word using phonotactic repair"""
        # Map donor phonemes to recipient inventory
        adapted_form = []
        for phoneme in source_word.form:
            if phoneme in self.phoneme_inventory:
                adapted_form.append(phoneme)
            else:
                # Find closest phoneme in recipient language
                closest = self._find_closest_phoneme(phoneme)
                adapted_form.append(closest)
        
        # Repair phonotactic violations
        repaired_form = repair_phonotactics(
            adapted_form, self.phonotactic_constraints, self.epenthetic_vowel
        )
        
        # Apply any active phonological rules
        current_tick = getattr(self, 'current_tick', 0)
        final_form = self.phonological_rules.apply_rules(repaired_form, current_tick)
        
        return Word(
            form=final_form,
            meaning=source_word.meaning,
            origin_lang_id=source_word.origin_lang_id,
            borrowed_from=donor_language.id,
            generation=source_word.generation + 1
        )
    
    def _find_closest_phoneme(self, target_phoneme: str) -> str:
        """Find the closest phoneme in this language's inventory"""
        if target_phoneme in self.phoneme_inventory:
            return target_phoneme
        
        if target_phoneme not in PHONEMES:
            # Fallback to a vowel if unknown phoneme
            vowels = [p for p in self.phoneme_inventory if is_syllabic(p)]
            return random.choice(vowels) if vowels else "a"
        
        # Find phoneme with minimum feature distance
        target_features = PHONEMES[target_phoneme]
        best_phoneme = None
        min_distance = float('inf')
        
        for phoneme in self.phoneme_inventory:
            if phoneme in PHONEMES:
                distance = sum(abs(f1 - f2) for f1, f2 in zip(target_features, PHONEMES[phoneme]))
                if distance < min_distance:
                    min_distance = distance
                    best_phoneme = phoneme
        
        return best_phoneme if best_phoneme else random.choice(list(self.phoneme_inventory))

    def __str__(self) -> str:
        return f"Language({self.name}, ID={self.id}, Gen={self.generation})"