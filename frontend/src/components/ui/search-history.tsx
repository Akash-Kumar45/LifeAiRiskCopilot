'use client';

import { useState, useEffect, ReactNode } from 'react';
import { ClockIcon, XIcon } from 'lucide-react';

interface SearchHistoryProps {
  onSelectSearch: (term: string) => void;
  currentSearch: string;
  children: ReactNode;
}

export function SearchHistory({ onSelectSearch, currentSearch, children }: SearchHistoryProps) {
  const [history, setHistory] = useState<string[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('searchHistory');
    if (saved) {
      setHistory(JSON.parse(saved));
    }
  }, []);

  const addToHistory = (term: string) => {
    if (!term.trim() || history.includes(term)) return;
    
    const newHistory = [term, ...history.slice(0, 4)];
    setHistory(newHistory);
    localStorage.setItem('searchHistory', JSON.stringify(newHistory));
  };

  const removeFromHistory = (term: string) => {
    const newHistory = history.filter(h => h !== term);
    setHistory(newHistory);
    localStorage.setItem('searchHistory', JSON.stringify(newHistory));
  };

  useEffect(() => {
    if (currentSearch && currentSearch.length > 2) {
      const timer = setTimeout(() => addToHistory(currentSearch), 1000);
      return () => clearTimeout(timer);
    }
  }, [currentSearch]);

  const suggestions = [
    'life insurance model',
    'mortality prediction', 
    'claims processing',
    'risk assessment',
    'underwriting'
  ];

  return (
    <div className="relative">
      <div 
        onFocus={() => setShowHistory(true)}
        onBlur={() => setTimeout(() => setShowHistory(false), 200)}
      >
        {children}
      </div>
      
      {showHistory && (
        <div className="absolute top-full left-0 right-0 bg-white/10 border border-white/20 rounded-lg mt-1 backdrop-blur-sm z-50 max-h-60 overflow-y-auto">
          {history.length > 0 && (
            <div className="p-2 border-b border-white/10">
              <p className="text-xs text-gray-400 mb-2 flex items-center">
                <ClockIcon className="w-3 h-3 mr-1" />
                Recent Searches
              </p>
              {history.map((term, index) => (
                <div key={index} className="flex items-center justify-between py-1 px-2 hover:bg-white/10 rounded group">
                  <button 
                    onClick={() => onSelectSearch(term)}
                    className="text-white text-sm flex-1 text-left"
                  >
                    {term}
                  </button>
                  <button 
                    onClick={() => removeFromHistory(term)}
                    className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-white"
                  >
                    <XIcon className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
          
          <div className="p-2">
            <p className="text-xs text-gray-400 mb-2">Suggestions</p>
            {suggestions.map((suggestion, index) => (
              <button 
                key={index}
                onClick={() => onSelectSearch(suggestion)}
                className="block w-full text-left py-1 px-2 text-white text-sm hover:bg-white/10 rounded"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}