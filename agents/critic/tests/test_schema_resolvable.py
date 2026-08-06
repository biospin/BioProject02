"""스키마 $ref 해석 회귀 테스트 (BIOP02-116).

**이 테스트가 막는 것:** 스키마의 `$id` 가 상대경로(`schemas/x.schema.json`)면,
내부 `#/$defs/...` 참조를 해석할 때 base URI 와 합쳐져 `schemas/schemas/x.schema.json`
이라는 없는 경로가 만들어지고 `RefResolutionError` 로 **검증기가 터진다**.

터지는 시점이 늦다는 게 고약하다 — `$ref` 는 **지연 해석**이라 빈 인스턴스나
`$defs` 를 안 타는 인스턴스로는 통과한다. 실제 산출물을 넣어야 드러난다.
그래서 이 테스트는 **$defs 를 실제로 타는 인스턴스**로 검증한다.

배경: BIOP02-116 은 "스키마 형식이라 주장만 하고 검증하는 코드가 없다"였다.
검증 코드가 생긴 뒤에도 이 버그 때문에 **한 번도 돌지 못했다**. 문서에만 있는
보장이 코드에만 있는 보장으로 바뀌었을 뿐이었다.

Run:
    python3 agents/critic/tests/test_schema_resolvable.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = ROOT / "schemas"

# $defs 를 실제로 타도록 만든 최소 인스턴스. 값이 맞을 필요는 없다 —
# 검증이 **실행되는지**(터지지 않는지)만 본다.
PROBES = {
    "hypothesis.schema.json": {
        "phenotype": {"predictions": {"er_status": {"label": "Positive", "prob_positive": 0.9}}}
    },
    "critic_report.schema.json": {
        "checks": [{"name": "data_leakage", "status": "pass"}],
        "checklist": {"data_leakage": {"status": "pass"}},
    },
    "cv_registry.schema.json": {"entry_id": "probe"},
}


def main():
    try:
        import jsonschema
    except ImportError:
        print("SKIP: jsonschema 미설치")
        return 0

    schemas = sorted(SCHEMA_DIR.glob("*.schema.json"))
    if not schemas:
        print(f"FAIL: {SCHEMA_DIR} 에 스키마가 없습니다")
        return 1

    fails = []
    for sp in schemas:
        d = json.loads(sp.read_text())
        sid = d.get("$id")

        # ① $id 가 있다면 절대 URI 여야 한다(상대경로 금지).
        if sid is not None and ":" not in sid.split("/")[0]:
            print(f"  [FAIL] {sp.name}: $id 가 상대경로입니다 — {sid!r}\n"
                  f"         → urn:... 또는 https://... 같은 절대 URI 로 두십시오.")
            fails.append(sp.name)
            continue

        # ② $defs 를 타는 인스턴스로 실제 해석이 되는지.
        probe = PROBES.get(sp.name, {})
        try:
            list(jsonschema.Draft202012Validator(d).iter_errors(probe))
            print(f"  [OK ] {sp.name}: $id={sid!r} · $ref 해석 정상")
        except Exception as e:  # RefResolutionError 등
            print(f"  [FAIL] {sp.name}: 검증 실행 불가 — {type(e).__name__}: {str(e)[:90]}")
            fails.append(sp.name)

    print(f"\n결과: {len(schemas) - len(fails)}/{len(schemas)} 통과")
    if fails:
        print("실패:", ", ".join(fails))
        return 1
    return 0


def test_schema_resolvable():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
