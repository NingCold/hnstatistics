from pathlib import Path

from hnstatistics.core.config.app_config import AppConfig

APP_ROOT = Path(__file__).resolve().parent.parent.parent

def get_default_save_dir(config: AppConfig) -> Path:
    if config.default_save_dir:
        return Path(config.default_save_dir)
    return APP_ROOT / "data"

def ensure_dir(path: Path) -> Path:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return Path.home()
    return path