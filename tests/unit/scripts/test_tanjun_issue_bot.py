from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_bot():
    root = Path(__file__).resolve().parents[3]
    path = root / ".github" / "scripts" / "tanjun_issue_bot.py"
    spec = importlib.util.spec_from_file_location("tanjun_issue_bot", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ai_paths_cannot_escape_checkout(tmp_path, monkeypatch) -> None:
    bot = _load_bot()
    monkeypatch.setattr(bot, "REPO_DIR", tmp_path)

    with pytest.raises(ValueError, match="escapes repository"):
        bot._repo_path("../outside.py")


def test_ai_change_is_written_as_text_inside_checkout(tmp_path, monkeypatch) -> None:
    bot = _load_bot()
    monkeypatch.setattr(bot, "REPO_DIR", tmp_path)

    path = bot._write_change({"path": "nested/file.py", "content": "print('ok')"})

    assert path == (tmp_path / "nested/file.py").resolve()
    assert path.read_text(encoding="utf-8") == "print('ok')"
