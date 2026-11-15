import os
import sys
import shutil
import zipfile
from pathlib import Path

SOURCE_DIR = Path(r"C:\Users\Arpit Yadav\.gemini\antigravity\scratch\chronofact")
STAGING_DIR = Path(r"C:\Users\Arpit Yadav\.gemini\antigravity\scratch\ChronoFact_SUTRAM2026_Submission")
ZIP_DEST_LOCAL = SOURCE_DIR / "ChronoFact_SUTRAM2026_Round2_Submission.zip"
ZIP_DEST_DESKTOP = Path(r"C:\Users\Arpit Yadav\OneDrive\Desktop\ChronoFact_SUTRAM2026_Round2_Submission.zip")

# Whitelist / Inclusions
INCLUDE_DIRS = [
    "app",
    "sample_evidence",
    "tests",
    "docs",
    "presentation",
    "models",
]

INCLUDE_FILES = [
    "README.md",
    "SETUP.md",
    "README_PHASES.md",
    "CHANGELOG_PRODUCTION.md",
    "requirements.txt",
    "requirements_prod.txt",
    ".env.example",
    "Dockerfile",
    "docker-compose.yml",
    "run.py",
    "start.bat",
    "START_FULL.bat",
    "phase3_disk.py",
    "phase4_memory.py",
    "phase5_report.py",
    "phase6_ml.py",
    "training_data.csv",
]

EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pyc",
    ".DS_Store",
    "Thumbs.db",
    ".git",
    "venv",
    ".pytest_cache",
]

def clean_and_package():
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[*] Packaging clean source from: {SOURCE_DIR}")
    print(f"[*] Staging directory: {STAGING_DIR}")

    # Copy individual whitelisted files
    for fname in INCLUDE_FILES:
        src = SOURCE_DIR / fname
        if src.exists():
            shutil.copy2(src, STAGING_DIR / fname)
            print(f"  + Copied file: {fname}")

    # Copy whitelisted directories recursively
    for dname in INCLUDE_DIRS:
        src = SOURCE_DIR / dname
        if src.exists() and src.is_dir():
            dst = STAGING_DIR / dname
            shutil.copytree(
                src, 
                dst, 
                ignore=shutil.ignore_patterns(
                    "__pycache__", 
                    "*.pyc", 
                    "*.mp4", 
                    "*.mp3", 
                    "*.pdf", 
                    "*.docx",
                    ".DS_Store"
                )
            )
            print(f"  + Copied dir: {dname}")

    # Copy presentation pptx explicitly into presentation/ inside staging
    staging_pres_dir = STAGING_DIR / "presentation"
    staging_pres_dir.mkdir(parents=True, exist_ok=True)
    pres_file = SOURCE_DIR / "presentation" / "ChronoFact_SUTRAM2026_Round2_Presentation.pptx"
    if pres_file.exists():
        shutil.copy2(pres_file, staging_pres_dir / "ChronoFact_SUTRAM2026_Round2_Presentation.pptx")
        print("  + Copied presentation PPTX")

    speaker_notes = SOURCE_DIR / "presentation" / "PRESENTATION_SPEAKER_NOTES.md"
    if speaker_notes.exists():
        shutil.copy2(speaker_notes, staging_pres_dir / "PRESENTATION_SPEAKER_NOTES.md")
        print("  + Copied speaker notes MD")

    # Create ZIP archive
    print("\n[*] Compressing into ZIP file...")
    if ZIP_DEST_LOCAL.exists():
        ZIP_DEST_LOCAL.unlink()

    with zipfile.ZipFile(ZIP_DEST_LOCAL, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(STAGING_DIR):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(STAGING_DIR)
                # Ensure standard forward slash in zip headers
                zipf.write(full_path, arcname=str(rel_path).replace("\\", "/"))

    size_mb = ZIP_DEST_LOCAL.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Created local ZIP: {ZIP_DEST_LOCAL} ({size_mb:.2f} MB)")

    # Copy to Desktop
    if ZIP_DEST_DESKTOP.parent.exists():
        shutil.copy2(ZIP_DEST_LOCAL, ZIP_DEST_DESKTOP)
        print(f"[SUCCESS] Copied submission ZIP to Desktop: {ZIP_DEST_DESKTOP}")

    # Clean staging directory
    shutil.rmtree(STAGING_DIR)
    print("[*] Staging directory cleaned up.")

if __name__ == "__main__":
    clean_and_package()
