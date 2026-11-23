import re
import os
import shutil
from pathlib import Path

REPO_DIR = Path(r"C:\Users\Arpit Yadav\.gemini\antigravity\scratch\chronofact")

ROOT_VARS = """:root, [data-theme="light"] {
  /* Official Government of India Cyber Crime Portal (MHA / I4C / DFSS Design System) */
  --primary: #0262af;
  --primary-container: #EFF6FF;
  --primary-hover: #004d8c;
  --on-primary: #FFFFFF;
  --secondary: #002654;
  --accent-cyan: #38BDF8;
  --accent-gold: #F59E0B;

  --bg-canvas: #F4F7FB;
  --bg-sidebar: #FFFFFF;
  --bg-surface: #FFFFFF;
  --bg-card: #FFFFFF;
  --bg-card-hover: #F8FAFC;
  --bg-inset: #F8FAFC;
  --bg-input: #FFFFFF;
  --bg-elevated: #F1F5F9;

  --border-subtle: #CBD5E1;
  --border-hairline: #CBD5E1;
  --border-focus: #0262af;
  --border-divider: #E2E8F0;

  --text-primary: #0F172A;
  --text-secondary: #334155;
  --text-muted: #475569;
  --text-dim: #64748B;

  --color-danger: #DC2626;
  --color-danger-bg: #FEF2F2;
  --color-danger-border: #FECACA;
  --color-danger-text: #991B1B;

  --color-warning: #D97706;
  --color-warning-bg: #FFFBEB;
  --color-warning-border: #FDE68A;
  --color-warning-text: #92400E;

  --color-success: #059669;
  --color-success-bg: #ECFDF5;
  --color-success-border: #A7F3D0;
  --color-success-text: #065F46;

  --color-info: #0262af;
  --color-info-bg: #EFF6FF;
  --color-info-border: #BFDBFE;
  --color-info-text: #1D4ED8;

  --shadow-subtle: 0 1px 3px rgba(0, 0, 0, 0.05);
  --shadow-card: 0 4px 14px -2px rgba(2, 98, 175, 0.08);
  color-scheme: light;
}"""

