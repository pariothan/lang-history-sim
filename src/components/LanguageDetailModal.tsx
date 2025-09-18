import React, { useState, useMemo } from 'react';
import { X, Search } from 'lucide-react';
import { Language } from '../simulation/Language';

interface LanguageDetailModalProps {
  language: Language;
  onClose: () => void;
}

export function LanguageDetailModal({ language, onClose }: LanguageDetailModalProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredVocabulary = useMemo(() => {
    if (!searchTerm.trim()) {
      return Array.from(language.lexicon.entries());
    }
    
    const term = searchTerm.toLowerCase();
    return Array.from(language.lexicon.entries()).filter(([meaning, word]) =>
      meaning.toLowerCase().includes(term) ||
      word.form.join('').toLowerCase().includes(term)
    );
  }, [language.lexicon, searchTerm]);

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal">
        <div className="modal-header">
          <h2>{language.name}</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="modal-content">
          {/* Overview Section */}
          <div className="section">
            <h3>Language Overview</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.9rem' }}>
              <div>
                <strong>Language ID:</strong> {language.id}
              </div>
              <div>
                <strong>Generation:</strong> {language.generation}
              </div>
              <div>
                <strong>Prestige:</strong> {(language.prestige * 100).toFixed(1)}%
              </div>
              <div>
                <strong>Conservatism:</strong> {(language.conservatism * 100).toFixed(1)}%
              </div>
              <div>
                <strong>Phonemes:</strong> {language.getPhonemeCount()}
              </div>
              <div>
                <strong>Vocabulary:</strong> {language.getVocabularySize()} words
              </div>
              {language.parentId && (
                <div style={{ gridColumn: '1 / -1' }}>
                  <strong>Parent Language ID:</strong> {language.parentId}
                </div>
              )}
            </div>
          </div>

          {/* Phonological System */}
          <div className="section">
            <h3>Phonological System</h3>
            
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '1rem', marginBottom: '8px', color: '#60a5fa' }}>
                Vowels ({language.getVowels().length})
              </h4>
              <div className="phoneme-grid">
                {language.getVowels().map(vowel => (
                  <span key={vowel} className="phoneme">{vowel}</span>
                ))}
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '1rem', marginBottom: '8px', color: '#60a5fa' }}>
                Consonants ({language.getConsonants().length})
              </h4>
              <div className="phoneme-grid">
                {language.getConsonants().map(consonant => (
                  <span key={consonant} className="phoneme">{consonant}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Vocabulary Section */}
          <div className="section">
            <h3>Vocabulary</h3>
            
            <div style={{ position: 'relative', marginBottom: '12px' }}>
              <Search size={16} style={{ 
                position: 'absolute', 
                left: '12px', 
                top: '50%', 
                transform: 'translateY(-50%)',
                color: '#9ca3af'
              }} />
              <input
                type="text"
                placeholder="Search vocabulary..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-box"
                style={{ paddingLeft: '40px' }}
              />
            </div>

            <div className="vocab-list">
              {filteredVocabulary.length === 0 ? (
                <div style={{ textAlign: 'center', color: '#9ca3af', padding: '20px' }}>
                  No matching vocabulary found
                </div>
              ) : (
                <>
                  {filteredVocabulary.slice(0, 50).map(([meaning, word]) => (
                    <div key={meaning} className="vocab-item">
                      <span className="vocab-meaning">{meaning}</span>
                      <span className="vocab-form">
                        {word.form.join('')}
                        {word.borrowedFrom && (
                          <span style={{ fontSize: '0.7rem', color: '#9ca3af', marginLeft: '8px' }}>
                            (borrowed)
                          </span>
                        )}
                        {word.generation > 0 && (
                          <span style={{ fontSize: '0.7rem', color: '#9ca3af', marginLeft: '8px' }}>
                            (gen {word.generation})
                          </span>
                        )}
                      </span>
                    </div>
                  ))}
                  {filteredVocabulary.length > 50 && (
                    <div style={{ textAlign: 'center', color: '#9ca3af', padding: '12px', fontSize: '0.8rem' }}>
                      Showing first 50 of {filteredVocabulary.length} results
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}