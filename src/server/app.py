from pathlib import Path

class App:
    def __init__(self):
        self._allowed_paths = []
    
    def allow_path(self, path: Path) -> None:
        if path in self._allowed_paths:
            return
        self._allowed_paths.append(path)

    def get_allowed_paths(self) -> list[Path]:
        return self._allowed_paths

    def can_access(self, path: Path) -> bool:
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

    global _app_instance
    _app_instance = app

