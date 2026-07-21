# 논문 회의 통합 브리프 — 2026-07-21 (BIOP01 + BIOP02)

> 오늘 회의는 **두 편의 논문**을 함께 다룬다. 세부 배경은 각 프로젝트 브리프에 있고, 이 문서는 **한자리에서 결정할 것과 각자 준비할 것**을 합쳐 정리한 것이다.
> - BIOP01 상세 = `BioProject01/pipeline/hspc-velocity-benchmark/manuscript/MEETING_BRIEF_2026-07-21.md`
> - BIOP02 상세 = `BioProject02/MEETING_BRIEF_BIOP02_2026-07-21.md`
> 수치는 전부 결과 파일에서 읽은 실측이며 지어낸 값이 없다.

---

## 0. 한눈에 — 두 논문의 현재 위치

| | **BIOP01** (RNA velocity 신뢰성 감사) | **BIOP02** (SpatialPathoAgent 치환가능성 결정지도) |
|---|---|---|
| 한 줄 정체성 | 무엇을 **믿고 믿지 말아야 하는지**의 신뢰 지도 | H&E가 분자검사를 **언제 값싸게 대신할 수 있는지**의 결정지도 |
| 진행 단계 | **투고 준비 마무리** — 자동으로 할 수 있는 정비 완료 | **집필 착수** — Critic 게이트 방금 통과 |
| Critic/검증 | 사전등록 6/6 통과, 적대적 자체리뷰 반영 | **G2 Critic `PASS`**(2026-07-20, braveji 6차) |
| 투고처 | **미정** — Genome Biology 도전 vs Cell Reports Methods | **확정** — npj Precision Oncology |
| 최대 병목 | **저자·소속·corresponding 미확정** | **동일 — 저자·소속·corresponding 미확정** |

**두 논문이 같은 벽에 막혀 있다.** 남은 `<FILL>`이 대부분 사람이 정해야 하는 항목(저자·소속·corresponding)이라, **오늘 이것부터 정하면 두 편이 동시에 풀린다.**

---

## 1. BIOP01 — RNA velocity 신뢰성 감사

**정체성**: 새 방법을 제안하는 논문이 아니라 **신뢰성 감사** 논문. 원래는 chromatin→transcription **lag**으로 약물반응 timing을 예측하려 했는데, 그 전제를 검정하니 lag이 방법을 바꾸면 재현되지 않았다. **그 발견 자체가 논문이 되었다.**

**핵심 결과 세 가지**
1. **출력마다 신뢰도가 다르다** — 전사율 **α는 재현된다**(cross-method Spearman ρ = 0.88). **lag은 재현되지 않는다**(최강 쌍 +0.163, 대부분 |ρ| ≤ 0.08, 방향 일치 54.6% = 동전 던지기). 분해율 **γ도 비재현**(ρ ≈ −0.1).
2. **lag이 흔들리는 이유가 설명된다** — ATAC를 섞어 chromatin을 파괴해도 lag 분포가 그대로. lag은 chromatin이 아니라 **모델 구조가 만든 값**. profile-likelihood로 α=stiff, lag=sloppy.
3. **여섯 시스템에서 순서가 보존된다** — 여섯 번째(gastrulation)는 **결과를 보기 전 봉인한 6개 예측을 사후 구제 없이 6/6 통과**.

**최근 이틀 — 층② 인과 sub-claim이 하루에 세 번 뒤집혔다**
서로 다른 세포집합을 견주던 비교를 같은 세포집합으로 다시 재서 "chromatin은 무력하다"를 **철회**했고, 재적합이 bit 단위로 동일해(Δ_rr=0.000000) 적합 인공물도 아님을 확인했다. 현재 진술은 "chromatin 파괴가 출력을 실제로 움직이나 크기는 천장의 7% 수준". **주 결론(방법 간 불일치·α만 재현·lag 비재현)은 세 번 모두 영향받지 않았다.** 이건 약점이 아니라 **규율이 작동한 사례**로 설명한다.

**상태**: 적대적 자체리뷰 전량 반영, Supplementary 5패널 실물화, 참고문헌 26→**69편**(인용 결함 12건 해소), Additional file 11개 xlsx 변환, 영/한 원고 동기화. **PR #4** 병합 가능 상태. 남은 `<FILL>` = 저자·소속·corresponding·repository DOI·라이선스.

