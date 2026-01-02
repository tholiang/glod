import json
from pathlib import Path


class App:
    """
    Application configuration that persists allowed directories.
    
    Allowed directories are stored both in memory and in a JSON file
    so they survive server restarts.
    """
    
    def __init__(self, config_file: Path | None = None):
        self._allowed_paths = []
        # Use .glod_config in home directory if not specified
        self.config_file = config_file or Path.home() / ".glod_config"
        self._load_from_disk()
    
    def _load_from_disk(self) -> None:
        """Load allowed paths from the config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    paths = data.get("allowed_dirs", [])
                    self._allowed_paths = [Path(p) for p in paths if Path(p).exists()]
                    # Remove non-existent paths from disk
                    self._save_to_disk()
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_file}: {e}")
                self._allowed_paths = []
    
    def _save_to_disk(self) -> None:
        """Save allowed paths to the config file"""
        try:
            # Ensure parent directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "allowed_dirs": [str(p) for p in self._allowed_paths]
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config to {self.config_file}: {e}")
    
    def allow_path(self, path: Path) -> None:
        """Add a path to the allowed list and persist it"""
        if path in self._allowed_paths:
            return
        self._allowed_paths.append(path)
        self._save_to_disk()

    def get_allowed_paths(self) -> list[Path]:
        """Get all allowed paths"""
        return self._allowed_paths

    def can_access(self, path: Path) -> bool:
        """Check if a path is allowed"""
        for allowed_path in self._allowed_paths:
            if path.is_relative_to(allowed_path):
                return True
        return False


# Global app instance
_app_instance = None

def get_app() -> App:
    """Get or create the global app instance"""
    global _app_instance
    if _app_instance is None:
        _app_instance = App()
    return _app_instance

def set_app(app: App) -> None:
    """Set the global app instance"""
    global _app_instance
    _app_instance = app

