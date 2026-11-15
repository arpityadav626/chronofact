import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_docx(filename):
    doc = Document()
    
    # Page setup - 0.75 in margins
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    # Styles
    navy = RGBColor(0, 38, 84)      # #002654
    blue = RGBColor(2, 98, 175)     # #0262af
    dark = RGBColor(15, 23, 42)     # #0F172A
    gray = RGBColor(100, 116, 139)  # #64748B
    green = RGBColor(5, 150, 105)   # #059669
    red = RGBColor(220, 38, 38)     # #DC2626
    
    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r = p_title.add_run("⚖️ CHRONOFACT")
    r.font.name = "Arial"
    r.font.size = Pt(24)
    r.font.bold = True
    r.font.color.rgb = navy
    
    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(2)
    r = p_sub.add_run("OFFICIAL 3-MINUTE DEMO VIDEO SCRIPT")
    r.font.name = "Arial"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = blue
    
    # Sub-meta
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(14)
    r = p_meta.add_run("National Judicial Cyber Forensic Intelligence Workbench | BSA 2023 §63(4)\nSetup: OBS Studio (1080p Screen + Corner Webcam) · Mode: Real Presenter (No AI Video)")
    r.font.name = "Arial"
    r.font.size = Pt(9.5)
    r.font.italic = True
    r.font.color.rgb = gray
    
    # Divider line
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(10)
    r = p_div.add_run("―" * 58)
    r.font.color.rgb = RGBColor(203, 213, 225)
    
    # Checklist Header
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(8)
    h1.paragraph_format.space_after = Pt(4)
    r = h1.add_run("📋 PRE-RECORDING CHECKLIST (20 Mins Before)")
    r.font.name = "Arial"
    r.font.size = Pt(12)
    r.font.color.rgb = navy
    
    checklist_items = [
        ("OBS Resolution:", "Browser Source set to Width: 1920, Height: 1080 (Press Ctrl + S to stretch to canvas edge-to-edge)."),
        ("Pre-load Workbench:", "Open http://127.0.0.1:8000 in your browser. Verify credentials examiner / SecurePassMin16Chars! or 1-Click Login works."),
        ("OBS Interact Mode:", "Right-click Browser Source in OBS → Click 'Interact'. This allows live clicking on buttons during recording!"),
        ("Audio & Mic Check:", "Use wired earphones or collar mic. Keep voice meter in OBS green/yellow zone (no red distortion)."),
        ("Webcam Setup:", "Stack 2-3 books under laptop so camera is at eye-level. Face a light source or desk lamp (no bright window behind)."),
        ("Silence Distractions:", "Turn Windows Focus Assist ON (Alarms only). Close WhatsApp, Teams, Discord.")
    ]
    for title, desc in checklist_items:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"☐  {title} ")
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = dark
        r2 = p.add_run(desc)
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = dark

    # Script Timeline Header
    h2 = doc.add_heading(level=1)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r = h2.add_run("⏱️ FULL SHOT-BY-SHOT TIMELINE (3:00 Minutes)")
    r.font.name = "Arial"
    r.font.size = Pt(13)
    r.font.color.rgb = navy

    # Section 1: Hook
    p_sec = doc.add_paragraph()
    p_sec.paragraph_format.space_before = Pt(8)
    p_sec.paragraph_format.space_after = Pt(2)
    r = p_sec.add_run("🔴 [0:00 – 0:20] THE HOOK — Problem Statement")
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = red
    
    p_vis = doc.add_paragraph()
    p_vis.paragraph_format.space_after = Pt(4)
    r = p_vis.add_run("🎬 Visual: Fullscreen Webcam OR Dark Slide with text: 'In Indian courts, over 80% of cyber crime evidence gets dismissed... not because the suspect is innocent, but because evidence lacks mathematical chain-of-custody.'")
    r.font.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = gray
    
    p_speak = doc.add_paragraph()
    p_speak.paragraph_format.space_after = Pt(8)
    r = p_speak.add_run('🎙️ SPEAK (Serious, high impact):\n"Imagine this: A cyber criminal loots ₹50 lakhs or leaks sensitive corporate data at 2 AM.\nPolice catch him. But in court, the defense lawyer claims just one thing: \'Sir, this digital log is doctored. The timestamp is modified. And there is no valid statutory certificate.\'\nUnder the new Bharatiya Sakshya Adhiniyam, 2023, electronic records without mathematical chain-of-custody are instantly rejected.\nThe criminal walks free — not because he didn\'t commit the crime — but because our investigation lacked mathematical legal proof."\n(Pause 1 second — let it sink in)')
    r.font.size = Pt(9.5)
    r.font.color.rgb = dark

    # Section 2: Solution
    p_sec = doc.add_paragraph()
    p_sec.paragraph_format.space_before = Pt(6)
    p_sec.paragraph_format.space_after = Pt(2)
    r = p_sec.add_run("💡 [0:20 – 0:40] THE SOLUTION — Introducing ChronoFact")
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = blue
    
    p_vis = doc.add_paragraph()
    p_vis.paragraph_format.space_after = Pt(4)
    r = p_vis.add_run("🎬 Visual: Switch to Screen Recording (1080p) showing Login Terminal with National Emblem and official GoI portal aesthetics. Webcam in bottom-right corner.")
    r.font.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = gray
    
    p_speak = doc.add_paragraph()
    p_speak.paragraph_format.space_after = Pt(8)
    r = p_speak.add_run('🎙️ SPEAK:\n"Presenting CHRONOFACT — the National Judicial Cyber Forensic Intelligence Workbench, built strictly for Section 63(4) of the Bharatiya Sakshya Adhiniyam, 2023.\nChronoFact fuses multi-source digital evidence — IP server access logs, telecom BTS tower pings, and suspect statements — into an immutable cryptographic timeline.\nIt doesn\'t just store logs. It proves the exact second a suspect lied, with zero-tamper mathematical certainty."')
    r.font.size = Pt(9.5)
    r.font.color.rgb = dark

    # Section 3: Live Demo 1
    p_sec = doc.add_paragraph()
    p_sec.paragraph_format.space_before = Pt(6)
    p_sec.paragraph_format.space_after = Pt(2)
    r = p_sec.add_run("📱 [0:40 – 1:20] LIVE DEMO 1: Forensic Workbench & Exhibit Vault")
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = green

    # Table for Demo 1
    t1 = doc.add_table(rows=6, cols=3)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Step", "Action on Screen (OBS Interact)", "What to Say (Voiceover)"]
    for i, h in enumerate(headers):
        cell = t1.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "0262af")
        set_cell_margins(cell, 80, 80, 100, 100)

    rows_data1 = [
        ("1", "Click green '1-Click Officer Auto-Login' button", '"The examiner authenticates into an air-gapped forensic terminal with role-based cryptographic keys."'),
        ("2", "Dashboard loads: State v. Vikram Malhotra (FIR 204/2026)", '"Immediately, our live judicial case loads: State of NCT of Delhi v. Vikram Malhotra."'),
        ("3", "Click Examiner badge in navbar (Examiner #FE-802 / Vikram)", '"Every investigation is cryptographically bound to the Lead Examiner and Badge ID, auditable at every click."'),
        ("4", "Highlight 4 Metric Cards (Seized Exhibits: 4, NIST Dual Hash: 100%)", '"Look at the evidence vault. Every file is sealed with dual NIST FIPS hashes — SHA-256 plus SHA3-256. If a single bit is touched, the vault alarms immediately."'),
        ("5", "Click 'Switch / Load Case Samples' button", '"ChronoFact comes pre-loaded with multiple real-world forensic samples — from crypto exfiltration to financial fraud."')
    ]
    for row_idx, rdata in enumerate(rows_data1, start=1):
        for col_idx, text in enumerate(rdata):
            cell = t1.cell(row_idx, col_idx)
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, 60, 60, 80, 80)
            if row_idx % 2 == 0:
                set_cell_background(cell, "F8FAFC")

    # Section 4: Live Demo 2
    p_sec = doc.add_paragraph()
    p_sec.paragraph_format.space_before = Pt(10)
    p_sec.paragraph_format.space_after = Pt(2)
    r = p_sec.add_run("🖥️ [1:20 – 2:00] LIVE DEMO 2: AI Anomaly Radar (The Alibi Buster)")
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = navy

    # Table for Demo 2
    t2 = doc.add_table(rows=5, cols=3)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = t2.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "002654")
        set_cell_margins(cell, 80, 80, 100, 100)

    rows_data2 = [
        ("1", "Highlight Suspect Alibi Box (Yellow border)", '"Here is suspect Vikram\'s defense statement: \'Sir, I had high fever, I was asleep in bed and completely offline till morning.\' Traditional investigators struggle to disprove this."'),
        ("2", "Highlight Ground Reality Box (Emerald border)", '"ChronoFact\'s AI Anomaly Engine cross-references server logs against telecom BTS tower records."'),
        ("3", "Hover over +24.8 km Conflict & +5h 28m Time Skew", '"Boom! An undeniable spatial-temporal conflict: At the exact minute Vikram claimed to be asleep, an authenticated session logged in from IP 192.168.1.105, pinging a tower 24.8 km away from his home!"'),
        ("4", "Scroll to Multi-Stream Chronological Timeline", '"Every event from server CSVs, phone dumps, and network streams is chronologically synchronized on a microsecond timeline. His alibi is mathematically obliterated."')
    ]
    for row_idx, rdata in enumerate(rows_data2, start=1):
        for col_idx, text in enumerate(rdata):
            cell = t2.cell(row_idx, col_idx)
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, 60, 60, 80, 80)
            if row_idx % 2 == 0:
                set_cell_background(cell, "F8FAFC")

    # Section 5: Live Demo 3
    p_sec = doc.add_paragraph()
    p_sec.paragraph_format.space_before = Pt(10)
    p_sec.paragraph_format.space_after = Pt(2)
    r = p_sec.add_run("⚖️ [2:00 – 2:30] LIVE DEMO 3: BSA 2023 §63(4) Statutory Certificate & Merkle Vault")
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = blue

    # Table for Demo 3
    t3 = doc.add_table(rows=5, cols=3)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = t3.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "059669")
        set_cell_margins(cell, 80, 80, 100, 100)

    rows_data3 = [
        ("1", "Open Statutory Legal Certificate View / Modal", '"Now comes the judicial game-changer: Under Bharatiya Sakshya Adhiniyam Section 63(4), digital evidence requires a mandatory certificate signed by the examiner."'),
        ("2", "Show pre-filled Schedule of Exhibits & Dual Hashes", '"ChronoFact auto-compiles the entire statutory certificate — Schedule of Exhibits, SHA-256 digests, and custodial affirmation. Zero manual drafting errors."'),
        ("3", "Click 'Inspect Merkle Tree / Master Root'", '"All exhibits are committed to a deterministic Merkle Tree. The Master Root seals all evidence. If defense lawyers question item 2, we provide a single cryptographic inclusion proof."'),
        ("4", "Click 'Export Case Dossier (ZIP)'", '"One tap exports the complete legal dossier — signed certificates, hash manifests, and raw exhibits ready for the magistrate."')
    ]
    for row_idx, rdata in enumerate(rows_data3, start=1):
        for col_idx, text in enumerate(rdata):
            cell = t3.cell(row_idx, col_idx)
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, 60, 60, 80, 80)
            if row_idx % 2 == 0:
                set_cell_background(cell, "F8FAFC")

    # Section 6: Impact
    p_sec = doc.add_paragraph()
    p_sec.paragraph_format.space_before = Pt(10)
    p_sec.paragraph_format.space_after = Pt(2)
    r = p_sec.add_run("🏆 [2:30 – 2:50] IMPACT & WHY WE WIN")
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = navy

    p_speak = doc.add_paragraph()
    p_speak.paragraph_format.space_after = Pt(8)
    r = p_speak.add_run('🎙️ SPEAK:\n"Why does ChronoFact win?\nBecause it bridges the fatal gap between cyber forensics and the Indian Judicial Code.\nPolice officers get instant alibi busting. Public prosecutors get court-admissible certificates. And judges get zero-tamper mathematical truth.\nIt is 100% air-gapped capable, DPDP-compliant, and runs on standard government hardware with ₹0 extra infrastructure cost."')
    r.font.size = Pt(9.5)
    r.font.color.rgb = dark

    # Section 7: Closing
    p_sec = doc.add_paragraph()
    p_sec.paragraph_format.space_before = Pt(6)
    p_sec.paragraph_format.space_after = Pt(2)
    r = p_sec.add_run("🙏 [2:50 – 3:00] CLOSING (The Line They Remember)")
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = red

    p_speak = doc.add_paragraph()
    p_speak.paragraph_format.space_after = Pt(12)
    r = p_speak.add_run('🎙️ SPEAK (Slow down, confident eye contact into camera):\n"Criminals can fake an alibi. They can wipe their browser history.\nBut they cannot rewrite the laws of mathematics.\nChronoFact — Where Forensic Evidence Meets Judicial Truth.\nThank you."')
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.color.rgb = navy

    # Novelty Lines
    h3 = doc.add_heading(level=1)
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(6)
    r = h3.add_run("🧠 JUDGES Q&A — NOVELTY CRACKERS (Memorize These)")
    r.font.name = "Arial"
    r.font.size = Pt(12)
    r.font.color.rgb = navy

    qna = [
        ("Q: BSA 2023 Section 63(4) vs Old Section 65B?", 
         "Section 65B of the Evidence Act was vague regarding device ownership and hashing. BSA Section 63(4) explicitly mandates cryptographic hash preservation, examiner qualification, and schedule-based integrity. ChronoFact is engineered natively for BSA 2023 from Day 1."),
        ("Q: Why use Dual Hashing (SHA-256 + SHA3-512)?", 
         "NIST FIPS standards and modern judicial forensics recommend dual hashing to protect against quantum collision vulnerabilities and provide defense-proof authenticity in high-court appeals."),
        ("Q: What if the internet is down in the police station?", 
         "ChronoFact is 100% offline and air-gapped capable. The dual hashing engine, Merkle tree calculator, and spatial conflict engine run directly in-memory on the local machine with zero external cloud dependencies."),
        ("Q: What stops an investigator from tampering with logs?", 
         "Every ingested exhibit is committed to a deterministic Merkle tree. Modifying even 1 single byte invalidates the root digest, and our built-in forensic test suite immediately triggers an uncatchable Integrity Violation error.")
    ]
    for q, a in qna:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        rq = p.add_run(f"• {q}\n")
        rq.font.bold = True
        rq.font.size = Pt(9.5)
        rq.font.color.rgb = blue
        ra = p.add_run(f"  {a}")
        ra.font.size = Pt(9.5)
        ra.font.color.rgb = dark

    doc.save(filename)
    print(f"DOCX created successfully at: {filename}")

if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "CHRONOFACT_Official_Demo_Script.docx"
    create_docx(out_path)
