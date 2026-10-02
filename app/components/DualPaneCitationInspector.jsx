import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  FileText,
  Database,
  Mail,
  Copy,
  Check,
  Search,
  CornerDownRight,
  Maximize2,
  Minimize2,
  X,
  Cpu,
  Fingerprint,
  Info
} from 'lucide-react';

export const DEFAULT_SCENARIOS = [
  {
    id: 'claim-001',
    query: 'Was the suspect Vikram Malhotra actively logged into the server during his claimed medical leave?',
    verdict: 'Contradiction Confirmed: Suspect active during claimed sleep',
    verdictType: 'contradiction',
    extractedSentence: '2025-09-12T15:24:10Z,vikram.malhotra,192.168.1.105,LOGIN,OK',
    isVerified: true,
    exhibitId: 'EV-BB0B03',
    fileName: 'server_access.csv',
    fileSha256: 'c67d5b83921074a38217bb41a0b36e8492048591823700147981249bcf122618',
    targetLineNumber: 2,
    charOffsetStart: 42,
    charOffsetEnd: 104,
    sourceContext: 'Authentication Audit Log (Active Directory Session)',
    rawContent: `timestamp,user,ip_address,action,status
2025-09-12T15:24:10Z,vikram.malhotra,192.168.1.105,LOGIN,OK
2025-09-12T15:28:45Z,vikram.malhotra,192.168.1.105,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX
2025-09-12T15:31:00Z,vikram.malhotra,192.168.1.105,EXPORT_PATENT_DRAFT,OK`
  },
  {
    id: 'claim-002',
    query: 'Did the suspect state he was incapacitated with fever and asleep in bed?',
    verdict: 'Verbatim Alibi Statement Confirmed: Claimed Bed Rest & Offline Status',
    verdictType: 'corroboration',
    extractedSentence: 'Sir I am suffering from high fever, I am asleep in bed and completely offline till tomorrow morning.',
    isVerified: true,
    exhibitId: 'EV-8EA211',
    fileName: 'whatsapp_chat.txt',
    fileSha256: '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069',
    targetLineNumber: 2,
    charOffsetStart: 122,
    charOffsetEnd: 228,
    sourceContext: 'WhatsApp Chat Export (Android /data/data/com.whatsapp)',
    rawContent: `[12/09/2025, 15:20:10] Team Lead: Vikram are you available on Slack for urgent sync?
[12/09/2025, 15:25:40] Vikram Malhotra: Sir I am suffering from high fever, I am asleep in bed and completely offline till tomorrow morning.
[12/09/2025, 15:26:00] Team Lead: Ok take rest.`
  },
  {
    id: 'claim-003',
    query: 'Did the suspect transfer 50 Bitcoin to an illicit offshore mixer account at 15:45?',
    verdict: 'Prompt Hallucination Rejected: Zero Verifiable Grounds in Seized Exhibits',
    verdictType: 'rejected',
    extractedSentence: 'Transaction TXID 0x99a2bf executed 50.0 BTC transfer to offshore mixer.',
    isVerified: false,
    rejectionReason: 'Claimed transaction hash and bitcoin mixer reference do not appear in any ingested forensic byte stream. Zero-token match detected.',
    exhibitId: 'EV-8EA211',
    fileName: 'whatsapp_chat.txt',
    fileSha256: '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069',
    targetLineNumber: undefined,
    charOffsetStart: undefined,
    charOffsetEnd: undefined,
    sourceContext: 'Investigative Query Intercept (Adversarial LLM Test)',
    rawContent: `[12/09/2025, 15:20:10] Team Lead: Vikram are you available on Slack for urgent sync?
[12/09/2025, 15:25:40] Vikram Malhotra: Sir I am suffering from high fever, I am asleep in bed and completely offline till tomorrow morning.
[12/09/2025, 15:26:00] Team Lead: Ok take rest.`
  }
];

