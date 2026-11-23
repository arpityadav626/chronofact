import re
import os
import shutil
from pathlib import Path

REPO_DIR = Path(r"C:\Users\Arpit Yadav\.gemini\antigravity\scratch\chronofact")

def fix_styles_css():
    file_path = REPO_DIR / "styles.css"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove stray closing brace at line 704-705
    content = content.replace(
        '.sidebar-nav-item.active {\n  color: var(--text-primary) !important;\n  background-color: var(--bg-inset) !important;\n  border-left: 3px solid var(--primary) !important;\n  border-color: var(--border-subtle) !important;\n  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;\n  font-weight: 600 !important;\n}\n  font-weight: 600 !important;\n}',
        '.sidebar-nav-item.active {\n  color: var(--text-primary) !important;\n  background-color: var(--bg-inset) !important;\n  border-left: 3px solid var(--primary) !important;\n  border-color: var(--border-subtle) !important;\n  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;\n  font-weight: 700 !important;\n}'
    )

    # 2. Remove stray closing brace at line 998-999
    content = content.replace(
        '.megamenu-wraper {\n  background: #FFFFFF !important;\n  border-top: 1px solid #E2E8F0 !important;\n  border-bottom: 1px solid #E2E8F0 !important;\n  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);\n}\n  box-shadow: 0 2px 10px rgba(2, 98, 175, 0.25);\n}',
        '.megamenu-wraper {\n  background: #F1F5F9 !important;\n  border-top: 1px solid #CBD5E1 !important;\n  border-bottom: 2px solid #CBD5E1 !important;\n  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06) !important;\n}'
    )

    # 3. Enhance .common-wrapper (Top strip)
    content = re.sub(
        r'\.common-wrapper\s*\{[^}]*\}',
        '''.common-wrapper {
  background: #FFFFFF !important;
  color: #0F172A !important;
  border-bottom: 1.5px solid #CBD5E1 !important;
  padding: 6px 0 !important;
}''',
        content
    )

    # 4. Enhance .text-size-btn
    content = re.sub(
        r'/\* Accessibility Text-Size Controls.*?\*/\s*\.text-size-btn\s*\{[^}]*\}\s*\.text-size-btn:hover\s*\{[^}]*\}\s*\.text-size-btn\.active\s*\{[^}]*\}',
        '''/* Accessibility Text-Size Controls (High-Contrast Courtroom Standard) */
.text-size-btn {
  font-size: 11px !important;
  font-weight: 800 !important;
  padding: 3px 8px !important;
  border-radius: 4px !important;
  border: 1.5px solid #64748B !important;
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  cursor: pointer !important;
  line-height: 1.2 !important;
  display: inline-block !important;
  transition: all 0.15s ease !important;
}

.text-size-btn:hover {
  background-color: #E2E8F0 !important;
  border-color: #1E293B !important;
  color: #0F172A !important;
}

.text-size-btn.active {
  background-color: #0F172A !important;
  color: #FFFFFF !important;
  border-color: #0F172A !important;
}''',
        content,
        flags=re.DOTALL
    )

    # 5. Enhance .portal-nav-btn
    content = re.sub(
        r'\.portal-nav-btn\s*\{[^}]*\}\s*\.portal-nav-btn:hover\s*\{[^}]*\}\s*\.portal-nav-btn\.active\s*\{[^}]*\}',
        '''.portal-nav-btn {
  display: inline-flex !important;
  align-items: center !important;
  gap: 7px !important;
  padding: 8px 14px !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  color: #334155 !important;
  background: transparent !important;
  border: 1px solid transparent !important;
  border-radius: 6px !important;
  transition: all 0.15s ease !important;
  cursor: pointer !important;
  white-space: nowrap !important;
}

.portal-nav-btn i {
  color: #475569 !important;
  width: 15px !important;
  height: 15px !important;
}

.portal-nav-btn:hover {
  background-color: #E2E8F0 !important;
  color: #0F172A !important;
}

.portal-nav-btn.active {
  background-color: #0F172A !important;
  color: #FFFFFF !important;
  border-color: #0F172A !important;
  box-shadow: 0 2px 4px rgba(15, 23, 42, 0.25) !important;
}

.portal-nav-btn.active span {
  color: #FFFFFF !important;
  font-weight: 800 !important;
}

.portal-nav-btn.active i {
  color: #F8FAFC !important;
}''',
        content,
        flags=re.DOTALL
    )

    # 6. Enhance .header-case-badge
    content = re.sub(
        r'\.header-case-badge\s*\{[^}]*\}\s*\.header-case-badge:hover\s*\{[^}]*\}',
        '''.header-case-badge {
  background: #FFFFFF !important;
  border: 1.5px solid #94A3B8 !important;
  border-radius: 9999px !important;
  padding: 6px 14px !important;
  color: #0F172A !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
  cursor: pointer !important;
  font-weight: 700 !important;
}

.header-case-badge:hover {
  background: #F8FAFC !important;
  border-color: #475569 !important;
}

.header-case-badge * {
  color: #0F172A !important;
}''',
        content,
        flags=re.DOTALL
    )

    # 7. Add bottom clearance and button rules
    addition = '''
/* Guaranteed Bottom Clearance so cards are never cut off by demo banner */
#workbench-scroll-area {
  padding-bottom: 6rem !important;
}
main {
  padding-bottom: 6rem !important;
}

/* High-Contrast Action Buttons */
.btn-editorial-primary {
  background-color: #0F172A !important;
  color: #FFFFFF !important;
  border: 1.5px solid #0F172A !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
  padding: 8px 14px !important;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.2) !important;
  cursor: pointer !important;
  transition: all 0.15s ease !important;
}
.btn-editorial-primary:hover {
  background-color: #1E293B !important;
  border-color: #1E293B !important;
}
.btn-editorial-primary * {
  color: #FFFFFF !important;
}

.btn-editorial-secondary {
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  border: 1.5px solid #CBD5E1 !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  padding: 8px 14px !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
  cursor: pointer !important;
  transition: all 0.15s ease !important;
}
.btn-editorial-secondary:hover {
  background-color: #F8FAFC !important;
  border-color: #94A3B8 !important;
  color: #0F172A !important;
}
.btn-editorial-secondary * {
  color: #0F172A !important;
}

/* Light Footer Styles */
.footer-top-wrapper {
  background: #F8FAFC !important;
  color: #334155 !important;
  border-top: 1.5px solid #CBD5E1 !important;
}
.footer-top-wrapper * {
  color: #334155 !important;
}
.footer-top-wrapper .font-bold {
  color: #0F172A !important;
}
.footer-bottom-wrapper {
  background: #FFFFFF !important;
  color: #64748B !important;
  border-top: 1px solid #E2E8F0 !important;
}
'''
    content += addition

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed styles.css successfully")

