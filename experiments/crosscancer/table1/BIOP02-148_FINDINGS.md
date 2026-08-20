# BIOP02-148 — Table 1(코호트 특성표) 5암종

`claim_level: descriptive`(가설 검정 아님, 사전등록 대상 없음) · jamie, 2026-08-20

## 범위

티켓 본문 그대로 전체 범위(축소 옵션 미사용) — 5암종(유방·폐·대장·위·두경부) × 환자수/
슬라이드수/train·holdout/나이/성별/stage/grade/tissue source site 수 + 엔드포인트별
유병률·결측·assay source + participant flow. 신규 모델링·통계 검정 없음 — **전부 이미 커밋된
정본 파일에서 집계만** 했다(가설 검정이 아니므로 결과-보기-전 사전등록은 생략, 대신 "숫자는
전부 기존 파일 인용, 재계산 없음"을 아래 산출물 자체에 명시).

## 산출물

- `fetch_table1_clinical.py` → `table1_clinical.json` — age/sex/stage/grade/TSS site
  (cBioPortal PATIENT+SAMPLE level, 5개 study). **정정 1건**: GRADE·TISSUE_SOURCE_SITE_CODE는
  PATIENT-level이 아니라 SAMPLE-level 속성임을 최초 실행에서 0건으로 확인 후 발견(팀 기존
  `sh_fetch_labels.py`가 이미 같은 패턴 사용 — 뒤늦게 확인). 재실행 후 정상 값 확보.
- `build_table1.py` → `table1_master.json`(정본) + `TABLE1.md` + `PARTICIPANT_FLOW.md` —
  기존 `patient_labels.csv`/`split.csv`/`tcga_brca_manifest.csv`/`mil_cost_results.json`에서
  집계, 신규 라벨 없음.
- `check_table1_numbers.py` — DoD "결과 파일과 1:1 대조" 자체 검증(아래 결과 참조).

## 핵심 발견 — 결과 파일과의 대조

`check_table1_numbers.py` 실행 결과 **불일치 0건**:
- Table 1b의 holdout n_pos·n_holdout 6개 암종×엔드포인트 전부 `mil_cost_results.json`(정본)과
  정확히 일치.
- **`manuscript/sections/02_results.md`의 R2 표(축별 홀드아웃 양성 표본 6행)와 R1 prose가
  인용한 헤드라인 n_pos(폐 LUSC 153·두경부 HPV 26·두경부 grade 41) 전부 Table 1과 1:1
  일치** — 이게 DoD의 "본문·표 R1/R2와 분모 불일치 0건" 항목이다. 원고가 이미 실측 수치를
  쓰고 있었고 이번 Table 1이 그걸 독립적으로 재확인한 셈이다(원고를 보고 베낀 게 아니라
  `mil_cost_results.json`에서 각자 계산 → 우연 일치가 아니라 같은 정본을 공유).

## 결과 요약

Table 1 전문 = `TABLE1.md`, 참여자 흐름 = `PARTICIPANT_FLOW.md`. 주목할 점만:

1. **grade 커버리지가 암종마다 극단적으로 다르다.** 위(440/440, 100%)·두경부(519/523, 99%)는
   완비, 유방·폐·대장은 **0%**(cBioPortal `GRADE` 속성 자체가 이 3개 study엔 없음 — 체리피킹
   아니라 실측 확인, BIOP02-140에서 폐도 같은 걸 이미 확인했음). 이걸 Table 1에 그대로
   드러내는 게 "결측을 숨기지 않는다"는 프로젝트 원칙에 맞다고 판단해 각주 없이 표 자체에
   0.0%로 명시했다.
2. **PAM50은 이진 유병률 정의가 안 된다.** 초안에서 "positive=Normal-like 제외"로 억지로
   이진화했더니 100%가 나와(정의상 당연) 무의미했다 — 5-class 분포(LumB 321·LumA 243·
   Basal 198·HER2 120)로 바꿔 표기했다. 이 실수는 결과를 보기 전에 잡았다(집계 스크립트
   개발 중 이상값으로 발견, 발표용 숫자로 나가기 전).
3. **holdout denominator가 같은 암종 안에서도 엔드포인트마다 다르다**(티켓이 걱정한
   "endpoint denominator audit" 그대로) — 위는 lauren_diffuse n=58 vs msi_h n=107, 같은
   GASTRIC holdout 132명 중 라벨 있는 하위집합만 쓰기 때문. Table 1b에 암종별이 아니라
   엔드포인트별 행으로 분리해 이 차이가 보이게 했다.
4. **폐 KRAS-G12C 관련 교차확인**: `LUNG_NSCLC/full/SUBTYPE_BASELINE_NOTE.md`(2026-07-14,
   기존 산출물)가 이미 histology-only baseline 0.793(n_pos 15/315)을 봉인해뒀다는 걸 이번에
   확인했다 — R1 prose의 "조직형만으로 예측한 기준선 0.793"의 정확한 출처다. 방금 병합
   대기 중인 BIOP02-140(jamie, PR #136)이 이 기준선에 purity/stage/site를 더한 확장판
   (0.802)이라 서로 다른 카드지만 같은 결론(KRAS는 histology 편중)을 독립적으로 강화한다 —
   참고로만 남긴다, BIOP02-148 자체 스코프는 아님.

## Table 1 배치 판단 (DoD 항목)

**본문(main text) 권장.** TRIPOD+AI 13b는 baseline 특성표를 본문에 두는 걸 표준으로 삼고,
`02_results.md` R1 앞에 두는 게 자연스럽다(R0가 "다섯 암종 약 열다섯 endpoint"를 서술하는데
Table 1이 그 숫자의 근거가 됨). 다만 **원고 prose(`02_results.md`/`03_methods.md`) 직접
수정은 이번 PR에서 안 했다** — 다른 분들이 이미 쓰고 있는 살아있는 원고라 Owner≠Reviewer
취지상 배치·문구는 리뷰에서 합의 후 반영하는 게 맞다고 판단. 지금은 `experiments/crosscancer/
table1/`에 독립 파일로 두고, 리뷰 통과 후 원고 편입을 별도 커밋으로 제안.

## DoD 체크

- [x] Table 1 초안 (배치 판단 포함 — 위)
- [x] 모든 수치가 커밋된 결과 파일과 1:1 대조 — `check_table1_numbers.py`, 불일치 0건
- [x] 본문·표 R1/R2와 분모 불일치 0건 — 위 스크립트로 확인(6/6 R2행 + 3개 R1 인용 전부 일치)
- [x] participant flow — `PARTICIPANT_FLOW.md`
- [ ] **독립 리뷰: 박세진(sezinie000) 또는 지용기** — 아직

## 스킵/후속

- 유방 er/pr/her2/pam50은 holdout(val+test) 분리 없이 코호트 전체로 표기(Table 1b에 명시) —
  Paper A/B 코드가 CPTAC 외부검증을 별도로 쓰고 이 매니페스트 자체엔 holdout-전용 예측치가
  없어서다. 필요하면 후속으로 holdout만 분리한 값을 추가.
- assay-source 텍스트는 각 fetch 스크립트 주석·문서에서 인용(신규 조사 아님) — 표기가 틀리면
  리뷰에서 정정 부탁.
