import os
import subprocess

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CHRONOFACT - Official 3-Minute Demo Video Script</title>
<style>
  @page {
    size: A4;
    margin: 14mm 16mm 14mm 16mm;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #0F172A;
    background: #FFF;
    line-height: 1.45;
    font-size: 11pt;
    margin: 0;
    padding: 0;
  }
  .header-box {
    border-bottom: 2px solid #0262af;
    padding-bottom: 12px;
    margin-bottom: 16px;
  }
  .title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  h1 {
    font-size: 22pt;
    color: #002654;
    margin: 0;
    font-weight: 800;
    letter-spacing: -0.5px;
  }
  .badge {
    background: #EFF6FF;
    color: #0262af;
    border: 1px solid #BFDBFE;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 9pt;
    font-weight: 700;
    text-transform: uppercase;
  }
  .subtitle {
    color: #0262af;
    font-size: 13pt;
    font-weight: 700;
    margin: 4px 0 2px 0;
  }
  .meta {
    color: #64748B;
    font-size: 9pt;
    margin: 0;
  }
  h2 {
    font-size: 12.5pt;
    color: #002654;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 4px;
    margin-top: 18px;
    margin-bottom: 8px;
    font-weight: 700;
  }
  .checklist {
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 14px;
  }
  .checklist-item {
    font-size: 9pt;
    margin-bottom: 4px;
    display: flex;
    align-items: flex-start;
    gap: 6px;
  }
  .checklist-item strong {
    color: #0F172A;
  }
  .section-tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 9.5pt;
    margin-top: 10px;
    margin-bottom: 4px;
  }
  .tag-red { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
  .tag-blue { background: #EFF6FF; color: #0262af; border: 1px solid #BFDBFE; }
  .tag-green { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
  .tag-navy { background: #F1F5F9; color: #002654; border: 1px solid #CBD5E1; }
  
  .visual-cue {
    font-style: italic;
    color: #475569;
    font-size: 8.5pt;
    background: #F1F5F9;
    padding: 5px 8px;
    border-left: 3px solid #64748B;
    margin: 3px 0 6px 0;
    border-radius: 0 4px 4px 0;
  }
  .speech-bubble {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-left: 3px solid #0262af;
    padding: 7px 10px;
    font-size: 9.5pt;
    color: #0F172A;
    margin-bottom: 10px;
    border-radius: 0 6px 6px 0;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 6px 0 12px 0;
    font-size: 8.5pt;
  }
  th {
    background: #002654;
    color: #FFF;
    text-align: left;
    padding: 5px 8px;
    font-weight: 700;
    border: 1px solid #002654;
  }
  td {
    padding: 5px 8px;
    border: 1px solid #CBD5E1;
    vertical-align: top;
  }
  tr:nth-child(even) td {
    background: #F8FAFC;
  }
  .step-num {
    font-weight: 700;
    color: #0262af;
    text-align: center;
    width: 25px;
  }
  .qna-box {
    margin-bottom: 6px;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 9pt;
  }
  .qna-q { font-weight: 700; color: #0262af; margin-bottom: 2px; }
  .qna-a { color: #334155; }
  .page-break { page-break-before: always; }
</style>
</head>
<body>

<div class="header-box">
  <div class="title-row">
    <div>
      <h1>⚖️ CHRONOFACT</h1>
      <div class="subtitle">OFFICIAL 3-MINUTE DEMO VIDEO SCRIPT</div>
      <p class="meta">National Judicial Cyber Forensic Intelligence Workbench | BSA 2023 §63(4)<br>Setup: OBS Studio (1080p Screen Recording + Corner Webcam) · Mode: Real Presenter (No AI Video)</p>
    </div>
    <div>
      <span class="badge">Official Hackathon Script</span>
    </div>
  </div>
</div>

<div class="checklist">
  <strong style="color: #002654; font-size: 9.5pt; display: block; margin-bottom: 4px;">📋 PRE-RECORDING CHECKLIST (Do this 20 minutes before)</strong>
  <div class="checklist-item"><span>☐</span> <div><strong>OBS Resolution:</strong> Set Browser Source to <strong>Width: 1920, Height: 1080</strong> (Press <code>Ctrl + S</code> in OBS to stretch to canvas edge-to-edge).</div></div>
  <div class="checklist-item"><span>☐</span> <div><strong>Pre-load Workbench:</strong> Open <code>http://127.0.0.1:8000/</code> in your browser. Verify credentials <code>examiner</code> / <code>SecurePassMin16Chars!</code> or 1-Click login.</div></div>
  <div class="checklist-item"><span>☐</span> <div><strong>OBS Interact Mode:</strong> Right-click Browser Source in OBS &rarr; Click <strong>"Interact"</strong> so you can click live buttons on camera!</div></div>
  <div class="checklist-item"><span>☐</span> <div><strong>Audio &amp; Mic Check:</strong> Connect wired earphone or collar mic. Keep voice meter in OBS green/yellow zone (no red distortion).</div></div>
  <div class="checklist-item"><span>☐</span> <div><strong>Webcam Setup:</strong> Stack books under laptop so camera is eye-level. Good front light on face. Silence phone &amp; turn Focus Assist ON.</div></div>
</div>

<h2>⏱️ FULL SHOT-BY-SHOT TIMELINE (3:00 Minutes)</h2>

<span class="section-tag tag-red">🔴 [0:00 – 0:20] THE HOOK — Problem Statement</span>
<div class="visual-cue">🎬 Visual: Fullscreen Webcam OR Dark Slide with text: "In Indian courts, over 80% of cyber crime evidence gets dismissed... not because the suspect is innocent, but because evidence lacks mathematical chain-of-custody."</div>
<div class="speech-bubble">
  <strong>🎙️ SPEAK (Serious, high impact):</strong><br>
  "Imagine this: A cyber criminal loots ₹50 lakhs or leaks sensitive corporate data at 2 AM.<br>
  Police catch him. But in court, the defense lawyer claims just one thing: <em>'Sir, this digital log is doctored. The timestamp is modified. And there is no valid statutory certificate.'</em><br>
  Under the new <strong>Bharatiya Sakshya Adhiniyam, 2023</strong>, electronic records without mathematical chain-of-custody are <strong>instantly rejected</strong>.<br>
  The criminal walks free — not because he didn't commit the crime — but because our investigation lacked mathematical legal proof."<br>
  <em>(Pause 1 second — let it sink in)</em>
</div>

<span class="section-tag tag-blue">💡 [0:20 – 0:40] THE SOLUTION — Introducing ChronoFact</span>
<div class="visual-cue">🎬 Visual: Switch to Screen Recording (1080p) showing Login Terminal with National Emblem and official GoI portal aesthetics. Webcam in bottom-right corner.</div>
<div class="speech-bubble">
  <strong>🎙️ SPEAK:</strong><br>
  "Presenting <strong>CHRONOFACT</strong> — the National Judicial Cyber Forensic Intelligence Workbench, built strictly for <strong>Section 63(4) of the Bharatiya Sakshya Adhiniyam, 2023</strong>.<br>
  ChronoFact fuses multi-source digital evidence — IP server access logs, telecom BTS tower pings, and suspect statements — into an immutable cryptographic timeline.<br>
  It doesn't just store logs. It <strong>proves</strong> the exact second a suspect lied, with zero-tamper mathematical certainty."
</div>

<span class="section-tag tag-green">📱 [0:40 – 1:20] LIVE DEMO 1: Forensic Workbench &amp; Exhibit Vault</span>
<div class="visual-cue">🎬 Visual: OBS Interact window live screen actions:</div>

<table>
  <thead>
    <tr>
      <th style="width: 35px;">Step</th>
      <th style="width: 45%;">Action on Screen (OBS Interact)</th>
      <th>What to Say (Voiceover)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="step-num">1</td>
      <td>Click green <strong>"1-Click Officer Auto-Login"</strong> button</td>
      <td>"The examiner authenticates into an air-gapped forensic terminal with role-based cryptographic keys."</td>
    </tr>
    <tr>
      <td class="step-num">2</td>
      <td>Dashboard loads: <strong>State v. Vikram Malhotra (FIR 204/2026)</strong></td>
      <td>"Immediately, our live judicial case loads: State of NCT of Delhi v. Vikram Malhotra."</td>
    </tr>
    <tr>
      <td class="step-num">3</td>
      <td>Click Examiner badge in navbar (Examiner #FE-802 / Vikram)</td>
      <td>"Every investigation is cryptographically bound to the Lead Examiner and Badge ID, auditable at every click."</td>
    </tr>
    <tr>
      <td class="step-num">4</td>
      <td>Highlight 4 Metric Cards (Seized Exhibits: 4, NIST Dual Hash: 100%)</td>
      <td>"Look at the evidence vault. Every file is sealed with dual NIST FIPS hashes — SHA-256 plus SHA3-256. If a single bit is touched, the vault alarms immediately."</td>
    </tr>
    <tr>
      <td class="step-num">5</td>
      <td>Click <strong>"Switch / Load Case Samples"</strong> button</td>
      <td>"ChronoFact comes pre-loaded with multiple real-world forensic samples — from crypto exfiltration to financial fraud."</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<span class="section-tag tag-navy">🖥️ [1:20 – 2:00] LIVE DEMO 2: AI Anomaly Radar (The Alibi Buster)</span>
<div class="visual-cue">🎬 Visual: Scroll down to "Spatial-Temporal Conflict Matrix" &amp; "Timeline Reconstruction":</div>

<table>
  <thead>
    <tr>
      <th style="width: 35px;">Step</th>
      <th style="width: 45%;">Action on Screen (OBS Interact)</th>
      <th>What to Say (Voiceover)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="step-num">1</td>
      <td>Highlight <strong>Suspect Alibi Box</strong> (Yellow border)</td>
      <td>"Here is suspect Vikram's defense statement: 'Sir, I had high fever, I was asleep in bed and completely offline till morning.' Traditional investigators struggle to disprove this."</td>
    </tr>
    <tr>
      <td class="step-num">2</td>
      <td>Highlight <strong>Ground Reality Box</strong> (Emerald border)</td>
      <td>"ChronoFact's AI Anomaly Engine cross-references server logs against telecom BTS tower records."</td>
    </tr>
    <tr>
      <td class="step-num">3</td>
      <td>Hover over: <strong>+24.8 km Conflict &amp; +5h 28m Time Skew</strong></td>
      <td>"Boom! An undeniable spatial-temporal conflict: At the exact minute Vikram claimed to be asleep, an authenticated session logged in from IP 192.168.1.105, pinging an antenna 24.8 km away from his home!"</td>
    </tr>
    <tr>
      <td class="step-num">4</td>
      <td>Scroll to <strong>Multi-Stream Chronological Timeline</strong></td>
      <td>"Every event from server CSVs, phone dumps, and network streams is chronologically synchronized on a microsecond timeline. His alibi is mathematically obliterated."</td>
    </tr>
  </tbody>
</table>

<span class="section-tag tag-blue">⚖️ [2:00 – 2:30] LIVE DEMO 3: BSA 2023 §63(4) Statutory Certificate &amp; Merkle Vault</span>
<div class="visual-cue">🎬 Visual: Open "BSA Legal Certificate" view / modal:</div>

<table>
  <thead>
    <tr>
      <th style="width: 35px;">Step</th>
      <th style="width: 45%;">Action on Screen (OBS Interact)</th>
      <th>What to Say (Voiceover)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="step-num">1</td>
      <td>Open Statutory Legal Certificate View (Emblem &amp; Header)</td>
      <td>"Now comes the judicial game-changer: Under Bharatiya Sakshya Adhiniyam Section 63(4), digital evidence requires a mandatory certificate signed by the examiner."</td>
    </tr>
    <tr>
      <td class="step-num">2</td>
      <td>Show pre-filled Schedule of Exhibits &amp; Dual Hashes</td>
      <td>"ChronoFact auto-compiles the entire statutory certificate — Schedule of Exhibits, SHA-256 digests, and custodial affirmation. Zero manual drafting errors."</td>
    </tr>
    <tr>
      <td class="step-num">3</td>
      <td>Click <strong>"Inspect Merkle Tree / Master Root"</strong></td>
      <td>"All exhibits are committed to a deterministic Merkle Tree. The Master Root seals all evidence. If defense lawyers question item 2, we provide a single cryptographic inclusion proof."</td>
    </tr>
    <tr>
      <td class="step-num">4</td>
      <td>Click <strong>"Export Case Dossier (ZIP)"</strong></td>
      <td>"One tap exports the complete legal dossier — signed certificates, hash manifests, and raw exhibits ready for the magistrate."</td>
    </tr>
  </tbody>
</table>

<span class="section-tag tag-navy">🏆 [2:30 – 2:50] IMPACT &amp; WHY WE WIN</span>
<div class="speech-bubble">
  <strong>🎙️ SPEAK:</strong><br>
  "Why does ChronoFact win?<br>
  Because it bridges the fatal gap between <strong>cyber forensics</strong> and the <strong>Indian Judicial Code</strong>.<br>
  Police officers get instant alibi busting. Public prosecutors get court-admissible certificates. And judges get zero-tamper mathematical truth.<br>
  It is 100% air-gapped capable, DPDP-compliant, and runs on standard government hardware with ₹0 extra infrastructure cost."
</div>

<span class="section-tag tag-red">🙏 [2:50 – 3:00] CLOSING (The Line They Remember)</span>
<div class="visual-cue">🎬 Visual: Fullscreen webcam on presenter (or split-screen). Slow down speech, confident eye contact into camera.</div>
<div class="speech-bubble" style="border-left-color: #DC2626; font-size: 10.5pt; font-weight: 700; color: #002654;">
  <strong>🎙️ SPEAK:</strong><br>
  "Criminals can fake an alibi. They can wipe their browser history.<br>
  But they cannot rewrite the laws of mathematics.<br>
  ChronoFact — Where Forensic Evidence Meets Judicial Truth.<br>
  Thank you."
</div>

<h2>🧠 JUDGES Q&amp;A — NOVELTY CRACKERS (Memorize These)</h2>

<div class="qna-box">
  <div class="qna-q">Q: BSA 2023 Section 63(4) vs Old Section 65B?</div>
  <div class="qna-a">"Section 65B of the Evidence Act was vague regarding device custody and hashing. BSA Section 63(4) explicitly mandates cryptographic hash preservation, examiner qualification, and schedule-based integrity. ChronoFact is engineered natively for BSA 2023 from Day 1."</div>
</div>

<div class="qna-box">
  <div class="qna-q">Q: Why use Dual Hashing (SHA-256 + SHA3-512)?</div>
  <div class="qna-a">"NIST FIPS standards and modern judicial forensics recommend dual hashing to protect against quantum collision vulnerabilities and provide defense-proof authenticity in high-court appeals."</div>
</div>

<div class="qna-box">
  <div class="qna-q">Q: What if the internet is down in the police station?</div>
  <div class="qna-a">"ChronoFact is 100% offline and air-gapped capable. The dual hashing engine, Merkle tree calculator, and spatial conflict engine run directly in-memory on the local machine with zero external cloud dependencies."</div>
</div>

<div class="qna-box">
  <div class="qna-q">Q: What stops an investigator from tampering with logs?</div>
  <div class="qna-a">"Every ingested exhibit is committed to a deterministic Merkle tree. Modifying even 1 single byte invalidates the root digest, and our built-in forensic test suite immediately triggers an uncatchable Integrity Violation error."</div>
</div>

</body>
</html>
"""

with open("script_print.html", "w", encoding="utf-8") as f:
    f.write(html_content)

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
pdf_out = os.path.abspath("CHRONOFACT_Official_Demo_Script.pdf")
html_path = os.path.abspath("script_print.html")

cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={pdf_out}",
    html_path
]

res = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(pdf_out):
    print(f"PDF generated successfully at: {pdf_out} ({os.path.getsize(pdf_out)} bytes)")
else:
    print(f"PDF generation failed: {res.stderr}")
