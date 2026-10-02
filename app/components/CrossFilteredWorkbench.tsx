import React, { useState, useMemo, useRef, useCallback } from 'react';
import {
  Filter,
  X,
  Copy,
  Check,
  Locate,
  AlertTriangle,
  Clock,
  ChevronDown,
  CheckCircle2,
  FileText,
  Database,
  Mail,
  MessageSquare,
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  Terminal,
  FilterX
} from 'lucide-react';
import { TimelineSearchFilterToolbar, TimelineEmptyState, FilterStats } from './TimelineSearchFilterToolbar';

export interface ExhibitItem {
  id: string; // e.g. "EV-BB0B03"
  filename: string; // e.g. "server_access.csv"
  file_type: 'SERVER_LOG' | 'CHAT_EXPORT' | 'EMAIL' | 'DOCUMENT';
  sha256: string;
  size_bytes: number;
  uploaded_at: string;
}

export interface TimelineEvent {
  id: string; // e.g. "FACT-001"
  evidence_id: string; // e.g. "EV-BB0B03"
  t_min: string;
  t_max?: string;
  is_interval: boolean;
  actor: string;
  locator: string; // e.g. "Row 1", "Line 2"
  fact_type: 'AUTH_EVENT' | 'FILE_TRANSFER' | 'CHAT_MESSAGE' | 'EMAIL_MESSAGE';
  raw_content: string;
  summary_title?: string;
}

export interface AnomalyItem {
  id: string; // e.g. "INC-001"
  title: string;
  category: string;
  fact_ids: string[]; // e.g. ["FACT-001", "FACT-002"]
  discrepancy_delta: string;
  claimed_statement: {
    source: string;
    text: string;
    timestamp_ist: string;
  };
  server_reality: {
    source: string;
    action: string;
    user: string;
    ip: string;
    timestamp_ist: string;
    timestamp_utc: string;
  };
  benign_explanations: string[];
}

export interface CrossFilteredWorkbenchProps {
  initialExhibits?: ExhibitItem[];
  initialEvents?: TimelineEvent[];
  initialAnomalies?: AnomalyItem[];
  onExhibitSelected?: (exhibitId: string | null) => void;
  onAnomalyClicked?: (anomalyId: string, targetFactId: string) => void;
}

// Built-in Sample Datasets for Plug-and-Play Testing
export const MOCK_EXHIBITS: ExhibitItem[] = [
  {
    id: 'EV-BB0B03',
    filename: 'server_access.csv',
    file_type: 'SERVER_LOG',
    sha256: 'c67d5b83921074a38217bb41a0b36e8492048591823700147981249bcf122618',
    size_bytes: 275,
    uploaded_at: '2026-10-02T16:30:00Z'
  },
  {
    id: 'EV-8EA211',
    filename: 'whatsapp_chat.txt',
    file_type: 'CHAT_EXPORT',
    sha256: '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069',
    size_bytes: 277,
    uploaded_at: '2026-10-02T16:35:00Z'
  },
  {
    id: 'EV-0ADDE3',
    filename: 'confidential_leak.eml',
    file_type: 'EMAIL',
    sha256: '94f0e21a81dc41c28c899d123491baee0231cfb562a1048892ca8220018d4512',
    size_bytes: 355,
    uploaded_at: '2026-10-02T16:40:00Z'
  }
];

export const MOCK_TIMELINE_EVENTS: TimelineEvent[] = [
  {
    id: 'FACT-001',
    evidence_id: 'EV-BB0B03',
    t_min: '2025-09-12T15:24:10Z',
    is_interval: false,
    actor: 'vikram.malhotra',
    locator: 'Row 1',
    fact_type: 'AUTH_EVENT',
    raw_content: '2025-09-12T15:24:10Z,vikram.malhotra,192.168.1.105,LOGIN,OK',
    summary_title: 'Authentication Session Established: LOGIN OK'
  },
  {
    id: 'FACT-002',
    evidence_id: 'EV-8EA211',
    t_min: '2025-09-12T09:55:40Z', // 15:25:40 IST is 09:55:40 UTC
    is_interval: false,
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
    is_interval: false,
    actor: 'vikram.malhotra',
    locator: 'Row 2',
    fact_type: 'FILE_TRANSFER',
    raw_content: '2025-09-12T15:28:45Z,vikram.malhotra,192.168.1.105,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX',
    summary_title: 'Confidential Financial Model Export: CONFIDENTIAL_Q3_FINANCIALS.XLSX'
  },
  {
    id: 'FACT-004',
    evidence_id: 'EV-0ADDE3',
    t_min: '2025-09-12T10:00:00Z', // 15:30:00 IST is 10:00:00 UTC
    is_interval: true,
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
    is_interval: false,
    actor: 'vikram.malhotra',
    locator: 'Row 3',
    fact_type: 'FILE_TRANSFER',
    raw_content: '2025-09-12T15:31:00Z,vikram.malhotra,192.168.1.105,EXPORT_PATENT_DRAFT,OK',
    summary_title: 'Source Code Patent Vault Export: EXPORT_PATENT_DRAFT OK'
  }
];

