import React, { useState, useRef, useEffect } from 'react';
import { Ingredient } from '../types';

interface IngredientInputProps {
  onGenerate: (ingredients: string[]) => void;
  onBack: () => void;
}

const COMMON_INGREDIENTS = [
  "Chicken Breast", "Eggs", "Pasta", "Tomato", "Onion", "Garlic", "Spinach", "Rice", "Milk", "Cheese", "Lemon", "Potato"
];

const IngredientInput: React.FC<IngredientInputProps> = ({ onGenerate, onBack }) => {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [inputValue, setInputValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const addIngredient = (name: string) => {
    if (!name.trim()) return;
    const isDuplicate = ingredients.some(i => i.name.toLowerCase() === name.toLowerCase());
    if (isDuplicate) {
        setInputValue('');
        return;
    }
    
    setIngredients([...ingredients, { id: Date.now().toString(), name: name.trim() }]);
    setInputValue('');
  };

  const removeIngredient = (id: string) => {
    setIngredients(ingredients.filter(i => i.id !== id));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      addIngredient(inputValue);
    }
  };

  return (
    <div className="relative flex h-screen w-full flex-col bg-background-dark text-white font-display overflow-hidden animate-fade-in">
        {/* Background gradient hint */}
        <div className="absolute top-0 left-0 right-0 h-64 bg-gradient-to-b from-primary/10 to-transparent pointer-events-none"></div>

        {/* Header */}
        <div className="relative z-10 flex items-center justify-between p-6 pt-safe">
            <button onClick={onBack} className="p-2 -ml-2 rounded-full hover:bg-white/10 transition-colors">
                <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <h2 className="text-lg font-semibold">My Fridge</h2>
            <div className="w-10"></div> {/* Spacer for alignment */}
        </div>

        <div className="flex-1 flex flex-col w-full max-w-md mx-auto px-6 overflow-hidden">
            <h1 className="text-3xl font-bold mb-2">What's inside?</h1>
            <p className="text-white/60 mb-8">Add 3+ ingredients for the best result.</p>

            {/* Input Area */}
            <div className="relative mb-6">
                <input
                    ref={inputRef}
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="e.g., Avocado, Chicken..."
                    className="w-full bg-surface-dark border-2 border-transparent focus:border-primary rounded-xl px-5 py-4 text-lg placeholder:text-white/30 outline-none transition-all shadow-inner"
                />
                <button 
                    onClick={() => addIngredient(inputValue)}
                    className={`absolute right-3 top-3 p-2 rounded-lg bg-primary/20 text-primary hover:bg-primary hover:text-white transition-all ${!inputValue.trim() ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}
                >
                    <span className="material-symbols-outlined text-xl">add</span>
                </button>
            </div>

            {/* Selected Ingredients List */}
            <div className="flex-1 overflow-y-auto no-scrollbar pb-4">
                <div className="flex flex-wrap gap-2 mb-8">
                    {ingredients.map(ing => (
                        <div key={ing.id} className="animate-fade-in flex items-center bg-primary/20 text-blue-100 px-3 py-1.5 rounded-lg border border-primary/20">
                            <span className="font-medium mr-2">{ing.name}</span>
                            <button onClick={() => removeIngredient(ing.id)} className="hover:text-white transition-colors flex items-center">
                                <span className="material-symbols-outlined text-lg">close</span>
                            </button>
                        </div>
                    ))}
                    {ingredients.length === 0 && (
                        <div className="w-full text-center py-10 opacity-30">
                            <span className="material-symbols-outlined text-6xl mb-2">kitchen</span>
                            <p>Your fridge is empty</p>
                        </div>
                    )}
                </div>

                {/* Suggestions */}
                {ingredients.length < 5 && (
                    <div className="animate-slide-up">
                        <p className="text-sm font-semibold text-white/50 uppercase tracking-wider mb-3">Popular Items</p>
                        <div className="flex flex-wrap gap-2">
                            {COMMON_INGREDIENTS.filter(name => !ingredients.some(i => i.name.toLowerCase() === name.toLowerCase())).slice(0, 8).map(item => (
                                <button 
                                    key={item}
                                    onClick={() => addIngredient(item)}
                                    className="bg-surface-dark hover:bg-white/10 border border-white/5 rounded-full px-4 py-2 text-sm transition-all"
                                >
                                    + {item}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Action Bar */}
            <div className="pb-8 pt-4">
                <button
                    disabled={ingredients.length === 0}
                    onClick={() => onGenerate(ingredients.map(i => i.name))}
                    className="group relative w-full flex items-center justify-center overflow-hidden rounded-xl h-14 bg-primary hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-[0_4px_20px_rgba(19,127,236,0.3)] active:scale-[0.98]"
                >
                    <span className="material-symbols-outlined mr-2 text-2xl animate-pulse-slow">auto_awesome</span>
                    <span className="text-white text-lg font-bold">Generate Recipe</span>
                </button>
            </div>
        </div>
    </div>
  );
};

export default IngredientInput;