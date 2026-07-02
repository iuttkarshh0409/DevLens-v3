import React, { useState, useEffect } from 'react';
import { animate } from 'framer-motion';

export const AnimatedScore = ({ value }) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const controls = animate(0, value, {
      duration: 1.0,
      ease: [0.16, 1, 0.3, 1], // Custom cubic-bezier for snappy, premium feel
      onUpdate: (latest) => setDisplayValue(latest),
    });
    return () => controls.stop();
  }, [value]);

  return (
    <span className="tabular-nums font-mono font-light text-brand-textPrimary">
      {displayValue.toFixed(1)}
    </span>
  );
};

export default AnimatedScore;
