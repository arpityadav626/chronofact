import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  FileText,
  Binary,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Info,
  Copy,
  Check,
  Download,
  X,
  Sparkles,
  RefreshCw
} from 'lucide-react';

export const SAMPLE_TAMPERED_CONTENT =
  "timestamp,user,ip_address,action,status\n" +
  "2025-09-12T15:24:10Z,vikram.malhotra,192.168.1.105,LOGIN,OK\n" +
  "2025-09-12T15:28:45Z,vikram.malhotra\u200B,192.168.1.105,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX\n" +
  "2025-09-12T15:31:00Z,vikram.malhotra,192.168.1.105,EXPORT_PATENT_DRAFT,OK\r\n" +
  "2025-09-12T15:34:12Z,vikram.malhotra,192.168.1.105,LOGOUT,OK\n";

export const SAMPLE_PRISTINE_CONTENT =
  "timestamp,user,ip_address,action,status\n" +
  "2025-09-12T15:24:10Z,vikram.malhotra,192.168.1.105,LOGIN,OK\n" +
  "2025-09-12T15:28:45Z,vikram.malhotra,192.168.1.105,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX\n" +
  "2025-09-12T15:31:00Z,vikram.malhotra,192.168.1.105,EXPORT_PATENT_DRAFT,OK\n" +
  "2025-09-12T15:34:12Z,vikram.malhotra,192.168.1.105,LOGOUT,OK\n";