def fix_styles_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Restore :root variables
    content = re.sub(
        r':root,\s*\[data-theme="light"\],\s*/\*.*?\*/',
        ROOT_VARS,
        content
    )

    # 2. Portal nav btn span rule
    if ".portal-nav-btn span {" not in content:
        content = content.replace(
            ".portal-nav-btn {",
            ".portal-nav-btn {\n  color: #0F172A !important;\n}\n.portal-nav-btn span {\n  color: #0F172A !important;\n  font-weight: 700 !important;\n}\n.portal-nav-btn-old {"
        )
        content = content.replace(".portal-nav-btn-old {", ".portal-nav-btn {")

    # 3. Footer wrappers
    content = re.sub(
        r'\.footer-top-wrapper\s*\{[^}]*\}',
        '''.footer-top-wrapper {
  background: #FFFFFF !important;
  color: #334155 !important;
  padding: 32px 0 24px 0 !important;
  border-top: 2px solid #CBD5E1 !important;
}''',
        content
    )
    content = re.sub(
        r'\.footer-bottom-wrapper\s*\{[^}]*\}',
        '''.footer-bottom-wrapper {
  background: #F1F5F9 !important;
  color: #475569 !important;
  padding: 16px 0 28px 0 !important;
  font-size: 11px !important;
  border-top: 1px solid #CBD5E1 !important;
}''',
        content
    )

    # 4. Workbench scroll area bottom padding
    content = re.sub(
        r'#workbench-scroll-area\s*\{[^}]*\}',
        '''#workbench-scroll-area {
  padding-bottom: 7rem !important;
  height: 100% !important;
  min-height: 0 !important;
}''',
        content
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed {file_path}")

def fix_index_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove the white-forcing CSS in <style>
    bad_style_block = re.search(
        r'/\* Megamenu text contrast \*/.*?#officer-menu-btn \.officer-label\s*\{[^}]*\}\s*\}',
        content,
        re.DOTALL
    )
    if bad_style_block:
        replacement = """/* Megamenu High-Contrast Dark Text */
    .megamenu-wraper {
      background-color: #F8FAFC !important;
      border-bottom: 1.5px solid #CBD5E1 !important;
    }
    .megamenu-wraper .portal-nav-btn {
      color: #0F172A !important;
      font-weight: 700 !important;
    }
    .megamenu-wraper .portal-nav-btn span {
      color: #0F172A !important;
      font-weight: 700 !important;
    }
    .megamenu-wraper .portal-nav-btn i {
      color: #334155 !important;
    }
    .megamenu-wraper .portal-nav-btn.active {
      background-color: #0F172A !important;
      color: #FFFFFF !important;
      border-color: #0F172A !important;
    }
    .megamenu-wraper .portal-nav-btn.active span {
      color: #FFFFFF !important;
      font-weight: 800 !important;
    }
    .megamenu-wraper .portal-nav-btn.active i {
      color: #FFFFFF !important;
    }
    .megamenu-wraper .officer-label {
      color: #0F172A !important;
      font-weight: 700 !important;
    }
    #officer-menu-btn,
    #officer-menu-btn span,
    #officer-menu-btn .officer-label {
      color: #0F172A !important;
    }
    .header-case-badge,
    .header-case-badge span,
    .header-case-badge i {
      color: #0F172A !important;
    }
    #header-vault-status-pill,
    #header-vault-status-pill span {
      color: #064E3B !important;
    }"""
        content = content.replace(bad_style_block.group(0), replacement)

    # 2. Fix #workbench-scroll-area classes: change h-screen to h-full min-h-0 pb-24
    content = content.replace(
        'id="workbench-scroll-area" class="flex-1 flex flex-col h-screen overflow-y-auto min-w-0 bg-[#F8FAFC]"',
        'id="workbench-scroll-area" class="flex-1 flex flex-col h-full min-h-0 overflow-y-auto min-w-0 bg-[#F8FAFC] pb-28"'
    )

    # 3. Fix footer markup to use high-contrast dark text on clean courtroom background
    old_footer = re.search(r'<footer class="w-full mt-12 no-print select-none">.*?</footer>', content, re.DOTALL)
    if old_footer:
        new_footer = """<footer class="w-full mt-12 no-print select-none pb-24">
        <div class="footer-top-wrapper px-6 py-8">
          <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-6 text-xs text-slate-700">
            <div class="space-y-2">
              <div class="font-extrabold text-[#0F172A] uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                <i data-lucide="shield" class="w-4 h-4 text-[#0262af]"></i>
                <span>About ChronoFact • I4C</span>
              </div>
              <p class="text-slate-600 text-[11px] leading-relaxed">
                National Judicial Cyber Forensic Intelligence Workbench operated in adherence with the Indian Cyber Crime Coordination Centre (I4C), Ministry of Home Affairs, and Directorate of Forensic Science Services (DFSS).
              </p>
            </div>

            <div class="space-y-2">
              <div class="font-extrabold text-[#0F172A] uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                <i data-lucide="scale" class="w-4 h-4 text-amber-600"></i>
                <span>Statutory Mandate</span>
              </div>
              <ul class="space-y-1.5 text-[11px] text-slate-600">
                <li>&bull; Bharatiya Sakshya Adhiniyam, 2023 §63(4)</li>
                <li>&bull; Information Technology Act, 2000 §79A</li>
                <li>&bull; ISO/IEC 27037:2012 Digital Evidence Handling</li>
                <li>&bull; NIST FIPS 180-4 / FIPS 202 Dual Hash</li>
              </ul>
            </div>

            <div class="space-y-2">
              <div class="font-extrabold text-[#0F172A] uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                <i data-lucide="code-2" class="w-4 h-4 text-cyan-600"></i>
                <span>Project Reference</span>
              </div>
              <div class="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
                <div class="text-[10px] uppercase text-cyan-700 font-bold">SUTRAM 2026 Prototype</div>
                <div class="text-xs font-bold text-slate-900">ChronoFact 2.0 AI Workbench</div>
                <div class="text-[10px] text-slate-500 font-mono">Academic Research Project</div>
              </div>
            </div>

            <div class="space-y-2">
              <div class="font-extrabold text-[#0F172A] uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                <i data-lucide="server" class="w-4 h-4 text-emerald-600"></i>
                <span>Forensic Terminal Status</span>
              </div>
              <div class="space-y-1 text-[11px] text-slate-600">
                <div class="flex items-center gap-1.5 text-emerald-700 font-semibold">
                  <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <span>Evaluation Node #FE-802 (Offline Safe Mode)</span>
                </div>
                <div id="footer-examiner-info" class="text-slate-700 font-medium">Examiner: A. Sharma (Forensic Analyst #FE-802)</div>
                <div>Hash Verification: SHA-256 + SHA3-256</div>
                <div>Specification: RFC 6962 Merkle Tree Audit</div>
              </div>
            </div>
          </div>
        </div>

        <div class="footer-bottom-wrapper px-6 py-4">
          <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-600">
            <div>
              &copy; 2026 ChronoFact Research Team. Built for SUTRAM 2026 National Cyber Security Hackathon. Academic Research Prototype — Not affiliated with any Government entity.
            </div>
            <div class="flex items-center gap-3 font-medium">
              <span>SUTRAM 2026 Prototype</span>
              <span>&bull;</span>
              <span>ISO/IEC 27037:2012 Forensic Standard</span>
              <span>&bull;</span>
              <span class="text-emerald-700 font-mono font-bold">Merkle Root Verified</span>
            </div>
          </div>
        </div>
      </footer>"""
        content = content.replace(old_footer.group(0), new_footer)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed {file_path}")

fix_styles_file(REPO_DIR / "styles.css")
fix_styles_file(REPO_DIR / "app" / "static" / "styles.css")
fix_index_file(REPO_DIR / "index.html")
fix_index_file(REPO_DIR / "app" / "static" / "index.html")
print("ALL FILES FIXED!")
