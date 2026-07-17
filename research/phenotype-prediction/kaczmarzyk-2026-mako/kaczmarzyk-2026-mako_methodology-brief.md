# kaczmarzyk-2026-mako — Methodology Brief (경계 문서 ★)

> ⚠️ 이 브리프는 **재구현 가이드가 아니라 경계(fence) 문서**다. MAKO는 우리가 재현·차별화할 baseline(=Dawood)이 아니라 **스쿱된 슬롯(B4, prognosis/ROR-P 재사용)** 이다. 목적: (1) 그들이 정확히 무엇을 예측했고 성능·외부검증이 어떤지 확정, (2) 이것이 **우리 claim을 어떻게 제한**하는지, (3) 그들의 해석가능성(HIPPO)이 method 선례로 인용할 가치가 있는지.

## A. 그들이 정확히 무엇을 했나 (WHAT — 확정)
- **예측 대상:** PAM50 기반 **ROR-P(risk-of-recurrence) 재발위험 점수** — PAM50 상관계수 가중합 + 증식 성분. **아형/수용체 상태 분류가 아님.** (연속값 + low/int/high 3구간.)
- **입력·집계:** H&E WSI → 12 병리 FM tile embedding + 2 비-병리 baseline(ResNet50/ViT-DINOv2) → **ABMIL(gated attention)** → WSI-level ROR-P.
- **코호트:** **CBCS ER+/HER2- n=847(883 WSI) 학습·10-fold CV → TCGA-BRCA ER+/HER2- n=613 외부검증.**
- **성능(검증):**
  - 분류 Low/Med vs High ROC AUC — **CONCH: CBCS 0.809 / TCGA 0.850**(외부 +10.4% vs ResNet50); H-optimus-0·Virchow2 TCGA 0.840.
  - 연속 회귀 Pearson r — **H-optimus-0 CBCS 0.638**(최고), 12중 11 FM이 baseline 초과; **TCGA 외부에서는 다중검정 보정 후 유의 모델 0**(회귀 축 일반화 실패).
  - 생존 — ABMIL 범주형 모델 C-index가 transcriptomic ROR-P와 **동등(p>0.05)**; CBCS ER+/HER2- 847중 107 재발.
- **해석가능성:** attention map(저자 "unreliable" 인정) + **HIPPO**(patch 제거/추가 → necessity·sufficiency). 종양 영역이 high ROR-P에 necessary·(대부분) sufficient; 고위험 patch 형태(핵 다형성·유사분열·괴사·침윤) [미확인 정밀도].
- **정확한 요약:** 분류·생존 축은 외부검증까지 성립, 연속 회귀 축만 외부 실패. **재발위험 예측(prognosis-from-H&E)은 외부검증까지 done.**

## B. 이것이 우리 claim을 어떻게 제한하나 (BOUND — 가장 중요)
**축을 바꾼다. "us too, but better/interpretable/governed"는 금지 — 그 문장은 스쿱으로 직행.**

| | MAKO (스쿱된 축) | 우리 (다른 축) |
|---|---|---|
| 산출물 | H&E → **ROR-P 재발위험 예측기** (정확도 리더보드 + 해석) | **예측기가 아님.** cost-of-substitution **결정지도** |
| 질문 | 재발위험을 얼마나 잘 예측하나 | 값싼 H&E-예측 표현형이 분자검사를 **대신할 때 치료 랭킹 충실도를 얼마나 잃나** |
| 방법 축 | FM×ABMIL 성능 벤치 + 외부검증 | 냉동 세포주→약물 지도에 (측정 아형 vs H&E-예측 아형) 입력 → divergence 아형별 층화 |
| 결론 형태 | 어느 FM이 최고 AUC/r | luminal ≈0 손실(안전한 값싼 triage) / HER2 붕괴(분자검사 필수) |
| 거버넌스 | — | Critic-gated, `hypothesis_only`, 사전등록 miss-rate |

- **금지 프레이밍:** "우리도 H&E로 재발/예후를 예측한다"(해석·거버넌스를 붙여도) → **B4 스쿱.** MAKO가 우리 데이터로 우리 실험(12 FM×ABMIL, 외부검증)을 이미 출판.
- **허용 프레이밍:** "H&E→재발위험/분자마커 예측은 **외부검증까지 포화**([MAKO], [Fernandez-Romero 2026]) → 우리는 정확도 리더보드를 만들지 않고, 값싼 형태학이 치료적으로 충분한 곳과 아닌 곳의 **치환-비용 결정지도**를 낸다."
- **회귀 실패는 기회 아님:** MAKO의 연속 ROR-P 외부검증 실패를 우리 진입 틈으로 오해 금지 — 분류·생존은 유지되어 축은 여전히 점유. 우리는 이 축에서 경쟁하지 않는다.
- **C3 residual 자기가드:** 우리 novelty 문서 C3(연속 ROR-P/proliferation residual → 비용지도 sharpening)가 ROR-P를 건드린다. 사용 시 **MAKO를 predictor-of-record로 인용 + "결정지도 입력"으로만 프레이밍**, "ROR-P 예측 신규성"으로 절대 승격 금지. 리뷰어가 MAKO를 안다고 가정.

## C. HIPPO를 method 선례로 인용할 가치 (CITE — 예)
- **HIPPO = perturbation 기반 해석:** patch를 제거/추가해 예측 이동으로 necessity·sufficiency 판정. 이는 우리 **Critic 7-point #3 counterfactual check("핵심 feature 제거 시 랭킹 변화")** 와 **개념적으로 동형**.
- **인용 방식:** 일반적 "interpretable pathology" cite가 아니라, **우리 counterfactual 게이트의 구체적 method 선례**로 명명. "MAKO는 HIPPO로 종양 patch가 예측에 necessary/sufficient함을 보였다 — 우리는 같은 counterfactual 원리를 *치료 랭킹* 공간으로 옮겨, feature 제거가 hypothesis 랭킹을 바꾸는지를 Critic 게이트로 검사한다."
- attention map은 저자 스스로 unreliable이라 했으므로 **attention이 아니라 HIPPO(perturbation)** 를 선례로 인용할 것.

## D. BIOP02 연계 (요약)
- **진입 금지:** B4(예후/ITH/ROR-P 재사용) — MAKO가 외부검증까지 점유. 정확도 리더보드 재생산 금지.
- **인용:** standing FM benchmark(예측 포화 근거) + HIPPO(counterfactual 선례).
- **Paper C 참고:** FM 간 성능 편차(CONCH/H-optimus-0/Virchow2)는 "치환가능성 법칙의 모델 비의존성" 검증 설계의 baseline 문헌으로만.
- **거버넌스:** 우리 출력은 `hypothesis_only` + Critic pass; "predict recurrence/prognosis from H&E" 표현 금지.

## 검증 플래그
헤드라인(12 FM+2 baseline, CBCS ER+/HER2- n=847→TCGA n=613, CONCH 0.809/0.850, H-optimus-0 r=0.638, TCGA 회귀 유의 0, 생존 C-index 동등, HIPPO necessity/sufficiency) = PMC12895011 Version of Record 확인 + 로컬 abstract 이중확인. 컷포인트 11.76/52.94·patch 120개/2.0mm²·재발 107/847 = 단일 WebFetch 요약 → **[미확인 정밀도]**, 인용 전 원문 표 재확인. 모두 `hypothesis_only` 가정 유지.
