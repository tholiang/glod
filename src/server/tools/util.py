from pathlib import Path

from server.app import get_app

def _check_access(filepath: str) -> bool:
    """Check if the app allows access to this filepath"""
    app = get_app()
    try:
        path = Path(filepath).resolve()
        return app.can_access(path)
    except Exception:
        return False