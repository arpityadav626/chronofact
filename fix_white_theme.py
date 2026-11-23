import re
import os
import shutil
from pathlib import Path

REPO_DIR = Path(r"C:\Users\Arpit Yadav\.gemini\antigravity\scratch\chronofact")

def fix_styles_css():
    file_path = REPO_DIR / "styles.css"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Fix .common-wrapper (Make it light slate #F8FAFC, border #E2E8F0, text #334155)
    old_common = """.common-wrapper {
  background: #0F172A !important;
  color: #F8FAFC !important;
  border-bottom: 1px solid #1E293B !important;
}"""
    new_common = """.common-wrapper {
  background: #F8FAFC !important;
  color: #334155 !important;
  border-bottom: 1px solid #E2E8F0 !important;
}"""
    content = content.replace(old_common, new_common)

    # 2. Fix .megamenu-wraper (Make it pure white #FFFFFF, border #E2E8F0)
    old_megamenu = """.megamenu-wraper {
  background: #0B0F19 !important;
  border-top: 1px solid #1E293B;
  border-bottom: 1px solid #1E293B;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}"""
    new_megamenu = """.megamenu-wraper {
  background: #FFFFFF !important;
  border-top: 1px solid #E2E8F0 !important;
  border-bottom: 1px solid #E2E8F0 !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}"""
    content = content.replace(old_megamenu, new_megamenu)

    # 3. Fix .portal-nav-btn for light background
    old_portal_btn = """.portal-nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #FFFFFF !important;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  transition: all 0.15s ease;
  cursor: pointer;
  white-space: nowrap;
}

.portal-nav-btn:hover {
  background-color: rgba(255, 255, 255, 0.12);
  border-bottom-color: #FBBF24;
  color: #FFFFFF !important;
}

.portal-nav-btn.active {
  background-color: #002654 !important;
  border-bottom-color: #FBBF24 !important;
  color: #FFFFFF !important;
}"""
    new_portal_btn = """.portal-nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #475569 !important;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  transition: all 0.15s ease;
  cursor: pointer;
  white-space: nowrap;
}

.portal-nav-btn:hover {
  background-color: #F8FAFC !important;
  color: #0F172A !important;
  border-bottom-color: #94A3B8 !important;
}

.portal-nav-btn.active {
  background-color: #F1F5F9 !important;
  border-bottom-color: #0F172A !important;
  color: #0F172A !important;
}"""
    content = content.replace(old_portal_btn, new_portal_btn)

    # 4. Remove .megamenu-wraper, .megamenu-wraper * { color: #FFFFFF; }
    old_megamenu_colors = """.megamenu-wraper,
.megamenu-wraper * {
  color: #FFFFFF;
}

.megamenu-wraper .officer-label {
  color: #FFFFFF !important;
  font-weight: 600;
}"""
    new_megamenu_colors = """.megamenu-wraper .officer-label {
  color: #0F172A !important;
  font-weight: 700;
}"""
    content = content.replace(old_megamenu_colors, new_megamenu_colors)

    # 5. Fix .header-case-badge for light theme
    old_case_badge = """.header-case-badge {
  background: rgba(0, 0, 0, 0.3) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  color: #FFFFFF !important;
  cursor: pointer;
  transition: all 0.15s ease;
}

.header-case-badge:hover {
  background: rgba(0, 0, 0, 0.45) !important;
  border-color: var(--border-hairline) !important;
  transform: translateY(-1px);
}"""
    new_case_badge = """.header-case-badge {
  background: #F1F5F9 !important;
  border: 1px solid #CBD5E1 !important;
  color: #0F172A !important;
  cursor: pointer;
  transition: all 0.15s ease;
}

.header-case-badge:hover {
  background: #E2E8F0 !important;
  border-color: #94A3B8 !important;
  transform: translateY(-1px);
}"""
    content = content.replace(old_case_badge, new_case_badge)

    # 6. Fix .text-size-btn so text is bold, dark and 100% visible
    old_text_btn = """/* Accessibility Text-Size Controls */
.text-size-btn {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.125rem 0.45rem;
  border-radius: 4px;
  border: 1px solid var(--border-hairline);
  background-color: #FFFFFF;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.text-size-btn:hover, .text-size-btn.active {
  background-color: var(--primary);
  color: #FFFFFF;
  border-color: var(--primary);
}"""
    new_text_btn = """/* Accessibility Text-Size Controls (High-Contrast Courtroom Standard) */
.text-size-btn {
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.15rem 0.55rem;
  border-radius: 4px;
  border: 1px solid #94A3B8;
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  cursor: pointer;
  transition: all 0.15s ease;
  line-height: 1.2;
}

.text-size-btn:hover {
  background-color: #E2E8F0 !important;
  border-color: #475569 !important;
  color: #0F172A !important;
}

.text-size-btn.active {
  background-color: #0F172A !important;
  color: #FFFFFF !important;
  border-color: #0F172A !important;
}"""
    content = content.replace(old_text_btn, new_text_btn)

    # 7. Remove .common-wrapper .text-size-btn dark overrides
    content = re.sub(r'\.common-wrapper \.text-size-btn:hover,\s*\.common-wrapper \.text-size-btn\.active\s*\{[^}]*\}', '', content)

    # 8. Fix footer wrappers to be light
    content = content.replace('background: #1E293B;\n  color: #94A3B8;', 'background: #F8FAFC;\n  color: #64748B;')
    content = content.replace('background: #0F172A;\n  color: #CBD5E1;', 'background: #FFFFFF;\n  color: #64748B;')

    # 9. Override officer menu button
    content = content.replace('color: #FFFFFF !important;\n  cursor: pointer;\n  transition: all 0.15s ease;\n}', 'color: #0F172A !important;\n  cursor: pointer;\n  transition: all 0.15s ease;\n}')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed styles.css")

def fix_index_html():
    file_path = REPO_DIR / "index.html"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Fix Academic Utility Strip (common-wrapper) to use dark text on light background
    old_util_strip = '''  <!-- 2. Academic Utility Strip -->
  <div class="common-wrapper px-4 sm:px-6 py-1.5 text-xs select-none no-print">
    <div class="max-w-[1920px] mx-auto flex items-center justify-between flex-wrap gap-2">
      <div class="flex items-center gap-2 sm:gap-3 text-white/95">
        <div class="flex items-center gap-1.5 font-bold">
          <span class="text-xs">SUTRAM 2026</span>
          <span class="text-white/40">|</span>
          <span class="text-xs">National Cyber Security Hackathon</span>
        </div>
        <span class="hidden sm:inline text-white/40">|</span>
        <span class="hidden sm:inline font-medium text-white/85 text-[11px]">Digital Forensic &amp; Electronic Evidence Research Project</span>
      </div>
      
      <div class="flex items-center gap-2 sm:gap-3">
        <!-- Accessibility Text Controls (A- A A+ A++) -->
        <div class="flex items-center gap-1 bg-white/10 px-2 py-0.5 rounded border border-white/20 shadow-xs">
          <span class="text-[10px] text-white/70 font-bold uppercase pr-0.5">Text:</span>
          <button onclick="setTextScale(0)" id="ts-btn-0" class="text-size-btn" title="Small (85%)">A−</button>
          <button onclick="setTextScale(1)" id="ts-btn-1" class="text-size-btn active" title="Normal (100%)">A</button>
          <button onclick="setTextScale(2)" id="ts-btn-2" class="text-size-btn" title="Large (115%)">A+</button>
          <button onclick="setTextScale(3)" id="ts-btn-3" class="text-size-btn" title="Extra Large (130%)">A++</button>
        </div>
        
        <!-- Local Evaluation Mode Badge -->
        <div class="hidden md:flex items-center gap-1.5 text-[11px] font-mono font-medium text-white bg-white/15 px-2.5 py-0.5 rounded border border-white/25">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Evaluation Node #FE-802 • Offline Safe Mode</span>
        </div>
      </div>
    </div>
  </div>'''

    new_util_strip = '''  <!-- 2. Academic Utility Strip (Clean Light Courtroom Palette) -->
  <div class="common-wrapper px-4 sm:px-6 py-1.5 text-xs select-none no-print border-b border-slate-200 bg-slate-50">
    <div class="max-w-[1920px] mx-auto flex items-center justify-between flex-wrap gap-2 text-slate-700">
      <div class="flex items-center gap-2 sm:gap-3 text-slate-700">
        <div class="flex items-center gap-1.5 font-bold">
          <span class="text-xs text-slate-900 font-extrabold">SUTRAM 2026</span>
          <span class="text-slate-400">|</span>
          <span class="text-xs text-slate-800 font-semibold">National Cyber Security Hackathon</span>
        </div>
        <span class="hidden sm:inline text-slate-400">|</span>
        <span class="hidden sm:inline font-medium text-slate-600 text-[11px]">Digital Forensic &amp; Electronic Evidence Research Project</span>
      </div>
      
      <div class="flex items-center gap-2 sm:gap-3">
        <!-- Accessibility Text Controls (A- A A+ A++) with High-Contrast Dark Text -->
        <div class="flex items-center gap-1.5 bg-white px-2 py-1 rounded border border-slate-300 shadow-xs">
          <span class="text-[10px] text-slate-700 font-extrabold uppercase pr-0.5">Text:</span>
          <button onclick="setTextScale(0)" id="ts-btn-0" class="text-size-btn" title="Small (85%)">A−</button>
          <button onclick="setTextScale(1)" id="ts-btn-1" class="text-size-btn active" title="Normal (100%)">A</button>
          <button onclick="setTextScale(2)" id="ts-btn-2" class="text-size-btn" title="Large (115%)">A+</button>
          <button onclick="setTextScale(3)" id="ts-btn-3" class="text-size-btn" title="Extra Large (130%)">A++</button>
        </div>
        
        <!-- Local Evaluation Mode Badge -->
        <div class="hidden md:flex items-center gap-1.5 text-[11px] font-mono font-medium text-slate-700 bg-white px-2.5 py-1 rounded border border-slate-300">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
          <span>Evaluation Node #FE-802 • Offline Safe Mode</span>
        </div>
      </div>
    </div>
  </div>'''
    content = content.replace(old_util_strip, new_util_strip)

    # 2. Fix Right side of Megamenu:
    # A) Replace vault pill with clean light badge
    old_vault_pill = '''        <!-- Vault Sealed Pill -->
        <div id="header-vault-status-pill" class="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-black/35 text-white text-xs border border-white/20 whitespace-nowrap shadow-xs" title="Cryptographic Vault Sealed">
          <span class="w-2 h-2 rounded-full bg-emerald-400 shrink-0"></span>
          <span class="font-mono font-bold text-xs text-white" id="header-exhibit-stat">3</span>
          <span class="text-[11px] font-semibold text-emerald-300">Vault Sealed</span>
        </div>'''
    new_vault_pill = '''        <!-- Vault Sealed Pill -->
        <div id="header-vault-status-pill" class="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-900 text-xs border border-emerald-300 whitespace-nowrap shadow-xs" title="Cryptographic Vault Sealed">
          <span class="w-2 h-2 rounded-full bg-emerald-600 shrink-0"></span>
          <span class="font-mono font-bold text-xs text-emerald-950" id="header-exhibit-stat">3</span>
          <span class="text-[11px] font-bold text-emerald-800">Vault Sealed</span>
        </div>'''
    content = content.replace(old_vault_pill, new_vault_pill)

    # B) Replace Case Selector Pill with light version
    old_case_pill = '''        <!-- Active Case Pill (Clickable Case Switcher) -->
        <button 
          onclick="openCaseSelectorModal()"
          class="header-case-badge hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs whitespace-nowrap shadow-xs cursor-pointer"
          title="Click to Switch / Load Case Samples"
        >
          <i data-lucide="folder-search" class="w-3.5 h-3.5 text-amber-300 shrink-0"></i>
          <span id="header-active-case-name" class="font-bold text-white">State v. Vikram Malhotra</span>
          <span class="text-white/40">|</span>
          <span id="header-active-case-fir" class="font-mono text-emerald-300 font-semibold text-[11px]">FIR 204/2026</span>
          <i data-lucide="chevron-down" class="w-3 h-3 text-white/70 shrink-0"></i>
        </button>'''
    new_case_pill = '''        <!-- Active Case Pill (Clickable Case Switcher) -->
        <button 
          onclick="openCaseSelectorModal()"
          class="header-case-badge hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs whitespace-nowrap shadow-xs cursor-pointer bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-800"
          title="Click to Switch / Load Case Samples"
        >
          <i data-lucide="folder-search" class="w-3.5 h-3.5 text-amber-600 shrink-0"></i>
          <span id="header-active-case-name" class="font-bold text-slate-900">State v. Vikram Malhotra</span>
          <span class="text-slate-400">|</span>
          <span id="header-active-case-fir" class="font-mono text-emerald-700 font-bold text-[11px]">FIR 204/2026</span>
          <i data-lucide="chevron-down" class="w-3 h-3 text-slate-500 shrink-0"></i>
        </button>'''
    content = content.replace(old_case_pill, new_case_pill)

    # C) Remove Audio / Haptic Toggle Completely per user request
    audio_toggle_pattern = r'<!-- Audio / Haptic Toggle -->\s*<button\s+onclick="hapticEngine\.toggle\(\); updateHeaderSoundIcon\(\);".*?</button>'
    content = re.sub(audio_toggle_pattern, '<!-- Sound Permanently Disabled per Courtroom Requirement -->', content, flags=re.DOTALL)

    # D) Replace Officer Profile Badge with light version
    old_officer_badge = '''        <!-- Officer Profile & Terminal Gate Button (Screenshot 1 & 2 Fix) -->
        <div class="relative">
          <div class="flex items-center gap-1 bg-black/30 pl-2 pr-1.5 py-1 rounded-full border border-white/25 text-white shadow-xs">
            <!-- Clicking avatar/label opens dropdown -->
            <button 
              id="officer-menu-btn"
              onclick="toggleOfficerDropdown(event)" 
              class="flex items-center gap-2 text-white hover:opacity-90 transition cursor-pointer bg-transparent border-0"
              title="Click to view Examiner Menu"
            >
              <div id="officer-badge-avatar" class="w-6 h-6 rounded-full bg-cyan-400 text-[#002654] flex items-center justify-center font-black text-[11px] shrink-0 shadow-xs">
                FE
              </div>
              <span id="officer-badge-label" class="font-bold text-xs text-white hidden md:inline officer-label">Examiner #FE-802</span>
              <i data-lucide="chevron-down" class="w-3.5 h-3.5 text-white/90 shrink-0"></i>
            </button>
            <!-- Direct Quick Edit Pencil button right on the navbar! -->
            <button 
              onclick="openEditOfficerNameDialog(event)" 
              class="px-2 py-0.5 rounded-full bg-white/15 hover:bg-white/25 text-amber-300 hover:text-white transition cursor-pointer flex items-center gap-1 border border-white/20" 
              title="Change Examiner Name Directly"
            >
              <i data-lucide="edit-3" class="w-3 h-3"></i>
              <span class="text-[10px] font-semibold text-amber-200 hidden sm:inline">Change</span>
            </button>
          </div>'''
    new_officer_badge = '''        <!-- Officer Profile & Terminal Gate Button (Light Courtroom Palette) -->
        <div class="relative">
          <div class="flex items-center gap-1 bg-slate-100 pl-2 pr-1.5 py-1 rounded-full border border-slate-300 text-slate-800 shadow-xs">
            <!-- Clicking avatar/label opens dropdown -->
            <button 
              id="officer-menu-btn"
              onclick="toggleOfficerDropdown(event)" 
              class="flex items-center gap-2 text-slate-800 hover:opacity-90 transition cursor-pointer bg-transparent border-0"
              title="Click to view Examiner Menu"
            >
              <div id="officer-badge-avatar" class="w-6 h-6 rounded-full bg-slate-900 text-white flex items-center justify-center font-black text-[11px] shrink-0 shadow-xs">
                FE
              </div>
              <span id="officer-badge-label" class="font-bold text-xs text-slate-900 hidden md:inline officer-label">Examiner #FE-802</span>
              <i data-lucide="chevron-down" class="w-3.5 h-3.5 text-slate-600 shrink-0"></i>
            </button>
            <!-- Direct Quick Edit Pencil button right on the navbar! -->
            <button 
              onclick="openEditOfficerNameDialog(event)" 
              class="px-2 py-0.5 rounded-full bg-slate-200 hover:bg-slate-300 text-slate-700 transition cursor-pointer flex items-center gap-1 border border-slate-300" 
              title="Change Examiner Name Directly"
            >
              <i data-lucide="edit-3" class="w-3 h-3 text-slate-700"></i>
              <span class="text-[10px] font-bold text-slate-700 hidden sm:inline">Change</span>
            </button>
          </div>'''
    content = content.replace(old_officer_badge, new_officer_badge)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed index.html")

def fix_app_js():
    file_path = REPO_DIR / "app.js"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Permanent silence for hapticEngine & sound
    old_haptic_def = '''// Audio / Sound FX Engine (Dual Web Audio API Synth Engine)
class HapticAudioEngine {
  constructor() {
    this.ctx = null;
    this.enabled = true;'''
    new_haptic_def = '''// Audio Engine (Permanently Disabled per Courtroom Requirement)
class HapticAudioEngine {
  constructor() {
    this.ctx = null;
    this.enabled = false;'''
    content = content.replace(old_haptic_def, new_haptic_def)

    # Disable all audio methods
    content = content.replace('playTap() {', 'playTap() { return;')
    content = content.replace('playSoftTap() {', 'playSoftTap() { return;')
    content = content.replace('playSuccess() {', 'playSuccess() { return;')
    content = content.replace('playError() {', 'playError() { return;')
    content = content.replace('toggle() {', 'toggle() { this.enabled = false; return false;')

    # 2. Fix setTextScale inline styles so text is always high-contrast visible
    old_ts_styles = '''      if (i === levelIdx) {
        btn.classList.add('active');
        btn.style.backgroundColor = '#00453D';
        btn.style.color = '#FFFFFF';
        btn.style.borderColor = '#00453D';
      } else {
        btn.classList.remove('active');
        btn.style.backgroundColor = '#FFFFFF';
        btn.style.color = '#131B2E';
        btn.style.borderColor = '#BEC9C5';
      }'''
    new_ts_styles = '''      if (i === levelIdx) {
        btn.classList.add('active');
        btn.style.backgroundColor = '#0F172A';
        btn.style.color = '#FFFFFF';
        btn.style.borderColor = '#0F172A';
      } else {
        btn.classList.remove('active');
        btn.style.backgroundColor = '#FFFFFF';
        btn.style.color = '#0F172A';
        btn.style.borderColor = '#94A3B8';
      }'''
    content = content.replace(old_ts_styles, new_ts_styles)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed app.js")

def sync_to_static():
    static_dir = REPO_DIR / "app" / "static"
    for fname in ["index.html", "login.html", "styles.css", "app.js"]:
        src = REPO_DIR / fname
        dst = static_dir / fname
        if src.exists() and static_dir.exists():
            shutil.copy2(src, dst)
            print(f"Synced {fname} to app/static/{fname}")

if __name__ == "__main__":
    fix_styles_css()
    fix_index_html()
    fix_app_js()
    sync_to_static()
