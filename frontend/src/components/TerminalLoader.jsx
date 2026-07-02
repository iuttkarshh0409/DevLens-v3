import React, { useState, useEffect, useMemo } from 'react';

export const TerminalLoader = () => {
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
    <div className="w-full max-w-2xl mx-auto bg-black border border-brand-borderDefault rounded-xl p-6 font-mono text-xs text-left scanlines text-brand-purple min-h-[250px] shadow-2xl relative">
      <div className="flex items-center justify-between pb-3 border-b border-brand-borderDefault mb-4 text-brand-textSecondary">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
          <span className="w-2.5 h-2.5 rounded-full bg-zinc-600/80" />
          <span className="w-2.5 h-2.5 rounded-full bg-brand-purple/80" />
        </span>
        <span>bash — 80x24</span>
      </div>
      <div className="space-y-2.5">
        {logs.map((log, i) => (
          <div key={i} className={i === 0 ? "text-brand-textPrimary font-bold" : ""}>
            {log}
          </div>
        ))}
        <div className="inline-block w-1.5 h-4 bg-brand-purple animate-caret ml-1" />
      </div>
    </div>
  );
};

export default TerminalLoader;
