from __future__ import annotations

import json
from pathlib import Path

import pandas as pd



def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)



def save_json(obj, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)



def read_csv(path):
    return pd.read_csv(path)



def write_csv(df, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)



def ensure_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path



def write_manifest(manifest: dict, path):
    save_json(manifest, path)
    return Path(path)



def build_run_manifest(*, run_id: str, runner: str, config: str | None = None, notes=None, extra=None):
    manifest = {
        'run_id': run_id,
        'runner': runner,
        'config': config,
        'notes': list(notes or []),
    }
    if extra:
        manifest.update(extra)
    return manifest
