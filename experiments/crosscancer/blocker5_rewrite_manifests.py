#!/usr/bin/env python3
"""BLOCKER-5 remediation: manifest embedding_path를 개인홈 → /workspace 공유경로로 재작성.
복사(rsync) 완료 후 실행. 각 새 경로의 실제 존재를 검증하고, 하나라도 없으면 그 암종은 중단(원본 보존).
"""
import csv, os, sys, shutil

OLD_BASE = "/home/kkkim/project/BioProject02/experiments/crosscancer"
NEW_BASE = "/workspace/data/cache/biop02/crosscancer"
CANCERS = {
    "LUNG_NSCLC":    "embedding_manifest_lung_nsclc_uni.csv",
    "COLORECTAL":    "embedding_manifest_colorectal_uni.csv",
    "HEADNECK_HNSC": "embedding_manifest_gastric_stad_uni.csv",  # placeholder, fixed below
    "GASTRIC_STAD":  "embedding_manifest_gastric_stad_uni.csv",
}
# 정확한 파일명 매핑
CANCERS = {
    "LUNG_NSCLC":    "embedding_manifest_lung_nsclc_uni.csv",
    "COLORECTAL":    "embedding_manifest_colorectal_uni.csv",
    "HEADNECK_HNSC": "embedding_manifest_headneck_hnsc_uni.csv",
    "GASTRIC_STAD":  "embedding_manifest_gastric_stad_uni.csv",
}

def rewrite(cancer, fname):
    path = f"{OLD_BASE}/{cancer}/full/{fname}"
    if not os.path.exists(path):
        # 파일명 자동탐색(접두 embedding_manifest_)
        d = f"{OLD_BASE}/{cancer}/full"
        cand = [f for f in os.listdir(d) if f.startswith("embedding_manifest_") and f.endswith(".csv")]
        if not cand: print(f"  [{cancer}] manifest 없음"); return False
        path = f"{d}/{cand[0]}"
    rows = list(csv.reader(open(path)))
    hdr = rows[0]; ci = hdr.index("embedding_path")
    old_pref = f"{OLD_BASE}/{cancer}/full/embeddings/"
    new_pref = f"{NEW_BASE}/{cancer}/uni_v1/"
    missing = 0; changed = 0; out = [hdr]
    for r in rows[1:]:
        p = r[ci]
        if p.startswith(old_pref):
            np_ = new_pref + p[len(old_pref):]
        elif p.startswith(new_pref):
            np_ = p  # 이미 이관됨(idempotent)
        else:
            np_ = p  # 예상외 경로 — 건드리지 않음
        if not os.path.exists(np_): missing += 1
        if np_ != p: changed += 1
        r[ci] = np_; out.append(r)
    if missing:
        print(f"  [{cancer}] ❌ 새 경로 {missing}건 미존재 — 재작성 중단(원본 보존). 복사 확인 필요.")
        return False
    # 백업 후 저장
    shutil.copy(path, path + ".prehome_bak")
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(out)
    print(f"  [{cancer}] ✅ {changed}행 재작성, 전 경로 /workspace 존재 검증 OK ({path})")
    return True

ok = all(rewrite(c, f) for c, f in CANCERS.items())
print("=== 전체 성공 ===" if ok else "=== 일부 실패 — 위 로그 확인 ===")
sys.exit(0 if ok else 1)
