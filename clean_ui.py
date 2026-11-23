import re
import os
import shutil
from pathlib import Path

REPO_DIR = Path(r"C:\Users\Arpit Yadav\.gemini\antigravity\scratch\chronofact")

def clean_index_html():
    file_path = REPO_DIR / "index.html"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove Language Switcher
    content = re.sub(
        r'<!-- Language Switcher \(EN / HI\) -->\s*<div class="flex items-center gap-1" id="lang-switcher">.*?</div>',
        '',
        content,
        flags=re.DOTALL
    )

    # 2. Remove Theme Toggle Button
    content = re.sub(
        r'<!-- 1-Click Dark/Light Theme Toggle -->\s*<button\s+onclick="toggleTheme\(\)".*?</button>',
        '',
        content,
        flags=re.DOTALL
    )

    # 3. Replace Hindi Title with English
    old_title_pattern = r'<div class="text-\[13px\] sm:text-\[15px\] font-black text-primary leading-tight font-serif tracking-tight">\s*न्यायिक इलेक्ट्रॉनिक साक्ष्य विश्लेषण कार्यपीठ\s*</div>\s*<div class="text-\[12px\] sm:text-\[13px\] font-semibold text-secondary leading-tight">\s*Judicial Electronic Evidence Chronology &amp; Verification Workbench\s*</div>'
    new_title = '''<div class="text-[14px] sm:text-[16px] font-black text-primary leading-tight font-serif tracking-tight">
            Judicial Electronic Evidence Chronology &amp; Verification Workbench
          </div>
          <div class="text-[11px] sm:text-[12px] font-medium text-secondary leading-tight">
            Digital Forensics &amp; Admissibility Reasoning System
          </div>'''
    content = re.sub(old_title_pattern, new_title, content, flags=re.DOTALL)

    # 4. Replace Sidebar Subtitles
    content = content.replace('<div class="text-[10px] text-slate-500 font-normal">प्रकरण अवलोकन</div>', '<div class="text-[10px] text-slate-500 font-normal">Health &amp; Telemetry</div>')
    content = content.replace('<div class="text-[10px] text-slate-500 font-normal">साक्ष्य भंडार</div>', '<div class="text-[10px] text-slate-500 font-normal">Digital Storage</div>')
    content = content.replace('<div class="text-[10px] text-slate-500 font-normal">घटनाक्रम समयरेखा</div>', '<div class="text-[10px] text-slate-500 font-normal">Chronological Graph</div>')
    content = content.replace('<div class="text-[10px] text-slate-500 font-normal">न्यायिक विश्लेषण</div>', '<div class="text-[10px] text-slate-500 font-normal">Contradiction Radar</div>')
    content = content.replace('<div class="text-[10px] text-slate-500 font-normal">न्यायालय प्रमाणन</div>', '<div class="text-[10px] text-slate-500 font-normal">Courtroom Certificate</div>')

    # 5. Remove data-i18n-hi and data-i18n-en attributes
    content = re.sub(r'\s*data-i18n-hi="[^"]*"', '', content)
    content = re.sub(r'\s*data-i18n-en="[^"]*"', '', content)

    # 6. Change hardcoded dark bg on scroll area to clean off-white
    content = content.replace(
        'id="workbench-scroll-area" class="flex-1 flex flex-col h-screen overflow-y-auto min-w-0 bg-[#0B0F17]"',
        'id="workbench-scroll-area" class="flex-1 flex flex-col h-screen overflow-y-auto min-w-0 bg-[#F8FAFC]"'
    )

    # 7. Remove dark: classes
    content = content.replace('text-slate-800 dark:text-slate-200', 'text-slate-800')
    content = content.replace('text-slate-500 dark:text-slate-400', 'text-slate-500')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Cleaned index.html")

def clean_login_html():
    file_path = REPO_DIR / "login.html"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove all [data-theme="dark"] CSS rules from <style>
    content = re.sub(r'\[data-theme="dark"\]\s*\{[^}]*\}', '', content)
    content = re.sub(r'\[data-theme="dark"\][^{]+\{[^}]*\}', '', content)

    # 2. Remove Language Switcher
    content = re.sub(
        r'<!-- Language Switcher \(EN / HI\) -->\s*<div class="flex items-center gap-1" id="lang-switcher">.*?</div>',
        '',
        content,
        flags=re.DOTALL
    )

    # 3. Remove Theme Toggle Button
    content = re.sub(
        r'<!-- Theme Toggle \(Light / Dark\) -->\s*<button\s+onclick="toggleLoginTheme\(\)".*?</button>',
        '',
        content,
        flags=re.DOTALL
    )

    # 4. Remove dark: classes
    content = content.replace('text-emerald-600 dark:text-emerald-400', 'text-emerald-600')

    # 5. Remove data-i18n-hi and data-i18n-en attributes
    content = re.sub(r'\s*data-i18n-hi="[^"]*"', '', content)
    content = re.sub(r'\s*data-i18n-en="[^"]*"', '', content)

    # 6. Simplify JS: lock to light theme, remove setLanguage and theme toggles
    old_script_match = re.search(r'// Bilingual Language Controller.*?// Form Submission', content, re.DOTALL)
    if old_script_match:
        content = content.replace(old_script_match.group(0), '// Form Submission')

    old_theme_match = re.search(r'// Theme Engine Controller.*?(?=// DOM Ready)', content, re.DOTALL)
    if old_theme_match:
        content = content.replace(old_theme_match.group(0), '')

    # Ensure DOM ready cleans up localStorage and enforces light
    content = content.replace(
        'window.addEventListener(\'DOMContentLoaded\', () => {\n      initLoginTheme();',
        'window.addEventListener(\'DOMContentLoaded\', () => {\n      document.documentElement.setAttribute(\'data-theme\', \'light\');\n      try { localStorage.removeItem(\'chronofact_theme\'); localStorage.removeItem(\'chronofact_lang\'); } catch (_) {}'
    )
    content = re.sub(r'// Restore saved language\s*try\s*\{\s*const savedLang = localStorage\.getItem\(\'chronofact_lang\'\).*?\}\s*catch\s*\(_\)\s*\{\}', '', content, flags=re.DOTALL)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Cleaned login.html")

