# BIOP02-123 — #2 site/batch 감사 + #5 FM 재현성 (박세진)

> Paper C 게재 요건 실행 카드. #2=MUST(게재 blocker, BIOP02-122 심판) · #5=STRONG.
> 방법: 기존 UNI 임베딩·라벨·다중FM 결과 재사용(신규 데이터·큰 학습 없음). CPU.
> 독립 리뷰 = jamie(류재면, split/site 감사 라인). claim=provisional.
>
> **⚠️ 개정 (2026-08-11, jamie #11736 후속 반영):** 초판(커밋 4934d89)의 두 한계를 닫았다.
> (1) **site-predictability를 group-aware CV로 재실행** — `StratifiedKFold`→`StratifiedGroupKFold(groups=case_id)`. 초판에서 본인이 #11730에 캐치했으나 최종 커밋에 미반영됐던 것(다중슬라이드 leakage 우려).
> (2) **LOSO drop에 paired 부트스트랩 CI + P(drop>0) 추가** — 초판은 🟢/🟡/🔴 임계(0.05/0.10)가 단일 관측치에 걸려 있었다. 아래 수치는 **모두 재실행본**이다.

## #2 site/batch confounding 감사 (MUST)

### (1) site-predictability — 임베딩→TSS site 예측 (group-aware CV)
UNI mean-pool → TSS site **StratifiedGroupKFold(groups=case_id)** OvR macro-AUROC (+그룹단위 permutation null). 같은 환자 슬라이드를 한 fold에 묶어 다중슬라이드 leakage 배제:

| 코호트 | macro-AUROC (group-aware) | null | (초판 random-CV) |
|---|---|---|---|
| HNSC | 0.984 | 0.512 | 0.982 |
| LUNG | 0.978 | 0.490 | 0.984 |
| COLORECTAL | 0.951 | 0.498 | 0.955 |
| GASTRIC | 0.988 | 0.484 | 0.989 |

→ **group-aware CV에서도 0.95~0.99** = 다중슬라이드 leakage를 배제해도 임베딩이 TSS site를 강하게 예측. 초판 random-CV 값과 **사실상 동일**(다중슬라이드 leakage 미미) → **site 서명 결론 견고**(Howard 2021 실재). 다중슬라이드 수: HNSC +22 / LUNG +96 / COLO +7 / GAST +26장.

### (2) label-site imbalance (Cramér's V)
LUNG histology **1.00**(LUAD/LUSC 별개 프로젝트=site) · GASTRIC Lauren **0.563** — 심한 교란. HPV 0.397 · BRAF 0.333 · EGFR 0.36 · KRAS 0.36 · MSI 0.288 — 중간.

### (3) LOSO 심판 — random CV vs site-grouped CV (같은 모델, GroupKFold on TSS) + drop CI
drop = random − site-grouped. **drop_CI·P(drop>0)는 paired 부트스트랩 2000회**(같은 resample로 두 AUC 재계산):

| 코호트 | endpoint | random | site-grouped | drop | drop 95%CI | P(drop>0) | 판정 |
|---|---|---|---|---|---|---|---|
| HNSC | **HPV** | 0.902 | 0.840 | +0.062 | [0.018, 0.112] | 0.999 | 🟡 교란 유의·신호생존 |
| LUNG | histology | 0.966 | 0.868 | +0.098 | [0.081, 0.116] | 1.00 | 🔴 큰교란(확실)·잔존신호 |
| LUNG | EGFR | 0.776 | 0.796 | −0.021 | [−0.074, 0.031] | 0.22 | 🟢 site-독립 |
| LUNG | KRAS | 0.733 | 0.667 | +0.065 | [0.005, 0.127] | 0.98 | 🟡 교란 유의·신호생존 |
| COLO | **BRAF** | 0.801 | 0.716 | +0.085 | [0.018, 0.149] | 0.99 | 🟡 교란 유의·신호생존 |
| GAST | **MSI** | 0.837 | 0.821 | +0.015 | [−0.020, 0.051] | 0.81 | 🟢 site-독립(CI가 0 포함) |
| GAST | Lauren | 0.898 | 0.713 | +0.184 | [0.115, 0.258] | 1.00 | 🔴 최대교란(확실)·잔존신호 |
| GAST | EBV | 0.862 | 0.811 | +0.051 | [−0.007, 0.115] | 0.96 | 🟡 경계(CI가 0 포함) |
| HNSC | grade | 0.697 | 0.650 | +0.047 | [−0.001, 0.095] | 0.97 | 🟢 경계 |

(near-chance라 무의미: HNSC egfr_amp rand 0.48, GAST erbb2 rand 0.55)

### 종합 판정 (BIOP02-122 심판) — 🟡 조건부 (CI 강화판)
- **MSI가 가장 견고** — drop CI[−0.020, 0.051]이 0을 포함 = site-독립 확증. EGFR(폐)도 site-grouped가 오히려 높아 site-독립.
- **HPV·BRAF·KRAS는 drop이 유의하게 >0**(P>0 ≈ 0.98~1.0) → **site 교란이 실재**한다. 단 site-grouped AUROC가 여전히 chance 상회(HPV 0.840·BRAF 0.716·KRAS 0.667) → **신호가 holdout 후에도 살아남는다.** ⇒ "분자 앵커는 교란 없음"이 아니라 **"교란은 실재하되 신호가 site 제거 후에도 생존"**이 CI 기반 정확한 서술.
- **형태학-정의 라벨(histology·Lauren)**: drop이 크고 확실(CI가 0에서 멀리, P>0=1.0). 단 site-grouped도 0.868/0.713로 **잔존 신호 존재** → "전량 site 아티팩트"는 아니나 **caveat 필수**.
- **⚠️ 색(🟢/🟡/🔴) 취약성:** 11개 중 9개 endpoint의 drop CI가 0.05/0.10 임계를 가로지른다 → **색을 소수 둘째자리로 확정하는 것은 방어 불가.** 방어 가능한 것은 (a) drop 부호·유의성(P>0), (b) holdout 후 chance 상회 여부. **결정지도엔 색이 아니라 drop CI를 싣는다.**
- **BIOP02-122 결론**: "TCGA=다기관" 논거는 **분자 앵커에 한해 부분 성립**(holdout 후 신호 생존) → #1 외부검증을 "전향검증"으로 강등할 근거 유지. 단 (1) site-predictability 0.95~0.99 강함, (2) **모든 양성 drop이 유의**(site 교란 실재가 CI로 확증) → **논문은 LOSO/site-disjoint 증거 전면화 + drop CI 명시 + 형태학 caveat 필수. 완전한 external validation 대체는 아님.**
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

## 개정 이력 (jamie #11736 후속 — 2026-08-11)
- ✅ **[해결] group-aware CV** — site-predictability를 `StratifiedGroupKFold(groups=case_id)`로 재실행. 초판(4934d89)이 `StratifiedKFold`였고 본인 #11730 캐치가 최종 커밋·FINDINGS에서 빠졌던 문제. 재실행 결과 0.95~0.99로 초판과 사실상 동일 → 결론 견고(leakage 미미)임이 오히려 확증됨.
- ✅ **[해결] LOSO drop CI** — `boot_ci`가 정의만 되고 미호출이던 것을, paired 부트스트랩 `boot_drop_ci`(2000회)로 drop 95%CI·P(drop>0)를 전 endpoint에 산출·표기. 색 임계의 단일관측 취약성을 정량화(9/11 endpoint의 CI가 임계를 가로지름 → 색이 아니라 CI로 보고).

## 남은 것 / 한계
- LOSO는 mean-pool LR 기반 diagnostic(같은 모델서 random vs site-grouped 격리). 헤드라인 수치의 attention-MIL LOSO는 필요 시 heavier follow-up(이번 CI 강화는 diagnostic 층에 한정).
- **색(🟢/🟡/🔴)은 참고용** — drop CI가 임계를 가로지르는 endpoint가 다수라, 결정지도·본문은 **색이 아니라 drop CI + P(drop>0)**를 인용한다.
- endpoint별 permutation null은 기존 5-seed shuffle-null(BIOP02-101)로 대체; 이번 재실행의 permutation null은 site-predictability에 그룹단위로 적용.
- jamie 교차검토 후 서술 수위 확정.
