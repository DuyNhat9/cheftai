import React, { useState } from 'react';
import Onboarding from './components/Onboarding';
import IngredientInput from './components/IngredientInput';
import LoadingScreen from './components/LoadingScreen';
import RecipeResult from './components/RecipeResult';
import PromptBuilder from './components/PromptBuilder';
import { generateRecipe } from './services/geminiService';
import { AppState, Recipe } from './types';

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>(AppState.ONBOARDING);
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [showPromptHelper, setShowPromptHelper] = useState<boolean>(true);

  const handleStart = () => {
    setAppState(AppState.INPUT);
  };

  const handleBackToInput = () => {
    setAppState(AppState.INPUT);
  };
  
  const handleBackToOnboarding = () => {
    setAppState(AppState.ONBOARDING);
  };

  const handleGenerate = async (ingredients: string[]) => {
    setAppState(AppState.GENERATING);
    try {
      const generatedRecipe = await generateRecipe(ingredients);
      setRecipe(generatedRecipe);
      setAppState(AppState.RESULT);
    } catch (error) {
      console.error(error);
      // In a real app, show a toast or error modal. 
      // For now, go back to input to try again.
      alert("Something went wrong generating the recipe. Please try again.");
      setAppState(AppState.INPUT);
    }
  };

  return (
    <main className="w-full max-w-[100vw] overflow-hidden bg-slate-950 text-slate-50 min-h-screen">
      <header className="w-full flex items-center justify-between px-4 sm:px-6 py-3 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur z-10">
        <div className="flex items-center gap-2">
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-500 text-slate-950 font-bold text-lg shadow-md shadow-emerald-500/40">
            C
          </span>
          <div className="flex flex-col">
            <span className="text-sm font-semibold tracking-tight">CheftAi Playground</span>
            <span className="text-[11px] text-slate-400">
              Chuyển nhanh giữa Recipe Generator và Cursor Prompt Helper
            </span>
          </div>
        </div>
        <div className="inline-flex items-center gap-1 rounded-full bg-slate-900/90 border border-slate-700 p-1 text-xs">
          <button
            type="button"
            onClick={() => setShowPromptHelper(false)}
            className={`px-3 py-1.5 rounded-full font-medium transition ${
              !showPromptHelper
                ? 'bg-slate-800 text-slate-50 shadow-sm'
                : 'text-slate-400 hover:text-slate-100'
            }`}
          >
            Recipe mode
          </button>
          <button
            type="button"
            onClick={() => setShowPromptHelper(true)}
            className={`px-3 py-1.5 rounded-full font-medium transition ${
              showPromptHelper
                ? 'bg-emerald-500 text-slate-950 shadow-sm shadow-emerald-500/40'
                : 'text-slate-400 hover:text-slate-100'
            }`}
          >
            Prompt Helper
          </button>
        </div>
      </header>

      {showPromptHelper ? (
        <PromptBuilder />
      ) : (
        <div className="w-full max-w-[100vw] overflow-hidden">
          {appState === AppState.ONBOARDING && <Onboarding onStart={handleStart} />}
          {appState === AppState.INPUT && (
            <IngredientInput onGenerate={handleGenerate} onBack={handleBackToOnboarding} />
          )}
          {appState === AppState.GENERATING && <LoadingScreen />}
          {appState === AppState.RESULT && recipe && (
            <RecipeResult recipe={recipe} onRestart={handleBackToInput} />
          )}
        </div>
      )}
    </main>
  );
};

export default App;