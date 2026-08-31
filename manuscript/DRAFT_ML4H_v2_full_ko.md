<!-- 이 국문본은 영문 정본 `DRAFT_ML4H_v2_full.md`(v2)의 국문 인계본이다. 수치·구조는 영문 v2가 정본이며, 판단지점·게이트는 `DRAFT_ML4H_v2_CHANGELOG.md` 참조. -->

# Paper C — ML4H 2026 회람 초안 v2 (완전 IMRaD)

> **상태.** ML4H 2026을 앞둔 **kkkim(Leader) 검토** 및 팀 회람용 갱신 완전 초안이다. 제출본이 아니라 *검토 초안*이다. v1 완전 초안([`DRAFT_paperC_full_en.md`](DRAFT_paperC_full_en.md))과 상세 섹션 골격([`sections/`](sections/)) 위에, 최신 결과 파일(다중 FM 5-seed, BIOP02-147 염색 정규화, PAM50 라벨 출처 정합)에 맞춰 갱신하였다. 변경 내역 = [`DRAFT_ML4H_v2_CHANGELOG.md`](DRAFT_ML4H_v2_CHANGELOG.md).
> **모든 수치는 결과 파일에서 실측**한 값이며, 각 헤드라인 값에는 kkkim이 대조할 수 있도록 인라인 `<!-- src: ... -->` 주석이 붙어 있다. 기억이나 슬라이드에서 옮긴 수치는 하나도 없다. 상태 `hypothesis_only`, 후향적, `critic_status: pending`.
> **claim 규율.** Paper C는 사전등록된 다섯 암종 연구다(유방 앵커 + 폐·대장·위·두경부 — 열린 pan-cancer 아틀라스가 아니라 의도된 경계). 이는 약물 반응 예측(DRP) 모델이 **아니다**(약물 구조 입력 없음, 가설-전용 산출). 헤드라인 주장은 사전등록 법칙과 held-out 검정이 Critic 서명을 통과하기 전까지 **잠정**으로 유지한다.
> **Venue 주기.** 기존 프로젝트 산출물은 npj Precision Oncology + medRxiv를 타깃했다([`SUBMISSION_PREP.md`](SUBMISSION_PREP.md) L4). 이 초안은 두 타깃 어느 쪽에도 쓸 수 있도록 **venue-중립 완전 IMRaD**로 작성했으며, **ML4H 2026 분량/형식 제약은 `<FILL: ML4H 2026 CFP 원문 — 사람 확정>`**이다. 29 KB IMRaD 초안은 워크숍형 venue에는 압축이 필요할 것이다(Leader 결정).
> **저자 대면 메타데이터는 미확정.** 저자·저자순서·소속·corresponding author/이메일·funding/acknowledgments(GPU 제공처)·COI가 모두 `<FILL: 팀 확정>`이며, 공개 전 팀이 확정해야 한다.

---

## Abstract

조직병리(H&E) 영상으로 종양의 분자 표현형을 예측할 수 있다는 것과, 그 예측이 분자검사를 임상적으로 대체해도 된다는 것은 서로 다른 주장이다. 우리는 이 둘을 분리하는 cost-of-substitution 프레임을 제시한다. 예측 오류를 사전정의한 치료 라우팅의 오분류 손실(misassignment cost, 이하 오배정률 — 금전적 비용이 아니라 치료 배정이 얼마나 어긋났는지를 정규화한 값이다)로 환산하는 프레임을 다암종에 적용해, 두경부 HPV에서는 검정력을 갖춘 긍정 신호를 확인하고 다수 변이·증폭 축에서는 현재 자료로 판정할 수 없음을 정량화하였다. 유방을 앵커로 폐·대장·위·두경부를 더한 다섯 암종에서 사전등록된 형태학적 상관물 법칙을 같은 규약으로 봉인 검정하였으나, 검정력을 갖춘 확증은 제한적이다. 관찰 스펙트럼의 양 끝은 실측으로 고정된다 — 형태에 또렷한 축(두경부 HPV 홀드아웃 AUROC 0.959, 주모델 UNI의 사전등록 홀드아웃에서 검정력을 갖춘 유일한 비-대조 양성 결과이며, 폐 LUSC 조직형 0.939는 양성대조)과, 이 코호트·라우팅 정의에서 대체 지지 신호를 보이지 않은 음성 앵커(유방 HER2 0.599)가 그것이다. 유방 앵커에서 H&E-예측 아형으로 정한 항HER2 라우팅은 이 코호트·라우팅 정의에서 HER2 축을 일관 실패시켰고(오배정률 1.00), 이는 분자검사가 여전히 필수인 영역을 비용으로 보이는 정직한 음성이다. 이 HER2 축의 표현형 예측은 H&E 염색 정규화 아래에서도 여전히 우연 수준에 머물렀으므로, HER2 음성은 염색 변이의 아티팩트가 아니다(다만 라우팅/비용 단계 자체는 정규화 아래에서 재실행하지 않았다). 임상적으로 중요한 변이·증폭 축의 대부분은 우리의 사전등록 site-disjoint 분할에서 홀드아웃 양성 표본이 25에 미치지 못해 탐색적이다. 탐색적 결과 일부는 형태학적 상관물 가설과 양립하지만, 변이·증폭 축 전반에서 법칙의 방향성을 확정할 검정력은 없었다. 우리는 "예측 가능성"이 아니라 "대체 안전성"을 의사결정 기준으로 제안한다. 모든 산출은 후향적·가설 수준이며 전향 검증이 필요하다.

<!-- v2 change: Yale pCR 0.533 결과를 Abstract에서 삭제(critic_status pending → 잠정, 본문 승격 금지). HER2 음성의 염색 정규화 견고성 추가. -->

---

## 1. Introduction

조직병리 H&E 이미지를 AI로 분석하려는 연구는 디지털 병리의 확산과 함께 여러 장기에서 이루어져 왔다[CITE-I1]. CLAM 계열의 weakly-supervised multiple-instance learning이 퍼지면서[CITE-I2], 비뇨기암[CITE-I3]·유방암[CITE-I4]·췌장암[CITE-I5] 등에서 연구가 활발히 이루어졌고, 지식 증류와 병리 파운데이션 모델이 그 성능을 끌어올렸다[CITE-I6]. 그중에서도 이미지에서 조직의 분자 상태를 예측하려는 요구는 계속되어 왔다. 그 이유는 대체 대상 쪽에 있다. 분자 상태를 확인하는 통상적 방법인 IHC 염색이나 조직파괴적 분자검사는 대체로 비싸고 오래 걸리는 반면, H&E 염색은 상대적으로 저렴하고 통상 진료에서 이미 촬영된다[CITE-I7]. 그런데 이 분자검사들은 여러 암종에서 조기 발견·예후 예측·치료 방향 결정에 중요한 역할을 한다[CITE-I8]. 값싼 영상이 비싼 검사를 대신할 수 있다면 얻는 것이 크다는 뜻이다. 그리고 H&E로부터 분자 상태를 학습·예측할 수 있다는 것 자체는 반복적으로 입증되어 왔다[CITE-I9].

