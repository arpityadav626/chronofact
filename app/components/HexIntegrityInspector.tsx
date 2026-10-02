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
  Search,
  Hash,
  CornerDownLeft,
  Eye,
  Sliders,
  Sparkles,
  RefreshCw,
  ExternalLink
} from 'lucide-react';

export type AnomalySeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export interface TamperAnomaly {
  id: string;
  ruleId: 'TAMPER-NEWLINE-01' | 'TAMPER-UNICODE-02' | 'TAMPER-MAGIC-03' | 'TAMPER-CONTROL-04';
  title: string;
  severity: AnomalySeverity;
  startByte: number; // e.g. 0x014E
  endByte: number;
  byteLength: number;
  hexPreview: string; // e.g. "0D 0A" or "E2 80 8B"
  lineNumber?: number;
  explanation: string;
  recommendation: string;
}

export interface ExhibitInspectionData {
  id: string;
  filename: string;
  sha256: string;
  sizeBytes: number;
  fileType: string;
  rawContent: string;
  magicBytesHex: string;
  magicStatus: 'MATCH' | 'MISMATCH' | 'UNKNOWN';
  magicDescription: string;
  anomalies: TamperAnomaly[];
  dominantNewline: 'LF' | 'CRLF' | 'CR' | 'NONE';
  newlineBreakdown: {
    lfCount: number;
    crlfCount: number;
    crCount: number;
  };
  unicodeArtifactCount: number;
  integrityScore: number; // 0 (compromised) to 100 (clean)
}

export interface HexIntegrityInspectorProps {
  isOpen: boolean;
  onClose: () => void;
  exhibitId?: string;
  filename?: string;
  rawText?: string;
  sha256Digest?: string;
  fileType?: string;
  onSelectAnomaly?: (anomaly: TamperAnomaly) => void;
}

// Built-in Default Exhibit with Simulated Realistic Forensic Tampering:
// A Linux server access CSV that was tampered in Windows Notepad:
// 1. Injected Windows CRLF (0x0D 0x0A) at Byte 0x014E (Line 4) in an otherwise Unix LF file.
// 2. Injected Zero-Width Space (U+200B: E2 80 8B) at Byte 0x00C8 to conceal an IP modification.
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

/**
 * Pure low-level tampering heuristics analyzer
 */
