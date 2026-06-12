# Lens: Industry / Deployment — Olsson 2022 Conformal Prediction

## 코드·재현성 / Code & reproducibility
**KR.** 코드 공개: `github.com/heolss/Conformal_analyses` (Zenodo 아카이브 `10.5281/zenodo.7147740`). 환자 WSI 원본은 프라이버시로 비공개지만 **익명 데모 데이터셋**이 GitHub/Zenodo에 동봉 → conformal 후처리 레이어 자체는 재현 가능. 베이스 모델(Inception-V3 앙상블, GBT)은 표준 스택.
**EN.** Code is open (GitHub + Zenodo DOI). Patient WSIs are withheld for privacy, but anonymized demo datasets ship with the repo, so the CP post-processing layer is reproducible even without the clinical cohort. Base model uses commodity components (Inception-V3 ensembles + gradient-boosted trees).

## 배포 관점의 매력 / Why it's deployment-friendly
- **베이스 모델 재학습 불필요.** Calibration set(여기선 train의 10%)만 떼어두면 어떤 기존 분류기에도 사후 부착 — CI/CD에 가볍게 끼움. 우리 UNI+phenotype head 파이프라인에 추론 시간만 추가.
- **추론 오버헤드 무시 가능.** Nonconformity score는 이미 계산된 softmax에서 즉시 도출; p-value 계산은 O(calibration 크기) 정렬 한 번.
- **운영 안전장치.** ε를 운영 SLA로 직접 노출(예: "암 검출 오류 ≤0.1%를 보장하되 ~22% 케이스는 사람 리뷰로 라우팅"). 제품 의사결정과 통계 보장이 1:1 매핑 — 규제/임상 거버넌스에 설명 용이.
- **분포 이동 모니터링 공짜.** 외부 scanner/lab에서 빈·다중 prediction set 비율 급증이 **데이터 드리프트 알람**이 됨(MLOps 모니터링 신호).

## 운영 리스크 / Deployment risks
- **Calibration 신선도.** Scanner·염색·코호트가 바뀌면 calibration이 stale → 보장 무효. 주기적 recalibration 운영 루틴 필요(우리: TCGA→CPTAC 전환 시 재보정 필수).
- **기권율 폭주.** OOD 입력에서 80%까지 flagged → 인간 검토 큐 폭증. ε와 인력 용량의 트레이드오프를 운영 지표로 관리.
- **소수 클래스.** 희귀 phenotype(HER2-E)의 calibration 표본 부족 → prediction set 불안정. class-balanced calibration 또는 Mondrian per-class 표본 확보 필요.

## BIOP02 적용 메모 / Adoption note
우리 스택에 그대로 이식 가능: frozen UNI 타일 임베딩 → phenotype head softmax → (Guo temperature scaling) → conformal layer → `claim_level`/`critic_status` 게이트. ε를 hypothesis 발화 임계로 노출하면 Critic의 "claim-level check"(checklist #7)와 자연 연동. 산출물 등록 시 calibration set 해시·ε·flagged-rate를 `metrics.json`에 기록 권장.

**판정.** Low-friction, model-agnostic, 운영 SLA로 직접 환산 가능 — 배포 측면에서 최고 등급 도입 후보.
