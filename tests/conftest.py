import pytest

@pytest.fixture(autouse=True)
def isolated_audit_db(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'audit.sqlite3'))
    monkeypatch.setenv('POLICY_MODE', 'local')
    monkeypatch.setenv('ENABLE_STRANDS', 'false')
