# H&E × Spatial Transcriptomics — 스쿱 지형 + defensible 각 (2026-07-11)

> 출처: literature-scout + novelty-strategist 병렬 스캔(GPU 0). 목적 = "ST를 넣어 'spatial' 이름값을 벌 것인가(Track C)" 값싼 판단.
> **결론(양 에이전트 수렴): 지금 ST 트랙 개설 NO.** 우리 차별점(cost-of-substitution)은 ST 불필요·오히려 직접경로가 더 defensible. ST는 제출 후 or 방어용으로만.

## 1. 스쿱 지형 요약
- **"H&E→ST 발현 예측"은 포화(레드오션):** ST-Net(2020)·HisToGene·Hist2ST·BLEEP·iStar(Nat Biotech 2024)… + 1k급 페어 코퍼스 2종(HEST-1k·STimage-1K4M, NeurIPS 2024) + 멀티모달 FM(OmiCLIP/Loki Nat Methods 2025). **방법론 진입 금지.**
- **⚠️ 최대 위협 = Path2Space (Cell 2026, bioRxiv 2024-10):** H&E→예측ST→**chemo·trastuzumab 반응**, **~976 TCGA-BRCA** — 우리와 코호트 규모·치료축 겹침. **단 "ST 경유 경로"를 스쿱**하며, 우리가 이미 가진 **직접경로(H&E→표현형→치료, ST 미경유)는 스쿱 안 함.**
- **ST-attention 검증각은 이미 스쿱:** "Beyond Attention Heatmaps"(MedIA 2026, arXiv 2603.08328)가 "ST로 H&E-MIL attention 검증"을 이미 함 → **순진한 'attention을 ST로 설명' 각은 단독 실행 금지.**
- **HER2 공간 이질성 자체는 20년 된 기성 생물학**(Andersson 2021·Wu 2021·HER2-low T-DXd) → 새롭지 않음. 새로움은 "이질성이 있다"가 아니라 **축별 치환비용 ledger에 접는 것.**

## 2. 남은 whitespace (우리가 살 자리)
1. **결정수준 cost-of-substitution** — 필드는 correlation(r≈0.3-0.5)·survival만. "측정 대신 예측라벨 쓸 때 축별 치료결정 손실"은 미개척 = **우리 Paper A 프레이밍, 직교.**
2. **Path2Space vs Wang(Nat Commun 2025) 모순** — Path2Space "예측ST 유용" vs Wang "예측발현 저조" → 아무도 '결정손실'로 안 봐서 미해결 = 우리 프레이밍의 자리.

## 3. Banked 각 (지금 실행 X, 미래/방어용)

### ★ Angle A (방어용·값쌈, revision-ready) — 공간 이질성 = 치환비용의 irreducible FLOOR
- **주장:** 확진 HER2+ 종양에서도 종양 면적 일부는 치료 ERBB2 역치 아래 → 우리 "anti-HER2 100% mis-route"는 **아티팩트가 아니라 floor**(어떤 patient-level 예측기도 H&E든 IHC든 sub-region 타깃 복원 불가). **약점→강화(일방향) 결과로 전환.**
- **defensible:** concordance 아님(2603.08328 회피)·"이질성 존재" 아님(Andersson 회피) = cost ledger. 미점유.
- **값싼 실험:** Andersson 8 HER2+ 종양(+HEST 유방 Xenium)에 spot ERBB2를 H&E에 오버레이 → "치료역치 이하 면적%". 그림 1장, 학습 0.
- **정직한 한계:** ST 코호트(TCGA 아님)라 메커니즘 시연이지 우리 숫자 분해 아님(유추). 공개 유방 ST는 HER2 0/low/3+ 경계 **미포괄** → "within-category sub-threshold 면적"까지만, "cross-category mis-routing 행렬" 불가.
- **운용:** 사전제출 필수그림 아님. **리뷰어가 HER2 gold-standard 공간불안정성 공격할 것 → 방어 탄약(limitation 문단+요청 시 그림)으로 미리 준비.** 반나절이면 supplementary로 승격.
- ⚠️ VERIFY: ERBB2가 해당 HEST Xenium 유방 패널에 있는지(Visium이면 보장·Xenium이면 확인).

### Angle C (진짜 미래 ST 논문 — banked, 착수조건 명시) — 공간분해 치료가설 flip
> **결정(2026-07-11, 사용자):** C는 지금 착수 X, **잘 기록해 bank.** 착수 트리거 = Paper B(therapeutic-evidence 링킹) 성숙. **⚠️ 필요 시 Paper A와 B를 합칠 수 있음(사용자)** → 합치면 C의 토대(therapeutic 링킹+cost)가 Paper A/B 통합본에 함께 서므로 **C 착수 시점이 앞당겨질 수 있음.** 병합 여부에 따라 C를 통합논문 확장으로 갈지, 독립 Paper C로 갈지 재판단.

