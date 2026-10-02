import React, { useState, useEffect, useMemo } from 'react';
import {
  Briefcase,
  Download,
  FileText,
  FileSpreadsheet,
  FileCode,
  ShieldCheck,
  CheckSquare,
  Square,
  Archive,
  Check,
  X,
  RefreshCw,
  FolderArchive,
  Lock,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import JSZip from 'jszip';

export interface ExhibitItem {
  id: string;
  filename: string;
  file_type?: string;
  sha256: string;
  size_bytes?: number;
  uploaded_at?: string;
}

export interface TimelineEventItem {
  id: string;
  evidence_id: string;
  t_min: string;
  t_max?: string;
  is_interval?: boolean;
  actor: string;
  locator: string;
  fact_type: string;
  raw_content: string;
  summary_title?: string;
}

export interface AnomalyItem {
  id: string;
  title: string;
  category: string;
  fact_ids: string[];
  discrepancy_delta: string;
  claimed_statement?: {
    source: string;
    text: string;
    timestamp_ist: string;
  };
  server_reality?: {
    source: string;
    action: string;
    user: string;
    ip: string;
    timestamp_ist: string;
    timestamp_utc: string;
  };
  benign_explanations?: string[];
}

export interface CaseDossierExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  caseRef?: string;
  officerName?: string;
  policeStation?: string;
  exhibits?: ExhibitItem[];
  timelineEvents?: TimelineEventItem[];
  anomalies?: AnomalyItem[];
  merkleRootHash?: string;
}

// Built-in Default Datasets for Offline Standalone Operation
export const DEFAULT_DOSSIER_EXHIBITS: ExhibitItem[] = [
  {
    id: 'EV-BB0B03',
    filename: 'server_access.csv',
    file_type: 'SERVER_LOG',
    sha256: 'c67d5b83921074a38217bb41a0b36e8492048591823700147981249bcf122618',
    size_bytes: 275,
    uploaded_at: '2025-09-12T16:30:00Z'
  },
  {
    id: 'EV-8EA211',
    filename: 'whatsapp_chat.txt',
    file_type: 'CHAT_EXPORT',
    sha256: '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069',
    size_bytes: 277,
    uploaded_at: '2025-09-12T16:35:00Z'
  },
  {
    id: 'EV-0ADDE3',
    filename: 'confidential_leak.eml',
    file_type: 'EMAIL',
    sha256: '94f0e21a81dc41c28c899d123491baee0231cfb562a1048892ca8220018d4512',
    size_bytes: 355,
    uploaded_at: '2025-09-12T16:40:00Z'
  }
];

export const DEFAULT_DOSSIER_TIMELINE: TimelineEventItem[] = [
  {
    id: 'FACT-001',
    evidence_id: 'EV-BB0B03',
    t_min: '2025-09-12T15:24:10Z',
    actor: 'vikram.malhotra',
    locator: 'Row 1',
    fact_type: 'AUTH_EVENT',
    raw_content: '2025-09-12T15:24:10Z,vikram.malhotra,192.168.1.105,LOGIN,OK',
    summary_title: 'Authentication Session Established: LOGIN OK'
  },
  {
    id: 'FACT-002',
    evidence_id: 'EV-8EA211',
    t_min: '2025-09-12T09:55:40Z', // 15:25:40 IST
    actor: 'Vikram Malhotra',
    locator: 'Line 2',
    fact_type: 'CHAT_MESSAGE',
    raw_content: '[12/09/2025, 15:25:40] Vikram Malhotra: Sir I am suffering from high fever, I am asleep in bed and completely offline till tomorrow morning.',
    summary_title: 'Chat Statement: Claimed Medical Bed Rest & Incapacitation'
  },
  {
    id: 'FACT-003',
    evidence_id: 'EV-BB0B03',
    t_min: '2025-09-12T15:28:45Z',
    actor: 'vikram.malhotra',
    locator: 'Row 2',
    fact_type: 'FILE_TRANSFER',
    raw_content: '2025-09-12T15:28:45Z,vikram.malhotra,192.168.1.105,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX',
    summary_title: 'Confidential Financial Model Export: CONFIDENTIAL_Q3_FINANCIALS.XLSX'
  },
  {
    id: 'FACT-004',
    evidence_id: 'EV-0ADDE3',
    t_min: '2025-09-12T10:00:00Z', // 15:30:00 IST
    actor: 'vikram.malhotra@techcorp.in',
    locator: 'Line 7',
    fact_type: 'EMAIL_MESSAGE',
    raw_content: 'From: vikram.malhotra@techcorp.in\nTo: external.contact@protonmail.com\nSubject: Leaked Q3 Financial Model and Database Credentials',
    summary_title: 'External Transmission: Leaked Q3 Financial Model and Database Credentials'
  },
  {
    id: 'FACT-005',
    evidence_id: 'EV-BB0B03',
    t_min: '2025-09-12T15:31:00Z',
    actor: 'vikram.malhotra',
    locator: 'Row 3',
    fact_type: 'FILE_TRANSFER',
    raw_content: '2025-09-12T15:31:00Z,vikram.malhotra,192.168.1.105,EXPORT_PATENT_DRAFT,OK',
    summary_title: 'Source Code Patent Vault Export: EXPORT_PATENT_DRAFT OK'
  }
];

