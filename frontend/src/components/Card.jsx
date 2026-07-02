import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../utils/cn';

export const Card = ({ children, className, delay = 0, accent }) => {
  const accentBorders = {
    emerald: "hover:border-brand-purple/40",
    sky: "hover:border-brand-purple/30",
    amber: "hover:border-brand-purple/20"
  };

  return (
    <motion.div 
      initial={{ y: 16, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
      className={cn(
        "relative group glass rounded-2xl p-7 sm:p-8 overflow-hidden transition-all duration-500 border-brand-borderDefault",
        accent ? accentBorders[accent] : "hover:border-brand-purple/40",
        className
      )}
    >
      {children}
    </motion.div>
  );
};

export default Card;
