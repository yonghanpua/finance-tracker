import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent

with open(ROOT / "config.yaml") as f:
    _cfg = yaml.safe_load(f)

EXCEL_PATH = _cfg["paths"]["excel"]
WATCH_DIR = ROOT / _cfg["paths"]["watch_dir"]
LOG_PATH = ROOT / _cfg["paths"]["log"]
DB_DRIVER = _cfg["database"]["driver"]
DB_SERVER = _cfg["database"]["server"]
DB_NAME = _cfg["database"]["database"]