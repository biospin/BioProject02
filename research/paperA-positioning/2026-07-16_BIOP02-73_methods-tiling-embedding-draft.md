# BIOP02-73 — Paper A Methods 초안: Tiling + 임베딩 파이프라인

> 작성: 2026-07-16 (kkkim 세션). **마감: 2026-08-22.**
> 상태: **Methods 초안 (리뷰·수치 확정 대상).** 모든 파라미터는 리포 실측 근거를 붙였고, 미확정은 `[확인 필요]`로 명시 — 임의 수치 금지.
> 근거 파일: `agents/embedding/README.md`(tiling/UNI) · `agents/data/split_policy_v0.md`(split) · `agents/modeling/configs/baseline_*_uni.yaml`(CLAM) · `research/paperA-positioning/2026-07-10_research-plan.md`(모델·데이터).

---

## 2. Methods (draft)

### 2.1 Data and cohorts
분석은 유방암(BRCA) H&E whole-slide image(WSI)에 한정한다(BRCA-only, 사전등록 제약). 학습·튜닝은 **TCGA-BRCA**, 외부 hold-out test는 **CPTAC-BRCA** 공식 라벨을 사용하며, CPTAC는 학습·모델선택 전 과정에 **일절 노출하지 않는다**. 표현형 라벨은 ER, PR, HER2 status 및 PAM50 subtype이다.

### 2.2 WSI tiling
각 WSI를 Otsu 조직 마스크로 전경(조직) 영역을 검출한 뒤 비중첩 patch로 분할한다.

| 항목 | 값 | 근거 |
|---|---|---|
| Tile size | 256 × 256 px | `tile_wsi.py` |
| Target resolution (MPP) | 0.5 μm/px (≈20×) | `tile_config.yaml` |
| Tissue mask | Otsu, threshold 0.1 | `tile_wsi.py` |
| Per-slide tile cap | 5,000 (random sample, seed=42) | `tile_wsi.py` |
| 좌표계 | level-0 pixel (x, y) | `coords.npy (N,2) int64` |

배율 스케일링: 좌표는 level-0 픽셀로 저장하고, target MPP에 맞춰 read_size를 조정한다(예: 40× 슬라이드는 512×512로 읽어 224×224로 리사이즈). Tile 상한은 슬라이드당 5,000개로, 초과 시 seed=42 고정 random sampling으로 재현성을 확보한다.

> ✅ **Stain normalization (해소 2026-07-16):** H&E 색보정(Macenko/Reinhard) **미적용**. `extract_uni.py`는 UNI 입력에 ImageNet 채널 정규화(mean=(0.485,0.456,0.406), std=(0.229,0.224,0.225))만 적용. → Methods에 "no H&E stain normalization was applied; tiles were channel-normalized with ImageNet statistics at UNI input"로 기술하고, stain 변이 미보정을 Limitations에 명시.

### 2.3 Foundation-model tile embedding
각 tile을 병리 파운데이션 모델로 임베딩한다. 기본 모델은 **UNI**(MahmoodLab/UNI; Chen et al. 2024), tile 임베딩 차원 **1024** (float32)로, tile은 모델 입력 규격(224×224)에 맞춰 리사이즈한다.

> ✅ **모델 버전 (해소 2026-07-16):** headline 임베딩 = **UNI v1 (1024-dim)** 확정. CLAM config `baseline_*_clam.yaml`의 `embedding_dim: 1024`, 프로젝트 CLAUDE.md도 "UNI v1이 헤드라인(1024-d), UNI2-h(1536-d)는 SOTA 견고성 검증용". 디렉토리 `*_uni_v2`는 **UNI2-h가 아니라 UNI v1의 2차 실행 라벨**(1024-d 그대로). → Methods에 "UNI (Chen et al. 2024), 1024-dim"으로 고정. (부차 비교로 CONCH 512·EXAONE Path 2.0 768 존재하나 headline은 UNI v1.)

Slide 표현은 tile 임베딩 집합으로 두고, 집계는 attention-MIL 분류기(2.5)가 수행한다.

