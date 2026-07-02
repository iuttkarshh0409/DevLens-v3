import React from 'react';

export const NavigationHeader = () => {
  return (
    <div className="flex justify-between items-center py-6 border-b border-brand-borderDefault mb-16 relative z-10">
      <div className="flex items-center gap-2 bg-brand-borderDefault/10 border border-brand-borderDefault rounded-full px-4 py-1.5 font-mono text-[10px] sm:text-xs font-bold text-brand-textPrimary tracking-widest">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-purple opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-purple"></span>
        </span>
        NAMESPACE // DEVLENS
      </div>
      <div className="font-mono text-[10px] sm:text-xs text-brand-textSecondary tracking-widest uppercase">
        SWAYAM_SANCHAY / V2.6
      </div>
    </div>
  );
};

export default NavigationHeader;
