# Paper C 보고지침(reporting guideline) 체크리스트 — 참조자료

> **출처:** medsci-skills(Aperivue) `check-reporting` 스킬의 `references/checklists/`에서 **Paper C에 해당하는 것만 선별 복사**.
> **차용 근거:** 집필 스킬 벤치마크(`../pilot_writing_skills_2026-07-17.md`, 2026-07-18) — 이 체크리스트가 **유일한 차용 항목**이다(아래 §3).
> **성격:** 참조자료(reference)일 뿐 **자동 게이트가 아니다.** 준수 판정은 사람/Critic이 한다(검증 게이트 설계는 자작 유지 = `docs/HARNESS_REVIEW_2026-07-17.md` §4.5 원칙).

---

## 1. 왜 가져왔나 — 우리 하네스의 gap

Paper C는 **H&E 형태 → 분자 표현형을 맞히는 예측모델(prediction model)** 논문이다. 이런 논문에는 국제 표준 보고지침이 있다: **TRIPOD+AI**(예측모델 AI 확장). 그런데 우리 집필 하네스(`.claude/agents/manuscript-writer.md`·`paper-critic.md`·`agents/critic/checklist_v1.md`)에는 **이 표준 준수를 점검하는 항목이 없다**(2026-07-18 grep 확인 — 우리 "CLAIM"은 `claim_level` 뜻, "disclaimer"는 DRP-아님 뜻이라 다름).

즉 **분석 검증(7-point Critic)은 강하지만, "저널 표준대로 빠짐없이 보고했는가"는 아무도 안 본다.** 이 gap을 이 참조자료로 메운다.

## 2. 어느 체크리스트를 언제 쓰나 (Paper C 매핑)

| 파일 | 표준 | Paper C에서 언제 | 라이선스 |
|---|---|---|---|
| **`TRIPOD_AI.md`** | TRIPOD+AI 2024 | ★ **주 표준.** 초안 완성 후 전 항목 대조(제목·초록·배경·데이터출처·예측변수·결과·통계·모델·검증·한계) | CC BY 4.0 |
| `TRIPOD.md` | TRIPOD 2015 | TRIPOD+AI의 base(비-AI 항목 참조) | CC BY 4.0 |
| **`CLAIM_2024.md`** | CLAIM 2024 | ★ **의료영상 AI 특화.** H&E 이미지 파이프라인(타일링·전처리·모델·평가) 보고 완결성 | RSNA open access |
| `PROBAST_AI.md` | PROBAST+AI | 우리 스스로 편향위험 자기점검(리뷰어가 이걸로 우릴 볼 것) | CC BY-NC 4.0 (참조만) |
| `STROBE.md` | STROBE 2007 | Yale 앵커(관찰적 outcome 코호트) 섹션 보고 | CC BY |
| `_LICENSES.md` | — | 출처·인용정보(원고에 체크리스트 인용 시 필요) | — |

**우선순위: TRIPOD+AI > CLAIM > (Yale 섹션) STROBE.** PROBAST+AI는 자기방어용.

## 3. 벤치마크에서 "유일하게 차용키로 한 것" — 정리

집필 스킬 벤치마크(AIPOCH 605 + medsci 57, ~90종 census + 14종 정독) 결론:

- **차용 = 이 체크리스트 텍스트 1건뿐.** 나머지 집필 스킬은 전부 (a) 우리 `manuscript-writer` 중복·열등이거나 (b) 실행코드 없는 LLM 프롬프트.
- **⚠️ 차용 금지 1건:** AIPOCH `abstract-trimmer`가 `"to the best of our knowledge"`를 정규식으로 **무조건 삭제**(`main.py:38-42`, kkkim 실물 확인) → 정당한 스코프 hedge를 기계적으로 제거 = 우리 정직성 규율("hedge 격상 금지") **정면 위반**.
- **원칙 재확인:** 표준 체크리스트(기계적·공개표준)는 참조 차용 OK, 논지·프레이밍·검증 게이트는 자작 유지. 5개 영역(인용·재현성·병리·단일세포·집필) 벤치마크가 **전부 같은 결론**에 수렴.

## 4. 사용법 (집필 워크플로에 물리기)

1. **초안이 나오면**(manuscript-writer 산출 후) → `TRIPOD_AI.md`·`CLAIM_2024.md`를 열고 항목별로 "우리 원고에 있나 / 어디에"를 대조. 빠진 항목 = `<FILL>` 또는 추가 집필.
2. **paper-critic 실행 시** 이 파일들을 함께 읽혀 "TRIPOD+AI 미충족 항목"을 지적하게 한다(프롬프트 보강). 단 **준수 판정은 사람 확인** — 스킬처럼 자동 PASS 찍지 않는다.
3. **원고에 표준 인용** — TRIPOD+AI를 썼으면 Methods/Reporting에 원 논문(Collins GS et al. BMJ 2024)을 인용(`_LICENSES.md` 참조). 이때 인용은 우리 `verify_citations.py`로 검증.

## 5. 한계 (정직)

- **미검증:** Paper C 원고가 아직 없어 실제 대조는 못 해봤다. 초안 나온 뒤 유용성 확정.
- 이건 **참조 텍스트**지 실행 도구가 아니다. "빠짐없이 봤다"는 사람이 책임진다.
- CC BY-NC(PROBAST_AI 등)는 비영리 참조만 — 우리 프로젝트는 학술 비영리라 OK지만 상업 배포 금지.