export function analyzeExhibitBytes(
  filename,
  rawContent,
  exhibitId = "EV-TAMPER-01",
  sha256Digest = "c67d5b83921074a38217bb41a0b36e8492048591823700147981249bcf122618",
  fileType = "SERVER_LOG"
) {
  const encoder = new TextEncoder();
  const bytes = encoder.encode(rawContent || "");
  const sizeBytes = bytes.length;

  const magicSlice = bytes.slice(0, Math.min(8, bytes.length));
  const magicHex = Array.from(magicSlice)
    .map((b) => b.toString(16).padStart(2, "0").toUpperCase())
    .join(" ");

  const anomalies = [];
  const ext = (filename || "").split(".").pop()?.toLowerCase() || "";
  let magicStatus = 'MATCH';
  let magicDescription = 'Valid ASCII/UTF-8 Plain Text Structure';

  if (["csv", "txt", "log", "json"].includes(ext)) {
    if (bytes.length >= 4 && bytes[0] === 0x50 && bytes[1] === 0x4b && bytes[2] === 0x03 && bytes[3] === 0x04) {
      magicStatus = 'MISMATCH';
      magicDescription = 'Header is PK ZIP / Office XML container (50 4B 03 04)';
      anomalies.push({
        id: 'ANOM-MAGIC-01',
        ruleId: 'TAMPER-MAGIC-03',
        title: 'Magic Byte Spoofing (ZIP Container)',
        severity: 'CRITICAL',
        startByte: 0,
        endByte: 3,
        byteLength: 4,
        hexPreview: '50 4B 03 04',
        explanation: `Exhibit has extension '.${ext}' but initial magic bytes match a PK ZIP container (50 4B 03 04). Potential camouflage to evade plain text parsers.`,
        recommendation: 'Quarantine file and run deep uncompressed archive inspection.'
      });
    } else if (bytes.length >= 2 && bytes[0] === 0x4d && bytes[1] === 0x5a) {
      magicStatus = 'MISMATCH';
      magicDescription = 'Header is Windows PE Executable (4D 5A)';
      anomalies.push({
        id: 'ANOM-MAGIC-02',
        ruleId: 'TAMPER-MAGIC-03',
        title: 'Executable Masquerading (PE Header)',
        severity: 'CRITICAL',
        startByte: 0,
        endByte: 1,
        byteLength: 2,
        hexPreview: '4D 5A',
        explanation: `Exhibit header matches Windows Portable Executable (MZ).`,
        recommendation: 'Immediate malware sandbox detonation recommended.'
      });
    }
  }

  // Scan newlines (\r\n CRLF vs \n LF vs \r CR)
  const newlineOccurrences = [];
  let lfCount = 0;
  let crlfCount = 0;
  let crCount = 0;
  let currentLine = 1;

  for (let i = 0; i < bytes.length; i++) {
    if (bytes[i] === 0x0d) {
      if (i + 1 < bytes.length && bytes[i + 1] === 0x0a) {
        crlfCount++;
        newlineOccurrences.push({ offset: i, type: 'CRLF', lineNum: currentLine });
        currentLine++;
        i++;
      } else {
        crCount++;
        newlineOccurrences.push({ offset: i, type: 'CR', lineNum: currentLine });
        currentLine++;
      }
    } else if (bytes[i] === 0x0a) {
      lfCount++;
      newlineOccurrences.push({ offset: i, type: 'LF', lineNum: currentLine });
      currentLine++;
    }
  }

  let dominantNewline = 'NONE';
  if (lfCount >= crlfCount && lfCount >= crCount) {
    dominantNewline = 'LF';
  } else if (crlfCount >= lfCount && crlfCount >= crCount) {
    dominantNewline = 'CRLF';
  } else if (crCount > 0) {
    dominantNewline = 'CR';
  }

  if ((lfCount > 0 && crlfCount > 0) || (crCount > 0 && (lfCount > 0 || crlfCount > 0))) {
    newlineOccurrences.forEach((occ, idx) => {
      if (occ.type !== dominantNewline) {
        const hex = occ.type === 'CRLF' ? '0D 0A' : occ.type === 'LF' ? '0A' : '0D';
        const byteLen = occ.type === 'CRLF' ? 2 : 1;
        anomalies.push({
          id: `ANOM-NL-${idx}`,
          ruleId: 'TAMPER-NEWLINE-01',
          title: `Mixed Line Ending Sequence (${occ.type} vs Dominant ${dominantNewline})`,
          severity: 'MEDIUM',
          startByte: occ.offset,
          endByte: occ.offset + byteLen - 1,
          byteLength: byteLen,
          hexPreview: hex,
          lineNumber: occ.lineNum,
          explanation: `Non-standard newline sequence detected at Byte 0x${occ.offset.toString(16).toUpperCase().padStart(4, '0')} (Line ${occ.lineNum}). File dominantly uses ${dominantNewline} but switched to ${occ.type} (0x${hex}).`,
          recommendation: 'Consistent with manual text editing in an uncalibrated editor (e.g. Windows Notepad editing a Unix server log).'
        });
      }
    });
  }

  // Scan hidden unicode characters & zero-width spaces
  let unicodeArtifactCount = 0;
  for (let i = 0; i < bytes.length - 2; i++) {
    if (bytes[i] === 0xe2 && bytes[i + 1] === 0x80 && bytes[i + 2] === 0x8b) {
      unicodeArtifactCount++;
      anomalies.push({
        id: `ANOM-ZWSP-${i}`,
        ruleId: 'TAMPER-UNICODE-02',
        title: 'Hidden Zero-Width Space (U+200B)',
        severity: 'HIGH',
        startByte: i,
        endByte: i + 2,
        byteLength: 3,
        hexPreview: 'E2 80 8B',
        explanation: `Invisible Unicode Zero-Width Space (U+200B, bytes E2 80 8B) detected at Byte 0x${i.toString(16).toUpperCase().padStart(4, '0')}. Zero-width spaces are invisible to humans in standard text viewers and are typically introduced during manual tampering or copy-pasting.`,
        recommendation: 'Inspect surrounding fields for deliberate identifier obfuscation.'
      });
    } else if (bytes[i] === 0xe2 && bytes[i + 1] === 0x80 && bytes[i + 2] === 0x8c) {
      unicodeArtifactCount++;
      anomalies.push({
        id: `ANOM-ZWNJ-${i}`,
        ruleId: 'TAMPER-UNICODE-02',
        title: 'Zero-Width Non-Joiner (U+200C)',
        severity: 'HIGH',
        startByte: i,
        endByte: i + 2,
        byteLength: 3,
        hexPreview: 'E2 80 8C',
        explanation: `Hidden Unicode Zero-Width Non-Joiner (U+200C) detected at Byte 0x${i.toString(16).toUpperCase().padStart(4, '0')}.`,
        recommendation: 'Verify provenance of raw transmission stream.'
      });
    } else if (bytes[i] === 0xef && bytes[i + 1] === 0xbb && bytes[i + 2] === 0xbf && i > 0) {
      unicodeArtifactCount++;
      anomalies.push({
        id: `ANOM-BOM-${i}`,
        ruleId: 'TAMPER-UNICODE-02',
        title: 'Mid-Stream Byte Order Mark (BOM)',
        severity: 'MEDIUM',
        startByte: i,
        endByte: i + 2,
        byteLength: 3,
        hexPreview: 'EF BB BF',
        explanation: `UTF-8 Byte Order Mark (U+FEFF) found mid-stream at Byte 0x${i.toString(16).toUpperCase().padStart(4, '0')}. Mid-stream occurrences indicate document concatenation or text splicing.`,
        recommendation: 'Check for document concatenation or log file splicing.'
      });
    }
  }

  let scoreDeduction = 0;
  anomalies.forEach((a) => {
    if (a.severity === 'CRITICAL') scoreDeduction += 35;
    else if (a.severity === 'HIGH') scoreDeduction += 25;
    else if (a.severity === 'MEDIUM') scoreDeduction += 15;
    else scoreDeduction += 5;
  });

  const integrityScore = Math.max(0, 100 - scoreDeduction);

  return {
    id: exhibitId,
    filename,
    sha256: sha256Digest,
    sizeBytes,
    fileType,
    rawContent,
    magicBytesHex: magicHex,
    magicStatus,
    magicDescription,
    anomalies,
    dominantNewline,
    newlineBreakdown: { lfCount, crlfCount, crCount },
    unicodeArtifactCount,
    integrityScore
  };
}

