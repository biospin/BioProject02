# kaczmarzyk-2026-mako — Lens: Academic

## Novelty 평가
H&E에서 **PAM50 기반 ROR-P 재발위험 점수**를 예측한 최초급의 pathology-FM 벤치마크. 진짜 신규성은 (a) 예측 대상을 아형/수용체 상태가 아니라 **재발위험 assay 값**으로 잡은 점, (b) 12개 병리 FM을 동일 ABMIL로 head-to-head 비교하며 **외부검증(CBCS→TCGA)** 을 붙인 점, (c) attention의 신뢰 한계를 인정하고 **perturbation 기반 HIPPO**로 necessity/sufficiency를 검사한 점. 모델(ABMIL)·백본(공개 FM 12종)은 기존 자산 재사용 → 방법론적 신규성은 **중간**, "무엇을 예측하는가(재발위험)"의 응용 신규성과 벤치마크 규모가 기여.

## Rigor 평가
- 강점: 12 FM + 2 baseline 전수 비교, **10-fold CV**, **독립 코호트 외부검증**(CBCS→TCGA), 분류·회귀·생존 3축, 생존에서 transcriptomic assay와 C-index 동등성 검정, 다중검정 보정, HIPPO necessity/sufficiency로 형태학 귀속.
- 약점: **연속 ROR-P 회귀가 TCGA 외부에서 유의 도달 0**(교차코호트 일반화 실패를 저자도 명시) — 분류·생존만 유지. prospective·임상 배포 검증 없음. 컷포인트·patch 수 등 일부 세부는 [미확인 정밀도].

## BIOP02와의 관계 (굵게 = 직접 스쿱)
- **같은 코호트 방향: TCGA-BRCA를 외부검증 타깃으로 사용**(우리 Paper A/C도 TCGA-BRCA).
- **같은 방법군: pathology FM × attention-MIL, BRCA, 외부검증** — 우리 예측 스택과 동형.
- **우리가 "공짜 재사용"으로 기대한 예후/ROR-P 재사용 슬롯(B4)을 우리 데이터로 우리 실험(12 FM × ABMIL, 외부검증)으로 이미 출판** → **prognosis-from-H&E 축은 스쿱 확정, 진입 금지.**

## 차별점 (우리의 방어선 — 축 자체를 바꾼다)
- **핵심: 우리는 예측기가 아니다.** MAKO = "H&E → 재발위험 점수(정확도 리더보드 + 해석)". 우리 = **cost-of-substitution 결정지도** — 값싼 H&E-예측 표현형이 분자검사를 대신할 때 *치료 랭킹 충실도*를 얼마나 잃는지(luminal 안전 / HER2 붕괴)를 Critic-gated·hypothesis_only로 지도화. **ROR-P/재발위험 예측은 우리 claim이 아니다.**
- "us too, but with interpretability/governance" 금지 — 그 문장은 스쿱으로 직행. **다른 축(치환-비용 의사결정)** 으로만 포지셔닝.
- MAKO의 회귀 외부검증 실패는 *우리 진입 기회가 아니다*(분류+생존은 유지되므로 축은 여전히 점유됨). 우리는 이 축에서 경쟁하지 않는다.

## 인용 포인트
- **standing FM benchmark**로 인용: "H&E→재발위험/예후 예측은 이미 외부검증까지 포화"([MAKO]) → 우리는 또 하나의 정확도 리더보드를 만들지 않는다는 근거.
- **HIPPO를 counterfactual 방법 선례로 인용**(아래 methodology-brief 참조) — patch 제거로 예측 이동을 보는 방식이 우리 Critic #3(counterfactual)과 개념적으로 동형.
- **C3 자기방어:** 우리 novelty 문서 C3가 연속 ROR-P/proliferation residual을 비용지도 입력으로 쓴다 → ROR-P를 건드리면 반드시 MAKO를 predictor-of-record로 인용하고 "결정지도 입력"으로 프레이밍, **"ROR-P 예측 신규성"으로 절대 프레이밍 금지.**

## 검증 플래그
헤드라인 수치 모두 PMC12895011(Version of Record)에서 확인 + 로컬 abstract 파일과 이중 확인: 12 FM+2 baseline, CBCS ER+/HER2- n=847→TCGA n=613, CONCH 분류 CBCS 0.809/TCGA 0.850, H-optimus-0 회귀 CBCS r=0.638, TCGA 회귀 유의 0, 생존 C-index 동등. 컷포인트(11.76/52.94)·고위험 patch(120개/2.0mm²)·재발 107/847 = 단일 WebFetch 요약 근거라 **[미확인 정밀도]** — 인용 시 원문 표 재확인.
