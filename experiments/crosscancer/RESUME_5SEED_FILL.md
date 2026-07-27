# RESUME — 다중 FM 5-seed 우연배제 fill + 자동 크로스체크 (2026-07-23 시작)

> **단일 원천.** 어느 세션이든 이 파일 + 산출 JSON 존재 여부로 상태를 판단한다.
> scratchpad 경로는 세션마다 다르므로 **완료 판정은 산출 JSON으로** 한다(마커에 의존 금지).

## 목적
`MULTIFM_COMPARISON.md`가 스스로 남긴 남은 일 — 신형 FM(virchow2·uni2h)에도 UNI과 동일한 **5-seed 우연배제**(`real_auroc > null_mean + 2·null_sd`, ddof=1) — 중 빠진 4칸을 채운다.

빠진 이유:
1. `sh_robustness_5seed.py`의 `ENDPOINTS`에 **COLORECTAL이 없어**(argparse choices에서 거부) 07-22 실행이 rc=2 실패.
2. **폐 임베딩**이 5seed 실행(07-22 03:42)보다 늦게(07-23 08:25) 끝나 대상에서 빠짐.

수정: 스크립트에 `COLORECTAL: ["braf_v600e"]` 추가. run_mil_cost `CANCER_CFG["COLORECTAL"]["endpoints"]`와 일치. 스모크(real-only) = **0.8676**로 MULTIFM_COMPARISON UNI 정본값 재현 확인.

## 채워야 할 4칸 → 완료 판정 파일
```
COLORECTAL/full/shuffle_null_robustness_virchow2.json    # braf_v600e
COLORECTAL/full/shuffle_null_robustness_uni2h.json       # braf_v600e
LUNG_NSCLC/full/shuffle_null_robustness_virchow2.json    # histology_lusc, egfr_activating, kras_g12c
LUNG_NSCLC/full/shuffle_null_robustness_uni2h.json       # (동일 3 endpoint)
```
(위·두경부는 이미 존재. GASTRIC/HEADNECK `shuffle_null_robustness_{virchow2,uni2h}.json` 있음.)

## 실행 방법 (재개 시 이대로)
GPU 여유 확인 후, 빠진 칸만:
```bash
cd experiments/crosscancer
PY=/opt/envs/spatialpatho/bin/python
$PY sh_robustness_5seed.py --cancer COLORECTAL --fm virchow2 --device cuda:0
$PY sh_robustness_5seed.py --cancer COLORECTAL --fm uni2h    --device cuda:1
$PY sh_robustness_5seed.py --cancer LUNG_NSCLC --fm virchow2 --device cuda:2
$PY sh_robustness_5seed.py --cancer LUNG_NSCLC --fm uni2h    --device cuda:0   # 대장 v2 끝난 뒤
```
각 run: real(seed42) + null 5seed[42,1,2,3,4]. 산출은 기본 경로(`<cancer>/full/shuffle_null_robustness_<fm>.json`).
대장 1 endpoint ≈ 15분, 폐 3 endpoint ≈ 40분/FM.

## 자동 크로스체크 (사용자 지시 2026-07-23 — 4칸 완료되면 자동 진행)
1. **결정론 재계산 대조** — 저장된 real AUROC가 재실행값과 일치(seed42, 코드경로 불변이라 일치해야 함).
2. **결정지도 순서 보존** — 논지는 절대값이 아니라 **순서**: 각 FM에서 endpoint를 real−null 마진(또는 real AUROC)으로 정렬했을 때 UNI 결정지도의 순서(강신호=histology/hpv/braf/msi > 약신호=lauren/erbb2 …)가 유지되는지. Spearman으로 UNI 순위 vs virchow2/uni2h 순위 대조.
3. **MULTIFM_COMPARISON.md 갱신** — 대장 BRAF 3-FM 표에 5-seed 마진 채움(특히 UNI2-h 얇은 마진 0.292가 5seed로도 유지되는지). 과대주장 차단 문구 유지("FM 우열 주장 금지"·"1암종 1endpoint로 법칙 일반화 금지").
4. **사람 사인오프 요청** — Owner≠Reviewer라 kkkim이 최종 판정 못 함. **JIRA BIOP02-101**에 sjpark/braveji 멘션으로 크로스체크 요청(결정론·순서보존 결과 첨부).
5. **커밋** — 스크립트 COLORECTAL 패치 + 4칸 JSON + 갱신된 MULTIFM_COMPARISON + 이 RESUME. BIOP02-101.

## 과대주장 가드 (봉인)
- braf_v600e는 **n_pos=15 < 사전등록 25 → exploratory**. 5seed PASS해도 "확증"이 아니라 "방향 근거".
- 5-seed는 **모델 비의존성의 근거**지 "법칙 성립" 근거가 아니다(1암종·소수 endpoint).
- 최종 claim_level=hypothesis_only, critic_status=pending 유지. 본문 승격은 Critic pass 후.
