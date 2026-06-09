# BIOP02 Novelty & Positioning (v0.1)

작성 2026-06-09 (kkkim). 선행연구 조사(research/_index/) + novelty-strategist 종합. **타겟 저널: npj Precision Oncology.**

> 이 문서는 Scientific Critic 검토 대상. claim-level(#6 anti-DRP, #7 hypothesis-only)·생물학적 타당성(#5) 직접 관련.

## 한 줄 결론

**예측 정확도로는 못 이긴다.** H&E→BRCA 표현형(Couture/Naik/Gamble/Shamai/Tafavvoghi)도, H&E→약물민감도(Dawood 2024, npj Prec Onc, 우리 타겟 저널)도 이미 존재. **이길 수 있는 축 = ① 표현형 병목(auditability) ② 다중경로 수렴 ③ site-통제 외부검증 + Critic 게이트.** 기여는 "더 나은 숫자"가 아니라 **재현·반증 가능 프로토콜**.

## Contribution statement (리뷰어가 Dawood·Tafavvoghi를 안다고 가정)

> H&E 형태를 BRCA의 **랭킹된, 명시적 hypothesis-only 치료 제안**으로 바꾸는 **감사 가능(auditable)·표현형 병목(phenotype-bottlenecked)** 파이프라인을 제시한다. end-to-end 이미지→약물민감도 회귀(Dawood 2024)와 달리, 치료 랭킹을 **해석 가능한 분자표현형 중간단계**(파운데이션 임베딩 기반 ER/PR/HER2/PAM50)로 경유시키고, **독립 근거 경로가 합의할 때만**(PRISM/GDSC/CTRP 민감도 전이 + LINCS 시그니처 역전 + actionability KB) 가설을 지지하며, 모든 가설을 **Scientific Critic 판정기**가 site-stratified·외부검증(CPTAC) 하에 게이트한다. 기여는 더 나은 약물민감도 수치가 아니라, 각 제안이 예측 표현형으로 추적되고 직교 데이터로 교차검증되며 경로 불일치 시 기각되는 **재현·반증 프로토콜**이다.

## 두 scoop과의 차별화 (정직한 중복 = 굵게)

### vs Dawood 2024 (최고 위험 — 동일 저널·동일 과제군)
- **중복: "H&E→다약물 민감도, TCGA-BRCA"는 그들 것.** 리뷰1에서 "Dawood 대비 뭐가 새롭나" 반드시 받음.
- 그들이 **안 한** 것(논문 검증됨): ① 해석 가능 중간단계(그들은 saliency heatmap뿐) ② **단일 경로**(CTRP ridge 회귀 imputation)뿐 vs 우리 다중경로 합의 ③ **외부검증 없음**(TCGA 5-fold CV만) vs 우리 CPTAC ④ **ImageNet ShuffleNet** vs 파운데이션 모델(단 측정해야 주장) ⑤ 명시적 anti-DRP/hypothesis-only 거버넌스.
- **주장 금지:** 더 나은 약물민감도 상관, "H&E가 약물민감도 예측" novelty, 임상 효용.

### vs Tafavvoghi 2024 (직접 subtype baseline, 공개코드)
- **중복: 동일 4-class subtype, 동일 TCGA-BRCA+CPTAC. 그들 macro-F1 0.727이 우리 bar(SOTA 목표, 약한 내부 baseline 아님).**
- 그들이 안 한 것: ① subtype에서 멈춤(치료 연결 없음) ② **site 통제 없음, 외부 test split 없음** ③ **XGBoost-on-tile-counts** vs 파운데이션 MIL. → UNI+attention-MIL이 *더 엄격한*(site-stratified) 프로토콜에서 0.727을 넘으면 공정한 head-to-head 승리.
- 정직한 한계: 그들 HER2-E F1=0.545 — H&E로 소수 subtype 천장 낮음. "HER2-E 고친다" 약속 금지 → **calibrated uncertainty로 저신뢰 HER2-E 가설을 Critic이 기각**.

## 가장 싼 검증 실험 (~150슬라이드 + CPTAC, GPU 저렴, leakage 통제)

| # | 실험 | 증명하는 것 |
|---|---|---|
| **Exp1** | 파운데이션(UNI/CONCH) vs ImageNet 백본 vs Tafavvoghi 공개 XGBoost, 동일 split, ER/PR/HER2/PAM50 | 표현형 성능 이득의 출처가 임베딩임 + 두 scoop 실제 방법 대비 개선 정량화 (임베딩 사전계산 → 저렴) |
| **Exp2** ★ | 동일 모델, random split vs Howard site-preserved split + site-classifier probe | 기존 수치(0.727·Dawood 상관)가 site 교란됨 + 우리 수치가 정직함. **최강 리뷰어 방패, 거의 무료** |
| **Exp3** ★ | 병목 라우터(우리) vs end-to-end(Dawood 충실 재현) — 전이 일치 + **오류 귀속성** 비교 | 병목이 수사가 아니라 오류를 진단가능하게 만듦. 정확도 동등+감사성 우위 = 논문 thesis 실증 |
| **Exp4** | 다중경로 수렴 ablation: 약물별 PRISM/GDSC/CTRP/LINCS/OncoKB 신호 일치도 → ≥k 합의 가설이 known BRCA-actionable로 enrich (HER2+→anti-HER2, basal/BRCA-like→PARP/platinum) | 수렴이 실제 신호(투표 장난 아님). 공개 KB만, GPU 불필요. **OncoKB 레벨은 토큰/라이선스 gated → 개방 경로(Open Targets/DGIdb/CIViC) 도달 범위 정량화 + 잔여 gap 표기** |
| **Exp5** | Critic 7-point를 가설 분류기로 — 생존 가설 precision vs OncoKB/CIViC, Dawood식 raw 예측 기각률 | Critic 게이트가 결과를 바꿈(기각률>0). 아니면 장식 |

**최소 논문 세트: Exp1+Exp2+Exp4.** Exp3가 benchmark→method 논문으로 격상. **최고 레버리지 단일 수: Exp3+Exp2 평가체제.**

## 주요 리스크 / 리뷰어 반론 + 방어

1. "Dawood 2024 + extra steps" (동일저널 desk-reject 위험) → abstract를 auditability+다중경로+외부검증으로 시작, "약물민감도 예측"으로 시작 절대 금지. intro 2번째 문장에 Dawood 인용+delta 명시. Exp3가 실증 답.
2. "치료 라벨이 여전히 cell-line imputed — Dawood가 이미 인정한 약점" (사실) → 숨기지 말고 **수렴의 존재 이유로 전환**: 단일 경로는 취약 → 직교 경로 합의 요구. hypothesis-only claim-level은 정직한 귀결.
3. "임상 검증 없는데 왜 npj Prec Onc?" → Dawood도 없음(검증됨), 거기 실림. 반증 프로토콜 기여로 포지셔닝. 가능하면 HER2+ 수렴 가설이 anti-HER2 actionability 회수하는지 후향 점검.
4. "파운데이션 이득은 그냥 더 나은 feature" → 동의(고립 시). 기여는 **파이프라인 설계**, Exp1은 substrate 정량화일 뿐. UNI 과대선전 금지.
5. "site 교란이면 너희 수치도 부풀려짐" → Exp2가 선제 방어(낮고 정직한 수치를 primary로) → 반론을 강점으로 전환.
6. "PAM50/HER2-E from H&E는 거의 chance" → calibration+uncertainty Critic 기각. 분류 잘한다 주장 안 함, "못할 때를 안다" 주장.

## 멀티에이전트/Critic 앵글 (정직한 포지셔닝)
- 멀티에이전트 오케스트레이션 자체는 **framing, 독립 novelty 아님** — AI co-scientist(2025), AI Scientist(2024), VirSci(2024)가 이미 crowded. "AI 에이전트가 가설 생성"·"LLM-as-critic" 자체는 novelty 주장 불가.
- **단, 측정 가능한 기각률을 가진 falsifiability gate로서의 Critic(Exp5)은 method로 출판 가능** — "에이전트 있어요"가 아니라 가설에 대한 operating characteristic으로 보고할 때.
- owner≠reviewer·anti-self-reference 규칙은 문서화된 LLM-judge 편향(Zheng 2023 position/verbosity/self-enhancement; Panickssery 2024 self-preference 인과)에 대한 **구체적 완화책** — 일반 "리뷰어 에이전트 추가"가 아님.

## 치료가설 근거 축 확장 (DepMap/GDSC 외)
| 축 | 자료 | 역할 |
|---|---|---|
| 3번째 약물 DB | CTRP/CTD² (Seashore-Ludlow 2015, Rees 2016) | PRISM↔GDSC↔CTRP 3중 일관성(Critic #4) |
| 시그니처 역전(독립 경로) | LINCS L1000 (Subramanian 2017) / CMap (Lamb 2006) | 민감도 전이와 방법론적 독립인 2번째 가설 경로 |
| Actionability KB | OncoKB(Chakravarty 2017)·Open Targets(Ochoa 2023)·DGIdb·CIViC(Griffith 2017) | 생물학적 타당성 grounding(Critic #5) |
| 경로 DB | MSigDB(Liberzon 2015)·Reactome(Gillespie 2022) | pathway-activity 중간단계 + 경로-약물 링크 |
| 직교 모델계 | organoid/PDX (Vlachogiannis 2018) | "cell-line only" 비판 방어 |

## 엄밀성 필수 적용 (조사로 확정)
- **patient-level + site-stratified split** (Howard 2021 site signature; Bussola 2020 patient-level; Yagis 2021 누수 29–55% 부풀림). split_policy_v0에 반영.
- stain: 정규화 단독 의존 X. **stain augmentation 우선 + site-stratified split** (Tellez 2019; de Jong 2025 — 모든 FM이 medical-center 시그니처 인코딩, UNI 포함). Macenko/Reinhard 정규화는 robustness ablation으로만.
- uncertainty 게이팅: temperature scaling(Guo 2017) + MC-dropout(Gal 2016)/ensembles + conformal(Olsson 2022, Angelopoulos 2021). 가장 가까운 통합 blueprint = TRUECAM(preprint, UNI/CONCH+conformal) → 인용+차별화.

## 다음 단계
1. 상위 scoop/baseline(Dawood·Tafavvoghi·UNI·CLAM·Howard·Subramanian·OncoKB) BioProject01 멀티렌즈 상세분석
2. Exp2+Exp3 설계 구체화(research-methodologist) → split_policy_v0 연계
3. Scientific Critic 검토 핸드오프(아래 reviewer 재지정 이슈 참조)
