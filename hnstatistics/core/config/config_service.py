import json
from pathlib import Path

from hnstatistics.core.config.app_config import AppConfig

class ConfigService:
    def __init__(self, config_path: Path):
        self.config_path = config_path
    
    def load(self) -> AppConfig:
        if not self.config_path.exists():
            config = AppConfig()
            self.save(config)
            return config
        with self.config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return AppConfig(**data)
    
    def save(self, config: AppConfig):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(config.__dict__, f, indent=2, ensure_ascii=False)