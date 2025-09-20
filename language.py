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
        
        # Initialize phonological generator
        self.phonological_generator = PhonologicalGenerator(
            self.phoneme_inventory, self.phonotactic_constraints)
        
        # Phonological rules and evolution
        self.phonological_rules = PhonologicalRuleSet()
        self.epenthetic_vowel = random.choice(CONFIG.EPENTHETIC_VOWEL_CHOICES)
        self.last_evolution_tick = 0
        
        # Precompute phonological weights
        self._update_phonological_weights()
        
        # Apply inheritance drift after weights are computed
        if parent is not None:
            self._drift_phonemes()
            self._drift_constraints()
        
        # Lexicon
        self.lexicon: Dict[str, Word] = {}
        if parent is None:
            self._generate_initial_lexicon()
        else:
            self._inherit_lexicon(parent)
        
        # Language properties
        self.prestige = random.uniform(*CONFIG.PRESTIGE_RANGE)
        self.conservatism = random.uniform(*CONFIG.CONSERVATISM_RANGE)
        
        # Generate or inherit name
        if parent is None:
            self.name_word = self._generate_name_word()
        else:
            # Inherit name from parent (will evolve later)
            self.name_word = Word(parent.name_word.form.copy(), "language_name", 
                                parent.name_word.origin_lang_id, generation=parent.name_word.generation)
        
        # Geographic branching marker (for display only, not part of phonology)
        self.geographic_branch_marker = ""
        
        # Evolution tracking
        self.parent_id = parent.id if parent else None
        self.children: List[int] = []
        
        # Prestige tracking
        self.prestige_history: List[float] = [self.prestige]
        
    def _select_initial_phonemes(self) -> Set[str]:
        """Select initial phoneme inventory using maximum dispersion"""
        vowels = [p for p in INVENTORY if is_syllabic(p)]
        consonants = [p for p in INVENTORY if not is_syllabic(p)]
        
        # Ensure minimum vowel system
        selected = set(random.sample(vowels, min(CONFIG.MIN_INITIAL_VOWELS, len(vowels))))
        
        # Add consonants using feature dispersion
        remaining = set(consonants)
        while len(selected) < random.randint(*CONFIG.INITIAL_INVENTORY_SIZE_RANGE) and remaining:
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
        constraint_func = random.choices(constraint_types, weights=CONFIG.CONSTRAINT_PROFILE_WEIGHTS, k=1)[0]
        return constraint_func()
    
    def _calculate_inventory_dispersion(self, inventory: set) -> float:
        """Calculate how well dispersed phonemes are in feature space"""
        if len(inventory) <= 1:
            return 0.0
            
        total_distance = 0.0
        count = 0
        
        inventory_list = list(inventory)
        for i, p1 in enumerate(inventory_list):
            for j, p2 in enumerate(inventory_list[i+1:], i+1):
                total_distance += self._feature_distance(p1, p2)
                count += 1
        
        return total_distance / count if count > 0 else 0.0
    
    def _find_optimal_phoneme_to_add(self, current_inventory: set) -> Optional[str]:
        """Find phoneme that maximizes inventory dispersion when added"""
        available = set(INVENTORY) - current_inventory
        if not available:
            return None
            
        best_phoneme = None
        best_dispersion = -1.0
        
        for candidate in available:
            test_inventory = current_inventory | {candidate}
            dispersion = self._calculate_inventory_dispersion(test_inventory)
            
            if dispersion > best_dispersion:
                best_dispersion = dispersion
                best_phoneme = candidate
        
        return best_phoneme
    
    def _find_phoneme_to_remove(self, current_inventory: set) -> Optional[str]:
        """Find phoneme whose removal least impacts dispersion (or improves it)"""
        if len(current_inventory) <= CONFIG.MIN_VOWEL_COUNT:
            return None
            
        # Don't remove if it would leave too few vowels
        vowels_in_inv = [p for p in current_inventory if is_syllabic(p)]
        
        best_phoneme = None
        best_dispersion = -1.0
        
        for candidate in current_inventory:
            # Preserve vowel minimum
            if is_syllabic(candidate) and len(vowels_in_inv) <= CONFIG.MIN_VOWEL_COUNT:
                continue
                
            test_inventory = current_inventory - {candidate}
            dispersion = self._calculate_inventory_dispersion(test_inventory)
            
            if dispersion > best_dispersion:
                best_dispersion = dispersion
                best_phoneme = candidate
        
        return best_phoneme
    
    def _find_suboptimal_phoneme_for_substitution(self) -> Optional[str]:
        """Find phoneme that contributes least to inventory dispersion for substitution"""
        if len(self.phoneme_inventory) <= CONFIG.MIN_VOWEL_COUNT:
            return None
        
        # Don't substitute if it would leave too few vowels
        vowels_in_inv = [p for p in self.phoneme_inventory if is_syllabic(p)]
        
        best_phoneme = None
        best_dispersion = -1.0
        
        for candidate in self.phoneme_inventory:
            # Preserve vowel minimum
            if is_syllabic(candidate) and len(vowels_in_inv) <= CONFIG.MIN_VOWEL_COUNT:
                continue
            
            # Test what happens if we remove this phoneme
            test_inventory = self.phoneme_inventory - {candidate}
            dispersion = self._calculate_inventory_dispersion(test_inventory)
            
            # Find phoneme whose removal LEAST harms dispersion (contributes least)
            if dispersion > best_dispersion:
                best_dispersion = dispersion
                best_phoneme = candidate
        
        return best_phoneme
    
    def _drift_phonemes(self):
        """Apply phonological drift with bias toward maximal distinctiveness"""
        # Chance to add phonemes (bias toward better dispersion)
        if random.random() < CONFIG.P_PHONEME_ADD:
            available = set(INVENTORY) - self.phoneme_inventory
            if available:
                if random.random() < CONFIG.P_OPTIMIZE_ADD:
                    optimal_phoneme = self._find_optimal_phoneme_to_add(self.phoneme_inventory)
                    if optimal_phoneme:
                        self.phoneme_inventory.add(optimal_phoneme)
                else:  # 30% chance for random addition
                    self.phoneme_inventory.add(random.choice(list(available)))
        
        # Chance to remove phonemes (bias toward keeping optimal dispersion)
        if random.random() < CONFIG.P_PHONEME_REMOVE and len(self.phoneme_inventory) > CONFIG.MIN_PHONEME_INVENTORY_SIZE:
            if random.random() < CONFIG.P_OPTIMIZE_REMOVE:
                phoneme_to_remove = self._find_phoneme_to_remove(self.phoneme_inventory)
                if phoneme_to_remove:
                    self.phoneme_inventory.remove(phoneme_to_remove)
            else:  # 20% chance for random removal
                vowels_in_inv = [p for p in self.phoneme_inventory if is_syllabic(p)]
                if len(vowels_in_inv) > CONFIG.MIN_VOWEL_COUNT:
                    candidates = [p for p in self.phoneme_inventory 
                                if not is_syllabic(p) or len(vowels_in_inv) > CONFIG.MIN_VOWEL_COUNT + 1]
                    if candidates:
                        self.phoneme_inventory.remove(random.choice(candidates))
        
        # Chance to substitute phonemes (biased toward full phonemic space utilization)
        if random.random() < CONFIG.P_PHONEME_SUBSTITUTE:
            if len(self.phoneme_inventory) > CONFIG.MIN_VOWEL_COUNT:
                # Choose a phoneme to replace (bias toward removing less optimal ones)
                old_phoneme = self._find_suboptimal_phoneme_for_substitution()
                if not old_phoneme:
                    old_phoneme = random.choice(list(self.phoneme_inventory))
                
                # Don't substitute if it would violate vowel constraints
                vowels_in_inv = [p for p in self.phoneme_inventory if is_syllabic(p)]
                if is_syllabic(old_phoneme) and len(vowels_in_inv) <= CONFIG.MIN_VOWEL_COUNT:
                    pass  # Skip substitution to preserve vowels
                else:
                    # Find replacement that improves phonemic space utilization
                    available_phonemes = set(INVENTORY) - self.phoneme_inventory
                    if available_phonemes and old_phoneme in IDX:
                        current_dispersion = self._calculate_inventory_dispersion(self.phoneme_inventory)
                        
                        # Evaluate candidates based on dispersion improvement + similarity
                        candidates = []
                        dispersion_improvements = []
                        similarity_weights = []
                        old_idx = IDX[old_phoneme]
                        
                        for candidate in available_phonemes:
                            if candidate in IDX:
                                # Preserve vowel/consonant type preference
                                if is_syllabic(old_phoneme) == is_syllabic(candidate):
                                    # Test inventory with substitution
                                    test_inventory = (self.phoneme_inventory - {old_phoneme}) | {candidate}
                                    new_dispersion = self._calculate_inventory_dispersion(test_inventory)
                                    
                                    # Collect metrics for normalization
                                    dispersion_improvement = max(0, new_dispersion - current_dispersion)
                                    candidate_idx = IDX[candidate]
                                    similarity_weight = self.mut_weights[old_idx][candidate_idx]
                                    
                                    candidates.append(candidate)
                                    dispersion_improvements.append(dispersion_improvement)
                                    similarity_weights.append(similarity_weight)
                        
                        # Normalize both components and combine with proper weighting
                        weights = []
                        if candidates:
                            # Normalize dispersion improvements
                            max_disp = max(dispersion_improvements) if dispersion_improvements else 1.0
                            norm_dispersion = [d / max_disp if max_disp > 0 else 0 for d in dispersion_improvements]
                            
                            # Normalize similarity weights 
                            max_sim = max(similarity_weights) if similarity_weights else 1.0
                            norm_similarity = [s / max_sim if max_sim > 0 else 0 for s in similarity_weights]
                            
                            # Combine with 70/30 weighting (dispersion/similarity)
                            for norm_disp, norm_sim in zip(norm_dispersion, norm_similarity):
                                if max_disp > 0:  # If any dispersion improvement exists
                                    combined_weight = CONFIG.DISPERSION_WEIGHT * norm_disp + CONFIG.SIMILARITY_WEIGHT * norm_sim
                                else:  # Fall back to similarity only
                                    combined_weight = norm_sim
                                weights.append(combined_weight)
                        
                        if candidates and weights and max(weights) > 0:
                            # Choose replacement based on combined score
                            new_phoneme = random.choices(candidates, weights=weights, k=1)[0]
                            
                            # Safeguard: verify substitution doesn't significantly harm dispersion
                            test_inventory = (self.phoneme_inventory - {old_phoneme}) | {new_phoneme}
                            final_dispersion = self._calculate_inventory_dispersion(test_inventory)
                            dispersion_change = final_dispersion - current_dispersion
                            
                            # Only proceed if dispersion doesn't decrease significantly
                            if dispersion_change >= CONFIG.DISPERSION_TOLERANCE:
                                self.phoneme_inventory.remove(old_phoneme)
                                self.phoneme_inventory.add(new_phoneme)
        
        # Update phonological generator after inventory changes
        self.phonological_generator = PhonologicalGenerator(
            self.phoneme_inventory, self.phonotactic_constraints)
    
    def _drift_constraints(self):
        """Apply small changes to phonotactic constraints when splitting from parent"""
        # Small chance to modify constraints
        if random.random() < CONFIG.P_CONSTRAINT_DRIFT:
            
            # Modify syllable type preferences slightly
            if random.random() < CONFIG.P_SYLLABLE_DRIFT:
                self._modify_syllable_preferences()
            
            # Change gemination settings
            if random.random() < CONFIG.P_GEMINATION_DRIFT:
                self.phonotactic_constraints.allow_gemination = not self.phonotactic_constraints.allow_gemination
                if self.phonotactic_constraints.allow_gemination:
                    self.phonotactic_constraints.gemination_probability = random.uniform(*CONFIG.GEMINATION_PROB_RANGE)
            
            # Modify word length preferences
            if random.random() < CONFIG.P_WORD_LENGTH_DRIFT:
                self.phonotactic_constraints.preferred_syllables = random.randint(*CONFIG.SYLLABLE_COUNT_RANGE)
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
    
    def _generate_name_word(self) -> Word:
        """Generate a name word for this language"""
        name_form = self._generate_word()
        
        # Fallback if name generation fails
        if not name_form or len(name_form) < 2:
            # Use a simple phoneme-based fallback
            vowels = [p for p in self.phoneme_inventory if is_syllabic(p)]
            consonants = [p for p in self.phoneme_inventory if not is_syllabic(p)]
            
            if vowels and consonants:
                # Create a simple CV-CV pattern
                name_form = [random.choice(consonants), random.choice(vowels),
                           random.choice(consonants), random.choice(vowels)]
            elif vowels:
                # Vowel-only fallback
                name_form = random.choices(vowels, k=3)
            elif consonants:
                # Consonant-vowel fallback with default vowel
                name_form = [random.choice(consonants), "a", random.choice(consonants), "a"]
            else:
                # Ultimate fallback
                name_form = list(f"Lang{self.id}")
        
        return Word(name_form, "language_name", self.id)
    
    @property
    def name(self) -> str:
        """Get the language name as a display string"""
        base_name = "".join(self.name_word.form)
        return base_name + self.geographic_branch_marker
    
    def _drift_prestige(self, speaker_count: int = 1):
        """Apply gradual prestige drift over time"""
        from config import CONFIG
        
        # Base drift - random walk with slight bias toward middle
        base_drift = random.uniform(-CONFIG.PRESTIGE_DRIFT_MAGNITUDE, CONFIG.PRESTIGE_DRIFT_MAGNITUDE)
        
        # Bias toward middle (0.5) to prevent extreme values
        middle_bias = (CONFIG.PRESTIGE_DRIFT_BIAS - self.prestige) * CONFIG.PRESTIGE_MIDDLE_BIAS_STRENGTH
        
        # Success factor - languages with more speakers tend to gain prestige
        success_factor = 0.0
        if speaker_count > 1:
            # Logarithmic bonus for successful languages
            success_factor = min(0.002, 0.0005 * math.log(speaker_count))
        
        # Apply drift
        total_drift = base_drift + middle_bias + success_factor
        self.prestige += total_drift
        
        # Clamp to valid range
        self.prestige = max(0.05, min(0.95, self.prestige))
        
        # Track history
        self.prestige_history.append(self.prestige)
        
        # Keep history manageable
        if len(self.prestige_history) > 100:
            self.prestige_history = self.prestige_history[-50:]
    
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
    
    def branch_geographic(self) -> 'Language':
        """Create a geographic branch (no phonological drift)"""
        import copy
        
        # Create new language with same ID allocation system
        Language._next_id += 1
        branch = Language.__new__(Language)
        branch.id = Language._next_id
        branch.generation = self.generation
        
        # Copy phonological system exactly (no drift)
        branch.phoneme_inventory = self.phoneme_inventory.copy()
        branch.phonotactic_constraints = copy.deepcopy(self.phonotactic_constraints)
        branch.phonological_generator = PhonologicalGenerator(
            branch.phoneme_inventory, branch.phonotactic_constraints)
        branch.phonological_rules = copy.deepcopy(self.phonological_rules)
        branch.epenthetic_vowel = self.epenthetic_vowel
        branch.last_evolution_tick = self.last_evolution_tick
        
        # Copy lexicon exactly
        branch.lexicon = {}
        for meaning, word in self.lexicon.items():
            new_word = Word(word.form.copy(), meaning, word.origin_lang_id, 
                          word.borrowed_from, word.generation)
            branch.lexicon[meaning] = new_word
        
        # Copy language properties
        branch.prestige = self.prestige
        branch.conservatism = self.conservatism
        # Copy name word exactly (no phonological change for geographic branches)
        branch.name_word = Word(self.name_word.form.copy(), "language_name", 
                               self.name_word.origin_lang_id, generation=self.name_word.generation)
        # Add geographic branch marker for display
        branch.geographic_branch_marker = self.geographic_branch_marker + "'"
        
        # Set up family relationships
        branch.parent_id = self.id
        branch.children = []
        self.children.append(branch.id)
        
        # Copy prestige history
        branch.prestige_history = self.prestige_history.copy()
        
        # Copy phonological weights
        branch._update_phonological_weights()
        
        # Initialize fields that __init__ would normally set
        branch.geographic_branch_marker = branch.geographic_branch_marker  # Already set above
        
        return branch
    
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
        if tick - self.last_evolution_tick < CONFIG.EVOLUTION_INTERVAL:
            return
        
        self.last_evolution_tick = tick
        
        # Calculate contact pressure from other languages
        contact_pressure = 0.0
        if contact_languages:
            for lang in contact_languages[:CONFIG.MAX_CONTACT_LANGUAGES]:
                # More prestigious languages have more influence
                influence = lang.prestige / (self.prestige + 0.1)
                contact_pressure += influence * CONFIG.CONTACT_INFLUENCE_FACTOR
        
        contact_pressure = min(contact_pressure, CONFIG.CONTACT_PRESSURE_CAP)
        
        # Evolve phonological rules
        self.phonological_rules.evolve(tick, self.conservatism, contact_pressure)
        
        # Apply phonological changes to a sample of the lexicon
        self._apply_sound_changes(tick)
        
        # Evolve the language name like vocabulary
        self._evolve_name(tick)
        
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
        sample_size = min(CONFIG.SAMPLE_SIZE_LEXICON, len(self.lexicon))
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
    
    def _evolve_name(self, tick: int):
        """Apply phonological evolution to the language name"""
        if not hasattr(self, 'name_word') or not self.name_word:
            return
        
        old_form = self.name_word.form[:]
        
        # Apply active phonological rules (like vocabulary words)
        if self.phonological_rules.get_active_rules(tick):
            new_form = self.phonological_rules.apply_rules(self.name_word.form, tick)
            
            if new_form != old_form:
                # Repair phonotactic violations after sound changes
                repaired_form = repair_phonotactics(
                    new_form, self.phonotactic_constraints, self.epenthetic_vowel
                )
                
                # Update the name word
                self.name_word = Word(
                    form=repaired_form,
                    meaning="language_name",
                    origin_lang_id=self.name_word.origin_lang_id,
                    borrowed_from=self.name_word.borrowed_from,
                    generation=self.name_word.generation + 1
                )
        
        # Apply random mutations (like vocabulary words)
        if random.random() < CONFIG.P_NAME_MUTATION:
            self.mutate_word(self.name_word)
    
    def _evolve_constraints(self, tick: int, contact_pressure: float):
        """Evolve phonotactic constraints over time"""
        # Gradually shift syllable structure preferences
        if random.random() < CONFIG.P_SYLLABLE_EVOLUTION:
            self._shift_syllable_preferences(contact_pressure)
        
        # Expand or contract consonant clusters
        if random.random() < CONFIG.P_CLUSTER_EVOLUTION:
            self._evolve_clusters(contact_pressure)
        
        # Change coda restrictions
        if random.random() < CONFIG.P_CODA_EVOLUTION:
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