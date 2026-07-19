# Session Log — BioProject02 전용

> **프로젝트별 분리(2026-07-10):** 이 로그는 **BIOP02만** 기록한다. 전역 `~/.claude/SESSION_LOG.md`(BIOP01+BIOP02 혼합 과거 아카이브)와 **동기화하지 않는다.** BIOP01 기록은 BIOP01 로그/전역 아카이브 참조.
> 최신 항목이 위(역시간순). 같은 날짜는 새벽→낮→저녁 순으로 아래로 내려갑니다.

---

## 2026-07-19 — 브랜치 위생·병합게이트 + G2 remediation(PR #36) + 블로그 07 초안 + watchdog 등록

**브랜치 위생 + 병합 게이트**
- BIOP01이 넘긴 "d0f3f4f는 BIOP02" 검증: split lock 정본 hash는 이미 main meta에 있고 folds 미러·stamping만 누락 → **focused PR #32**로 이관(내가 앞서 "main에 folds 있음"이라 오판 → git ls-tree exit0 함정, 정정). **용기님(braveji)이 PR #32 머지 + BIOP02-41 Critic cross-sign PASS**(6ffdeb9).
- docs/-53가 fetch만 하고 merge 안 해 main보다 97앞/13뒤로 드리프트한 것 정리(merge origin/main, 뒤 0). **재발방지**: SessionStart 훅 `.claude/hooks/git_drift_check.sh`(개인 settings.local.json) — 세션 시작 시 앞/뒤 격차 표시. memory `feedback-branch-hygiene`.
- **병합 게이트 봉인** `experiments/crosscancer/MERGE_TO_MAIN_CHECKLIST.md`(G1~G5) — 즉흥 병합 방지. **G1 결과확정 kkkim 승인** + G3 claim규율 검증.

