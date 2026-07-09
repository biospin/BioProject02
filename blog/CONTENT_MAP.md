# BIOP02 콘텐츠 소스 맵 — 9편 → 주제별 6편

> 2026-07-09 재구성. 기존 9편(worklog식)을 서사 주제 6편으로 묶어 BIOP01 방식(초심자 재작성 → 보존 게이트 → 문체 윤문)으로 재작성한다.
>
> **사실(숫자·hedge)의 단일 원천 = 기록:** `experiments/kkkim/20260708_3way/comparison.md`·`comparison_report.json`(임베딩 비교), `experiments/kkkim/20260703_critic_biop02-53/critic_report.json`·`REVIEW.md`(모델링 Critic), `SESSION_LOG.md`, git 커밋. 원본 블로그는 `archive_2026-07-09_pre-reorg/`에 두고 서사 소스로만 재사용한다. **블로그와 기록이 어긋나면 기록이 정답.**

## 재구성 매핑 (원본 9 → 신규 6)

| 신규 편 | 슬러그 | 원본 편 | 사실 원천(record) | 작업자 |
|---|---|---|---|---|
| 1. 코호트에서 타일까지 (flagship) | `01_cohort-to-tile` | 원본1 | manifest(split_hash=5995f29d), tile_config.yaml, BIOP02-37/38, SESSION_LOG | kkkim |
| 2. 세 파운데이션 모델: UNI·CONCH·EXAONE | `02_three-foundation-models` | 원본2 + 원본4 | `20260708_3way/comparison.md`(AUROC·site), 커밋 69fe4ce(완료), f7b008a=stale, EXAONE 3함정 | kkkim |
| 3. 느린 건 GPU가 아니었다: 임베딩 I/O 가속 | `03_embedding-io-acceleration` | 원본3 | 56→15ms/타일, UNI 오차 0.0·CONCH 4e-6, 커밋 9f42561, BIOP02-38 | **kkkim** |
| 4. 임베딩을 믿기 전에: 배치효과와 외부검증 | `04_trust-batcheffect-external` | 원본6 + 원본5 | site macro-AUROC 0.9977[.9958-.9989], TSS 중복 0, CPTAC 653/653·1024d, 임시라벨 395/653·tumor 120/122, `DECISION_rule_adjustment.md` | kkkim |
| 5. 형태학이 분자 표현형을 맞히나: 모델링과 Critic | `05_modeling-and-critic` | 원본7 | `critic_report.json`·`REVIEW.md`: ER CLAM 0.901/무작위 0.526/mean 0.816/subtype_only 0.918(ceiling), HER2 ext 0.53·auprc 0.12, 판정 caution, 커밋 3f45ffd, PR#21 | 모델링=**sjpark**, 리뷰=kkkim |
| 6. 여섯 명이 한 서버에서: 인프라·협업·자동화 | `06_infra-collab-automation` | 원본7(infra) + 원본8(OpenClaw) | 서버 A100→A6000×3, /workspace 규칙, PR#15 merge(c1a56fe), OpenClaw 2026.5.18 런북 3함정 | infra=kkkim, **OpenClaw=braveji(BIOP02-85)** |

> 파일명 날짜는 재작성일 `2026-07-09`. 순번은 위 1~6. 예: `2026-07-09_BIOP02_01_cohort-to-tile.md`.

## 조직 원칙
1. **숫자·hedge는 record 원천에만 정본으로.** 6편은 그걸 옮길 뿐, 새 수치·주장을 만들지 않는다.
2. **주제별 묶음.** 원본2+4(임베딩 추출 세 모델), 6+5(신뢰성=배치효과+외부검증), 7infra+8(인프라·자동화)을 각각 한 서사로 통합. I/O 가속(원본3)·모델링Critic(원본7)은 독립 서사가 강해 단독 유지.
3. **flagship(01)이 프로젝트 전체를 framing** — 나머지 편은 그 위에서 개별 주제. 편끼리 교차링크(2편↔3편 I/O, 4편↔5편 외부검증).
4. **역추적성.** 각 편 하단에 record 문서·커밋 링크. 통합 편은 원 작업자 태그 유지.

## 게이트 (STYLE_CONTRACT §5)
- 각 편: `content-fidelity-auditor`(원본+record 대조, EXAONE 완료 커밋·작업자 귀속·hedge 포함) → `korean-style-rewriter`(문체) → (장문) `naturalness-reviewer`.
- 앵커(01)도 게이트 예외 없음.
