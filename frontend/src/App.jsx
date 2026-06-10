import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence, animate } from 'framer-motion';
import { Github, Clipboard, ArrowRight, CheckCircle2, AlertCircle, Download, Zap, FileText, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import MeshBackground from './MeshBackground';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// --- CONFIGURATION ---
const API_BASE_URL = window.location.hostname === "localhost" ? "http://localhost:8000" : "";

// --- UI COMPONENTS ---

const UTCClock = () => {
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
    <div className="flex items-center gap-2 font-mono text-[10px] sm:text-xs text-accent-emerald tracking-widest uppercase">
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-emerald opacity-75"></span>
        <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-emerald"></span>
      </span>
      {time}
    </div>
  );
};

const NavigationHeader = () => {
  return (
    <div className="flex justify-between items-center py-6 border-b border-white/5 mb-16 relative z-10">
      <div className="flex items-center gap-2 bg-white/[0.02] border border-white/10 rounded-full px-4 py-1.5 font-mono text-[10px] sm:text-xs font-bold text-white tracking-widest">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-emerald opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-emerald"></span>
        </span>
        DEVLENS_AUDITOR
      </div>
      <div className="font-mono text-[10px] sm:text-xs text-zinc-500 tracking-widest uppercase">
        SWAYAM_SANCHAY / V2.6
      </div>
    </div>
  );
};

const AnimatedScore = ({ value }) => {
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
    <span className="tabular-nums font-mono font-light text-white">
      {displayValue.toFixed(1)}
    </span>
  );
};