---

## 2. BIOP02 — 치환가능성 결정지도 (SpatialPathoAgent)

**정체성**: "분자 표현형이 형태학적으로 예측된다"와 "그래서 분자검사를 임상적으로 대체해도 된다"는 **다르다**. 어떤 축은 H&E에 보이고 어떤 축은 안 보이며, 그 경계를 비용으로 환산해 **다섯 암종 사전등록 결정지도**로 그린다. 유방은 前 Paper A였다가 **anchor 챕터로 흡수**됐다(플래그십 1편으로 수렴).

**어제 생긴 최대 변화 — Critic G2 `PASS`** (braveji 6차 재판정)
7-point 중 data_leakage·counterfactual·cross_dataset·biological_plausibility·drp_framing·claim_level = pass, baseline_comparison만 caution. **"critic pending이라 헤드라인 승격 금지"였던 제약이 풀렸다.**

**본문에 쓸 수 있는 실측**

| 암종 | 축 | holdout AUC [95% CI] | 의미 |
|---|---|---|---|
| 두경부 | HPV | **0.959 [0.921–0.986]** | 강하게 보임 — 유일한 검정력 있는 CONFIRM |
| 폐 | LUSC 조직형 | **0.939 [0.905–0.967]** | 강하게 보임(양성대조) |
| 대장 | BRAF V600E | **0.868 [0.780–0.938]** | 보임(회고적 지위) |
| 위 | Lauren diffuse | **0.536 [0.379–0.694]** | **안 보임 = 대체 불가**(정직한 음성) |
| 유방(anchor) | 수용체 3축 + PAM50 | Fig2/Fig3 백킹 JSON | HER2축 상시 실패 = 대체 불가 |

**견고성**: 5-seed 우연배제(HPV real 0.959 > 임계 0.790, Critic 독립 재계산 10/10 일치) · counterfactual(HPV 상위 20% 타일 제거 시 −0.107, 무작위 ~0 = 특정 형태에 충실) · pixel-mean(HPV 0.922) · 위 Lauren 실패는 **Lauren 국한 site-교란**으로 원인 규명.

**정직하게 실을 한계 2건**: ① MIL 부가가치 제한(여러 endpoint에서 CLAM이 mean-pool baseline을 유의하게 못 넘음) ② 두경부 HPV 커버리지 편향(결손군 HPV+ 0.40 vs 포함군 0.10 — 원인은 **TSS site CR에 진단 슬라이드 자체가 없음**, 형태 난이도 편향 아님).

**막힌 것**: Yale 실제-결과 앵커 A3(sjpark)·A4(jhans) **미착수** / 다중 FM 모델-비의존성(폐 임베딩 진행 중, Supplement 자리) / Fig1·2·3 Critic 서명 / CPTAC lock(jamie).

---

## 3. 공통으로 결정할 것 (두 논문 동시 해제)

1. **저자·기여·저자순서 + 소속 + corresponding(이름·이메일)** — **두 논문 모두의 최대 병목.** 이게 없으면 투고도 preprint도 못 올린다.
   - BIOP01 추가 쟁점 — **하차자 세 분 정리**: 박상준 님은 **기여 있음**(주제 선정·참고문헌 분석 = conception) → 저자 포함 여부와 **연락해 의사 확인하는 절차**를 정해야 한다. 전연수·박성진 님은 기여 없음 → 저자 아님, 배정 티켓 종료.
   - BIOP01 분석 하네스가 박상준 님 `Harness_Baseline`에서 반입돼 원저작자로 명시돼 있고 원 repo에 LICENSE가 없다 → 저자 결정과 별개로 **출처 표기 유지 방식** 확인 필요.
   - BIOP02는 여기에 **GPU 자원 제공처(Modulabs) Acknowledgments 표기**가 추가된다.
