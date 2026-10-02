import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  MapPin,
  X,
  AlertTriangle,
  ShieldAlert,
  Radio,
  Server,
  MessageSquare,
  Copy,
  Check,
  Compass,
  Activity
} from 'lucide-react';

export const DEFAULT_GEO_POINTS = [
  {
    id: 'geo-claimed-01',
    type: 'claimed_alibi',
    label: "Suspect's Self-Claimed Alibi Location",
    sublabel: 'Home Residence (Bed Rest Alibi), Gurugram Sector 48, Haryana',
    latitude: 28.4231,
    longitude: 77.0422,
    timestamp: '2025-09-12 15:25:40 IST',
    sourceExhibitId: 'EV-8EA211 (whatsapp_chat.txt)',
    metadata: {
      accuracyRadiusMeters: 50
    }
  },
  {
    id: 'geo-ip-02',
    type: 'ip_egress',
    label: 'ISP / Public IP Geo-Location',
    sublabel: 'AWS Asia-Pacific Datacenter / Corporate VPN Egress, Bengaluru',
    latitude: 12.9716,
    longitude: 77.5946,
    timestamp: '2025-09-12 15:24:10 UTC (20:54:10 IST)',
    sourceExhibitId: 'EV-BB0B03 (server_access.csv)',
    metadata: {
      ipAddress: '103.21.124.58 (LAN: 192.168.1.105)',
      ispName: 'Amazon Data Services / Tata Teleservices WAN',
      asn: 'AS16509',
      accuracyRadiusMeters: 5000
    }
  },
  {
    id: 'geo-cdr-03',
    type: 'cell_tower',
    label: 'Suspect Cell Tower Coordinates (CDR Triangulation)',
    sublabel: 'Tower DEL-CYB-0982 (Indira Gandhi Airport Aerocity, New Delhi)',
    latitude: 28.5562,
    longitude: 77.1000,
    timestamp: '2025-09-12 15:28:12 IST',
    sourceExhibitId: 'EV-78BC5A (cdr_telco_export.csv)',
    metadata: {
      towerId: 'DEL-CYB-0982',
      cgi: '404-45-1204-0982',
      azimuth: 120,
      accuracyRadiusMeters: 450
    }
  }
];

export function calculateDistanceKm(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) *
      Math.cos(lat2 * (Math.PI / 180)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10;
}

