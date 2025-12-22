import React from 'react';

const LoadingScreen: React.FC = () => {
  return (
    <div className="flex h-screen w-full flex-col items-center justify-center bg-background-dark text-white p-6">
      <div className="relative w-24 h-24 mb-8">
         <div className="absolute inset-0 border-4 border-surface-dark rounded-full"></div>
         <div className="absolute inset-0 border-4 border-primary rounded-full border-t-transparent animate-spin"></div>
         <div className="absolute inset-0 flex items-center justify-center">
            <span className="material-symbols-outlined text-3xl text-primary animate-pulse">restaurant</span>
         </div>
      </div>
      
      <h2 className="text-2xl font-bold mb-2 text-center animate-pulse">Thinking...</h2>
      <p className="text-white/60 text-center max-w-xs">
        Our AI chef is reviewing your ingredients and crafting the perfect dish.
      </p>
    </div>
  );
};

export default LoadingScreen;