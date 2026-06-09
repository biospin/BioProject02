# CLAM — Methodology Brief (what we reuse vs. compare)

## BIOP02 파이프라인 안에서의 위치
```
H&E WSI
  └─[REUSE/PARALLEL] tissue segmentation (Otsu) + fixed-mag tiling (256×256@20×)   ← CLAM 선례
        └─ FM tile embedding (UNI/CONCH; CLAM toolkit가 encoder swap 지원)
              └─[COMPARE] slide-level aggregation
                    ├─ MLP baseline (mean/attention-free)          ← 우리 progression 1단계
                    ├─ ABMIL (Ilse 2018)  = minimal attention-MIL  ← progression 2단계 primary
                    └─ CLAM-SB / CLAM-MB  = pathology-grade comparator  ← 동일 단계 standard
                          └─ BRCA phenotype: ER / PR / HER2 / PAM50(multi-class)
```

## (A) REUSE — preprocessing precedent
CLAM의 전처리는 우리 tiling 설계의 **검증된 reference**다.
- **Tissue segmentation**: CLAM `use_otsu`/`sthresh`/`mthresh`/`a_t`/`a_h` ↔ 우리
  `tile_config.yaml` Otsu-mask. 동일 원리 → 우리 mask 품질을 CLAM default와 대조해 sanity check.
- **Fixed-magnification tiling**: CLAM은 고정 배율에서 patch 좌표를 추출. 우리도 256×256 @ 20×
  고정. patch coords (.h5 ↔ coords.npy) 포맷 정합으로 downstream 호환.
- **Frozen encoder feature extraction**: CLAM은 ResNet50을 frozen으로 쓰지만 `--model_name uni_v1`
  로 UNI(1024)/CONCH(512) swap 지원 → 우리 FM embedding 추출 경로와 직접 연결.
- 결론: 우리 `tile_wsi.py`는 인프라 제약(per-patient cap 5000, S3 read-only) 때문에 유지하되,
  **파라미터·산출 포맷을 CLAM과 정합**시켜 재현성과 비교가능성을 확보한다.

## (B) COMPARE — modeling baseline
우리 modeling 진행은 규칙상 **MLP → attention MIL** (건너뛰기 금지).
- **MLP baseline**: 전체 tile embedding을 mean-pool 후 MLP. 가장 단순한 slide-level head.
- **ABMIL**: gated-attention pooling. attention-MIL의 minimal form, primary baseline.
- **CLAM-SB / CLAM-MB**: ABMIL + instance-level clustering constraint (+ class별 branch).
  - **CLAM-MB ↔ PAM50 (5-class)**: multi-class subtyping의 정석 reference. PAM50 baseline 비교에 필수.
  - **CLAM-SB ↔ ER/PR/HER2 (binary)**: single-branch attention 비교.

### 공정 비교 원칙
모든 aggregator (MLP·ABMIL·CLAM-SB·CLAM-MB)를 **동일 FM embedding** 위에서 같은
patient-level split으로 평가해야 aggregator 자체의 marginal gain을 분리할 수 있다 (Critic #2).
data leakage 방지 위해 split은 `split_policy_v0` lock 이후 고정 (Critic #1).

## (C) Critic 연계 (7-point)
- #1 leakage: patient-level split, CLAM과 동일 fold 규약.
- #2 baseline: random/subtype-only/pixel-mean + MLP + ABMIL + CLAM-SB/MB.
- #6 DRP framing: CLAM은 subtyping 모델 — drug-response 어휘 금지.
- #7 claim-level: 모든 비교 결과 `hypothesis_only` 유지.

## (D) 알려진 한계 / 미확정
- Nature 본문(IdP redirect)에서 정확한 **AUC 수치·slide count**를 WebFetch로 확정하지 못함.
  baseline 표에 CLAM 원논문 수치를 인용할 땐 **본문/표를 직접 열어 검증** 후 기입.
- CLAM 원검증은 RCC/NSCLC subtyping + LN metastasis — **BRCA phenotype(ER/PR/HER2/PAM50)
  과제는 우리가 직접 재현/학습**해야 하며, 원논문 수치를 그대로 우리 task 성능으로 오인용 금지.

## Verdict
**전처리는 reuse·정합, 모델은 ABMIL/CLAM을 standard baseline으로 compare.** CLAM은 우리
MLP→attention-MIL progression의 상한 기준선이자 PAM50 multi-class 비교의 핵심 comparator이고,
preprocessing은 Otsu-tiling 설계의 검증 선례다 — 어느 쪽도 우리 novelty가 아니다.
