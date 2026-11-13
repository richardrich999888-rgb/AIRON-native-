"""Authorised rehearsal through Soup's native loader; frozen evaluation stays separate."""
import json
import os
from pathlib import Path
from .integrity import Rejected


def evaluation_rows(path):
    return [row for row in json.loads(Path(path).read_text()) if row["split"] in {"test", "regression"}]


def training_data_config(root, seed):
    root = Path(root)
    rows = json.loads((root/"records.json").read_text())
    primary = sum(r["split"] == "train" for r in rows)
    replay = sum(r["split"] == "replay" for r in rows)
    if primary < 1 or replay > primary:
        raise Rejected("Invalid approved rehearsal counts")
    cfg = {"train": str(root/"train.jsonl"), "format": "chatml", "val_split": 0.0, "max_length": 256}
    if replay:
        cfg.update(replay=str(root/"replay.jsonl"), replay_ratio=replay/(primary+replay), replay_seed=seed)
    return cfg, {"primary_rows": primary, "replay_rows": replay, "mixed_rows": primary+replay}


def load_training_data(config, expected):
    from soup_cli.data.loader import load_dataset
    previous = Path.cwd()
    # Soup confines replay paths to cwd. Only the worker's approved, read-only
    # dataset directory is selected here; no client-controlled process cwd.
    os.chdir(Path(config.train).parent)
    try:
        data = load_dataset(config)
    finally:
        os.chdir(previous)
    if len(data["train"]) != expected["mixed_rows"]:
        raise Rejected("Native Soup loader omitted or repeated authorised training rows")
    return data
