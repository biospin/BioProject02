"""
BIOP02-59 — Biological plausibility check (Critic #5).

sjpark의 phenotype 예측(ER/PR/HER2) + jhans draft rule(endocrine_rule_draft.py)을
연결해 hypothesis.schema.json 형식 출력을 만들고, 최소 타당성 점검을 수행한다.

BIOP02-60(jhans) 완료 — endocrine_rule.py v1.0 정식 연결.
   rationale은 BIOP02-52 consistency_scores.csv 실측 Spearman ρ 기반 confidence 포함.

점검 항목:
  1. claim_level == "hypothesis_only" 강제
  2. 금지 표현 스캔 (personalized therapy, ICI/pembrolizumab, DRP framing)
  3. phenotype 예측과 drug_class 매핑의 방향성 일치 (예: HER2+인데 anti-HER2가
     추천 목록에 없으면 불일치로 표시)

Run:
    python agents/modeling/scripts/biological_plausibility_check.py \
        --slide_id TCGA-EXAMPLE \
        --er Positive --pr Positive --her2 Negative --pam50 LumA \
        --out experiments/sjpark/biological_plausibility/example.json
"""

import argparse
import datetime
import json
import subprocess
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from therapeutic_evidence.rules import endocrine_rule, check_forbidden_phrases


def get_git_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def plausibility_check(er, pr, her2, hypotheses):
    """phenotype과 drug_class 방향성이 맞는지 최소 검증."""
    issues = []
    drug_classes = " ".join(h["drug_class"].lower() for h in hypotheses)

    her2_pos = her2.strip().lower() == "positive"
    er_pos = er.strip().lower() == "positive"
    pr_pos = pr.strip().lower() == "positive"

    if her2_pos and "anti-her2" not in drug_classes:
        issues.append("HER2 양성인데 anti-HER2 계열이 추천 목록에 없음")
    if not her2_pos and "anti-her2" in drug_classes:
        issues.append("HER2 음성인데 anti-HER2 계열이 추천됨 (방향성 불일치)")
    if (er_pos or pr_pos) and "endocrine" not in drug_classes:
        issues.append("ER/PR 양성인데 endocrine therapy가 추천 목록에 없음")
    if not er_pos and not pr_pos and not her2_pos and "chemotherapy" not in drug_classes:
        issues.append("Triple-negative인데 chemotherapy가 추천 목록에 없음")

    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slide_id", required=True)
    parser.add_argument("--patient_id", default="")
    parser.add_argument("--cohort", default="TCGA-BRCA")
    parser.add_argument("--er", required=True)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--her2", required=True)
    parser.add_argument("--pam50", default=None)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    hypotheses = endocrine_rule(args.er, args.pr, args.her2, args.pam50)

    all_text = json.dumps(hypotheses, ensure_ascii=False)
    forbidden = check_forbidden_phrases(all_text)

    direction_issues = plausibility_check(args.er, args.pr, args.her2, hypotheses)

    output = {
        "schema_version": "0.1",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "commit_hash": get_git_hash(),
        "slide": {
            "slide_id": args.slide_id,
            "patient_id": args.patient_id or args.slide_id.split("-01Z")[0],
            "cohort": args.cohort,
        },
        "phenotype": {
            "model": "SlideMLP/CLAM-SB (BIOP02-39/46/53)",
            "predictions": {
                "er_status": args.er,
                "pr_status": args.pr,
                "her2_status": args.her2,
                "pam50": args.pam50,
            },
        },
        "hypothesis": hypotheses,
        "claim_level": "hypothesis_only",
        "critic_status": "pending",
        "critic_5_biological_plausibility": {
            "status": "caution" if (forbidden or direction_issues) else "pass_draft",
            "forbidden_phrase_violations": forbidden,
            "direction_consistency_issues": direction_issues,
            "note": "BIOP02-60(jhans) 완료 전 draft 검증. 정식 DepMap/GDSC 연결 후 재검증 필요.",
        },
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