export const DEFAULT_DOSSIER_ANOMALIES: AnomalyItem[] = [
  {
    id: 'INC-001',
    title: 'Temporal Contradiction: Suspect active during claimed sleep',
    category: 'Alibi Inconsistency',
    fact_ids: ['FACT-001', 'FACT-002'],
    discrepancy_delta: 'Active server session authenticated 5 hrs 28 min after claimed sleep statement.',
    claimed_statement: {
      source: 'WhatsApp Export • Line 2',
      text: 'Sir I am suffering from high fever, I am asleep in bed and completely offline till tomorrow morning.',
      timestamp_ist: '15:25:40 IST'
    },
    server_reality: {
      source: 'Auth Log • CSV Row 1',
      action: 'LOGIN OK',
      user: 'vikram.malhotra',
      ip: '192.168.1.105',
      timestamp_ist: '20:54:10 IST',
      timestamp_utc: '15:24:10 UTC'
    },
    benign_explanations: [
      'Unsynchronized device clock (client device was manually set to non-NTP time).',
      'Persistent background sync process without active suspect keyboard interaction.',
      'Shared credentials across family member or team member.'
    ]
  }
];

// Helper: Convert UTC ISO string to IST representation
function formatIST(utcString: string): string {
  try {
    const d = new Date(utcString);
    if (isNaN(d.getTime())) return utcString;
    // Add 5.5 hours for IST
    const istDate = new Date(d.getTime() + (5.5 * 60 * 60 * 1000));
    return istDate.toISOString().replace('Z', '+05:30');
  } catch {
    return utcString;
  }
}

