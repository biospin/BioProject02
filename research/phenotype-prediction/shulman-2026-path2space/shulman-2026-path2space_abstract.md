# shulman-2026-path2space — Abstract (Path2Space)

## 서지
- **Title:** AI-predicted spatial transcriptomics unlocks breast cancer biomarkers from pathology
- **Model:** **Path2Space**
- **Authors:** Eldad D. Shulman, Emma M. Campagnolo, Roshan Lodha, Youngmin Chung, Amos Stemmer, … (34인) … , Eytan Ruppin (corresponding, last) — Crossref 확정
- **Venue:** Cell vol 189 (2026), article S0092-8674(26)00458-7 · PMID 42105763
- **DOI:** [10.1016/j.cell.2026.04.023](https://doi.org/10.1016/j.cell.2026.04.023) · preprint bioRxiv 2024.10.16.618609

## 초록 요약
Path2Space는 **H&E 조직병리 슬라이드에서 직접 공간 유전자 발현(spatial transcriptomics)을
예측/재구성**하는 딥러닝 모델이다. 대규모 유방암 ST 데이터로 학습해 **수천 개 유전자**의
공간 발현을 견고하게 예측하며, **기존 21개 방법을 능가**한다.

- **적용 규모:** **976개 TCGA-BRCA 종양**에 추론 → 종양미세환경(TME) 지도 작성.
- **결과:** **cell-type abundance를 정확히 추정**하고, 생존 결과가 뚜렷이 다른 **3개의 공간
  기반 유방암 subgroup**을 식별.
- **임상 적용:** 예측 ST에서 유도한 **저비용 공간 TME landscape**가, 값비싼 기존 bulk-sequencing
  기반 바이오마커보다 **화학요법 및 trastuzumab 반응 예측을 더 정확히** 수행.
- **함의:** 일상 조직병리에서 확장 가능한 저비용 반응 바이오마커 발굴이 가능하다는 **advocacy**.

## 우리 논문에서의 역할
- **CONTRAST / 최근접 인접(미스쿱).** H&E × 분자 × 치료축 + ~976 TCGA-BRCA로 **코호트 규모·치료축이 겹치는 가장 가까운 선행**이지만, **방향이 반대**다: Path2Space는 예측 ST 유래 공간지표(SPAND)가 측정 RNA/FISH만큼/보다 좋다는 **바이오마커 옹호**, 우리는 형태가 분자검사를 대체할 때의 **결정손실을 감사(cost-of-substitution)**.
- **경로 차이:** 그들은 **H&E→예측ST→마커**(재구성 경로), 우리는 **H&E→표현형→치료**(ST 미경유 직접 경로) → 스쿱 아님, 직교 축.
- **인용 방식:** "가장 가까운 선행"으로 정직 인용하되 방향 반대를 명시. cross-cancer outline에서 대조군으로 배치(유방 전용 — 대장/범암종 버전 미존재, 2026-07 확인).
- **주의(서사 충돌):** Path2Space는 HER2 공간 이질성(SPAND 높음)을 *좋은* trastuzumab 반응 예측자로 쓰는 반면, 우리 결정지도는 같은 이질성을 **치환비용의 floor(나쁨)**로 프레이밍 → 정면 대비이므로 이 반대해석을 본문에서 반드시 다뤄야 함. 코드/가중치는 Zenodo·GitHub 공개(비상업 학술) → 필요 시 우리 TCGA-BRCA add-on 주석에 재사용 가능.
