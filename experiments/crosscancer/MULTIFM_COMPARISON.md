# 다중 FM 재학습 비교 — 대장(첫 결과) · 모델 비의존성 검정

> 목적: 치환가능성 결정지도가 **특정 파운데이션 모델(UNI)의 산물이 아닌지** 검정. 각 FM 임베딩 공간에서 CLAM을 **재학습**해야 성립하는 주장이라(HANDOFF §1 "주장 한계"), 임베딩만으로는 말할 수 없다.
> claim_level: **hypothesis_only** · critic_status: **pending** · 2026-07-20. 산출 = `COLORECTAL/full/mil_cost_results_{virchow2,uni2h}.json`(재학습 러너 `multifm_retrain_watcher.py` 자동 실행, 07-20 01:36/01:39).
> **Owner=kkkim(대행) → Reviewer=sjpark/braveji 크로스체크 필요**(Owner≠Reviewer).

## 비교 조건 (apples-to-apples 확인)
동일 endpoint(braf_v600e)·동일 site-disjoint 프로토콜·n_pos=15. 단 임베딩 커버리지가 FM별로 미세하게 달라(UNI 523장/holdout 151, 신형 526장/holdout 152) 홀드아웃이 1명 차이난다.

### ⚠️ 2026-07-23 정정 — 5-seed 재현값이 정본, 아래 mil_cost 단일값은 stale
신형 FM의 mil_cost 단일 real(virchow2 0.9328·uni2h 0.9377)은 **재학습 시점의 구 커버리지(holdout 151)** 산물이다. 임베딩이 526장으로 는 뒤 5-seed로 재현하면 **virchow2 0.8798·uni2h 0.8978**(holdout 152, 결정론 재현 2회 일치)이며 이것이 현재 정본이다. UNI(523장)는 불변. 상세·크로스체크 = `CROSSCHECK_5SEED_MULTIFM.md`.

| FM | 차원 | real(5-seed seed42, 정본) | shuffle-null 5-seed mean | thr(mean+2sd) | 5-seed 판정 | (구 mil_cost 단일, stale) |
|---|---|---|---|---|---|---|
| UNI v1 (정본) | 1024 | 0.8676 | ~0.53 | — (기존 통과) | ✅ | 0.8676 |
| Virchow2 | 2560 | **0.8798** | 0.602 | 0.8688 | ✅ PASS(마진 0.011) | 0.9328 |
| UNI2-h | 1536 | **0.8978** | 0.608 | 0.9272 | ❌ **FAIL** | 0.9377 |

## 읽는 법 (과대주장 차단)

1. **대장 braf = 부분적 모델 비의존성(2/3 FM).** 5-seed 우연배제에서 UNI·Virchow2는 PASS이나 **UNI2-h는 FAIL**(real 0.8978 < thr 0.9272). §4에서 예고한 "얇은 마진"이 실제로 우연배제를 통과 못 했다. → "대장 BRAF가 모델 비의존적으로 확인됐다"는 서술 **금지**. "3 FM 중 2개에서 우연배제, uni2h는 소표본(n_pos=15) null 소음으로 미확보"로 정직하게 쓴다.
2. **FM 우열은 주장할 수 없다.** 세 real이 0.868~0.898로 근접하고 CI가 겹친다. "신형 FM이 더 낫다"는 서술 금지(구 stale 값 0.93대가 우열 인상을 줬으나 정정됨).
3. **exploratory(n_pos=15 < 사전등록 25).** 5-seed PASS도 확증이 아니라 방향 근거. 대칭 규칙상 확증·반증 어느 쪽도 못 한다.
4. **폐는 대조적으로 강함.** 폐 3 endpoint(histology/egfr/kras)는 virchow2·uni2h **6/6 PASS**이고 결정지도 순서가 세 FM에서 **Spearman 1.000**으로 보존된다(`CROSSCHECK_5SEED_MULTIFM.md`). 모델 비의존성 근거는 대장 단일 칸이 아니라 **폐 다축 순서보존**이 진짜 무게중심이다.
5. **범위 한계.** 대장은 braf 한 endpoint(MSI·anti-EGFR 미재학습), 위·두경부는 기존 5-seed만. "법칙이 모델 비의존적"이라는 일반 주장은 폐 순서보존을 근거로 조심스럽게, 대장 uni2h FAIL을 함께 보고하며 한다.

## 현재 말할 수 있는 것 / 없는 것
- ✅ 말할 수 있음: "폐 결정지도 순서(조직형>EGFR>KRAS)는 UNI·Virchow2·UNI2-h에서 Spearman 1.000으로 보존됐다(6/6 5-seed PASS, 전부 exploratory)."
- ✅ 말할 수 있음: "대장 BRAF는 UNI·Virchow2에서 5-seed 우연배제를 통과했으나 UNI2-h에서는 미통과."
- ❌ 말할 수 없음: "법칙이 모델 비의존적이다"(대장·폐 소수 축) · "신형 FM이 더 낫다"(근접·CI 겹침) · "대장 BRAF가 모델 비의존적으로 확인됐다"(uni2h FAIL) · "확증됐다"(n_pos<25).

## 남은 일
- [x] 신형 FM 5-seed 우연배제 — 대장·폐 완료(2026-07-23). 결과 = 위 표 + `CROSSCHECK_5SEED_MULTIFM.md`. 위·두경부는 07-19/20 완료분 존재.
- [ ] **사람 Owner≠Reviewer 사인오프**(sjpark/braveji, BIOP02-101) — 특히 대장 uni2h FAIL 재현·서술 수위 동의.
- [ ] (선택) 대장 나머지 endpoint(MSI·anti-EGFR) 재학습 — 대장을 단일 칸에서 다축으로 올려 순서보존 검정 가능하게.
- [ ] **sjpark/braveji 크로스체크**: ① 결정론 재계산이 저장값과 일치하는지 ② UNI 결정지도의 **순서**가 다른 FM에서도 유지되는지(절대값이 아니라 순서가 논지).
