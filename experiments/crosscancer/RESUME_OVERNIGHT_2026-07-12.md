# 밤샘 자율 실행 — 재개 프로토콜 (2026-07-12 밤)

> 세션이 끊겨도 내일 이 문서 + `PROGRESS_DECISIONS.md` + `../../research/paperC-positioning/PAPER_DIRECTION.md`를 읽고 이어서 진행. detached OS 프로세스는 세션과 무관하게 계속 돈다.

## 지금 돌고 있는 것 (detached, 세션 무관 지속)
| 작업 | 프로세스 | 진행 | 완료 산출물(자동 생성) |
|---|---|---|---|
| 폐 임베딩 | 마스터 74878 + 워커 | 868/1050 | `LUNG_NSCLC/full/embeddings/*.npy`, manifest |
| 폐 supervised chain | (임베딩 완료 감지 대기) | — | 폐 `mil_cost_results.json` + 법칙 held-out(EGFR/KRAS/TRU/histology) |
| 위(STAD) 임베딩 | `sh_embed.py` 156432 (+3워커 GPU0/1/2) | STAD ~166/442 | `GASTRIC_STAD/full/embeddings/*.npy` |
| 두경부(HNSC) 임베딩 **병렬** | `sh_embed_hnsc_gpu2.py` (워커 3개, physGPU2 고정) | HNSC 0→진행 | `HEADNECK_HNSC/full/embeddings/*.npy` · 로그 `EMBED_HNSC_GPU2_HEARTBEAT.log` |
| ↳ 주의 | 병목=GDC 다운로드라 GPU2에 HNSC 병렬 추가(동시 실행). 마스터 sh_embed(순차)가 STAD 후 HNSC를 다시 돌려도 idempotent skip이라 충돌 없음. 라벨 20/21/22로 마스터 0/1/2와 비충돌 | | |
| 위·두경부 chain | `sh_chain.py` 158576 (임베딩 대기) | — | 각 `full/mil_cost_results.json` + `full/LAW_TEST.md` + `SH_CHAIN_DONE.json` |
| watcher | 147012 | — | `RESULTS_SUMMARY.md` 자동 |

## 내일 재개 시 할 일 (순서)
1. **완료 확인**: `SH_CHAIN_DONE.json`, 각 `LAW_TEST.md`, 폐 `mil_cost_results.json` 존재 확인. 임베딩 카운트 확인.
2. **법칙 held-out 검정 harvest**: 각 `LAW_TEST.md`(사전예측 vs 실측, 자동 verdict) 읽고 **PROGRESS_DECISIONS에 결과+의미 기록**. 핵심 관전 포인트:
   - **위 HER2-amp**: 유방 HER2(0.599)와 **부합(consistent)**인가? exploratory(n_pos~17)라 "복제(replicate)"는 주장 금지 — LAW_TEST가 자동 INCONCLUSIVE 처리.
   - **폐 EGFR 등급적(0.75-0.89) > KRAS(≤0.65)** 순서 성립? **두경부 HPV(≥0.80) > EGFR** 성립?
   - 반증(필수 마커가 잘 예측되거나 대체가능 축이 blind)이면 정직하게 법칙 실패 보고(사후 구제 금지).
3. **정직한 수치 검증(게이트)**: 커밋/공유 전 headline AUROC 재계산해 summary와 대조.
4. **미해결 TODO**:
   - ⚠️ `COLORECTAL/full/routing_cost.json`의 msi/anti_egfr **mean_cost가 아직 null** — `clinical_routing_distance_preregistered.json` 적용됐는지 확인, 안 됐으면 적용.
   - 폐 subtype 라벨(`LUNG_NSCLC/full/subtype_labels.csv`, authoritative 397명) → 폐 chain이 subtype arm(TRU 법칙검정) 포함하는지 확인.
   - Critic 7항목(braveji 총괄, owner≠reviewer)은 위 결과 안착 후.

## 오늘 밤 확정된 결론 (기록 완료)
- **메커니즘 경로 확정**: 대장 공간-ST 그림 **폐기**(Visium=해상도 null, Su IMC=축 틀림). MSI 판별축은 공간 기하 아니라 **TIL 밀도** → 우리 H&E 모델의 **해석가능 형태특징**으로 시연(방법 스카우트 #2). 유방 ERBB2 floor(공간)는 유지. 상세=PROGRESS "밤샘 harvest".
- **anti-EGFR bag-size 교란** 확인(ρ=−0.26~−0.33) → all-RAS 형태 상관물 부재 강화. 원고 명시.
- shuffle-null 5-seed 안정 = 누수 없음.
- 용어: "형태학적 상관물"(표준), "침묵/조용/silent" 폐기(→ `PAPER_DIRECTION.md` §용어).

## SOTA 다중 FM 견고성 (2026-07-12 추가) — 최대 IF 레버
- **[사용자 액션] HF 게이팅 신청**: `paige-ai/Virchow2`(1순위)·`MahmoodLab/UNI2-h`(2순위)·(선택)`prov-gigapath/prov-gigapath`. 기관 이메일(@gmail 불가).
- 목적: HER2/RAS 상관물 부재가 프런티어 FM 전반에서 성립 → 법칙 모델 비의존(약한 인코더 반박 차단).
- 로컬 가용=UNI·CONCH뿐(Virchow2 등 미다운로드). CONCH는 UNI보다 약해 interim만.
- 구현: coords 영구저장 → 재다운로드+재추출(재타일 불필요). **폐 임베딩 완료 후** 핵심 마커(HER2·MSI·RAS) 서브셋만. 계획=`../../research/paperC-positioning/FLAGSHIP_PLAN.md` §SOTA.

## 대기 중 사람 결정 (다음 세션에 물을 것)
- 대장 ST를 mechanism 그림에서 빼고 TIL-특징 경로로 가는 것 최종 확인(밤샘 결과가 이를 강하게 지지).
- AI 결정 레이어(치환가능성 스코어 + 보정/기권) 착수 시점(결과 안착 후).
