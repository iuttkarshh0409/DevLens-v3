import React, { useState, useEffect } from 'react';

export const UTCClock = () => {
  const [time, setTime] = useState("");
  useEffect(() => {
    const updateTime = () => {
      const date = new Date();
      const h = String(date.getUTCHours()).padStart(2, '0');
      const m = String(date.getUTCMinutes()).padStart(2, '0');
      const s = String(date.getUTCSeconds()).padStart(2, '0');
      setTime(`[UTC ${h}:${m}:${s}] — sys.clock.synced`);
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-2 font-mono text-[10px] sm:text-xs text-brand-purple tracking-widest uppercase">
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-purple opacity-75"></span>
        <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-purple"></span>
      </span>
      {time}
    </div>
  );
};

export default UTCClock;
