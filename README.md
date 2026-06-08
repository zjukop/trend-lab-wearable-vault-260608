# Wearable Vault

Local-first health data exporter for wearable data ownership.

This starter repo provides a tiny runnable core for:

- local SQLite storage
- CSV/JSON/Markdown exports
- a simple device adapter interface
- no cloud, no account, no subscription

## Requirements

Python 3.11+

## Install

```bash
pip install -e .
```

## Run

Create demo data and export it:

```bash
wearable-vault --demo --export-dir exports
```

Or with Python:

```bash
python -m wearable_vault.main --demo
```

## What this is not yet

This is a minimal starter, not a full BLE client or encrypted vault. The next steps are adding BLE adapters, SQLCipher/encryption support, FIT/TCX exporters, and dashboard rendering.
