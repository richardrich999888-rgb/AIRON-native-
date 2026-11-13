"""Explicit connected preparation. Runtime worker never calls this module."""
import argparse
import importlib.metadata as metadata
import json
import shutil
import subprocess
import sys
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download
from airon_adaptation.controller import Controller
from airon_adaptation.integrity import file_hash, manifest, write_json
from airon_adaptation.worker import upstream_identity

MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
REVISION = "12fd25f77366fa6b3b4b768ec3050bf629380bac"
FILES = ["README.md", "config.json", "generation_config.json", "merges.txt", "model.safetensors",
         "special_tokens_map.json", "tokenizer.json", "tokenizer_config.json", "vocab.json"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--assets", required=True)
    parser.add_argument("--approve-synthetic-data", action="store_true", required=True)
    parser.add_argument("--local-assets", action="store_true", help="Use approved local assets; never download")
    args = parser.parse_args()
    assets = Path(args.assets).absolute()
    approved = json.loads((Path(__file__).resolve().parents[1]/"model.lock.json").read_text())
    if not args.local_assets:
        assets.mkdir(parents=True, exist_ok=False)
        info = HfApi().model_info(MODEL, revision=REVISION)
        if info.sha != REVISION or info.card_data.get("license") != "apache-2.0":
            raise RuntimeError("Pinned model revision or declared licence differs")
        for name in FILES:
            cached = hf_hub_download(MODEL, name, revision=REVISION)
            shutil.copyfile(cached, assets/name)
    if manifest(assets, model=True) != approved["manifest"]:
        raise RuntimeError("Model assets differ from approved pinned bytes")
    # Model card and declared licence retained; weight/dataset rights remain separate from Soup.
    source = upstream_identity()
    packages = []
    for dist in sorted(metadata.distributions(), key=lambda d: d.metadata["Name"].lower()):
        packages.append({"name": dist.metadata["Name"], "version": dist.version,
                         "license_expression": dist.metadata.get("License-Expression"),
                         "license": dist.metadata.get("License"),
                         "license_classifiers": [c for c in dist.metadata.get_all("Classifier", [])
                                                 if c.startswith("License ::")],
                         "license_files": dist.metadata.get_all("License-File", [])})
    ctl = Controller(args.root)
    try:
        model = ctl.import_base(assets, identifier=MODEL, revision=REVISION, license_id="Apache-2.0")
        ctl.import_knowledge(Path(__file__).resolve().parents[3]/"website/offline/documents.json")
        rows = json.loads((Path(__file__).resolve().parents[1]/"fixtures/enterprise-routing.json").read_text())
        ds = ctl.call("prepare_dataset", {"rows": rows, "authorization": {
            "synthetic": True, "approved_for_training": True, "license": "CC0-1.0"}},
            actor="local-operator", role="operator")
        job = ctl.call("create_training_job", {"base_id": model["id"], "dataset_id": ds["id"],
            "config": {"epochs": 3, "lr": 0.0003, "rank": 8, "seed": 52}},
            actor="local-operator", role="operator")
        write_json(ctl.root/"provisioning.json", {"source": source, "model": model, "dataset": ds, "job": job,
                                                 "dependencies": packages, "assets_manifest": manifest(assets, model=True)})
        (ctl.root/"resolved-requirements.txt").write_text(subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"], text=True))
        print("DEPENDENCY_INVENTORY=" + json.dumps([{"name": p["name"], "version": p["version"],
              "license": p["license_expression"] or (p["license"] or "").split("\n")[0][:160],
              "license_files": p["license_files"]} for p in packages]))
        print(json.dumps({"root": str(ctl.root), "model_id": model["id"], "dataset_id": ds["id"], "job_id": job["id"]}))
    finally:
        ctl.close()


if __name__ == "__main__":
    main()
