import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { cn } from '../utils/cn';

export const ChecklistItem = ({ item, id }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.div 
      layout
      className="group bg-brand-surface border border-brand-borderDefault rounded-xl overflow-hidden cursor-pointer hover:border-brand-purple/30 transition-all border-l-2 border-l-brand-purple"
      onClick={() => setIsOpen(!isOpen)}
    >
      <div className="flex items-center justify-between p-5 select-none font-mono text-xs">
        <div className="flex items-center gap-3">
          {item.impact === 'High' ? (
            <div className="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.5)]" />
          ) : (
            <div className="w-2 h-2 rounded-full bg-brand-purple" />
          )}
          <span className="font-bold text-brand-textPrimary">
            {item.title}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className={cn(
            "text-[9px] font-bold uppercase px-2 py-0.5 rounded-full border",
            item.impact === 'High' ? 'text-rose-400 border-rose-500/20 bg-rose-500/5' : 'text-brand-textInverse border-brand-borderDefault bg-brand-borderDefault/10'
          )}>
            {item.impact}
          </span>
          <motion.div animate={{ rotate: isOpen ? 180 : 0 }}>
            <ArrowRight className="w-4 h-4 rotate-90 text-brand-textInverse" />
          </motion.div>
        </div>
      </div>
      
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
            className="px-5 pb-5 overflow-hidden"
          >
            <div className="border-t border-brand-borderDefault pt-4">
              <div className="bg-black border border-brand-borderDefault rounded-lg p-4 font-mono text-xs text-left scanlines text-brand-textSecondary">
                <div className="text-brand-textInverse mb-2 pb-2 border-b border-brand-borderDefault">
                  $ cat /audit/priority_{String(id + 1).padStart(2, '0')}.md
                </div>
                <div className="flex gap-2">
                  <span className="text-brand-purple select-none">[+]</span>
                  <p className="text-brand-textPrimary leading-relaxed font-sans">{item.hiring_impact || item.reasoning}</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ChecklistItem;
