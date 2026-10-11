import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from app.engines.ml_model import ForensicAnomalyModel

p = Path("models")
m = sorted(p.glob("manifest_*.json"))
print("latest:", m[-1].name)

model = ForensicAnomalyModel(model_path=str(m[-1]))
print("loaded model_id:", model.model_id)
with open(m[-1]) as f:
    man = json.load(f)
print("manifest_id:", man.get("model_id"))
print("model_file:", man.get("model_file"))