2. **투고처** — BIOP01: Genome Biology 도전 vs Cell Reports Methods base case(자체 적대심사에서 GB reject 위험 75~85%로 봤다). BIOP02: npj Precision Oncology 확정 + preprint(medRxiv) 시점.
3. **논문 생산 하네스 검토(BIOP02-100, 이건규 님)** — **두 프로젝트 공통 자산.** BIOP01이 그 하네스로 굴러간 첫 사례이므로, 게이트가 실제로 과대주장을 막았는지 양쪽에서 확인한다.
4. **JIRA 트랙 정리** — BIOP01 스터디 과제(BIOP01-1~20)를 계속 갈지 통째로 정리할지. 하차자 배정 6건(박성진 6·13·20 / 전연수 2·9·16)은 종료. BIOP02는 스프린트 에픽 S0·S1을 어제 종결했고 S2~S8은 하위 잔여로 유지 중.

---

## 4. 사람별 준비사항 (두 프로젝트 통합 — 각자 여기만 보면 됨)

### 지용기 님 (braveji) — Orchestrator·Critic 총괄
- **[BIOP01]** **PR #4 병합 여부** 판단. 병합하면 main에서 `skills/`·`analysis/`가 사라진다. 하네스 정본은 외부 repo(`kakyungkim/paper-analysis-harness`)이고 main 사본은 5/25에서 멈춘 구버전이라 내용 손실은 없으나, **main 쪽을 쓰는 분이 있는지** 확인 필요.
- **[BIOP01]** BIOP01-52 **리뷰어 배정**(현재 미배정). BIOP01-22(하네스 통합·재현성)·BIOP01-45(OpenClaw 배선) 현재 상태 공유.
- **[BIOP02]** **Fig1/2/3 Critic 서명 순서와 소요 시간** — 무엇부터 서명 가능한지. 원고 어느 시점에 최종 서명(BIOP02-75)이 필요한지.
- **[BIOP02]** BIOP02-66(Figure 버전관리·Confluence)·-71(registry) 현황 — 그림 버전이 원고와 어긋나지 않도록. 제출 패키지(-76·-79)에 필요한 팀 입력 목록.

### 박세진 님 (sjpark) — Modeling
- **[BIOP01]** 크로스리뷰가 **네 건(25·39·42·44)** 몰려 있다. 전부는 부담이니 회의에서 우선순위를 함께 정한다. 그중 **BIOP01-44(신규 추가분석 critic)를 먼저** 봐주시면 도움이 크다 — 최근 이틀 사이 층② 인과 주장이 세 번 바뀌었고 그 판단의 타당성에 외부 시선이 필요하다(근거 `results/velocity_matrix_paired_shuffle.md`, `results/velocity_matrix_runtorun_null.md`). 원고 전체 리뷰(BIOP01-52) 수용 가능 여부도.
- **[BIOP02]** **Yale A3(항HER2 축 점수 산출) 착수 가능 시점** — 오늘 기한을 정해야 이 섹션의 **본문 포함 여부**가 결정된다.
- **[BIOP02]** BIOP02-53(MIL)·-90(ER predictions_ext) 검토중 마무리 계획 / BIOP02-72 Methods 모델링 절 초안 가능 여부.
- **[BIOP02]** braveji 요청분 — **mean_embed per-patient proba 커밋**(paired 검정의 형식 근거). 있으면 baseline caution 문서화가 닫힌다.

### 서정한 님 (jhans) — Therapeutic Evidence
- **[BIOP01]** BIOP01-24(10x E18 mouse brain)는 현재 논문에서 재현 축 하나를 이미 담당 중이다. **추가로 보실 계획이 있는지, 현 상태로 마무리할지** 알려주시면 티켓을 정리한다.
- **[BIOP02]** **Yale A4(pCR 층화 + DeLong 검정) 착수 가능 시점** — A3와 함께 본문 포함 여부를 가른다.
- **[BIOP02]** BIOP02-80 Paper B 기획을 이번 원고에 넣을지, 별도 트랙으로 둘지 의견. 치료거리·DepMap/GDSC 근거 중 **Discussion에 인용할 것**이 있는지.

### jamie 님 (류재면) — Data
- **[BIOP02]** **BIOP02-70 CPTAC 외부검증 lock**의 잔여 작업과 **예상 완료일** — Methods·외부검증 서술의 long pole이다.
- **[BIOP02]** BIOP02-49 HER2/PAM50 라벨 QC(검토 중) 종결 여부 / BIOP02-74 Methods 데이터 출처·split 정책 절 착수 시점.
- **[BIOP01]** 스터디 과제 티켓만 남아 있다(BIOP01-5·12·19). 이 트랙을 계속 갈지 정리할지 회의에서 정한다.

