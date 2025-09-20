# Language Evolution Simulator - Design Document

## Overview

The Language Evolution Simulator is a sophisticated Python application that models realistic linguistic evolution and geographic spread of languages over time. It simulates phonological change, lexical borrowing, language contact, and family formation using principles from historical linguistics, generating procedural worlds with geographic features and tracking how languages evolve and spread across communities.

## System Architecture

### Core Components

The application follows a modular architecture with clear separation of concerns:

1. **Main Entry Point** (`main.py`)
   - Delegates execution to the visualization system
   - Provides clean application startup

2. **Visualization System** (`visualization.py`)
   - Tkinter-based GUI with real-time rendering
   - 7-mapmode visualization system for different linguistic perspectives
   - Interactive controls and event handling
   - Performance-optimized with cached colors and fonts

3. **World Generation** (`world.py`)
   - Procedural terrain generation using cellular automata
   - Island-biased generation with smoothing passes
   - Efficient neighbor mapping for adjacency queries
   - Support for long-distance community interactions

4. **Language Evolution Engine** (`simulation.py`)
   - Per-tick evolution mechanics
   - Contact-based linguistic interactions
   - Geographic spread and contiguity enforcement
   - Prestige dynamics and long-distance interactions

5. **Language Modeling** (`language.py`)
   - Phonological inventory management
   - Lexicon and word evolution
   - Language splitting and inheritance
   - Name evolution system

6. **Phonological System** (`phonology.py`)
   - Distinctive feature theory implementation
   - Phonotactic constraint modeling
   - Sound change algorithms
   - Feature-based color projection for visualization

7. **Vocabulary Management** (`vocabulary.py`)
   - Swadesh list-based semantic concepts
   - Word generation and meaning mapping

8. **Configuration System** (`config.py`)
   - Centralized parameter management
   - 50+ configurable evolution parameters
   - Runtime tuning without code changes

## Data Structures

### World Model
- **World**: 2D grid of `Optional[Community]` with neighbor mapping
- **Community**: Position (x,y), language_id, prestige, population
- **Efficient neighbor lookup**: O(1) adjacency queries for spread mechanics

### Language Model
- **Language**: Complete linguistic system with:
  - `phoneme_inventory`: Set of available phonemes
  - `phonotactic_constraints`: Syllable structure rules
  - `lexicon`: Dictionary mapping meanings to Word objects
  - `name_word`: Evolving language name
  - `prestige`/`conservatism`: Sociolinguistic properties
  - Lineage tracking (parent/children relationships)

- **Word**: Dataclass containing:
  - `form`: List of phonemes
  - `meaning`: Semantic content
  - `origin_lang_id`: Source language
  - `borrowed_from`: Borrowing metadata
  - `generation`: Evolutionary distance from origin

### Phonological Framework
- **Distinctive Features**: Binary feature vectors for each phoneme
- **Phonotactic Constraints**: Rule systems (default/complex/mora-based)
- **Phonological Rules**: Sound change patterns and productivity
- **Feature Distance**: Similarity calculations for realistic mutations

## Core Algorithms

### Evolution Mechanics (Per Simulation Tick)

For each community and its language, the system applies:

1. **Internal Evolution** (`language.evolve`)
   - Phoneme inventory drift (add/remove/substitute with optimization)
   - Constraint evolution
   - Rule generation and decay
   - Name evolution through phonological processes

2. **Stochastic Processes** (probability-driven):
   - Word mutation (`P_MUTATE`)
   - Geographic spread to neighbors (`P_SPREAD`)
   - Lexical borrowing with adaptation (`P_BORROW`)
   - Language splitting (`P_LANGUAGE_SPLIT`)
   - Long-distance spread (`P_LONG_DISTANCE_SPREAD`)
   - Prestige drift (`P_PRESTIGE_DRIFT`)

3. **Contiguity Enforcement** (periodic):
   - Connected component analysis using BFS
   - Automatic language splitting for non-contiguous territories
   - Geographic branching without phonological change

### Phonological Evolution

**Inventory Optimization**: Uses feature space dispersion to maintain optimal phoneme distributions:
- **Addition**: Selects phonemes that maximize inventory dispersion
- **Removal**: Removes phonemes with minimal dispersion impact
- **Substitution**: Balances dispersion improvement with phonological similarity

**Sound Change**: Feature-based mutations respect phonological naturalness:
- Distance calculations use distinctive feature vectors
- Weighted probabilities favor phonologically plausible changes
- Adaptation mechanisms for borrowed words

### Language Contact and Borrowing

**Prestige-Based Borrowing**: Higher prestige languages influence neighbors:
- Phonological adaptation using target language constraints
- Epenthesis and repair strategies for foreign phonotactics
- Contact pressure calculations based on neighbor languages

**Geographic Spread**: Multiple spread mechanisms:
- Adjacent neighbor spread (primary)
- Long-distance spread within Manhattan distance bands
- Contiguity-aware seeding prevents disconnected territories

## Visualization System

### 7-Mapmode System

The visualization provides seven distinct perspectives on the linguistic landscape:

