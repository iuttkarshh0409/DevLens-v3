import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../utils/cn';

export const Badge = ({ children, status }) => {
  const styles = {
    "ELITE": "bg-brand-purple/10 text-brand-textPrimary border-brand-purple/40 shadow-1",
    "STRONG": "bg-brand-purple/15 text-brand-textPrimary border-brand-purple/30 shadow-2",
    "INTERVIEW": "bg-brand-purple/10 text-brand-textPrimary border-brand-purple/20",
    "POLISH": "bg-zinc-800 text-brand-textSecondary border-brand-borderStrong",
    "REJECT": "bg-rose-500/10 text-rose-400 border-rose-500/20",
    "Audit Failed": "bg-zinc-900 text-brand-textInverse border-brand-borderDefault"
  };
  return (
    <motion.span 
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={cn(
        "px-4 py-1.5 rounded-full border text-[10px] font-mono font-bold uppercase tracking-widest transition-all",
        styles[status] || styles['Audit Failed']
      )}
    >
      {children}
    </motion.span>
  );
};

export default Badge;
