# 아형-매개 confound 검정 — 회의 전 부분 결론 (2026-07-12 ~19:15)

> advisor 지정 결정적 검정("H&E가 통상 병리를 넘어 마커를 보는가"). **방법 한계 정직히**: 여기 oracle은 LOO 범주-비율(빠른 proxy)이고 완전 partialling-incremental(per-patient p_HE + DeLong)은 subagent 몫. PAM50-for-ER은 near-tautology. hypothesis_only.

## 결과 (병리-라벨 oracle vs H&E MIL)
| 마커 | oracle(병리라벨) | H&E MIL | 판정 |
|---|---|---|---|
| **HER2-amp(유방)** | **0.789**(PAM50) | 0.75 | **병리에 흡수** — H&E가 아형 oracle을 못 넘음 → 아형-매개(정확 분석, holdout) |
| ER(유방) | 0.846(PAM50) | 0.90 | H&E 미세 초과(+0.05) — 대체로 아형연관·약간 넘음(rough, PAM50 near-tautology) |
| MSI-H(대장) | 미완(조직형 fetch 빈값) | 0.92 | **미완** — a priori H&E가 세밀 형태(TIL·점액)로 조직형 넘을 가능성(미검증) |
| all-RAS(대장) | 미완 | 0.71 | 미완 |

## 결론 (정직)
- **confound는 실재·확인됨(적어도 HER2)**: H&E의 HER2 신호(0.75)는 PAM50-아형 oracle(0.79)을 못 넘음 → "H&E가 HER2 증폭을 본다"가 아니라 "**HER2가 많은 아형의 형태를 본다**"와 부합.
- ER도 대체로 아형연관(oracle 0.85), H&E는 약간만 초과 → 마커-특이성 약함.
- **MSI/RAS는 미완** — 이게 법칙의 사활: MSI가 조직형 oracle을 뚜렷이 넘으면(H&E가 세밀 MSI 형태 포착) 법칙이 그 마커에선 산다. 완전 incremental 필요.
- **함의**: "형태 상관물이 치환가능성 결정" 법칙은 **마커마다 병리-baseline을 넘는지에 달림**. HER2/ER은 아형-매개라 법칙의 마커-특이 주장 약함. **MSI 결과가 논문 성립을 가름.**

## 다음 (정확 검정)
per-patient p_HE로 완전 partialling-incremental(MSI·RAS 포함, DeLong/LR) — subagent 진행 또는 MIL 재실행 필요. 대장 조직형은 GDC/TCGA-CDR로 대체 조달.

---
## ⚠️ 정정 (subagent 정확 incremental 도착 — 제 crude oracle 뒤집힘, 19:10)
제 oracle은 **PAM50을 "병리 baseline"으로 잘못 사용**했습니다. **PAM50은 분자 아형(분자데이터 필요, ER/HER2로 일부 co-define=near-circular)이지 통상 병리가 아닙니다.** 정확 분석(nested LR + DeLong, 5-fold CV):
| 마커 | vs **통상병리(조직형)** Δ | vs PAM50(분자,circular) Δ | 판정 |
|---|---|---|---|
| ER | **+0.236** (CI 0.15–0.33, p≈0) | +0.034(작지만 유의) | **H&E가 통상병리 넘음(마커-특이)** |
| HER2-amp | **+0.178** (CI 0.10–0.26, p=1e-6) | +0.035(유의) | **H&E가 통상병리 넘음** |
- **정정**: "HER2 아형에 흡수"(내 crude oracle)는 **틀림**. 올바른 baseline(통상 조직형)과 비교하면 H&E가 ER·HER2에 **유의한 마커-특이 신호를 더함.** PAM50 대비 작은 증분은 **near-circular ceiling**이지 흡수 아님.
- **단 honest 한계**: 통상 baseline=조직형(ductal/lobular)뿐(TCGA-BRCA 등급 결측)이라 **coarse** — H&E가 이걸 넘는 건 낮은 바. "type+등급+세밀형태 전체"를 넘는지는 두 baseline 사이, 미해결.
- **HER2 "blind(chance)"는 여전히 틀렸음**(H&E ~0.73). 그러나 "아형 흡수"도 아님 → **약하지만 마커-특이**가 정직한 현 상태.
- **MSI/RAS(대장): 나·subagent 둘 다 미완**(cBioPortal 대장 공변량·per-patient p_HE plumbing). MSI가 통상병리 넘는지가 대장 법칙의 사활 — 회의 후 완료.
- **교훈(반복)**: 나 또 crude proxy로 성급히 "흡수" 결론냄 → 정확 분석이 뒤집음. baseline 정의(분자 vs 통상병리)가 결론을 가름. **법칙 생사 선언 보류.**
