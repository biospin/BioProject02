"""
Validate the cross-validation registry (BIOP02-57) before committing/sharing.

Checks each JSONL entry against schemas/cv_registry.schema.json. Uses the
`jsonschema` package when available; otherwise falls back to essential
stdlib-only checks (required fields, enums, entry_id pattern, Owner!=Reviewer,
duplicate entry_id, claim_level, pass-only sharing rule).

Run:
    python experiments/registry/validate_registry.py \
      --registry experiments/registry/cross_validation_registry.jsonl \
      --schema schemas/cv_registry.schema.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ENTRY_ID_RE = re.compile(r"^cv-[0-9]{8}-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")


def _read_jsonl(path: Path) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"line {i}: invalid JSON: {exc}")
        if not isinstance(obj, dict):
            raise SystemExit(f"line {i}: entry must be a JSON object")
        rows.append((i, obj))
    return rows


def _fallback_check(entry: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Essential checks when the jsonschema package is unavailable."""
    errs: list[str] = []
    for field in schema.get("required", []):
        if field not in entry:
            errs.append(f"missing required field: {field}")

    eid = entry.get("entry_id", "")
    if eid and not ENTRY_ID_RE.match(eid):
        errs.append(f"entry_id does not match cv-<YYYYMMDD>-<endpoint>-<embedding>-<model>: {eid!r}")

    commit = entry.get("commit_hash", "")
    if commit and not COMMIT_RE.match(str(commit)):
        errs.append(f"commit_hash not a git sha: {commit!r}")

    props = schema.get("properties", {})
    for field in ("endpoint", "embedding_model", "critic_status"):
        allowed = props.get(field, {}).get("enum")
        if allowed and entry.get(field) not in allowed:
            errs.append(f"{field}={entry.get(field)!r} not in {allowed}")

    if entry.get("claim_level") != "hypothesis_only":
        errs.append("claim_level must be 'hypothesis_only'")

    return errs


def _cross_field_check(entry: dict[str, Any]) -> list[str]:
    """Governance rules not expressible in JSON Schema — enforced in every mode."""
    errs: list[str] = []
    owner, reviewer = entry.get("owner"), entry.get("reviewer")
    if reviewer and owner == reviewer:
        errs.append(f"Owner != Reviewer violated (both {owner!r})")
    return errs


def validate(registry: Path, schema_path: Path) -> int:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    rows = _read_jsonl(registry)

    try:
        import jsonschema  # type: ignore

        validator = jsonschema.Draft202012Validator(schema)
        mode = "jsonschema"
    except Exception:
        validator = None
        mode = "fallback (jsonschema 미설치 — 핵심 항목만 검사)"

    total_errors = 0
    seen_ids: dict[str, int] = {}

    for line_no, entry in rows:
        errs: list[str] = []
        if validator is not None:
            errs = [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in validator.iter_errors(entry)]
        else:
            errs = _fallback_check(entry, schema)

        errs += _cross_field_check(entry)

        eid = entry.get("entry_id")
        if eid in seen_ids:
            errs.append(f"duplicate entry_id {eid!r} (first at line {seen_ids[eid]})")
        elif isinstance(eid, str):
            seen_ids[eid] = line_no

        if errs:
            total_errors += len(errs)
            print(f"[FAIL] line {line_no} ({eid or '?'}):")
            for e in errs:
                print(f"    - {e}")
        else:
            status = entry.get("critic_status")
            flag = "" if status == "pass" else f"  (critic_status={status} → 공유 불가)"
            print(f"[OK]   line {line_no}: {eid}{flag}")

    print(f"\nmode={mode}  entries={len(rows)}  errors={total_errors}")
    return 0 if total_errors == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the cross-validation registry JSONL")
    parser.add_argument("--registry", default="experiments/registry/cross_validation_registry.jsonl")
    parser.add_argument("--schema", default="schemas/cv_registry.schema.json")
    args = parser.parse_args()
    raise SystemExit(validate(Path(args.registry), Path(args.schema)))


if __name__ == "__main__":
    main()
