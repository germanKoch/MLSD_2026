"""Download the pinned RCAEval RE2-OB subset into data/raw/rcaeval."""

import hashlib
import json
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi, snapshot_download

REPO_ID = "phamquiluan/RCAEval"
REVISION = "afeacb11bcc94dadfd1c8f483ee4377b2b8b614e"
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "rcaeval"
CASE_FILES = {"metrics.parquet", "logs.parquet", "traces.parquet", "inject_time.txt"}


def main() -> None:
    info = HfApi().dataset_info(REPO_ID, revision=REVISION, files_metadata=True)
    files = {
        item.rfilename: item
        for item in info.siblings
        if item.rfilename.startswith("re2ob_") or item.rfilename == "cases.parquet"
    }
    case_names = {name.split("/")[0] for name in files if "/" in name}
    expected = {f"{case}/{name}" for case in case_names for name in CASE_FILES}
    expected.add("cases.parquet")
    if info.sha != REVISION or len(case_names) != 90 or set(files) != expected:
        raise ValueError("Unexpected revision or RE2-OB file layout")

    size = sum(item.size for item in files.values())
    print(f"Downloading {len(case_names)} cases, {len(files)} files, {size:,} bytes")
    snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        revision=REVISION,
        allow_patterns=sorted(files),
        local_dir=DATA_DIR,
        max_workers=4,
    )

    manifest_files = []
    for name, item in sorted(files.items()):
        path = DATA_DIR / name
        if path.stat().st_size != item.size:
            raise ValueError(f"File size mismatch: {name}")
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if item.lfs and digest != item.lfs.sha256:
            raise ValueError(f"SHA-256 mismatch: {name}")
        manifest_files.append({"path": name, "bytes": item.size, "sha256": digest})

    index = pd.read_parquet(DATA_DIR / "cases.parquet")
    cases = index.loc[index["dataset"].eq("RE2-OB")]
    if len(cases) != 90 or set(cases["case"]) != case_names:
        raise ValueError("The case index does not match the downloaded subset")

    manifest = {
        "repo_id": REPO_ID,
        "revision": REVISION,
        "subset": "RE2-OB",
        "case_count": len(cases),
        "total_bytes": size,
        "files": manifest_files,
    }
    (DATA_DIR / "download_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Verified {len(files)} files in {DATA_DIR}")


if __name__ == "__main__":
    main()