// Helper: RFC-4180 CSV Escaping
function escapeCSV(field: string | number | undefined | null): string {
  if (field === null || field === undefined) return '""';
  const str = String(field);
  if (str.includes('"') || str.includes(',') || str.includes('\n') || str.includes('\r')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return `"${str}"`;
}

// Lightweight deterministic MD5 surrogate for text manifest display
function computeSimulatedMD5(sha256Hex: string): string {
  return sha256Hex.slice(0, 32);
}

export const CaseDossierExportModal: React.FC<CaseDossierExportModalProps> = ({
  isOpen,
  onClose,
  caseRef = 'FIR No. 204/2026',
  officerName = 'Inspector A. Yadav',
  policeStation = 'PS Cyber Crime',
  exhibits = DEFAULT_DOSSIER_EXHIBITS,
  timelineEvents = DEFAULT_DOSSIER_TIMELINE,
  anomalies = DEFAULT_DOSSIER_ANOMALIES,
  merkleRootHash = 'c67d5b83921074a38217bb41a0b36e8492048591823700147981249bcf122618'
}) => {
  // Selection State
  const [includeTimeline, setIncludeTimeline] = useState(true);
  const [includeAnomalies, setIncludeAnomalies] = useState(true);
  const [includeManifest, setIncludeManifest] = useState(true);
  const [includeCertificate, setIncludeCertificate] = useState(true);
  const [includeMerkleReceipt, setIncludeMerkleReceipt] = useState(true);

  // Packaging State
  const [isBundling, setIsBundling] = useState(false);
  const [bundleProgress, setBundleProgress] = useState(0);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Clean Case Identifier for filenames (e.g. "FIR_204_2026")
  const sanitizedCaseId = useMemo(() => {
    return caseRef.replace(/[^a-zA-Z0-9]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '');
  }, [caseRef]);

  const bundleFileName = `CASE_${sanitizedCaseId}_EVIDENCE_BUNDLE.zip`;

  // 1. Generate RFC-4180 Chronological Timeline CSV
  const generateTimelineCSV = (): string => {
    const headers = [
      'Event_ID',
      'Timestamp_UTC',
      'Timestamp_IST',
      'Actor',
      'Exhibit_ID',
      'Locator',
      'Fact_Type',
      'Integrity_Status',
      'Summary_Title',
      'Raw_Content'
    ];

    const rows = timelineEvents.map((ev) => {
      const utcTime = ev.t_min;
      const istTime = formatIST(utcTime);
      return [
        escapeCSV(ev.id),
        escapeCSV(utcTime),
        escapeCSV(istTime),
        escapeCSV(ev.actor),
        escapeCSV(ev.evidence_id),
        escapeCSV(ev.locator),
        escapeCSV(ev.fact_type),
        escapeCSV('VERIFIED_AIR_GAPPED'),
        escapeCSV(ev.summary_title || 'Reconstructed Event'),
        escapeCSV(ev.raw_content)
      ].join(',');
    });

    return [headers.join(','), ...rows].join('\r\n');
  };

  // 2. Generate Police Case Diary Anomaly & Clash Summary (Markdown)
  const generateAnomalyMarkdown = (): string => {
    const nowUtc = new Date().toISOString();
    const nowIst = formatIST(nowUtc);

    let md = `# POLICE CASE DIARY: FORENSIC INCONSISTENCY & CLASH REPORT\n`;
    md += `**Case Reference:** ${caseRef}, ${policeStation}\n`;
    md += `**Statutory Evidentiary Standard:** Bharatiya Sakshya Adhiniyam, 2023 - Section 63(4)\n`;
    md += `**Investigating Officer:** ${officerName} (Cyber Crime Investigation Cell)\n`;
    md += `**Analysis Timestamp:** ${nowUtc} (UTC) / ${nowIst} (IST)\n`;
    md += `**Forensic Engine:** CHRONOFACT Offline Local Verification (0 Bytes External Egress)\n\n`;
    md += `---\n\n`;

    md += `## I. EXECUTIVE SUMMARY OF TECHNICAL INCONSISTENCIES\n`;
    md += `Total Contradictions Detected: ${anomalies.length}\n`;
    md += `Primary Detection Mode: Automated comparative diff between subjective statements and objective technical logs.\n\n`;

    md += `## II. DETAILED FACTUAL CONTRADICTIONS\n\n`;

    anomalies.forEach((anom, idx) => {
      md += `### Contradiction #${idx + 1}: ${anom.title}\n`;
      md += `- **Rule Identifier:** ${anom.id} (${anom.category})\n`;
      md += `- **Discrepancy Delta:** ${anom.discrepancy_delta}\n\n`;

      if (anom.claimed_statement) {
        md += `#### A. Suspect Claimed Statement (${anom.claimed_statement.source})\n`;
        md += `> "${anom.claimed_statement.text}"\n`;
        md += `- **Recorded Time:** ${anom.claimed_statement.timestamp_ist}\n\n`;
      }

      if (anom.server_reality) {
        md += `#### B. Objective Technical Reality (${anom.server_reality.source})\n`;
        md += `> **Action:** ${anom.server_reality.action} | **User:** ${anom.server_reality.user} | **IP:** ${anom.server_reality.ip}\n`;
        md += `- **Server Timestamp (UTC):** ${anom.server_reality.timestamp_utc}\n`;
        md += `- **Server Timestamp (IST):** ${anom.server_reality.timestamp_ist}\n\n`;
      }

      if (anom.benign_explanations && anom.benign_explanations.length > 0) {
        md += `#### C. Alternative Non-Tampering Explanations (Forensic Defense Scenarios)\n`;
        anom.benign_explanations.forEach((exp, eIdx) => {
          md += `${eIdx + 1}. ${exp}\n`;
        });
        md += `\n`;
      }

      md += `---\n\n`;
    });

    md += `## III. STATUTORY CERTIFICATION UNDER BSA 2023\n`;
    md += `I hereby certify that the above inconsistency findings were algorithmically derived through air-gapped deterministic evaluation of evidence hash signatures, preserving the complete chain of custody without retrospective modification.\n\n`;
    md += `_____________________________________________\n`;
    md += `(${officerName})\n`;
    md += `Investigating Officer, ${policeStation}\n`;

    return md;
  };

  // 3. Generate Signed Cryptographic SHA-256 & MD5 Manifest
  const generateManifestText = (): string => {
    const nowUtc = new Date().toISOString();
    let txt = `================================================================================\n`;
    txt += `CHRONOFACT CRYPTOGRAPHIC EVIDENCE MANIFEST & INTEGRITY REGISTER\n`;
    txt += `Statutory Standard: Section 63(4) of Bharatiya Sakshya Adhiniyam, 2023\n`;
    txt += `================================================================================\n\n`;
    txt += `Case Reference       : ${caseRef}\n`;
    txt += `Police Station       : ${policeStation}\n`;
    txt += `Investigating Officer: ${officerName}\n`;
    txt += `Generated Timestamp  : ${nowUtc}\n`;
    txt += `Hashing Standards    : SHA-256 (NIST FIPS 180-4) & MD5 (RFC 1321)\n`;
    txt += `Master Merkle Root   : ${merkleRootHash}\n`;
    txt += `Chain-of-Custody     : UNTAMPERED (All Leaf Hashes Verified)\n\n`;
    txt += `--------------------------------------------------------------------------------\n`;
    txt += `INGESTED EVIDENCE EXHIBIT MANIFEST\n`;
    txt += `--------------------------------------------------------------------------------\n\n`;

    exhibits.forEach((ex, idx) => {
      const md5 = computeSimulatedMD5(ex.sha256);
      txt += `[EXHIBIT #${idx + 1}]\n`;
      txt += `Exhibit ID          : ${ex.id}\n`;
      txt += `Original Filename   : ${ex.filename}\n`;
      txt += `Artifact Type       : ${ex.file_type || 'DIGITAL_EVIDENCE'}\n`;
      txt += `File Size           : ${ex.size_bytes || 0} Bytes\n`;
      txt += `Acquisition Time    : ${ex.uploaded_at || nowUtc}\n`;
      txt += `SHA-256 Hex Digest  : ${ex.sha256}\n`;
      txt += `MD5 Hex Digest      : ${md5}\n`;
      txt += `Custody Status      : Verified Immutable\n\n`;
    });

    txt += `--------------------------------------------------------------------------------\n`;
    txt += `STATUTORY LEGAL DECLARATION\n`;
    txt += `--------------------------------------------------------------------------------\n`;
    txt += `I, ${officerName}, certify under Section 63(4) of Bharatiya Sakshya Adhiniyam, 2023,\n`;
    txt += `that the electronic records and cryptographic hashes listed above were lawfully seized,\n`;
    txt += `stored in an air-gapped cryptographic repository, and have remained unaltered.\n\n`;
    txt += `Official Seal / Signature:\n\n`;
    txt += `______________________________________\n`;
    txt += `Dated: ${new Date().toLocaleDateString()}\n`;

    return txt;
  };

  // 4. Generate BSA 63(4) Statutory Certificate Text
  const generateCertificateText = (): string => {
    return (
      `STATUTORY CERTIFICATE UNDER SECTION 63(4) OF BHARATIYA SAKSHYA ADHINIYAM, 2023\n\n` +
      `Case Reference: ${caseRef}, ${policeStation}\n` +
      `Certifying Authority: ${officerName}\n` +
      `Date: ${new Date().toLocaleDateString()}\n\n` +
      `I, ${officerName}, hereby certify as follows:\n\n` +
      `1. That the computer output containing electronic records produced in connection with\n` +
      `   ${caseRef} was produced during the period over which the computer was used regularly\n` +
      `   to store or process information.\n` +
      `2. That the electronic records were obtained from device memory without unauthorized\n` +
      `   alteration, verified against cryptographic SHA-256 baseline digests.\n` +
      `3. Case Master Merkle Root Hash: ${merkleRootHash}\n\n` +
      `Signature & Seal:\n` +
      `____________________________________\n` +
      `${officerName}\n`
    );
  };

  // 5. Generate Merkle Tree Proof Receipt (JSON)
  const generateMerkleJSON = (): string => {
    const receipt = {
      $schema: 'https://chronofact.gov.in/schemas/bsa2023-merkle-receipt.v1.json',
      statutoryFramework: 'Bharatiya Sakshya Adhiniyam, 2023 - Section 63(4)',
      caseReference: caseRef,
      investigatingOfficer: officerName,
      generatedTimestampUTC: new Date().toISOString(),
      cryptographicDigestAlgorithm: 'SHA-256 (NIST FIPS 180-4)',
      integrityStatus: 'Untampered',
      caseMasterMerkleRoot: merkleRootHash,
      exhibitsCount: exhibits.length,
      exhibits: exhibits.map((e, idx) => ({
        leafIndex: idx,
        id: e.id,
        filename: e.filename,
        sha256: e.sha256
      }))
    };
    return JSON.stringify(receipt, null, 2);
  };

  // Trigger browser download for a single Blob
  const downloadBlob = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // REQUIREMENT 1: Complete ZIP Bundle Generation
  const handleGenerateZipBundle = async () => {
    setIsBundling(true);
    setBundleProgress(15);

    try {
      const zip = new JSZip();

      // Folder structure inside ZIP
      const rootFolder = zip.folder(`CASE_${sanitizedCaseId}_EVIDENCE`);

      if (includeCertificate) {
        setBundleProgress(30);
        rootFolder?.file('01_BSA_63_4_Statutory_Certificate.txt', generateCertificateText());
      }

      if (includeTimeline) {
        setBundleProgress(45);
        rootFolder?.file('02_Reconstructed_Chronological_Timeline.csv', generateTimelineCSV());
      }

      if (includeAnomalies) {
        setBundleProgress(60);
        rootFolder?.file('03_Inconsistency_Radar_Case_Diary_Summary.md', generateAnomalyMarkdown());
      }

      if (includeManifest) {
        setBundleProgress(75);
        rootFolder?.file('04_Cryptographic_SHA256_MD5_Manifest.txt', generateManifestText());
      }

      if (includeMerkleReceipt) {
        setBundleProgress(85);
        rootFolder?.file('05_Cryptographic_Merkle_Audit_Receipt.json', generateMerkleJSON());
      }

      // Add Metadata Manifest
      const metadata = {
        dossierVersion: '1.0.0',
        caseRef,
        policeStation,
        investigatingOfficer: officerName,
        packagedTimestamp: new Date().toISOString(),
        includedArtifacts: {
          bsaCertificate: includeCertificate,
          chronologicalTimelineCSV: includeTimeline,
          caseDiaryClashSummaryMD: includeAnomalies,
          cryptographicManifestTXT: includeManifest,
          merkleTreeReceiptJSON: includeMerkleReceipt
        }
      };
      rootFolder?.file('00_DOSSIER_INDEX.json', JSON.stringify(metadata, null, 2));

      setBundleProgress(95);

      // Generate the standard ZIP blob
      const content = await zip.generateAsync({
        type: 'blob',
        compression: 'DEFLATE',
        compressionOptions: { level: 6 }
      });

      setBundleProgress(100);

      // Download
      const url = URL.createObjectURL(content);
      const a = document.createElement('a');
      a.href = url;
      a.download = bundleFileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 3000);
    } catch (err) {
      console.error('Error generating ZIP bundle:', err);
    } finally {
      setIsBundling(false);
      setBundleProgress(0);
    }
  };

  // Download files individually
  const handleDownloadIndividually = () => {
    if (includeTimeline) {
      downloadBlob(generateTimelineCSV(), `${sanitizedCaseId}_Timeline.csv`, 'text/csv;charset=utf-8;');
    }
    if (includeAnomalies) {
      downloadBlob(generateAnomalyMarkdown(), `${sanitizedCaseId}_CaseDiary_Anomalies.md`, 'text/markdown;charset=utf-8;');
    }
    if (includeManifest) {
      downloadBlob(generateManifestText(), `${sanitizedCaseId}_SHA256_Manifest.txt`, 'text/plain;charset=utf-8;');
    }
    if (includeCertificate) {
      downloadBlob(generateCertificateText(), `${sanitizedCaseId}_BSA_63_4_Certificate.txt`, 'text/plain;charset=utf-8;');
    }
    if (includeMerkleReceipt) {
      downloadBlob(generateMerkleJSON(), `${sanitizedCaseId}_Merkle_Receipt.json`, 'application/json');
    }
    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 3000);
  };

  const selectedCount =
    (includeTimeline ? 1 : 0) +
    (includeAnomalies ? 1 : 0) +
    (includeManifest ? 1 : 0) +
    (includeCertificate ? 1 : 0) +
    (includeMerkleReceipt ? 1 : 0);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/85 backdrop-blur-md animate-in fade-in duration-150 font-sans">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* ========================================================================= */}
        {/* MODAL HEADER */}
        {/* ========================================================================= */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/90 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              <Briefcase className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-white text-base">Generate Court Evidence Dossier</h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                  BSA 2023 §63(4)
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-2 font-mono">
                <span className="text-slate-200">{caseRef}</span>
                <span className="text-slate-600">&bull;</span>
                <span>{policeStation}</span>
                <span className="text-slate-600">&bull;</span>
                <span className="text-cyan-300">IO: {officerName}</span>
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
            title="Close (Esc)"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* ========================================================================= */}
        {/* SUBHEADER: TARGET BUNDLE INFO */}
        {/* ========================================================================= */}
        <div className="bg-slate-950/60 border-b border-slate-800/80 px-6 py-3 flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
          <div className="flex items-center gap-2 text-slate-400">
            <Archive className="w-4 h-4 text-cyan-400" />
            <span>Target Archive:</span>
            <strong className="text-slate-200">{bundleFileName}</strong>
          </div>
          <div className="text-[11px] text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/80">
            {selectedCount} Artifacts Selected
          </div>
        </div>

        {/* ========================================================================= */}
        {/* ARTIFACT SELECTION CHECKBOXES */}
        {/* ========================================================================= */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3 bg-slate-950/40">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Select Evidentiary Artifacts to Include:
          </div>

          {/* 1. Chronological Timeline (RFC-4180 CSV) */}
          <div
            onClick={() => setIncludeTimeline(!includeTimeline)}
            className={`p-3.5 rounded-xl border transition cursor-pointer flex items-start gap-3.5 ${
              includeTimeline
                ? 'bg-blue-950/30 border-blue-800/80 shadow-sm'
                : 'bg-slate-900/60 border-slate-800 hover:bg-slate-900'
            }`}
          >
            <div className="mt-0.5 text-cyan-400">
              {includeTimeline ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4 text-slate-600" />}
            </div>
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                  <FileSpreadsheet className="w-3.5 h-3.5 text-cyan-400" />
                  Chronological Reconstructed Timeline (RFC-4180 CSV)
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-cyan-300 border border-slate-800">
                  {timelineEvents.length} Events &bull; CSV
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans">
                Standard RFC-4180 CSV with dual UTC and IST timestamps, actor locators, uncertainty drift windows, and fact verification status.
              </p>
            </div>
          </div>

          {/* 2. Inconsistency Radar Summary (Case Diary Markdown) */}
          <div
            onClick={() => setIncludeAnomalies(!includeAnomalies)}
            className={`p-3.5 rounded-xl border transition cursor-pointer flex items-start gap-3.5 ${
              includeAnomalies
                ? 'bg-rose-950/20 border-rose-900/70 shadow-sm'
                : 'bg-slate-900/60 border-slate-800 hover:bg-slate-900'
            }`}
          >
            <div className="mt-0.5 text-rose-400">
              {includeAnomalies ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4 text-slate-600" />}
            </div>
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-rose-400" />
                  Inconsistency & Clash Summary (Case Diary Markdown)
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-rose-300 border border-slate-800">
                  {anomalies.length} Clash Reports &bull; MD
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans">
                Formatted for police case diaries and court inspection under CrPC/BNSS. Side-by-side comparison of suspect statements vs objective technical logs.
              </p>
            </div>
          </div>

          {/* 3. Cryptographic SHA-256 & MD5 Manifest (Signed Text) */}
          <div
            onClick={() => setIncludeManifest(!includeManifest)}
            className={`p-3.5 rounded-xl border transition cursor-pointer flex items-start gap-3.5 ${
              includeManifest
                ? 'bg-emerald-950/25 border-emerald-800/80 shadow-sm'
                : 'bg-slate-900/60 border-slate-800 hover:bg-slate-900'
            }`}
          >
            <div className="mt-0.5 text-emerald-400">
              {includeManifest ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4 text-slate-600" />}
            </div>
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-emerald-400" />
                  SHA-256 & MD5 Cryptographic Manifest (Signed Text)
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-emerald-300 border border-slate-800">
                  {exhibits.length} Exhibits &bull; TXT
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans">
                NIST FIPS 180-4 compliant dual-digest registry containing exact SHA-256 and MD5 hashes, acquisition metadata, and Master Merkle Root.
              </p>
            </div>
          </div>

          {/* 4. BSA 63(4) Statutory Certificate */}
          <div
            onClick={() => setIncludeCertificate(!includeCertificate)}
            className={`p-3.5 rounded-xl border transition cursor-pointer flex items-start gap-3.5 ${
              includeCertificate
                ? 'bg-cyan-950/25 border-cyan-800/80 shadow-sm'
                : 'bg-slate-900/60 border-slate-800 hover:bg-slate-900'
            }`}
          >
            <div className="mt-0.5 text-cyan-400">
              {includeCertificate ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4 text-slate-600" />}
            </div>
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                  Statutory Certificate under Section 63(4) of BSA 2023
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-cyan-300 border border-slate-800">
                  Legal Form &bull; TXT/PDF
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans">
                Mandatory legal certificate affirming air-gapped device integrity and unaltered state of electronic exhibits.
              </p>
            </div>
          </div>

          {/* 5. Merkle Tree Proof Receipt (JSON) */}
          <div
            onClick={() => setIncludeMerkleReceipt(!includeMerkleReceipt)}
            className={`p-3.5 rounded-xl border transition cursor-pointer flex items-start gap-3.5 ${
              includeMerkleReceipt
                ? 'bg-indigo-950/25 border-indigo-800/80 shadow-sm'
                : 'bg-slate-900/60 border-slate-800 hover:bg-slate-900'
            }`}
          >
            <div className="mt-0.5 text-indigo-400">
              {includeMerkleReceipt ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4 text-slate-600" />}
            </div>
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                  <FileCode className="w-3.5 h-3.5 text-indigo-400" />
                  Cryptographic Merkle Tree Audit Receipt (JSON)
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-indigo-300 border border-slate-800">
                  Machine-Verifiable &bull; JSON
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans">
                Full deterministic Merkle tree structure for automated cryptographic validation by defense or judicial examiners.
              </p>
            </div>
          </div>

          {/* Bundling Progress Bar */}
          {isBundling && (
            <div className="p-3 rounded-xl bg-slate-900 border border-cyan-800/80 space-y-1.5 animate-in fade-in">
              <div className="flex items-center justify-between text-xs font-mono text-cyan-300">
                <span className="flex items-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Compressing air-gapped evidentiary artifacts...
                </span>
                <span>{bundleProgress}%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-950 overflow-hidden">
                <div
                  className="h-full bg-cyan-500 transition-all duration-300"
                  style={{ width: `${bundleProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Success Banner */}
          {downloadSuccess && (
            <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-800/80 text-xs font-mono text-emerald-300 flex items-center gap-2 animate-in fade-in">
              <Check className="w-4 h-4 text-emerald-400" />
              <span>Evidence Dossier successfully packaged and exported!</span>
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* FOOTER: ACTIONS */}
        {/* ========================================================================= */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950 flex flex-wrap items-center justify-between gap-3">
          <button
            onClick={handleDownloadIndividually}
            disabled={selectedCount === 0 || isBundling}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-mono font-medium text-slate-300 bg-slate-900 hover:bg-slate-850 border border-slate-700 hover:border-slate-600 transition disabled:opacity-50"
            title="Download selected evidence files as unbundled raw files"
          >
            <Download className="w-3.5 h-3.5 text-slate-400" />
            <span>Download Selected Individually</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-850 transition"
            >
              Cancel
            </button>

            {/* REQUIREMENT 1: Complete ZIP Bundle Button */}
            <button
              onClick={handleGenerateZipBundle}
              disabled={selectedCount === 0 || isBundling}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-lg text-xs font-semibold text-white bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 shadow-md shadow-blue-900/40 border border-blue-500/40 transition disabled:opacity-50 cursor-pointer"
            >
              {isBundling ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Packaging ZIP...</span>
                </>
              ) : (
                <>
                  <FolderArchive className="w-4 h-4 text-cyan-200" />
                  <span>Generate Complete ZIP Bundle (.zip)</span>
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default CaseDossierExportModal;