export function analyzeExhibitBytes(
  filename: string,
  rawContent: string,
  exhibitId: string = "EV-TAMPER-01",
  sha256Digest: string = "c67d5b83921074a38217bb41a0b36e8492048591823700147981249bcf122618",
  fileType: string = "SERVER_LOG"
): ExhibitInspectionData {
  const encoder = new TextEncoder();
  const bytes = encoder.encode(rawContent);
  const sizeBytes = bytes.length;

  // 1. Extract Magic Bytes (First 8 bytes)
  const magicSlice = bytes.slice(0, Math.min(8, bytes.length));
  const magicHex = Array.from(magicSlice)
    .map((b) => b.toString(16).padStart(2, "0").toUpperCase())
    .join(" ");

  const anomalies: TamperAnomaly[] = [];

  // Heuristic A: File Header Magic Bytes vs Extension
  const ext = filename.split(".").pop()?.toLowerCase() || "";
  let magicStatus: 'MATCH' | 'MISMATCH' | 'UNKNOWN' = 'MATCH';
  let magicDescription = 'Valid ASCII/UTF-8 Plain Text Structure';

  if (["csv", "txt", "log", "json"].includes(ext)) {
    // Check if starts with PK zip container (50 4B 03 04)
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
        explanation: `Exhibit has extension '.${ext}' but initial magic bytes match a PK ZIP / Office XML container (50 4B 03 04). Potential file extension camouflage to evade plain text forensic parsers.`,
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
        explanation: `Exhibit header matches Windows Portable Executable (MZ). Executable binary file disguised as text document.`,
        recommendation: 'Immediate malware sandbox detonation recommended.'
      });
    } else if (bytes.length >= 5 && bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46 && bytes[4] === 0x2d) {
      magicStatus = 'MISMATCH';
      magicDescription = 'Header is Adobe PDF (%PDF-)';
      anomalies.push({
        id: 'ANOM-MAGIC-03',
        ruleId: 'TAMPER-MAGIC-03',
        title: 'PDF Container Masquerading',
        severity: 'HIGH',
        startByte: 0,
        endByte: 4,
        byteLength: 5,
        hexPreview: '25 50 44 46 2D',
        explanation: `File extension is .${ext} but contains %PDF- magic signature.`,
        recommendation: 'Re-index as PDF evidence artifact.'
      });
    }
  }

  // Heuristic B: Scan Newlines (\r\n CRLF vs \n LF vs \r CR)
  const newlineOccurrences: { offset: number; type: 'CRLF' | 'LF' | 'CR'; lineNum: number }[] = [];
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
        i++; // skip LF
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

  let dominantNewline: 'LF' | 'CRLF' | 'CR' | 'NONE' = 'NONE';
  if (lfCount > 0 || crlfCount > 0 || crCount > 0) {
    if (lfCount >= crlfCount && lfCount >= crCount) {
      dominantNewline = 'LF';
    } else if (crlfCount >= lfCount && crlfCount >= crCount) {
      dominantNewline = 'CRLF';
    } else {
      dominantNewline = 'CR';
    }
  }

  // Detect Mixed Line Ending Anomalies
  if ((lfCount > 0 && crlfCount > 0) || (crCount > 0 && (lfCount > 0 || crlfCount > 0))) {
    // Flag the minority newlines
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
          explanation: `Non-standard newline sequence detected at Byte 0x${occ.offset.toString(16).toUpperCase().padStart(4, '0')} (Line ${occ.lineNum}). File dominantly uses ${dominantNewline} (${dominantNewline === 'LF' ? `${lfCount} instances` : `${crlfCount} instances`}), but switched to ${occ.type} (0x${hex}).`,
          recommendation: 'Consistent with manual text editing in an uncalibrated editor (e.g. Windows Notepad editing a Unix server log).'
        });
      }
    });
  }

  // Heuristic C: Hidden Non-Printable Unicode Characters & Zero-Width Spaces
  // Check UTF-8 byte sequences:
  // E2 80 8B -> U+200B Zero-Width Space
  // E2 80 8C -> U+200C Zero-Width Non-Joiner
  // E2 80 8D -> U+200D Zero-Width Joiner
  // E2 81 A0 -> U+2060 Word Joiner
  // EF BB BF -> U+FEFF Zero-Width No-Break Space (when offset > 0)
  // E2 80 AE -> U+202E Right-to-Left Override
  let unicodeArtifactCount = 0;
  for (let i = 0; i < bytes.length - 2; i++) {
    // Check E2 80 8B (Zero-width space)
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
        explanation: `Invisible Unicode Zero-Width Space (U+200B, bytes E2 80 8B) detected at Byte 0x${i.toString(16).toUpperCase().padStart(4, '0')}. Zero-width spaces are invisible to humans in standard text viewers and are typically introduced during manual tampering, copy-pasting from web portals, or prompt steganography.`,
        recommendation: 'Inspect surrounding username/token fields for deliberate identity obfuscation.'
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
        explanation: `UTF-8 Byte Order Mark (U+FEFF) found mid-stream at Byte 0x${i.toString(16).toUpperCase().padStart(4, '0')}. BOM headers should only appear at offset 0. Mid-stream occurrences indicate concatenation or copy-paste between multiple file fragments.`,
        recommendation: 'Check for document concatenation or log file splicing.'
      });
    }
  }

  // Check NUL bytes in plain text files
  if (["csv", "txt", "log", "eml"].includes(ext)) {
    for (let i = 0; i < bytes.length; i++) {
      if (bytes[i] === 0x00) {
        anomalies.push({
          id: `ANOM-NUL-${i}`,
          ruleId: 'TAMPER-CONTROL-04',
          title: 'NUL Byte Injection in Text Stream',
          severity: 'HIGH',
          startByte: i,
          endByte: i,
          byteLength: 1,
          hexPreview: '00',
          explanation: `Binary NUL byte (0x00) found at Byte 0x${i.toString(16).toUpperCase().padStart(4, '0')}. Plain text logs should not contain NUL bytes.`,
          recommendation: 'Investigate possible binary shellcode injection or corrupt file append.'
        });
      }
    }
  }

  // Calculate forensic integrity score (100 is pristine, 0 is heavily compromised)
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
    newlineBreakdown: {
      lfCount,
      crlfCount,
      crCount
    },
    unicodeArtifactCount,
    integrityScore
  };
}