> **인용 채울 자리.** 후보는 `research/REFERENCE_LIST.md` 등재 slug 만 쓴다. 지어낸 인용 없음.
>
> | 표식 | 뒷받침해야 할 내용 | 배정 | 성격 |
> |---|---|---|---|
> | `[CITE-I1]` | 디지털 병리·computer-aided pathology 의 확산 | `nam-2020-digitalpath-intro` | 정식(리뷰) |
> | `[CITE-I2]` | weakly-supervised WSI 학습과 CLAM 계열 MIL의 확산 | `lu-2021-clam` · `ilse-2018-abmil` | 정식 |
> | `[CITE-I3]` | 비뇨기암(전립선·방광) H&E AI 연구 | `paik-2025-urologic-dp` · `cho-2026-prostate-br` | 정식·프리프린트 |
> | `[CITE-I4]` | 유방암 H&E WSI AI 연구 | `lee-2025-brca-recurrence` · `lee-2024-murss` · `lee-2023-receptor-status` | 정식·정식·학회초록 |
> | `[CITE-I5]` | 췌장 등 타 장기로의 확장 | `lee-2022-pdac-survival` | 학회초록 |
> | `[CITE-I6]` | 지식 증류·파운데이션 모델이 성능을 끌어올림 | `cho-2026-g2l` · `kim-2023-rckd` · `chen-2024-uni` | 정식 |
> | `[CITE-I7]` | IHC·조직파괴 분자검사의 비용·소요시간 부담 (H&E 대비) | **미확보 — 우선순위 높음** | |
> | `[CITE-I8]` | 분자검사의 조기 발견·예후·치료 방향 결정 역할 | **미확보 — 우선순위 높음** | |
> | `[CITE-I9]` | H&E로부터 분자 상태 예측이 반복 입증됨 | `coudray-2018-natmed` · `kather-2019-msi` · `kather-2020-actionable` · `naik-2020-natcommun` · `schmauch-2020-he2rna` | 정식 |
>
> `I1`·`I3`–`I5` 는 **분야가 여러 장기에서 활발했다는 넓이 근거**다. 학회 초록도 이 용도로는 유효하다.
> ⚠️ `I7`·`I8` 두 자리가 이 문단의 논지(비용 비대칭)를 떠받친다. 넓이 주장이 아니라 **구체적 사실 주장**이 실리므로 정식 논문이 필요하다.
> ⚠️ `cho-2026-g2l` AAAI 게재연도, `cho-2026-prostate-br` 최종 게재처 미확정.
> ⚠️ `lee-2023-receptor-status` 는 유방 수용체(HER2/ER/PR) 예측으로 본 연구 유방 앵커와 주제가 가장 가깝다. 넓이 인용으로 두되, Related work 에 선행연구로 한 문장 세울지 검토할 것.
> ⚠️ **자기인용 범위.** `paik-2025` `lee-2022/2023/2024/2025` `cho-2026-*` 는 주저자가 저자로 참여한 논문이다(9자리 중 `I3`·`I4`·`I5` 와 `I6` 일부). `nam-2020`·`kim-2023-rckd` 는 주저자가 저자가 아니다. 게재 단계에서 자기인용 비중을 한 번 점검한다.


우리는 cost-of-substitution 프레임을 제안한다. 예측 오류를 치료 라우팅의 오분류 비용으로 환산해, 각 분자 축에서 H&E가 값싸게 대체될 수 있는지 아니면 분자검사가 필수인지를 묻는다. 기준은 예측 가능성이 아니라 대체 안전성이다. 이 프레임은 약물 반응을 예측하지 않으며, 마커에서 치료 배정으로 가는 치환비용만 조작화하고, 약물 구조를 입력으로 받지 않는다.

이를 유방 앵커에 폐·대장·위·두경부를 더한 다섯 암종의 사전등록된 형태학적 상관물 법칙으로 검정한다. 법칙의 요지는, 어떤 분자 변이가 H&E 해상도에서 알아볼 수 있는 형태학적 상관물을 가질 때에만 H&E가 그 검사를 값싸게 대신할 수 있다는 것이다. 다섯 암종은 법칙을 검정하기 위한 의도된 경계이지 열린 pan-cancer 아틀라스 확장이 아니며, 예측을 결과 이전에 봉인하는 사전등록은 확증 강도 자체를 주는 것이 아니라 사후 선택을 억제하는 claim 규율을 제공한다.

이 논문의 기여는 넷이다. 첫째, 치환비용 프레임 그 자체와, 동일한 사전등록 규약 하나를 다섯 암종에 적용해 확증 가능한 축과 미결 축을 구분한 것이다. 둘째, 정직한 음성 앵커다 — 유방 HER2 축은 H&E 기반 대체를 지지하는 신호를 보이지 않으며, 이 음성은 H&E 염색 정규화에 견고하다. 셋째, claim 규율이다 — 우리의 사전등록 분할이 판정할 수 없는 다수의 변이·증폭 축에서 점수가 높게 나온 축만 보고하는 대신 검정력 부족을 명시적으로 판정한 것이다. 넷째, 예측 정확도 경쟁이 아니라 "언제 대체가 안전한가"라는 다른 질문의 정립이다. 유방 단일 코호트 예측[Fernandez-Romero 2026]이나 약물 감수성 예측[Dawood 2024]과 달리, 본 연구는 동일한 사전등록 평가 규약 하나와 치환비용 렌즈를 다암종 코호트에 적용하는 방법론적 틀을 기여한다. 외부 치료결과 점검(Yale pCR)과 공간전사체 기전 관찰은 기여가 아니라 잠정적·Critic 대기의 탐색적 분석(§R6, §R7)으로만 보고한다.

<!-- v2 change: 기여 목록을 다섯에서 넷으로 축소. v1 (iii) "Yale + ST 비용 증명"과 (iv) "Yale 앵커"를 독립 기여에서 제거 — Yale은 critic-pending, ST는 hypothesis_only. -->

---

## 2. Results

### R0. 이 논문이 실제로 세운 것

우리는 다섯 암종에서 약 열다섯 개 endpoint를 사전등록 아래 검정하였다. 그중 검정력을 갖춘 비-대조 확증은 정확히 하나, 두경부 HPV였다. 나머지 변이·증폭 축은 대부분 홀드아웃 양성 표본이 스물다섯에 못 미쳐 사전등록 규칙상 미결로 남았다. 따라서 본문은 "법칙을 다섯 암종에서 검증하였다"고 쓰지 않는다.

우리가 세운 것은 두 가지다. 하나는 지도의 양 끝을 같은 규약 아래 실측으로 고정한 것이다. 형태에 또렷이 보이는 축과 보이지 않는 축이 각각 무엇인지를 동일한 대조군·판정 기준으로 측정하였다. 다른 하나는 지도의 가운데를 지금 정할 수 없는 이유를 정량화한 것으로, 이것이 R2의 검정력 천장이다.

### R1. 사전등록 site-disjoint 분할에서 관찰한 다섯 암종 치환비용 스펙트럼 — 확증 축과 미결 축의 구분

