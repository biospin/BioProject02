# BIOP02-96 #1 (data leakage) — kkkim 증거 제출

> braveji Critic 4차 재판정(PR #49) required_followups 대응. 2026-07-16, owner=kkkim.
> braveji SSH 키 부재로 서버 실파일·assert 로그만 미확인 상태였음 → 아래로 완결.
>
> **정정 (2026-07-17, braveji PR #50 리뷰 반영):** 아래 §② 표의 단위 표기가 부정확했다. split.csv는 **슬라이드가 아니라 case(환자) 단위**이고, "1 slide=1 patient" 서술은 틀렸다(HNSC 임베딩 manifest는 472슬라이드/450환자, 22환자가 다중슬라이드). **누수 판정(PASS)은 불변** — split이 case 단위라 patient-disjoint가 성립하고, 한 환자의 모든 슬라이드가 같은 split에 귀속되므로 슬라이드 누수도 없다. 근거만 정확히 고쳤고 결론은 그대로다. `overlap_assert.py`도 함께 커밋(기존엔 JSON 결과물만 있었음).

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
`experiments/crosscancer/<암종>/full/split.csv` (컬럼: case_id, tss_code, split) 기준, train/val/test 3분할 pairwise. **split.csv 한 행 = 한 case(환자)** — 아래 수치는 슬라이드가 아니라 case 수다.

| 암종 | cases (split.csv 행=환자) | train/val/test | **patient overlap** | **TSS overlap** | 판정 |
|---|---|---|---|---|---|
| LUNG_NSCLC | 1050 | 735/158/157 | **0** | **0** | PASS |
| COLORECTAL | 534 | 374/80/80 | **0** | **0** | PASS |
| HEADNECK_HNSC | 523 | 366/79/78 | **0** | **0** | PASS |
| GASTRIC_STAD | 440 | 308/66/66 | **0** | **0** | PASS |

**ALL_PASS = True.** patient(case_id) disjoint **및** TSS site-disjoint 모두 4/4 암종 통과 — Howard PreservedSiteCV 불변식(patient-overlap==0) 충족.

**슬라이드 vs case (누수와 무관함을 명시):** split은 **case 단위**로 정의된다. 임베딩 manifest의 슬라이드 수는 이 case 수와 별개다(§① 참조: 예 HNSC 472슬라이드 / 고유 450환자 / 22환자 다중슬라이드). 한 환자의 모든 슬라이드는 그 환자의 split을 그대로 상속하므로, case-disjoint가 성립하면 슬라이드 단위 누수도 발생하지 않는다. (HNSC train 커버리지 결손 19.7%는 누수가 아니라 학습분포 편향 이슈로 별도 followup에서 다룬다.)

- 기계 판정 원본: `patient_overlap_assert.json` (라벨 `n_cases` = split.csv 행 수)
- 재현 스크립트: `overlap_assert.py` (split.csv만 입력, 결정론적). `python overlap_assert.py` → 위 표 + JSON 재생성.

## 판정
#1 data_leakage의 두 미결(실파일 서버검증 · patient-overlap assert 로그)이 **owner=kkkim 제출로 완결**. braveji 확인 후 #1 caution→pass 상신 가능.
