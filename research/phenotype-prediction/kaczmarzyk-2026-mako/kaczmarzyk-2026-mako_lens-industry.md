# kaczmarzyk-2026-mako — Lens: Industry / Reproducibility

## 코드 가용성
- **GitHub: https://github.com/kaczmarj/MAKO** — 논문 분석 재현 코드 공개.
- **HIPPO**(perturbation 해석 도구)는 저자(Kaczmarzyk) 계열 방법 — 별도 재사용 가능(우리 counterfactual 게이트 선례로 참조).
- 백본 12종은 모두 **공개 pathology FM**(CONCH·UNI·Virchow/Virchow2·Prov-GigaPath·Phikon/Phikon-v2·H-optimus-0·CTransPath·Hibou-L·Kaiko-L/14·DiRLV2) → 임베딩 스택 자체는 재현 진입장벽 낮음(단 일부는 HF 게이팅).

## 데이터 가용성
- **TCGA-BRCA WSI: GDC portal**(open-access slides) — 우리 Paper A/C와 동일 출처. 외부검증 코호트라 재현 용이.
- **CBCS(Carolina Breast Cancer Study):** 학습 코호트. **접근 조건 [미확인]** — CBCS는 TCGA/GDC처럼 열린 공개 리소스가 아니라 연구참여 코호트라 데이터 사용에 별도 승인·협약이 필요할 수 있음(원문/저자 확인 필요). → **학습 재현은 CBCS 접근에 의존.**
- ROR-P 라벨: PAM50 전사체 → ROR-P 산출(assay-정의 값). 우리는 이 축을 재현할 이유 없음(진입 금지 슬롯).

## 재현성 평가
- 외부검증부(TCGA-BRCA)는 공개 슬라이드 + 공개 FM + 공개 코드라 **재현 가능**. 학습부(CBCS)는 코호트 접근이 게이트.
- 우리 관점에서 이 논문은 **재현 대상이 아니라 경계 표지(fence marker)** — B4 슬롯이 이미 외부검증까지 점유됐음을 확인하는 용도.

## 우리가 재사용/참조할 것 (제한적 — 진입 금지 슬롯이므로)
1. **HIPPO(perturbation 해석)** — 우리 Critic #3 counterfactual 게이트의 **method 선례**로 인용/참조(재현이 아니라 개념 정렬). 상세는 methodology-brief.
2. **standing FM benchmark 수치** — "예측 축 포화"의 인용 근거(리더보드 재생산 금지).
3. FM×ABMIL 성능 편차(CONCH vs H-optimus-0 vs Virchow2) — Paper C의 "치환가능성 법칙 모델 비의존성" 검증 시 **참고 baseline 문헌**으로만.

## 산업/거버넌스 메모
- MAKO는 재발위험 점수를 직접 출력(예측기). 우리는 **동일 축을 재생산하지 않으며**, 출력은 cost-of-substitution 결정지도 + `hypothesis_only` + Critic pass. "predict recurrence/prognosis from H&E" 표현은 우리 산출물에서 금지(스쿱 축).
- BRCA-only(Paper A/B) 및 Paper C 5-암종 경계 준수 — MAKO는 BRCA 단일이라 Paper C cross-cancer 축과는 직접 겹치지 않음(anchor 암종 참고용).
