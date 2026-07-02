import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../utils/cn';

export const PremiumButton = ({ children, onClick, disabled, className, variant = 'primary' }) => {
  const styles = {
    primary: "bg-brand-purple hover:bg-brand-purple/95 text-white font-mono font-bold uppercase tracking-wider shadow-[0_0_20px_rgba(153,92,214,0.3)]",
    secondary: "bg-brand-surface hover:bg-zinc-900 text-brand-textPrimary border border-brand-borderDefault font-mono font-bold uppercase tracking-wider",
    ghost: "bg-transparent text-brand-textSecondary hover:text-white font-mono font-bold uppercase tracking-wider"
  };

  return (
    <motion.button
      whileHover={disabled ? {} : { 
        scale: 1.02, 
        y: -2,
        transition: { duration: 0.2, ease: "easeOut" } 
      }}
      whileTap={disabled ? {} : { 
        scale: 0.98,
        y: 0 
      }}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "relative rounded-xl font-bold px-6 py-3.5 transition-all flex items-center justify-center gap-2 text-xs focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-purple",
        styles[variant],
        disabled && "opacity-45 cursor-not-allowed",
        className
      )}
    >
      {children}
    </motion.button>
  );
};

export default PremiumButton;
