#!/usr/bin/env python3
"""hypothesis 산출물 ↔ schemas/hypothesis.schema.json 검증 (BIOP02-116).

배경: 산출 스크립트 docstring은 "hypothesis.schema.json 형식"이라 말할 뿐 검증하지 않았다
(리포에 jsonschema 검증 코드 부재). 그래서 스키마 위반이 최소 4주간 미탐지됐다.
이 스크립트가 그 검증을 실물로 만든다 — 산출 시점·CI에서 호출한다.

사용:
  python agents/critic/scripts/validate_hypothesis.py <파일|디렉토리> [...]
  python agents/critic/scripts/validate_hypothesis.py --all   # 알려진 hypothesis 산출물 전수
반환: 위반 있으면 exit 1 (CI blocking 편입용).
"""
import json, sys, glob
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "schemas/hypothesis.schema.json"
# 알려진 hypothesis 산출물 위치(전수 점검 대상; 새 위치 생기면 추가)
KNOWN_GLOBS = [
    "experiments/jhans/biological_plausibility/example_*.json",
    "experiments/*/hypothesis/*.json",
]

def validate_one(path, validator):
    try:
        data = json.loads(Path(path).read_text())
    except Exception as e:
        return [f"JSON 파싱 실패: {e}"]
    return [f"{list(err.path)}: {err.message}" for err in validator.iter_errors(data)]

def main(argv):
    try:
        import jsonschema
    except ImportError:
        print("jsonschema 미설치 — `pip install jsonschema` (spatialpatho env). "
              "CI에선 requirements에 포함할 것.", file=sys.stderr)
        return 2
    schema = json.loads(SCHEMA.read_text())
    validator = jsonschema.Draft202012Validator(schema)

    if not argv or argv == ["--all"]:
        targets = []
        for g in KNOWN_GLOBS:
            targets += glob.glob(str(REPO / g))
    else:
        targets = []
        for a in argv:
            p = Path(a)
            targets += [str(x) for x in p.rglob("*.json")] if p.is_dir() else [a]
    targets = sorted(set(targets))
    if not targets:
        print("검증 대상 없음."); return 0

    fails = 0
    for t in targets:
        errs = validate_one(t, validator)
        rel = Path(t).relative_to(REPO) if str(t).startswith(str(REPO)) else t
        if errs:
            fails += 1
            print(f"❌ {rel}")
            for e in errs:
                print(f"     - {e}")
        else:
            print(f"✅ {rel}")
    print(f"\n{len(targets)-fails}/{len(targets)} 통과.")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
