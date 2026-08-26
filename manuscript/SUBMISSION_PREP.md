# 제출 준비 — Supplementary 인벤토리 · 플랫폼 사전 준비 (BIOP02-76)

**작성:** braveji (Orchestrator) · 2026-08-19 · 기한 2026-08-26
**타깃:** npj Precision Oncology (+ medRxiv preprint 동시)
**근거:** [`TARGET_JOURNAL_GUIDE.md`](TARGET_JOURNAL_GUIDE.md) · [`DRAFT_paperC_full_ko.md`](DRAFT_paperC_full_ko.md) L186–202 · [`SECTION_ASSIGNMENT_paperC.md`](SECTION_ASSIGNMENT_paperC.md)

> **이 티켓은 본문·완료조건이 비어 있었다.** 범위를 저널 가이드와 원고가 스스로 "예정"이라 적은 항목에서 역산해 정의했다. 아래 3절이 그 결과다.
> **정직 고지:** 이 문서는 *무엇이 있고 없는지의 목록*이다. 미존재 항목을 있다고 적지 않았고, 각 줄의 근거는 파일 실물이다.

---

## 1. Supplementary 구성 — 존재/미존재

저널 가이드가 지정한 것(`TARGET_JOURNAL_GUIDE.md` L26·L32·L34·L57·L76)과 원고가 예정으로 적은 것을 합친 전체 목록.

