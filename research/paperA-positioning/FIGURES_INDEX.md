> ⚠️ **라벨 정리(2026-07-17):** "Paper A"는 독립 논문이 아니라 **Paper C(플래그십)의 유방 anchor 챕터**다(D11/D12 흡수, 2026-07-12). 아래 figure들은 C 유방 anchor의 그림으로 읽는다. 정본 = [`../paperC-positioning/PAPER_STRUCTURE_DECISION_2026-07-17.md`](../paperC-positioning/PAPER_STRUCTURE_DECISION_2026-07-17.md).

# Paper A(= C 유방 anchor) — Figure 레지스트리 / 버전 관리 (BIOP02-66)

**목적:** Paper A(cost-of-substitution) figure의 **단일 출처·버전 규칙**과 현재 상태를 한 곳에 정리. Confluence(VC) 공유의 근거 문서.
**관리자:** braveji(Orchestrator). **정본 figure 계획:** `research/paperA-positioning/2026-07-10_research-plan.md` §9.
**최종 갱신:** 2026-07-15 · 근거 = origin/main + 진행 중 PR.

---

## ⚠️ 먼저 — 이름 충돌 (반드시 인지)

Paper A가 **표현형 예측 → cost-of-substitution**으로 재정립되면서(2026-07-10), research-plan §9의 canonical Fig 번호와 **기존 파일명이 어긋난다**:

| 기존 파일 (구 프레이밍) | 구 의미 | 새 계획에서의 위치 |
|---|---|---|
| `fig3_baseline_comparison.png` | 표현형 AUC baseline 비교 | **Supplementary**(headline 아님) — 새 Fig 3 아님 |
| `fig4_external_sanity_lock.png` | CPTAC 외부 sanity | **Fig 4 후보**(positive-control) 또는 Supp |

→ 파일명의 `fig3/fig4`를 새 계획 Fig 3/4로 **혼동 금지**. canonical 번호는 아래 표 기준.

---

## Canonical figure 목록 (research-plan §9 기준)

| Fig | 제목 | 상태 | 소스 스크립트 / 산출물 | 담당 | JIRA |
|---|---|---|---|---|---|
| **Fig 1** | Pipeline + governance schematic (개념도) | ✅ **critic_status: pass** (braveji 서명 2026-07-21) — DRP framing·claim-level·사실정합·시각 QA 통과. 수치 주장 없는 도식 | `agents/modeling/scripts/make_fig1_pipeline.py` → `experiments/braveji/fig1_pipeline/fig1_pipeline.{png,pdf}` | braveji | BIOP02-62 |
| **Fig 2** ⭐ | label↔therapy 해리 2-panel (**최결정 그림**) | ⚠️ **critic_status: caution** (braveji 검증 2026-07-23) — 원자료 재현 전부 일치하나 근거 CI가 **슬라이드 단위**(pseudo-replication). **수정 4건 후 서명** — headline 승격 금지 | `experiments/kkkim/20260710_cost_of_substitution/make_fig2_confusion_distance.py` → `fig2_confusion_distance.{png,pdf,json}` | kkkim/sjpark | BIOP02-91 |
| **Fig 3** | 축별 cost + headline 대비 (cost bar + CI) | ⚠️ **critic_status: caution** (braveji 검증 2026-07-23) — 동일 근거 JSON. **표시 CI를 환자 단위 `[0.331, 0.427]`로 교체 필요**(현재 `[0.348,0.420]`은 과소). 결론(0 배제)은 유지 | `experiments/kkkim/20260710_cost_of_substitution/make_fig3_axis_cost.py` → `fig3_axis_cost.{png,pdf,json}` | kkkim/sjpark | BIOP02-91 |
| **Fig 4** | C2 positive-control recall + miss-rate | ⏳ 미착수 (fig4_external_sanity_lock는 구 프레이밍) | `experiments/sjpark/fig4_external_sanity_lock.png`(구), 재작성 필요 | sjpark | — |
| **Fig 5** (선택) | Dawood baseline 대조 | ⏳ 미착수 | — | — | — |

