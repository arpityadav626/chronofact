#!/usr/bin/env python3
"""
CHRONOFACT Single-File Prototype Builder
========================================
Compiles the complete ChronoFact 2.0 judicial forensic workbench into
ONE SINGLE, SELF-CONTAINED HTML FILE (Zero Dependencies, Offline-Ready).

Bundles:
1. Evaluator Login Portal (SUTRAM 2026 Academic Disclaimer)
2. Interactive Forensic Workbench (Multi-case, Merkle tree, Hex Inspector)
3. Inconsistency Radar with the 4 Mandatory Benign Hypotheses
4. BSA 2023 §63(4) Statutory Certificate Generator with Dual Signature Blocks
5. Inlined styles.css & inlined app.js with precomputed ML anomaly benchmarks
"""

import re
from pathlib import Path

def build_single_file(source_dir: Path, output_file: Path):
    index_path = source_dir / "index.html"
    login_path = source_dir / "login.html"
    styles_path = source_dir / "styles.css"
    app_path = source_dir / "app.js"

    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()

    with open(login_path, "r", encoding="utf-8") as f:
        login_html = f.read()

    with open(styles_path, "r", encoding="utf-8") as f:
        css = f.read()

    with open(app_path, "r", encoding="utf-8") as f:
        js = f.read()

    # Extract login body content
    body_match = re.search(r"<body[^>]*>(.*?)<!-- Interactive Client Engine -->", login_html, re.DOTALL)
    if body_match:
        login_body_inner = body_match.group(1).strip()
    else:
        login_body_inner = "<!-- Login UI Container -->"

    # In index_html, remove the redirect script that forces redirection to login.html
    redirect_pattern = r"<script>\s*\(function\(\)\s*\{\s*try\s*\{\s*var user = sessionStorage\.getItem\('chronofact_auth_user'\);.*?window\.location\.replace\('login\.html'\);.*?\}\s*\)\(\);\s*</script>"
    index_html = re.sub(redirect_pattern, "<!-- Standalone Authentication Gate Embedded -->", index_html, flags=re.DOTALL)

    # In index_html, optionally inline vendor scripts if present
    vendor_dir = source_dir / "assets" / "vendor"
    if (vendor_dir / "tailwind.min.js").exists() and (vendor_dir / "lucide.min.js").exists():
        with open(vendor_dir / "tailwind.min.js", "r", encoding="utf-8") as f:
            tw_js = f.read()
        with open(vendor_dir / "lucide.min.js", "r", encoding="utf-8") as f:
            lucide_js = f.read()
        with open(vendor_dir / "jszip.min.js", "r", encoding="utf-8") as f:
            jszip_js = f.read()
        vendor_replacement = f"""
  <!-- Inlined Offline Air-Gapped Vendor Libraries (Zero Network Dependencies) -->
  <script>
{tw_js}
  </script>
  <script>
{lucide_js}
  </script>
  <script>
{jszip_js}
  </script>
"""
        vendor_pattern = r'<!-- Offline Air-Gapped Local Vendor Scripts.*?<script src="assets/vendor/jszip\.min\.js"></script>\s*<script>.*?</script>'
        index_html = re.sub(vendor_pattern, lambda m: vendor_replacement, index_html, flags=re.DOTALL)

    # In index_html, replace the external stylesheet link with inlined <style>
    style_link_pattern = r'<link\s+rel=["\']stylesheet["\'][^>]*styles\.css[^>]*>'
    inlined_css = f"""
  <style>
/* ==========================================================================
   CHRONOFACT 2.0 INLINED FORENSIC DESIGN SYSTEM
   ========================================================================== */
{css}

/* Standalone Login Overlay Styles */
#login-overlay {{
  font-family: 'Inter', '"Noto Sans Devanagari"', system-ui, sans-serif;
}}
.trust-legal-banner {{
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: linear-gradient(135deg, #FFF8E1, #FFECB3);
  border: 1.5px solid #F59E0B;
  border-left: 5px solid #D97706;
  border-radius: 12px;
  padding: 0.85rem 1.1rem;
  font-size: 0.8rem;
  line-height: 1.55;
  color: #78350F;
  box-shadow: 0 1px 4px rgba(217, 119, 6, 0.08);
}}
.reassurance-strip {{
  background-color: #EFF6FF;
  border-top: 1px solid #DBEAFE;
  padding: 0.65rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 1.5rem;
  font-size: 0.75rem;
  color: #0262af;
  font-weight: 600;
}}
.reassurance-item {{
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}}
.squircle-badge {{
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}}
  </style>
"""
    index_html = re.sub(style_link_pattern, inlined_css, index_html)

    # Extract body content from index_html and wrap it in a workbench container
    body_content_match = re.search(r"<body[^>]*>(.*?)</body>", index_html, re.DOTALL)
    if not body_content_match:
        raise ValueError("Could not find body tag in index.html")
    
    workbench_content = body_content_match.group(1).strip()
    
    # Remove the bottom script tag from workbench_content
    script_tag_pattern = r'<script\s+src=["\']app\.js[^"\']*["\'][^>]*></script>'
    workbench_content = re.sub(script_tag_pattern, "", workbench_content)

    # Single-file combined body
    single_file_body = f"""
  <!-- ====================================================================== -->
  <!-- 1. STANDALONE LOGIN & EVALUATION OVERLAY GATE                          -->
  <!-- ====================================================================== -->
  <div id="login-overlay" style="display: none; min-height: 100vh; flex-direction: column; justify-content: space-between; position: fixed; inset: 0; z-index: 99999; background: #F4F7FB; overflow-y: auto;">
{login_body_inner}
  </div>

  <!-- ====================================================================== -->
  <!-- 2. MAIN CYBER FORENSIC WORKBENCH CONTAINER                             -->
  <!-- ====================================================================== -->
  <div id="workbench-root" style="display: none; min-height: 100vh;">
{workbench_content}
  </div>

  <!-- ====================================================================== -->
  <!-- 3. INLINED JAVASCRIPT LOGIC & FORENSIC ENGINES                         -->
  <!-- ====================================================================== -->
  <script>
/* Standalone Authentication & Gateway Controller */
function checkStandaloneAuth() {{
  try {{
    var user = sessionStorage.getItem('chronofact_auth_user');
    var token = sessionStorage.getItem('chronofact_auth_token');
    var loginEl = document.getElementById('login-overlay');
    var benchEl = document.getElementById('workbench-root');
    
    if (user && token && (user === 'examiner' || user === 'analyst' || user === 'arpit' || user === 'forensic_examiner')) {{
      if (loginEl) loginEl.style.display = 'none';
      if (benchEl) benchEl.style.display = 'block';
      if (window.lucide) lucide.createIcons();
    }} else {{
      if (loginEl) loginEl.style.display = 'flex';
      if (benchEl) benchEl.style.display = 'none';
      if (window.lucide) lucide.createIcons();
    }}
  }} catch (e) {{
    console.error('Auth check error:', e);
  }}
}}

function oneClickDemoLogin() {{
  var u = document.getElementById('login-username');
  var p = document.getElementById('login-password');
  if (u) u.value = 'examiner';
  if (p) p.value = 'SecurePassMin16Chars!';
  var alertBox = document.getElementById('login-alert-box');
  if (alertBox) {{
    alertBox.className = "p-3 rounded-xl border border-emerald-300 bg-emerald-50 text-emerald-800 text-xs font-semibold flex items-center gap-2";
    alertBox.innerHTML = '<i data-lucide="check-circle" class="w-4 h-4 text-emerald-600"></i> Evaluator credentials populated. Click Enter Forensic Workbench.';
    alertBox.classList.remove('hidden');
  }}
  if (window.lucide) lucide.createIcons();
}}

function handleLoginSubmit(e) {{
  if (e && e.preventDefault) e.preventDefault();
  var uInput = document.getElementById('login-username');
  var pInput = document.getElementById('login-password');
  var alertBox = document.getElementById('login-alert-box');
  var u = uInput ? uInput.value.trim() : '';
  var p = pInput ? pInput.value.trim() : '';

  if ((u === 'examiner' && p === 'SecurePassMin16Chars!') ||
      (u === 'analyst' && p === 'ChronoFact2026!') ||
      (u === 'arpit' && p === 'arpit626') ||
      (u === 'forensic_examiner' && p === 'SecurePassMin16Chars!')) {{
    
    sessionStorage.setItem('chronofact_auth_user', u);
    sessionStorage.setItem('chronofact_auth_token', 'CF2-STANDALONE-' + Date.now());
    sessionStorage.setItem('chronofact_officer', u === 'analyst' ? 'P. Verma (Forensic Junior Analyst)' : 'A. Sharma (Forensic Analyst #FE-802)');

    var loginEl = document.getElementById('login-overlay');
    var benchEl = document.getElementById('workbench-root');
    if (loginEl) loginEl.style.display = 'none';
    if (benchEl) benchEl.style.display = 'block';

    if (window.lucide) lucide.createIcons();
    if (typeof loadCaseData === 'function') {{
      loadCaseData('CASE_VIKRAM');
    }}
  }} else {{
    if (alertBox) {{
      alertBox.className = "p-3 rounded-xl border border-red-300 bg-red-50 text-red-800 text-xs font-semibold flex items-center gap-2";
      alertBox.innerHTML = '<i data-lucide="alert-triangle" class="w-4 h-4 text-red-600"></i> Invalid Examiner Credentials. Use examiner / SecurePassMin16Chars!';
      alertBox.classList.remove('hidden');
    }}
    if (window.lucide) lucide.createIcons();
  }}
}}

function togglePasswordVisibility() {{
  var input = document.getElementById('login-password');
  var icon = document.getElementById('password-toggle-icon');
  if (!input) return;
  if (input.type === 'password') {{
    input.type = 'text';
    if (icon) icon.setAttribute('data-lucide', 'eye-off');
  }} else {{
    input.type = 'password';
    if (icon) icon.setAttribute('data-lucide', 'eye');
  }}
  if (window.lucide) lucide.createIcons();
}}

/* Hook into terminal lock / sign out */
window.addEventListener('DOMContentLoaded', function() {{
  checkStandaloneAuth();
}});

/* ==========================================================================
   MAIN INLINED APPLICATION CODE (app.js)
   ========================================================================== */
{js}

/* Override lockTerminal to return to login overlay */
var originalLockTerminal = window.lockTerminal;
window.lockTerminal = function() {{
  try {{
    sessionStorage.removeItem('chronofact_auth_user');
    sessionStorage.removeItem('chronofact_auth_token');
  }} catch (_) {{}}
  var loginEl = document.getElementById('login-overlay');
  var benchEl = document.getElementById('workbench-root');
  if (loginEl) loginEl.style.display = 'flex';
  if (benchEl) benchEl.style.display = 'none';
  if (window.lucide) lucide.createIcons();
}};
  </script>
"""

    # Reconstruct the HTML cleanly without regex escape issues
    head_part = index_html[:index_html.find("<body")]
    full_html = f"{head_part}<body class=\"bg-canvas text-primary font-sans antialiased min-h-screen\">\n{single_file_body}\n</body>\n</html>"

    output_file.write_text(full_html, encoding="utf-8")
    print(f"Generated single-file prototype at: {output_file} ({output_file.stat().st_size:,} bytes)")

if __name__ == "__main__":
    src = Path("C:/Users/Arpit Yadav/.gemini/antigravity/scratch/chronofact")
    
    # 1. Output to scratch
    out_scratch = src / "ChronoFact_Single_File_Prototype.html"
    build_single_file(src, out_scratch)
    
    # 2. Output to Desktop for quick evaluator access
    desktop_dir = Path("C:/Users/Arpit Yadav/OneDrive/Desktop")
    if desktop_dir.exists():
        out_desktop = desktop_dir / "ChronoFact_Single_File_Prototype.html"
        build_single_file(src, out_desktop)
