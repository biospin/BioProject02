# BIOP02-141 — #8 슬라이드·영역 강건성 (HPV·MSI 우선, 박세진)

> Paper C NICE #8 (HPV 칸엔 사실상 MUST). "성능이 몇 장의 슬라이드나 비종양 아티팩트의 산물이 아님"을 실측.
> 선행(BIOP02-123 후속 group-aware CV·LOSO CI·🟡 재서술)은 커밋 e7f1d43로 완료 후 착수.
> 방법: 기존 UNI **per-tile** 임베딩(5000 tiles×1024) 재사용. CPU. 신규 데이터·큰 학습 없음.
> 독립 리뷰 = jamie(류재면). claim=provisional.

## 요약 판정
**HPV·MSI 양성 예측은 타일 subsample에 강건하다 — 신호가 소수 타일에 집중돼 있지 않다**(이 지표가 답하는 축은 "영역 집중도"이지 "종양 vs 기질 조직 의존성"이 아님 — 아래 (B) 주의). 단 "다중슬라이드 추첨 의존" 질문은 통계적으로 미검정이며(양성 다중슬라이드 환자 HPV 1·MSI 0), **그 유일한 관측 사례(HPV+ TCGA-QK-A6IF)는 두 슬라이드가 0.9226 vs 0.0010으로 극단적 불일치** — "모른다"가 아니라 "경고 신호"로 읽어야 한다(jamie #11736 후속). tumor-only/necrosis 대조는 **annotation 부재로 불가**(지어내지 않고 '안 됨'으로 기록).

## (A) 다중 슬라이드 일치도 — ⚠️ 양성 부재로 결론 불가
한 환자 여러 슬라이드를 held-out LR(단일슬라이드 환자로 학습)로 독립 점수:

| 코호트/endpoint | 다중슬라이드 환자 | 그중 양성 | call 일치율@0.5 | median score SD |
|---|---|---|---|---|
| HNSC / HPV | 17 | **1** | 0.941 | 0.0001 |
| GAST / MSI | 26 | **0** | 0.962 | 0.0007 |

- **핵심 제약:** 다중슬라이드 환자에 endpoint 양성이 HNSC 1명·GAST 0명뿐이다. 위 요약 일치율·median score_sd(0.0001)는 **나머지 16명 음성 환자에 지배**되므로, 정작 검증하려던 **"HPV/MSI 양성 확증이 어느 슬라이드를 뽑느냐에 달렸나"는 통계적으로 답할 수 없다.**
- **⚠️ 단, 유일한 양성 관측 사례를 요약값 뒤에 숨기면 안 된다 (jamie #11736 후속):** HPV+ 다중슬라이드 환자는 **TCGA-QK-A6IF 딱 1명**인데, 두 슬라이드 HPV score가 **0.9226 vs 0.0010 (score_sd 0.65, calls_agree@0.5 = False)** — 한쪽 슬라이드에서 **극적으로 실패**했다. n=1이라 일반화는 불가하나, 이 사례 자체는 "미검정(중립)"이 아니라 **"슬라이드 추첨 의존이 실제로 나타난 경고 신호"**다. 결정지도 caveat에 이 구체 수치를 명시한다.
- 이는 결정지도의 한계로 그대로 실어야 한다(TCGA cross-cancer에서 양성 다중슬라이드 표본 부재 + 유일 사례 극단 불일치).

## (B) 타일 subsample region-robustness (대체 지표 — 양성 포함 전 환자)
각 환자 첫 슬라이드에서 타일을 무작위 subsample→mean-pool→**OOF(StratifiedKFold) held-out LR**로 재점수. subsample 50회. score 변동(SD)·call flip이 작으면 신호가 슬라이드 전반에 퍼짐(강건):

| endpoint | n_pos | OOF-AUROC | **양성** SD@50% | SD@25% | flip@50% | flip@25% | top-5% 타일 기여 |
|---|---|---|---|---|---|---|---|
| HPV (HNSC) | 42 | 0.902 | **0.0035** | 0.0066 | **0.0** | 0.0 | **15.8%** |
| MSI (GAST) | 76 | 0.837 | **0.0063** | 0.0103 | **0.0** | 0.0 | **15.8%** |

- **양성 score는 타일의 절반을 버려도 거의 안 움직인다**(SD 0.003~0.006, AUROC 스케일 대비 무시 가능). 4분의 1만 남겨도 call이 한 번도 뒤집히지 않았다(flip 0%).
- **(C) 타일 기여 집중도:** per-tile 선형기여 s_i=w·z_i 기준 상위 5% 타일이 슬라이드 양성신호의 **약 16%만** 차지 → 신호가 소수 타일에 집중돼 있지 않고 **diffuse**. (음성은 s 합이 음수라 top-k share 지표가 부호상 해석 불가 — 양성 클래스에만 의미.)
- ⇒ **"성능이 몇 개 타일에 집중된 아티팩트"라는 가설은 기각.** HPV·MSI 앵커의 신뢰도를 강화한다.
- **⚠️ 이 지표가 답하는 축의 한계 (jamie #11736 후속):** subsample robustness는 **"타일을 무작위로 줄여도 점수가 안 바뀌나"(공간적 분산·소수 타일 집중도)**를 잰다. 이는 tumor-only 대조가 묻는 **"종양 조직 vs 기질/괴사 중 어디서 신호가 오나"(조직 유형 의존성)와 다른 질문**이다. 종양·기질 타일이 매 subsample에 같은 비율로 섞여 들어가면, 모델이 **기질에서 신호를 얻고 있어도 이 지표는 여전히 "강건"**으로 나온다. → 따라서 이 결과는 tumor-only 대조를 **대신하지 않으며**, "다른 축(영역 집중도)을 답한다"로만 해석한다.

## 불가(NOT FEASIBLE) — 카드 지침대로 '안 됨' 기록
- **tumor-only vs WSI 전체** — 종양영역 annotation 없음 → 측정 불가. (위 (B)는 이를 **대체하지 못함** — 다른 축.)
- **necrosis·stroma 제외** — 조직타입 annotation 없음 → 측정 불가.
- **attention FM-cross** — crosscancer 임베딩은 **uni_v1 단일 FM만** 존재 → FM 교차 attention 불가.
- **attention seed-cross** — 학습된 CLAM 모델 없음, **coords 파일도 없음** → seed 교차 attention(공간맵)은 CLAM 학습(GPU)+coords 필요, **heavier follow-up**. (본 카드의 (B)/(C)는 "소수 타일 집중도" 축만 coords 없이 답함 — 조직유형 의존성은 미해결.)

## 결정지도에 붙일 caveat 문장 (개정 — jamie #11736 반영)
> HPV·MSI 예측은 타일 subsample(50% dropout, 50회)에 강건하며(score SD ≤ 0.006, call flip 0%) 상위 5% 타일이 양성신호의 ~16%만 차지해 **소수 타일에 집중된 산물이 아니다(영역 집중도 축)**. 단 이 지표는 **종양 vs 기질 조직 의존성(tumor-only 축)을 대신하지 않으며**, 그 대조는 annotation 부재로 **미측정**이다. 또한 **슬라이드-간 재현성은 미검정**인데(양성 다중슬라이드 HPV 1·MSI 0), **유일한 HPV+ 관측 사례(TCGA-QK-A6IF)는 두 슬라이드가 0.92 vs 0.001로 극단 불일치**하여 슬라이드 추첨 의존 위험을 배제하지 못한다.

## 산출물
experiments/crosscancer/slide_robustness/: BIOP02-141_FINDINGS.md, robust_HNSC_hpv.json, robust_GAST_msi.json. 스크립트: slide_region_robustness.py. 헤드라인은 파일 참조.