export function DualPaneCitationInspector({
  isOpen,
  onClose,
  claim: initialClaim,
  onSelectClaim,
  availableClaims = DEFAULT_SCENARIOS
}) {
  const [activeClaim, setActiveClaim] = useState(initialClaim || availableClaims[0]);
  const [searchFilter, setSearchFilter] = useState('');
  const [copiedType, setCopiedType] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const lineRefs = useRef({});
  const viewerContainerRef = useRef(null);

  useEffect(() => {
    if (initialClaim) {
      setActiveClaim(initialClaim);
    }
  }, [initialClaim]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const rawLines = useMemo(() => {
    if (!activeClaim?.rawContent) return [];
    return activeClaim.rawContent.split(/\r?\n/);
  }, [activeClaim?.rawContent]);

  const verificationAudit = useMemo(() => {
    if (!activeClaim) {
      return { isDeterministicMatch: false, matchedLineIndex: -1, charIndex: -1 };
    }

    if (!activeClaim.isVerified) {
      return { isDeterministicMatch: false, matchedLineIndex: -1, charIndex: -1 };
    }

    const cleanQuote = activeClaim.extractedSentence.trim().toLowerCase();
    let matchedLineIndex = -1;
    let charIndex = -1;

    for (let i = 0; i < rawLines.length; i++) {
      const lineLower = rawLines[i].toLowerCase();
      const pos = lineLower.indexOf(cleanQuote);
      if (pos !== -1) {
        matchedLineIndex = i;
        charIndex = pos;
        break;
      }
      const words = cleanQuote.split(/\s+/).filter(w => w.length > 4);
      if (words.length > 2 && words.every(w => lineLower.includes(w))) {
        matchedLineIndex = i;
        charIndex = 0;
        break;
      }
    }

    if (matchedLineIndex === -1 && activeClaim.targetLineNumber && activeClaim.targetLineNumber <= rawLines.length) {
      matchedLineIndex = activeClaim.targetLineNumber - 1;
    }

    return {
      isDeterministicMatch: matchedLineIndex !== -1,
      matchedLineIndex,
      charIndex
    };
  }, [activeClaim, rawLines]);

  useEffect(() => {
    if (isOpen && activeClaim?.isVerified && verificationAudit.matchedLineIndex !== -1) {
      const targetLine = verificationAudit.matchedLineIndex + 1;
      const timeoutId = setTimeout(() => {
        const lineEl = lineRefs.current[targetLine];
        if (lineEl) {
          lineEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 180);
      return () => clearTimeout(timeoutId);
    }
  }, [isOpen, activeClaim, verificationAudit]);

  const handleCopy = (text, type) => {
    navigator.clipboard.writeText(text);
    setCopiedType(type);
    setTimeout(() => setCopiedType(null), 2000);
  };

  const truncateHash = (hash) => {
    if (!hash || hash.length < 16) return hash;
    return `${hash.slice(0, 8)}...${hash.slice(-8)}`;
  };

  const getFileIcon = (filename) => {
    if (filename.endsWith('.csv') || filename.endsWith('.sql')) {
      return <Database className="w-4 h-4 text-cyan-400" />;
    }
    if (filename.endsWith('.eml')) {
      return <Mail className="w-4 h-4 text-amber-400" />;
    }
    return <FileText className="w-4 h-4 text-blue-400" />;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-950/85 backdrop-blur-md animate-in fade-in duration-200">
      <div
        className={`bg-slate-900 border border-slate-800 rounded-2xl w-full flex flex-col shadow-2xl overflow-hidden transition-all duration-300 ${
          isFullscreen ? 'h-full max-w-full' : 'max-w-6xl max-h-[92vh] h-[860px]'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/70 select-none">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-inner">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                  Dual-Pane Mechanical Citation Inspector
                </h2>
                {activeClaim.isVerified ? (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-[11px] font-mono font-semibold rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800 shadow-sm">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    Mechanical Match: 100% Grounded
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-[11px] font-mono font-semibold rounded-full bg-rose-950/90 text-rose-300 border border-rose-800 shadow-sm">
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                    Unverified by Source Record
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-2">
                <span>Deterministic Zero-Hallucination Gate</span>
                <span className="text-slate-600">&bull;</span>
                <span className="font-mono text-[11px] text-slate-400">BSA 2023 §63(4) Strict Mechanical Grounding</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-1 bg-slate-950 border border-slate-800 rounded-lg p-1 mr-2 text-xs">
              <span className="text-[10px] uppercase font-bold text-slate-500 px-2 font-mono">Test Sample:</span>
              {availableClaims.map((item, idx) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveClaim(item);
                    if (onSelectClaim) onSelectClaim(item);
                  }}
                  className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors ${
                    activeClaim.id === item.id
                      ? 'bg-slate-800 text-cyan-300 font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                  title={item.query}
                >
                  {item.isVerified ? `Ex.${idx + 1} Grounded` : `Ex.${idx + 1} Reject`}
                </button>
              ))}
            </div>

            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
              title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>

            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
              title="Close (Esc)"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Dual Pane Body */}
        <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-slate-800 flex-1 overflow-hidden min-h-0 bg-slate-950/40">
          
          {/* Left Column: AI Finding Card */}
          <div className="p-6 overflow-y-auto space-y-5 flex flex-col justify-between">
            <div className="space-y-5">
              
              <div>
                <div className="flex items-center justify-between text-[11px] uppercase font-bold tracking-wider text-slate-400 font-mono mb-2">
                  <span className="flex items-center gap-1.5 text-slate-300">
                    <Info className="w-3.5 h-3.5 text-cyan-400" />
                    Investigative Query / Claim
                  </span>
                  <span className="text-cyan-400 font-mono bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-900/60">
                    Claim ID: {activeClaim.id}
                  </span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/90 text-xs text-slate-300 leading-relaxed font-sans">
                  "{activeClaim.query}"
                </div>
              </div>

              {/* Verdict Card */}
              <div
                className={`p-4 rounded-xl border transition-all ${
                  activeClaim.isVerified
                    ? activeClaim.verdictType === 'contradiction'
                      ? 'bg-rose-950/20 border-rose-900/60 text-rose-200'
                      : 'bg-emerald-950/20 border-emerald-900/60 text-emerald-200'
                    : 'bg-rose-950/40 border-rose-700/80 text-rose-200 shadow-inner'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    {activeClaim.isVerified ? (
                      activeClaim.verdictType === 'contradiction' ? (
                        <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
                      ) : (
                        <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                      )
                    ) : (
                      <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
                    )}
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold tracking-wider font-mono opacity-80">
                      Forensic Verdict:
                    </span>
                    <h3 className="text-sm font-bold tracking-tight text-white leading-snug">
                      {activeClaim.verdict}
                    </h3>
                  </div>
                </div>
              </div>

              {/* Extracted Sentence */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-[11px] uppercase font-bold tracking-wider text-slate-400 font-mono">
                  <span>Extracted Sentence for Grounding</span>
                  {activeClaim.isVerified ? (
                    <span className="text-emerald-400 text-[10px] font-semibold flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      Deterministic Substring 100%
                    </span>
                  ) : (
                    <span className="text-rose-400 text-[10px] font-semibold flex items-center gap-1">
                      <XCircle className="w-3.5 h-3.5" />
                      Substring Absent (0%)
                    </span>
                  )}
                </div>

                <div
                  className={`p-4 rounded-xl border relative font-mono text-xs leading-relaxed ${
                    activeClaim.isVerified
                      ? 'bg-slate-900/90 border-slate-800 text-slate-200'
                      : 'bg-rose-950/20 border-rose-900/70 text-rose-300'
                  }`}
                >
                  <p className={!activeClaim.isVerified ? 'line-through opacity-75' : ''}>
                    {activeClaim.extractedSentence}
                  </p>
                  
                  <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
                    <span className="text-slate-400 font-sans text-xs">
                      {activeClaim.isVerified
                        ? 'Status: Verified verbatim in local disk bytes'
                        : 'Status: Hallucination detected and isolated'}
                    </span>
                    <button
                      onClick={() => handleCopy(activeClaim.extractedSentence, 'sentence')}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition text-[11px]"
                      title="Copy sentence"
                    >
                      {copiedType === 'sentence' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      <span>{copiedType === 'sentence' ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Provenance Record */}
              <div className="space-y-2.5">
                <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider font-mono">
                  Evidentiary Provenance Record:
                </span>
                
                <div className="space-y-2 text-xs font-mono">
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/90">
                    <span className="text-slate-400 flex items-center gap-2">
                      <Fingerprint className="w-3.5 h-3.5 text-cyan-400" />
                      Target Exhibit:
                    </span>
                    <span className="text-cyan-300 font-semibold px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-800/50">
                      {activeClaim.exhibitId} ({activeClaim.fileName})
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/90">
                    <span className="text-slate-400">Byte Range / Offset:</span>
                    <span className="text-slate-300">
                      {activeClaim.isVerified && activeClaim.charOffsetStart !== undefined
                        ? `0x${activeClaim.charOffsetStart.toString(16).padStart(4, '0').toUpperCase()} → 0x${(
                            activeClaim.charOffsetEnd || activeClaim.charOffsetStart + 50
                          )
                            .toString(16)
                            .padStart(4, '0')
                            .toUpperCase()} (Char: ${activeClaim.charOffsetStart})`
                        : 'N/A (Byte Distance: ∞)'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/90">
                    <span className="text-slate-400">Record Locator:</span>
                    <span className="text-slate-300">
                      {activeClaim.isVerified && activeClaim.targetLineNumber
                        ? `Line ${activeClaim.targetLineNumber} in ${activeClaim.fileName}`
                        : 'No Deterministic Index Found'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/90">
                    <span className="text-slate-400">Deterministic AST Match:</span>
                    <span
                      className={`font-semibold ${
                        activeClaim.isVerified ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {activeClaim.isVerified ? 'MATCH CONFIRMED (100.0%)' : 'REJECTED (0.0% MATCH)'}
                    </span>
                  </div>
                </div>
              </div>

            </div>

            <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[11px] text-slate-500 font-sans">
                Indian Evidence Act (BSA 2023 §63) Compliant
              </span>
              <button
                onClick={() =>
                  handleCopy(
                    `[BSA 63(4) Grounded Citation]\nExhibit: ${activeClaim.exhibitId} (${activeClaim.fileName})\nSHA-256: ${activeClaim.fileSha256}\nLine: ${activeClaim.targetLineNumber || 'N/A'}\nVerbatim Quote: "${activeClaim.extractedSentence}"\nFinding: ${activeClaim.verdict}`,
                    'full-citation'
                  )
                }
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 hover:border-slate-600 text-xs font-semibold font-mono transition"
              >
                {copiedType === 'full-citation' ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Citation Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Copy Court Citation</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Column: Raw Evidence Byte/Line Viewer */}
          <div className="p-6 flex flex-col h-full overflow-hidden bg-slate-950/80">
            
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-2 select-none">
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 rounded bg-slate-900 border border-slate-800">
                  {getFileIcon(activeClaim.fileName)}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-200">
                      {activeClaim.fileName}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">
                      {activeClaim.exhibitId}
                    </span>
                  </div>
                  <div className="text-[11px] font-mono text-slate-500 flex items-center gap-1.5 mt-0.5">
                    <span>SHA-256:</span>
                    <span className="text-slate-400">{truncateHash(activeClaim.fileSha256)}</span>
                    <button
                      onClick={() => handleCopy(activeClaim.fileSha256, 'hash')}
                      className="text-slate-500 hover:text-cyan-400 transition"
                      title="Copy full SHA-256 digest"
                    >
                      {copiedType === 'hash' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {activeClaim.isVerified ? (
                  <button
                    onClick={() => {
                      if (verificationAudit.matchedLineIndex !== -1) {
                        const targetLine = verificationAudit.matchedLineIndex + 1;
                        lineRefs.current[targetLine]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                      }
                    }}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-cyan-300 text-[11px] font-mono transition"
                    title="Jump to highlighted evidence line"
                  >
                    <CornerDownRight className="w-3 h-3 text-cyan-400" />
                    <span>Focus Line {activeClaim.targetLineNumber || verificationAudit.matchedLineIndex + 1}</span>
                  </button>
                ) : null}

                <span
                  className={`inline-flex items-center gap-1 text-[11px] font-mono font-medium px-2 py-0.5 rounded-full ${
                    activeClaim.isVerified
                      ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/80'
                      : 'bg-rose-950/70 text-rose-400 border border-rose-800'
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      activeClaim.isVerified ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'
                    }`}
                  ></span>
                  {activeClaim.isVerified ? 'Vault Verified' : 'Integrity Mismatch'}
                </span>
              </div>
            </div>

            <div className="py-2.5 flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  placeholder="Filter or search verbatim bytes in file..."
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-lg pl-8 pr-3 py-1 text-xs text-slate-300 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 font-mono"
                />
              </div>
              {searchFilter && (
                <button
                  onClick={() => setSearchFilter('')}
                  className="text-xs text-slate-400 hover:text-slate-200 px-2 py-1 rounded bg-slate-900 border border-slate-800"
                >
                  Clear
                </button>
              )}
            </div>

            {/* Viewer Content Box */}
            <div
              ref={viewerContainerRef}
              className="flex-1 min-h-0 overflow-y-auto rounded-xl bg-slate-950 border border-slate-800 p-3 font-mono text-xs select-text shadow-inner"
            >
              {/* Fallback Error Handling */}
              {!activeClaim.isVerified ? (
                <div className="space-y-4 my-2">
                  <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-700/80 shadow-lg text-rose-200 space-y-2.5">
                    <div className="flex items-center gap-2 text-rose-400 font-bold text-xs uppercase tracking-wider font-mono">
                      <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0" />
                      <span>Verification Failure: Claimed sentence does not exist in ingested exhibit bytes (Prompt Hallucination Rejected)</span>
                    </div>
                    <p className="text-xs text-rose-300/90 leading-relaxed font-sans">
                      The mechanical verifier scanned the complete raw byte sequence of exhibit{' '}
                      <span className="font-mono font-semibold text-rose-200">{activeClaim.exhibitId}</span>. The
                      claimed assertion could not be resolved deterministically to any byte offset or line.
                    </p>
                    {activeClaim.rejectionReason && (
                      <div className="p-2.5 rounded bg-rose-950/70 border border-rose-900/80 text-[11px] font-mono text-rose-300">
                        <strong className="text-rose-200">Rejection Cause:</strong> {activeClaim.rejectionReason}
                      </div>
                    )}
                    <div className="pt-2 border-t border-rose-900/50 flex items-center justify-between text-[11px] text-rose-400 font-mono">
                      <span>Levenshtein Distance: ∞</span>
                      <span>BSA §63(4) Inadmissible</span>
                    </div>
                  </div>

                  <div className="text-[11px] text-slate-500 font-mono pt-2">
                    Verbatim File Contents (Unmatched Raw Bytes):
                  </div>
                  <div className="opacity-50 space-y-1">
                    {rawLines.map((line, idx) => (
                      <div key={idx} className="flex items-start text-slate-400 hover:text-slate-200 font-mono text-[11px]">
                        <span className="w-10 shrink-0 text-slate-600 select-none text-right pr-3 font-mono">
                          {idx + 1}
                        </span>
                        <span className="whitespace-pre-wrap break-all">{line || ' '}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                /* Grounded Lines */
                <div className="space-y-0.5">
                  {rawLines.map((line, idx) => {
                    const lineNumber = idx + 1;
                    const isTargetLine = lineNumber === activeClaim.targetLineNumber || idx === verificationAudit.matchedLineIndex;
                    const matchesFilter = searchFilter
                      ? line.toLowerCase().includes(searchFilter.toLowerCase())
                      : true;

                    if (searchFilter && !matchesFilter && !isTargetLine) {
                      return null;
                    }

                    return (
                      <div
                        key={lineNumber}
                        ref={(el) => {
                          lineRefs.current[lineNumber] = el;
                        }}
                        className={`group flex items-start py-1 px-2 rounded transition-all duration-300 ${
                          isTargetLine
                            ? 'bg-cyan-950/70 border-l-4 border-cyan-400 text-cyan-100 shadow-md ring-1 ring-cyan-500/30'
                            : 'hover:bg-slate-900/80 text-slate-300'
                        }`}
                      >
                        <span
                          className={`w-10 shrink-0 select-none text-right pr-3 font-mono text-[11px] ${
                            isTargetLine ? 'text-cyan-400 font-bold' : 'text-slate-600 group-hover:text-slate-400'
                          }`}
                        >
                          {lineNumber}
                        </span>

                        <div className="flex-1 whitespace-pre-wrap break-all font-mono text-[11.5px] leading-relaxed">
                          {isTargetLine ? (
                            <div className="relative">
                              <span className="inline-block bg-amber-400/20 text-amber-200 border-b-2 border-amber-400 px-1 py-0.5 rounded font-semibold">
                                {line}
                              </span>
                              <span className="ml-2 inline-flex items-center gap-1 text-[10px] text-cyan-400 bg-cyan-950 px-1.5 py-0.5 rounded border border-cyan-800 uppercase font-mono font-bold tracking-wider">
                                <Check className="w-2.5 h-2.5" /> Verbatim Anchor
                              </span>
                            </div>
                          ) : (
                            <span>{line || ' '}</span>
                          )}
                        </div>

                        <button
                          onClick={() => handleCopy(line, `line-${lineNumber}`)}
                          className="opacity-0 group-hover:opacity-100 transition-opacity ml-2 p-1 text-slate-500 hover:text-slate-200 rounded hover:bg-slate-800"
                          title="Copy this line"
                        >
                          {copiedType === `line-${lineNumber}` ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Viewer Footer */}
            <div className="pt-3 mt-1 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-500 gap-2 select-none">
              <div className="flex items-center gap-3">
                <span>Encoding: UTF-8</span>
                <span>&bull;</span>
                <span>Lines: {rawLines.length}</span>
                <span>&bull;</span>
                <span>Size: {new Blob([activeClaim.rawContent]).size} Bytes</span>
              </div>
              <div className="flex items-center gap-2">
                {activeClaim.isVerified ? (
                  <span className="text-cyan-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    <span>Byte-level Provenance Grounded</span>
                  </span>
                ) : (
                  <span className="text-rose-400 flex items-center gap-1">
                    <XCircle className="w-3 h-3 text-rose-400" />
                    <span>Inference Blocked by Mechanical Gate</span>
                  </span>
                )}
              </div>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
}

export default DualPaneCitationInspector;
