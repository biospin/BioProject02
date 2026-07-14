# 폐 subtype-only(histology) baseline — 해석 (BLOCKER-3 잔여, braveji G2)

> 7-point #2의 세 번째 baseline(random·pixel-mean에 이어 subtype-only). cross-cancer에서 subtype-only는 대부분 순환이라 **폐 EGFR/KRAS from histology(LUAD/LUSC)만 비순환·유의미**하게 산출. 정본 `baseline_subtype.json`, 스크립트 `sh_subtype_baseline.py`. claim_level: hypothesis_only · critic_status: pending · 2026-07-14.
> baseline = 이미지 미사용, holdout 예측 = train에서 그 histology의 변이 양성률 → holdout(val+test site-disjoint) AUROC.

## 결과 (MIL과 대조)

| endpoint | histology-only AUROC (CI) | MIL AUROC | 증분(MIL−histology) | n_pos | 사전분류 |
|---|---|---|---|---|---|
| egfr_activating | 0.767 (0.700–0.817) | 0.852 | **+0.085** | 18/315 (expl) | 등급적 |
| kras_g12c | 0.793 (0.764–0.822) | 0.681 | **−0.112** | 15/315 (expl) | 필수 |

train 양성률: EGFR LUAD 9.6%/LUSC 0.7%, KRAS LUAD 12.9%/LUSC 0.0% (두 변이 모두 LUAD 편중이 histology-only 예측력의 근원).

## 해석 (law-test 정련)
1. **KRAS-G12C: histology-only(0.793)가 MIL(0.681)을 앞섬 → MIL은 histology 너머 신호 0(오히려 −).** KRAS의 겉보기 예측력은 **전부 LUAD-편중(histology)**이고, 변이 자체는 형태학적으로 침묵. **사전등록 "필수(형태 상관물 없음)" 분류를 오히려 강화** — MIL의 0.68은 변이 형태가 아니라 약한 histology 인식일 뿐. (⚠️ 단 둘 다 exploratory n_pos<25 → 확증 아님, 방향 근거.)
2. **EGFR: MIL(0.852)이 histology(0.767)를 +0.085 상회 → histology 너머 부분 형태 상관물 존재.** 사전등록 "등급적(lepidic/acinar 부분 가시)" 분류와 일치. 단 증분도 exploratory 구간.
3. **종합:** subtype-only baseline이 폐 변이 신호를 **"histology 성분 vs 그 너머"로 분해**. EGFR은 소폭 beyond-histology(등급적), KRAS는 순수 histology(필수). 이는 pixel-mean·shuffle-null에 더해 **7-point #2 baseline 3종을 폐 변이축에서 완비**하고, 법칙의 등급적/필수 구분을 baseline 층위에서 뒷받침.

## 순환이라 미산출한 것 (정직 명시)
- 폐 histology 자체 / 두경부 HPV(=아형축) / 위 MSI(=분자아형) / 위·두경부 Lauren·grade(Lauren은 site-교란 실패 endpoint, grade 약함) — subtype-only 예측 대상이 곧 아형이라 순환.
- 대장 BRAF: CMS는 별 파일이고 D13 증분검정이 이미 +CMS 조건화를 수행(anti-EGFR 증분이 +CMS서 소멸=아형 매개)로 대체됨.
- breast(anchor)의 PAM50→수용체 subtype-only는 Paper A 소관(여기 미포함).
