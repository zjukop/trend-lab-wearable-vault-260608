from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class HealthSample:
    timestamp: str
    metric: str
    value: float
    unit: str
    source: str = "demo-ble-heart-rate"


class DeviceAdapter:
    """Small interface for future BLE/community device adapters."""

    name = "base"

    def read_samples(self) -> list[HealthSample]:
        raise NotImplementedError


class DemoHeartRateAdapter(DeviceAdapter):
    name = "demo-ble-heart-rate"

    def read_samples(self) -> list[HealthSample]:
        now = datetime.now(UTC).replace(microsecond=0).isoformat()
        return [
            HealthSample(now, "heart_rate", 62, "bpm", self.name),
            HealthSample(now, "hrv", 48, "ms", self.name),
            HealthSample(now, "sleep_score", 86, "score", self.name),
        ]


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS samples (
                timestamp TEXT NOT NULL,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                source TEXT NOT NULL
            )
            """
        )


def save_samples(db_path: Path, samples: list[HealthSample]) -> None:
    init_db(db_path)
    with sqlite3.connect(db_path) as con:
        con.executemany(
            "INSERT INTO samples VALUES (?, ?, ?, ?, ?)",
            [(s.timestamp, s.metric, s.value, s.unit, s.source) for s in samples],
        )


def load_samples(db_path: Path) -> list[HealthSample]:
    init_db(db_path)
    with sqlite3.connect(db_path) as con:
        rows = con.execute(
            "SELECT timestamp, metric, value, unit, source FROM samples ORDER BY timestamp"
        ).fetchall()
    return [HealthSample(*row) for row in rows]


def export_samples(samples: list[HealthSample], export_dir: Path) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)
    rows = [asdict(s) for s in samples]

    (export_dir / "health-vault.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")

    with (export_dir / "google-fit.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "metric", "value", "unit", "source"])
        writer.writeheader()
        writer.writerows(rows)

    lines = ["# Personal Health Vault", ""]
    lines += [f"- {s.timestamp}: {s.metric} = {s.value:g} {s.unit} ({s.source})" for s in samples]
    (export_dir / "health-vault.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local-first wearable health data vault")
    parser.add_argument("--db", type=Path, default=Path(".wearable-vault/vault.sqlite3"))
    parser.add_argument("--export-dir", type=Path, default=Path("exports"))
    parser.add_argument("--demo", action="store_true", help="load demo wearable samples")
    args = parser.parse_args(argv)

    if args.demo:
        save_samples(args.db, DemoHeartRateAdapter().read_samples())

    samples = load_samples(args.db)
    export_samples(samples, args.export_dir)
    print(f"exported {len(samples)} samples to {args.export_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
