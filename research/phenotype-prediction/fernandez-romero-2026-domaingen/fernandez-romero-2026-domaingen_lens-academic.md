# fernandez-romero-2026-domaingen — Lens: Academic

## Novelty 평가
개별 부품(H&E→PAM50/IHC 예측, FM×MIL 벤치, TCGA→CPTAC 외부검증)은 모두 선행이 있으나, **진짜 기여는 "외부검증 붕괴를 계량하고 그 원인을 요인분해한 것"** — 대부분 논문이 internal validation만 보고하던 관행을 정면으로 반박. RPD로 열화를 정규화하고 4개 도메인 시프트 요인을 회귀해 **staining variability + feature space divergence가 80%(R²=0.800)** 설명한다는 결과가 방법론적 알맹이. 예측 SOTA 경쟁이 아니라 **negative/diagnostic** 논문이라는 점이 신규성의 성격(따라서 값이 낮은 게 결함이 아니라 메시지).

## Rigor 평가
- 강점: **13 FM × 3 MIL 전조합**(단일 모델 우연 배제), RPD 정규화, 아형별(HER2-enriched RPD=1.00) 층화, 요인 회귀로 원인까지 추적. 외부 코호트(CPTAC)를 실제로 돌림.
- 약점: **외부검증이 CPTAC 단일**이고 **flash-frozen**이라 조직준비 축과 코호트 축이 교락(FFPE↔frozen 자체가 거대 시프트). 저자도 **"exploratory"**로 한정. 지표가 PR-AUC/macro-F1이라 문헌 AUROC와 비교 곤란.

## BIOP02와의 중복 (굵게 = 직접 충돌 = NEAREST SCOOP)
- **같은 task family: H&E FM+MIL → PAM50 + ER/PR/HER2**
- **같은 코호트·설계: TCGA-BRCA CV → CPTAC-BRCA 외부검증**
- **같은 동기: "PAM50·IHC는 비싸고 많은 세팅에서 이용 불가"**
- **같은 실패 재현: HER2 외부 붕괴**(그들 RPD=1.00 ↔ 우리 registry HER2 외부 AUC 0.530 reject)

## 차별점 (우리의 방어선)
- 그들은 **예측 정확도**(PR-AUC/F1)를 잰다 → 우리는 **결정-가치·치환가능성**(형태 예측이 *언제* 분자검사를 값싸게 대체하나)을 mis-routing cost × therapeutic distance로 잰다.
- 그들의 **외부 붕괴 발견이 오히려 우리 논지를 지지**: "예측만으로는 취약 → 치환에는 비용이 있고 보정·기권이 필요"(SUBSTITUTABILITY_LAW의 외부 근거).
- 우리는 **다암종 결정지도**(유방 anchor + 폐·대장·위·두경부) — 그들은 유방 단일.
- (계획) 우리는 **치료-결과 anchor**(trastuzumab)로 라우팅 비용을 임상에 정박 — 그들엔 없음.

## 인용 포인트
- "H&E→분자 예측 + 외부검증 열화는 이미 출판됨[Fernandez-Romero 2026], 특히 HER2-enriched RPD=1.00 붕괴는 우리 HER2 reject와 일관" — **정성 한 줄 양보 후 즉시 결정-가치 프레임으로 전환.**
- CPTAC 도메인 붕괴 + "staining/feature-space가 80% 설명"을 **우리 AI 결정레이어(보정/기권)의 동기**로 인용.
- **주의:** 예측 정확도를 헤드라인으로 삼으면 정면 스쿱. figure로 방어하지 말 것(한 줄 인용까지).

## 검증 플래그
- 이중확인(OpenAlex abstract + PMC): 설계·코호트·HER2/Normal-like 붕괴·R²=0.800·지표종류.
- PMC quote-demand 재확인: MIL 3종·Virchow HER2 0.399→0.219·CPTAC flash-frozen.
- 우리 대비 수치(HER2 외부 AUC 0.530, ER 0.894 vs subtype_only 0.918 p=0.613)는 `experiments/registry/cross_validation_registry.jsonl`(AUROC) — 그들 PR-AUC와 **지표 상이, 직접 대조 불가**.