### Supplementary / exploratory (본문 아님)
| 파일 | 의미 | 소스 |
|---|---|---|
| `experiments/sjpark/fig3_baseline_comparison.png` | 표현형 AUC baseline 비교(Critic #2 시각화) | `agents/modeling/scripts/make_fig3_baseline_comparison.py` |
| `experiments/sjpark/fig4_external_sanity_lock.png` | CPTAC 외부 sanity lock | `agents/modeling/scripts/make_fig4_external_sanity_lock.py` |
| `experiments/kkkim/angle_A_spatial_erbb2/fig_erbb2_floor{,_v2}.png` | ERBB2 spatial floor 탐색 | `make_fig_erbb2_floor.py` / `make_fig_v2_forest.py` |

---

## 버전 관리 규칙

1. **단일 출처:** 모든 본문 figure는 **재현 스크립트(`make_*.py`)로 생성**하고 스크립트를 git에 커밋한다. 손편집 PNG 금지.
2. **파일명:** `figN_<slug>.{png,pdf,json}` (N=canonical 번호). png(뷰)+pdf(벡터, 제출용)+json(메타: 이슈·프레이밍·소스) 3종 동반 권장.
3. **경로:** 산출물은 `experiments/<owner>/...`에 두고, canonical 매핑은 **이 문서**가 단일 소스. (파일을 옮기지 않고 여기서 번호를 부여 — 이동 시 링크 깨짐 방지)
4. **버전 승계:** 게시된 figure는 덮어쓰지 않는다. 갱신 = 새 커밋(+ 필요 시 `_v2`), 구본은 supersede 표기. git 이력이 버전 관리.
5. **프레이밍 규율(CLAUDE.md):** hypothesis-only, NOT a DRP model, 성능수치 없는 스키마 그림엔 수치 미기재. headline claim은 provisional 표기.
6. **QA:** 커밋 전 렌더 PNG를 **육안 확인**(텍스트 오버플로·클리핑·겹침·tofu). (Fig 1에서 제목 오버플로 1건 잡음.)

## Confluence 게시 (완료조건)
- VC 스페이스 figure 페이지에 canonical 표 + 최신 PNG 게시. 상태: **이 레지스트리 페이지 게시** → 이미지 첨부는 후속(REST attachment).
- 블로그 6편은 이미 Confluence 게시됨(별건).

## Critic 서명 현황 (2026-07-23)

| Fig | critic_status | 서명/검증 | 잔여 |
|---|---|---|---|
| Fig 1 | **pass** | braveji 2026-07-21 | — |
| Fig 2·3 | **caution** | braveji 2026-07-23 (원자료 재현 일치) | 아래 4건 |
| Fig 4·5 | — | 미착수 | 산출 자체 |

**Fig 2·3 pass 승격 조건 (kkkim, BIOP02-91 코멘트 11395 / PR #70):**
1. 🔴 `headline_contrast.ci95`를 **환자 단위**로 교체 — n=294는 슬라이드이고 고유 환자는 **95명**(평균 3.09장). 슬라이드 단위 부트스트랩은 pseudo-replication으로 CI를 **1.32× 과소**. 환자 클러스터 = `[0.331, 0.427]`. **결론(0 배제)은 불변.**
2. `pred_source` 개인 홈 절대경로 → repo-relative
3. 라우팅 임계 `0.5` 명시
4. CI 메타(B·seed·리샘플 단위) 기재

근거·재현 스크립트: `experiments/braveji/BIOP02-91_cost_verification/`

## 남은 작업
- ~~Fig 2(최결정) 2-panel 확정~~ → ✅ 초안·main 병합(PR #63). ~~Fig 3 분리 산출~~ → ✅ 초안(2026-07-17). ~~Critic 검증~~ → ✅ 완료(caution, 위 4건 후 pass).
- Fig 4 positive-control 재작성 — sjpark.
- Confluence figure 페이지에 PNG 첨부 업로드 (REST attachment — Atlassian API 토큰 필요, 미보유).
