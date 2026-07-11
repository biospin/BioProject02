# Cross-cancer (Paper C) — 진행·결정·결과 로그

> 살아있는 문서. 주요 진행/결정/결과를 시간순으로 계속 append. follow-up·검증·활용용.
> 관련: 재개=`RESUME_CROSSCANCER.md` · JIRA 에픽 **BIOP02-93**(하위 94 임베딩/95 라벨·split/96 MIL·cost).

## 스코프·전제
- **사용자 (B) 지시(2026-07-11):** GPU 서버 sunset **8/15** 전 논문용으로 cross-cancer 전량 실행. 발표(일 18시 마감/21시 회의)엔 BRCA 결과 위주, cross-cancer는 후속.
- 리더 사인오프하 별도 트랙. A/B(BRCA)는 BRCA-only 유지. hypothesis_only·비-DRP.
- 대상: 폐 NSCLC(LUAD 541 + LUSC 512 = 1053장) → 대장(COAD 459 + READ 166 = 625장), UNI 임베딩.

## 결정 기록 (with 근거)
| # | 결정 | 근거 | 날짜 |
|---|---|---|---|
| D1 | **ALK 드롭** | 세포주 게이트 NO-GO(n=2)·fusion(MAF 아님)·frozen_map에 anti-ALK 축 없음 | 07-11 |
| D2 | **UNI만**(EXAONE/CONCH 스킵) | BRCA 헤드라인=UNI·EXAONE=coords 비호환 셋업 블로커·3배 GPU | 07-11 |
| D3 | 임베딩 raw=**SSD**, 워커당 **OMP=4**, **10워커** | HDD 18워커=thrash(load133)·무제한스레드=thrash(load73) 실측 → 스윗스팟 | 07-11 |
| D4 | 각 endpoint **{real, shuffle-null, prevalence-baseline}** | AUROC≈0.5가 'H&E-blind(가설확증)'인지 'MIL고장'인지 shuffle로 구분(advisor) | 07-11 |
| D5 | **histology(LUAD/LUSC)=양성대조** (≥0.75 게이트) | H&E가 형태 보는지 확인 → 파이프라인 정상성 검증. 실패 시 전체 의심 | 07-11 |
| D6 | 평가=**val+test hold-out 합침**(site-disjoint 유지) | 변이 endpoint test 양성 7-9명 얇음 → CI 넓음. 합쳐 ~15-17명 검정력↑. **사용자 결정** | 07-11 |
| D7 | **EGFR 라벨 보정**(S768I·exon20 dup·E709 추가, T790M·passenger 제외) | strict 9.4%가 놓친 진짜 activating 포섭 → 10.2%(문헌 11-13% 정합). anchor-chasing 아님. **사용자 질의 후** | 07-11 |
| D8 | 폐 cost **버전 A(targeted 3축) + 버전 B(histology 포함 mis-route) 둘 다 산출**, 프레이밍 보류 | LUAD/LUSC가 chemo 레짐 바꿔 치료축 될 수 있음 vs BRCA 평행 단순성. **사용자 결정(보류)** | 07-11 |

## 진행 상황
- 07-11 ~11:40 임베딩 자율 착수(스모크 PASS 후 detached). 튜닝 수렴(D3).
- 07-11 12:xx 라벨·split·MIL 스크립트 작성+검증, supervised 자동 체인 detached(임베딩 완료 감지).
- **임베딩 진척:** 07-11 12:56 = 폐 235/1053 · 대장 168/625. ETA 오늘밤~일 새벽.

## 검증된 사전결과 (임베딩 완료 전, 부분/GPU-free)
- **세포주 냉동지도·치료거리(완료):** 폐 antiKRAS-G12C↔chemo **0.914**·antiEGFR↔chemo 0.667 / 대장 antiBRAF↔baseline **0.868** (BRCA HER2↔chemo 0.765 재현). positive control 통과.
- **라벨 prevalence(게이트 통과):** EGFR-activating 10.2%·KRAS-G12C 12.4%·BRAF-V600E 9.0% (문헌 앵커 내). histology LUSC 484명.
- **split(site-disjoint 검증):** 폐 1050환자/69site(hash 9100041e)·대장 534/37site. patient/site-overlap 0.
- **MIL 스모크(양성대조, 부분 215장):** histology real AUROC **0.954** [0.90,0.99] vs shuffle-null **0.473** → 파이프라인 정상, H&E 형태 인식 확인.
- endpoint별 hold-out 양성수: histology 176(train308) / EGFR ~17 / KRAS ~15 / BRAF ~15 (val+test 합).

## 대기 중 (임베딩 완료 후 자동 산출 → **사람 검토 필요**)
- 폐/대장 `mil_cost_results.json`: endpoint별 real vs shuffle-null AUROC + cost 버전A/B.
- **가설:** 표적변이(EGFR/KRAS/BRAF) real≈shuffle(H&E-blind) vs histology real≫shuffle(H&E-triage) → BRCA "HER2 blind/basal triage" 패턴의 cross-cancer 재현.
- 검토 포인트: 양성대조 통과? 변이 CI? cost 프레이밍(A vs B)? EGFR 10.2% caveat.
