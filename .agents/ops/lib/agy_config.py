"""Local CLI discovery; no tennis-lab runner dependency."""
import shutil
from pathlib import Path

DEFAULT_AGY = Path(shutil.which("agy") or Path.home() / ".local/bin/agy")
MODEL_LABELS = {"gemini-4-hydrogen-high": "Gemini 4 Hydrogen (High)"}
