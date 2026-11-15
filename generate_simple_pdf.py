import os
import subprocess

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CHRONOFACT - Simple 3-Minute Demo Video Script</title>
<style>
  @page {
    size: A4;
    margin: 15mm 18mm 15mm 18mm;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    color: #1E293B;
    background: #FFF;
    line-height: 1.5;
    font-size: 11pt;
    margin: 0;
    padding: 0;
  }
  .header {
    border-bottom: 2px solid #0262af;
    padding-bottom: 10px;
    margin-bottom: 16px;
  }
  h1 {
    font-size: 20pt;
    color: #002654;
    margin: 0 0 4px 0;
    font-weight: 800;
  }
  .tagline {
    color: #0262af;
    font-size: 11pt;
    font-weight: 600;
    margin: 0;
  }
  .desc {
    color: #64748B;
    font-size: 9pt;
    margin-top: 2px;
  }
  .card {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #0262af;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 14px;
  }
  .card-title {
    font-weight: 700;
    font-size: 11pt;
    color: #002654;
    margin-bottom: 4px;
  }
  .visual {
    font-style: italic;
    color: #64748B;
    font-size: 9pt;
    margin-bottom: 6px;
  }
  .speak {
    color: #0F172A;
    font-size: 10pt;
    line-height: 1.5;
  }
  .speak strong {
    color: #002654;
  }
  .highlight {
    background: #FEF3C7;
    padding: 1px 4px;
    border-radius: 3px;
  }
  .page-break {
    page-break-before: always;
  }
</style>
</head>
<body>

<div class="header">
  <h1>⚖️ CHRONOFACT</h1>
  <div class="tagline">SIMPLE & NATURAL 3-MINUTE DEMO SCRIPT</div>
  <div class="desc">Easy to Speak &bull; Crystal Clear for Judges &bull; Zero Tongue-Twisting Jargon &bull; Exact 3:00 Minutes</div>
</div>

<div class="card">
  <div class="card-title">1. GREETING &amp; THE PROBLEM [0:00 – 0:25]</div>
  <div class="visual">🎬 Screen: Look at the webcam with a confident smile.</div>
  <div class="speak">
    "Hello judges and everyone! My name is <strong>Arpit</strong>, and today I am excited to present <strong>ChronoFact</strong>.<br><br>
    In cyber crime cases, the biggest challenge is not catching the criminal — it is <strong>proving the crime in court</strong>. Suspects fake their alibis, delete their search histories, and defense lawyers easily get digital evidence thrown out by saying: <em>'This log was modified or tampered with.'</em><br><br>
    Under India's new criminal laws, without mathematical proof, cyber criminals easily walk free. That is the exact problem we solve today."
  </div>
</div>

<div class="card">
  <div class="card-title">2. INTRODUCING CHRONOFACT [0:25 – 0:50]</div>
  <div class="visual">🎬 Screen: Show Login Screen (127.0.0.1:8000), then click the green "1-Click Auto Login" button.</div>
  <div class="speak">
    "Meet <strong>ChronoFact</strong> — an intelligent digital forensic workbench designed specifically for the new <strong>Bharatiya Sakshya Adhiniyam, Section 63(4)</strong>.<br><br>
    ChronoFact combines server access logs, mobile cell tower pings, and suspect statements into a single, tamper-proof timeline. It doesn't just store files — it proves the exact second a suspect lied, with zero-tamper certainty."
  </div>
</div>

<div class="card">
  <div class="card-title">3. LIVE DEMO: CASE OVERVIEW &amp; SEALED EXHIBITS [0:50 – 1:30]</div>
  <div class="visual">🎬 Screen: Dashboard opens. Point to "State v. Vikram Malhotra" and the 4 metric cards.</div>
  <div class="speak">
    "Let's log in. Here is our live investigation: <strong>State of NCT of Delhi versus Vikram Malhotra</strong> — a corporate data theft case.<br><br>
    Notice our evidence vault. We have seized exhibits like server logs and phone dumps. Every single file is protected with dual NIST cryptographic hashes. If anyone tampers with even a single letter in these files, the system catches it immediately.<br><br>
    And every action is cryptographically signed under the Lead Examiner's badge."
  </div>
</div>

<div class="page-break"></div>

<div class="card" style="border-left-color: #DC2626;">
  <div class="card-title" style="color: #DC2626;">4. THE AHA! MOMENT: BUSTING THE FAKE ALIBI [1:30 – 2:15]</div>
  <div class="visual">🎬 Screen: Scroll to the Spatial-Temporal Conflict Box (Yellow Alibi vs Green Reality).</div>
  <div class="speak">
    "Now, here is the most powerful feature of ChronoFact: <strong>The Alibi Buster</strong>.<br><br>
    The suspect, Vikram, gave this statement to the police: <em>'Sir, I had high fever, I was asleep at home, and completely offline.'</em><br><br>
    Traditionally, verifying this takes days. But watch what ChronoFact does: Our AI engine cross-references his server login against telecom cell tower pings.<br><br>
    And right here — we see a massive conflict: At the exact time Vikram claimed to be asleep, an authenticated session logged in from IP 192.168.1.105, pinging a tower <span class="highlight"><strong>24.8 kilometers away from his house!</strong></span><br><br>
    His fake alibi is completely busted in less than two seconds."
  </div>
</div>

<div class="card" style="border-left-color: #059669;">
  <div class="card-title" style="color: #059669;">5. COURT CERTIFICATE &amp; LEGAL EXPORT [2:15 – 2:45]</div>
  <div class="visual">🎬 Screen: Click "Generate BSA §63(4) Certificate" button and show the clean legal document.</div>
  <div class="speak">
    "Finally, how do we take this to court?<br><br>
    Under <strong>Section 63(4) of the Bharatiya Sakshya Adhiniyam</strong>, digital evidence requires a mandatory signed certificate.<br><br>
    ChronoFact automatically generates this court certificate with the complete schedule of exhibits, hash digests, and examiner affirmation. With one click, the investigator can export the entire judicial bundle as a ZIP file, ready for the judge."
  </div>
</div>

<div class="card" style="border-left-color: #002654;">
  <div class="card-title">6. IMPACT &amp; CLOSING PUNCHLINE [2:45 – 3:00]</div>
  <div class="visual">🎬 Screen: Look straight into the webcam. Speak slowly with confidence.</div>
  <div class="speak">
    "ChronoFact runs <strong>100% offline</strong> in air-gapped police stations, requires zero cloud costs, and guarantees 100% legal admissibility in court.<br><br>
    Criminals can lie about where they were. But they cannot rewrite the laws of mathematics.<br><br>
    <strong>ChronoFact: Where forensic evidence meets judicial truth. Thank you!</strong>"
  </div>
</div>

</body>
</html>
"""

with open("script_simple_print.html", "w", encoding="utf-8") as f:
    f.write(html_content)

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
pdf_out = os.path.abspath("CHRONOFACT_Simple_Demo_Script.pdf")
html_path = os.path.abspath("script_simple_print.html")

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
    print(f"Simple PDF generated successfully at: {pdf_out} ({os.path.getsize(pdf_out)} bytes)")
else:
    print(f"Simple PDF generation failed: {res.stderr}")
