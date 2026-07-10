# BIOP02-48 3-way 비교 — 방법론 노트 (EXAONE 1010 전량)

**날짜:** 2026-07-03 · **작성:** kkkim (Embedding) · **claim_level:** sanity (임베딩 QC / 모델 선택 — Critic-gated 예측 주장 아님)

## 코호트
- TCGA-BRCA slide-level, **1010/1010 전량** (교집합 n은 라벨별 결측으로 상이: er 1010, pr 1005, her2 698, pam50 1009).
- 모델: UNI(1024d, mean-pool), CONCH(512d, mean-pool), EXAONE_pm(768d, act1 mean-pool = apples-to-apples), EXAONE_sg(768d, EXAONE 자체 3-stage attention 집계).
- 라벨별로 **네 모델 모두 동일 교집합 슬라이드셋**에서 채점 (`compare_models.py` `set.intersection`). patient-grouped StratifiedGroupKFold(5), LogReg(class_weight=balanced), 1000× bootstrap 95% CI.

## ⚠️ 3장 mem-bounded 추출 (방법론 불일치 명시)
EXAONE Path 2.0의 `_load_wsi`는 **level-0 전체 해상도를 CPU RAM에 통째로 로드**한다. 아래 3장은 초고배율(60–80×)이라 level-0 픽셀이 서버 RAM(503GB)을 초과해 기본 경로로는 OOM(로드 불가):

| slide | level-0 | level-0 Mpx | 사용 레벨 | mpp_eff | n_patch(tissue) |
|---|---|---|---|---|---|
| TCGA-OL-A66H | 167936×420096 | 70,549 | level 1 (ds 4) | 0.465 | 1522 |
| TCGA-OL-A66J | 130304×247552 | 32,257 | level 1 (ds 4) | 0.658 | 12643 |
| TCGA-OL-A66K | 139008×256256 | 35,622 | level 1 (ds 4) | 0.658 | 20135 |

- **대응:** `extract_exaone.py --max-megapixels 15000` (신규 `MemBoundedEXAONE` 서브클래스). level-0가 임계 초과 시 가장 fine한 적합 피라미드 레벨을 읽고 **effective mpp = mpp × downsample로 스케일**해 물리적 타일 크기를 보존한다. forward/집계는 불변.
- **불일치:** 나머지 1007장은 level-0에서 추출, 이 3장은 level-1(≈0.5mpp target에 근접, 특히 A66H 0.465). target_mpp=0.5 사양에는 오히려 부합하나, **엄밀히는 나머지와 소스 레벨이 다름**.
- **타당성 근거:** 3장 임베딩 모두 finite·768d, slide_global norm 27.42(코호트 평균과 동일), patch_mean norm도 코호트 1σ 내 → in-distribution. A66H는 tissue tile이 1522로 낮으나(마스크 보수적) 임베딩은 정상 범위.
- **영향 범위:** 1010 중 3장(0.3%). 필요 시 이 3장 제외한 N-교집합 1007 결과도 동일 디렉토리 git 이력에 존재(동일 결론: EXAONE_sg가 er/pr/her2 우위, pam50만 UNI/CONCH).

## 결과 요약 (1010)
| Label | n | UNI | CONCH | EXAONE_pm | EXAONE_sg | winner |
|---|---|---|---|---|---|---|
| er | 1010 | .855 | .842 | .852 | **.923** | EXAONE_sg |
| pr | 1005 | .770 | .761 | .762 | **.845** | EXAONE_sg |
| her2 | 698 | .598 | .590 | .659 | **.697** | EXAONE_sg |
| pam50 | 1009 | **.736** | .734 | .732 | .704 | UNI |

**해석 주의:** EXAONE_sg 우위는 "EXAONE 타일 임베딩이 5% 낫다"가 아니라 **"학습된 슬라이드-레벨 attention 집계(slide_global) ≫ 단순 mean-pooling"**을 반영한다. apples-to-apples인 EXAONE_pm은 UNI/CONCH와 대등(er .852 vs .855). 즉 델타는 임베딩 품질 + 집계 방식이 섞인 값이며 순수 임베딩 비교는 pm 열로 봐야 한다. Modeling(sjpark)의 attention MIL이 UNI/CONCH mean-pool 대비 유사 이득을 낼지 검증 가치 있음.