const Badge = ({ children, status }) => {
  const styles = {
    "ELITE": "bg-accent-emerald/10 text-accent-emerald border-accent-emerald/20 shadow-[0_0_15px_rgba(16,185,129,0.15)]",
    "STRONG": "bg-accent-sky/10 text-accent-sky border-accent-sky/20 shadow-[0_0_15px_rgba(56,189,248,0.15)]",
    "INTERVIEW": "bg-accent-emerald/10 text-accent-emerald border-accent-emerald/20 shadow-[0_0_15px_rgba(16,185,129,0.15)]",
    "POLISH": "bg-accent-amber/10 text-accent-amber border-accent-amber/20 shadow-[0_0_15px_rgba(251,191,36,0.15)]",
    "REJECT": "bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-[0_0_15px_rgba(244,63,94,0.15)]",
    "Audit Failed": "bg-zinc-800 text-zinc-400 border-zinc-700"
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

const Card = ({ children, className, delay = 0, accent }) => {
  const accentBorders = {
    emerald: "hover:border-accent-emerald/30",
    sky: "hover:border-accent-sky/30",
    amber: "hover:border-accent-amber/30"
  };

  return (
    <motion.div 
      initial={{ y: 16, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
      className={cn(
        "relative group glass rounded-2xl p-7 sm:p-8 overflow-hidden transition-all duration-500",
        accent ? accentBorders[accent] : "hover:border-accent-emerald/30",
        className
      )}
    >
      {children}
    </motion.div>
  );
};

const PremiumButton = ({ children, onClick, disabled, className, variant = 'primary' }) => {
  const styles = {
    primary: "bg-accent-emerald hover:bg-accent-emeraldLight text-black font-mono font-bold uppercase tracking-wider shadow-[0_0_20px_rgba(16,185,129,0.2)]",
    secondary: "bg-bg-surface hover:bg-zinc-900 text-zinc-100 border border-white/10 font-mono font-bold uppercase tracking-wider",
    ghost: "bg-transparent text-zinc-500 hover:text-white font-mono font-bold uppercase tracking-wider"
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
        "relative rounded-xl font-bold px-6 py-3.5 transition-all flex items-center justify-center gap-2 text-xs",
        styles[variant],
        disabled && "opacity-45 cursor-not-allowed",
        className
      )}
    >
      {children}
    </motion.button>
  );
};

const TerminalLoader = () => {
  const [logs, setLogs] = useState([]);
  const allLogs = useMemo(() => [
    "$ devlens --audit --verbose",
    "> Establishing connection with GitHub API...",
    "> Resolving repository metadata...",
    "> Fetching repository file tree structure...",
    "> Extracting README.md file content (decoding Base64)...",
    "> Parsing package descriptors and dependencies...",
    "> Invoking Groq technical analysis model (llama-3.3-70b)...",
    "> Processing scoring algorithm logic...",
    "> Compiling final recruiter scorecard...",
    "> Audit completed successfully."
  ], []);

  useEffect(() => {
    let currentIdx = 0;
    const interval = setInterval(() => {
      if (currentIdx < allLogs.length) {
        setLogs(prev => [...prev, allLogs[currentIdx]]);
        currentIdx++;
      } else {
        clearInterval(interval);
      }
    }, 850);
    return () => clearInterval(interval);
  }, [allLogs]);

  return (
    <div className="w-full max-w-2xl mx-auto bg-black border border-white/10 rounded-xl p-6 font-mono text-xs text-left scanlines text-accent-emerald min-h-[250px] shadow-2xl relative">
      <div className="flex items-center justify-between pb-3 border-b border-white/5 mb-4 text-zinc-500">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
          <span className="w-2.5 h-2.5 rounded-full bg-accent-amber/80" />
          <span className="w-2.5 h-2.5 rounded-full bg-accent-emerald/80" />
        </span>
        <span>bash — 80x24</span>
      </div>
      <div className="space-y-2.5">
        {logs.map((log, i) => (
          <div key={i} className={i === 0 ? "text-zinc-100 font-bold" : ""}>
            {log}
          </div>
        ))}
        <div className="inline-block w-1.5 h-4 bg-accent-emerald animate-caret ml-1" />
      </div>
    </div>
  );
};

// --- APP CORE ---

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
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: url }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      const resData = await response.json();

      if (!response.ok) throw new Error(resData.detail || "Analysis failed");

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
    <div className="min-h-screen bg-bg-base text-zinc-300 font-sans selection:bg-accent-emerald/20 selection:text-accent-emeraldLight relative overflow-hidden">
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
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-accent-emerald/20 bg-accent-emerald/5 text-accent-emerald text-xs font-mono tracking-widest uppercase">
                    <Sparkles className="w-3.5 h-3.5" /> system_status: ready_for_audit
                  </div>
                  
                  {/* Outfit light mixed with mono caret on the same line */}
                  <h1 className="text-4xl sm:text-5xl lg:text-7xl font-display font-light tracking-tight text-white leading-tight">
                    code that <span className="text-accent-emerald font-mono font-normal tracking-wide inline-block border-r-2 border-accent-emerald pr-1 animate-caret">closes_deals.log</span>
                  </h1>
                  
                  <p className="max-w-2xl mx-auto text-zinc-400 text-sm sm:text-base md:text-lg leading-relaxed font-sans">
                    DevLens performs industrial-grade audits on your GitHub repositories to surface the hiring signals recruiters actually look for.
                  </p>
                </div>

                <div className="relative max-w-2xl mx-auto group">
                  <div className="absolute -inset-0.5 bg-accent-emerald rounded-2xl blur opacity-10 transition-all duration-300 group-within:opacity-30 group-within:blur-md" />
                  
                  <div className="relative bg-bg-surface border border-white/10 p-2.5 rounded-2xl flex flex-col sm:flex-row gap-2">
                    <div className="flex-1 flex items-center px-4 gap-3 bg-transparent">
                      <Github className="w-5 h-5 text-zinc-500 group-within:text-accent-emerald transition-colors" />
                      <input 
                        type="text"
                        placeholder="URL: github.com/user/project"
                        className="w-full bg-transparent border-none outline-none py-3 text-white placeholder:text-zinc-700 font-mono text-sm"
                        value={repoUrl}
                        onChange={(e) => setRepoUrl(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && performAudit(repoUrl)}
                      />
                      <motion.button 
                        whileHover={{ scale: 1.05, color: "#10B981" }}
                        whileTap={{ scale: 0.95 }}
                        onClick={handlePaste} 
                        className="text-zinc-500 transition-colors p-2"
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
                <div className="w-full max-w-2xl mx-auto bg-black border border-white/10 rounded-xl p-5 font-mono text-xs text-left scanlines text-zinc-400 shadow-2xl">
                  <div className="flex items-center justify-between pb-2 border-b border-white/5 mb-3 text-zinc-500">
                    <span>$ whoami --verbose</span>
                    <span>guest@devlens</span>
                  </div>
                  <div className="space-y-1.5 text-zinc-300">
                    <div><span className="text-zinc-500">NAME:</span> DevLens Repository Auditor</div>
                    <div><span className="text-zinc-500">VERSION:</span> 2.6.0-stable</div>
                    <div><span className="text-zinc-500">ROLES:</span> Technical Recruiter / Code Quality Assessor</div>
                    <div><span className="text-zinc-500">METRICS:</span> CI/CD, Documentation, Licensing, Setup guide</div>
                    <div><span className="text-zinc-500">STATUS:</span> Awaiting target repository URL...</div>
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
                  <div className="inline-block px-3 py-1 bg-accent-emerald/5 border border-accent-emerald/20 text-accent-emerald font-mono text-xs rounded-full uppercase tracking-wider">
                    RUNNING PROCESS
                  </div>
                  <h2 className="text-2xl font-display font-light text-white tracking-tight uppercase">Quantifying Skillset...</h2>
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
                <div className="flex justify-between items-center pb-6 border-b border-white/5">
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
                    <span className="text-zinc-500 text-xs font-mono uppercase tracking-[0.2em]">Recruiter Scorecard</span>
                    
                    {/* Score display */}
                    <div className="text-[8rem] sm:text-[11rem] md:text-[13rem] font-light leading-none tracking-tighter text-white font-display flex items-center justify-center">
                      <AnimatedScore value={data.score} />
                      <span className="text-zinc-600 text-3xl sm:text-4xl md:text-5xl font-mono self-end mb-6 sm:mb-8 md:mb-10 ml-2">/10</span>
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
                      <div className="w-8 h-px bg-zinc-800" />
                      <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-accent-emerald/80">Recruiter Verdict</span>
                    </div>
                    <p className="text-xl sm:text-2xl font-light text-zinc-100 leading-relaxed font-sans">
                      "{data.feedback}"
                    </p>
                  </Card>

                  <Card className="bg-gradient-to-br from-accent-sky/5 via-transparent to-transparent border-accent-sky/15 place-content-center shadow-lg" accent="sky">
                    <div className="space-y-5">
                      <div className="flex items-center gap-3">
                        <div className="p-2 border border-accent-sky/20 rounded-xl bg-accent-sky/5">
                          <Zap className="w-5 h-5 text-accent-sky fill-accent-sky/10" />
                        </div>
                        <span className="text-[10px] font-mono font-bold text-accent-sky uppercase tracking-widest">
                          {data.wow_insight?.title || 'Signal Detected'}
                        </span>
                      </div>
                      <p className="text-base sm:text-lg font-medium text-white leading-relaxed">
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
                        <div className="p-2 border border-accent-amber/20 rounded-xl bg-accent-amber/5">
                          <Zap className="w-5 h-5 text-accent-amber" />
                        </div>
                        <h3 className="text-white font-mono font-bold uppercase tracking-widest text-xs">Hiring Priority Items</h3>
                      </div>
                      <span className="font-mono text-[10px] text-zinc-500">SYSTEM.LOG_PRIORITIES</span>
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
                        <div className="p-2 border border-accent-sky/20 rounded-xl bg-accent-sky/5">
                          <FileText className="w-5 h-5 text-accent-sky" />
                        </div>
                        <h3 className="text-white font-mono font-bold uppercase tracking-widest text-xs">Documentation Health</h3>
                      </div>
                      <span className="font-mono text-[10px] text-zinc-500">SYSTEM.LOG_DOCS</span>
                    </div>

                    <div className="space-y-3">
                      {data.readme_audits && data.readme_audits.map((audit, id) => (
                         <motion.div 
                          key={id} 
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.5 + (id * 0.05) }}
                          className="group flex items-center justify-between p-4 bg-black border border-white/5 rounded-xl hover:border-white/10 transition-colors"
                         >
                            <div className="flex items-center gap-3">
                              {audit.passed ? (
                                  <div className="w-6 h-6 rounded-lg bg-accent-emerald/10 flex items-center justify-center border border-accent-emerald/20">
                                    <CheckCircle2 className="w-4 h-4 text-accent-emerald" />
                                  </div>
                              ) : (
                                  <div className="w-6 h-6 rounded-lg bg-rose-500/10 flex items-center justify-center border border-rose-500/20">
                                    <AlertCircle className="w-4 h-4 text-rose-500" />
                                  </div>
                              )}
                              <span className={cn(
                                "text-sm font-sans font-medium transition-all",
                                audit.passed ? "text-zinc-200" : "text-zinc-500 line-through decoration-zinc-700/50"
                              )}>{audit.label}</span>
                            </div>
                            <span className="font-mono text-[9px] text-zinc-500">
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
        <div className="border-t border-white/5 pt-8 mt-12 flex flex-col md:flex-row justify-between items-center gap-6 z-10 relative">
          <div className="text-zinc-600 font-mono text-[10px] uppercase tracking-widest text-center md:text-left">
            DEV_LENS // AUDIT REPORT SYSTEM V2.6
          </div>
          
          {/* Live UTC Clock */}
          <UTCClock />

          <div className="font-mono text-[10px] text-zinc-600 uppercase tracking-widest text-center md:text-right">
            continuously_in_motion
          </div>
        </div>
      </div>
    </div>
  );
}

const ChecklistItem = ({ item, id }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.div 
      layout
      className="group bg-[#0A0A0A] border border-white/5 rounded-xl overflow-hidden cursor-pointer hover:border-white/10 transition-all border-l-2 border-l-accent-amber"
      onClick={() => setIsOpen(!isOpen)}
    >
      <div className="flex items-center justify-between p-5 select-none font-mono text-xs">
        <div className="flex items-center gap-3">
          {item.impact === 'High' ? (
            <div className="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.5)]" />
          ) : (
            <div className="w-2 h-2 rounded-full bg-accent-amber" />
          )}
          <span className="font-bold text-zinc-200">
            {item.title}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className={cn(
            "text-[9px] font-bold uppercase px-2 py-0.5 rounded-full border",
            item.impact === 'High' ? 'text-rose-400 border-rose-500/20 bg-rose-500/5' : 'text-zinc-500 border-white/5 bg-white/5'
          )}>
            {item.impact}
          </span>
          <motion.div animate={{ rotate: isOpen ? 180 : 0 }}>
            <ArrowRight className="w-4 h-4 rotate-90 text-zinc-500" />
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
            <div className="border-t border-white/5 pt-4">
              {/* Retro simulated file terminal view */}
              <div className="bg-black border border-white/5 rounded-lg p-4 font-mono text-xs text-left scanlines text-zinc-400">
                <div className="text-zinc-500 mb-2 pb-2 border-b border-white/5">
                  $ cat /audit/priority_{String(id + 1).padStart(2, '0')}.md
                </div>
                <div className="flex gap-2">
                  <span className="text-accent-emerald select-none">[+]</span>
                  <p className="text-zinc-300 leading-relaxed font-sans">{item.hiring_impact || item.reasoning}</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
