"""启动阶段数据库迁移策略测试。"""

from __future__ import annotations

import logging

from backend.bootstrap import flask_factory


def test_startup_database_prefers_alembic(monkeypatch):
    """应优先执行 Alembic 升级。"""
    calls: list[str] = []

    def _fake_upgrade(revision: str = "head") -> None:
        calls.append(f"upgrade:{revision}")

    def _fake_create_all() -> None:
        calls.append("create_all")

    monkeypatch.setattr(flask_factory, "upgrade_database_schema", _fake_upgrade)
    monkeypatch.setattr(flask_factory, "init_database_schema", _fake_create_all)

    flask_factory._init_database_on_startup(logging.getLogger("test-startup-db"))

    assert calls == ["upgrade:head"]


def test_startup_database_fallback_to_create_all(monkeypatch):
    """Alembic 失败时应回退基线初始化。"""
    calls: list[str] = []

    def _fake_upgrade(_revision: str = "head") -> None:
        calls.append("upgrade")
        raise RuntimeError("upgrade failed")

    def _fake_create_all() -> None:
        calls.append("create_all")

    monkeypatch.setattr(flask_factory, "upgrade_database_schema", _fake_upgrade)
    monkeypatch.setattr(flask_factory, "init_database_schema", _fake_create_all)

    flask_factory._init_database_on_startup(logging.getLogger("test-startup-db-fallback"))

    assert calls == ["upgrade", "create_all"]