| # | 항목 | 상태 | 실물 근거 | 담당 |
|---|---|---|---|---|
| S1 | **보고 표준 매핑표 — TRIPOD+AI** | 🟢 **1차 완료(오늘)** | [`docs/reporting_checklists/TRIPOD_AI_mapping_paperC.md`](../docs/reporting_checklists/TRIPOD_AI_mapping_paperC.md) — 48항목 매핑(충족 21·부분 9·미충족 13·해당없음 5) | braveji |
| S2 | 보고 표준 매핑표 — CLAIM 2024 | ❌ 미착수 | `CLAIM_2024.md`는 **빈 원문 사본**(72행, 근거 참조 0건) | braveji |
| S3 | 보고 표준 매핑표 — PROBAST-AI | ❌ 미착수 | `PROBAST_AI.md` 동일 | braveji |
| S4 | 보고 표준 매핑표 — STROBE(Yale 절 한정) | ❌ 미착수 | `STROBE.md` 동일 | braveji |
| S5 | **Table 1 — 코호트 특성표** | ❌ 미작성 | 원고 L195 "예정"으로 자인. **저널 가이드가 "필수는 코호트 특성표"로 지목**(L34), TRIPOD 13b 필수 | 류재면(jamie) |
| S6 | 표 R5 — 다중 FM 비교 | 🟡 데이터 있음·표 미확정 | `experiments/crosscancer/MULTIFM_COMPARISON.md`·`CROSSCHECK_5SEED_MULTIFM.md` | kkkim |
| S7 | SFig1 — 다중 FM 순서 보존 | ❌ 미제작 | 원고 L193 "예정" | BIOP02-134 |
| S8 | Fig4 — 검정력 천장 | 🟡 **유사 그림 존재(단 학회용)** | `manuscript/figures/GIW2026_fig2_power_ceiling.{png,pdf}`는 스크립트 docstring상 **GIW 2026 long abstract 전용**이다(논문 Fig4 아님). 다만 v2에서 *"판정별 색 + 양성대조 빗금"*으로 고쳐 R2 판정 체계와 정합하므로 **재렌더 기반으로 적합**. 그대로 쓰지 말 것 | BIOP02-134 |
| S9 | Fig5 — HER2 오배정 상세 | ❌ 미제작 | 원고 L192 "예정" | BIOP02-134 |
| S10 | LOSO 탐색적 분석 | 🟡 러너 존재 | 원고 L71이 "Supplement에 탐색적으로 둔다"고 예고. `experiments/crosscancer/run_loso.py`(PR #108, braveji leakage 승인) | kkkim |
| S11 | 성능 상세 표(본문 표 최소화 대응) | 🟡 산출물 분산 | 저널 가이드 L32 "성능 상세는 supplementary로". 코호트별 JSON에 실측 존재 | kkkim |
| S12 | 사전등록 문서 | ✅ **존재** | `experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md` — **비교 논문 4편 대비 차별화 항목** | — |

**요약: 12항목 중 확실히 있는 것 2(S1·S12) · 부분 4 · 미존재 6.**

---

## 2. 제출 플랫폼 사전 준비

### 확인된 요건 (`TARGET_JOURNAL_GUIDE.md`)

- 온라인·완전 OA. **엄격한 단어수·페이지 제한 없음**, 간결 서술 권장.
- **포맷 요건은 게재 확정 시에만 적용** — 초기 투고는 심사에 적합하면 된다.
- 심사자는 **그림을 본문 적절한 위치에 삽입**한 형태를 선호.
- 구조: IMRaD, Results를 6–10개 주장형 소제목으로 분할 → **원고가 이미 R0–R7로 충족.**
- 본문 표는 최소, 상세는 Supplement로.

### ⚠️ 미확인 (문서가 스스로 표시한 것)

`TARGET_JOURNAL_GUIDE.md` L15가 **nature.com 저자 가이드 원문 크롤이 로그인 리다이렉트로 막혔다**고 적고 `<FILL: 저자 가이드 원문 수치>`를 남겨 두었다. 따라서 **초록 단어 상한·인용 스타일 등 세부 수치는 아직 근거가 없다.**

→ **투고 직전에 사람이 로그인해 원문으로 확정해야 한다.** 검색 요약을 규격으로 쓰지 않는다(발표자료를 기준으로 쓰지 않는다는 규율과 같은 종류).

### 제출 시 필요한 메타데이터 — **전부 미확정**

| 항목 | 상태 | 비고 |
|---|---|---|
| 저자 목록·순서 | ❌ | **최대 병목**(BIOP02-114). 이것 없이는 preprint도 불가 |
| 소속(affiliation) | ❌ | 동일 |
| Corresponding author + 이메일 | ❌ | 동일 |
| **Funding / Acknowledgments** | ❌ | **GPU 제공처(Modulabs) 명시는 자원 제공 조건**(`CLAUDE.md` Infrastructure). TRIPOD 22 필수 |
| 코드·모델 공개 범위 + 라이선스 | ❌ | TRIPOD 15-AI·21-AI. **FM 라이선스가 전부 비상업 학술**이라 가중치 재배포 가능 여부 별도 확인 필요 |
| 데이터 가용성 서술 | 🟡 | TCGA 공개 / Yale 접근 조건 기재 필요 |
| 윤리 승인·동의 | ❌ | 공개 데이터라 면제 가능성이 높으나 **명시 문구 필요** |
| 이해상충(COI) | ❌ | 저자 확정 후 |
| ORCID | ❌ | 저자 확정 후 |

**→ 9개 중 8개가 저자정보 확정에 연동된다.** 제출 준비의 임계경로는 기술 작업이 아니라 **팀 결정**이다.

---

## 3. 완료조건 (이 티켓)

이 티켓에 본문이 없었으므로 아래로 정의한다. 이견이 있으면 Leader가 조정한다.

1. ✅ **Supplement 구성 목록 확정** — §1 (오늘 완료)
2. ✅ **보고 표준 매핑 1건 이상 실물화** — S1 TRIPOD+AI (오늘 완료)
3. ✅ **제출 메타데이터 요구 목록 + 미확정 표시** — §2 (오늘 완료)
4. ⏳ **CLAIM 2024 매핑**(S2) — TRIPOD와 겹치는 항목이 많아 차이분만 하면 된다
5. ⏳ **저널 저자 가이드 원문 확정** — 사람이 로그인 필요(§2 미확인)

**BIOP02-79(S8 최종 정리)와의 경계:** -76은 *"무엇이 필요한지 목록화하고 만들 수 있는 것을 만든다"*, -79는 *"확정된 저자정보로 최종 패키지를 조립한다"*. 저자 확정 전에는 -79를 열 수 없다.

---

## 4. 다음이 봐야 할 것

- **가장 급한 산출물은 Table 1(S5)**이다. TRIPOD 필수이면서 저널 가이드가 "필수"로 지목했고, 담당(류재면)이 배정돼 있으며, 데이터는 이미 있다(코호트별 n·라벨 유병률·split).
- **저자정보 9건은 기술로 풀리지 않는다.** BIOP02-114가 열린 채로 남아 있는 한 -76·-79·preprint가 모두 대기한다.
- 보고 표준 매핑은 **하는 만큼 그대로 차별화**가 된다 — 비교 논문 4편이 전부 0건이다.
