# 치환가능성 법칙 — 5암종 통합 스코어보드 (G1 결과 확정용)

> 사전등록 `SUBSTITUTABILITY_LAW_PREREGISTRATION.md`(봉인) 대비 held-out 관측 통합. claim_level: **hypothesis_only** · critic_status: **caution**(braveji, 2026-07-14 — HPV 5-seed PASS 확인 후 CONFIRM 복원; BLOCKER-1·3·4-2는 kkkim 브랜치 `50bb7c9`에서 해소됨 — main 병합 대기. G2 pass 잔여: sjpark #4·jhans #5 sub-check + 위암 lauren 원인 진단 + braveji 3차 재검토). 2026-07-13 (**정본 재동기화 2026-07-14**: 폐 base 3 endpoint를 정본 JSON으로 정정, 대장 5-seed 실패검정 반영 — BLOCKER-2·4).
> 목적: Paper C 브랜치→main 병합 게이트 **G1(결과 확정)**의 단일 인계 문서. 정본 수치는 각 암종 `full/LAW_TEST.md` / `routing_cost.json`에서 직접 인용.
> **핵심 규율: "확정"=결과셋 동결+정직 라벨링이지 "법칙 확증"이 아니다.** 검정력 있는 봉인 확증은 아래 굵게 표시된 소수뿐.

## 인식론 구분 (읽기 전 필수)
- **Sealed-forward(진짜 held-out):** 폐·위·두경부 — 예측을 결과 전 커밋으로 봉인 후 MIL. (폐 예측 07-12 05:06 < 결과 15:35 등)
- **Retrospective(회고적):** 대장 — 결과(07-12 04:45) 먼저, 예측(05:06) 뒤. **held-out 확증 아님, 방향 일관까지만.** (`COLORECTAL/full/LAW_TEST.md` 상단 배너)
- **Anchor(내부 holdout):** 유방 — 기존 내부 site-disjoint holdout(외부 아님).
- **검정력 규칙(사전등록, 사후 이동 금지):** n_pos<25 → exploratory → **INCONCLUSIVE**(확증·반증 대칭 불가, 점추정은 "consistent with"까지).

## 통합 표

| 암종 | endpoint | 축 분류 | 관측 AUROC (CI) | n_pos | 검정력 | 지위 | 판정 |
|---|---|---|---|---|---|---|---|
| 두경부 | **HPV** | 대체가능(바이러스축 형태) | **0.9594 (0.921–0.986)** | **26** | **충분** | sealed | **✅ CONFIRM (≥0.80, 5-seed PASS — real 0.959 > thr 0.790)** |
| 두경부 | grade_high | 양성대조(분화도) | 0.8152 (0.742–0.882) | 41 | 충분 | sealed | ✅ 양성대조 PASS(≥0.75) |
| 두경부 | egfr_amp | 필수/등급적 | 0.6039 (0.443–0.760) | 17 | 부족 | sealed | INCONCLUSIVE(≤0.70 점추정 부합) |
| 폐 | **histology LUSC** | 대체가능(양성대조) | **0.939 (0.905–0.967)** | **153** | **충분** | sealed | **✅ 양성대조 CONFIRM(≥0.93 명확 적중)** |
| 폐 | egfr_activating | 등급적 | 0.8518 (0.725–0.953) | 15 | 부족 | sealed | INCONCLUSIVE(0.75–0.89 부합, shuffle 0.46) |
| 폐 | kras_g12c | 필수 | 0.6809 (0.577–0.783) | 14 | 부족 | sealed | INCONCLUSIVE(≤0.65 미세초과, EGFR>KRAS 점추정만) |
| 위 | lauren_diffuse | 양성대조(강한 형태) | 0.5364 (0.379–0.694) | 31 | 충분 | sealed | ⚠️ **양성대조 FAIL(예측 ≥0.85, 관측 0.54)** |
| 위 | msi_h | 대체가능 | 0.8599 (0.759–0.941) | 24 | 부족 | sealed | INCONCLUSIVE(≥0.82 점추정 부합) |
| 위 | erbb2_amp | 필수 | 0.6444 (0.523–0.771) | 14 | 부족 | sealed | **무효(real 0.6444≈null 0.6406, 신호 0) — "blind 적중"·유방 HER2 인용 철회** |
| 위 | ebv | 대체가능(부분) | 0.9477 (0.861–1.0) | 7 | 부족 | sealed | exploratory only |
| 대장 | msi_high | 대체가능 | 0.9184 (0.850–0.969) | 21 | 부족 | **retro** | 회고·consistent(held-out 아님) |
| 대장 | anti_egfr | 필수 | 0.7053 (0.620–0.783) | 84 | 충분 | **retro** | 회고·방향 consistent(misroute 0.416 최고) |
| 대장 | braf_v600 | 등급적/partial | 0.8817 (0.817–0.938) | 15 | 부족 | **retro** | 회고·consistent |
| 유방(anchor) | ER | 대체가능 | 0.901 | — | 내부 | anchor | 대체가능축 高 |
| 유방(anchor) | HER2 | 필수 | 0.599 | — | 내부 | anchor | 필수축 near-random(법칙 앵커) |
| 유방(anchor) | PAM50 | 아형 | 0.759 | — | 내부 | anchor | 아형 회복 中 |

## 결론 (정직한 bottom line — 이게 "확정")

1. **검정력 있는 sealed-forward 확증:** 양성대조(폐 histology **0.939** · 두경부 grade 0.815) + **두경부 HPV 0.9594(n_pos=26, 5-seed PASS — real 0.959 > thr 0.790, pixel-mean 0.922).** HPV가 "형태 상관물 有 → 대체가능(≥0.80)" 축의 **유일한 검정력 있는 확증**이며, 바이러스축이라 법칙을 새 종류로 확장. 5-seed 우연배제 확립(BLOCKER-1 해소, `50bb7c9` on kkkim branch — main 병합 대기). pixel-mean 0.922는 조직형·바이러스축이 저해상도 특징에서도 회수 가능함을 보임(MIL gap +0.037 — Limitation 소재). ⚠️ **HPV 커버리지 비무작위 Limitation**: 결손군(임베딩無) HPV+ 유병률 0.40 vs 포함군 0.10(~30 HPV+례 제외) → CONFIRM 0.9594는 **분석 부분집합 기준**, 전체 HNSC 일반화엔 결손 편향 명시(아래 §커버리지). (5-seed·counterfactual은 유효.)
2. **모든 변이/증폭축은 exploratory(n_pos<25) → INCONCLUSIVE.** 폐 EGFR/KRAS, 위 MSI 등 방향은 법칙과 일관하나 검정력 부족으로 확증·반증 불가. **[인용 철회, braveji G2] 위 ERBB2-amp(0.6444)는 shuffle-null 0.6406과 마진 0.004 = 신호 0**이라, 유방 HER2(0.599)와의 "증폭≠형태 일치"를 증거로 쓸 수 없음(신호 없는 endpoint에서 증거 가치 차용 불가).
3. **위암 양성대조(Lauren) FAIL(0.54) — 원인 진단 완료(`GASTRIC_STAD/full/LAUREN_POSCONTROL_DIAGNOSIS.md`, 14a181d):** **Lauren-특이 site-교란**이지 파이프라인 고장·데이터 희소 아님(dev 0.963→holdout 0.536, pixel-mean 0.63>MIL 0.54, 유병률 site종속 HU100%~CG18%). → 종전 **"위암 endpoint 전체 저신뢰"를 "Lauren 국한"으로 정정**; MSI(0.86, 5-seed PASS)·ebv 등 위암 일반화는 정상. *(braveji 3차 재검토 확인 대기.)*
4. **대장은 회고적** → 검정력 있는 held-out 확증 집계에서 제외. 방향 일관까지만.
5. **법칙 = 방향적으로 일관(directionally consistent), 이분법 미확립(dichotomy NOT established).** 확립엔 검정력 있는 필수/변이축 확증(n_pos≥25) 축적 필요 — 현 코호트 크기론 대부분 도달 불가(구조적 한계).
6. **5-seed shuffle-null 강건성 — 대장만 완료, 2/7 실패(BLOCKER-4 반영):** `COLORECTAL/full/shuffle_null_robustness.json`(기준 real > null_mean + 2·null_sd). **cms1_vs_rest 0.912 < 0.936 FAIL · cms4_vs_rest 0.661 < 0.773 FAIL**; cms2·cms3·msi_high·anti_egfr·braf PASS. 이 완료·실패 검정이 이전 대장 LAW_TEST에 "미실시(non-blocking)"로 잘못 기술되고 스코어보드 인용 0이던 것을 정정. sealed-forward 3암종(폐·위·두경부)엔 5-seed 미적용 → 우연배제 미확립(위 1).

## Counterfactual — attention-ablation (7-point #3 · 2026-07-15)

> sealed-forward 핵심 endpoint에 특징-제거 counterfactual: seed42 real 모델의 full-bag attention 상위 k% 타일 제거 후 재-forward(`sh_counterfactual.py`). **top-k 제거 낙차 ≫ random-k 제거**면 예측이 특정 고-attention 형태학에 충실. 정본 `<암종>/full/counterfactual_ablation.json`.

| endpoint | full AUROC | top-10% 낙차 | random-10% | top-20% 낙차 | random-20% | 충실도 |
|---|---|---|---|---|---|---|
| **두경부 HPV (CONFIRM)** | 0.9594 | 0.042 | −0.001 | **0.107** | 0.001 | ★ 강함 |
| 폐 histology (양성대조) | 0.939 | 0.032 | 0.001 | 0.084 | −0.000 | 강함 |
| 위 msi | 0.8599 | 0.010 | 0.001 | 0.036 | −0.002 | 중간 |
| 두경부 grade (양성대조) | 0.8152 | −0.004 | −0.001 | 0.017 | −0.001 | 약함(분산 특징) |

**해석:** 전 endpoint에서 **top-attention 타일 제거가 random 제거보다 AUROC를 크게 낮춘다**(random ~0). 특히 **HPV(CONFIRM)는 top-20% 제거 시 −0.107 vs random ~0** → 예측이 아티팩트가 아니라 특정 고-attention 형태학에 **충실(faithful)**. 충실도 순서(HPV>histology>msi>grade)는 각 형태특징의 국소성과 정합. → braveji `critic_report.json` **counterfactual_check: caution**("sealed-forward 3암종 counterfactual 없음") 보완, HPV CONFIRM 서술 지지. (random 제거는 seed0 단일 draw; 낙차 대비가 극명해 충분.)

## 누수 ASSERT + HPV 커버리지 (2026-07-15 · braveji followup 대응)

- **누수 assert (data_leakage caution의 assert-log 잔여 해소):** split.csv 직접 검증 — 4암종 전부 **patient_overlap=0, site-disjoint 위반=0**(site수 LUNG 69·COLORECTAL 37·HNSC 28·GASTRIC 22). 로그 `LEAKAGE_AND_COVERAGE_VERIFY.log`. **/workspace 임베딩 ls**도 동 로그 첨부(braveji SSH 키 부재 대체): 1052/622/472/442.
- **⚠️ HPV 커버리지 비무작위성 (CONFIRM Limitation) — 원인 규명 완료(2026-07-15):** 두경부 임베딩 결손(~14%)이 HPV에 비무작위 — 포함군 HPV+ 유병률 **0.102(n=412)** vs 결손군 **0.400(n=75)**, HPV+ ~30례 제외.
  - **메커니즘 = site-level 슬라이드 부재(형태학 문제 아님):** 결손 75명은 **다운로드/타일 실패가 아니라 애초 GDC에 진단(DX) 슬라이드가 없던 환자**(다운로드 큐 0/75). **TSS site `CR`이 통째 결손**(53명 전원 미포함, HPV+ 17/53=32% 편중) → 결손 HPV+ 30명 중 CR이 17명(57%). 즉 **HPV+ 많은 특정 기관(CR 등)이 임상·분자 데이터(=HPV 라벨)만 제공하고 H&E DX 슬라이드는 GDC 미공개**여서 생긴 데이터 가용성 아티팩트.
  - **함의:** AUROC 0.9594 자체는 "HPV+ 형태가 어려워 드롭"된 게 아니라 site-가용성 결손이므로 **형태-난이도 편향은 아님**. 단 분석셋이 CR류 site를 못 봐서 **그런 site로의 외삽엔 caveat**. site-disjoint holdout(가용 site 간 일반화)은 유효 → CONFIRM은 **"가용 site 기준 확증 + CR류 미표집 Limitation"**으로 기술. (5-seed PASS·counterfactual faithful 유효.)
- **pixel-mean Limitation(서술):** MIL이 pixel-mean을 크게 못 넘는 endpoint(위 lauren pixel 0.631>MIL 0.536 등)는 "MIL 부가가치 제한적, 형태 신호는 mean-pool로도 상당 회수"로 기술. subtype-only는 폐 EGFR/KRAS만 산출(cross-cancer 대부분 순환).

## G1 상태 — ✅ **확정 (kkkim Leader 승인, 2026-07-14)**
- [x] held-out 4암종 + anchor 결과 산출·정본 수치 확정.
- [x] 대장 회고적 지위 명시(sealed-forward와 구분).
- [x] 정직 라벨링(검정력·지위·판정, 위암 양성대조 FAIL 명시).
- [x] **kkkim(Leader) 최종 "결과 확정" 승인(2026-07-14).** 결과셋 동결 = 이 스코어보드 + 각 `LAW_TEST.md` + DECISION_MAP. **이후 변경은 새 버전.**
- → **다음: braveji Critic(G2 나머지) 인계.** claim은 "법칙 방향 일관·이분법 미확립"으로 동결(승격 금지).
