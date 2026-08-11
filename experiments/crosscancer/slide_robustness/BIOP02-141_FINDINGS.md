# BIOP02-141 — #8 슬라이드·영역 강건성 (HPV·MSI 우선, 박세진)

> Paper C NICE #8 (HPV 칸엔 사실상 MUST). "성능이 몇 장의 슬라이드나 비종양 아티팩트의 산물이 아님"을 실측.
> 선행(BIOP02-123 후속 group-aware CV·LOSO CI·🟡 재서술)은 커밋 e7f1d43로 완료 후 착수.
> 방법: 기존 UNI **per-tile** 임베딩(5000 tiles×1024) 재사용. CPU. 신규 데이터·큰 학습 없음.
> 독립 리뷰 = jamie(류재면). claim=provisional.

## 요약 판정
**HPV·MSI 양성 예측은 영역-강건하다 — 신호가 슬라이드 전반에 퍼져 있고 소수 타일/영역의 산물이 아니다.** 단 "다중슬라이드 추첨 의존" 질문은 **TCGA 데이터로 답할 수 없다**(양성 다중슬라이드 환자 ≈ 0). tumor-only/necrosis 대조는 **annotation 부재로 불가**(지어내지 않고 '안 됨'으로 기록).

## (A) 다중 슬라이드 일치도 — ⚠️ 양성 부재로 결론 불가
한 환자 여러 슬라이드를 held-out LR(단일슬라이드 환자로 학습)로 독립 점수:

| 코호트/endpoint | 다중슬라이드 환자 | 그중 양성 | call 일치율@0.5 | median score SD |
|---|---|---|---|---|
| HNSC / HPV | 17 | **1** | 0.941 | 0.0001 |
| GAST / MSI | 26 | **0** | 0.962 | 0.0007 |

- **핵심 제약:** 다중슬라이드 환자에 endpoint 양성이 HNSC 1명·GAST 0명뿐이다. 위 일치율은 **대부분 음성**(모델이 자신있게 낮게 주는)에 지배되므로, 정작 검증하려던 **"HPV/MSI 양성 확증이 어느 슬라이드를 뽑느냐에 달렸나"는 이 데이터로 답할 수 없다.**
- 이는 결정지도의 한계로 그대로 실어야 한다(TCGA cross-cancer에서 양성 다중슬라이드 표본 부재).

## (B) 타일 subsample region-robustness (대체 지표 — 양성 포함 전 환자)
각 환자 첫 슬라이드에서 타일을 무작위 subsample→mean-pool→**OOF(StratifiedKFold) held-out LR**로 재점수. subsample 50회. score 변동(SD)·call flip이 작으면 신호가 슬라이드 전반에 퍼짐(강건):

| endpoint | n_pos | OOF-AUROC | **양성** SD@50% | SD@25% | flip@50% | flip@25% | top-5% 타일 기여 |
|---|---|---|---|---|---|---|---|
| HPV (HNSC) | 42 | 0.902 | **0.0035** | 0.0066 | **0.0** | 0.0 | **15.8%** |
| MSI (GAST) | 76 | 0.837 | **0.0063** | 0.0103 | **0.0** | 0.0 | **15.8%** |

- **양성 score는 타일의 절반을 버려도 거의 안 움직인다**(SD 0.003~0.006, AUROC 스케일 대비 무시 가능). 4분의 1만 남겨도 call이 한 번도 뒤집히지 않았다(flip 0%).
- **(C) 타일 기여 집중도:** per-tile 선형기여 s_i=w·z_i 기준 상위 5% 타일이 슬라이드 양성신호의 **약 16%만** 차지 → 신호가 소수 타일에 집중돼 있지 않고 **diffuse**. (음성은 s 합이 음수라 top-k share 지표가 부호상 해석 불가 — 양성 클래스에만 의미.)
- ⇒ **"성능이 몇 개 타일/영역의 아티팩트"라는 가설은 기각.** HPV·MSI 앵커의 신뢰도를 강화한다.

## 불가(NOT FEASIBLE) — 카드 지침대로 '안 됨' 기록
- **tumor-only vs WSI 전체** — 종양영역 annotation 없음 → 측정 불가.
- **necrosis·stroma 제외** — 조직타입 annotation 없음 → 측정 불가.
- **attention FM-cross** — crosscancer 임베딩은 **uni_v1 단일 FM만** 존재 → FM 교차 attention 불가.
- **attention seed-cross** — 학습된 CLAM 모델 없음, **coords 파일도 없음** → seed 교차 attention(공간맵)은 CLAM 학습(GPU)+coords 필요, **heavier follow-up**. (본 카드의 (B)/(C)가 "영역 의존성" 질문을 coords 없이 대체 답변.)

## 결정지도에 붙일 caveat 문장 (초안)
> HPV·MSI 예측은 타일 subsample(50% dropout, 50회)에 강건하며(score SD ≤ 0.006, call flip 0%) 상위 5% 타일이 양성신호의 ~16%만 차지해 **소수 영역의 산물이 아니다**. 단 TCGA cross-cancer에는 양성 다중슬라이드 환자가 거의 없어(HPV 1·MSI 0) **슬라이드-간 재현성은 미검정**이며, **종양영역 한정 성능은 annotation 부재로 미측정**이다.

## 산출물
experiments/crosscancer/slide_robustness/: BIOP02-141_FINDINGS.md, robust_HNSC_hpv.json, robust_GAST_msi.json. 스크립트: slide_region_robustness.py. 헤드라인은 파일 참조.
