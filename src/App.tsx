import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Play, Pause, RotateCcw, Info, X, HelpCircle, Gauge } from 'lucide-react';
import { LanguageEvolutionSimulation } from './simulation/LanguageEvolutionSimulation';
import { CanvasRenderer } from './visualization/CanvasRenderer';
import { Language } from './simulation/Language';
import { LanguageDetailModal } from './components/LanguageDetailModal';
import { HelpModal } from './components/HelpModal';

function App() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const simulationRef = useRef<LanguageEvolutionSimulation | null>(null);
  const rendererRef = useRef<CanvasRenderer | null>(null);
  const animationRef = useRef<number | null>(null);
  
  const [isRunning, setIsRunning] = useState(true);
  const [showSidebar, setShowSidebar] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState<Language | null>(null);
  const [showHelp, setShowHelp] = useState(false);
  const [simulationSpeed, setSimulationSpeed] = useState(50); // milliseconds between frames
  const [stats, setStats] = useState({
    tick: 0,
    communities: 0,
    speakingCommunities: 0,
    languages: 0,
    largestLanguage: 0
  });
  const [topLanguages, setTopLanguages] = useState<Array<{id: number, name: string, speakers: number, color: string}>>([]);

  const initializeSimulation = useCallback(() => {
    if (!canvasRef.current) return;
    
    // Create new simulation
    simulationRef.current = new LanguageEvolutionSimulation();
    
    // Create renderer
    rendererRef.current = new CanvasRenderer(canvasRef.current, simulationRef.current);
    
    // Set up click handler
    rendererRef.current.onLanguageClick = (language: Language) => {
      setSelectedLanguage(language);
    };
    
    // Initial render
    rendererRef.current.render();
    updateStats();
  }, []);

  const updateStats = useCallback(() => {
    if (!simulationRef.current) return;
    
    const worldStats = simulationRef.current.world.calculateLanguageStats();
    const languages = simulationRef.current.getAllLanguages();
    
    setStats({
      tick: simulationRef.current.tickCount,
      communities: worldStats.totalCommunities,
      speakingCommunities: worldStats.speakingCommunities,
      languages: worldStats.languages,
      largestLanguage: worldStats.largestLanguage
    });

    // Update top languages with colors
    const sortedLangs = Object.entries(worldStats.languageDistribution)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 8)
      .map(([langId, speakers]) => {
        const language = languages.find(l => l.id === parseInt(langId));
        const color = rendererRef.current?.getLanguageColor(language) || '#666666';
        return {
          id: parseInt(langId),
          name: language?.name || `Lang${langId}`,
          speakers: speakers as number,
          color
        };
      });
    
    setTopLanguages(sortedLangs);
  }, []);

  const simulationLoop = useCallback(() => {
    if (!simulationRef.current || !rendererRef.current) {
      return;
    }

    if (isRunning) {
      // Run simulation step
      simulationRef.current.step();
      
      // Render
      rendererRef.current.render();
      
      // Update stats every 10 ticks
      if (simulationRef.current.tickCount % 10 === 0) {
        updateStats();
      }
    } else {
      // Still render when paused, just don't step simulation
      rendererRef.current.render();
    }
  }, [isRunning, updateStats]);

  const getFrameDelay = () => {
    // Convert speed slider (1-100) to delay (10-200ms)
    return Math.max(10, 210 - simulationSpeed * 2);
  };

  useEffect(() => {
    initializeSimulation();
    
    const handleResize = () => {
      if (rendererRef.current) {
        rendererRef.current.handleResize();
      }
    };

    const handleKeyPress = (e: KeyboardEvent) => {
      switch (e.key.toLowerCase()) {
        case ' ':
          e.preventDefault();
          setIsRunning(prev => !prev);
          break;
        case 'r':
          initializeSimulation();
          break;
        case 's':
          setShowSidebar(prev => !prev);
          break;
        case 'h':
          setShowHelp(true);
          break;
        case 'escape':
          setSelectedLanguage(null);
          setShowHelp(false);
          break;
      }
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('keydown', handleKeyPress);
    
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('keydown', handleKeyPress);
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    };
  }, [initializeSimulation]);

  useEffect(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    
    const runLoop = () => {
      simulationLoop();
      animationRef.current = setTimeout(runLoop, getFrameDelay());
    };
    
    runLoop();
    
    return () => {
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    };
  }, [simulationLoop, simulationSpeed]);

  const togglePlayPause = () => {
    setIsRunning(prev => !prev);
  };

  const resetSimulation = () => {
    initializeSimulation();
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Language Evolution Simulator</h1>
        <div className="controls">
          <button className="btn primary" onClick={togglePlayPause}>
            {isRunning ? <Pause size={16} /> : <Play size={16} />}
            {isRunning ? 'Pause' : 'Play'}
          </button>
          <button className="btn" onClick={resetSimulation}>
            <RotateCcw size={16} />
            Reset
          </button>
          <button className="btn" onClick={() => setShowSidebar(prev => !prev)}>
            <Info size={16} />
            Stats
          </button>
          <button className="btn" onClick={() => setShowHelp(true)}>
            <HelpCircle size={16} />
            Help
          </button>
          <div className="speed-control">
            <Gauge size={16} />
            <span>Speed:</span>
            <input
              type="range"
              min="1"
              max="100"
              value={simulationSpeed}
              onChange={(e) => setSimulationSpeed(parseInt(e.target.value))}
              className="speed-slider"
            />
            <span>{simulationSpeed}%</span>
          </div>
        </div>
      </header>

      <div className="main-content">
        <div className="canvas-container">
          <canvas ref={canvasRef} />
        </div>

        <div className={`sidebar ${showSidebar ? '' : 'hidden'}`}>
          <div className="stats-section">
            <h3>Simulation Stats</h3>
            <div className="stat-item">
              <span className="stat-label">Tick</span>
              <span className="stat-value">{stats.tick.toLocaleString()}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Communities</span>
              <span className="stat-value">{stats.speakingCommunities}/{stats.communities}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Languages</span>
              <span className="stat-value">{stats.languages}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Largest Language</span>
              <span className="stat-value">{stats.largestLanguage} speakers</span>
            </div>
          </div>

          <div className="stats-section">
            <h3>Top Languages</h3>
            <div className="language-list">
              {topLanguages.map((lang, index) => (
                <div 
                  key={lang.id} 
                  className="language-item"
                  style={{ borderLeftColor: lang.color }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>#{index + 1} {lang.name}</span>
                    <span>{lang.speakers} speakers</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="stats-section">
            <h3>Instructions</h3>
            <div style={{ fontSize: '0.8rem', color: '#9ca3af', lineHeight: 1.4 }}>
              <p><kbd>Space</kbd> - Play/Pause</p>
              <p><kbd>R</kbd> - Reset simulation</p>
              <p><kbd>S</kbd> - Toggle sidebar</p>
              <p><kbd>H</kbd> - Show help</p>
              <p><strong>Click</strong> on any region to view language details</p>
            </div>
          </div>
        </div>
      </div>

      {selectedLanguage && (
        <LanguageDetailModal
          language={selectedLanguage}
          onClose={() => setSelectedLanguage(null)}
        />
      )}

      {showHelp && (
        <HelpModal onClose={() => setShowHelp(false)} />
      )}
    </div>
  );
}

export default App;