### 2.4 Patient-level, site-disjoint splitting (leakage guard)
Split은 **환자 단위(`case_id` = TCGA-XX-XXXX 12자 prefix)** 로만 결정하며, slide/tile/file 단위 분배를 금지한다. 한 환자의 모든 슬라이드(DX1/DX2 포함)는 동일 fold에 묶인다(Bussola 2020; Yagis 2021).

추가로 **TCGA submitting-site(TSS) disjoint**를 강제한다(barcode 2번째 토큰 = TSS code = scanner/staining/fixation 시그니처 proxy). 기본 방식은 Howard PreservedSiteCV(class-balance QP 최적화), fallback은 site-grouped greedy이다(Howard et al. 2021).

- Hard invariant (빌드 시 + CI assert): `patient-overlap(train∩val∩test by case_id) == 0`.
- Fold 정의는 data-owner가 동결하고 정의 해시 **`split_hash=5995f29d3978b831`** 를 모든 `metrics.json`에 기록한다. CPTAC-BRCA는 외부 hold-out test로만 사용.

> `[확인 필요]` split_policy_v0 상태: "data-owner LOCKED (2026-07-11), Critic cross-sign(braveji) pending" — 최종 Methods 확정 전 Critic 서명 완료 여부 반영.

### 2.5 Attention-MIL phenotype classifiers
Slide-level 표현형 예측에 attention-based MIL(CLAM; Lu et al. 2021)을 사용한다. ER/PR/HER2 이진 status는 **CLAM-SB**, PAM50 다분류는 **CLAM-MB**로 학습한다.

학습 설정(`baseline_*_uni.yaml`):

| 항목 | 값 |
|---|---|
| Classifier head hidden dims | [512, 256] |
| Dropout | 0.3 |
| Epochs | 10 |
| Learning rate | 1.0e-3 |
| Batch size | 1 (slide/step, MIL 관례) |
| Seed | 42 |
| Optimizer | **Adam** (`train_mil.py:166`, lr=config) ✅ 해소 |

> `[확인 필요]` config의 `hidden_dims`가 CLAM attention head 정의인지 별도 MLP인지 코드(`run_baselines.py`/모델 정의)에서 확인해 정확히 기술. CLAM-SB/MB 표준 구성 대비 커스텀 여부도 명시.

### 2.6 Reproducibility
모든 실행은 seed=42로 고정하고, 각 `metrics.json`에 split_hash·config·commit hash·predictions를 기록한다(provenance). 

> ✅ **registry provenance (해소 2026-07-16):** `cross_validation_registry.jsonl`은 **이미 5개 엔트리로 채워짐**(er/pr/her2/pam50/pam50_4class, 각 commit_hash·critic_status 포함, `validate_registry.py` 통과). 연구계획서(07-10)의 "0 bytes"는 그 사이 갱신됨. → Methods "Reproducibility"에서 이 registry 참조 가능. (단 critic_status는 caution/reject 상태 — headline 승격은 별개 게이트.)

---

## 참조 (리포 근거 존재)
- Lu et al. 2021 — CLAM (`research/wsi-mil/lu-2021-clam/`)
- Chen et al. 2024 — UNI (`research/foundation-models/chen-2024-uni/`)
- Bussola 2020 · Yagis 2021 · Howard 2021 — split/leakage (`agents/data/split_policy_v0.md` 인용)

## 초안 미확정 요약 (2026-07-16: 5건 → 1건, 4건 해소)
1. ~~Stain normalization~~ ✅ 미적용(ImageNet 정규화만)
2. ~~UNI 모델 버전~~ ✅ UNI v1 1024-dim (`uni_v2`=v1 2차 실행 라벨)
3. **split_policy Critic 서명** — **미해소**(braveji cross-sign pending, 유일한 외부 의존)
4. ~~Optimizer~~ ✅ Adam (`train_mil.py:166`)
5. ~~registry provenance~~ ✅ 이미 5개 엔트리로 채워짐(validate 통과)

→ **kkkim이 해소 가능한 4건 완료. 남은 1건(#3 split Critic 서명)은 braveji 몫.**
