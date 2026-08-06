# BIOP02-123 — #2 site/batch 감사 + #5 FM 재현성 (박세진)

> Paper C 게재 요건 실행 카드. #2=MUST(게재 blocker, BIOP02-122 심판) · #5=STRONG.
> 방법: 기존 UNI 임베딩·라벨·다중FM 결과 재사용(신규 데이터·큰 학습 없음). CPU.
> 독립 리뷰 = jamie(류재면, split/site 감사 라인). claim=provisional.

## #2 site/batch confounding 감사 (MUST)

### (1) site-predictability — 임베딩→TSS site 예측
UNI mean-pool → TSS site 5-fold CV macro-AUROC (+permutation null):

| 코호트 | macro-AUROC | null |
|---|---|---|
| HNSC | 0.982 | 0.501 |
| LUNG | 0.984 | 0.504 |
| COLORECTAL | 0.955 | 0.500 |
| GASTRIC | 0.989 | 0.494 |

→ **4/4 코호트에서 H&E 임베딩이 TSS site를 0.95~0.99로 예측** = 강한 site 서명(Howard 2021 실재). 기관·스캐너·염색 서명이 임베딩에 대량 인코딩됨.

### (2) label-site imbalance (Cramér's V)
LUNG histology **1.00**(LUAD/LUSC 별개 프로젝트=site) · GASTRIC Lauren **0.563** — 심한 교란. HPV 0.397 · BRAF 0.333 · EGFR 0.36 · KRAS 0.36 · MSI 0.288 — 중간.

### (3) LOSO 심판 — random CV vs site-grouped CV (같은 모델, GroupKFold on TSS)
| 코호트 | endpoint | random | site-grouped | drop | 판정 |
|---|---|---|---|---|---|
| HNSC | **HPV** | 0.903 | 0.841 | +0.062 | 🟡 |
| LUNG | histology | 0.966 | 0.864 | +0.102 | 🔴 |
| LUNG | EGFR | 0.776 | 0.814 | −0.038 | 🟢 |
| LUNG | KRAS | 0.733 | 0.702 | +0.030 | 🟢 |
| COLO | **BRAF** | 0.801 | 0.726 | +0.075 | 🟡 |
| GAST | **MSI** | 0.837 | 0.830 | +0.007 | 🟢 |
| GAST | Lauren | 0.898 | 0.743 | +0.154 | 🔴 |
| GAST | EBV | 0.863 | 0.811 | +0.052 | 🟡 |

(near-chance라 무의미: HNSC egfr_amp 0.48, GAST erbb2 0.55)

### 종합 판정 (BIOP02-122 심판) — 🟡 조건부
- **분자 앵커(HPV·MSI·BRAF·EGFR·KRAS)는 site 빼도 대체로 생존**(🟢/🟡, 잔존 0.70~0.84). MSI 완전 robust, EGFR/KRAS site-독립. → 신호가 대부분 site로 설명되지 않음.
- **형태학-정의 라벨(LUNG histology·GASTRIC Lauren)만 🔴 site-driven** — caveat 필수.
- **BIOP02-122 결론**: "TCGA=다기관" 논거는 **분자 앵커에 한해 부분 성립**(LOSO 생존) → #1 외부검증을 "전향검증"으로 강등할 근거 있음. 단 site-predictability 0.95~0.99이 강하므로 **논문은 LOSO/site-disjoint 증거 전면화 + 형태학 endpoint caveat 필수. 완전한 external validation 대체는 아님.**
- ⚠️ 서술 수위는 jamie 교차검토.

## #5 FM 재현성 formal (STRONG)

기존 다중FM 5-seed real AUROC(BIOP02-101 검증필) 재분석.

### rank stability — endpoint 순서 보존 (UNI vs 신형FM)
| 코호트 | Spearman |
|---|---|
| LUNG | uni↔virchow2 1.0, uni↔uni2h 1.0 |
| HNSC | 1.0, 1.0 |
| GASTRIC | uni↔virchow2 1.0, uni↔uni2h 0.8 |

→ **결정지도 endpoint 순서는 3 FM에서 0.8~1.0으로 안정 = 모델 비의존적**.

### FM-민감 endpoint (FM 간 AUROC 편차>0.05)
Lauren(0.104)·egfr_amp(0.099)·erbb2(0.084)·kras(0.08)·grade(0.069)·ebv(0.068) — **전부 약신호/경계 endpoint**(AUROC~0.5~0.7). 강한 앵커(HPV·MSI·BRAF·histology)는 FM-안정.
→ "지도 cell 색이 FM 따라 바뀌는 endpoint"는 **약신호 칸에 국한** — 결정지도에 FM-불확실로 표기 권장. (BIOP02-101의 HPV Virchow2 5-seed 경계 FAIL도 null 분산 문제이지 신호 부재 아님과 정합.)

## 산출물
experiments/crosscancer/site_audit/: SITE_AUDIT_SUMMARY.json, SITE_AUDIT_VERDICT.json, FM_REPRODUCIBILITY.json, site_audit_*.json(4), loso_*.json(4). 스크립트: site_batch_audit.py, loso_audit.py.

## 남은 것 / 한계
- LOSO는 mean-pool LR 기반 diagnostic(같은 모델서 random vs site-grouped 격리). 헤드라인 수치의 attention-MIL LOSO는 필요 시 heavier follow-up.
- site-stratified permutation null은 site-predictability에 적용(위); endpoint별 permutation은 기존 5-seed shuffle-null(BIOP02-101)로 대체.
- jamie 교차검토 후 서술 수위 확정.