이 절은 축별 대체가능 정도를 비용으로 환산해 지도로 만든다. 중심 그림은 치료 거리로 가중한 confusion matrix에 비용을 겹친 Fig2이며, 축별 비용과 헤드라인 대비의 신뢰구간은 Fig3으로 보인다.

**보이는 끝.** 주모델 UNI의 홀드아웃에서 두경부 HPV는 AUROC 0.959 [0.921–0.986], 양성 표본 26명으로 사전등록 기준 0.80을 크게 상회하였다(모델 교체와 site-label 구조 감사에서 남은 한계는 표 R1 각주 †에 명시한다). <!-- src: experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md L17 (0.9594, n_pos=26); pre-reg threshold 0.80 = SUBSTITUTABILITY_LAW_PREREGISTRATION.md --> 이 축은 변이가 아니라 바이러스 감염이 만든 형태(비각화·basaloid)이므로, 법칙의 "형태학적 상관물" 조항을 새로운 종류로 확장할 가능성을 보인 사례가 된다(확증 범위는 HPV 축에 한정한다). 양성대조들은 예상대로 거동하였다 — 폐 LUSC 조직형 0.939 [0.905–0.967](양성 153명), 두경부 grade 0.815 [0.742–0.882](양성 41명). <!-- src: LAW_HELDOUT_SCOREBOARD.md L18, L20 -->

**보이지 않는 끝.** 유방 HER2는 0.599로 사실상 무작위 수준이며, 이 코호트와 라우팅 정의에서 H&E 기반 대체를 지지하는 신호를 보이지 않아 음성 앵커 역할을 한다. <!-- src: LAW_HELDOUT_SCOREBOARD.md L31 (0.599, anchor near-random) --> 위 ERBB2 증폭은 0.644인데 shuffle-null이 0.641로 실질적으로 같아 신호를 추론해서는 안 된다(이 때문에 앞서의 "blind hit" 인용을 G2 리뷰에서 철회하였다). <!-- src: LAW_HELDOUT_SCOREBOARD.md L25 (real 0.6444 ≈ null 0.6406) --> 폐 KRAS-G12C는 0.681이지만, 이미지를 전혀 쓰지 않고 조직형만으로 예측한 기준선이 0.793으로 오히려 더 높다. 따라서 겉보기 예측력은 변이의 형태가 아니라 LUAD 편중에서 온다. <!-- src: LAW_HELDOUT_SCOREBOARD.md L22; experiments/crosscancer/LUNG_NSCLC/full/SUBTYPE_BASELINE_NOTE.md -->

모든 endpoint에는 shuffle-null(5-seed), 유병률 기준선(0.5), pixel-mean 기준선을 함께 보고하며, 폐 변이축에는 조직형만 쓰는 subtype-only 기준선까지 갖추었다. 인식론적 지위도 구분해야 한다. 폐·위·두경부는 예측을 결과 이전에 커밋으로 봉인한 sealed-forward 검정이지만, 대장은 결과가 예측보다 먼저 나온 회고적 분석이므로 검정력 있는 봉인 확증 집계에서 제외한다. <!-- src: LAW_HELDOUT_SCOREBOARD.md "인식론 구분"; COLORECTAL/full/LAW_TEST.md top banner -->

**표 R1 — 치환비용 관찰 스펙트럼 (UNI 정본). 여기서 '비용'은 금전이 아니라 치료 오배정 손실(오배정률)이다.**

| 암종 | 축 | 역할 | AUROC [95% CI] | 홀드아웃 n_pos / 대조 기준선 | 형태학적 상관물 | 판정 |
|---|---|---|---|---|---|---|
| 두경부 | HPV | 가시축(바이러스) | 0.959 [0.921–0.986] | 양성 26 | 있음(비각화·basaloid) | **단일 FM·site-disjoint 확증**(모델 무관성·site 교란 미검증) † |
| 폐 | LUSC 조직형 | 양성대조 | 0.939 [0.905–0.967] | 양성 153 | 형태 그 자체 | 통과 ‡ |
| 두경부 | grade | 양성대조 | 0.815 [0.742–0.882] | 양성 41 | 있음 | 통과 |
| 대장 | BRAF V600E | 회고적 | 0.882 [0.817–0.938] | 양성 15 | 있음(serrated/MSI 동반) | 부합·회고적·검정력부족·탐색(확증 집계 제외) |
| 위 | MSI-H | 가시축 | 0.860 (개발 0.899) | 양성 24 | 있음(면역) | 미결(1명 부족) |
| 폐 | EGFR 활성변이 | 등급적 | 0.852 | 양성 15 | 부분 | 미결 |
| 폐 | KRAS-G12C | 필수축 | 0.681 (subtype-only 0.793) | 양성 14 | 없음(조직형 편중) | 미결 |
| 위 | ERBB2 증폭 | 필수축(유방 복제) | 0.644 (shuffle 0.641) | 양성 14 | 없음 | 검정력부족·관찰 신호 없음 |
| 유방 | HER2 | 앵커(필수축) | 0.599 | near-random | 없음 | **대체 지지 신호 없음 · 음성 앵커** |
| 위 | Lauren diffuse | (원 양성대조) | 0.536 (개발 0.963) | pixel-mean 0.631 | 약하게 있음 | 기관분리 사례(R4) |

<!-- v2 change: 대장 BRAF를 v1의 어긋난 짝 "0.868 [0.780–0.938]"에서 COLORECTAL/full/LAW_TEST.md L14에 함께 보고된 점추정+CI 짝 = 0.8817 [0.817, 0.938](holdout161, 정본 라우팅 분할)로 정정. 5-seed R5 값 0.8676은 다른 분할(holdout151)이다 — LAW_TEST.md L18 수치 일관성 주석 참조. -->

