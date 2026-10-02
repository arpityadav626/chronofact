import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Search,
  X,
  Filter,
  RotateCcw,
  MessageSquare,
  Server,
  Mail,
  ShieldCheck,
  ClockAlert,
  User,
  Users,
  Check,
  SearchX,
  Calendar,
  Sparkles,
  SlidersHorizontal,
  ChevronDown
} from 'lucide-react';

export const TimelineSearchFilterToolbar = ({
  events = [],
  onFilteredEventsChange,
  activeExhibitFilter = null,
  onClearExhibitFilter,
  className = ''
}) => {
  // 1. Search Query with Debounce
  const [searchInput, setSearchInput] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  // 2. Multi-Select Filters
  const [selectedEventTypes, setSelectedEventTypes] = useState([]);
  const [selectedIntegrity, setSelectedIntegrity] = useState([]);
  const [selectedActors, setSelectedActors] = useState([]);

  // Debounce effect (200ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(searchInput.trim().toLowerCase());
    }, 200);

    return () => clearTimeout(handler);
  }, [searchInput]);

  // Extract distinct actors from events
  const availableActors = useMemo(() => {
    const actorCounts = {};
    events.forEach((ev) => {
      if (!ev.actor) return;
      const cleanActor = ev.actor.trim();
      actorCounts[cleanActor] = (actorCounts[cleanActor] || 0) + 1;
    });

    return Object.entries(actorCounts).map(([name, count]) => ({
      name,
      count,
      isSuspect: name.toLowerCase().includes('vikram') || name.toLowerCase().includes('malhotra')
    })).sort((a, b) => (b.isSuspect ? 1 : 0) - (a.isSuspect ? 1 : 0) || b.count - a.count);
  }, [events]);

  // Compute category mapping helper
  const getEventCategory = useCallback((factType) => {
    const ft = (factType || '').toUpperCase();
    if (ft.includes('CHAT') || ft === 'WHATSAPP') return 'CHAT';
    if (ft.includes('SERVER') || ft.includes('LOG') || ft.includes('AUTH') || ft.includes('FILE_TRANSFER')) return 'SERVER';
    if (ft.includes('EMAIL') || ft.includes('EML') || ft.includes('MAIL')) return 'EMAIL';
    return 'OTHER';
  }, []);

  // Compute stats for pills dynamically based on all events
  const pillCounts = useMemo(() => {
    let chatCount = 0;
    let serverCount = 0;
    let emailCount = 0;
    let confirmedCount = 0;
    let uncertainCount = 0;

    events.forEach((ev) => {
      const cat = getEventCategory(ev.fact_type);
      if (cat === 'CHAT') chatCount++;
      if (cat === 'SERVER') serverCount++;
      if (cat === 'EMAIL') emailCount++;

      if (ev.is_interval) {
        uncertainCount++;
      } else {
        confirmedCount++;
      }
    });

    return {
      chat: chatCount,
      server: serverCount,
      email: emailCount,
      confirmed: confirmedCount,
      uncertain: uncertainCount
    };
  }, [events, getEventCategory]);

  // Filter Logic Execution
  const filteredEvents = useMemo(() => {
    return events.filter((ev) => {
      // 1. Parent Exhibit Filter Check
      if (activeExhibitFilter && ev.evidence_id !== activeExhibitFilter) {
        return false;
      }

      // 2. Event Type Multi-Select Filter
      if (selectedEventTypes.length > 0) {
        const cat = getEventCategory(ev.fact_type);
        if (!selectedEventTypes.includes(cat)) {
          return false;
        }
      }

      // 3. Integrity Status Multi-Select Filter
      if (selectedIntegrity.length > 0) {
        const isExact = !ev.is_interval;
        const matchesConfirmed = selectedIntegrity.includes('CONFIRMED') && isExact;
        const matchesUncertain = selectedIntegrity.includes('UNCERTAIN') && !isExact;
        if (!matchesConfirmed && !matchesUncertain) {
          return false;
        }
      }

      // 4. Actor Multi-Select Filter
      if (selectedActors.length > 0) {
        const actor = (ev.actor || '').toLowerCase();
        const matchesActor = selectedActors.some((a) => {
          const aLower = a.toLowerCase();
          return actor.includes(aLower) || aLower.includes(actor);
        });
        if (!matchesActor) {
          return false;
        }
      }

      // 5. Full-Text Search Query (Title, Content, Metadata, Actor, Locator, Evidence ID)
      if (debouncedQuery) {
        const title = (ev.summary_title || '').toLowerCase();
        const raw = (ev.raw_content || '').toLowerCase();
        const actor = (ev.actor || '').toLowerCase();
        const locator = (ev.locator || '').toLowerCase();
        const evId = (ev.evidence_id || '').toLowerCase();
        const factType = (ev.fact_type || '').toLowerCase();
        const uncert = (ev.uncertainty_label || '').toLowerCase();

        const matchesQuery =
          title.includes(debouncedQuery) ||
          raw.includes(debouncedQuery) ||
          actor.includes(debouncedQuery) ||
          locator.includes(debouncedQuery) ||
          evId.includes(debouncedQuery) ||
          factType.includes(debouncedQuery) ||
          uncert.includes(debouncedQuery);

        if (!matchesQuery) {
          return false;
        }
      }

      return true;
    });
  }, [
    events,
    activeExhibitFilter,
    selectedEventTypes,
    selectedIntegrity,
    selectedActors,
    debouncedQuery,
    getEventCategory
  ]);

  // Compute active filters stats
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (searchInput.trim().length > 0) count++;
    if (selectedEventTypes.length > 0) count += selectedEventTypes.length;
    if (selectedIntegrity.length > 0) count += selectedIntegrity.length;
    if (selectedActors.length > 0) count += selectedActors.length;
    if (activeExhibitFilter) count++;
    return count;
  }, [searchInput, selectedEventTypes, selectedIntegrity, selectedActors, activeExhibitFilter]);

  const hasActiveFilters = activeFilterCount > 0;

  // Inform parent callback
  useEffect(() => {
    if (onFilteredEventsChange) {
      onFilteredEventsChange(filteredEvents, {
        total: events.length,
        filtered: filteredEvents.length,
        hasActiveFilters,
        activeFilterCount
      });
    }
  }, [filteredEvents, events.length, hasActiveFilters, activeFilterCount, onFilteredEventsChange]);

  // Handlers
  const handleToggleEventType = (cat) => {
    setSelectedEventTypes((prev) =>
      prev.includes(cat) ? prev.filter((item) => item !== cat) : [...prev, cat]
    );
  };

  const handleToggleIntegrity = (integ) => {
    setSelectedIntegrity((prev) =>
      prev.includes(integ) ? prev.filter((item) => item !== integ) : [...prev, integ]
    );
  };

  const handleToggleActor = (actorName) => {
    setSelectedActors((prev) =>
      prev.includes(actorName)
        ? prev.filter((item) => item !== actorName)
        : [...prev, actorName]
    );
  };

  const handleClearAllFilters = () => {
    setSearchInput('');
    setDebouncedQuery('');
    setSelectedEventTypes([]);
    setSelectedIntegrity([]);
    setSelectedActors([]);
    if (onClearExhibitFilter) {
      onClearExhibitFilter();
    }
  };

  return (
    <div className={`space-y-3.5 ${className}`}>
      {/* 1. Main Search & Results Status Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        {/* Full-Text Search Input Box */}
        <div className="relative flex-1 group">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-cyan-400 transition-colors">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search timeline events, titles, raw text, IP addresses, or metadata..."
            className="w-full pl-10 pr-9 py-2.5 bg-brand-950/80 hover:bg-brand-950 border border-slate-800 focus:border-cyan-500/80 rounded-xl text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/50 shadow-inner transition font-sans"
          />
          {searchInput && (
            <button
              onClick={() => setSearchInput('')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 transition"
              title="Clear search query"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Counter Badge & Reset Controls */}
        <div className="flex items-center justify-between sm:justify-end gap-2 shrink-0">
          <div className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-xs font-mono">
            <span className="text-slate-400">Events:</span>
            <span
              className={`font-semibold ${
                filteredEvents.length === 0
                  ? 'text-rose-400'
                  : filteredEvents.length < events.length
                  ? 'text-cyan-400'
                  : 'text-emerald-400'
              }`}
            >
              {filteredEvents.length}
            </span>
            <span className="text-slate-600">/</span>
            <span className="text-slate-400">{events.length}</span>
          </div>

          {hasActiveFilters && (
            <button
              onClick={handleClearAllFilters}
              className="inline-flex items-center gap-1 px-3 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-rose-300 border border-rose-900/40 text-xs font-medium transition cursor-pointer shadow-sm"
              title="Reset all search queries and active filter pills"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset All ({activeFilterCount})</span>
            </button>
          )}
        </div>
      </div>

      {/* 2. Multi-Select Pills Filter Toolbar */}
      <div className="p-3 rounded-xl bg-brand-950/60 border border-slate-800/70 backdrop-blur-sm space-y-2.5 text-xs">
        {/* Row A: Event Types & Integrity Status */}
        <div className="flex flex-wrap items-center gap-y-2 gap-x-4">
          {/* Group 1: Event Type Filter */}
          <div className="flex items-center flex-wrap gap-1.5">
            <span className="text-[11px] font-mono font-medium text-slate-400 flex items-center gap-1 mr-1">
              <SlidersHorizontal className="w-3 h-3 text-slate-500" />
              <span>Event Type:</span>
            </span>

            {/* Chat Messages Pill */}
            <button
              onClick={() => handleToggleEventType('CHAT')}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition cursor-pointer border ${
                selectedEventTypes.includes('CHAT')
                  ? 'bg-cyan-950/90 text-cyan-300 border-cyan-500/80 ring-1 ring-cyan-500/40 shadow-sm shadow-cyan-950'
                  : 'bg-slate-900/60 hover:bg-slate-800/70 text-slate-400 hover:text-slate-200 border-slate-800'
              }`}
            >
              <MessageSquare className="w-3 h-3 text-cyan-400" />
              <span>Chat Messages</span>
              <span
                className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                  selectedEventTypes.includes('CHAT')
                    ? 'bg-cyan-900/80 text-cyan-200'
                    : 'bg-slate-800 text-slate-400'
                }`}
              >
                {pillCounts.chat}
              </span>
            </button>

            {/* Server Logs Pill */}
            <button
              onClick={() => handleToggleEventType('SERVER')}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition cursor-pointer border ${
                selectedEventTypes.includes('SERVER')
                  ? 'bg-amber-950/90 text-amber-300 border-amber-500/80 ring-1 ring-amber-500/40 shadow-sm shadow-amber-950'
                  : 'bg-slate-900/60 hover:bg-slate-800/70 text-slate-400 hover:text-slate-200 border-slate-800'
              }`}
            >
              <Server className="w-3 h-3 text-amber-400" />
              <span>Server Logs</span>
              <span
                className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                  selectedEventTypes.includes('SERVER')
                    ? 'bg-amber-900/80 text-amber-200'
                    : 'bg-slate-800 text-slate-400'
                }`}
              >
                {pillCounts.server}
              </span>
            </button>

            {/* Email Messages Pill */}
            <button
              onClick={() => handleToggleEventType('EMAIL')}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition cursor-pointer border ${
                selectedEventTypes.includes('EMAIL')
                  ? 'bg-indigo-950/90 text-indigo-300 border-indigo-500/80 ring-1 ring-indigo-500/40 shadow-sm shadow-indigo-950'
                  : 'bg-slate-900/60 hover:bg-slate-800/70 text-slate-400 hover:text-slate-200 border-slate-800'
              }`}
            >
              <Mail className="w-3 h-3 text-indigo-400" />
              <span>Email Messages</span>
              <span
                className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                  selectedEventTypes.includes('EMAIL')
                    ? 'bg-indigo-900/80 text-indigo-200'
                    : 'bg-slate-800 text-slate-400'
                }`}
              >
                {pillCounts.email}
              </span>
            </button>
          </div>

          <div className="hidden md:block w-px h-5 bg-slate-800" />

          {/* Group 2: Integrity Status Filter */}
          <div className="flex items-center flex-wrap gap-1.5">
            <span className="text-[11px] font-mono font-medium text-slate-400 flex items-center gap-1 mr-1">
              <ShieldCheck className="w-3 h-3 text-slate-500" />
              <span>Integrity:</span>
            </span>

            {/* Confirmed / Zero Skew */}
            <button
              onClick={() => handleToggleIntegrity('CONFIRMED')}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition cursor-pointer border ${
                selectedIntegrity.includes('CONFIRMED')
                  ? 'bg-emerald-950/90 text-emerald-300 border-emerald-500/80 ring-1 ring-emerald-500/40 shadow-sm shadow-emerald-950'
                  : 'bg-slate-900/60 hover:bg-slate-800/70 text-slate-400 hover:text-slate-200 border-slate-800'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block shadow-sm"></span>
              <span>Confirmed / Zero Skew</span>
              <span
                className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                  selectedIntegrity.includes('CONFIRMED')
                    ? 'bg-emerald-900/80 text-emerald-200'
                    : 'bg-slate-800 text-slate-400'
                }`}
              >
                {pillCounts.confirmed}
              </span>
            </button>

            {/* Uncertain / Ambiguous */}
            <button
              onClick={() => handleToggleIntegrity('UNCERTAIN')}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition cursor-pointer border ${
                selectedIntegrity.includes('UNCERTAIN')
                  ? 'bg-amber-950/90 text-amber-300 border-amber-500/80 ring-1 ring-amber-500/40 shadow-sm shadow-amber-950'
                  : 'bg-slate-900/60 hover:bg-slate-800/70 text-slate-400 hover:text-slate-200 border-slate-800'
              }`}
            >
              <ClockAlert className="w-3 h-3 text-amber-400" />
              <span>Uncertain / Ambiguous</span>
              <span
                className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                  selectedIntegrity.includes('UNCERTAIN')
                    ? 'bg-amber-900/80 text-amber-200'
                    : 'bg-slate-800 text-slate-400'
                }`}
              >
                {pillCounts.uncertain}
              </span>
            </button>
          </div>
        </div>

        {/* Row B: Actor / Suspect Multi-Select Pills */}
        <div className="pt-2 border-t border-slate-800/60 flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] font-mono font-medium text-slate-400 flex items-center gap-1 mr-1">
            <User className="w-3 h-3 text-slate-500" />
            <span>Actor / Suspect:</span>
          </span>

          {availableActors.map((actorObj) => {
            const isSelected = selectedActors.includes(actorObj.name);
            return (
              <button
                key={actorObj.name}
                onClick={() => handleToggleActor(actorObj.name)}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition cursor-pointer border ${
                  isSelected
                    ? 'bg-blue-950/90 text-blue-300 border-blue-500/80 ring-1 ring-blue-500/40 shadow-sm shadow-blue-950'
                    : actorObj.isSuspect
                    ? 'bg-rose-950/30 hover:bg-rose-900/40 text-rose-300/90 border-rose-900/40'
                    : 'bg-slate-900/60 hover:bg-slate-800/70 text-slate-400 hover:text-slate-200 border-slate-800'
                }`}
                title={`Filter events involving ${actorObj.name}`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    isSelected
                      ? 'bg-blue-400'
                      : actorObj.isSuspect
                      ? 'bg-rose-400'
                      : 'bg-slate-500'
                  }`}
                />
                <span className="font-mono">{actorObj.name}</span>
                {actorObj.isSuspect && (
                  <span className="text-[9px] uppercase px-1 py-0.2 rounded bg-rose-950 text-rose-400 border border-rose-800/60 font-mono">
                    Suspect
                  </span>
                )}
                <span
                  className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                    isSelected
                      ? 'bg-blue-900/80 text-blue-200'
                      : 'bg-slate-800/80 text-slate-400'
                  }`}
                >
                  {actorObj.count}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// Informative Empty State Component for 0 Matched Events
export const TimelineEmptyState = ({
  onClearFilters,
  searchQuery = '',
  hasFilters = true
}) => {
  return (
    <div className="py-14 px-6 text-center rounded-2xl bg-brand-950/60 border border-dashed border-slate-800 my-4 space-y-4 shadow-inner animate-in fade-in duration-200">
      <div className="w-14 h-14 rounded-2xl bg-slate-900/90 border border-slate-800 text-slate-400 mx-auto flex items-center justify-center shadow-lg">
        <SearchX className="w-7 h-7 text-rose-400/90" />
      </div>

      <div className="space-y-1.5">
        <h3 className="text-sm font-semibold text-slate-200 tracking-wide">
          No events matched your search query
        </h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
          {searchQuery
            ? `No chronological facts match "${searchQuery}" with the current filter settings.`
            : 'No events match the selected criteria across event types, integrity states, or actors.'}{' '}
          Try broadening your search terms or clearing active filters to see all evidence facts.
        </p>
      </div>

      {hasFilters && (
        <div className="pt-2 flex items-center justify-center gap-3">
          <button
            onClick={onClearFilters}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 shadow-md shadow-blue-900/30 transition cursor-pointer hover:shadow-lg"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Clear all filters</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default TimelineSearchFilterToolbar;
