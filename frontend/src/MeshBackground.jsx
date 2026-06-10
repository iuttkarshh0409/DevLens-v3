import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';

export default function MeshBackground() {
  const shouldReduceMotion = useReducedMotion();

  // Drift animations for the three radial orbs
  const orb1Animate = shouldReduceMotion
    ? {}
    : {
        x: [0, 80, -40, 0],
        y: [0, -60, 50, 0],
        transition: {
          duration: 24,
          repeat: Infinity,
          ease: "easeInOut",
        },
      };

  const orb2Animate = shouldReduceMotion
    ? {}
    : {
        x: [0, -90, 50, 0],
        y: [0, 70, -60, 0],
        transition: {
          duration: 28,
          repeat: Infinity,
          ease: "easeInOut",
        },
      };

  const orb3Animate = shouldReduceMotion
    ? {}
    : {
        x: [0, 50, -80, 0],
        y: [0, 80, -40, 0],
        transition: {
          duration: 32,
          repeat: Infinity,
          ease: "easeInOut",
        },
      };

  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden pointer-events-none z-0">
      {/* 1. Void base */}
      <div className="absolute inset-0 bg-[#050505]" />

      {/* 2. Lattice grid */}
      <div 
        className="absolute inset-0 opacity-70"
        style={{
          backgroundImage: `
            linear-gradient(rgba(16, 185, 129, 0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(16, 185, 129, 0.06) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
          maskImage: 'radial-gradient(circle at center, black 30%, transparent 85%)',
          WebkitMaskImage: 'radial-gradient(circle at center, black 30%, transparent 85%)',
        }}
      />

      {/* 3. Three drifting radial orbs */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Orb 1 — Emerald */}
        <motion.div
          animate={orb1Animate}
          className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] max-w-[500px] max-h-[500px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0) 70%)',
            filter: 'blur(80px)',
          }}
        />

        {/* Orb 2 — Sky */}
        <motion.div
          animate={orb2Animate}
          className="absolute top-[20%] right-[-10%] w-[45vw] h-[45vw] max-w-[450px] max-h-[450px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, rgba(56, 189, 248, 0) 70%)',
            filter: 'blur(90px)',
          }}
        />

        {/* Orb 3 — Indigo */}
        <motion.div
          animate={orb3Animate}
          className="absolute bottom-[-10%] left-[10%] w-[45vw] h-[45vw] max-w-[450px] max-h-[450px] rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0) 70%)',
            filter: 'blur(100px)',
          }}
        />
      </div>

      {/* 4. SVG noise overlay */}
      <div 
        className="absolute inset-0 opacity-[0.03] mix-blend-overlay"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
        }}
      />

      {/* 5. Vignette */}
      <div 
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(circle at center, transparent 40%, rgba(0, 0, 0, 0.7) 100%)'
        }}
      />
    </div>
  );
}
