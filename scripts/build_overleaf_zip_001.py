#!/usr/bin/env python3
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
DIST = ROOT / "dist"
OUT_ZIP = DIST / "native_local_cell_provenance_overleaf.zip"
OUT_JSON = ROOT / "artifacts/json/overleaf_zip_build_001.v1.json"
OUT_NOTE = ROOT / "notes/overleaf_zip_build_001.md"

INCLUDE_SUFFIXES = {".tex", ".bib", ".bst", ".cls", ".sty", ".png", ".jpg", ".jpeg", ".pdf", ".svg"}

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    files = sorted(
        p for p in PAPER.rglob("*")
        if p.is_file() and p.suffix.lower() in INCLUDE_SUFFIXES
    )

    DIST.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    if OUT_ZIP.exists():
        OUT_ZIP.unlink()

    entries = []
    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for path in files:
            arc = path.relative_to(PAPER).as_posix()
            z.write(path, arc)
            entries.append(arc)

    result = {
        "status": "overleaf_zip_build_recorded",
        "zip_path": str(OUT_ZIP),
        "zip_sha256": sha256_file(OUT_ZIP),
        "zip_size_bytes": OUT_ZIP.stat().st_size,
        "file_count": len(entries),
        "entries": entries,
        "contains_main_tex": "main.tex" in entries,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Overleaf ZIP build 001",
        "",
        "Status: " + result["status"],
        "",
        "- zip_path: `" + str(OUT_ZIP) + "`",
        "- zip_sha256: `" + result["zip_sha256"] + "`",
        "- zip_size_bytes: `" + str(result["zip_size_bytes"]) + "`",
        "- file_count: `" + str(result["file_count"]) + "`",
        "- contains_main_tex: `" + str(result["contains_main_tex"]) + "`",
        "",
        "## Entries",
        "",
    ]
    for e in entries:
        lines.append("- `" + e + "`")
    OUT_NOTE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("wrote", OUT_ZIP)
    print("wrote", OUT_JSON)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("zip_sha256", result["zip_sha256"])
    print("file_count", result["file_count"])

if __name__ == "__main__":
    main()
