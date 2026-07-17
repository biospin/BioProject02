# farahmand-2022-modpathol — Methodology Brief (재현·대조 가이드)

이 논문은 우리 **HER2 outcome anchor의 HEAD-TO-HEAD 벤치마크**다. 우리는 **동일한 Yale HER2 코호트(공개 TCIA HER2-TUMOR-ROIS)** 를 임베딩하고, **FROZEN TCGA-학습 phenotype 모델(Yale에 학습 X)** 에서 유도한 **anti-HER2 axis score**가 실제 trastuzumab pCR을 층화하는지 검정한다.

## A. 그들의 방법 (재현 대상 = 우리가 맞춰야 할 기준선)
```
병리의 수기 tumor ROI(invasive carcinoma)
   └─ 512×512 px @ 20× 비중첩 타일 (necrosis/in situ/benign 제외, fat/bg 타일 제거)
        └─ Inception v3 (transfer + full train; RMSProp lr0.1/wd0.9/mom0.9; rot+flip aug)
             └─ 타일별 HER2±(또는 response) 확률 → 평균 → 0.5 cutoff = slide label
```
- **HER2 상태:** Yale 188 slides(93+/95−) 학습 → CV AUC 0.90(CI 0.79–0.97); TCGA 187 독립 → 0.81(CI 0.73–0.84).
- **★우리 bar★ Trastuzumab 반응:** Yale **85(36 pCR/49 non)**, **5-fold CV AUC 0.80 (95% CI 0.69–0.88)**.
- CI = 1000회 bootstrap. **[미확인]** response 모델이 HER2 Inception 가중치 transfer인지 fresh train인지 미명시.

## B. 핵심 설계 차이 — 왜 우리 bar가 "0.80 초과"가 아닌가
| 축 | Farahmand (벤치마크) | BIOP02 (우리) |
|---|---|---|
| 학습 데이터 | **Yale에 직접 학습**(in-cohort 5-fold CV) | **Yale 미학습**, TCGA-학습 phenotype 모델 **frozen** 전이 |
| 출력 | black-box CNN 확률 | 해석가능 **anti-HER2 axis score** |
| 난이도 | 코호트 내부 fine-tuning 有 | **out-of-cohort·no fine-tuning → 구조적으로 더 어려움(핸디캡)** |

→ 그들의 **0.80은 in-cohort CV 천장**이고 우리 설정은 더 불리하다. 따라서 성공 기준은 **"0.80을 이긴다"가 아니라 "frozen-transfer AUROC가 0.80의 CI(0.69–0.88)에 도달/중첩하는가"**. point estimate가 0.80 아래라도 CI가 겹치면 벤치마크와 통계적으로 정합 — 이 프레이밍을 명시한다.

## C. 반드시 리포트할 것
1. **AUROC + bootstrap 95% CI** (그들과 동일하게 1000회) — CI 중첩 여부로 판정.
2. **HER2-probability baseline 대비 DeLong test.** 코호트가 **전부 HER2+**이므로 코호트 내에서 HER2 상태는 반응에 거의 비정보적 → HER2-prob이 올바른 null. axis score가 **HER2 양성 여부를 넘어서는** 반응 신호를 잡는다는 것을 DeLong 우위로 입증해야 진짜 기여(counterfactual 논리).
3. n=85·36/49 클래스 불균형 → AUROC와 함께 **AUPRC**도 병기.
4. `claim_level: hypothesis_only` + Critic pass 전 공유 금지. DRP 프레이밍 표현 금지.

## D. 데이터·재현 경로
- **데이터:** 공개 **TCIA HER2-TUMOR-ROIS** = status ROI + **85 response cohort의 pCR 라벨**(검증됨) → 우리 방식으로 재실행 가능.
- **모델:** 그들의 코드·가중치는 **비공개("upon request")** → 원모델 재실행 불가, **공개 AUC 수치와 대조만**. 우리는 frozen public FM(UNI)로 독립 파이프라인 구성.
- **주석 정합:** 그들 512px@20× / invasive-only ↔ 우리 tile_config(256×256@20×). 타일 크기·배율 차이를 대조 변수로 기록.

## E. 열린 리스크 (명시적 caveat)
- **[검증됨]** TCIA HER2-TUMOR-ROIS에 85 response cohort pCR 라벨 포함 → head-to-head 성립.
- **[미확인]** response 모델의 weight-transfer 여부 → 우리 baseline 재현 세부에 영향 가능.
- 벤치마크 자체가 n=85·외부검증 없음 → "0.80 도달"은 강한 주장이 아니라 provisional 신호로 서술.

## F. 검증 플래그
모든 수치 PMC10221954 확인: Inception v3·512px@20×·확률평균+0.5·188(93/95)·CV0.90(0.79–0.97)·TCGA187(92/95)0.81(0.73–0.84)·85(36/49)5-fold0.80(0.69–0.88)·bootstrap1000·code/data "upon request". TCIA response 라벨 포함 = TCIA collection 확인.
