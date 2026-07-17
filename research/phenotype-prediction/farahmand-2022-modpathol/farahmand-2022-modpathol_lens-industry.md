# farahmand-2022-modpathol — Lens: Industry / Reproducibility

## 임상 적용 관점
- **가치 제안:** H&E는 ISH/IHC보다 훨씬 흔하게·값싸게 확보된다. H&E에서 HER2 상태(AUC 0.81 독립)와 trastuzumab 반응(AUC 0.80)을 예측하면 **분자검사 비용 절감·치료 선택 가속**이 가능 — BIOP02 "cost-of-substitution" 논지와 직접 정렬.
- **성숙도:** 반응 예측은 single-institution n=85·외부검증 없음 → **연구단계 신호**이지 임상 배포 도구 아님. 규제/임상 적용 전 다기관 전향 검증 필수.
- **워크플로 마찰:** 입력이 **병리의 수기 tumor ROI** → 자동화 안 됨. 실배포하려면 tumor-detection 자동화(우리 tiling+FM 파이프라인이 대체 가능한 지점)가 선결.

## 코드·데이터 가용성 (재현성 대비)
- **코드·데이터 = "available upon request"** (공개 repo/DOI 없음). → 원 Inception v3 모델을 **재실행 불가**, 공개된 AUC 수치와 **비교만** 가능. (dawood-2024-hids가 GitHub 공개인 것과 대조 — 우리 재현 전략이 달라진다.)
- **데이터는 공개됨:** Yale 코호트가 **TCIA HER2-TUMOR-ROIS**로 공개(HER2 status ROI + 85 response cohort의 pCR 라벨 포함, 검증됨). → **모델은 못 받아도 데이터는 받아** 우리 방식으로 다시 돌릴 수 있다. 이것이 head-to-head를 성립시키는 핵심.
- TCGA-BRCA(독립 HER2 테스트)는 GDC 공개 — 우리 Paper A scope와 동일 출처.

## BIOP02 재현/대조 시 재사용할 것
1. **공개 TCIA HER2-TUMOR-ROIS 다운로드** — 85 response cohort(36 pCR / 49 non) + status ROI. 우리 anchor의 실데이터.
2. **벤치마크 수치 고정** — trastuzumab 5-fold CV AUC 0.80(CI 0.69–0.88), HER2 status 0.90/0.81을 대조표에 명기.
3. **주석 정책 참조** — invasive carcinoma만, necrosis/in situ/benign 제외. 우리 tile QC·tumor mask 기준과 정합.

## 산업/거버넌스 메모
- 우리 출력은 **anti-HER2 axis score(hypothesis_only)** — "치료 반응 예측 도구"·"personalized therapy" 표현 금지(7-point #6). Critic pass 후에만 `#biop02-experiments` 공유.
- 차별화 서사: 이들은 **비공개 in-cohort 모델**, 우리는 **공개 TCIA + frozen public FM(UNI 등) + 해석가능 axis + 외부 적용** → 재현성·투명성에서 우위.

## 검증 플래그
코드/데이터 "upon request" = PMC10221954 Availability 문구 확인. TCIA HER2-TUMOR-ROIS의 response/pCR 라벨 포함 = TCIA collection 페이지로 확인(공개).
