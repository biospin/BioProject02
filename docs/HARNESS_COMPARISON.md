> **공용 자산 안내:** 이 비교표는 논문 생산 하네스(BioProject01·02 공용)의 3자 대조입니다. 특정 프로젝트 소유가 아니며, 공용 홈(전용 스페이스/레포) 확정 시 이관 예정 — 현재는 리뷰 편의상 BIOP02 docs/에 임시 게시. 검토 티켓: BIOP02-100.

# 논문 생산 하네스 — 원본 · BioProject01 · BioProject02 상세 비교

*Designed by Ka-Kyung Kim, 2026 (CC BY 4.0). 같은 재사용 스캐폴드를 분야가 다른 두 프로젝트에 얹은 모습.*
*용어: **원본** = 모든 복사본이 갈라져 나온 기준 레포(upstream, github.com/kakyungkim/paper-production-harness).*

## 1. 구조 한눈에

원본은 **도메인 무관 제네릭 에이전트 + 프로젝트가 채울 FILL 템플릿**으로 구성된 재사용 스타터킷이다. 각 프로젝트는 여기에 **도메인 분석 슬롯 1개**를 꽂고 템플릿을 자기 분야로 채워 인스턴스화한다.

| | 원본 (paper-production-harness) | BioProject01 (단일세포 속도) | BioProject02 (병리 H&E) |
|---|---|---|---|
| 성격 | 재사용 스타터킷 | 인스턴스 | 인스턴스 |
| 도메인 분석 슬롯 | 없음(`<DOMAIN_ANALYSIS_AGENT>` 자리) | `hspc-velocity-analyst` | `spatialpatho-analyst` |
| 결과 요약(예시) | — | `pipeline/hspc-velocity-benchmark/results/FINDINGS.md` | `experiments/crosscancer/GASTRIC_STAD/full/LAW_TEST.md` |
| 검증 게이트 | 템플릿(FILL) | 헤드라인 재계산 스크립트(속도 지표) | 헤드라인 AUC/AUPRC 재계산 |
| 브랜치 | main | kkkim-pipeline | docs/BIOP02-53-kkkim-critic-review |

## 2. 에이전트별 상세 (3자 대조)

| 에이전트 | 층위 | 원본 | BioProject01 | BioProject02 | 차이 요약 |
|---|---|---|---|---|---|
| **design** | 제네릭 | 브랜드·로고·그림 미감 | = 원본 | = 원본 | 세 곳 동일 |
| **literature-scout** | 제네릭 | 선행연구·포지셔닝·related work | = 원본 | = 원본 | 세 곳 동일 |
| **paper-critic** | 제네릭 | 제출 전 적대적 검수 + 그림 QA | = 원본 | = 원본 | 세 곳 동일 |
| **novelty-strategist** | 제네릭 | 차별화 각도를 (novelty×feasibility×defensibility)로 랭킹 | 여기에 **"defensibility triple"** 추가: 각도마다 (a)반증기준 (b)가장 싼 make-or-break 테스트 (c)리뷰어 최강공격, **테스트 통과 전 headline 승격 금지** | = 원본(baseline) | BIOP01이 방어 규율을 확장 |
| **research-methodologist** | 제네릭 | 가설·기여문·설계·감사; pre-mortem = 공격 나열 + 가장 싼 방어 | pre-mortem을 **make-or-break 게이트로 강화**: 헤드라인 주장은 가장 단순한 confound를 실제 partial-out해 못 넘으면 **정직하게 강등(post-hoc rescue 금지)** | = 원본(baseline) | BIOP01이 방법론을 확장 |
| **manuscript-writer** | 오버레이 | FILL 템플릿(17칸: 연구설명·결과경로·저자·disclaimer 등) | 속도 도메인으로 채움(FINDINGS.md·GSE 데이터셋 경로, 독립연구자 IP flag), FILL 2칸 남음 | 병리로 채움(WSI/AUC 경로, 팀 저자순서, Modulabs ack), FILL 7칸 남음 | 각자 도메인으로 인스턴스화(정상) |
| **presenter** | 오버레이 | 발표자료 생성 템플릿 | 속도 원고·결과 경로, RNA/ATAC/pseudotime 용어, velocity 헤드라인 예시, 블로그 house-style | 병리 경로, WSI/H&E/AUPRC 용어, H&E 헤드라인, Modulabs ack | 각자 도메인으로 인스턴스화(정상) |
| **paper-orchestrator** | 오버레이 | 멀티에이전트 **계획**만; 제네릭 골격 | 로스터에 `hspc-velocity-analyst`, verify-gate = 구체 명령(p3_*.py), 속도 standing stance | 로스터에 `spatialpatho-analyst`, verify-gate = FILL, BRCA·NOT-drug-response stance | 각자 config로 인스턴스화(정상) |
| **(도메인 분석 슬롯)** | 프로젝트 전용 | 없음(자리표시자) | `hspc-velocity-analyst` (속도 벤치마크 파이프라인) | `spatialpatho-analyst` (WSI→임베딩→표현형→치료근거) | 각 프로젝트 고유 — 재사용의 핵심 교체 지점 |

## 3. 읽는 법

- **제네릭 층(design·literature-scout·paper-critic·novelty-strategist·research-methodologist)** — 분야와 무관한 공통 로직. 이상적으로 세 곳이 같아야 하며, 실제로 3/5가 완전 동일하다. `novelty-strategist`·`research-methodologist`는 BIOP01이 "주장을 provisional로 내보내고 가장 싼 confound-격파 테스트를 통과해야 headline 승격"이라는 **make-or-break 게이트**를 추가로 얹은 상태(원본·BIOP02는 baseline).
- **오버레이 층(manuscript-writer·presenter·paper-orchestrator)** — 도메인 이름·결과 경로·검증 게이트·발표 stance·감사표기. 여기가 **갈리는 게 설계 의도**(원본의 FILL 자리를 각 분야로 채움).
- **도메인 분석 슬롯** — 각 프로젝트가 자기 분석 파이프라인을 대표하는 에이전트 1개만 꽂는다.

**요지:** 공유 코어는 거의 동일하고 얇은 프로젝트 오버레이만 분야별로 갈린다 — 같은 하네스가 단일세포 속도와 병리라는 완전히 다른 두 분야에서 **슬롯 교체 + 템플릿 채움만으로** 도는 것을 두 인스턴스 비교로 확인할 수 있다.
