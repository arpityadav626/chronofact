import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def generate_simple_docx(filename):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    navy = RGBColor(0, 38, 84)
    blue = RGBColor(2, 98, 175)
    dark = RGBColor(30, 41, 59)
    gray = RGBColor(100, 116, 139)

    # Title
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("CHRONOFACT — SIMPLE 3-MINUTE DEMO SCRIPT")
    r.font.bold = True
    r.font.size = Pt(18)
    r.font.color.rgb = navy

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("Easy to speak · Easy for judges to understand · Natural Flow")
    r.font.size = Pt(10)
    r.font.italic = True
    r.font.color.rgb = gray

    sections = [
        ("[0:00 - 0:25] 1. GREETING & THE PROBLEM", 
         "🎬 Visual: Look at the webcam with a confident smile.",
         """\"Hello judges and everyone! My name is Arpit, and today I am excited to present ChronoFact.

In cyber crime cases, the biggest challenge is not catching the criminal — it is proving the crime in court. Suspects fake their alibis, delete their search histories, and defense lawyers easily get digital evidence thrown out by saying: 'This log was modified or tampered with.'

Under India's new criminal laws, without mathematical proof, cyber criminals easily walk free. That is the exact problem we solve today.\""""),

        ("[0:25 - 0:50] 2. INTRODUCING CHRONOFACT",
         "🎬 Visual: Show the Login Screen (127.0.0.1:8000), then click the green '1-Click Auto Login' button.",
         """\"Meet ChronoFact — an intelligent digital forensic workbench designed specifically for the new Bharatiya Sakshya Adhiniyam, Section 63(4).

ChronoFact combines server access logs, telecom mobile tower pings, and suspect statements into a single, tamper-proof timeline. It doesn't just store files — it proves the exact second a suspect lied, with zero-tamper certainty.\""""),

        ("[0:50 - 1:30] 3. LIVE DEMO: CASE OVERVIEW & SEALED EXHIBITS",
         "🎬 Visual: Dashboard loads. Point to 'State v. Vikram Malhotra' and the 4 metric cards.",
         """\"Let's log into the system. Here is our live investigation: State of NCT of Delhi versus Vikram Malhotra — a corporate data theft case.

Notice our evidence vault. We have seized exhibits like server logs and phone dumps. Every single file is protected with dual NIST cryptographic hashes. If anyone tampers with even a single letter in these files, the system catches it immediately.

And every action here is cryptographically signed under the Lead Examiner's badge.\""""),

        ("[1:30 - 2:15] 4. THE AHA! MOMENT: BUSTING THE FAKE ALIBI",
         "🎬 Visual: Scroll down to the Spatial-Temporal Conflict Box (Yellow Alibi vs Green Reality).",
         """\"Now, here is the most powerful feature of ChronoFact: The Alibi Buster.

The suspect, Vikram, gave this statement to the police: 'Sir, I had high fever, I was asleep at home, and completely offline.'

Traditionally, verifying this takes days. But watch what ChronoFact does: Our AI engine cross-references his server login against telecom cell tower pings.

And right here — we see a massive conflict: At the exact time Vikram claimed to be asleep, an authenticated session logged in from IP 192.168.1.105, pinging a tower 24.8 kilometers away from his house! 

His fake alibi is completely busted in less than two seconds.\""""),

        ("[2:15 - 2:45] 5. COURT CERTIFICATE & LEGAL EXPORT",
         "🎬 Visual: Click 'Generate BSA §63(4) Certificate' and show the clean legal document.",
         """\"Finally, how do we take this to court?

Under Section 63(4) of the Bharatiya Sakshya Adhiniyam, digital evidence requires a mandatory signed certificate. 

ChronoFact automatically generates this court certificate with the complete schedule of exhibits, hash digests, and examiner affirmation. With one click, the investigator can export the entire judicial bundle as a ZIP file, ready for the judge.\""""),

        ("[2:45 - 3:00] 6. IMPACT & CLOSING PUNCHLINE",
         "🎬 Visual: Look straight into the webcam. Speak slowly with confidence.",
         """\"ChronoFact runs 100% offline in air-gapped police stations, requires zero cloud costs, and guarantees 100% legal admissibility in court.

Criminals can lie about where they were. But they cannot rewrite the laws of mathematics.

ChronoFact: Where forensic evidence meets judicial truth. Thank you!\"""")
    ]

    for title, vis, speech in sections:
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(2)
        r = h.add_run(title)
        r.font.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = blue

        p_v = doc.add_paragraph()
        p_v.paragraph_format.space_after = Pt(3)
        r = p_v.add_run(vis)
        r.font.size = Pt(9)
        r.font.italic = True
        r.font.color.rgb = gray

        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_after = Pt(6)
        r = p_s.add_run(speech)
        r.font.size = Pt(10)
        r.font.color.rgb = dark

    doc.save(filename)
    print(f"Simple DOCX generated at: {filename}")

if __name__ == "__main__":
    generate_simple_docx("CHRONOFACT_Simple_Demo_Script.docx")