**G2 Critic remediation (PR #36, base main, focused)**
- 그간 braveji G2가 reject(5 blocker)→caution. main이 "50bb7c9 remediation 병합 대기"였는데 정본 JSON이 main에 없던 provenance 불일치 → PR #36으로 전달: 5-seed 우연배제(3암종, ★두경부 HPV 0.9594 PASS thr 0.790) + pixel-mean baseline(4암종).
- **위암 Lauren 양성대조 FAIL(0.54) 원인 진단** `LAUREN_POSCONTROL_DIAGNOSIS.md`: 파이프라인 고장·데이터희소 아님 = **Lauren 특이 site-교란**(dev 0.963→holdout 0.536, pixel-mean 0.63>MIL 0.54, 유병률 site종속 HU100%~CG18%). 권고 "위암 전체 저신뢰"→"Lauren 국한"(MSI 일반화 정상).
- **subtype-only baseline** `sh_subtype_baseline.py`+`SUBTYPE_BASELINE_NOTE.md`: cross-cancer 대부분 순환→비순환 폐 EGFR/KRAS from histology만. EGFR 0.767<MIL 0.852(등급적) · **KRAS 0.793>MIL 0.681(필수, MIL이 histology 못넘음)**. baseline 3종 폐 변이축 완비. JIRA -96 #11168~11170.
- kkkim 몫 G2 전부 완료 → 잔여 = sjpark #4·jhans #5 sub-check → braveji 3차 재검토(팀 대기).

**블로그 07편 초안(교차암종 치환지도)**
- `blog/2026-07-14_BIOP02_07_crosscancer-substitutability_DRAFT.md`(브랜치 `docs/BIOP02-blog07-crosscancer`). 비어있던 07 슬롯 채움(08=그림제작·09=스킬로 다른 주제, 중복 아님 검증). STYLE_CONTRACT 준수·수치 기록대조. **발행 EMBARGO(critic caution)** — 사용자 결정 (b): Critic pass 후 윤문(korean-style-rewriter Pass-2)·발행.

**watchdog 등록(다중 FM 위험완화)** — 사용자 선택
- HANDOFF의 "crontab 미등록" 진짜 원인 = **컨테이너에 cron/crontab 자체 없음**(실측). crontab 대신 **detached setsid 자기루프** `watchdog_loop.sh`(PID 873918, PPID=1, 세션 무관) 등록 — 10분마다 watchdog.sh 호출, master/재학습 러너 죽으면 idempotent 재기동. memory `infra-no-cron-use-detached-loop`. 다중 FM 임베딩은 대장 진행 중(HNSC 밤샘 완료 확인).
- 참고: braveji=**지용기(용기님)**, '이용진' 아님(memory 정정).

## 2026-07-18 — 다중 FM 2-FM 개편 + 스킬 벤치마크 5영역 + 블로그 분석/환경 분리 + 인용검증기 공유
**진행:** 어제 착수한 다중 FM 임베딩을 UNI2-h까지 확장(2-FM)하며 여러 버그를 잡았고, 외부 스킬 벤치마크를 5개 영역으로 마무리했으며, 블로그를 분석/환경 2계열로 나눠 Confluence·Drive에 반영하고, 인용검증기를 BIOP01과 공유했다. 집필(월요일 시작)을 위한 JIRA 요청 2건도 발송.

- **다중 FM 2-FM 개편(JIRA BIOP02-101, PR #65):** kkkim 결정으로 UNI2-h 추가(reg token 8개, 1536-d) + raw는 전 FM 검증 후에만 삭제(crosscancer만, BRCA 절대 보존). 버그 4~5건 실측 수정: HNSC 진입 시 gdc_query 일시실패가 master 죽임(try/except 격리), disk_guard가 없는 raw 디렉토리 statvfs(free_gb 상위 마운트로), 가드가 /workspace에 300GB 오적용(볼륨별 임계 raw300/ws60), 부분 raw(218MB→66MB) 무한재시도(크기검증 후 재다운로드). BRCA v2·u2 완료, HNSC 진행 중.
- **스킬 벤치마크 5영역 완료(전부 "차용 없음" 또는 참조만):** 인용검증(medsci 1/5·AIPOCH 방향반대)·재현성(ClawBio 검증함수 없음)·병리(실행코드 0줄)·단일세포(공식이나 파이프라인 무관)·집필(TRIPOD+AI 체크리스트만 참조 차용, abstract-trimmer는 hedge 삭제라 금지). 원칙 재확인: 표준 기계작업만 차용, 검증 게이트는 자작. 부수발견: pathology-roi-selector가 .py 0개인데 self-eval 92점(도구 자기평가 신뢰 금지).
- **자체 인용검증기 + 전역 공유:** `verify_citations.py`(우리 실패 5건 5/5, medsci 1/5, 뮤턴트 8/8 kill) + `bib_to_cites.py`(.bib 어댑터, 다줄·중첩 파싱). literature-scout·paper-critic에 물림. BIOP01에 복사·검증 완료(refs.bib 19편: VERIFIED 10·저자없음 4·검토필요 5), BIOP01 TODO에 향후 적용 명시.
- **블로그 분석/환경 분리:** Confluence "BIOP02 개발 블로그" 아래 분석 편(53477377)·환경 편(53510145) 그룹 생성, 기존 6편 재부모화+그룹내 재번호(분석1~4·환경1~2), 08편(분석5)·09편(환경3=스킬벤치마킹) 신규 게시. Drive 통합본 2종 분리(분석·환경). 09편은 3중 검증(naturalness·fidelity·ai-tell) 통과. BIOP01 블로그는 검토 후 분리 안 함(환경 1편뿐).
- **집필 준비(월요일 시작):** braveji에 Fig2/3 Critic 서명+HNSC HPV pixel-mean 판정 요청(BIOP02-91 c.11320). sjpark/jhans에 Yale 앵커 A3/A4 리마인더(BIOP02-80 c.11321, 이미 통지됐으나 미착수). TRIPOD+AI 등 보고표준 체크리스트를 docs/reporting_checklists에 참조자료로 도입.
- **⚠️ 사용자 피드백(memory 기록):** ① 모든 한글 문서 윤문체(내부용어·표덤프 금지, `feedback_korean_prose_style`) ② 호칭 아예 쓰지 말 것(내가 "형"이라 반복해 미스젠더링 — 김가경은 여성, kkkim은 이니셜, `user_kkkim` 갱신) ③ 발표자료 숫자를 합격선으로 쓰지 말 것(`feedback_evidence_sourcing`) ④ "했다"기 전에 실물 확인(`feedback_claim_vs_action`).
- **인프라 memory:** HF 캐시 `.incomplete` 함정·Virchow2/UNI2-h register token·detached conda 절대경로(`infra_hf_fm_embedding`).
- **(후반) 블로그 분석/환경 분리:** Confluence "BIOP02 개발 블로그" 아래 분석 편(53477377)·환경 편(53510145) 그룹 생성, 기존 6편 재부모화+그룹내 재번호(분석1~4·환경1~2), 08편(분석5)·09편(환경3) 신규 게시. Drive 통합본 2종 분리 업로드. 09편 3중 검증 통과. 구 Drive 통합본(7/5)은 수동 휴지통 안내(MCP 삭제 불가).
- **(후반) 인용검증기 BIOP01 공유:** `bib_to_cites.py`(.bib 어댑터) 신규, `verify_citations.py`가 프로젝트 무관 실증(BIOP01 refs 19편: VERIFIED 10·저자없음 4·검토필요 5). BIOP01 저장소에 도구 3개 복사·커밋(2d18ad0), BIOP01 TODO에 향후 적용 명시. `docs/shared_assets_2026-07-18.md`에 전역/프로젝트별 판단 산문 정리.
- **(후반) 집필 스킬 벤치마크 + 보고표준:** 5번째 영역(집필) 완료 — TRIPOD+AI 체크리스트만 참조 차용(`docs/reporting_checklists/`, README 윤문), abstract-trimmer는 hedge 삭제라 금지. 집필 블로커 요청 2건: braveji Fig2/3 서명+HNSC HPV pixel-mean(BIOP02-91 c.11320), sjpark/jhans Yale A3/A4 리마인더(BIOP02-80 c.11321).
- **(후반) 다중 FM 재학습 준비:** kkkim 결정=재학습 Owner는 kkkim(대행), Reviewer는 sjpark/braveji(Owner≠Reviewer). CLAM 학습시간 실측=코호트당 수분~17분(대장 UNI 267s). `run_mil_cost.py`에 `--fm {uni|virchow2|uni2h}` 파라미터화(UNI 기본 동작 불변, 회귀 스모크 확인). `multifm_retrain_watcher.py` 대기 러너 백그라운드 가동 — 대장·폐 임베딩 완료 시 자동 재학습(결과 critic_status pending). `README_multifm_retrain.md`.
- **(후반) 버그 수정:** DONE_BRCA가 virchow2 단독 시절 표식인데 UNI2-h 추가 후 스킵 유발 → BRCA uni2h 1/1010 멈춤. 표식만 믿지 않고 FM별 임베딩 개수 실측해 스킵 판정하도록 수정. BRCA uni2h는 cross-cancer 완주 후 재실행으로 이어짐.
- **(후반) 피드백 memory 추가:** 호칭 아예 쓰지 말 것(`user_kkkim` 갱신 — 김가경 여성·kkkim은 이니셜), 모든 한글 문서 윤문체(`feedback_korean_prose_style`), SESSION_LOG 매일 기록(`feedback_session_log_daily` — 반복 누락 지점, git 추적이라 커밋 필요).
- **(저녁) 백그라운드 끊김 방지 점검:** 임베딩 master·재학습 러너 둘 다 독립 세션(setsid)이라 창 끊겨도 생존 확인. HNSC 임베딩 348/472(3.2분/슬라이드, 07-19 새벽 완료 예상). 프로세스가 버그로 죽을 때 자동 재기동할 `watchdog.sh` 작성(idempotent, 완료 마커 있으면 skip) — 단 시스템 crontab 등록은 자동 분류기에 막혀 스크립트만 준비, 수동 등록 2줄 안내.
- **(저녁) 원고 폴더 신설 — kkkim 지시:** `BioProject02/manuscript/` 생성(월요일 집필 시작 목표). README(착수 가이드·**실측 숫자 표**·검증 게이트) + sections/ 5종 골격(abstract·intro·results·methods·discussion, 각 근거 파일 포인터 + `<FILL>`). 헤드라인 숫자는 결과 JSON 실측으로만(대장 BRAF 0.868·폐 LUSC 0.939·두경부 HPV 0.959·위 diffuse 0.536=정직한 음성, 전부 hypothesis_only·critic pending). Yale·다중 FM은 placeholder.
- **(저녁) 타깃 저널 집필 준비 — kkkim 지시:** 타깃 확정 = **npj Precision Oncology**(스트레치 Nat Commun/npj Dig Med/Med). 서브에이전트로 같은 저널 H&E→분자 논문 4편(자궁내막·자궁경부·NSCLC·Dawood 2024) 실제 정독 → `manuscript/WRITING_TARGET_GUIDE.md`(논문별 7축 + 종합 골격). `TARGET_JOURNAL_GUIDE.md`에 저널규정·보고표준·갭분석·preprint경로 정리. **핵심 갭 3(월요일 우선): 코호트 특성표·대체 동등성 검정(Paper B DeLong C-Index 원형)·NPV 임상효용 이중보고.** 차별화: 사전등록+TRIPOD/CLAIM 명시(exemplar 4편 전부 없음). ⚠️ 서브에이전트 정독 수치는 요약모델 훼손(CI 상한 1.003) — 구조만 신뢰, 수치 인용 시 원문 PDF 대조.
- **(저녁) preprint 정책 확인:** npj Prec Onc는 preprint 허용(선출판 아님). 임상 엔드포인트라 medRxiv 정합. 내부 게이트=저자정보 팀합의 + Critic 서명 후 공개.
- **(저녁) exemplar 수치 원문 재검증:** 서브에이전트 정독 수치가 요약모델 훼손 우려 → Europe PMC REST 원문 JSON(요약모델 미경유)으로 초록 헤드라인 대조. 훼손은 **딱 1곳**(Paper A p53abn class-wise CI 상한 1.003→실제 1.000). 초록 헤드라인 전부 정확 확인(A 0.867·C 0.87/0.96/0.88/0.83·B 생존p n=545). 본문 전용 수치는 초록에 없어 인용 시 PDF 대조 필요. 세 가이드 문서에 반영. 우리 원고 숫자는 결과 JSON 직독이라 무관.
- **(저녁) 커밋:** manuscript/ 8종 + watchdog.sh + SESSION_LOG → **c9fbe74**(feat/BIOP02-91 브랜치, 로컬 커밋·미푸시). 원고 관련이라 푸시는 확인 후.

---

## 2026-07-17 — 논문 구조 확정 + Yale 앵커 완료 + Fig2/3 + 다중 FM 착수
**진행:** Paper A/B/C 관계를 확정(C 플래그십 1편 수렴)하고, Yale HER2 아웃컴 앵커를 오버나잇으로 임베딩 완료했으며, 헤드라인 그림 Fig2/Fig3를 분리 산출하고, 다중 FM 견고성(Virchow2) 임베딩을 백그라운드로 착수했다.

- **논문 구조 확정(정본 `research/paperC-positioning/PAPER_STRUCTURE_DECISION_2026-07-17.md`, PR #57):** 결정 1-A(Yale 실제-결과 앵커를 C 본문에)·2-B(Paper B 무거운 엔진 조건부 보류)·3-A(jhans→Yale 앵커)·4-A(라벨 드리프트 정리). 前 Paper A = C의 유방 anchor 챕터(D11/D12 흡수).
- **Yale HER2 outcome anchor(A2) 완료 276/276, failed=0:** TCIA HER2-TUMOR-ROIS(trastuzumab 85 + HER2 191). 전부 1024-d·손상0·finite. Aspera 게이트 우회 = PathDB JSON API(memory `infra_tcia_pathdb_download`). `/workspace/data/cache/biop02/yale/uni_v1/` + manifest. PR #59. A3(sjpark)·A4(jhans) 통지(BIOP02-80 c.11283/11284).
- **Figures(PR #63/#64 머지):** Fig2(confusion×distance + cost overlay)="이 한 장이 논문"인 결정그림, 브랜치에 갇힌 것 해소. Fig3(축별 cost + headline contrast CI) 신규 분리. 둘 다 critic_status pending → 근거 JSON 서명 전 headline 승격 금지. 정직성: per-axis cost는 라우팅 스킴 따라 endocrine·chemo 반전 → 안전주장 아님.
- **인용 무결성(PR #58/#60/#62):** REFERENCE_LIST 77편 + CITATION_AUDIT(33+ 정확, 미확인 0) + CITATION_CORRECTIONS(우리 문서 오류 5건 정정 — 존재하지 않는 "Williams 2022" 인용 등). Ding 2025 실존 확인.
- **다중 FM 착수 + raw 보관 정책 변경(Leader 결정):** LRU 자동삭제로 cross-cancer raw 2,588장 소실 → 재다운로드 비용 발생 → 프로젝트 기간 중 raw 보관, 디스크 부족 시 자동삭제가 아니라 정지+사람 판단. CLAUDE.md 금지조항에 기간한정 예외 명시.
- **Critic Inspect eval 파일럿:** `evals/critic_pilot/`(66/66, 뮤턴트 전멸). ★캔 것: HNSC hpv_pos 헤드라인 0.9594(CI없음) vs pixel-mean 0.9224[.., .9745] CI가 헤드라인 포함 → braveji 판정 대상.

---

## 2026-07-12 (밤) — 대장 증분 검정 완료 + 블로그 그룹편성 + MCP 드롭 재시작
**진행:** 직전 세션 pivotal 미결(대장 MSI/anti-EGFR 증분)을 완결. per-patient p_HE를 seed=42 결정론 MIL 재실행으로 복원(재현 AUROC 0.9184/0.7053 커밋값 일치 검증), 통상병리 baseline=점액성 조직형+우측/좌측 편측성(cBioPortal coadread, 등급/oncotree 없음)으로 중첩 로지스틱 증분 계산.
- **결과(D13):** anti-EGFR(점돌연변이 위험검정, n_pos84) 통상병리 대비 **+0.049**(CI 0.003–0.096, LR p 0.026). advisor 요청 견고성: BH 다중비교 통과(0.030)·CV 7시드 부호 안정(mean +0.052)이나 **Bonferroni 미통과**(0.208), +CMS 넣으면 소멸. MSI(n_pos21) +0.129지만 **탐색적(INCONCLUSIVE)**.
- **판정:** 엄격한 이분법 법칙 안 서고(점돌연변이도 작은 증분), 기울기도 검정력 있는 교차암종 대비 부재로 미확립 → **법칙 생사 선언 보류, STAD/HNSC held-out 필요.** advisor 교정: 4마커 교차암종 표는 기준선 두께 섞여 like-with-like 아님 → 암종 내 동일기준선 비교만.
- **산출:** `COLORECTAL/full/{incremental_crc_results,incremental_crc_robustness,treatment_pHE}.json`·`CONCLUSION_CRC_INCREMENTAL.md`·`run_incremental_crc[_robust].py`·`dump_treatment_pHE.py`. PROGRESS_DECISIONS D13. 커밋 **57eb768** origin push 완료.
- **블로그:** cross-cancer 편 4편+사이드바 그룹편성 사전초안(`blog/2026-07-12_..._GROUPING-DRAFT.md`, 3층위=예측충실도/통상병리증분/치환비용).
- **인프라:** GPU 재배치 감시자 기동(PID 230205) — STAD 완료 시 HNSC를 3-GPU 균등 재배치. **atlassian MCP 40종 세션 중간 드롭**(서버 정상, 세션만 핸들 상실) → 재시작으로 복구, 메모리 [[infra-atlassian-credentials]] 기록. BIOP02-53에 Paper C 방향 공유 ADF 댓글(id 11107, biospin-leader 멘션).
- **사용자 피드백:** 채팅·문서에서 "정직/붕괴" 및 em대시 남발 금지(메모리 [[feedback-plain-professional-writing]] 갱신).

---

## 2026-07-12 (저녁) — held-out 법칙검정 + confound 반전 + 논문 재정립 (대형 세션)
**진행:** cross-cancer flagship을 5개 암종으로 확정(D12, 위·두경부 추가)하고, 사전등록 법칙 봉인 후 폐·위 held-out 법칙검정을 9시 회의 전 확보. 이어 사용자 제안 견고성 검정들이 서사를 **정직하게 뒤집음**.
- **held-out 결과(정직)**: 폐 — 조직형 양성대조 0.925 통과(파이프라인 sound), 변이축(EGFR/KRAS) n_pos 14-15로 **INCONCLUSIVE**, TRU-최고 예측 미스. 위 — HER2-amp near-chance이나 exploratory, **Lauren 양성대조 실패(라벨 희소)**. **법칙=유방+대장(well-powered)서 확립, held-out은 방향적 corroboration.**
- **⚠️ HER2 "blind" 반증**: 3정의(IHC/FISH/CNV) 검정 — 깨끗한 CNV 라벨로 H&E ~0.73(well-powered·누수통제). 0.599는 노이즈 IHC+작은 val split. CNV·IHC·FISH 3중 일치(89-94%)+CPTAC 단백질(d≈4).
- **⚠️ 프레임워크급 confound(advisor)**: "H&E가 통상병리(조직형·아형)를 보는 것 아니냐"(Critic #2). 정확 incremental — **H&E가 통상병리(조직형) 넘어 ER(Δ0.24)·HER2(Δ0.18) 예측(유의)** = 마커-특이. 단 PAM50(분자아형·circular) 대비는 작음(ceiling). **MSI/RAS(대장) 미완**(per-patient p_HE 미저장 → `run_cms_and_routing.py` Part-B에 msi/anti_egfr `patient_proba` 저장하면 즉시 가능). **MSI가 대장 법칙 사활.** → 함의: **partially_supports**, binary(blind/visible)→gradient.
- **비용 논거 붕괴(사용자 지적)**: NGS 패널/WGS가 변이·MSI(in-silico)·TMB 일괄 → H&E-triage 절감 미미. **cost 전면 금지, 과학+turnaround(H&E 당일 vs NGS 2주)+아카이브로.** 의의=골드스탠다드 대체 아니라 결정지도.
- **만든 것**: 자동리뷰 시스템(config-driven·project-agnostic·enabled=false), 개념도·결정지도·비용 그림(전부 보류—confound 반영 전), PAPER_DIRECTION §의의·용어정의, 다수 positioning 문서.
- **회의(21시) 권장**: WIP — well-powered 유방+대장만, confound 검정 중·MSI가 가름·blind/visible 잠정 명시. 그림 보류. 법칙 생사 선언 X.
- **⚠️ 반복 패턴(교정 중)**: 결론을 증거보다 앞서 여러 번 냄(0.014·clean label·cost sweet spot·crude oracle). memory 등록 + advisor·사용자 지적. **정확 검정 후 프레이밍.**
- **다음 최우선**: MSI/RAS incremental 완결(patient_proba 저장→검정) → 법칙 생사 판정 → 법칙·그림·비용 문서 confound 반영 재작성. 배경 STAD/HNSC 임베딩 회의 후 완성.

---

## 2026-07-12 (대장 CMS 아형 확보 + 비교 층위 교정 + 서사 재정립)

### 개념 교정 (사용자 지적으로 큰 방향 수정)
- **비교 층위 오류 발견·교정:** 유방 HER2(아형)와 대장 BRAF(변이)를 1:1로 비교해 "원리"라 제시한 것은 개념 층위가 다른 오류였다. 사용자 도메인 경험으로 잡혔다. 재발방지책을 memory `feedback-comparison-like-with-like`에 등록, `docs/ai-collaboration-cautions.md`(사례집)에 기록.
- **서사 재정립(사용자 질문 "H&E로 뭘 보나"):** "H&E→아형 예측"에 고착하지 않는다. H&E의 본래 정보는 형태(진단·조직형·등급·TME)이며, cost-of-substitution은 "각 결정 특징이 형태학적 상관물을 갖는지 → H&E 충분 vs 분자검사 필수의 결정 지도"다. 아형은 한 사례일 뿐. 이러면 아형 vs 변이 함정을 구조적으로 우회.

### 대장 CMS 아형 (like-with-like 준비 완료)
- 조사: CRC 아형 체계 전면 조사(`CRC_SUBTYPE_INVESTIGATION.md`). CMS=PAM50 격(아형), MSI-H=저비용축, RAS/BRAF/HER2-amp=고비용(HER2 격). CMS는 치료 라우팅 X(예후용). H&E→CMS 예측은 이미 됨(imCMS 2021) → 우리 novelty는 예측 아니라 cost-of-substitution.
- 계산: R env `cms-r`(CMScaller) 설치 → TCGA-COADREAD RNA-seq(cBioPortal 템플릿 유전자)로 **CMS 자가계산**(592샘플).
- 권위 라벨: **Synapse 토큰(사용자 재발급)으로 `cms_labels_public_all.txt` 다운로드** → TCGA 573환자 consensus. 최종=network 확정(80%)+RF보충(20%). 표준은 network consensus, RF(CMSclassifier)는 그로 학습된 공식 적용도구.
- **3자 일치도표**(`CMS_CONCORDANCE.md`): Synapse×CMSclassifier(RF) 100%(RF가 consensus 학습→동어반복, 독립검증 아님) · **CMScaller vs consensus 84%(유일한 독립 교차검증, 문헌 ~0.83 정합)** · confusion 2표. CMS1/CMS4 recall 높음(H&E 형태 뚜렷), CMS2↔4 경계 엇갈림.
- **최종 분석은 권위 consensus 라벨 사용**(499환자 임베딩 보유), 자가계산은 재현검증용 보존.

### 폐암 아형 (조사 완료, 라벨 준비 TODO)
- `LUNG_SUBTYPE_INVESTIGATION.md`: 전사체 아형(LUAD TRU/PI/PP·LUSC classical/basal/secretory/primitive)=PAM50 격. LUAD/LUSC 조직형=양성대조. EGFR≠HER2-blind(형태 상관물 有, 0.77-0.89) → graded 이야기. 예측은 스쿱(Chen 2021·Coudray 2018).
- ⚠️ **폐 전사체 아형 라벨: cBioPortal SUBTYPE 필드 비어있음(LUAD/LUSC 0건)** → TCGA 마커논문(LUAD Nature2014·LUSC Nature2012) supplement 또는 Liljedahl SSP/Wilkerson centroid 계산 필요(CRC CMS와 동일 패턴). **다음 단계.**

### 자율 잡
- 폐 임베딩 816/1053 진행 중(대형 tail, 오후 완료 예상). 대장 완료. watcher·waiter 가동(완료 시 알림).

## 2026-07-11 (✅ split_policy_v0 data-owner LOCK + cross-cancer Phase 1 + BIOP02-53 리뷰)

### 오후~저녁 (cross-cancer 자율실행 + ST결정 + Angle A + env 공용화)
- **🟢 cross-cancer 전량 임베딩·supervised 체인 자율 실행**(사용자 (B) 지시, GPU sunset 8/15 전): 폐 1053+대장 625 UNI 임베딩 detached, 오케스트레이터가 임베딩 완료 감지→라벨·split·MIL 자동. 튜닝 수렴(SSD raw·OMP4·10워커). 저녁 17:24 = 폐 487·대장 411. commit e7774de·31c4e16. 자재검증(prevalence·site-disjoint·histology 스모크 PASS)·advisor 게이트 내장.
- **ST 트랙 결정 D9 (지금 개설 X):** literature-scout+novelty-strategist + **Path2Space(Cell2026) bioRxiv 정독** → 우리 cost-of-substitution **미스쿱 확정**(Path2Space=바이오마커 advocacy·반대방향). Xenium 유방 ERBB2 포함 확인. ST는 데이터·마감·Paper B 의존으로 보류. `research/paperA-positioning/2026-07-11_HE-ST-scoop-and-angles.md`.
- **✅ Angle A 착수**(Paper A HER2 강화, JIRA **BIOP02-97**): Andersson HER2+ ST 8명 → 확진 HER2+ 종양도 면적 일부가 HER2-음성 배경 ERBB2(보수 median 12%·range 7-30%)=치환비용 floor. commit 6c73620. **역치 방법론 강화 中**(research-methodologist).
- **spatialpatho env 생성+/opt 공용화**(BIOP01 조율): base→전용 env `spatialpatho`(cu124) 클린설치→`/opt/envs/spatialpatho` clone·검증. commit ee9f00a·969847f. 미완: idle 후 원본제거+스크립트 PY 전환.
- **BIOP01 shared-infra**: `guide/gpu_env_biop02.md` canonical env 문서(a968ba4), BIOP01 SHARED-INFRA-GUIDE §4.2 채울 정보 전달.

- **✅ split_policy_v0 data-owner LOCK 완료** (commit `d0f3f4f`, JIRA BIOP02-41):
  - 정본 `split_hash=5995f29d3978b831` = `sha256(repr(sorted((case_id,split))))[:16]`(build_manifest 정의), manifest 재현 일치 검증.
  - **advisor 지적 반영 — 학습 정합 선검증**: UNI·CONCH·EXAONE embedding manifest(/workspace) 3종 dedup case_id→fold **1010/1010 일치·fold 불일치 0** → sjpark 전 실험이 잠긴 split 사용 확인 후 stamping(decorative lock 방지).
  - lock criteria: patient-overlap 0 / site-disjoint 0위반(37 site) / class balance(train 559/148·val 115/37·test 108/43) 검토.
  - 산출물: `split_policy_v0_folds.json`(사람용 case_id→fold 미러, 2차 해시 미발급=정본 단일화)·`split_manifest_meta.json` lock 블록·metrics.json 14개 split_hash stamping(template=placeholder)·`split_policy_v0.md` §6.1 lock record + §9 data-owner 서명.
  - **BIOP02-41 discrepancy 정리**("완료"인데 lock 산출물 부재) 댓글 11085 + -53 게이트 업데이트 11086.
  - 🔴 **남은 유일 블로커 = Critic cross-sign(braveji)**, owner≠reviewer로 self-review 금지 → braveji 서명 시 -53/-50/-56 Critic-pass 개방.
- **✅ cost-of-substitution B' receptor 라우팅 실행**(BIOP02-90 해소로 언블록, commit 5164a0c·e654475):
  - sjpark indexed 예측(n=294) → `patient_routing_cost_receptor.json`. antiHER2 100% mis-route(양 라우팅 robust)·endocrine 5%·chemo 73%. 헤드라인 contrast robust(PAM50 0.340·receptor 0.381, 둘다 CI 0배제).
  - **정직 판정**: endocrine 5%/chemo 73% 반전 = 외부 다수클래스 붕괴(예측 endocrine 89%(실제61%)·antiHER2 **0%**·chemo 11%; HER2 head 양성 0발화, ER over-call TNBC 73%) → majority-collapse 아티팩트. **단단한 결론 = HER2축 하나**(분자검사 필수). cost-of-sub 렌즈가 raw AUROC 숨긴 외부 miscalibration 노출 = 방법론 기여.
  - decision map §0/§2/§3 정직 갱신. **발표용 fig 개편**(PAM50 vs receptor 오라우팅율 비교, HER2 불변 강조, 겹침 QA 통과).
  - ⚠️ **BIOP02-41 임시 lock 결정**(사용자): dependent 티켓(-50/-53/-56) 임시 진행, Critic 서명은 braveji(오늘 확인 難) 후. **7/15 발표자료 마감** 우선. 멘션 알림 이슈 정정(biospin-leader accountId, memory BIOP01/02 양쪽 기록).
- **🟢 Cross-cancer 전량 임베딩 자율 착수(사용자 (B) 지시, GPU sunset 8/15 전 논문용)** — 폐 LUAD541+LUSC512=1053 → 대장 COAD459+READ166=625 UNI 임베딩. 자율 드라이버 `run_embed_crosscancer.py`(GDC스트리밍→타일→UNI, per-slide SSD LRU, idempotent, 하트비트), 스모크 검증 후 detached(setsid PPID=1). **튜닝 실측**: HDD 18워커=thrash(load133)→SSD 이전, 무제한스레드 10워커=thrash(load73)→OMP4, 최종 **10워커(5/암종)**. commit e7774de. **재개 가이드 `experiments/crosscancer/RESUME_CROSSCANCER.md`.** JIRA 에픽 -93 하위 **94(임베딩)/95(라벨·split)/96(MIL·cost)** 생성. supervised 후속(라벨·MIL·cost)은 임베딩 완료 후.
- **Cross-cancer(Paper C, BIOP02-93) Phase 1 착수** — 리더 사인오프하 별도 트랙(A/B는 BRCA-only 유지).
  - 세포주 치료축 게이트: 대장 **GO**(BRAF7/MSI16/KRAS22), 폐 **PARTIAL**(EGFR6·KRAS-G12C9·chemo68 GO / ALK2 NO-GO). commit 3fee857.
  - 냉동 세포주→약물 지도+치료거리(폐 3축·대장 2축): positive control 통과, 표적↔chemo 거리 폐 0.914·대장 0.868(BRCA HER2↔chemo 0.765 재현). commit 17e0ef7.
  - **GPU 파일럿 PASS**: TCGA-LUAD 15장 다운로드→타일→UNI(N,1024) 무수정 작동, cancer-agnostic 이식성 검증(infra-only, 성능주장 아님). GDC 우회 memory 기록(infra_gdc_api_download: gdc-client pip불가→REST /data, in연산자 500→=+and, 진단슬=파일명 -DX). 전체 코호트+MIL은 GPU 게이트(발표/Paper A 후).
- **BIOP02-53 리뷰**: sjpark 구현·2회 self-critic·braveji Critic 완료. 최신(11082): ER/PR NOT ADDITIVE(외부 subtype_only 상회=TCGA↔CPTAC 배치 아티팩트), HER2 reject, **PAM50 4-class 0.818 GENUINE(pass 1순위)**. sign-off 유일 블로커=kkkim split_policy_v0 lock.
- **티켓 감사**: kkkim 할당 22(미완 -73·-78·-91진행·-93)/멘션 22. 핵심: **split lock이 -50/-53/-56 공통·유일 블로커**, BIOP02-41 완료인데 실제 lock 산출물(서명+해시) 없음=discrepancy.
- **다음 세션 이어받기:** ① ~~split_policy_v0 formal lock~~ → **✅ 완료(위)**, 이제 braveji Critic-sign 대기. ② ~~sjpark BIOP02-90 리마인드~~ → **해소 확인**(다른 창: ER 예측 387 교정 `17e7b9b` + `cptac_ext_predictions_indexed.csv` main 도착 → cost-of-sub 라우팅 언블록). **receptor 라우팅 compute_cost.py B' 실행** 가능(다음 액션). ③ sjpark 제안 11001(PAM50 중심 Paper A 재구성) 수용 방향.
- git: 로컬 main 21 behind origin, 브랜치 push 완료(durability).

## 2026-07-10 (오후 — 블로그 윤문체 마무리 + 팀 티켓 검토 + PAM50 소스 규명)

*(이 창 세션. 밤사이 다른 창에서 진행한 Paper A cost-of-substitution·PR#24 머지·블로그 fix 등은 HANDOFF/TODO 참조.)*

- **로컬 브랜치 main 동기화** — merge `909502b`(push 안 함). `.gitignore` 충돌만 양쪽 합집합 해소, 동시 세션 미추적 파일·sjpark 예측 4파일(main 동일본) 보존. *(이후 main 추가 전진으로 다시 behind 5.)*
- **블로그 6편 윤문체 개별 검토 완료** — 1:91 / 2:90 / 3:90 / 4:89 / 5:88(어제 83→수정) / 6:79→**범위한정 2차 윤문**(대조부정 11→4·절말격언 3곳 해제; load-bearing 대조부정=귀속·hedge 보존, grep 검증). 통합본·`/workspace/blog/BIOP02/` 갱신.
- **팀 티켓 검토(64/68/52·49·90·55):**
  - 64/68(sjpark Fig3/4) 완료 — **Fig4가 공식 CPTAC 라벨(BIOP02-55)·has_her2=294 정확히 사용** 확인(내 재조인 올바로 소비). 판정: ER/PR "SIGNAL NOT ADDITIVE", HER2 "NULL/reject", PAM50 caution.
  - 52(jhans PRISM-GDSC) 완료, kkkim 직접 액션 없음.
  - **49(jamie HER2/PAM50 QC):** [Not Evaluated] 버그(has_her2 816→698) 정확·다운스트림 무영향 확인. **PAM50 소스 규명 = manifest PAM50은 `tcga_brca_pam50_computed.csv`(Parker 2009 계산본, conf 0.808~0.925)와 1009/1009 100% 일치** → jamie 57% 불일치는 "계산본 vs curated atlas"라 정상. 소스+`_PROVENANCE.md` 레포에 복사(미커밋). balance 표 sign-off(site-disjoint OK, HER2/PAM50 fold drift caveat). **JIRA -49 코멘트 11064.**
  - **90(내 subtask): 해소 확인** — ER predictions_ext 294→**387 교정**(HER2와 분리, commit `17e7b9b`), **`cptac_ext_predictions_indexed.csv` main 도착** → cost-of-substitution 라우팅 **언블록**.
  - **55(jamie 공식 라벨): 완료 검증** — CPTAC↔TCGA patient-level leakage **충돌 0건**(locked 1010, split_hash 5995f29d). 공식 has_er 120/has_her2 95 case → slide 387/294.
- **블로그 4·5편 공식 라벨 반영** — "임시(395/653)·검토필요" → "공식 BIOP02-55 교체·재실행 완료"(HER2 has_her2 294 기준 0.53 유지). hedge 전부 보존(HER2 reject·ER/PR not-additive·caution·ceiling), 검토필요 0건.

## 2026-07-09 (블로그 주제별 재작성 + 윤문체 검토 + CPTAC 공식 라벨 재조인)

- **SESSION_LOG 7/2~7/5 공백 채움 + 전체 역시간순 재정렬**(라벨 명확화: 7/1 새벽/낮/저녁 등).
- **개발 블로그 BIOP01 방식으로 전면 재구성·재작성 (9편 → 주제별 6편).**
  - BIOP01 재사용 셋업 확인(프로젝트 무관 `beginner-natural-writing.md`·캐노니컬 `build_index.py`·STYLE_CONTRACT §5) → BIOP02 스캐폴딩 신규 3종 작성(`blog/GLOSSARY.md`·`STYLE_CONTRACT.md`·`CONTENT_MAP.md`) + `sync_blog_to_workspace.sh` 심링크 파리티. 원본 9편 `blog/archive_2026-07-09_pre-reorg/` 백업.
  - 파이프라인(에이전트 18개): 앵커 1편 직접 작성 → manuscript-writer ×5(Pass1) → content-fidelity-auditor ×6(보존 게이트, 전편 PASS) → korean-style-rewriter ×6(윤문) → naturalness-reviewer 스윕(6편 발행가능, S1 0).
  - **advisor 함정 처리:** EXAONE 완료 커밋 `f7b008a`(스테일·66/1010 깨짐)→`69fe4ce`(7/8) 정정, phantom `20260703_cptac_labels/DECISION` 경로·미확인 "종양 120/122" 삭제(395/653만·근거를 실존 critic_report.json으로), 작업자 귀속 유지(I/O=kkkim·OpenClaw=braveji·모델링=sjpark), hedge 6종 전부 생존. 통합본 재생성(6편).
  - **편별 윤문체 검토(개별 리뷰어 6):** 1편 91 / 2편 90 / 3편 90 / 4편 89 / 5편 83(경미 2차 윤문 권고: 격언조 단문+HER2 동형 중복) / 6편 진행 중.
- **git fetch + JIRA 점검:** 원격 신규 = **jamie `feat/BIOP02-55-jamie-cptac-labels`(PR #24, 검토 중)** — 공식 CPTAC 라벨(kkkim 임시본 대체). 로컬 main = origin/main 최신. kkkim 열린 이슈 2건(BIOP02-73 S7 Methods·-78 S8 저널, 급하지 않음).
- **#1 PR #24 머지 조율:** kkkim(Leader) 코멘트 게시 + `@braveji18` 리뷰 요청(독립 교차검증 동일 확인). comment id 4923595106.
- **#2 CPTAC 임베딩-라벨 재조인(스테이징):** `experiments/kkkim/20260709_cptac_official_join/`. 653/653 case 매칭, has_labels 395/653(임시본과 동일), **task별 has_er 387·has_pr 375·has_her2 294·has_pam50 382**. 임시본 대비 40슬라이드 값 변경(HER2 30·PAM50 13; equivocal 보존 차이). **HER2 외부검증(caution) 재실행은 has_her2=1(294)만 대상**이어야 함. 공유 파일 미덮어씀(PR 머지 후 승격).

- **BIOP02 89개 티켓 전수 조회** (JIRA REST `/search/jql`; 구 `/search`는 410 Gone, MCP `search_jira_issues`는 "map" 버그 → urllib 우회). 티켓×담당×데드라인×의존 사슬 정리, 병목 표 작성.
- **병목 판단 2회 교정:** ① braveji 사유 반영(대부분 상류 대기·Owner≠Reviewer·외부실물) → ② **`git fetch` 결과 로컬 main이 73커밋 뒤처져 있었음 발견**, 이전 판단("-53이 전부 블록"·"MLP Δ+0.005") 폐기. 로컬 main be27eeb로 ff.
  - 실제(main): sjpark 모델링 라인 사실상 완료(CLAM-SB/MB·baseline 보강·counterfactual·2차 self-critic·Fig 3 -64). braveji v2/CLAM critic 4종(caution, 미머지). jhans -52v2 진행중.
  - 진짜 이슈=과학적 결과: ER/PR/HER2는 subtype-only가 형태학 모델과 대등/우위, PAM50만 CLAM-MB 이득.
- **미푸시/미커밋 정리:** EXAONE 550M 가중치 `.gitignore`(commit c215ee3, push). "유실"로 본 비교 스크립트는 feat/BIOP02-63에 실재 → 복원.
- **EXAONE Path 2.0 3-way(4열) 비교 완료** (commit 69fe4ce, push): 추출 1010/1010·768d·누락0. build_exaone_features.py로 patch_mean·slide_global 조립 → compare_models.py 4열 비교(`experiments/kkkim/20260708_3way/`).
  - 결과: EXAONE_slide_global ER 0.923/PR 0.845/HER2 0.697로 UNI/CONCH CI 비중첩 상회, PAM50만 UNI 0.736. **단 patch_mean(동일 mean-pool)은 UNI와 대등** → 이득은 EXAONE 자체 slide집계+내부tiling(Macenko@0.5mpp) 혼재. claim=sanity.
  - ⭐ ER 0.923 ≈ subtype-only 0.918 → sjpark에 CLAM+EXAONE 실험 제안.
- **JIRA BIOP02-48 코멘트 등록** (id 10967, @sjpark 공유: EXAONE→CLAM으로 subtype-only 벽 넘을 여지).

---

## 2026-07-05 (UMAP PR 머지 + 개발 블로그 9편 + paper-production 하네스)

- **feat/BIOP02-63-kkkim-embed-umap PR #15 머지** (origin/main 통합, commit 9e58c9e·c1a56fe) — Embedding UMAP(UNI 1010, site-confound 확인) 라인 병합.
- **개발 블로그 9편 + 통합본 등록** (BIOP02-38/-85, commit 7dd5552, `blog/`): 01 cohort·tiling / 02 UNI·CONCH 임베딩 / 02_2 임베딩 I/O 가속 심화편 / 03 EXAONE Path2 / 04 CPTAC 외부검증 / 05 UMAP site-confound / 06 모델링·Critic / 07 인프라·협업·PR15 / 08 OpenClaw JIRA-Slack 자동화 런북 + 통합본 `00_BIOP02_blog_all.md`.
- **paper-production 하네스 설치** (팀 공유, commit 8eb34a9): 논문 집필·발표 단계용 재사용 스캐폴드, 도메인 분석 슬롯 = `spatialpatho-analyst`. 분석 파이프라인 위에 얹는 집필 레이어(대체 아님).
- (미완, 저순위) 블로그 08·02_2 + 통합본 Drive 업로드는 GDrive MCP 세션 드롭으로 보류 — 폴더 `1Nd8G_VjYf1XQL67qpcDTQICscQbT-_6v`.

---

## 2026-07-04 (PseudoCon 2026 발표 신청 — 마감일)

- **PseudoCon 2026 발표 신청 완료 → 선정됨** (마감 07-04 충족, 발표 확정).

---

## 2026-07-03 (EXAONE 1010 전량 + BIOP02-38 머지 + sjpark CLAM 교차리뷰)

- **BIOP02-48 #done — EXAONE Path 2.0 1010 전량 추출 + 4-model 비교** (commit f7b008a). 초고배율 3장은 mem-bounded loader로 해결. *(주의: 7/8 무결성 재검증에서 이 산출물이 tmp 오명칭·66/1010로 깨져 있던 것이 발견되어 재추출·재비교됨 → 위 2026-07-08 항목 참조.)*
- **BIOP02-38 TCGA embed 브랜치 PR #14 머지** (commit a8435fd).
- **BIOP02-53 CPTAC IHC/PAM50 라벨 임시 확보** (공개 cBioPortal `brca_cptac_2020`, commit 039b93a) — external validation 임시 언블록.
- **Critic 교차리뷰 (kkkim→sjpark) — sjpark CLAM MIL: `caution`** (commit 3f45ffd, JIRA BIOP02-53 #comment). Owner≠Reviewer 규칙 적용(kkkim이 sjpark 모델링 결과 담당). caution 근거 = subtype-only baseline이 형태학 모델과 대등/우위 우려.

---

## 2026-07-02 (EXAONE 재처리 모드 + 팀 공유 데이터 경로 규칙)

- **AGENTS.md §2 팀 공유 데이터 경로 규칙 명문화** (commit 26edfc1, de62e6b): 팀원=별도 컨테이너 → 홈 경로 심링크 공유 금지, 임베딩/manifest는 `/workspace` 실파일로. memory `infra-workspace-shared-data`와 정합.
- **extract_exaone.py `--slides-file` explicit-list 모드 추가** (commit 4d436e2): 누락 슬라이드만 인덱스 시프트 없이 재처리 — 3-GPU 샤딩 재개 안정화용.
- 팀 라인 진척 관찰(kkkim 직접 아님): sjpark UNI v1 실험 아티팩트(-39/-40/-46) 등록, PR #12/#13/#19/#20 머지(서버 현행화 A6000×3·bastion, SSH 포트 정정, NAS 인벤토리 복구).

---

## 2026-07-01 (낮 — BIOP02-48 UNI vs CONCH 비교 + EXAONE 셋업·추출 착수)

- 세션 인수인계 파일(HANDOFF/TODO/SESSION_LOG)을 프로젝트 폴더에서도 주기 갱신하도록 결정 — git에는 제외(.gitignore 추가), SESSION_LOG는 로컬 지속 저장. `~/.claude/` 정본→프로젝트 폴더 복사, check-ignore 검증
- BIOP02-48 UNI vs CONCH 비교 커밋(f5651e1) + JIRA 완료 처리 — 전 phenotype UNI 근소 우위, site-confound은 CONCH 낮음
- EXAONE Path 2.0 임베딩 셋업: gated=False 해소 확인, 가중치 다운로드, cucim/rpack/opencv 설치
- EXAONE 블로커 해결: (1) from_pretrained→수동 load_state_dict(pytorch_model.bin), (2) /tmp noexec→triton 캐시 홈 경로 우회
- extract_exaone.py 전면 재작성(AutoModel 스텁 폐기→슬라이드 단위 EXAONEPathV20, act3 slide_global 768d) + run_tcga_exaone.sh 3-GPU 러너
- EXAONE 3-GPU 추출 착수(bg bbck2u9u4, 337/337/336 샤딩, ETA ~8h), 첫 산출물 검증 완료
- memory 업데이트: exaone_path2_interface (블로커 해소 반영)

---

## 2026-07-01 (새벽 — CONCH 완료 확인)

- **CONCH 임베딩 1010/1010 완료** (다른 창 세션이 밤사이 완주, 05:27). 무결성 검증: 손상 0, 전부 512-dim, 누락 0
- 다른 창에서 CONCH 설정을 여러 번 튜닝(단일→2샤드 cuda0+1→gpu0 solo)하며 재시작 — 전부 정상 done 후 수동 재기동(실패 0건). 충돌 점검 결과 샤드 disjoint로 동시쓰기 없음, cuda:1 경합도 gpu0-solo 전환으로 해소
- GPU 온도 모니터링 운영: 전 구간 peak 91~92°C(throttle 미도달), 안전. 죽음 알림은 노이즈라 온도 전용 워처로 전환
- **CPTAC 643/653** (이 세션, cuda:2) — 곧 완료, 마감 7/1 충족
- 다음: UNI vs CONCH 비교(BIOP02-48 마무리), CPTAC 653 완료 확인
- **CPTAC 653/653 완료** (06:29, 마감 7/1 충족): 손상 0·전부 1024-dim·누락 0. status tile_failed 10건은 전부 재시도 성공(진짜 누락 0). 매니페스트 653장 전량 커버

---

## 2026-06-30 (오후 — 진행상황 점검 세션)

### BioProject02
- **UNI 임베딩 (TCGA-BRCA) 1010/1010 완료 확인** — extract_uni 프로세스 모두 종료, `~/data/embeddings/biop02/tcga/uni_v1/`
- **sjpark에 UNI 임베딩 경로 노티 완료** → MLP 시작 가능
- **CPTAC 임베딩 143/653 진행 중** (PID 234505, cuda:2, stream_status.csv)
- **HF 새 토큰 수령** — 블로커 해소, `huggingface-cli login` 후 CONCH 다운로드만 남음

### 상태 파일
- 전역 HANDOFF/TODO/SESSION_LOG 갱신 (UNI 완료, sjpark 노티, HF 토큰 반영)

### 다음 행동
- `huggingface-cli login` → CONCH 다운로드 (BIOP02-48)
- BIOP02-63 UMAP 생성 (지금 가능)
- CPTAC 완주 모니터링 (마감 7/1)
- PseudoCon 2026 신청 (마감 7/4)

---

## 2026-06-30 (세션 — 컨텍스트 복구 + UNI 임베딩 실행)

### 작업 내용
1. **컨텍스트 복구** — 서버 재접속 후 이전 세션 내용 파악 (GitHub main 61 commits 싱크, manifest 재생성, UNI 로컬 로딩 등)
2. **UNI 임베딩 실행 중** — 3-GPU 병렬 (PIDs 143567/143793/143854), 19/1010 완료, ETA 오늘 저녁
3. **7/4 이전 플랜 수립** — UNI→CONCH→EXAONE 임베딩 순서, CPTAC 시작, PseudoCon 신청 일정
4. **상태 저장** — HANDOFF/TODO 업데이트

### 현재 블로커
- HF 토큰 만료 (CONCH 다운로드 불가) — 사용자가 새 토큰 제공 예정
- UNI 임베딩 완료 대기 중

### 다음 행동
- 새 HF 토큰 받으면 즉시 CONCH 다운로드 시작
- 오늘 저녁 UNI 완료 확인 후 sjpark 노티
- CPTAC 시작 (BIOP02-54, 마감 7/1)

---

## 2026-06-04

- 타일링 1010/1010 완료 (run_tiling_1010.py, CPU 우회, 예상보다 빠른 완료)
- mcp-atlassian 2.1.0 issueKey regex 버그 발견 및 패치 (BIOP02처럼 숫자 포함 프로젝트 키 지원)
- Critic 재리뷰 완료: BIOP02-39, 40 conditional_pass, commit_hash 직접 수정
- JIRA 정리: BIOP02-21/41/83 Ka-Kyung Kim 재할당, BIOP02-21/37/38/41/83/84 완료 처리
- manifest/split_policy 공용 경로 복사: `/workspace/data/cache/biop02/`
- BIOP02-41: sjpark 전수 필요 분석(소수 클래스 근거) 댓글 기록
- CLAUDE.md/update-jira.md/progress.md 규칙 추가 (한다고 하고 안 하기 금지, 중간 보고, @mention)
- memory 업데이트: tiling 1010장 범위, MCP bug 패치, JIRA 댓글 범위, JIRA @mention 규칙

---

## 2026-06-03 (오후 — 문서화 + jamie 대행 + Novelty 분석)

### MCP 인프라
- `~/.claude.json` MCP 설정 근본 원인 발견 및 수정: `@xuandev/atlassian-mcp` → `mcp-atlassian`
- JIRA MCP 구버전 컨텍스트 고착 문제 분석: 대화 세션 중 MCP 변경 불가, 새 세션 필요
- curl 직접 호출로 JIRA API 우회 (인증 HTTP 200 확인)

### 문서화
- `agents/embedding/README.md` 작성 (Quick Start, 스크립트 설명, 출력 경로)
- `agents/embedding/skills.md` 작성 (Sprint 0/1 작업 이력)
- `/status` 커맨드 스킬 생성 (`~/.claude/commands/status.md`)
- CLAUDE.local.md에 Agent 발행 규칙 추가 (Critic Agent 의존성 확인 의무화)

### jamie 대행 (Data Agent)
- NAS Synology FolderSharing API로 TCGA-BRCA DX1 1061개 파일 목록 조회
- TCGA CDR 임상 데이터 다운로드 및 파싱 (1097명, ER/PR/HER2/PAM50 컬럼 확인)
- 임상 기반 500장 manifest 생성: ER- 228 + HER2+/ER+ + ER+ 채우기
- split_policy_v0.csv 생성: patient-level 70/15/15, ER stratified, train 350/val 75/test 75
- WSI 다운로드 스크립트 구현 (download_wsi.py): openslide 유효성 검증 + resume 없이 처음부터

### 팀 관리
- braveji Slack 에스컬레이션 (리더 포지션, 팀 미진행 + 서버 인프라 문제)
- jamie BIOP02-83 코멘트 (공용 경로 이동 + manifest 공유 + 완료 확인 요청)
- sjpark 개인 카톡 (BIOP02-39, 40 착수 요청)
- 이건규 카톡 (GPU 서버 기한 + 저장소 + GPU 현황 확인 요청)
- GPU 20분 모니터링 루프 설정

### Novelty 분석
- deep-research 워크플로우 실행 (103 에이전트, 1.6M 토큰)
- 결론: DepMap/GDSC 직접 연결 선행 연구 없음, 목표 npj Precision Oncology (IF ~12)
- MAKO (npj Digital Medicine, 2026): UNI/CONCH 12종 벤치마크 — 단순 분자 표현형 예측은 novelty 아님

### 현재 진행 중
- WSI 다운로드: ~92/500 (PID 64501, /home/kkkim/data/tcga_brca_wsi/)
- 자동 타일링: PID 64228 대기 중
- GPU: 3개 100% 풀가동, 해제 시점 미확인

---

## 2026-06-03 (이전 세션 — Atlassian MCP 디버깅 + 상태파일 생성)

- Atlassian MCP 0개 반환 문제 반복 디버깅
  - 원인 1: `@xuandev/atlassian-mcp v1.1.1` — 구버전 API 엔드포인트 (`GET /rest/api/3/search`)
  - 원인 2: `mcp-atlassian@2.1.0`도 같은 구버전 엔드포인트 사용
  - 원인 3: `mcp-atlassian@2.1.0` 설치 시 `jsdom` dep 누락으로 크래시
  - 조치: `npm install -g mcp-atlassian@2.1.0 jsdom`, `~/.claude/mcp.json` env var 수정, handlers.js 패치
- `~/.claude/CLAUDE.md` 생성: 세션 시작 시 HANDOFF/TODO 읽기 + 기술 문제 해결 후 memory 저장 의무화
- `~/.claude/HANDOFF.md`, `TODO.md`, `SESSION_LOG.md`, `commands/progress.md` 생성
- memory `project_mcp_atlassian.md` 업데이트

## 2026-07-10 (팀 진행 스냅샷 + 병목 재파악 + CPTAC 승격/블로그 마감)

- **CPTAC 공식 라벨 승격**: PR #24(jamie -55) 머지 확인 → 공식 v1(653행, has_her2 294)을 공유 경로 `/workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv`로 cp(임시본 백업 보존). sjpark에 재실행 노티(JIRA -53 comment 10981).
- **블로그**: 05편 2차 윤문(격언조 종결·HER2 동형중복) 반영, 나머지 5편 STYLE_CONTRACT 클린. 공용 스페이스 저장 `/workspace/blog/BIOP02/`(Drive 대신, sync_blog_to_workspace.sh, BIOP01 패턴). git 커밋 `77c698c`(9→6편 재구성, 심링크 2개 gitignore) push.
- **팀 전수 대조(git main 50fc502 + JIRA)**: 오늘 sjpark·braveji가 외부검증 루프 종결 — sjpark 공식라벨 4태스크 외부재실행·Fig3/Fig4(-64/-68), braveji -50 #done·-53 총괄 Critic(외부 역전 발견)·-57 registry. jamie -55 완료·-49(HER2 QC) 착수. JIRA 상태가 git보다 크게 지연.
  - 외부검증(공식): ER 0.894(subtype_only 0.918과 p=0.613 동등)·PR 0.778(gap +0.001)·HER2 0.530 reject·PAM50 0.722. 일반화 잘 되나 subtype_only 상한 못 넘음, HER2 양쪽 random.
  - **병목=사람대기 아니라 형식게이트:** ① label-shuffle null(sjpark) ② split_policy_v0 lock 해시 기록(jamie) ③ HER2 reject Limitation 서술. ①②를 JIRA -53/-55에 노티.

## 2026-07-10 (Paper A 방향 재정립 + cost-of-substitution 실험 + 전 방향 전수 탐색)

**Paper A 재정립:** "H&E→분자표현형 예측+외부검증+multi-FM" 레드오션 스쿱 확정(Fernandez-Romero 2026 Med Biol Eng Comput = 우리 설계+HER2 실패 재현; Dawood 2024 = H&E→약물 전이). → **cost-of-substitution + Critic 거버넌스**로 재정립. 유일 방어 헤드라인 = "값싼 H&E가 어떤 치료결정엔 충분·어떤 결정엔 위험"의 정량 지도. (novelty-strategist·literature-scout 2에이전트 + 원문 검증; Fernandez-Romero abstract는 OpenAlex/Semantic Scholar API로 확보, 지표가 PR-AUC/F1이라 우리 AUROC와 직접비교 불가)

**실험 (experiments/kkkim/):**
- 세포주 게이트 GO: DepMap∩GDSC 유방 51라인, 축별 ER+15/HER2amp14/TNBC23 전부 ≥5(`20260710_cellline_counts/`). 항HER2는 GDSC2 Lapatinib/Afatinib/Sapitinib Z로 검증.
- 냉동 세포주→약물 지도(286약물) + 치료거리(antiHER2↔chemo 0.765 최대) + 환자 라우팅(PAM50 예비): **antiHER2 cost 0.718·mis-route 100%**(모델이 HER2 예측 못 함)·chemo 0.105·endocrine 0.378, **헤드라인 contrast 0.340 CI[0.276,0.402] 0배제**. 사전등록 약물패널(anchor antiHER2 3/3·chemo 7/7·endocrine 1/8) + **D1 흡수**(세포주 내분비 사각=ER+ 이중한계). 2패널 그림. receptor 라우팅 골격은 sjpark ER 예측 도착 시 자동실행(`20260710_cost_of_substitution/`).

**방향 전수 탐색(결과 = A가 유일 헤드라인):**
- B(pCR/IMPRESS): 파이프라인 실증 GO(126/126, ~3–4 GPU-h), 사이드 논문(`20260710_pcr_impress/`).
- C(공간 modality): NO-GO standalone(Path2Space Cell 2026-04 직격 스쿱, 공개 유방 IMC에 paired H&E 없음) → 검증 add-on DEFERRED(§7.1, Path2Space 코드 공개·비상업 라이선스 확인=conditional-go). B×C 접점(Path2Space∩IMPRESS) 기록(§7.2).
- D2(PRISM repurposing) 얇음·D3(CRISPR dependency) red ocean(2025 2건 스쿱)·endpoint 전환(HRD/PIK3CA/HER2-low 등) 스쿱 → 모두 A 못 이김.
- BIOP01↔02: 발표 서사만(생물학 Paper C = GSE240112 near-scoop·n=3·multiome 없음, 데이터-블록). BIOP01 진짜 결론 확인(chromatin-lag 반증/α robust) → BIOP01 폴더에 `BIOP02_LINK.md` 남김(미커밋).

**산출 문서:** `research/paperA-positioning/`(novelty-scoop·research-plan·subtype-decision-map·tierC-roadmap) + `research/program-narrative/biop01-02-static-dynamic` + `experiments/kkkim/EXPERIMENTS_INDEX_2026-07.md`.

**JIRA(ADF 기본 전환):** jhans -52 세포주 카운트(11004), sjpark -53 ER 예측 재생성(11006), BIOP02-78 Paper A 기록(11007), **BIOP02-90 신규 Subtask**(sjpark ER 예측, -53 하위). memory `feedback-jira-adf-default` 저장(api/3 ADF).

**발표(PseudoCon 2026):** 제출 블러브 다회 윤문 확정 — 제목 "단일세포부터 병리 이미지까지", 연결=치료효과(01 세포 변화 속도 / 02 아형 맞춤 처방 → 치료 효과에 다가섬, DRP·대시·클리셰 제거). 결과 폄하 X("실패처럼 보이던 결과에서 의미"), 운영 연결=에이전트 팀.

**배경:** BIOP01 profile-likelihood(`p3_profile_likelihood.py --subset 400`) 백그라운드 실행 중 — 타 세션, BIOP02 무관, 미개입.

**세션 마무리:** 게재료(APC) 조사 → `research/publication-cost-2026-07.md`(최저 eLife $2.5k / J.Pathol.Informatics $1.47k; 한국 KESLI/NST 협정은 대학·출연연만 → 싸이토젠 소속 미커버). BIOP02-90 Subtask 생성(sjpark ER 예측, -53 하위) + sjpark 카톡 문구. **발표 블러브 최종 확정**(제목 "단일세포부터 병리 이미지까지", 연결=치료효과 01 속도/02 아형처방 → 치료효과에 다가섬; DRP·em대시·클리셰·구어체 제거, 결과 폄하 X). **SESSION_LOG 프로젝트별 분리**(BIOP01 항목 제거, 전역 ~/.claude 동기화 중단, memory `feedback-session-log-project-scoped`). HANDOFF 즉시재개 갱신(다음 창 인수인계). 커밋 `ca38fd5`까지 push.
