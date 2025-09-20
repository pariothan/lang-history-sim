import React from 'react';
import { X } from 'lucide-react';

interface HelpModalProps {
  onClose: () => void;
}

export function HelpModal({ onClose }: HelpModalProps) {
  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal">
        <div className="modal-header">
          <h2>Language Evolution Simulator - Help</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="modal-content">
          <div className="help-content">
            <h4>What is this?</h4>
            <p>
              This is a simulation of how languages evolve and spread over time. It models realistic 
              linguistic phenomena including sound changes, word borrowing, language contact, and 
              family formation using principles from historical linguistics.
            </p>

            <h4>How it works</h4>
            <p>
              The simulation starts with a few languages scattered across a procedurally generated 
              world. Each language has its own phonological system (sounds) and vocabulary. Over time:
            </p>
            <ul>
              <li><strong>Languages spread</strong> to neighboring communities based on prestige</li>
              <li><strong>Words change</strong> through phonological mutations and sound shifts</li>
              <li><strong>Languages borrow words</strong> from prestigious neighbors</li>
              <li><strong>Languages split</strong> into daughter languages when populations grow</li>
              <li><strong>Languages go extinct</strong> when they lose all speakers</li>
            </ul>

            <h4>Visual System</h4>
            <p>
              Each language is colored based on its phonological features. Languages with similar 
              sound systems appear in similar colors, making it easy to see linguistic relationships 
              and family groupings.
            </p>

            <h4>Controls</h4>
            <ul>
              <li><kbd>Space</kbd> - Play/Pause the simulation</li>
              <li><kbd>R</kbd> - Reset with a new world</li>
              <li><kbd>S</kbd> - Toggle the statistics sidebar</li>
              <li><kbd>H</kbd> - Show this help dialog</li>
              <li><kbd>Esc</kbd> - Close dialogs</li>
              <li><strong>Speed Slider</strong> - Adjust simulation speed from 1% to 100%</li>
              <li><strong>View Dropdown</strong> - Switch between different map visualization modes</li>
              <li><strong>Click</strong> on any colored region to view detailed language information</li>
            </ul>

            <h4>Map Modes</h4>
            <p>Use the "View" dropdown to switch between different visualization modes:</p>
            <ul>
              <li><strong>Languages</strong> - Each language has a unique color based on its sound system</li>
              <li><strong>Prestige</strong> - Red = high prestige, Blue = low prestige languages</li>
              <li><strong>Age</strong> - Purple = older languages, Green = younger languages</li>
              <li><strong>Phonemes</strong> - Orange = many sounds, Cyan = few sounds</li>
              <li><strong>Vocabulary</strong> - Yellow = large vocabulary, Magenta = small vocabulary</li>
              <li><strong>Families</strong> - Related languages share similar colors</li>
            </ul>

            <h4>Language Details</h4>
            <p>
              Click on any community to explore its language in detail. You can see:
            </p>
            <ul>
              <li><strong>Phoneme inventory</strong> - All the sounds the language uses</li>
              <li><strong>Complete vocabulary</strong> - All words with their meanings</li>
              <li><strong>Word origins</strong> - Which words were borrowed from other languages</li>
              <li><strong>Language genealogy</strong> - Parent-child relationships between languages</li>
            </ul>

            <h4>What to watch for</h4>
            <p>
              As the simulation runs, you'll see fascinating patterns emerge:
            </p>
            <ul>
              <li><strong>Language families</strong> - Groups of related languages with similar colors</li>
              <li><strong>Geographic barriers</strong> - How mountains and water affect language spread</li>
              <li><strong>Prestige effects</strong> - How influential languages spread faster</li>
              <li><strong>Contact zones</strong> - Areas where languages meet and influence each other</li>
            </ul>

            <p>
              Let the simulation run for a while to see complex linguistic landscapes develop!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}