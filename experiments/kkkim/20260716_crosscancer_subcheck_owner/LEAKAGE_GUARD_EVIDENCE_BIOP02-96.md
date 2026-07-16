# BIOP02-96 #1 (data leakage) — kkkim 증거 제출

> braveji Critic 4차 재판정(PR #49) required_followups 대응. 2026-07-16, owner=kkkim.
> braveji SSH 키 부재로 서버 실파일·assert 로그만 미확인 상태였음 → 아래로 완결.

## ① /workspace 실파일 존재 (재현성 실증)
`/workspace/data/cache/biop02/crosscancer/` (공유 볼륨) 실측:

| 암종 | .npy 임베딩 | 용량 |
|---|---|---|
| LUNG_NSCLC | 1052 | 18G |
| COLORECTAL | 622 | 9.1G |
| HEADNECK_HNSC | 472 | 8.4G |
| GASTRIC_STAD | 442 | 7.0G |

→ braveji 보고 수치(LUNG 1052 / COLORECTAL 622 / HEADNECK 472 / GASTRIC 442)와 정확히 일치. embedding_path 이관(BLOCKER-5, /home→/workspace 43G) 실파일 확인 완료.

## ② patient-overlap assert (leakage guard)
`experiments/crosscancer/<암종>/full/split.csv` (컬럼: case_id, tss_code, split) 기준, train/val/test 3분할 pairwise:

| 암종 | slides | patients | train/val/test | **patient overlap** | **TSS overlap** | 판정 |
|---|---|---|---|---|---|---|
| LUNG_NSCLC | 1050 | 1050 | 735/158/157 | **0** | **0** | PASS |
| COLORECTAL | 534 | 534 | 374/80/80 | **0** | **0** | PASS |
| HEADNECK_HNSC | 523 | 523 | 366/79/78 | **0** | **0** | PASS |
| GASTRIC_STAD | 440 | 440 | 308/66/66 | **0** | **0** | PASS |

**ALL_PASS = True.** patient(case_id) disjoint **및** TSS site-disjoint 모두 4/4 암종 통과 — Howard PreservedSiteCV 불변식(patient-overlap==0) 충족. 1 slide=1 patient 구조라 slide/patient 누수 없음.

- 기계 판정 원본: `patient_overlap_assert.json`
- 재현: `python overlap_assert.py`(split.csv만 입력, 결정론적)

## 판정
#1 data_leakage의 두 미결(실파일 서버검증 · patient-overlap assert 로그)이 **owner=kkkim 제출로 완결**. braveji 확인 후 #1 caution→pass 상신 가능.