1. **LANGUAGE_NAME**: Shows actual language names (apostrophes hidden)
2. **VOCABULARY_ITEM**: Displays specific vocabulary words with phoneme-based colors
3. **PHONOLOGICAL_RULES**: Rule complexity visualization
4. **LANGUAGE_FAMILY**: Family relationships with ancestor-based grouping
5. **PHONEME_COUNT**: Inventory size heatmap
6. **SPEAKER_COUNT**: Population density visualization
7. **PRESTIGE**: Sociolinguistic status heatmap

### Rendering Techniques

**Color Systems**:
- **Hash-based colors**: Stable colors for categorical data (languages, families)
- **Feature-projected colors**: Phonologically-meaningful colors for vocabulary
- **Gradient colors**: Smooth heatmaps for numeric data

**Performance Optimizations**:
- Cached font and color calculations
- Dirty tracking for selective updates
- Pre-computed gradient mappings

**Interactive Features**:
- Mode cycling (M key)
- Vocabulary word cycling (V key)
- Click-to-inspect language details
- Real-time parameter display

## Special Features

### Name Evolution System

Languages have evolving names that undergo the same phonological processes as vocabulary:
- Names stored as Word objects with generational tracking
- Inheritance from parent languages during splits
- Geographic branching markers separate from phonological evolution
- Display names stripped of apostrophes for visual clarity

### Geographic Contiguity Enforcement

Realistic territorial constraints through automated enforcement:
- BFS-based connected component detection
- Automatic splitting of non-contiguous languages
- Preservation of largest territory as original language
- Creation of "branch" languages for separated regions

### Boundary Drawing Logic

Intelligent boundary rendering that respects linguistic relationships:
- No boundaries between languages with same base name (ignoring apostrophes)
- Visual unity for related language variants
- 2px black boundary lines for clear territorial definition

### Comprehensive Configuration System

Full customizability through centralized parameters:

**Phonological Parameters**:
- `P_PHONEME_ADD`/`P_PHONEME_REMOVE`: Inventory change rates (currently 0.7 each)
- `MIN_VOWEL_COUNT`: Minimum vowel inventory (3)
- `DISPERSION_WEIGHT`/`SIMILARITY_WEIGHT`: Optimization balance

**Evolution Parameters**:
- `P_MUTATE`: Word-level change rate (0.05)
- `P_SPREAD`: Geographic expansion (0.24)
- `P_BORROW`: Lexical borrowing (0.12)
- `P_LANGUAGE_SPLIT`: Language divergence (0.01)

**Contact Parameters**:
- `PRESTIGE_THRESHOLD`: Borrowing influence threshold
- `LONG_DISTANCE_RANGE`: Maximum interaction distance
- `CONTIGUITY_ENFORCE_INTERVAL`: Territory checking frequency

**World Generation**:
- `GRID_W`/`GRID_H`: World dimensions
- `LAND_PROB_INIT`: Initial land probability
- `ISLAND_BIAS`: Centralization factor
- `SMOOTH_STEPS`: Terrain smoothing iterations

## Technical Implementation

### Performance Considerations

**Efficient Data Structures**:
- Set-based phoneme inventories for O(1) membership testing
- Flat community lists for linear iteration
- Cached neighbor mappings for adjacency queries

**Optimized Algorithms**:
- LRU-cached color calculations
- Pre-computed mutation and addition weights
- Selective contiguity checking with dirty tracking

### Error Handling and Robustness

**Linguistic Constraints**:
- Minimum vowel and inventory size enforcement
- Phonotactic repair for invalid combinations
- Graceful handling of empty inventories

**Geographic Constraints**:
- Bounds checking for world coordinates
- Safe neighbor access with null handling
- Contiguity validation and automatic correction

### Extensibility Design

**Modular Architecture**: Clear separation enables easy extension:
- New mapmode addition through enum extension
- Custom constraint types via function registration
- Additional phonological processes through rule system

**Configuration-Driven Behavior**: New parameters easily added to CONFIG class
**Event-Driven Evolution**: Plugin-style addition of new evolutionary processes

## Usage and Controls

### Interactive Controls
- **Q/Esc**: Quit application
- **R**: Reset simulation
- **N**: Generate new world
- **Space**: Pause/Resume
- **M**: Cycle through visualization mapmodes
- **V**: Cycle vocabulary words (in vocabulary mapmode)
- **Click**: Inspect language details

### Simulation Flow
1. **World Generation**: Creates procedural terrain with land masses
2. **Language Seeding**: Randomly places initial language communities
3. **Evolution Loop**: Continuous tick-based evolution with visualization updates
4. **Real-time Statistics**: Population, vocabulary, and family tracking

## Future Enhancement Opportunities

1. **Interactive Configuration Panel**: Runtime parameter adjustment
2. **Historical Tracking**: Detailed evolutionary trees and change histories
3. **Export Capabilities**: Language data and family tree export
4. **Advanced Phonology**: Tone systems, morphophonology, allophony
5. **Cultural Features**: Non-linguistic cultural evolution and contact
6. **Performance Scaling**: Multi-threading for larger world simulations

This design document represents the current state of a sophisticated, realistic language evolution simulator that successfully models complex linguistic phenomena through configurable, algorithmically sound mechanisms while providing rich visual feedback and interactive exploration capabilities.