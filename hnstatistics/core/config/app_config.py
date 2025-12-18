from dataclasses import dataclass
from pathlib import Path

@dataclass
class AppConfig:
    font_family: str = "Segoe UI"
    font_size: int = 12
    font_weight: str = "normal"  # "normal" or "bold"
    default_save_dir: str | None = None
    