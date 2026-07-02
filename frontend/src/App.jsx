import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Github, Clipboard, ArrowRight, CheckCircle2, AlertCircle, Download, Zap, FileText, Sparkles } from 'lucide-react';
import { cn } from './utils/cn';

// Subcomponents
import MeshBackground from './MeshBackground';
import UTCClock from './components/UTCClock';
import NavigationHeader from './components/NavigationHeader';
import AnimatedScore from './components/AnimatedScore';
import Badge from './components/Badge';
import Card from './components/Card';
import PremiumButton from './components/PremiumButton';
import TerminalLoader from './components/TerminalLoader';
import ChecklistItem from './components/ChecklistItem';

// API Service
import { fetchAuditReport } from './services/api';

export default function App() {
  const [view, setView] = useState('LANDING');
  const [repoUrl, setRepoUrl] = useState('');
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const performAudit = async (url) => {
    if (!url.includes('github.com/')) {
        setError("Please enter a valid GitHub repository URL");
        return;
    }
    setView('LOADING');
    setError(null);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000);

    try {
      const resData = await fetchAuditReport(url, controller.signal);
      clearTimeout(timeoutId);
      setData(resData);
      
      // Let the terminal stream finish nicely
      setTimeout(() => {
        setView('RESULTS');
      }, 3000);
    } catch (err) {
      setError(err.name === 'AbortError' ? "Analysis timed out" : err.message);
      setView('LANDING');
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text.includes('github.com')) setRepoUrl(text);
    } catch (err) {}
  };

  const handleSaveAnalysis = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `devlens-audit-${data.score}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-bg-base text-brand-textSecondary font-sans selection:bg-brand-purple/20 selection:text-brand-textPrimary relative overflow-hidden">
      {/* Dynamic system background */}
      <MeshBackground />

      <div className="relative z-10 max-w-7xl mx-auto px-6 sm:px-12 flex flex-col justify-between min-h-screen pb-12">
        <div>
          {/* Top navigation header */}
          <NavigationHeader />

          <AnimatePresence mode="wait">
            {/* 1. LANDING VIEW */}
            {view === 'LANDING' && (
              <motion.div 
                key="landing"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="max-w-4xl mx-auto pt-8 pb-12 text-center space-y-16"
              >
                <div className="space-y-6">
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-brand-purple/20 bg-brand-purple/5 text-brand-purple text-xs font-mono tracking-widest uppercase">
                    <Sparkles className="w-3.5 h-3.5" /> system_status: ready_for_audit
                  </div>
                  
                  {/* Outfit light mixed with mono caret on the same line */}
                  <h1 className="text-4xl sm:text-5xl lg:text-7xl font-display font-light tracking-tight text-brand-textPrimary leading-tight">
                    code that <span className="text-brand-purple font-mono font-normal tracking-wide inline-block border-r-2 border-brand-purple pr-1 animate-caret">closes_deals.log</span>
                  </h1>
                  
                  <p className="max-w-2xl mx-auto text-brand-textSecondary text-sm sm:text-base md:text-lg leading-relaxed font-sans">
                    DevLens performs industrial-grade audits on your GitHub repositories to surface the hiring signals recruiters actually look for.
                  </p>
                </div>

                <div className="relative max-w-2xl mx-auto group">
                  <div className="absolute -inset-0.5 bg-brand-purple rounded-2xl blur opacity-10 transition-all duration-300 group-within:opacity-30 group-within:blur-md" />
                  
                  <div className="relative bg-bg-surface border border-brand-borderDefault p-2.5 rounded-2xl flex flex-col sm:flex-row gap-2">
                    <div className="flex-1 flex items-center px-4 gap-3 bg-transparent">
                      <Github className="w-5 h-5 text-brand-textInverse group-within:text-brand-purple transition-colors" />
                      <input 
                        type="text"
                        placeholder="URL: github.com/user/project"
                        className="w-full bg-transparent border-none outline-none py-3 text-brand-textPrimary placeholder:text-brand-textInverse font-mono text-sm focus-visible:ring-0"
                        value={repoUrl}
                        onChange={(e) => setRepoUrl(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && performAudit(repoUrl)}
                        aria-label="GitHub Repository URL"
                      />
                      <motion.button 
                        whileHover={{ scale: 1.05, color: "#995cd6" }}
                        whileTap={{ scale: 0.95 }}
                        onClick={handlePaste} 
                        className="text-brand-textInverse transition-colors p-2"
                        aria-label="Paste from clipboard"
                      >
                        <Clipboard className="w-4 h-4" />
                      </motion.button>
                    </div>
                    
                    <PremiumButton onClick={() => performAudit(repoUrl)} disabled={!repoUrl.includes('github.com/')}>
                      Analyze <ArrowRight className="w-4 h-4" />
                    </PremiumButton>
                  </div>
                </div>

                {error && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="max-w-md mx-auto p-4 bg-rose-950/20 backdrop-blur border border-rose-500/20 text-rose-400 rounded-xl flex items-center gap-3"
                  >
                    <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
                    <p className="text-xs font-mono text-left leading-snug">{error}</p>
                  </motion.div>
                )}

                {/* Simulated static system logger under search */}
                <div className="w-full max-w-2xl mx-auto bg-black border border-brand-borderDefault rounded-xl p-5 font-mono text-xs text-left scanlines text-brand-textSecondary shadow-2xl">
                  <div className="flex items-center justify-between pb-2 border-b border-brand-borderDefault mb-3 text-brand-textInverse">
                    <span>$ whoami --verbose</span>
                    <span>guest@devlens</span>
                  </div>
                  <div className="space-y-1.5 text-brand-textPrimary">
                    <div><span className="text-brand-textSecondary">NAME:</span> DevLens Repository Auditor</div>
                    <div><span className="text-brand-textSecondary">VERSION:</span> 2.6.0-stable</div>
                    <div><span className="text-brand-textSecondary">ROLES:</span> Technical Recruiter / Code Quality Assessor</div>
                    <div><span className="text-brand-textSecondary">METRICS:</span> CI/CD, Documentation, Licensing, Setup guide</div>
                    <div><span className="text-brand-textSecondary">STATUS:</span> Awaiting target repository URL...</div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* 2. LOADING VIEW */}
            {view === 'LOADING' && (
              <motion.div 
                key="loading"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.02 }}
                transition={{ duration: 0.3 }}
                className="max-w-4xl mx-auto pt-16 pb-12 text-center space-y-12"
              >
                <div className="space-y-4">
                  <div className="inline-block px-3 py-1 bg-brand-purple/5 border border-brand-purple/20 text-brand-purple font-mono text-xs rounded-full uppercase tracking-wider">
                    RUNNING PROCESS
                  </div>
                  <h2 className="text-2xl font-display font-light text-brand-textPrimary tracking-tight uppercase">Quantifying Skillset...</h2>
                </div>
                
                {/* Advanced simulated terminal logger */}
                <TerminalLoader />
              </motion.div>
            )}

            {/* 3. RESULTS VIEW */}
            {view === 'RESULTS' && data && (
              <motion.div 
                key="results"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="max-w-6xl mx-auto space-y-12 pb-16"
              >
                {/* Results Screen Sub Header controls */}
                <div className="flex justify-between items-center pb-6 border-b border-brand-borderDefault">
                  <PremiumButton variant="ghost" onClick={() => setView('LANDING')} className="px-0">
                    <ArrowRight className="w-4 h-4 rotate-180" /> <span className="uppercase tracking-widest text-[10px] font-mono font-bold">New Audit</span>
                  </PremiumButton>
                  <PremiumButton onClick={handleSaveAnalysis} variant="secondary">
                    <Download className="w-4 h-4" /> Save Analysis
                  </PremiumButton>
                </div>

                {/* Main Scorecard Section */}
                <section className="relative text-center py-8">
                  <div className="space-y-4">
                    <span className="text-brand-textInverse text-xs font-mono uppercase tracking-[0.2em]">Recruiter Scorecard</span>
                    
                    {/* Score display */}
                    <div className="text-[8rem] sm:text-[11rem] md:text-[13rem] font-light leading-none tracking-tighter text-brand-textPrimary font-display flex items-center justify-center">
                      <AnimatedScore value={data.score} />
                      <span className="text-brand-textInverse text-3xl sm:text-4xl md:text-5xl font-mono self-end mb-6 sm:mb-8 md:mb-10 ml-2">/10</span>
                    </div>

                    <div className="flex justify-center">
                      <Badge status={data.status}>{data.status}</Badge>
                    </div>
                  </div>
                </section>

                {/* Executive Verdict Bento Panel */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  <Card className="lg:col-span-2 space-y-6" accent="emerald">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-px bg-brand-borderDefault" />
                      <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-brand-purple/80">Recruiter Verdict</span>
                    </div>
                    <p className="text-xl sm:text-2xl font-light text-brand-textPrimary leading-relaxed font-sans">
                      "{data.feedback}"
                    </p>
                  </Card>

                  <Card className="bg-gradient-to-br from-brand-purple/5 via-transparent to-transparent border-brand-purple/15 place-content-center shadow-lg" accent="sky">
                    <div className="space-y-5">
                      <div className="flex items-center gap-3">
                        <div className="p-2 border border-brand-purple/20 rounded-xl bg-brand-purple/5">
                          <Zap className="w-5 h-5 text-brand-purple fill-brand-purple/10" />
                        </div>
                        <span className="text-[10px] font-mono font-bold text-brand-purple uppercase tracking-widest">
                          {data.wow_insight?.title || 'Signal Detected'}
                        </span>
                      </div>
                      <p className="text-base sm:text-lg font-medium text-brand-textPrimary leading-relaxed">
                        {data.wow_insight?.description}
                      </p>
                    </div>
                  </Card>
                </div>

                {/* Priority items & document status checklist */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {/* Checklist Grid */}
                  <Card accent="amber">
                    <div className="flex items-center justify-between mb-8">
                      <div className="flex items-center gap-3">
                        <div className="p-2 border border-brand-purple/20 rounded-xl bg-brand-purple/5">
                          <Zap className="w-5 h-5 text-brand-purple" />
                        </div>
                        <h3 className="text-brand-textPrimary font-mono font-bold uppercase tracking-widest text-xs">Hiring Priority Items</h3>
                      </div>
                      <span className="font-mono text-[10px] text-brand-textInverse">SYSTEM.LOG_PRIORITIES</span>
                    </div>

                    <div className="space-y-4">
                      {data.checklist && data.checklist.map((item, id) => (
                         <ChecklistItem key={id} item={item} id={id} />
                      ))}
                    </div>
                  </Card>

                  {/* Documentation Health */}
                  <Card accent="sky">
                    <div className="flex items-center justify-between mb-8">
                      <div className="flex items-center gap-3">
                        <div className="p-2 border border-brand-purple/20 rounded-xl bg-brand-purple/5">
                          <FileText className="w-5 h-5 text-brand-purple" />
                        </div>
                        <h3 className="text-brand-textPrimary font-mono font-bold uppercase tracking-widest text-xs">Documentation Health</h3>
                      </div>
                      <span className="font-mono text-[10px] text-brand-textInverse">SYSTEM.LOG_DOCS</span>
                    </div>

                    <div className="space-y-3">
                      {data.readme_audits && data.readme_audits.map((audit, id) => (
                         <motion.div 
                          key={id} 
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.5 + (id * 0.05) }}
                          className="group flex items-center justify-between p-4 bg-black border border-brand-borderDefault rounded-xl hover:border-brand-purple/30 transition-colors"
                         >
                            <div className="flex items-center gap-3">
                              {audit.passed ? (
                                  <div className="w-6 h-6 rounded-lg bg-brand-purple/10 flex items-center justify-center border border-brand-purple/20">
                                    <CheckCircle2 className="w-4 h-4 text-brand-purple" />
                                  </div>
                              ) : (
                                  <div className="w-6 h-6 rounded-lg bg-rose-500/10 flex items-center justify-center border border-rose-500/20">
                                    <AlertCircle className="w-4 h-4 text-rose-500" />
                                  </div>
                              )}
                              <span className={cn(
                                "text-sm font-sans font-medium transition-all",
                                audit.passed ? "text-brand-textPrimary" : "text-brand-textInverse line-through decoration-zinc-700/50"
                              )}>{audit.label}</span>
                            </div>
                            <span className="font-mono text-[9px] text-brand-textInverse">
                              {audit.passed ? "PASSED" : "FAILED"}
                            </span>
                         </motion.div>
                      ))}
                    </div>
                  </Card>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Systems Footer */}
        <div className="border-t border-brand-borderDefault pt-8 mt-12 flex flex-col md:flex-row justify-between items-center gap-6 z-10 relative">
          <div className="text-brand-textInverse font-mono text-[10px] uppercase tracking-widest text-center md:text-left">
            DEV_LENS // AUDIT REPORT SYSTEM V2.6
          </div>
          
          {/* Live UTC Clock */}
          <UTCClock />

          <div className="font-mono text-[10px] text-brand-textInverse uppercase tracking-widest text-center md:text-right">
            continuously_in_motion
          </div>
        </div>
      </div>
    </div>
  );
}
