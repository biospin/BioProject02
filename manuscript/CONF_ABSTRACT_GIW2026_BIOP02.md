# GIW/ISCB-Asia 2026 — BIOP02 (Paper C) 학회 초록

> **상태**: 초안. 팀 확정 전. BIOP02-142.
> **마감**: 2026-08-15 23:59 AoE (no extensions). 채택 통보 09-16. 사전등록 09-30.
> **제출 형식**: 200단어 블라인드 초록. 신청 (ii) talk and poster. 트랙 Multi-omics Integration and Foundation Models. 제출 시스템 Oxford Abstract.
> **블라인드**: 저자·소속·직위·연구비 미기재. 사사(Pseudo Lab)는 정본 원고·camera-ready 에만.
> **수치 출처**: 전부 `manuscript/DRAFT_paperC_full_en.md` (UNI canonical). 이 파일에서 새로 만든 수치 없음.

---

## Title (EN)

When is it safe to replace a molecular test with H&E? A cost-of-substitution frame across five cancers

## Abstract (EN) — 197 단어

AI models can read molecular status from H&E histology. That does not license replacing the test, and we find almost nowhere that it does. The field reports how well a phenotype is predicted, not what happens when the prediction is wrong: which treatment the patient gets instead. We measure that. Our cost-of-substitution frame turns each prediction error into a misassignment under a treatment routing fixed in advance. Patient scores came from attention-based multiple-instance learning over foundation-model tile embeddings, evaluated under one pre-registered, site-disjoint protocol across five retrospective TCGA cancers against a five-seed label-shuffled null. Of about fifteen axes, one confirmation survived: head and neck HPV, holdout AUROC 0.959 with 26 positives, and even that cleared the null in only two of three foundation models. The frame also disqualified an apparent success: lung histology scored 0.939, but institution codes match the label perfectly, so morphology and site signature cannot be told apart. Breast HER2 (0.599) misassigned every anti-HER2 candidate. Most actionable axes had fewer than 25 positives and stay undecided; we did not lower the threshold. Judged by substitution safety rather than predictability, only one axis held. The rest need the molecular test itself, not an AI substitute.

---

## 제목 (KO)

분자검사를 H&E로 대체해도 안전한 때는 언제인가: 5개 암종에 적용한 치환비용 프레임

## 초록 (KO) — 176 단어

AI 모델은 H&E 조직형태에서 분자 상태를 읽어낸다. 그러나 읽어낼 수 있다는 것이 검사를 대체해도 된다는 뜻은 아니며, 대체해도 되는 자리는 거의 없었다. 이 분야는 표현형이 얼마나 잘 예측되는지를 보고할 뿐, 예측이 틀렸을 때 환자가 대신 어떤 치료를 받는지는 말하지 않는다. 우리는 그것을 측정한다. 치환비용 프레임은 예측 오류 하나하나를 사전에 고정한 치료 라우팅에서의 오배정으로 환산한다. 환자별 점수는 파운데이션 모델 타일 임베딩 위에 얹은 어텐션 기반 다중 인스턴스 학습으로 얻었고, 사전등록된 site-disjoint 프로토콜 하나를 후향적 TCGA 5개 암종에 동일하게 적용했으며, 엔드포인트마다 라벨을 섞은 5시드 귀무분포와 대조했다. 약 15개 축 가운데 살아남은 확증은 하나였다. 두경부 HPV로 홀드아웃 AUROC 0.959, 양성 26명이다. 그마저도 파운데이션 모델 3종 중 2종에서만 귀무분포를 넘었다. 이 프레임은 잘 맞아 보이던 결과 하나도 탈락시켰다. 폐 조직형은 0.939를 기록했으나 기관 코드가 라벨과 완전히 일치해 형태학과 기관 서명을 구분할 수 없다. 유방 HER2는 0.599로, 항HER2 후보를 전부 오배정했다. 임상적으로 중요한 축 대부분은 홀드아웃 양성이 25에 못 미쳐 미결로 남았고, 우리는 임계를 낮추지 않았다. 예측 성능이 아니라 치환의 안전성으로 하나씩 따져 본 결과, 유의하게 살아남은 축은 하나뿐이었다. 나머지 축에서는 AI 예측으로 대신한 검사가 아니라 실제 분자검사가 필요하다는 것을 확인했다.

---

## 수치 대조표 (초록 ↔ 원고)