† HPV 견고성은 3개 파운데이션 모델 중 2개(UNI·UNI2-h)에서만 5-seed 우연배제를 통과했고 Virchow2에서는 사전 기준을 통과하지 못하였다(real 0.9199 < 임계 0.9234, 마진 −0.0035 — 이는 셔플 null 산포가 넓은 것이며 신호 부재가 아니다; R5 참조). <!-- src: experiments/crosscancer/MULTIFM_COMPARISON.md §5; CROSSCHECK_5SEED_MULTIFM.md HPV/virchow2 row --> 또한 site 감사에서 site-label 구조화가 관찰되었다(Cramér's V = 0.378). HPV는 지도 한쪽 끝을 고정한 유일한 검정력 앵커일 뿐 법칙 일반화나 모델 무관 확증이 아니다. <!-- src: experiments/kkkim/20260805_site_audit/site_audit_results.json -->
‡ 폐 조직형(양성대조)은 site 감사에서 V(site, label) = 1.000이었다 — TCGA-LUAD/LUSC의 기관코드가 조직형과 100% 일치해 형태 신호와 site 서명이 분리 불가하다. 양성대조를 해석하는 모든 곳에 이 한계를 명시한다. <!-- src: site_audit_results.json -->

### R2. 우리 사전등록 분할에서는 변이축을 정할 수 없다 — 검정력 천장

이 한계는 우리의 동일한 site-disjoint 규약을 다섯 암종에 적용한 뒤에야 드러난다. 임상적으로 중요한 변이·증폭 축은 우리의 사전등록 홀드아웃에서 양성 스물다섯이라는 임계에 반복적으로 미치지 못하였다(표 R2).

즉 우리가 택한 기관 분리 단일 분할에서는 실행 가능한 변이 대부분에 검정력이 확보되지 않았다. 우리는 이를 "공개 데이터로는 원리적으로 불가능하다"로 일반화하지 않는다. grouped 또는 leave-one-site-out 교차검증으로 검정력을 회복할 가능성은 남아 있으며, 이는 Supplement에 탐색적으로 둔다.

임계는 사후에 조정하지 않았다. 위 MSI가 24명으로 한 명 부족했지만 기준을 25에서 24로 낮추지 않았고, 골대를 옮기지 않은 것 자체가 결과를 신뢰할 근거가 된다. 따라서 변이축의 치환가능성을 확정 판정하려면 기관 코호트나 전향적 수집이 필요하며, 그때까지 지도의 가운데 구간은 열어 둔다.

**표 R2 — 검정력 천장**

| 축 | 홀드아웃 양성 | 판정 |
|---|---|---|
| 폐 EGFR 활성변이 | 15 | 미결 |
| 폐 KRAS-G12C | 14 | 미결 |
| 위 ERBB2 증폭 | 14 | 검정력부족 · 관찰 신호 없음 |
| 위 MSI-H | 24 | 미결(임계 1명 부족) |
| 위 EBV | 7 | 탐색적 |
| 두경부 EGFR 증폭 | 17 | 미결 |

<!-- src: LAW_HELDOUT_SCOREBOARD.md 통합 표, n_pos column -->

### R3. 유방 앵커 — 예측 아형으로 정한 항HER2 라우팅은 이 코호트에서 대체를 지지하지 않는다

사전정의한 라우팅 정의와 이 코호트에서는 H&E-예측 아형에 따른 항HER2 배정이 치료 대상 식별을 지지하지 않았다(항HER2 오배정률 1.00). <!-- src: experiments/kkkim/20260710_cost_of_substitution/patient_routing_cost.json, therapeutic_distance.json --> 다만 오배정률과 그 비용 해석은 명시된 operating point에 의존하며, 그 임계를 사전정의하는 분석은 아직 완료되지 않았다. 이는 이 영역에서 H&E 대체가 안전하지 않을 수 있음을 오배정 손실로 보인 관찰이다.

정직하게 적어야 할 제약이 하나 있다. 축별 비용은 라우팅 스킴에 따라 내분비 요법과 화학요법이 서로 뒤집힌다(0.378과 0.035, 0.105와 0.510). 스킴이 바뀌어도 견고한 주장은 항HER2 오배정률 1.00과 헤드라인 대비의 신뢰구간이 0을 배제한다는 것뿐이므로, 이를 "다른 축은 안전하다"는 주장으로 확대하지 않는다.

HER2 음성은, 표현형 예측 수준에서, 염색 변이의 아티팩트가 아니다. 유방 앵커에 대한 염색 정규화 견고성 점검(Macenko 정규화, 임베딩 재추출 및 같은 fold에서 CLAM 재학습)에서 HER2 *표현형* 예측은 여전히 우연 수준에 머물렀고(AUROC 0.641로, 표 R1의 정규화 미적용 0.599보다 약간 높으나 여전히 가시축들에는 크게 못 미친다), ER은 높게 유지되었으며(0.917 대 0.901), PAM50도 보존되었다(0.740 대 0.759). <!-- src: experiments/kkkim/20260819_stain_norm_robustness/clam_rerun/sjpark/{her2_status,er_status,pam50}_clam*_uni_stainnorm/metrics.json (0.6408, 0.9166, 0.7396); non-normalised anchor values from Table R1 / LAW_HELDOUT_SCOREBOARD.md --> 따라서 앵커 endpoint의 순위(ER 높음 > PAM50 중간 > HER2 우연 수준)는 염색 정규화 유무와 무관하게 보존되며, 이는 "H&E가 HER2를 값싸게 대체할 수 없다"가 미보정 염색 차이에서 나온 것이 아님을 시사한다. 두 가지 범위 한계를 정직하게 적는다 — 라우팅/비용 파이프라인(오배정률 1.00)은 정규화 아래에서 **재실행하지 않았고**(표현형 예측만 재실행), 염색 정규화 실행에는 shuffle-null을 계산하지 않았으므로 여기서 "우연 수준"은 null이 아니라 그 값 및 ER/PAM50과의 비교에 근거한다. 이 견고성 점검은 유방 앵커에만 해당한다 — 헤드라인 다암종 결과(HPV, 폐)는 raw 슬라이드가 소실되어 재추출이 보류된 상태라 재점검하지 못하였다(Discussion 한계 참조).

<!-- v2 change: 염색 정규화 견고성 문단 추가(BIOP02-147). 수치는 정규화 삼중값을 자체 견고성 점검으로 보고. 정밀한 전/후 대조표는 만들지 않음 — 정규화 미적용 same-fold baseline의 출처가 모호(scoreboard 앵커 HER2=0.599 vs same-fold uni_v1 metrics.json HER2=0.5509)하기 때문. 그 모호성에 따라 비교는 정성적으로 서술. -->

### R4. 위 Lauren diffuse는 형태 부재가 아니라 기관 분리가 만든 사례다

이전 골격에서는 이 결과를 "형태학에 진짜로 보이지 않는 축의 증거"로 세웠으나, 우리 자체 진단은 그 해석을 지지하지 않는다.

Lauren diffuse는 원래 양성대조였다. 인환세포와 미만형은 강한 H&E 형태이므로 높게 나와야 했는데 0.536에 그쳤다. 그러나 원인은 H&E에 보이지 않아서가 아니다. 같은 파이프라인의 위 MSI는 개발셋 0.899에서 홀드아웃 0.860으로 정상 일반화하는 반면, Lauren만 개발셋 0.963에서 홀드아웃 0.536으로 0.43이나 떨어졌다. 게다가 저해상도 pixel-mean 기준선이 0.631로 MIL의 0.536보다 높으므로, 약한 형태 신호는 존재하는데 모델이 그것을 잡지 못한 것이다. 직접적 원인은 Lauren 유병률이 기관마다 크게 다르고, 기관 분리 분할이 고유병 기관을 평가셋에 몰아넣은 것(학습 46퍼센트, 평가 88퍼센트)이다. <!-- src: experiments/crosscancer/GASTRIC_STAD/full/LAUREN_POSCONTROL_DIAGNOSIS.md; LAW_HELDOUT_SCOREBOARD.md 결론 #3 -->

따라서 본문에서는 이 사례를 기관 분리 평가가 지름길 학습을 정당하게 차단한 방법론적 사례로 서술하고, 저신뢰 판정은 위암 Lauren에 국한한다. 같은 코호트의 MSI는 유효하게 남는다. "H&E가 Lauren을 보지 못한다"고 쓰지 않는다. "예측된다는 사실과 대체할 수 있다는 주장은 다르다"는 논지의 대표 사례는 Lauren이 아니라 유방 HER2와 폐 KRAS로 세운다.

### R5. 지도의 축 순서는 파운데이션 모델을 바꿔도 보존된다 (Supplement)

같은 슬라이드, 같은 기관 분리 홀드아웃, 같은 endpoint에서 임베딩 공간만 교체해(UNI 1024차원, Virchow2 2560차원, UNI2-h 1536차원) CLAM을 다시 학습하였다. 이 절의 논지는 절대값이 아니라 순서이며, 개별 축의 모델 무관성이 아니다.

무게중심은 폐의 순서 보존이다. 폐의 세 endpoint는 세 임베딩 공간 모두에서 조직형 > EGFR > KRAS 순서를 유지하였고, UNI 대비 Spearman 상관이 두 신형 모델 모두 1.000이었으며, 5-seed 우연배제도 폐에서 6개 중 6개가 통과하였다. <!-- src: experiments/crosscancer/CROSSCHECK_5SEED_MULTIFM.md (Spearman 1.000, 6/6 PASS) --> 다만 이것은 순서 안정성이지 모델 일반성이나 확증이 아니다.

단일 endpoint 결과는 모델에 따라 갈리며, 이를 그대로 보고한다(표 R5). 헤드라인인 두경부 HPV는 UNI와 UNI2-h에서 통과했으나, Virchow2에서는 점추정이 동등하게 높은데도(0.9199) 셔플 null의 산포가 커서 사전 기준을 통과하지 못하였다. 대장 BRAF도 세 모델 중 둘(UNI·Virchow2)에서만 통과했다(UNI2-h는 저검정력 셔플 null을 넘지 못함). <!-- src: MULTIFM_COMPARISON.md §1, §5 -->

두 종류의 음성을 구분해야 하는데, 둘 다 세 모델에서 재현되지만 이유가 다르기 때문이다. 위 Lauren은 세 모델 모두에서 우연배제에 실패한다(0.536 / 0.640 / 0.603) — 이는 R4의 **site-교란 실패가 모델 비의존적으로 재현된 것**이며, 즉 그 아티팩트가 UNI 특유가 아니라는 뜻이지 형태 신호의 부재가 아니다. 위 ERBB2 증폭은 세 모델 모두에서 실패하는데(0.644 / 0.668 / 0.585) 매 경우 real ≈ null이기 때문이며 — 이는 진짜 **신호의 부재**다. 이 둘을 한데 묶으면 R4가 바로잡은 오류를 다시 들여오게 된다. <!-- src: MULTIFM_COMPARISON.md §5 "lauren·erbb2는 전 FM FAIL(각각 site-교란·신호0)" -->

우연배제 통과가 곧 신호의 증거는 아니라는 점을 한 사례가 분명히 보여 준다. 두경부 EGFR 증폭은 UNI2-h에서 형식상 통과로 기록되지만, real AUROC가 0.505로 사실상 우연 수준이며 셔플 null의 산포가 좁아 기준선이 그만큼 낮게 잡혔다. 이는 실력이 아니라 낮은 기준선으로 얻은 통과이므로, 이 축을 통과나 양성으로 표기하지 않는다. <!-- src: 02_results.md R5 paragraph; braveji G2 finding (BIOP02-101) -->

이 절이 말할 수 있는 것은 결국 두 가지로 좁혀진다. 폐 지도의 축 순서가 세 모델에서 보존되었다는 것, 그리고 음성 결과가 모델과 무관하게 재현되었다는 것이다. 반대로 "파운데이션 모델과 무관하게 확증되었다"고는 쓰지 않는다 — 헤드라인 단일 endpoint 확증(두경부 HPV, 대장 BRAF)은 각각 세 모델 중 둘에서만 5-seed 우연배제를 통과했으므로, 이는 순위 안정성이지 모델 무관성이 아니다.

**표 R5 — 다중 파운데이션 모델 (5-seed 정본)**

| endpoint | UNI | Virchow2 | UNI2-h | 5-seed 우연배제 |
|---|---|---|---|---|
| 두경부 HPV | 0.9594 | 0.9199 | 0.9559 | UNI·UNI2-h 통과 / **Virchow2 미통과(마진 −0.0035)** |
| 대장 BRAF | 0.8676 | 0.8798 | 0.8978 | UNI·Virchow2 통과 / **UNI2-h 미통과** |
| 위 MSI-H | 0.8599 | 0.8795 | 0.8670 | 두 신형 모두 통과 |
| 위 Lauren(양성대조) | 0.5364 | 0.6404 | 0.6033 | 세 모델 모두 미통과(site-교란 재현) |
| 위 ERBB2 증폭 | 0.6444 | 0.6682 | 0.5845 | 세 모델 모두 미통과(신호 부재 재현) |
| 폐(조직형 > EGFR > KRAS) | 순서 보존 | 순서 보존 | 순서 보존 | Spearman 1.000 · 6/6 |

<!-- src: CROSSCHECK_5SEED_MULTIFM.md, MULTIFM_COMPARISON.md (5-seed 정본). 여기 대장 BRAF 행은 5-seed holdout151 값(0.8676 등)으로, 표 R1의 holdout161 라우팅 값 0.882와 다른 분할이다 — 같은 마커, CI 일관. -->

### R6. 외부 치료결과 앵커(Yale pCR) — 잠정 · Critic 대기

탐색적 점검으로, 항HER2 축 점수를 frozen-transfer로 산출해 Yale 코호트의 병리학적 완전관해(pCR)를 층화하고, AUROC와 부트스트랩 신뢰구간으로 평가한 뒤 측정 HER2 확률 기준선과 DeLong 검정으로 비교하였다. 사전 비교기준(성패 판정이 아니라 눈금 대조)은 Farahmand 등이 보고한 교차검증 AUC 0.80 [0.69–0.88]에 근접·중첩하는 것으로 정의하였다.

**이 결과는 `critic_status: pending`이며 본문으로 승격하지 않는다.** 여기에는 대기 포인터로만 남긴다 — 항HER2 축은 H&E-예측 표현형으로 pCR을 층화하지 못했고, 이는 후향적 지도의 HER2 음성과 방향적으로 일관되지만, Critic 서명 전까지 그 수치는 Abstract와 헤드라인 주장에서 제외한다. 전체 방법과 잠정 값은 M7에 있고, Discussion은 이를 아직 서명을 기다리는 실증 앵커("실증 이빨 대기")로 다룬다.

<!-- v2 change: R6 강등. v1은 R6·Abstract·M7·Discussion에서 AUROC 0.533 [0.411–0.653]을 완전한 결과로 서술했다. 과제 지시(A3/A4 critic_status pending → 잠정, 본문 승격 금지)에 따라 그 수치는 Abstract·헤드라인에서 빼고, M7(잠정값 포함 방법)과 여기 대기 포인터에만 남긴다. -->

### R7. 공간전사체가 시사하는 기전 (supporting, 잠정 · Critic 대기)

지도의 "왜"를 공개 공간전사체로 들여다본 탐색적 분석이다. 여기의 모든 내용은 `hypothesis_only`이고 Critic 미통과 상태이므로 헤드라인이 아니라 기전 보강으로 읽는다.

확진 HER2 양성 종양(8명)에서도 종양 spot의 일부는 같은 절편의 비종양 참조와 구별되지 않는 ERBB2 수준을 보인다. 종양 spot의 ERBB2가 참조 이하일 확률의 중앙값은 0.158이며, 8명 모두 신뢰구간이 0을 배제하고 확산·깊이 아티팩트를 배제하는 kill-test를 통과한다(내부 한정 7/8, 깊이 조건화 3/3). <!-- src: 02_results.md R7; experiments/kkkim/angle_A_spatial_erbb2/ --> 환자 한 명에 라벨은 하나뿐이라 이 저발현 부위를 표현할 수 없으므로, 이는 아형 라우팅 오차의 가능한 기전 — "HER2 대체 불가"가 예측의 노이즈가 아니라 라벨이 버리는 정보에서 올 수 있다는 후보 설명 — 을 보강한다(원리적 하한으로 단정하지 않는다). 한계: mRNA는 단백질·증폭과 다르고, spot은 세포가 아니며, ST 코호트는 우리 TCGA 코호트가 아니다(기전 예시이지 동일 코호트 검증이 아니다).

반면 대장에서 예측한 공간 상관물은 Visium 해상도에서 드러나지 않았다. 55µm spot이 핵 해상도보다 거칠어 림프구 특이 텍스처에 접근하지 못하기 때문이며, 이는 생물학적 반증이 아니라 기질·해상도 한계다. 따라서 대장 공간 기전은 열린 문제로 남기며, co-registered H&E를 갖춘 기질이 적정 검정이다.

---

## 3. Discussion

우리의 지도는 "예측 가능성"이 아니라 "대체 안전성"을 기준으로 삼는다. 축마다 경계가 다르고 그 경계가 임상 비용으로 정량화된다는 것이 이 프레임의 핵심이다.

형태에 보이지 않는 축을 가려내는 것 자체가 지도가 주는 정보다. 유방 HER2와 폐 KRAS처럼 H&E 대체가 위험한 축을 표시하는 데 이 프레임의 가치가 있으며, 위 Lauren은 형태 부재가 아니라 기관 분리가 만든 사례이므로 이 목록에서 제외한다.

유방 HER2에서는 예측 아형 라우팅이 이 코호트·라우팅 정의에서 일관되게 실패했고, 이는 분자검사가 여전히 필수인 영역을 비용으로 시사한다. 축별 비용의 스킴 의존성은 정직하게 서술하고, 견고한 주장은 항HER2 오배정률 1.00과 대비의 신뢰구간으로 한정한다. 이 음성은 염색 아티팩트가 아니다 — 유방 앵커에 대한 염색 정규화 아래에서 HER2는 우연 수준에 머문 반면 ER·PAM50은 보존되었다. 후향적 지도에 실증 이빨을 붙이기 위해 외부 치료결과 앵커(Yale pCR)를 다는 중이며, 그 잠정 결과는 HER2 음성과 방향적으로 일관되지만 `critic_status: pending`이라 Critic 서명 전까지 승격하지 않는다.

한계는 정면에 둔다. 모든 산출은 후향적·코호트 수준이며 `hypothesis_only`로, 개인 수준 benefit 주장이 아니다.

**Site/batch 교란과 염색 변이 한계 — "정말 형태인가?"라는 두 공격을 함께.** site-disjoint 분할은 동일 기관 슬라이드가 학습과 평가에 함께 들어가는 leakage를 방지했지만, 라벨과 기관의 결합(confounding)은 남아 있어 성능을 순수 형태 신호로 해석하는 데 한계가 있다. site/batch 교란 감사는 site-disjoint 분할이 라벨을 조직원천기관과 교란함을 다섯 개 endpoint에서 확인하였다 — 폐 조직형(양성대조) V = 1.000으로 형태와 site 서명이 분리 불가하고, 두경부 HPV V = 0.378, 위 Lauren은 유병률이 0.46에서 0.88로 이동하며, 폐 EGFR·KRAS도 site-label 연관이 유의하다. 이는 교란의 필요조건이지 "모델이 site를 읽는다"의 증명이 아니다. 별개로, H&E 염색 정규화는 주 파이프라인에 적용하지 않았다. 염색 정규화 견고성 점검은 유방 앵커 패턴(HER2 우연 수준, ER 높음, PAM50 보존)을 보존했지만, **이 점검은 유방 앵커에만 해당한다** — 다암종 헤드라인 축(두경부 HPV, 폐 조직형)은 raw 슬라이드가 소실되어 재추출이 보류돼 재점검하지 못하였다. 즉 리뷰어가 스캐너/염색 아티팩트로 가장 공격하기 쉬운 두 헤드라인 결과가 바로 site-교란 플래그를 달고 있으면서 아직 염색 검증이 안 된 축들이며, 이를 그대로 명시한다. H&E로부터의 site 예측성과 leave-one-site-out 성능이 교란 문제의 최종 판정을 하며, 그때까지 두 앵커를 해석하는 곳마다 이 한계를 명시한다. <!-- src: site_audit_results.json; experiments/kkkim/20260819_stain_norm_robustness/ (BRCA anchor only); GPU return / raw loss noted in RESUME.md -->

모델 비의존성에 대해서는, 폐 endpoint 간 상대적 AUROC 순서(조직형 > EGFR > KRAS)와 주요 음성 결과가 평가한 세 파운데이션 모델 전반에서 보존되었으나, 개별 분자 축의 우연배제 통과 여부는 모델에 따라 달랐다. 이는 순서 안정성이지 법칙 전체의 모델 비의존성이 아니다 — 헤드라인 단일 endpoint 확증(HPV, 대장 BRAF)은 각각 세 모델 중 둘에서만 우연배제를 통과했다. 20-seed 재점검은 Virchow2 HPV 임계가 안정화(≈0.837)되어 그 칸이 통과로 뒤집힐 것임을 시사했으나, **이 판정 변경은 채택하지 않는다** — braveji의 Critic 확인 대기 중이며(BIOP02-123) 보고 상태는 "3개 중 2개 모델"로 유지한다. <!-- src: 04_discussion.md item 6; experiments/kkkim/20260820_shuffle_null_20seed/ -->

**앵커 표현형 예측 신뢰성(유방).** 네 가지 한계를 정면에 둔다. (i) 형태의 부가가치는 endpoint별로 다르며 사소한 기준선 위에 가산되지 않는다 — ER/PR 예측은 slide-mean-embedding 기준선을 외부에서 이기지만(+0.128/+0.223) subtype-only 기준선에는 외부에서 역전당하고, HER2는 mean-embedding 기준선조차 이기지 못한다. 네 endpoint 중 PAM50 4-class만이 유효 기준선(mean-embedding)을 내부·외부 모두에서 CI 비중첩으로 넘는다(+0.089/+0.165). (ii) attention 반사실 충실도는 슬라이드 순위(AUROC) 수준이 아니라 확률 수준에서만 주장한다(무작위 제거 대비 10–23×) — MIL 신호가 중복적이기 때문이다. (iii) HER2는 정직한 음성으로(기준선·교차데이터 점검 모두에서 기각), 파이프라인 실패가 아니라 지도의 앵커다. (iv) 치료 가설은 세포주-환자 전이 한계를 물려받으며 `hypothesis_only`다. <!-- src: 04_discussion.md Limitations 1–4; experiments/braveji/BIOP02-75_critic_gate/GATE_STATUS.md -->

**PAM50 라벨 출처 주기.** PAM50은 이 논문에서 비중이 있다(유효 기준선을 내부·외부 모두에서 넘는 유일한 앵커 endpoint다). manifest PAM50 라벨(로컬/genefu 계산, Parker 2009)은 cBioPortal PanCancer Atlas SUBTYPE 라벨과 **57.0% 일치**(일치 514/902)하며, 곧 **43.0% 불일치**(불일치 388/902)로, 가장 큰 불일치는 LumB↔LumA와 Normal→LumA다. <!-- src: agents/data/manifests/pam50_source_reconcile_biop02-74.json (concordance_pct=57.0, n_match=514/n_overlap=902) --> manifest 코호트에 대한 cBioPortal 실측 커버리지가 높으므로(97.2%), 로컬/genefu 라벨을 쓰기 위한 사전등록 fallback 조건(`split_policy_v0.md §10`: cBioPortal 커버리지가 부족할 때만 fallback 허용)은 **충족되지 않았다**. 따라서 앵커 endpoint의 정본 PAM50 라벨 출처를 무엇으로 할지는 Methods의 미결 정합 항목이며, 여기서는 해결이 아니라 표시만 한다. <!-- src: pam50_source_reconcile_biop02-74.json policy_check field -->

임상·연구 함의는 다음과 같다. 이 관찰 지도는 H&E 대체가 뚜렷하게 위험한 음성 축(유방 HER2)과 현재 자료로 판정할 수 없는 미결 축을 식별함으로써, 향후 전향 검증 연구의 우선순위를 정하는 의사결정 틀이 된다. 어디서 H&E 선별이 실제로 비용을 절감하는지는 전향 검증 이전에 권고할 수 없으며, 이 논문은 임상 권고나 전면 대체를 주장하지 않는다. 가치는 비싸거나 느리거나 희소한 분자검사와 자원제한 세팅에 집중된다. 요컨대 우리의 기여는 "골드스탠다드를 이긴다"가 아니라 "값싼 H&E가 언제 분자검사를 pre-screen하거나 triage할 수 있고 언제 불가한지를 지도로 예측 가능하게 만든다"는 데 있다.

---

## 4. Methods

### M1. 코호트와 라벨
유방암(TCGA-BRCA, 약 1,010 진단 슬라이드)을 앵커로 삼고 폐·대장·위·두경부를 더한 다섯 암종을 다룬다. 각 코호트의 슬라이드 수는 결과 JSON에 실측되어 있다(대장 523, 폐 1,026, 위 439, 두경부 468). <!-- src: 03_methods.md M1 --> 라벨 출처와 환자 단위 split은 `agents/data/`에서 관리하며, 사전등록된 축 경계는 봉인 문서(`experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md`)에 기록되어 있다. 유방 PAM50 endpoint의 경우 manifest 라벨(로컬/genefu, Parker 2009)과 cBioPortal PanCancer Atlas SUBTYPE 라벨은 중첩 환자의 57.0%에서 일치하고(514/902; 43.0% 불일치), cBioPortal 커버리지가 높으므로(97.2%) 로컬 라벨을 쓰기 위한 사전등록 fallback 조건(`split_policy_v0.md §10`)이 충족되지 않았으며, PAM50 라벨 출처의 정본 확정은 미결 정합 항목이다. <!-- src: pam50_source_reconcile_biop02-74.json -->

### M2. 타일링·임베딩
각 whole-slide image는 20× 배율에서 256×256 픽셀 타일로 분할하고, 조직 영역은 Otsu 임계로 배경과 분리하며, 환자당 최대 5,000 타일로 상한을 두었다. 헤드라인 임베딩은 UNI v1(1024차원)이며, 모델 비의존성 검정을 위해 동일 좌표에 Virchow2(2560차원, CLS 토큰과 mean patch 토큰 결합, register 토큰 제외)와 UNI2-h(1536차원)로도 재추출하였다. 슬라이드 단위 EXAONE Path 2.0 인터페이스는 좌표 기반 파이프라인과 비호환이라 견고성 세트에서 제외하였다. 타일은 224×224로 리사이즈하고 ImageNet 통계로 채널 정규화하였다. H&E 염색 정규화는 주 파이프라인에 적용하지 않았으며, 그로 인한 미보정 염색 변이는 한계로 명시하고 염색 정규화 견고성 점검(M10)으로 별도 검증한다. <!-- src: 03_methods.md M2 -->

### M3. 모델·학습
CLAM-SB attention MIL을 사용하였다(hidden 512·attention 256, 40–50 epoch, 시드 42 고정). 예측은 슬라이드 단위로 산출한 뒤 환자 단위로 집계하였다. <!-- src: 03_methods.md M3; experiments/crosscancer/run_mil_cost.py -->

### M4. 평가 설계
모든 평가는 site-disjoint holdout에서 수행하였다. 같은 제출 기관(TSS)의 슬라이드가 학습과 평가에 동시에 들어가지 않도록 분할해 기관 지문에 의한 leakage를 차단하였고, 검정력을 위해 validation과 test를 합쳤다. 대조군은 shuffle-null, 유병률 기준선(0.5), subtype-only 또는 pixel-mean 기준선 세 가지다. 신뢰구간은 1,000회 부트스트랩 95% CI로 보고하며, 환자 군집이 중요한 경우(수용체 라우팅)에는 CI를 환자 단위로 재계산하였다. <!-- src: 03_methods.md M4 -->

### M5. cost-of-substitution 프레임
치환비용은 confusion matrix에 치료 거리를 곱해, 측정 마커로 정한 치료와 H&E-예측 마커로 정한 치료가 갈리는 곳에서 발생하는 오분류 비용으로 정의한다. 선도지표는 거리무관 misroute_rate다. 이 프레임은 약물 반응을 예측하지 않으며 약물 구조를 입력으로 받지 않는다. <!-- src: 03_methods.md M5; experiments/kkkim/20260710_cost_of_substitution/ -->

### M6. 사전등록·claim 규율
판정 임계는 슬라이드나 관찰값이 아니라 봉인된 사전등록 문서에서만 인용한다. 검정력 규칙(양성 25 미만 → 탐색적 → INCONCLUSIVE)은 결과를 본 뒤 옮기지 않으며 확증과 반증에 대칭으로 적용한다. 모든 산출은 `hypothesis_only`이고 후향적이다. <!-- src: 03_methods.md M6 -->

### M7. Yale 앵커 (잠정, Critic 대기)
항HER2 축 점수를 frozen-transfer(앵커 모델을 추가 학습 없이 적용)로 산출하고 Yale 코호트의 pCR을 층화해 AUROC와 부트스트랩 95% 신뢰구간을 구한 뒤 측정 HER2 확률 기준선과 DeLong 검정으로 비교하였다. 사전 비교기준은 Farahmand 등의 0.80 [0.69–0.88] 근접·중첩으로 정의하였다. 잠정 결과는 AUROC 0.533 [0.411–0.653]으로 — 항HER2 축이 H&E-예측 표현형으로는 pCR을 층화하지 못했으며 이는 지도의 HER2 음성과 방향적으로 일관되지만 — 이 값은 `critic_status: pending`이라 Abstract나 헤드라인 주장으로 옮기지 않는다. <!-- src: 02_results.md R6 (0.533 [0.411–0.653]); status pending per task instruction -->

### M8. 다중 모델 견고성
각 파운데이션 모델 임베딩 공간에서 CLAM을 처음부터 재학습하였다(좌표계가 다르므로 예측 모델을 각각 다시 적합해야 같은 층위의 비교가 된다). 판정 기준은 5-seed shuffle-null 우연배제(real AUROC > null 평균 + 2×표준편차, ddof = 1)이며 시드는 42·1·2·3·4를 사용하였다. 결정론은 동일 시드 재실행 2회로 확인하였다(대장 BRAF Virchow2 시드 42 = 0.8798 재현). 정본 결과는 `CROSSCHECK_5SEED_MULTIFM.md`와 `MULTIFM_COMPARISON.md`에 있다. sjpark이 커밋된 소스로부터 독립 재계산하였고(BIOP02-101, 교차검증 PASS), braveji의 최종 다중 FM Critic 서명은 진행 중이다. <!-- src: 03_methods.md M8; MULTIFM_COMPARISON.md header -->

### M9. site/batch 교란 감사
각 endpoint에서 site-disjoint 분할이 라벨을 조직원천기관(TSS)과 교란하는지 정량화하였다. site와 label의 Cramér's V와 순열 p, train/test 유병률 시프트, test 양성의 site 집중도 순열검정을 산출하였다. 이는 교란의 필요조건을 보는 분석이며, 모델이 실제로 site를 사용하는지에 대한 최종 판정은 H&E로부터의 site 예측성과 leave-one-site-out 성능으로 한다. <!-- src: 03_methods.md M9; site_audit_results.json -->

### M10. 염색 정규화 견고성 (유방 앵커)
앵커 결과가 미보정 H&E 염색 변이의 아티팩트인지 검정하기 위해, 유방 앵커 슬라이드에서 Macenko 염색 정규화(torchstain 1.3.0, 고정된 조밀조직 참조 타일)로 임베딩을 재추출하고 같은 fold(`split_policy_v0`, fold hash 5995f29d3978b831)에서 ER·HER2·PAM50에 대해 CLAM을 재학습하였다. HER2 표현형 예측은 우연 수준에 머물렀고(AUROC 0.641), ER은 높게 유지(0.917), PAM50은 보존(0.740)되었으며, 앵커 순위 ER > PAM50 > HER2는 정규화 미적용 앵커 순서(표 R1: ER 0.901, PAM50 0.759, HER2 0.599)와 일치한다. 표현형 예측만 재실행했고 라우팅/비용 파이프라인은 재실행하지 않았으며, 염색 정규화 실행에는 shuffle-null을 계산하지 않았다. 이 견고성 점검은 유방 앵커에만 해당하며, 다암종 raw 슬라이드는 소실되어 염색 정규화 재추출은 보류한다. <!-- src: experiments/kkkim/20260819_stain_norm_robustness/RESUME.md; clam_rerun/sjpark/*/metrics.json (0.6408/0.9166/0.7396) -->

---

## 그림·표

- **Fig1** 파이프라인 개념도(H&E → 임베딩 → 표현형 → 라우팅 오배정률)
  `[Figure 1: pipeline — WSI tiling → UNI embedding → CLAM MIL phenotype → marker-to-treatment routing → misassignment rate]`
- **Fig2** confusion × distance에 오배정 손실을 겹친 관찰 지도(중심 그림)
  `[Figure 2: central map — per-axis substitution cost across five cancers, legible end (HPV/histology) to illegible end (HER2/ERBB2)]`
- **Fig3** 축별 오배정 손실과 헤드라인 대비의 신뢰구간
  `[Figure 3: per-axis cost with 95% CI; headline contrast CI excluding 0]`
- **Fig4**(예정) 검정력 천장 — 축별 홀드아웃 양성 표본과 판정 가능 경계
  `[Figure 4: holdout n_pos per axis vs the 25-positive pre-registered threshold; verdict-coloured, positive controls hatched]`
- **Fig5**(예정) HER2 오배정 상세 — 라우팅 스킴별 치료 카테고리 오배정률
  `[Figure 5: anti-HER2 misassignment rate = 1.00; scheme-dependence of endocrine/chemo cost]`
- **SFig1**(예정) 다중 모델 비교 — UNI/Virchow2/UNI2-h 순서 보존과 갈리는 칸
  `[SFigure 1: lung order preserved (Spearman 1.000); diverging single cells (HPV/Virchow2, BRAF/UNI2-h)]`
- **표 R1** 치환비용 관찰 스펙트럼 · **표 R2** 검정력 천장 · **표 R5** 다중 파운데이션 모델(Supplement)
- **Table 1**(예정) 코호트 특성 — 5암종 n·라벨 유병률·split `<FILL: jamie — S5 in SUBMISSION_PREP.md>`

## 미결 항목과 게이트 (kkkim 검토용)

- **저자 대면 메타데이터 미확정** — 저자/순서, 소속, corresponding author + 이메일, funding/acknowledgments(**프로젝트 README에 따라 GPU 제공처 Modulabs를 반드시 명시**), COI, ORCID. `<FILL: 팀 확정>`. 이것이 임계 경로다(BIOP02-114).
- **Yale(R6/M7)은 `critic_status: pending`** — 잠정, Abstract/헤드라인에서 제외; 본문 승격은 Critic 서명 후에만.
- **20-seed HPV/Virchow2 플립 미채택** — braveji 대기(BIOP02-123)로 상태는 "3개 중 2개 모델" 유지.
- **PAM50 라벨 출처** — cBioPortal과 57.0% 일치; fallback 조건 미충족(커버리지 97.2%). 정본 라벨 출처는 Methods 미결 정합 항목(BIOP02-74).
- **염색 정규화는 유방 앵커에만** — 다암종 헤드라인(HPV, 폐)은 염색 미검증(raw 소실).
- **braveji 7-point Critic 최종 서명(BIOP02-75)** — Paper C 전체에 대해 대기 중.
- **인용**은 `agents/critic/scripts/verify_citations.py`로 기계 검증하기 전까지 잠정(대괄호)이다.
- **Venue** — npj Precision Oncology vs ML4H 2026: 형식/분량 제약 `<FILL: ML4H 2026 CFP 원문 — 사람 확정>`; 워크숍 venue에는 압축 필요 가능(Leader 결정).
- **보고 표준 매핑**(TRIPOD+AI 완료; CLAIM/PROBAST/STROBE 대기) 및 **Table 1(코호트 특성)**을 Supplement로 첨부.
