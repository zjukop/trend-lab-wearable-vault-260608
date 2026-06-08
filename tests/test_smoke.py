from pathlib import Path

from wearable_vault.main import main


def test_smoke_exports_demo_data(tmp_path: Path) -> None:
    db = tmp_path / "vault.sqlite3"
    out = tmp_path / "exports"

    assert main(["--demo", "--db", str(db), "--export-dir", str(out)]) == 0
    assert db.exists()
    assert (out / "health-vault.json").exists()
    assert (out / "google-fit.csv").exists()
    assert (out / "health-vault.md").read_text(encoding="utf-8").startswith("# Personal Health Vault")