- **주장:** 우리 DepMap/GDSC 링커는 환자당 subtype→약물 가설 1개. 공간혼합 종양(luminal이 basal/HER2-like subclone 보유, Wu 2021)에선 종양 면적 일부가 patient-level 가설에 오배정. "region-level subtype이 다른 top 가설 내는 면적%" 정량.
- **defensible:** 우리 시그니처(therapeutic-evidence 링킹+cost)를 공간으로 확장 = 사실상 미점유. 어떤 interpretability각보다 on-brand.
- **의존:** Paper B(jhans, 2026-07-06 착수) 성숙 필요 → Paper C.

### Angle B (강등, 단독 금지) — "H&E-blind vs triageable" ST검증 → Angle A에 흡수.

## 4. 결정 자료 (C 착수 여부)
**권장: 지금 ST 트랙 개설 NO.**
- 근거: 차별점(cost-of-substitution·cross-cancer taxonomy·Critic)은 ST 불필요. 유방 페어 ST는 다른 환자·치료라벨 없음·HER2 경계 미포괄. Sprint 5 그림동결(7/17)+cross-cancer 진행 중 → 신규 모달리티=마감 리스크·서사 희석.
- **최고 레버리지 1수:** Angle A를 **사전제출 필수가 아닌 revision 방어탄약**으로 미리 빌드. HER2 공간불안정 공격 대비. clean·반나절이면 "치환비용 floor" supplementary로 승격(강화·일방향).
- Angle C = Paper B 존재 후 진짜 ST 논문.

## 5. tie-breaker 확인 결과 (2026-07-11, bioRxiv 전문 정독)

### ✅ Path2Space는 "cost-of-substitution/결정손실"을 하지 **않음** → 우리 프레이밍 **인접·미스쿱 확정**
bioRxiv v2(2024.10.16.618609) 전문 확인. Path2Space의 치료반응 프레이밍 = **바이오마커 advocacy**(예측ST 유래 지표가 측정 RNA/FISH만큼/보다 좋다), **우리와 반대 방향:**
- HER2 pathway **SPAND(공간 이질성) 점수가 trastuzumab pCR 예측** — TransNEO AUC 0.80·IMPRESS 0.72, **bulk RNA-seq(0.66/0.64)·FISH 능가**. trastuzumab-특이(chemo엔 약함).
- 주장 = "H&E-유래 공간지표가 측정 분자검사만큼/보다 우수" (예측기 옹호). **"측정 대신 예측라벨로 치료 결정 시 축별 손실"은 전혀 안 함.**
- → **우리 cost-of-substitution(결정손실 감사)는 직교·미스쿱.** Path2Space는 "가장 가까운 선행"으로 정직 인용하되, **방향이 반대**(그들=예측 옹호 / 우리=치환 실패 지점 감사)임을 명시.
- 부수 포지셔닝: **Path2Space vs Wang 모순**을 우리가 해소 가능 — Path2Space는 *공간* 예측지표(SPAND), Wang은 raw 예측발현. 우리 결정손실 렌즈가 둘 위에 앉음.

### ⚠️ Angle A에 대한 **역설/주의**(Path2Space가 만든 복잡성)
Path2Space는 **HER2 공간 이질성(SPAND 높음)을 *좋은* trastuzumab 반응 예측자**로 씀(HER2-high↔low 혼재 → 면역반응 spillover 가설). 우리 Angle A는 같은 이질성을 **치환비용의 floor(나쁨)**로 프레이밍 → **정면 대비.** Angle A 추진 시 이 반대해석을 반드시 다뤄야 함(이질성=예측신호 vs 이질성=결정불가). 단순 스쿱은 아니나 서사 충돌 관리 필요.

### 참고: 반응 코호트 = TransNEO + IMPRESS
Path2Space가 쓴 HER2+ 반응 코호트 = TransNEO(trastuzumab 61/chemo 93)·IMPRESS(62/64). 우리 repo에 `experiments/kkkim/20260710_pcr_impress/` 이미 존재 → IMPRESS pCR이 우리 레이더에도 있음(연계 가능).

### 남은 확인 1건
- Angle A용 HEST Xenium 유방 패널 **ERBB2 포함 여부**(Visium이면 보장·Xenium이면 확인). → 아래 §6.

## 6. ✅ HEST ERBB2 패널 확인 완료 (2026-07-11)
- **10x Xenium Human Breast 패널(280유전자, Janesick 2023=HEST 포함본)에 ERBB2 포함 확인** (10x 문서: "ERBB2, PGR, ESR1, GATA3, MKI67 포함"). Andersson은 Visium 전사체라 자동 포함.
- → **Angle A(공간 ERBB2 sub-threshold 면적) 데이터 실행 가능.** 두 tie-breaker 모두 해소 → Angle A는 언제든 반나절 실행 가능한 방어탄약으로 확정(사전제출 필수 아님).

---
관련: `2026-07-10_subtype-decision-map.md`(Paper A 코어) · `PROGRESS_DECISIONS.md`(D9 결정). Sources: HEST-1k(arXiv 2406.16192)·Beyond Attention Heatmaps(2603.08328)·Path2Space(bioRxiv 2024.10.16.618609/Cell 2026)·Andersson 2021(PMID 34650042)·Wu 2021(Nat Genet)·Wang 2025(Nat Commun s41467-025-56618-y)·OmiCLIP/Loki(Nat Methods 2025).
