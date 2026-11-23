import os
import sys
import shutil
import zipfile
from pathlib import Path

SOURCE_DIR = Path(r"C:\Users\Arpit Yadav\.gemini\antigravity\scratch\chronofact")
STAGING_DIR = Path(r"C:\Users\Arpit Yadav\.gemini\antigravity\scratch\ChronoFact_SUTRAM2026_Submission")
ZIP_DEST_LOCAL = SOURCE_DIR / "ChronoFact_Prototype.zip"
ZIP_DEST_VIDEOS = Path(r"C:\Users\Arpit Yadav\Videos\chronofact\ChronoFact_Prototype.zip")
ZIP_DEST_DESKTOP = Path(r"C:\Users\Arpit Yadav\OneDrive\Desktop\ChronoFact_Prototype.zip")

# Whitelist / Inclusions
INCLUDE_DIRS = [
    "app",
    "assets",
    "sample_evidence",
    "tests",
    "docs",
    "presentation",
    "models",
    "model-runs",
]

INCLUDE_FILES = [
    "ChronoFact_Single_File_Prototype.html",
    "index.html",
    "login.html",
    "app.js",
    "styles.css",
    "README.md",
    "SETUP.md",
    "CHANGELOG.md",
    "README_PHASES.md",
    "CHANGELOG_PRODUCTION.md",
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-extras.txt",
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
    "eval_ml.py",
    "generate_realistic_training_data.py",
    "build_single_file_prototype.py",
    "package_submission.py",
    "training_data.csv",
    "CHRONOFACT_Official_Demo_Script.pdf",
    "ChronoFact_Presentation_CheatSheet.pdf",
    "ChronoFact_System_Flowchart.pdf",
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
                    "*.pptx",
                    "*.ppt",
                    ".DS_Store"
                )
            )
            print(f"  + Copied dir: {dname}")

    # PPTX is excluded per user request (uploaded separately)
    staging_pres_dir = STAGING_DIR / "presentation"
    staging_pres_dir.mkdir(parents=True, exist_ok=True)

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

    # Clean and copy to Videos/chronofact (Ensure ONLY the single ZIP file exists in Videos/chronofact)
    if ZIP_DEST_VIDEOS.parent.exists():
        for item in ZIP_DEST_VIDEOS.parent.iterdir():
            if item.is_file() and item.name != "ChronoFact_Prototype.zip":
                try:
                    item.unlink()
                except Exception as e:
                    print(f"  - Warning removing {item}: {e}")
        shutil.copy2(ZIP_DEST_LOCAL, ZIP_DEST_VIDEOS)
        print(f"[SUCCESS] Cleaned Videos folder and copied single ZIP to Videos: {ZIP_DEST_VIDEOS}")

    # Copy to Desktop
    if ZIP_DEST_DESKTOP.parent.exists():
        shutil.copy2(ZIP_DEST_LOCAL, ZIP_DEST_DESKTOP)
        print(f"[SUCCESS] Copied submission ZIP to Desktop: {ZIP_DEST_DESKTOP}")

    # Clean staging directory
    shutil.rmtree(STAGING_DIR)
    print("[*] Staging directory cleaned up.")

if __name__ == "__main__":
    clean_and_package()