| 초록의 수치 | 출처 (`DRAFT_paperC_full_en.md`) |
| --- | --- |
| HPV 0.959 · 양성 26 | R1 "head and neck HPV reached AUROC 0.959 [0.921-0.986] with 26 positives" |
| 3종 중 2종 통과 | R1 각주 † · R5 표 (Virchow2 real 0.9199 < 임계 0.9234) |
| 폐 조직형 0.939 · 기관코드 완전 일치 | R1 "lung LUSC histology 0.939" · 각주 ‡ "V(site, label) = 1.000" |
| 유방 HER2 0.599 · 전부 오배정 | R1 "Breast HER2 is 0.599" · R3 "anti-HER2 misassignment rate 1.00" |
| 양성 25 미만 미결 | R2 표 (EGFR 15 · KRAS 14 · ERBB2 14 · MSI 24 · EBV 7 · HNSC EGFR 17) |
| 임계 미하향 | R2 "Gastric MSI came one patient short at 24, and we did not lower the criterion" |
| 약 15개 축 | R0 "about fifteen endpoints across five cancers" |

## 제약 검증

* 단어수 **EN 197 / KO 176** (공백 분할, 상한 200).
  * ⚠️ 제출 시스템이 하이픈을 단어 경계로 세면 **EN 207**이 되어 반려된다. Oxford Abstract 입력창의 실시간 카운트를 반드시 확인할 것.
  * 초과 시 자를 순서: ① 암종 나열 없음(이미 제거됨) → ② 오배정 손실 정의절 `meaning ...` → ③ 방법 문장의 `attention-based` 수식.
* 문장부호 대시(em/en dash) **0개**. 하이픈은 복합어 철자라 유지(`site-disjoint`, `anti-HER2`, `cost-of-substitution` 등).
* 블라인드 위반 없음.

## 2페이지 long abstract 로 넘긴 것 (구두 신청 시)

초록 200단어에 들어가지 못했으나 원고에 있는 것들. 넣을 자리를 미리 정해 둔다.

1. **폐 KRAS-G12C 0.681 < 조직형만 쓰는 기준선 0.793** — 양성 14명이라 우리 규칙상 미결 축이므로, 결론이 아니라 관찰로만 쓴다.
2. **Yale pCR 0.533 [0.411, 0.653]** — 탐색적 결과 확인이며 독립 검증이 아니다. Farahmand 0.80에 못 미친다고 명시.
3. **Cramér's V = 0.378** (HPV site-라벨 구조) — 초록에서는 "3종 중 2종"만 남겼다.
4. **음성 결과의 모델 무관 재현** (Lauren 실패·ERBB2 무신호가 3종 모두에서) — 원고 R5 근거. 초록에 넣기엔 자리가 없었다.
5. **operating point 미완성** — 오배정률 1.00의 해석이 임계에 의존하며 사전정의 분석(BIOP02-138)이 미완이라는 사실. 초록에서는 수치 해석을 안 하는 방식으로 우회했다.
6. 그림 우선순위: **Fig2(결정지도) + Fig4(검정력 천장)**. 지도보다 지도를 만든 증거가 먼저다.

## ⚠️ 쓰면 안 되는 문장 (카운슬 검토에서 걸러낸 것)

* ~~"Across models, endpoint ranking was perfectly preserved (Spearman 1.000), proving failure modes reflect task structure rather than architecture."~~
  Gemini 제안이나 **기각**. (a) Spearman 1.000은 폐 세 엔드포인트 한정이고, (b) 원고 R5가 "순서 안정성이지 모델 일반성도 확증도 아니다"라고 명시하며, (c) 같은 초록의 "HPV는 3종 중 2종만 통과"와 자기모순이다.
* ~~"its apparent power comes from subtype skew rather than mutation morphology"~~
  KRAS는 양성 14명으로 **미결 축**이다. 미결 축에 기전 결론을 붙이지 않는다.
* ~~"failed to stratify ... in an external cohort"~~
  Yale은 **탐색적 결과 확인**이지 독립 검증이 아니다.

## 검토 이력

* 2026-08-11 · 이건규 초안.
* 2026-08-11 · GPT(codex gpt-5.5)·Gemini(Antigravity) **독립 적대 검토**. 서로의 답을 보지 않은 1라운드.
  * 두 모델이 **독립적으로 겹친 지적 3건** 전부 반영: KRAS 단정 · anti-HER2 operating point 한정 누락 · Yale "external cohort" 표현.
  * 둘 다 `retrospective` 명시를 권고 → `five retrospective TCGA cancers` 로 반영.
  * 놓친 강점에서 갈림: GPT = 폐 조직형 site 감사(**채택**), Gemini = Spearman 1.000(**기각**, 위 참조).
  * 둘 다 `we did not lower the threshold` 를 삭제했으나 **유지**. 어느 쪽도 삭제 이유를 대지 않았고, 이 문장이 숫자 나열을 변명에서 규율로 바꾼다.
* 다음: **kkkim critic** (Owner ≠ Reviewer. BIOP01 초록은 이건규가 검토했으므로 교차).

관련: BIOP02-142 · BIOP01-86(학회 정보·결정) · BIOP01-87(BIOP01 초록) · BIOP02-121(게재 요건) · BIOP02-138(operating point)