def clean_styles_css():
    file_path = REPO_DIR / "styles.css"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update root to cover both light and any fallback dark selector
    content = content.replace(':root, [data-theme="light"] {', ':root, [data-theme="light"], [data-theme="dark"] {')

    # 2. Remove [data-theme="dark"] { ... } block
    dark_block_match = re.search(r'\[data-theme="dark"\]\s*\{.*?color-scheme:\s*dark;\s*\}', content, re.DOTALL)
    if dark_block_match:
        content = content.replace(dark_block_match.group(0), '/* Dark theme permanently decommissioned - pure courtroom light theme */')

    # 3. Remove dark button overrides
    content = re.sub(r'\[data-theme="dark"\]\s*\.btn-editorial-primary\s*\{[^}]*\}', '', content)
    content = re.sub(r'\[data-theme="dark"\]\s*\.btn-editorial-primary:hover\s*\{[^}]*\}', '', content)

    # 4. Remove dark hex view overrides
    content = re.sub(r'\[data-theme="dark"\]\s*\.hex-offset-col\s*\{[^}]*\}', '', content)
    content = re.sub(r'\[data-theme="dark"\]\s*\.hex-anomaly-byte\s*\{[^}]*\}', '', content)

    # 5. Ensure scroll area background is pure canvas
    content += '\n\n#workbench-scroll-area {\n  background-color: var(--bg-canvas) !important;\n}\n'

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Cleaned styles.css")

def clean_app_js():
    file_path = REPO_DIR / "app.js"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace theme controller with static light enforcer
    old_theme_code = '''// Dual Light/Dark Theme Controller (Cellebrite x Palantir Legal-Tech Standard)
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  try {
    localStorage.setItem('chronofact-theme', theme);
  } catch (_) {}
  const icons = document.querySelectorAll('.theme-toggle-icon');
  icons.forEach(icon => {
    icon.setAttribute('data-lucide', theme === 'dark' ? 'sun' : 'moon');
  });
  if (window.lucide) lucide.createIcons();
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
}

// Initialize theme from storage or system preference
(function initTheme() {
  try {
    const saved = localStorage.getItem('chronofact-theme');
    if (saved) {
      applyTheme(saved);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      applyTheme('dark');
    } else {
      applyTheme('light');
    }
  } catch (_) {}
})();'''

    new_theme_code = '''// White Courtroom Theme Enforcer
function applyTheme(theme = 'light') {
  document.documentElement.setAttribute('data-theme', 'light');
  try {
    localStorage.removeItem('chronofact-theme');
    localStorage.removeItem('chronofact_theme');
  } catch (_) {}
}

function toggleTheme() {
  applyTheme('light');
}

(function initTheme() {
  applyTheme('light');
})();'''

    content = content.replace(old_theme_code, new_theme_code)

    # 2. Replace language controller with English-only
    old_lang_match = re.search(r'// =============================================================================\s*// BILINGUAL LANGUAGE CONTROLLER.*?// =============================================================================\s*// TERMINAL AUTHENTICATION GUARD', content, re.DOTALL)
    if old_lang_match:
        new_lang_code = '''// =============================================================================
// LANGUAGE CONTROLLER (ENGLISH COURTROOM STANDARD)
// =============================================================================
let currentLang = 'en';

function setLanguage(lang = 'en') {
  currentLang = 'en';
  try {
    localStorage.removeItem('chronofact_lang');
  } catch (_) {}
}

// =============================================================================
// TERMINAL AUTHENTICATION GUARD'''
        content = content.replace(old_lang_match.group(0), new_lang_code)

    # 3. Replace setLanguage(savedLang) in init
    content = content.replace("setLanguage(savedLang);", "setLanguage('en');")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Cleaned app.js")

def sync_to_static():
    static_dir = REPO_DIR / "app" / "static"
    for fname in ["index.html", "login.html", "styles.css", "app.js"]:
        src = REPO_DIR / fname
        dst = static_dir / fname
        if src.exists() and static_dir.exists():
            shutil.copy2(src, dst)
            print(f"Synced {fname} to app/static/{fname}")

if __name__ == "__main__":
    clean_index_html()
    clean_login_html()
    clean_styles_css()
    clean_app_js()
    sync_to_static()