export const HexIntegrityInspector = ({
  isOpen,
  onClose,
  exhibitId = "EV-BB0B03",
  filename = "server_access.csv",
  rawText = SAMPLE_TAMPERED_CONTENT,
  sha256Digest = "c67d5b83921074a38217bb41a0b36e8492048591823700147981249bcf122618",
  fileType = "SERVER_LOG",
  onSelectAnomaly
}) => {
  const [activeView, setActiveView] = useState('hex');
  const [currentText, setCurrentText] = useState(rawText);
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);
  const [hoveredByte, setHoveredByte] = useState(null);
  const [isCopied, setIsCopied] = useState(false);
  const [isSimulatedTampered, setIsSimulatedTampered] = useState(true);

  useEffect(() => {
    setCurrentText(rawText);
  }, [rawText]);

  const inspection = useMemo(() => {
    return analyzeExhibitBytes(filename, currentText, exhibitId, sha256Digest, fileType);
  }, [filename, currentText, exhibitId, sha256Digest, fileType]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const rawBytes = useMemo(() => {
    return new TextEncoder().encode(currentText || '');
  }, [currentText]);

  const byteAnomalyMap = useMemo(() => {
    const map = new Map();
    inspection.anomalies.forEach((anom) => {
      for (let b = anom.startByte; b <= anom.endByte; b++) {
        map.set(b, anom);
      }
    });
    return map;
  }, [inspection.anomalies]);

  const handleJumpToAnomaly = (anom) => {
    setSelectedAnomaly(anom);
    if (onSelectAnomaly) onSelectAnomaly(anom);

    if (activeView === 'hex') {
      const rowIndex = Math.floor(anom.startByte / 16);
      const rowElem = document.getElementById(`hex-row-${rowIndex}`);
      if (rowElem) {
        rowElem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        rowElem.classList.add('bg-amber-500/20');
        setTimeout(() => rowElem.classList.remove('bg-amber-500/20'), 1500);
      }
    } else {
      if (anom.lineNumber) {
        const lineElem = document.getElementById(`text-line-${anom.lineNumber}`);
        if (lineElem) {
          lineElem.scrollIntoView({ behavior: 'smooth', block: 'center' });
          lineElem.classList.add('bg-amber-500/20');
          setTimeout(() => lineElem.classList.remove('bg-amber-500/20'), 1500);
        }
      }
    }
  };

  const toggleSimulatedTamper = () => {
    if (isSimulatedTampered) {
      setCurrentText(SAMPLE_PRISTINE_CONTENT);
      setIsSimulatedTampered(false);
      setSelectedAnomaly(null);
    } else {
      setCurrentText(SAMPLE_TAMPERED_CONTENT);
      setIsSimulatedTampered(true);
      setSelectedAnomaly(null);
    }
  };

  const handleCopyTamperReport = () => {
    const report = {
      exhibitId: inspection.id,
      filename: inspection.filename,
      sha256: inspection.sha256,
      sizeBytes: inspection.sizeBytes,
      integrityScore: inspection.integrityScore,
      dominantNewline: inspection.dominantNewline,
      newlineBreakdown: inspection.newlineBreakdown,
      magicBytesHex: inspection.magicBytesHex,
      magicStatus: inspection.magicStatus,
      totalAnomalies: inspection.anomalies.length,
      anomalies: inspection.anomalies
    };
    navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/85 backdrop-blur-md animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl max-h-[94vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/90 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl border ${inspection.anomalies.length > 0 ? 'bg-amber-950/80 text-amber-400 border-amber-800/80' : 'bg-emerald-950/80 text-emerald-400 border-emerald-800/80'}`}>
              <Binary className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-white text-base">
                  Exhibit Integrity & File Structure Audit - [{inspection.id}]
                </h3>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold border ${inspection.integrityScore < 80 ? 'bg-rose-950 text-rose-300 border-rose-800' : 'bg-emerald-950 text-emerald-300 border-emerald-800'}`}>
                  Integrity: {inspection.integrityScore}/100
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5 flex flex-wrap items-center gap-2 font-mono">
                <span className="text-slate-200">{inspection.filename}</span>
                <span className="text-slate-600">&bull;</span>
                <span>{inspection.sizeBytes} Bytes</span>
                <span className="text-slate-600">&bull;</span>
                <span className="text-cyan-400">SHA-256: {inspection.sha256.substring(0, 12)}...</span>
                <span className="text-slate-600">&bull;</span>
                <span className="text-slate-300">Magic: [{inspection.magicBytesHex}]</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="inline-flex rounded-lg bg-slate-950 p-1 border border-slate-800">
              <button
                onClick={() => setActiveView('text')}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition ${activeView === 'text' ? 'bg-cyan-900 text-cyan-200 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Parsed Text View</span>
              </button>
              <button
                onClick={() => setActiveView('hex')}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium transition ${activeView === 'hex' ? 'bg-cyan-900 text-cyan-200 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
              >
                <Binary className="w-3.5 h-3.5" />
                <span>Raw Hex / Offset View</span>
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Anomaly Banner */}
        <div className={`px-6 py-3.5 border-b flex flex-col md:flex-row md:items-center justify-between gap-3 ${inspection.anomalies.length > 0 ? 'bg-gradient-to-r from-amber-950/40 via-rose-950/20 to-slate-950 border-amber-900/60' : 'bg-emerald-950/30 border-emerald-900/50'}`}>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              {inspection.anomalies.length > 0 ? (
                <>
                  <ShieldAlert className="w-4 h-4 text-rose-400" />
                  <span className="text-xs font-bold font-mono text-rose-300 uppercase tracking-wider">
                    Tamper Warning: {inspection.anomalies.length} Structural Anomalies Detected
                  </span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold font-mono text-emerald-300 uppercase tracking-wider">
                    File Structure Verified: 0 Structural Anomalies Detected
                  </span>
                </>
              )}
            </div>

            <p className="text-[11px] text-slate-400 font-sans">
              Dominant Newline: <strong className="text-slate-200 font-mono">{inspection.dominantNewline}</strong> (LF: {inspection.newlineBreakdown.lfCount}, CRLF: {inspection.newlineBreakdown.crlfCount}) &bull; Hidden Unicode Artifacts: <strong className="text-slate-200 font-mono">{inspection.unicodeArtifactCount}</strong> &bull; Magic: <strong className="text-slate-200">{inspection.magicDescription}</strong>
            </p>
          </div>

          {inspection.anomalies.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              {inspection.anomalies.map((anom) => (
                <button
                  key={anom.id}
                  onClick={() => handleJumpToAnomaly(anom)}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-mono font-medium transition border ${selectedAnomaly?.id === anom.id ? 'bg-amber-500 text-slate-950 border-amber-400 font-bold' : anom.severity === 'CRITICAL' ? 'bg-rose-950/80 text-rose-300 border-rose-800' : 'bg-amber-950/80 text-amber-300 border-amber-800'}`}
                >
                  <AlertTriangle className="w-3 h-3" />
                  <span>Byte 0x{anom.startByte.toString(16).toUpperCase()}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Main Body */}
        <div className="flex-1 overflow-y-auto bg-slate-950/60 p-4 font-mono text-xs select-text">
          {activeView === 'text' ? (
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 space-y-1">
              <div className="text-[10px] font-mono uppercase text-slate-500 pb-2 border-b border-slate-850 flex items-center justify-between">
                <span>Line-Numbered Parsed Stream</span>
                <span>Highlights: Amber = Mixed Newline, Red = Hidden Unicode</span>
              </div>

              {currentText.split('\n').map((line, idx) => {
                const lineNum = idx + 1;
                const hasCrlf = line.endsWith('\r');
                const cleanLine = hasCrlf ? line.slice(0, -1) : line;
                const isLineFlagged = inspection.anomalies.some((a) => a.lineNumber === lineNum || (a.ruleId === 'TAMPER-UNICODE-02' && cleanLine.includes('\u200B')));

                return (
                  <div
                    key={`line-${lineNum}`}
                    id={`text-line-${lineNum}`}
                    className={`flex items-start gap-3 py-1 px-2 rounded font-mono text-xs transition ${isLineFlagged ? 'bg-amber-950/20 border-l-2 border-amber-500' : 'hover:bg-slate-900/60'}`}
                  >
                    <span className="w-8 text-right text-slate-600 select-none text-[11px] font-mono shrink-0">
                      {lineNum}
                    </span>

                    <div className="flex-1 text-slate-200 break-all">
                      {cleanLine.includes('\u200B') ? (
                        cleanLine.split('\u200B').map((seg, sIdx, arr) => (
                          <React.Fragment key={`seg-${sIdx}`}>
                            <span>{seg}</span>
                            {sIdx < arr.length - 1 && (
                              <span
                                className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-950 text-rose-300 border border-rose-700 mx-1 align-middle animate-pulse"
                                title="Tampering Artefact: Zero-Width Space (U+200B)"
                              >
                                [ZWSP U+200B]
                              </span>
                            )}
                          </React.Fragment>
                        ))
                      ) : (
                        <span>{cleanLine}</span>
                      )}

                      {hasCrlf ? (
                        <span className="inline-flex items-center ml-2 px-1 py-0.2 rounded text-[9px] font-bold bg-amber-950 text-amber-300 border border-amber-800">
                          [CRLF]
                        </span>
                      ) : (
                        <span className="text-slate-700 text-[10px] ml-1 select-none">[LF]</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs overflow-x-auto">
              <div className="grid grid-cols-[80px_1fr_180px] gap-4 pb-2 mb-2 border-b border-slate-850 text-slate-500 uppercase text-[10px] tracking-wider select-none font-semibold">
                <div>OFFSET</div>
                <div className="grid grid-cols-16 gap-1 text-center">
                  <span>00</span><span>01</span><span>02</span><span>03</span><span>04</span><span>05</span><span>06</span><span>07</span>
                  <span className="border-l border-slate-800 pl-1">08</span><span>09</span><span>0A</span><span>0B</span><span>0C</span><span>0D</span><span>0E</span><span>0F</span>
                </div>
                <div>DECODED ASCII</div>
              </div>

              <div className="space-y-1">
                {Array.from({ length: Math.ceil(rawBytes.length / 16) }).map((_, rIdx) => {
                  const rowOffset = rIdx * 16;
                  const rowOffsetHex = rowOffset.toString(16).padStart(8, '0').toUpperCase();
                  const rowBytesSlice = Array.from(rawBytes.slice(rowOffset, rowOffset + 16));
                  const hasAnomalyInRow = rowBytesSlice.some((_, cIdx) => byteAnomalyMap.has(rowOffset + cIdx));

                  return (
                    <div
                      key={`row-${rIdx}`}
                      id={`hex-row-${rIdx}`}
                      className={`grid grid-cols-[80px_1fr_180px] gap-4 py-0.5 px-1 rounded transition items-center ${hasAnomalyInRow ? 'bg-amber-950/15' : 'hover:bg-slate-900/50'}`}
                    >
                      <span className="text-slate-500 font-mono select-none text-[11px]">
                        {rowOffsetHex}
                      </span>

                      <div className="grid grid-cols-16 gap-1 text-center">
                        {Array.from({ length: 16 }).map((__, cIdx) => {
                          const byteIndex = rowOffset + cIdx;
                          if (byteIndex >= rawBytes.length) {
                            return <span key={`empty-${cIdx}`} className="text-slate-800 select-none">..</span>;
                          }

                          const byteVal = rawBytes[byteIndex];
                          const hexStr = byteVal.toString(16).padStart(2, '0').toUpperCase();
                          const anomaly = byteAnomalyMap.get(byteIndex);
                          const isSelected = selectedAnomaly && byteIndex >= selectedAnomaly.startByte && byteIndex <= selectedAnomaly.endByte;

                          let byteStyle = 'text-slate-300 hover:bg-slate-800 rounded cursor-pointer';
                          if (anomaly) {
                            byteStyle = anomaly.severity === 'CRITICAL' || anomaly.severity === 'HIGH'
                              ? 'bg-rose-950 text-rose-200 border border-rose-700 font-bold rounded'
                              : 'bg-amber-950 text-amber-200 border border-amber-700 font-bold rounded';
                          }
                          if (isSelected) {
                            byteStyle += ' ring-2 ring-cyan-400';
                          }

                          return (
                            <span
                              key={`hex-${byteIndex}`}
                              onMouseEnter={() => setHoveredByte(byteIndex)}
                              onMouseLeave={() => setHoveredByte(null)}
                              onClick={() => anomaly && setSelectedAnomaly(anomaly)}
                              className={`py-0.5 px-0.5 transition font-mono ${byteStyle} ${cIdx === 7 ? 'mr-1' : ''}`}
                              title={anomaly ? `${anomaly.title} (Byte 0x${byteIndex.toString(16).toUpperCase()})` : `Byte 0x${byteIndex.toString(16).toUpperCase()}: ${hexStr}`}
                            >
                              {hexStr}
                            </span>
                          );
                        })}
                      </div>

                      <div className="font-mono text-slate-400 select-text flex">
                        {Array.from({ length: 16 }).map((__, cIdx) => {
                          const byteIndex = rowOffset + cIdx;
                          if (byteIndex >= rawBytes.length) {
                            return <span key={`a-empty-${cIdx}`}>&nbsp;</span>;
                          }
                          const byteVal = rawBytes[byteIndex];
                          const char = byteVal >= 32 && byteVal <= 126 ? String.fromCharCode(byteVal) : '.';
                          const anomaly = byteAnomalyMap.get(byteIndex);

                          return (
                            <span
                              key={`ascii-${byteIndex}`}
                              className={`inline-block w-[11px] text-center ${anomaly ? 'text-amber-300 font-bold bg-amber-950/60' : 'text-slate-300'}`}
                            >
                              {char}
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Selected Anomaly Explanation Drawer */}
        {selectedAnomaly && (
          <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/95 flex items-start justify-between gap-4 animate-in slide-in-from-bottom duration-150">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${selectedAnomaly.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-300 border-rose-800' : 'bg-amber-950 text-amber-300 border-amber-800'}`}>
                  {selectedAnomaly.ruleId} &bull; {selectedAnomaly.severity}
                </span>
                <span className="font-semibold text-white text-xs">
                  {selectedAnomaly.title}
                </span>
                <span className="text-slate-500 font-mono text-[11px]">
                  Byte Range: 0x{selectedAnomaly.startByte.toString(16).toUpperCase()} - 0x{selectedAnomaly.endByte.toString(16).toUpperCase()}
                </span>
                <span className="text-cyan-400 font-mono text-[11px] bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-800/80">
                  Hex: [{selectedAnomaly.hexPreview}]
                </span>
              </div>
              <p className="text-xs text-slate-300 font-sans">
                {selectedAnomaly.explanation}
              </p>
              <p className="text-[11px] text-slate-400 font-sans">
                <strong className="text-slate-200">Judicial Recommendation:</strong> {selectedAnomaly.recommendation}
              </p>
            </div>

            <button
              onClick={() => setSelectedAnomaly(null)}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-800 bg-slate-950 flex flex-wrap items-center justify-between gap-3">
          <button
            onClick={toggleSimulatedTamper}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition border ${isSimulatedTampered ? 'bg-amber-950/60 text-amber-300 border-amber-800/80' : 'bg-slate-900 text-slate-300 border-slate-700'}`}
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>{isSimulatedTampered ? 'Exhibit: Tampered Sample' : 'Exhibit: Pristine Sample'}</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyTamperReport}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium text-slate-200 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition"
            >
              {isCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-cyan-400" />}
              <span>{isCopied ? 'Report Copied' : 'Copy Tamper Report'}</span>
            </button>

            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition shadow-md shadow-cyan-600/20"
            >
              Done
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default HexIntegrityInspector;
