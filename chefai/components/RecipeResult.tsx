import React from 'react';
import { Recipe } from '../types';

interface RecipeResultProps {
  recipe: Recipe;
  onRestart: () => void;
}

const RecipeResult: React.FC<RecipeResultProps> = ({ recipe, onRestart }) => {
  return (
    <div className="relative flex h-screen w-full flex-col bg-background-dark text-white font-display overflow-hidden animate-fade-in">
       {/* Background Image Header */}
       <div className="absolute top-0 left-0 right-0 h-80 z-0">
          <img 
            src={`https://picsum.photos/800/600?random=${Math.floor(Math.random() * 100)}`} 
            alt="Recipe Result" 
            className="w-full h-full object-cover opacity-60 mask-image-gradient"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background-dark via-background-dark/80 to-transparent"></div>
       </div>

       {/* Top Nav */}
       <div className="relative z-20 flex items-center justify-between p-6 pt-safe">
            <button onClick={onRestart} className="p-2 -ml-2 rounded-full bg-black/20 backdrop-blur-md hover:bg-white/10 transition-colors">
                <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <div className="flex gap-2">
                 <button className="p-2 rounded-full bg-black/20 backdrop-blur-md hover:bg-white/10 transition-colors">
                    <span className="material-symbols-outlined text-primary">favorite</span>
                </button>
            </div>
        </div>

        {/* Content */}
        <div className="relative z-10 flex-1 overflow-y-auto no-scrollbar px-6 pb-20">
            <div className="flex flex-col gap-1 mb-6">
                <div className="flex items-center gap-2 mb-2">
                     <span className={`px-2 py-1 rounded text-xs font-bold uppercase tracking-wide 
                        ${recipe.difficulty === 'Easy' ? 'bg-green-500/20 text-green-400' : 
                          recipe.difficulty === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}`}>
                        {recipe.difficulty}
                     </span>
                     <span className="text-white/50 text-xs">•</span>
                     <span className="text-white/70 text-xs flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px]">schedule</span> {recipe.cookTime}
                     </span>
                     <span className="text-white/50 text-xs">•</span>
                     <span className="text-white/70 text-xs flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px]">local_fire_department</span> {recipe.calories} kcal
                     </span>
                </div>
                <h1 className="text-3xl font-extrabold leading-tight text-white">{recipe.title}</h1>
                <p className="text-white/70 text-base leading-relaxed mt-2">{recipe.description}</p>
            </div>

            {/* Ingredients Section */}
            <div className="mb-8">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary">grocery</span> Ingredients
                </h3>
                <div className="bg-surface-dark rounded-xl p-4 border border-white/5">
                    <ul className="flex flex-col gap-3">
                        {recipe.ingredients.map((ing, idx) => (
                            <li key={idx} className="flex items-start gap-3">
                                <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-primary shrink-0"></div>
                                <span className="text-white/90 text-sm">{ing}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Instructions Section */}
            <div className="mb-8">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                     <span className="material-symbols-outlined text-primary">menu_book</span> Instructions
                </h3>
                <div className="flex flex-col gap-6">
                    {recipe.instructions.map((step, idx) => (
                        <div key={idx} className="flex gap-4">
                            <div className="flex flex-col items-center">
                                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 text-primary font-bold text-sm border border-primary/20 shrink-0">
                                    {idx + 1}
                                </div>
                                {idx !== recipe.instructions.length - 1 && (
                                    <div className="w-0.5 h-full bg-white/10 my-2 rounded-full"></div>
                                )}
                            </div>
                            <p className="text-white/80 text-sm leading-relaxed pt-1">{step}</p>
                        </div>
                    ))}
                </div>
            </div>
            
            <div className="h-10"></div>
        </div>

        {/* Floating Action Button (Optional for sharing/saving) */}
        <div className="absolute bottom-6 left-0 right-0 px-6 flex justify-center z-20">
             <button onClick={onRestart} className="bg-surface-dark border border-white/10 shadow-xl hover:bg-white/10 text-white font-medium py-3 px-6 rounded-full flex items-center gap-2 transition-all">
                <span className="material-symbols-outlined">restart_alt</span>
                Create Another
             </button>
        </div>
    </div>
  );
};

export default RecipeResult;