export const HexIntegrityInspector: React.FC<HexIntegrityInspectorProps> = ({
  isOpen,
  onClose,
  exhibitId = "EV-BB0B03",
  filename = "server_access.csv",
  rawText = SAMPLE_TAMPERED_CONTENT,
  sha256Digest = "c67d5b83921074a38217bb41a0b36e8492048591823700147981249bcf122618",
  fileType = "SERVER_LOG",
  onSelectAnomaly
}) => {
  // State
  const [activeView, setActiveView] = useState<'text' | 'hex'>('hex');
  const [currentText, setCurrentText] = useState<string>(rawText);
  const [selectedAnomaly, setSelectedAnomaly] = useState<TamperAnomaly | null>(null);
  const [hoveredByte, setHoveredByte] = useState<number | null>(null);
  const [isCopied, setIsCopied] = useState(false);
  const [isSimulatedTampered, setIsSimulatedTampered] = useState(true);

  const hexContainerRef = useRef<HTMLDivElement>(null);
  const textContainerRef = useRef<HTMLDivElement>(null);

  // Sync state if rawText prop changes
  useEffect(() => {
    setCurrentText(rawText);
  }, [rawText]);

  // Run heuristics analysis
  const inspection = useMemo(() => {
    return analyzeExhibitBytes(filename, currentText, exhibitId, sha256Digest, fileType);
  }, [filename, currentText, exhibitId, sha256Digest, fileType]);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Precompute byte array for Hex View
  const rawBytes = useMemo(() => {
    return new TextEncoder().encode(currentText);
  }, [currentText]);

  // Map byte index to anomaly lookup
  const byteAnomalyMap = useMemo(() => {
    const map = new Map<number, TamperAnomaly>();
    inspection.anomalies.forEach((anom) => {
      for (let b = anom.startByte; b <= anom.endByte; b++) {
        map.set(b, anom);
      }
    });
    return map;
  }, [inspection.anomalies]);

  // Scroll to anomaly in active view
  const handleJumpToAnomaly = (anom: TamperAnomaly) => {
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
      anomalies: inspection.anomalies.map((a) => ({
        rule: a.ruleId,
        title: a.title,
        severity: a.severity,
        startOffsetHex: `0x${a.startByte.toString(16).toUpperCase()}`,
        byteLength: a.byteLength,
        hexPreview: a.hexPreview,
        lineNumber: a.lineNumber,
        explanation: a.explanation
      }))
    };
    navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleExportHexDump = () => {
    let dump = `CHRONOFACT FORENSIC HEX DUMP\n`;
    dump += `EXHIBIT: ${inspection.filename} (${inspection.id})\n`;
    dump += `SHA-256: ${inspection.sha256}\n`;
    dump += `TIMESTAMP: ${new Date().toISOString()}\n`;
    dump += `--------------------------------------------------------------------------------\n`;
    dump += `OFFSET   00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F  ASCII\n`;
    dump += `--------------------------------------------------------------------------------\n`;

    const totalRows = Math.ceil(rawBytes.length / 16);
    for (let r = 0; r < totalRows; r++) {
      const offset = r * 16;
      const offsetHex = offset.toString(16).padStart(8, '0').toUpperCase();
      let hexPart = '';
      let asciiPart = '';

      for (let c = 0; c < 16; c++) {
        const byteIndex = offset + c;
        if (byteIndex < rawBytes.length) {
          const byteVal = rawBytes[byteIndex];
          hexPart += byteVal.toString(16).padStart(2, '0').toUpperCase() + ' ';
          if (c === 7) hexPart += ' ';
          asciiPart += byteVal >= 32 && byteVal <= 126 ? String.fromCharCode(byteVal) : '.';
        } else {
          hexPart += '   ';
          if (c === 7) hexPart += ' ';
          asciiPart += ' ';
        }
      }
      dump += `${offsetHex}  ${hexPart} |${asciiPart}|\n`;
    }

    const blob = new Blob([dump], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${inspection.id}_${inspection.filename}.hexdump.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/85 backdrop-blur-md animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl max-h-[94vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        
        {/* ========================================================================= */}
        {/* REQUIREMENT 1: MODAL HEADER */}
        {/* ========================================================================= */}
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

          {/* Dual-View Toggle & Close */}
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
              title="Close (Esc)"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* REQUIREMENT 3: ANOMALY BANNER & HEURISTICS STATUS */}
        {/* ========================================================================= */}
        <div className={`px-6 py-3.5 border-b flex flex-col md:flex-row md:items-center justify-between gap-3 ${inspection.anomalies.length > 0 ? 'bg-gradient-to-r from-amber-950/40 via-rose-950/20 to-slate-950 border-amber-900/60' : 'bg-emerald-950/30 border-emerald-900/50'}`}>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              {inspection.anomalies.length > 0 ? (
                <>
                  <ShieldAlert className="w-4 h-4 text-rose-400" />
                  <span className="text-xs font-bold font-mono text-rose-300 uppercase tracking-wider">
                    Tamper Warning: {inspection.anomalies.length} Structural Anomalies Detected
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                    High Evidentiary Scrutiny Required
                  </span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold font-mono text-emerald-300 uppercase tracking-wider">
                    File Structure Verified: 0 Structural Anomalies Detected
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                    Pristine Evidentiary Baseline
                  </span>
                </>
              )}
            </div>

            <p className="text-[11px] text-slate-400 font-sans">
              Dominant Newline: <strong className="text-slate-200 font-mono">{inspection.dominantNewline}</strong> (LF: {inspection.newlineBreakdown.lfCount}, CRLF: {inspection.newlineBreakdown.crlfCount}) &bull; Hidden Unicode Artifacts: <strong className="text-slate-200 font-mono">{inspection.unicodeArtifactCount}</strong> &bull; Magic Signature: <strong className="text-slate-200">{inspection.magicDescription}</strong>
            </p>
          </div>

          {/* Anomaly Quick Selector Chips */}
          {inspection.anomalies.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              {inspection.anomalies.map((anom) => (
                <button
                  key={anom.id}
                  onClick={() => handleJumpToAnomaly(anom)}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-mono font-medium transition border ${selectedAnomaly?.id === anom.id ? 'bg-amber-500 text-slate-950 border-amber-400 font-bold' : anom.severity === 'CRITICAL' ? 'bg-rose-950/80 text-rose-300 border-rose-800 hover:bg-rose-900/80' : 'bg-amber-950/80 text-amber-300 border-amber-800 hover:bg-amber-900/80'}`}
                  title={anom.explanation}
                >
                  <AlertTriangle className="w-3 h-3" />
                  <span>Byte 0x{anom.startByte.toString(16).toUpperCase()}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* MAIN BODY: DUAL VIEW (TEXT VS HEX) */}
        {/* ========================================================================= */}
        <div className="flex-1 overflow-y-auto bg-slate-950/60 p-4 font-mono text-xs select-text">
          
          {/* VIEW A: PARSED TEXT VIEW */}
          {activeView === 'text' && (
            <div ref={textContainerRef} className="rounded-xl border border-slate-800 bg-slate-950 p-4 space-y-1">
              <div className="text-[10px] font-mono uppercase text-slate-500 pb-2 border-b border-slate-850 flex items-center justify-between">
                <span>Line-Numbered Parsed Stream</span>
                <span>Highlights: Amber = Mixed Newline, Red = Hidden Unicode</span>
              </div>

              {currentText.split('\n').map((line, idx) => {
                const lineNum = idx + 1;
                const hasCrlf = line.endsWith('\r');
                const cleanLine = hasCrlf ? line.slice(0, -1) : line;
                const lineAnomalies = inspection.anomalies.filter((a) => a.lineNumber === lineNum || (a.ruleId === 'TAMPER-UNICODE-02' && cleanLine.includes('\u200B')));
                const isLineFlagged = lineAnomalies.length > 0;

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
                      {/* Render text with special chips for hidden characters */}
                      {cleanLine.includes('\u200B') ? (
                        cleanLine.split('\u200B').map((seg, sIdx, arr) => (
                          <React.Fragment key={`seg-${sIdx}`}>
                            <span>{seg}</span>
                            {sIdx < arr.length - 1 && (
                              <span
                                className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-950 text-rose-300 border border-rose-700 mx-1 align-middle animate-pulse cursor-help"
                                title="Tampering Artefact: Zero-Width Space (U+200B) detected here"
                              >
                                [ZWSP U+200B]
                              </span>
                            )}
                          </React.Fragment>
                        ))
                      ) : (
                        <span>{cleanLine}</span>
                      )}

                      {/* Display explicit line ending badge */}
                      {hasCrlf ? (
                        <span
                          className="inline-flex items-center ml-2 px-1 py-0.2 rounded text-[9px] font-bold bg-amber-950 text-amber-300 border border-amber-800 cursor-help"
                          title="Non-standard newline sequence: Windows CRLF (0x0D 0x0A)"
                        >
                          [CRLF]
                        </span>
                      ) : (
                        <span className="text-slate-700 text-[10px] ml-1 select-none">[LF]</span>
                      )}
                    </div>

                    {isLineFlagged && (
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-900/40 text-amber-300 border border-amber-800 shrink-0">
                        {lineAnomalies[0].ruleId}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* VIEW B: RAW HEX / OFFSET VIEW */}
          {activeView === 'hex' && (
            <div ref={hexContainerRef} className="rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs overflow-x-auto">
              
              {/* Hex View Column Header */}
              <div className="grid grid-cols-[80px_1fr_180px] gap-4 pb-2 mb-2 border-b border-slate-850 text-slate-500 uppercase text-[10px] tracking-wider select-none font-semibold">
                <div>OFFSET</div>
                <div className="grid grid-cols-16 gap-1 text-center">
                  <span>00</span><span>01</span><span>02</span><span>03</span><span>04</span><span>05</span><span>06</span><span>07</span>
                  <span className="border-l border-slate-800 pl-1">08</span><span>09</span><span>0A</span><span>0B</span><span>0C</span><span>0D</span><span>0E</span><span>0F</span>
                </div>
                <div>DECODED ASCII</div>
              </div>

              {/* Hex Rows */}
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
                      {/* Offset */}
                      <span className="text-slate-500 font-mono select-none text-[11px]">
                        {rowOffsetHex}
                      </span>

                      {/* 16 Hex Pairs */}
                      <div className="grid grid-cols-16 gap-1 text-center">
                        {Array.from({ length: 16 }).map((__, cIdx) => {
                          const byteIndex = rowOffset + cIdx;
                          if (byteIndex >= rawBytes.length) {
                            return <span key={`empty-${cIdx}`} className="text-slate-800 select-none">..</span>;
                          }

                          const byteVal = rawBytes[byteIndex];
                          const hexStr = byteVal.toString(16).padStart(2, '0').toUpperCase();
                          const anomaly = byteAnomalyMap.get(byteIndex);
                          const isHovered = hoveredByte === byteIndex;
                          const isSelected = selectedAnomaly && byteIndex >= selectedAnomaly.startByte && byteIndex <= selectedAnomaly.endByte;

                          let byteStyle = 'text-slate-300 hover:bg-slate-800 rounded cursor-pointer';
                          if (anomaly) {
                            if (anomaly.severity === 'CRITICAL' || anomaly.severity === 'HIGH') {
                              byteStyle = 'bg-rose-950 text-rose-200 border border-rose-700 font-bold rounded shadow-sm shadow-rose-900/30';
                            } else {
                              byteStyle = 'bg-amber-950 text-amber-200 border border-amber-700 font-bold rounded shadow-sm shadow-amber-900/30';
                            }
                          }
                          if (isSelected) {
                            byteStyle += ' ring-2 ring-cyan-400';
                          }

                          return (
                            <span
                              key={`hex-${byteIndex}`}
                              onMouseEnter={() => setHoveredByte(byteIndex)}
                              onMouseLeave={() => setHoveredByte(null)}
                              onClick={() => {
                                if (anomaly) setSelectedAnomaly(anomaly);
                              }}
                              className={`py-0.5 px-0.5 transition font-mono ${byteStyle} ${cIdx === 7 ? 'mr-1' : ''}`}
                              title={anomaly ? `${anomaly.title} (Byte 0x${byteIndex.toString(16).toUpperCase()}) - Click to inspect` : `Byte 0x${byteIndex.toString(16).toUpperCase()} (${byteIndex}): ${hexStr}`}
                            >
                              {hexStr}
                            </span>
                          );
                        })}
                      </div>

                      {/* Decoded ASCII Representation */}
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

        {/* ========================================================================= */}
        {/* ACTIVE ANOMALY INSPECTION DRAWER (IF SELECTED OR HOVERED) */}
        {/* ========================================================================= */}
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
                  Byte Range: 0x{selectedAnomaly.startByte.toString(16).toUpperCase()} - 0x{selectedAnomaly.endByte.toString(16).toUpperCase()} ({selectedAnomaly.byteLength} Bytes)
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

        {/* ========================================================================= */}
        {/* FOOTER: FORENSIC UTILITIES & ACTIONS */}
        {/* ========================================================================= */}
        <div className="px-6 py-3.5 border-t border-slate-800 bg-slate-950 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {/* Toggle Pristine vs Tampered Demonstration */}
            <button
              onClick={toggleSimulatedTamper}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition border ${isSimulatedTampered ? 'bg-amber-950/60 text-amber-300 border-amber-800/80 hover:bg-amber-900/60' : 'bg-slate-900 text-slate-300 border-slate-700 hover:bg-slate-800'}`}
              title="Toggle simulated tamper artifacts (mixed CRLF & zero-width space) to test the engine"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>{isSimulatedTampered ? 'Exhibit: Tampered Sample' : 'Exhibit: Pristine Sample'}</span>
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleExportHexDump}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium text-slate-200 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition shadow-sm"
              title="Download standard forensic hex dump text file"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" />
              <span>Export Hex Dump (.hex)</span>
            </button>

            <button
              onClick={handleCopyTamperReport}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium text-slate-200 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition shadow-sm"
              title="Copy JSON Tamper Heuristic Report for legal dossier"
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