export function GeoLocationDrawer({
  isOpen,
  onClose,
  points = DEFAULT_GEO_POINTS,
  caseRef = 'FIR No. 204/2026, PS Cyber Crime',
  anomalyTitle = 'Temporal & Spatial Contradiction: Suspect Alibi vs Network Egress'
}) {
  const [selectedPointId, setSelectedPointId] = useState(points[0]?.id || '');
  const [copiedText, setCopiedText] = useState(null);
  const [activeLayer, setActiveLayer] = useState('all');

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const distanceAnalysis = useMemo(() => {
    const alibi = points.find((p) => p.type === 'claimed_alibi');
    const ip = points.find((p) => p.type === 'ip_egress');
    const tower = points.find((p) => p.type === 'cell_tower');

    let maxDistanceKm = 0;
    let alibiToIpKm = 0;
    let alibiToTowerKm = 0;

    if (alibi && ip) {
      alibiToIpKm = calculateDistanceKm(alibi.latitude, alibi.longitude, ip.latitude, ip.longitude);
      maxDistanceKm = Math.max(maxDistanceKm, alibiToIpKm);
    }
    if (alibi && tower) {
      alibiToTowerKm = calculateDistanceKm(alibi.latitude, alibi.longitude, tower.latitude, tower.longitude);
      maxDistanceKm = Math.max(maxDistanceKm, alibiToTowerKm);
    }

    const isImpossible = maxDistanceKm > 50;

    return {
      alibiToIpKm,
      alibiToTowerKm,
      maxDistanceKm,
      isImpossible
    };
  }, [points]);

  const visiblePoints = useMemo(() => {
    if (activeLayer === 'all') return points;
    if (activeLayer === 'alibi') return points.filter((p) => p.type === 'claimed_alibi');
    if (activeLayer === 'ip') return points.filter((p) => p.type === 'ip_egress');
    if (activeLayer === 'tower') return points.filter((p) => p.type === 'cell_tower');
    return points;
  }, [points, activeLayer]);

  const activePoint = useMemo(() => {
    return points.find((p) => p.id === selectedPointId) || points[0];
  }, [points, selectedPointId]);

  const handleCopy = (text, label) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200 select-none">
      <div className="flex-1 cursor-pointer" onClick={onClose} />

      <div className="w-full max-w-3xl bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col h-full overflow-hidden animate-in slide-in-from-right duration-300">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-inner">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                  Geo-Location & IP Intelligence Drawer
                </h2>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  Air-Gapped Map Engine
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-2">
                <span>{caseRef}</span>
                <span className="text-slate-600">&bull;</span>
                <span className="text-cyan-400 font-mono">CDR Triangulation & Geodesic Bounds</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
              title="Close Drawer (Esc)"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Geographic Impossibility Flag Banner */}
        {distanceAnalysis.isImpossible && (
          <div className="bg-rose-950/70 border-b border-rose-800/80 px-6 py-3.5 flex items-start gap-3.5 shadow-inner">
            <div className="p-1.5 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30 mt-0.5 shrink-0">
              <ShieldAlert className="w-5 h-5 animate-pulse" />
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-rose-200 uppercase tracking-wider text-xs">
                  Geographic Impossibility Flag: Physical location mismatch detected
                </span>
                <span className="px-1.5 py-0.2 rounded bg-rose-900/80 text-rose-200 text-[10px] font-mono border border-rose-700">
                  Delta: {distanceAnalysis.maxDistanceKm} km
                </span>
              </div>
              <p className="text-rose-300/90 leading-relaxed font-sans text-xs">
                Suspect claimed in WhatsApp to be incapacitated in bed at Gurugram, while an active server login 
                occurred within minutes via ISP egress in Bengaluru ({distanceAnalysis.alibiToIpKm} km separation). 
                Under <strong>BSA 2023 §63</strong>, this physically refutes the ungrounded alibi statement.
              </p>
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* Filter Pins */}
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px]">
              <span className="px-2 text-slate-500 uppercase font-bold text-[10px]">Filter Pins:</span>
              <button
                onClick={() => setActiveLayer('all')}
                className={`px-2.5 py-1 rounded-lg transition ${
                  activeLayer === 'all' ? 'bg-slate-800 text-white font-semibold shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                All (3)
              </button>
              <button
                onClick={() => setActiveLayer('alibi')}
                className={`px-2.5 py-1 rounded-lg transition ${
                  activeLayer === 'alibi' ? 'bg-cyan-950 text-cyan-300 font-semibold border border-cyan-800/60' : 'text-slate-400 hover:text-cyan-300'
                }`}
              >
                Claimed Alibi
              </button>
              <button
                onClick={() => setActiveLayer('ip')}
                className={`px-2.5 py-1 rounded-lg transition ${
                  activeLayer === 'ip' ? 'bg-rose-950 text-rose-300 font-semibold border border-rose-800/60' : 'text-slate-400 hover:text-rose-300'
                }`}
              >
                ISP / IP Egress
              </button>
              <button
                onClick={() => setActiveLayer('tower')}
                className={`px-2.5 py-1 rounded-lg transition ${
                  activeLayer === 'tower' ? 'bg-amber-950 text-amber-300 font-semibold border border-amber-800/60' : 'text-slate-400 hover:text-amber-300'
                }`}
              >
                Cell Tower
              </button>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono text-slate-500">Coordinate Grid: WGS-84</span>
            </div>
          </div>

          {/* Tactical Vector Forensic Map */}
          <div className="relative rounded-2xl border border-slate-800 bg-slate-950 overflow-hidden shadow-2xl h-[340px] flex items-center justify-center">
            
            <div
              className="absolute inset-0 opacity-20"
              style={{
                backgroundImage:
                  'linear-gradient(to right, #334155 1px, transparent 1px), linear-gradient(to bottom, #334155 1px, transparent 1px)',
                backgroundSize: '32px 32px'
              }}
            />

            <div className="absolute w-[440px] h-[440px] rounded-full border border-slate-800/50 pointer-events-none" />
            <div className="absolute w-[280px] h-[280px] rounded-full border border-slate-800/60 pointer-events-none" />
            <div className="absolute w-[120px] h-[120px] rounded-full border border-cyan-500/10 pointer-events-none" />

            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              <defs>
                <linearGradient id="trajGradientJsx" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#f43f5e" stopOpacity="0.8" />
                </linearGradient>
              </defs>
              <path
                d="M 280 90 Q 380 180 440 260"
                fill="none"
                stroke="url(#trajGradientJsx)"
                strokeWidth="2.5"
                strokeDasharray="6 4"
                className="animate-pulse"
              />
              <line
                x1="280"
                y1="90"
                x2="315"
                y2="75"
                stroke="#f59e0b"
                strokeWidth="1.5"
                strokeDasharray="3 3"
              />
            </svg>

            <div className="absolute top-[170px] left-[340px] -translate-x-1/2 -translate-y-1/2 bg-slate-900/90 text-rose-300 border border-rose-800/70 rounded-full px-2.5 py-0.5 text-[10px] font-mono font-semibold shadow-lg backdrop-blur pointer-events-none flex items-center gap-1">
              <Activity className="w-3 h-3 text-rose-400 animate-spin" />
              <span>&Delta; 1,742.4 km (Impossible Speed)</span>
            </div>

            {/* PIN 1 */}
            <div
              onClick={() => setSelectedPointId('geo-claimed-01')}
              className="absolute top-[80px] left-[270px] cursor-pointer group z-10"
              title="Click to view Claimed Alibi details"
            >
              <div className="relative flex items-center justify-center">
                <span className="absolute w-8 h-8 rounded-full bg-cyan-500/20 animate-ping pointer-events-none" />
                <div className="w-6 h-6 rounded-full bg-cyan-950 border-2 border-cyan-400 flex items-center justify-center text-cyan-300 shadow-lg shadow-cyan-500/30 group-hover:scale-110 transition">
                  <MessageSquare className="w-3 h-3" />
                </div>
              </div>
              <div className="mt-1 -ml-12 px-2 py-0.5 rounded bg-slate-900/90 border border-slate-700 text-[10px] font-mono text-cyan-300 whitespace-nowrap shadow">
                Claimed Alibi: Gurugram
              </div>
            </div>

            {/* PIN 2 */}
            <div
              onClick={() => setSelectedPointId('geo-ip-02')}
              className="absolute top-[250px] left-[430px] cursor-pointer group z-10"
              title="Click to view IP Egress details"
            >
              <div className="relative flex items-center justify-center">
                <span className="absolute w-8 h-8 rounded-full bg-rose-500/20 animate-ping pointer-events-none" />
                <div className="w-6 h-6 rounded-full bg-rose-950 border-2 border-rose-400 flex items-center justify-center text-rose-300 shadow-lg shadow-rose-500/30 group-hover:scale-110 transition">
                  <Server className="w-3 h-3" />
                </div>
              </div>
              <div className="mt-1 -ml-16 px-2 py-0.5 rounded bg-slate-900/90 border border-rose-900 text-[10px] font-mono text-rose-300 whitespace-nowrap shadow">
                IP Egress: Bengaluru (WAN)
              </div>
            </div>

            {/* PIN 3 */}
            <div
              onClick={() => setSelectedPointId('geo-cdr-03')}
              className="absolute top-[65px] left-[305px] cursor-pointer group z-10"
              title="Click to view Cell Tower details"
            >
              <div className="relative flex items-center justify-center">
                <span className="absolute w-6 h-6 rounded-full bg-amber-500/20 animate-ping pointer-events-none" />
                <div className="w-5 h-5 rounded-full bg-amber-950 border-2 border-amber-400 flex items-center justify-center text-amber-300 shadow-lg shadow-amber-500/30 group-hover:scale-110 transition">
                  <Radio className="w-2.5 h-2.5" />
                </div>
              </div>
              <div className="mt-1 -ml-10 px-1.5 py-0.2 rounded bg-slate-900/90 border border-amber-800 text-[9px] font-mono text-amber-300 whitespace-nowrap shadow">
                Tower: DEL-CYB-0982
              </div>
            </div>

            {/* Legend */}
            <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-slate-800 rounded-xl p-2.5 text-[10px] font-mono space-y-1.5 shadow-lg backdrop-blur">
              <div className="text-slate-400 uppercase font-bold text-[9px] tracking-wider mb-1">
                Forensic Geo Legend:
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
                <span className="text-slate-300">Claimed Alibi Statement</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-400" />
                <span className="text-slate-300">Server Authentication / WAN IP</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                <span className="text-slate-300">Telecom CDR Cell Tower</span>
              </div>
            </div>

            <div className="absolute top-3 right-3 text-[10px] font-mono text-slate-500 bg-slate-900/80 px-2.5 py-1 rounded-lg border border-slate-800">
              India Subcontinent Projection &bull; 0 EXTERNAL EGRESS
            </div>
          </div>

          {/* Cards List */}
          <div className="space-y-3">
            <h3 className="text-xs uppercase font-bold tracking-wider font-mono text-slate-400 flex items-center justify-between">
              <span>Geo-Spatial Evidence Dossier ({visiblePoints.length} Points)</span>
              <span className="text-[11px] text-cyan-400 font-normal">Click any point to inspect metadata</span>
            </h3>

            <div className="grid grid-cols-1 gap-3">
              {visiblePoints.map((point) => {
                const isSelected = point.id === activePoint.id;
                const isAlibi = point.type === 'claimed_alibi';
                const isIp = point.type === 'ip_egress';

                return (
                  <div
                    key={point.id}
                    onClick={() => setSelectedPointId(point.id)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer select-text ${
                      isSelected
                        ? isAlibi
                          ? 'bg-cyan-950/30 border-cyan-500/80 ring-1 ring-cyan-500/30 shadow-md'
                          : isIp
                          ? 'bg-rose-950/30 border-rose-500/80 ring-1 ring-rose-500/30 shadow-md'
                          : 'bg-amber-950/30 border-amber-500/80 ring-1 ring-amber-500/30 shadow-md'
                        : 'bg-slate-950/70 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3">
                        <div
                          className={`p-2 rounded-lg mt-0.5 ${
                            isAlibi
                              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                              : isIp
                              ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                              : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          }`}
                        >
                          {isAlibi ? (
                            <MessageSquare className="w-4 h-4" />
                          ) : isIp ? (
                            <Server className="w-4 h-4" />
                          ) : (
                            <Radio className="w-4 h-4" />
                          )}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="text-xs font-bold text-white tracking-tight">{point.label}</h4>
                            <span
                              className={`text-[10px] font-mono px-2 py-0.2 rounded-full border ${
                                isAlibi
                                  ? 'bg-cyan-950 text-cyan-300 border-cyan-800'
                                  : isIp
                                  ? 'bg-rose-950 text-rose-300 border-rose-800'
                                  : 'bg-amber-950 text-amber-300 border-amber-800'
                              }`}
                            >
                              {isAlibi ? 'Self-Claimed Alibi' : isIp ? 'Public IP Egress' : 'Cell Tower CDR'}
                            </span>
                          </div>
                          <p className="text-xs text-slate-300 mt-1">{point.sublabel}</p>
                          <div className="text-[11px] font-mono text-slate-400 flex flex-wrap items-center gap-3 mt-2">
                            <span className="text-cyan-300">
                              GPS: {point.latitude.toFixed(4)}° N, {point.longitude.toFixed(4)}° E
                            </span>
                            <span>&bull;</span>
                            <span>Recorded: {point.timestamp}</span>
                            <span>&bull;</span>
                            <span className="text-slate-400">Exhibit: {point.sourceExhibitId}</span>
                          </div>
                        </div>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCopy(
                            `[Geo Evidence]\nType: ${point.label}\nCoords: ${point.latitude}, ${point.longitude}\nTimestamp: ${point.timestamp}\nExhibit: ${point.sourceExhibitId}`,
                            point.id
                          );
                        }}
                        className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-700 transition"
                        title="Copy GPS coordinates & metadata"
                      >
                        {copiedText === point.id ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>

                    {(point.metadata.ipAddress || point.metadata.towerId) && (
                      <div className="mt-3 pt-2.5 border-t border-slate-800/80 grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px] font-mono">
                        {point.metadata.ipAddress && (
                          <div className="p-2 rounded bg-slate-900/60 border border-slate-850">
                            <span className="text-slate-500 block text-[10px] uppercase font-bold">WAN / Local IP</span>
                            <span className="text-slate-200">{point.metadata.ipAddress}</span>
                          </div>
                        )}
                        {point.metadata.ispName && (
                          <div className="p-2 rounded bg-slate-900/60 border border-slate-850">
                            <span className="text-slate-500 block text-[10px] uppercase font-bold">ISP / ASN</span>
                            <span className="text-slate-200">{point.metadata.ispName}</span>
                          </div>
                        )}
                        {point.metadata.cgi && (
                          <div className="p-2 rounded bg-slate-900/60 border border-slate-850">
                            <span className="text-slate-500 block text-[10px] uppercase font-bold">Cell CGI & Azimuth</span>
                            <span className="text-slate-200">{point.metadata.cgi} ({point.metadata.azimuth}°)</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950 flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs font-mono text-slate-400">
            <span>BSA 2023 Section 63(4) Forensic Map Dossier</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() =>
                handleCopy(
                  JSON.stringify(
                    {
                      case: caseRef,
                      triangulationAnalysis: distanceAnalysis,
                      geodesicPoints: points
                    },
                    null,
                    2
                  ),
                  'geojson'
                )
              }
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium font-mono text-slate-300 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition"
            >
              {copiedText === 'geojson' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>Copy GeoJSON Manifest</span>
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
}

export default GeoLocationDrawer;
