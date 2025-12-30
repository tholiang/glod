from server.app import App
from pathlib import Path

def test_basic_valid_access():
    app = App()
    app.allow_path(Path("etc/blah"))
    assert app.can_access(Path("etc/blah"))

def test_subdir_valid_access():
    app = App()
    app.allow_path(Path("etc/blah"))
    assert app.can_access(Path("etc/blah/blah.txt"))

def test_invalid_access():
    app = App()
    app.allow_path(Path("etc/blah"))
    assert not app.can_access(Path("etc/blah2"))