import sys
import uvicorn
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    print("=" * 60)
    print("Starting CHRONOFACT — Digital Forensic Investigation Workbench")
    print("Serving interactive UI at: http://127.0.0.1:8000")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
