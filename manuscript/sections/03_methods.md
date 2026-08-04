# Methods (집필 골격 — 지금 바로 쓸 수 있음)

> 타일링부터 검정까지 전부 코드·결과 파일이 있어 월요일에 병행 집필 가능. 파라미터는 실제 config/코드에서만 인용(파일:줄 명시), 지어내지 않는다.

## M1. 코호트와 라벨

이 연구는 유방암(TCGA-BRCA, 약 1,010 진단 슬라이드)을 앵커로 삼고 폐·대장·위·두경부를 더한 다섯 암종을 다룬다. 각 코호트의 슬라이드 수는 결과 JSON에 실측되어 있다(대장 523, 폐 1,026, 위 439, 두경부 468). 라벨 출처와 환자 단위 split은 [../../agents/data/](../../agents/data/)에서 관리하며, 사전등록된 축 경계는 봉인 문서 [../../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md](../../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md)에 기록되어 있다. 이 다섯 암종은 열린 pan-cancer 아틀라스 확장이 아니라 치환가능성 법칙을 검정하기 위한 의도된 경계다.

## M2. 타일링 · 임베딩

각 whole-slide image는 20× 배율에서 256×256 픽셀 타일로 분할하였다. 조직 영역은 Otsu 임계로 배경과 분리하고, 환자당 최대 5,000 타일로 상한을 두어 대형 슬라이드의 과대표집을 막았다(설정 [../../agents/embedding/configs/tile_config.yaml](../../agents/embedding/configs/tile_config.yaml)). 좌표는 슬라이드별로 저장해 이후 임베딩·재현에 재사용하였다.

각 타일은 병리 파운데이션 모델로 특징 벡터로 인코딩하였다. 헤드라인 임베딩은 **UNI v1(1024차원)**이며, 모델 비의존성 검정을 위해 동일 좌표에 대해 Virchow2(2560차원)와 UNI2-h(1536차원)로도 재추출하였다(M8, Supplement). Virchow2 임베딩은 CLS 토큰과 패치 토큰 평균을 이어붙인 값(1280+1280=2560차원)으로, register 토큰을 제외해 산출하였다. 슬라이드 단위 인터페이스인 EXAONE Path 2.0은 좌표 기반 파이프라인과 호환되지 않아 이 견고성 세트에서 제외하였다. 타일은 각 모델의 입력 규격(224×224)으로 리사이즈하고 ImageNet 통계(mean 0.485/0.456/0.406, std 0.229/0.224/0.225)로 채널 정규화하였다. **H&E 염색 정규화(Macenko·Reinhard 등)는 적용하지 않았으며**, 이로 인한 염색 변이 미보정은 한계로 명시한다(추출 코드 [../../agents/embedding/scripts/extract_uni.py](../../agents/embedding/scripts/extract_uni.py)·[../../agents/embedding/scripts/extract_virchow2.py](../../agents/embedding/scripts/extract_virchow2.py)). 임베딩은 영구 보관하고(manifest에 `/workspace` 절대경로), raw WSI는 추출 후 스트리밍 캐시에서 삭제하였다.

## M3. 모델 · 학습

표현형 예측과 축별 검정에는 CLAM-SB attention MIL을 사용하였다. 입력 특징 차원은 각 임베딩의 차원(UNI 1024)이고, hidden 512·attention 256, 40–50 epoch로, 시드 42를 고정해 결정론적으로 학습하였다(코드 [../../experiments/crosscancer/run_mil_cost.py](../../experiments/crosscancer/run_mil_cost.py)). 예측은 슬라이드 단위로 산출한 뒤 환자 단위로 집계하였다.

## M4. 평가 설계

모든 평가는 site-disjoint holdout에서 수행하였다. 같은 제출 기관(TSS)의 슬라이드가 학습과 평가에 동시에 들어가지 않도록 분할해 기관 지문에 의한 leakage를 차단하였고, 검정력을 위해 validation과 test를 평가에 합쳤다(분할 정책은 각 결과 JSON의 `eval` 필드에 명시). 대조군은 세 가지다: 라벨을 무작위로 섞은 shuffle-null, 유병률 기준선(0.5), 그리고 해당 축에서 아형-only 또는 pixel-mean 기준선. 신뢰구간은 1,000회 부트스트랩 95% CI로 보고하였다(결과 JSON `ci95`). 환자 클러스터를 반영해야 하는 곳(수용체 라우팅)은 슬라이드가 아니라 환자 단위로 CI를 재계산하였다.

