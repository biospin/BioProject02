# HuggingFace Foundation Model 접근 권한 신청 완료

> 작성: kkkim | 일자: 2026-05-17 | Sprint 0

---

## 개요

SpatialPathoAgent 임베딩 파이프라인에 사용할 병리 기반 파운데이션 모델 5종에 대해 HuggingFace 접근 권한을 신청하고 전종 승인 완료함. 신청 시 기관 이메일을 HF 계정 primary email로 설정 후 진행. 당초 계획의 Virchow v1 대신 최신 버전인 Virchow2로 대체 신청함.

---

## 모델별 신청 결과

### 1. UNI v1 (MahmoodLab, 1024차원, CC-BY-NC-ND 4.0)

- HF: https://huggingface.co/MahmoodLab/UNI
- 신청 방식: Intended Use 폼 작성 필요
- 결과: 즉시 승인 완료

### 2. CONCH (MahmoodLab, 512차원, CC-BY-NC-ND 4.0)

- HF: https://huggingface.co/MahmoodLab/CONCH
- 신청 방식: Intended Use 폼 작성 필요
- 결과: 즉시 승인 완료

### 3. EXAONE Path 2.0 (LGAI, 768차원, EXAONEPath NC)

- HF: https://huggingface.co/LGAI-EXAONE/EXAONE-Path-2.0
- 신청 방식: 공개 모델 — 별도 신청 절차 없음
- 결과: 즉시 사용 가능

### 4. Virchow2 (Paige AI, CC-BY-NC-ND 4.0) — Virchow v1 대체

- HF: https://huggingface.co/paige-ai/Virchow2
- 신청 방식: 이름 + 이메일 입력만 필요 (Intended Use 항목 없음)
- 결과: 즉시 승인 완료
- 비고: 라이선스상 상업적 주체는 저자 별도 연락 권고되어 있으나 즉시 승인됨

### 5. UNI2-h (MahmoodLab, 1536차원, CC-BY-NC-ND 4.0)

- HF: https://huggingface.co/MahmoodLab/UNI2-h
- 신청 방식: Intended Use 폼 작성 필요
- 결과: 즉시 승인 완료

---

## Intended Use 폼 작성 내용 (UNI / CONCH / UNI2-h 공통)

```
We are building a computational pathology pipeline that predicts
molecular phenotypes (ER/PR/HER2 status, PAM50 subtypes) directly
from H&E whole-slide images in breast cancer (TCGA-BRCA, CPTAC-BRCA).

We plan to evaluate multiple foundation models as tile-level feature
extractors, feeding embeddings into MLP and attention MIL classifiers.
The goal is to assess how well morphological features captured by
foundation models correlate with IHC-based molecular subtypes, and to
generate hypothesis-level therapeutic evidence via DepMap/GDSC transfer.

This is an independent collaborative research project targeting
peer-reviewed publication. Dataset: ~150 TCGA-BRCA slides (open
access). Academic, non-commercial use only.
```

---

## 비고

- 모든 라이선스는 비상업적 학술 연구 전용 — 논문 출판 외 사용 금지
- Virchow v1 → Virchow2 대체 건은 AGENTS.md 및 CLAUDE.md 업데이트 필요 (braveji 확인 요청)
