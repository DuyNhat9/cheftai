import React from 'react';

interface OnboardingProps {
  onStart: () => void;
}

const Onboarding: React.FC<OnboardingProps> = ({ onStart }) => {
  return (
    <div className="relative flex h-screen w-full flex-col overflow-hidden bg-background-dark group/design-root font-display">
      {/* Dynamic Background Layer */}
      <div className="absolute inset-0 z-0 h-full w-full">
        <img
          className="h-full w-full object-cover opacity-90 transition-transform duration-[20s] ease-in-out hover:scale-105"
          alt="Close up of chef cutting fresh vegetables on a wooden board"
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuBoUjAXx8LU_5PsPnCxsfbS-1cx1RSBDdcLq-JjIfWqYyXtmXE8mNpUqAtY7qcjqV-7pEd52Bj_zS_DF4ktVd0__lnNUriQyekEVflFTsgu6rXEpnNH4ubYxYy6F8t-B8XZkVcwI6Cy4v59szmnoFJk8zhUsDrOm_rqS_5STSMTMI2QwCqcgnZ-WwEM_P13PcVFIelrNEIVW4Kbss8QGymiJWScgbl1cfhYhw82ZR9C1EDNgXP7FTjHK0SZFDIBP__weKiYjQSqolAm"
        />
      </div>

      {/* Gradient Overlay for Contrast */}
      <div className="gradient-overlay absolute inset-0 z-10 pointer-events-none"></div>

      {/* Main Content Container */}
      <div className="relative z-20 flex h-full w-full flex-col justify-end px-4 pb-10 pt-safe animate-fade-in">
        <div className="flex flex-col items-center w-full max-w-md mx-auto">
          {/* Visual Indicator of AI/Magic */}
          <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-white/10 backdrop-blur-md border border-white/10 shadow-lg animate-slide-up">
            <span className="material-symbols-outlined text-primary text-4xl">auto_awesome</span>
          </div>

          {/* HeadlineText */}
          <h1 className="text-white tracking-tight text-[36px] font-extrabold leading-tight px-2 text-center pb-4 drop-shadow-sm animate-slide-up" style={{ animationDelay: '0.1s' }}>
            Cook smarter,<br />not harder.
          </h1>

          {/* BodyText */}
          <p className="text-white/90 text-[17px] font-normal leading-relaxed pb-8 px-4 text-center animate-slide-up" style={{ animationDelay: '0.2s' }}>
            Let AI create the perfect recipe from what's in your fridge.
          </p>

          {/* SingleButton */}
          <div className="w-full px-2 pb-4 animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <button
              onClick={onStart}
              className="group relative w-full flex cursor-pointer items-center justify-center overflow-hidden rounded-lg h-14 bg-primary hover:bg-primary-hover transition-all duration-200 shadow-[0_0_20px_rgba(19,127,236,0.3)] active:scale-[0.98]"
            >
              <span className="text-white text-[17px] font-bold leading-normal tracking-wide">Start Cooking</span>
              <span className="material-symbols-outlined ml-2 text-white text-xl group-hover:translate-x-1 transition-transform">arrow_forward</span>
            </button>
          </div>

          {/* MetaText */}
          <div className="flex items-center gap-4 pb-4 animate-slide-up" style={{ animationDelay: '0.4s' }}>
            <button className="text-[#9dabb9] text-xs font-medium leading-normal hover:text-white transition-colors">Terms of Service</button>
            <span className="text-[#9dabb9] text-xs">•</span>
            <button className="text-[#9dabb9] text-xs font-medium leading-normal hover:text-white transition-colors">Privacy Policy</button>
          </div>
        </div>

        {/* Safe area spacer */}
        <div className="h-2 w-full"></div>
      </div>
    </div>
  );
};

export default Onboarding;