## M5. cost-of-substitution 프레임

치료 라우팅의 치환비용은 confusion matrix에 치료 거리(therapeutic distance)를 곱해, 측정 마커로 정한 치료와 H&E-예측 마커로 정한 치료가 갈리는 오분류 비용으로 정의하였다. 선도지표는 거리무관 misroute_rate이며, 정의와 계산은 [../../experiments/kkkim/20260710_cost_of_substitution/](../../experiments/kkkim/20260710_cost_of_substitution/)에 있다. 이 프레임은 약물 반응을 예측하지 않는다 — 마커에서 치료 배정으로의 치환비용만 조작화하며 약물 구조를 입력으로 쓰지 않는다.

## M6. 사전등록 · claim 규율

법칙의 판정 임계는 봉인된 사전등록 문서에서만 인용하고 발표자료의 관측치를 기준값으로 쓰지 않는다. 검정력 규칙(양성 표본 25 미만 → exploratory → INCONCLUSIVE)은 결과를 본 뒤 옮기지 않으며 확증과 반증에 대칭으로 적용한다. 모든 산출은 `hypothesis_only`이고 후향적이며, 개인 수준 benefit이 아니라 전향 검증이 필요한 가설이다.

## M7. Yale 앵커 방법

후향적 결정지도에 실제 치료결과 층화를 달아 앵커 축(HER2)을 실증으로 검정하였다. 항HER2 축 점수를 산출하고(A3), 그 점수로 Yale 코호트의 병리학적 완전관해(pCR)를 층화해 AUROC와 부트스트랩 95% 신뢰구간을 구한 뒤 측정 HER2 확률 기준선과 DeLong 검정으로 비교하였다(A4, 스크립트 `run_yale_pcr.sh`). frozen-transfer(추가 학습 없이 앵커 모델을 그대로 전이)로 수행하였고, 성공 기준은 Farahmand 등의 교차검증 AUC 0.80[0.69–0.88]에 근접·중첩하는 것으로 사전 정의하였으며 이를 능가한다는 주장은 하지 않는다. 결과는 AUROC 0.533[0.411–0.653]으로, 항HER2 축이 H&E-예측 표현형으로는 pCR을 층화하지 못함을 보였다 — 결정지도의 "HER2 대체 불가" 음성과 일관되는 정직한 음성이다.

## M8. 다중 FM 견고성 방법

결정지도가 특정 파운데이션 모델(UNI)의 산물인지 형태 신호 자체인지를 가리기 위해, 각 FM(Virchow2, UNI2-h) 임베딩 공간에서 CLAM을 처음부터 **재학습**하였다(임베딩만 교체하는 것으로는 불충분 — 좌표계가 다르므로 예측 모델을 각각 다시 적합해야 같은 층위의 비교가 된다). 재학습 러너는 [../../experiments/crosscancer/multifm_retrain_watcher.py](../../experiments/crosscancer/multifm_retrain_watcher.py)이며, UNI와 동일한 site-disjoint 프로토콜·endpoint·판정 기준을 사용하였다.

논지는 절대 AUROC가 아니라 결정지도의 **순위 보존**이다. 판정 기준은 5-seed shuffle-null 우연배제(real AUROC > null 평균 + 2×표준편차, ddof=1)로 다른 곳과 동일하며, 시드는 42·1·2·3·4를 사용하였다. 결정론은 동일 시드 재실행 2회로 확인하였다(대장 BRAF Virchow2 seed42 = 0.8798 재현 일치). 결과 정본은 [../../experiments/crosscancer/CROSSCHECK_5SEED_MULTIFM.md](../../experiments/crosscancer/CROSSCHECK_5SEED_MULTIFM.md)·[../../experiments/crosscancer/MULTIFM_COMPARISON.md](../../experiments/crosscancer/MULTIFM_COMPARISON.md)이고, sjpark·braveji가 원자료에서 독립 재계산해 사인오프하였다(BIOP02-101).