export const MOCK_ANOMALIES: AnomalyItem[] = [
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

export const CrossFilteredWorkbench: React.FC<CrossFilteredWorkbenchProps> = ({
  initialExhibits = MOCK_EXHIBITS,
  initialEvents = MOCK_TIMELINE_EVENTS,
  initialAnomalies = MOCK_ANOMALIES,
  onExhibitSelected,
  onAnomalyClicked
}) => {
  // State 1: Active Exhibit Cross-Filtering
  const [selectedExhibitId, setSelectedExhibitId] = useState<string | null>(null);

  // State 2: Anomaly Pulser Targeting
  const [pulsingEventId, setPulsingEventId] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);
  const [expandedDrawerId, setExpandedDrawerId] = useState<string | null>(null);

  // DOM node references for timeline auto-scrolling
  const timelineNodeRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});
  const filterBannerRef = useRef<HTMLDivElement | null>(null);

  // Active Exhibit Metadata
  const selectedExhibit = useMemo(() => {
    if (!selectedExhibitId) return null;
    return initialExhibits.find((e) => e.id === selectedExhibitId) || null;
  }, [selectedExhibitId, initialExhibits]);

  // Filtered timeline events logic
  const [toolbarFilteredEvents, setToolbarFilteredEvents] = useState<TimelineEvent[]>(initialEvents);

  const handleFilteredEventsChange = useCallback((filtered: TimelineEvent[]) => {
    setToolbarFilteredEvents(filtered);
  }, []);

  // Requirement 1: Exhibit Row Selection Handler
  const handleExhibitRowClick = useCallback(
    (exhibitId: string) => {
      setSelectedExhibitId((prev) => {
        const next = prev === exhibitId ? null : exhibitId;
        if (onExhibitSelected) onExhibitSelected(next);
        return next;
      });

      // Smooth scroll timeline banner into view
      setTimeout(() => {
        if (filterBannerRef.current) {
          filterBannerRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }, 50);
    },
    [onExhibitSelected]
  );

  // Requirement 1: Clear Filter Handler
  const handleClearFilter = useCallback(() => {
    setSelectedExhibitId(null);
    if (onExhibitSelected) onExhibitSelected(null);
  }, [onExhibitSelected]);

  // Requirement 3: Anomaly Card Click -> Clear Filter & Scroll with Pulsing Highlight
  const handleAnomalyCardClick = useCallback(
    (anomaly: AnomalyItem) => {
      // 1. Clear active exhibit filters
      setSelectedExhibitId(null);
      if (onExhibitSelected) onExhibitSelected(null);

      const targetFactId = anomaly.fact_ids[0];
      if (!targetFactId) return;

      if (onAnomalyClicked) {
        onAnomalyClicked(anomaly.id, targetFactId);
      }

      // 2. Smoothly scroll to target event node on timeline
      setTimeout(() => {
        const nodeEl = timelineNodeRefs.current[targetFactId];
        if (nodeEl) {
          nodeEl.scrollIntoView({ behavior: 'smooth', block: 'center' });

          // 3. Apply 2-second glowing ring animation
          setPulsingEventId(targetFactId);
          setTimeout(() => {
            setPulsingEventId(null);
          }, 2000);
        }
      }, 120);
    },
    [onExhibitSelected, onAnomalyClicked]
  );

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(text);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const truncateHash = (hash: string) => {
    if (!hash || hash.length < 16) return hash;
    return `${hash.slice(0, 8)}...${hash.slice(-8)}`;
  };

  const getFileTypeBadge = (type: string) => {
    switch (type) {
      case 'SERVER_LOG':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-amber-950/40 text-amber-300 border border-amber-800/50">
            <Database className="w-3 h-3 text-amber-400" /> Server Log
          </span>
        );
      case 'CHAT_EXPORT':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-cyan-950/40 text-cyan-300 border border-cyan-800/50">
            <MessageSquare className="w-3 h-3 text-cyan-400" /> Chat Export
          </span>
        );
      case 'EMAIL':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-indigo-950/40 text-indigo-300 border border-indigo-800/50">
            <Mail className="w-3 h-3 text-indigo-400" /> Email
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
            <FileText className="w-3 h-3" /> Document
          </span>
        );
    }
  };

  return (
    <div className="space-y-8 p-4 sm:p-6 bg-slate-950 text-slate-100 min-h-screen">
      
      {/* ========================================================================= */}
      {/* SECTION 1: CASE EVIDENCE & EXHIBITS TABLE */}
      {/* ========================================================================= */}
      <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <span>Case Evidence & Exhibits</span>
              <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                {initialExhibits.length} Exhibits
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Click any exhibit row to filter the Reconstructed Event Timeline by source file.
            </p>
          </div>
          {selectedExhibitId && (
            <button
              onClick={handleClearFilter}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-blue-400 bg-blue-950/60 hover:bg-blue-900/60 border border-blue-800 transition self-start"
            >
              <X className="w-3.5 h-3.5" />
              <span>Clear Filter</span>
            </button>
          )}
        </div>

        {/* Responsive Evidence Table */}
        <div className="overflow-x-auto rounded-xl border border-slate-800/80 bg-slate-950/50">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/80 text-[11px] uppercase font-mono tracking-wider text-slate-400 select-none">
                <th className="py-3 px-4">Exhibit ID</th>
                <th className="py-3 px-4">Artifact Name</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">SHA-256 Cryptographic Hash</th>
                <th className="py-3 px-4">File Size</th>
                <th className="py-3 px-4">Seizure Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {initialExhibits.map((item) => {
                const isSelected = selectedExhibitId === item.id;
                return (
                  <tr
                    key={item.id}
                    onClick={() => handleExhibitRowClick(item.id)}
                    className={`cursor-pointer transition-all duration-200 select-none ${
                      isSelected
                        ? 'ring-1 ring-blue-500 bg-blue-950/20 shadow-sm'
                        : 'hover:bg-slate-800/40'
                    }`}
                    title={isSelected ? 'Click to deselect filter' : 'Click to filter timeline by this exhibit'}
                  >
                    {/* Exhibit ID */}
                    <td className={`py-3 px-4 font-mono font-medium flex items-center gap-2 ${
                      isSelected ? 'text-blue-400 font-bold' : 'text-cyan-400'
                    }`}>
                      {isSelected ? (
                        <Check className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                      ) : (
                        <span className="w-3.5 h-3.5 inline-block" />
                      )}
                      <span>{item.id}</span>
                    </td>

                    {/* Artifact Name */}
                    <td className="py-3 px-4 font-medium text-white group-hover:text-cyan-300">
                      {item.filename}
                    </td>

                    {/* Format Badge */}
                    <td className="py-3 px-4">{getFileTypeBadge(item.file_type)}</td>

                    {/* Truncated Hash + 1-Click Copy */}
                    <td className="py-3 px-4 font-mono" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center gap-2">
                        <span
                          className="text-slate-300 text-[11px] bg-slate-900 px-2 py-0.5 rounded border border-slate-800"
                          title={item.sha256}
                        >
                          {truncateHash(item.sha256)}
                        </span>
                        <button
                          onClick={() => copyToClipboard(item.sha256)}
                          className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition"
                          title="Copy full SHA-256 hash"
                        >
                          {copiedHash === item.sha256 ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    </td>

                    {/* File Size */}
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {(item.size_bytes / 1024).toFixed(1)} KB
                    </td>

                    {/* Seizure Timestamp */}
                    <td className="py-3 px-4 text-slate-400 text-[11px] font-sans">
                      {new Date(item.uploaded_at).toLocaleDateString('en-IN', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric'
                      })}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* SECTION 2: INCONSISTENCY RADAR (Anomaly Cross-Linking) */}
      {/* ========================================================================= */}
      <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <span>Inconsistency Radar</span>
              <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-rose-950/80 text-rose-300 border border-rose-800/60">
                {initialAnomalies.length} Anomalies
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Click an anomaly card to clear all filters and jump smoothly to conflicting nodes on the timeline.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {initialAnomalies.map((inc) => {
            const isDrawerOpen = expandedDrawerId === inc.id;
            return (
              <div
                key={inc.id}
                onClick={() => handleAnomalyCardClick(inc)}
                className="bg-slate-950/80 border border-rose-900/40 hover:border-rose-700/60 rounded-xl p-4 transition duration-200 shadow-sm space-y-3.5 cursor-pointer hover:bg-rose-950/20 group"
                title="Click anomaly card to clear filters and jump to conflicting events on timeline"
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] uppercase font-bold font-mono tracking-wider px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800/60">
                        {inc.category}
                      </span>
                      <span className="text-[11px] font-mono text-slate-500">{inc.id}</span>
                    </div>
                    <h3 className="text-sm font-semibold text-rose-200 tracking-wide group-hover:text-rose-100 transition">
                      {inc.title}
                    </h3>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAnomalyCardClick(inc);
                    }}
                    className="p-2 rounded-lg bg-rose-950/50 hover:bg-rose-900/70 text-rose-400 border border-rose-800/60 transition shrink-0"
                    title="Locate conflicting events on timeline"
                  >
                    <Locate className="w-4 h-4" />
                  </button>
                </div>

                {/* Side-by-Side Diff */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  {/* Left: Claimed Statement */}
                  <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 flex flex-col justify-between space-y-2">
                    <div>
                      <div className="flex items-center justify-between text-[10px] font-semibold text-cyan-400 uppercase tracking-wider">
                        <span>Claimed Statement</span>
                        <MessageSquare className="w-3.5 h-3.5 opacity-60" />
                      </div>
                      <p className="text-slate-300 italic text-[11px] leading-relaxed mt-1.5">
                        "{inc.claimed_statement.text}"
                      </p>
                    </div>
                    <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px]">
                      <span className="text-slate-400">{inc.claimed_statement.source}</span>
                      <span className="font-mono text-cyan-400 font-medium">
                        {inc.claimed_statement.timestamp_ist}
                      </span>
                    </div>
                  </div>

                  {/* Right: Server Reality */}
                  <div className="p-3.5 rounded-lg bg-rose-950/25 border border-rose-900/40 flex flex-col justify-between space-y-2">
                    <div>
                      <div className="flex items-center justify-between text-[10px] font-semibold text-rose-400 uppercase tracking-wider">
                        <span>Server Reality</span>
                        <Database className="w-3.5 h-3.5 opacity-60" />
                      </div>
                      <div className="mt-1 font-mono text-rose-200 text-[11px] leading-relaxed space-y-0.5">
                        <div className="font-semibold">{inc.server_reality.action}</div>
                        <div className="text-[10px] text-rose-300/80">
                          User: {inc.server_reality.user} &bull; {inc.server_reality.ip}
                        </div>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-rose-900/30 flex items-center justify-between text-[10px]">
                      <span className="text-slate-400">{inc.server_reality.source}</span>
                      <span className="font-mono text-rose-300 font-medium">
                        {inc.server_reality.timestamp_ist}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Discrepancy Pill */}
                <div className="px-3 py-2 rounded-lg bg-rose-950/40 border border-rose-900/50 flex items-center gap-2 text-xs text-rose-300">
                  <Clock className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                  <span>
                    <strong>Discrepancy:</strong> {inc.discrepancy_delta}
                  </span>
                </div>

                {/* Benign Explanations Accordion */}
                <div className="pt-1" onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setExpandedDrawerId(isDrawerOpen ? null : inc.id);
                    }}
                    className="w-full flex items-center justify-between py-1.5 px-3 rounded-lg bg-slate-900 hover:bg-slate-850 text-slate-400 hover:text-slate-200 text-xs font-medium transition border border-slate-800"
                  >
                    <span className="flex items-center gap-1.5 text-amber-400/90 text-[11px]">
                      <span>View {inc.benign_explanations.length} Alternative Non-Tampering Explanations</span>
                    </span>
                    <ChevronDown
                      className={`w-3.5 h-3.5 transition-transform duration-200 ${
                        isDrawerOpen ? 'rotate-180' : ''
                      }`}
                    />
                  </button>
                  {isDrawerOpen && (
                    <div className="mt-2 p-3 rounded-lg bg-amber-950/15 border border-amber-900/30 text-xs space-y-1 text-slate-300">
                      <p className="text-[10px] uppercase font-semibold text-amber-400 tracking-wider mb-1 font-mono">
                        Plausible Non-Tampering Scenarios:
                      </p>
                      <ul className="list-disc list-inside space-y-1 text-slate-400 text-[11px]">
                        {inc.benign_explanations.map((exp, idx) => (
                          <li key={idx}>{exp}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ========================================================================= */}
      {/* SECTION 3: RECONSTRUCTED EVENT TIMELINE */}
      {/* ========================================================================= */}
      <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <span>Reconstructed Event Timeline</span>
              <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                {toolbarFilteredEvents.length} Events {selectedExhibitId ? '(Filtered)' : ''}
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Strict partial ordering verified against cryptographic log headers and device offsets.
            </p>
          </div>
        </div>

        {/* Advanced Search & Filter Toolbar */}
        <TimelineSearchFilterToolbar
          events={initialEvents}
          activeExhibitFilter={selectedExhibitId}
          onClearExhibitFilter={handleClearFilter}
          onFilteredEventsChange={handleFilteredEventsChange}
        />

        {/* Requirement 1: Active Filter Banner */}
        {selectedExhibit && (
          <div
            ref={filterBannerRef}
            className="p-3 rounded-xl bg-blue-950/30 border border-blue-800/50 text-xs flex items-center justify-between shadow-sm animate-in fade-in duration-200"
          >
            <div className="flex items-center gap-2.5">
              <div className="p-1 rounded-md bg-blue-500/20 text-blue-400">
                <Filter className="w-3.5 h-3.5" />
              </div>
              <span className="text-slate-300">
                Filtered by:{' '}
                <strong className="text-blue-300 font-mono">
                  [{selectedExhibit.id}]
                </strong>{' '}
                <span className="text-slate-400 font-mono">({toolbarFilteredEvents.length} events)</span>
              </span>
            </div>
            <button
              onClick={handleClearFilter}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium text-blue-300 bg-blue-900/40 hover:bg-blue-800/60 border border-blue-700/50 transition cursor-pointer"
            >
              <X className="w-3 h-3" />
              <span>Reset Filter</span>
            </button>
          </div>
        )}

        {/* Requirement 2: Clean Empty State when no events match */}
        {toolbarFilteredEvents.length === 0 ? (
          <TimelineEmptyState
            onClearFilters={() => {
              handleClearFilter();
              setToolbarFilteredEvents(initialEvents);
            }}
            hasFilters={true}
          />
        ) : (
          /* Timeline Vertical Track */
          <div className="relative pl-6 space-y-6 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-800 pt-2">
            {toolbarFilteredEvents.map((ev) => {
              const isPulsing = pulsingEventId === ev.id;
              const isExact = !ev.is_interval;

              return (
                <div
                  key={ev.id}
                  ref={(el) => {
                    timelineNodeRefs.current[ev.id] = el;
                  }}
                  className={`relative group transition-all duration-500 ${
                    isPulsing
                      ? 'ring-4 ring-rose-500 shadow-2xl shadow-rose-500/50 p-3 rounded-2xl bg-rose-950/40'
                      : ''
                  }`}
                >
                  {/* Timeline Dot Marker */}
                  <div
                    className={`absolute -left-[30px] top-2 w-4 h-4 rounded-full flex items-center justify-center transition-all ${
                      isPulsing
                        ? 'bg-rose-500 ring-4 ring-rose-950 animate-ping'
                        : isExact
                        ? 'bg-emerald-500 ring-4 ring-emerald-950/80'
                        : 'bg-amber-500 ring-4 ring-amber-950/80 animate-pulse'
                    }`}
                  />

                  {/* Event Card */}
                  <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 hover:border-slate-700 transition space-y-2.5">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-cyan-400 font-bold">{ev.id}</span>
                        <span className="text-slate-500">&bull;</span>
                        <span className="text-slate-300 font-semibold">
                          {ev.summary_title || ev.raw_content}
                        </span>
                      </div>
                      <span className="font-mono text-[11px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800 self-start sm:self-auto">
                        {ev.t_min}
                      </span>
                    </div>

                    {/* Metadata Pills */}
                    <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono text-slate-400">
                      <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                        Actor: {ev.actor}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-blue-300">
                        Exhibit: {ev.evidence_id}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                        Locator: {ev.locator}
                      </span>
                      {isExact ? (
                        <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                          Exact (Zero Skew)
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-amber-950/60 text-amber-400 border border-amber-800/60">
                          ± 4h Drift Window
                        </span>
                      )}
                    </div>

                    {/* Verbatim Code Snippet */}
                    <div className="p-2.5 rounded-lg bg-black/60 border border-slate-850 font-mono text-[11px] text-slate-300 overflow-x-auto whitespace-pre-wrap break-all">
                      {ev.raw_content}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

    </div>
  );
};

export default CrossFilteredWorkbench;