### 이건규 님 (gglee) — 재편입·하네스 검토
- **[공통]** **BIOP02-100 논문 생산 하네스 검토** — 범위가 두 프로젝트에 걸쳐 있다.
  - BIOP01 시작점: `docs/HARNESS.md` · `CLAUDE.md`의 라우팅·계약 섹션 · `results/FINDINGS.md`
  - BIOP02 시작점: `docs/HARNESS.md` · `CLAUDE.md`의 라우팅·계약 섹션 · `experiments/crosscancer/LAW_HELDOUT_SCOREBOARD.md`
  - 봐주실 초점: **게이트가 실제로 과대주장을 막았는가.** BIOP01은 층② 인과 주장이 이틀 새 세 번 바뀌었는데 전부 사전 봉인 기준에 걸려 바뀌었고, BIOP02는 Critic이 reject→caution→pass로 6차까지 가며 블로커를 잡았다. **두 사례가 하네스의 실전 검증 자료다.**
- **[정정]** BIOP01 브리프에 "Atlassian 계정 복구 전"이라 적혀 있으나, **확인 결과 계정은 active이고**(accountId `712020:bff61238-…`) **GitHub biospin 두 레포 모두 admin 권한**이 있습니다. 접근이 실제로 막히는 게 있으면 회의 때 알려주세요.

### 김가경 (kkkim) — Leader·양 논문 총괄
- **[BIOP02]** Results 골격 초안(5암종 결정지도 → 유방 anchor → 위 정직한 음성) + 실측 숫자표 최신본. G2 PASS 반영해 `manuscript/README.md`의 "critic pending" 서술 갱신.
- **[BIOP02]** 다중 FM(Virchow2·UNI2-h) 임베딩 진척·ETA 보고 — 4/5 코호트 완료, 폐 진행 중.
- **[BIOP01]** 층② 인과 수위(단서 달고 실을지 vs seed 반복 확보 후) 판단 자료 정리.

---

## 5. 회의 후 즉시 굴러가야 할 것

1. **저자·소속·corresponding 확정** → 두 논문의 공개 게이트 동시 해제 → BIOP01 투고 절차, BIOP02 preprint 일정 확정.
2. **BIOP01**: 투고처 결정 → PR #4 병합 → 남은 `<FILL>`(DOI·라이선스) 채움.
3. **BIOP02**: Results 초안 + 코호트 특성표(Table 1) 착수 — 가장 빨리 타깃 저널 수준에 오르는 두 가지.
4. **Yale A3/A4 기한 확정** — 미달 시 Supplement 강등을 사전 합의.
5. **JIRA**: 하차자 티켓 6건 종료, 스터디 과제 트랙 존폐 결정, 리뷰어 재분산.

---

## 6. 회의 전 공지용 문구 (그대로 복사)

안녕하세요. 오늘 논문 회의는 **BIOP01·BIOP02 두 편**을 함께 다룹니다. 미리 봐주시면 좋을 것들을 정리했습니다.

**두 논문 모두 같은 지점에 막혀 있습니다 — 저자 목록·순서·소속·corresponding(이름과 이메일)입니다.** 이것만 정해지면 BIOP01은 투고 절차로, BIOP02는 preprint 일정으로 각각 넘어갑니다. 회의 전에 이 부분에 대한 생각을 정리해 오시면 좋겠습니다.

- **BIOP01**은 자동으로 할 수 있는 정비가 끝났습니다(적대적 자체리뷰 반영, Supplementary 그림, 참고문헌 69편). 투고처를 Genome Biology로 도전할지 Cell Reports Methods를 기준으로 갈지 의견을 부탁드립니다.
- **BIOP02**는 어제 **Critic 게이트를 통과(PASS)** 해서 집필 착수 조건이 갖춰졌습니다. 타깃은 npj Precision Oncology입니다.

**배경 자료**: 통합 브리프 `BioProject02/MEETING_BRIEF_2026-07-21_BIOP01+BIOP02.md` (프로젝트별 상세는 각 브리프 참조). 각자 준비하실 항목은 이 문서 §4에 이름별로 정리해 두었습니다.

부담 없이 보실 수 있는 분량만 보고 오셔도 됩니다. 나머지는 회의에서 같이 정리하겠습니다.