def fix_app_js():
    file_path = REPO_DIR / "app.js"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Completely remove LuxuryHapticAudio class and audio event listeners
    old_audio_pattern = r'// =============================================================================\s*// 1\. REFINED ACOUSTIC HAPTIC SOUND ENGINE.*?const hapticEngine = new LuxuryHapticAudio\(\);.*?\}\);'
    
    silent_engine = '''// =============================================================================
// 1. SOUND PERMANENTLY DISABLED (100% SILENT COURTROOM STANDARD)
// =============================================================================
const hapticEngine = {
  isMuted: true,
  enabled: false,
  init() {},
  toggle() { return false; },
  playSoftTap() {},
  playHoverTick() {},
  playChime() {},
  playSuccess() {},
  playWhoosh() {},
  playTap() {},
  playError() {}
};'''

    content = re.sub(old_audio_pattern, silent_engine, content, flags=re.DOTALL)

    # Also update setTextScale so it applies high-contrast styling
    old_ts_func = r'function setTextScale\(levelIdx = 1\) \{.*?\n\}'
    new_ts_func = '''function setTextScale(levelIdx = 1) {
  if (levelIdx < 0 || levelIdx >= TEXT_SCALE_LEVELS.length) levelIdx = 1;
  const scale = TEXT_SCALE_LEVELS[levelIdx];
  const root = document.documentElement;
  try {
    if (window.CSS && CSS.supports && CSS.supports('zoom', '1.15')) {
      root.style.zoom = String(scale);
    } else {
      root.style.fontSize = (scale * 16) + 'px';
    }
    localStorage.setItem('chronofact_text_scale', String(levelIdx));
  } catch (_) {}

  // Update active state on buttons
  [0, 1, 2, 3].forEach(i => {
    const btn = document.getElementById(`ts-btn-${i}`);
    if (btn) {
      if (i === levelIdx) {
        btn.classList.add('active');
        btn.style.backgroundColor = '#0F172A';
        btn.style.color = '#FFFFFF';
        btn.style.borderColor = '#0F172A';
      } else {
        btn.classList.remove('active');
        btn.style.backgroundColor = '#FFFFFF';
        btn.style.color = '#0F172A';
        btn.style.borderColor = '#64748B';
      }
    }
  });
}'''
    content = re.sub(old_ts_func, new_ts_func, content, flags=re.DOTALL)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed app.js successfully")

def fix_index_html():
    file_path = REPO_DIR / "index.html"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Ensure audio icon is removed
    content = re.sub(
        r'<!-- Audio / Haptic Toggle -->\s*<button\s+onclick="hapticEngine\.toggle\(\); updateHeaderSoundIcon\(\);".*?</button>',
        '',
        content,
        flags=re.DOTALL
    )

    # 2. Add pb-24 to main container
    content = content.replace(
        '<main class="flex-1 p-6 lg:p-10 space-y-10 max-w-7xl w-full mx-auto">',
        '<main class="flex-1 p-6 lg:p-10 space-y-10 max-w-7xl w-full mx-auto pb-24">'
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed index.html successfully")

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
    fix_app_js()
    fix_index_html()
    sync_to_static()
