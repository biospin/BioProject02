# Critic #2 — Phenotype baseline 비교 **최종표 + 결론 lock** (BIOP02-69)

**작성:** braveji (Critic 총괄) · 2026-07-15 · main `102bf33` 기준
**완료조건 충족:** 엔드포인트별 baseline 대비 우열 최종표 + 결론 문장 lock.

**이번에 메운 공백:** `run_baselines.py`는 mean_embed proba를 계산하지만 **요약만 저장**해 per-patient proba가 없었고, 그래서 CLAM vs mean_embed paired 검정이 불가능했다(BIOP02-50 recompute 잔여, "sjpark 대기"). braveji가 GPU 머신 `/workspace` 임베딩에서 **mean_embed proba를 재생성해 내부·외부 paired 검정을 직접 산출**했다. baseline 정의는 sjpark 소유 `MeanEmbedBaseline`을 그대로 재사용(재발명 금지), 정렬 무결성 가드(predictions.npy label == manifest label) 4/4 통과, `auc_clam` 전부 기존 기록과 일치.

---

## 최종표

| endpoint | CLAM int / ext | vs **mean_embed** (int) | vs **mean_embed** (ext) | vs **subtype_only** (ext) | 판정 |
|---|---|---|---|---|---|
| **ER** | 0.9013 / 0.894 | **+0.0839** CI[0.018, 0.1495] p=.014 ✅ | **+0.1283** CI[0.0885, 0.1707] p≈0 ✅ | −0.067 CI[−0.0935, −0.0419] p≈0 ❌ **역전** | SIGNAL, NOT ADDITIVE |
| **PR** | 0.7765 / 0.7776 | +0.0894 CI[−0.0011, 0.178] p=.054 ⚠️ 경계 | **+0.2230** CI[0.157, 0.2861] p≈0 ✅ | −0.1343 CI[−0.1785, −0.0923] p≈0 ❌ **역전** | SIGNAL, NOT ADDITIVE |
| **HER2** | 0.5992 / 0.5297 | +0.0491 CI[−0.0221, 0.1284] p=.186 ❌ | **−0.054** CI[−0.1721, 0.0638] p=.368 ❌ | −0.2603 CI[−0.3651, −0.1504] p≈0 ❌ **역전** | **REJECT** |
| **PAM50-4c** | 0.8053 / 0.8181 | **+0.0889** CI[0.0394, 0.14] p=.001 ✅ | **+0.165** CI[0.1218, 0.2064] p≈0 ✅ | N/A (정의상 순환) | **#2 PASS** |

- ✅ = CI가 0을 배제하고 CLAM 우세 / ❌ = 미달 또는 역전.
- subtype_only는 PAM50에 **적용 불가**(PAM50로 PAM50 예측 = 순환) → mean_embed가 유효 기준선.
- ER/PR/HER2 mean_embed = braveji 신규 산출(`paired_meanembed_*.json`). PAM50 = sjpark 산출(검증 인용).

---

## 결론 lock (본문 서술 시 이 문장을 벗어나지 않는다)

1. **PAM50 4-class가 Critic #2를 통과한 유일한 엔드포인트다.** 유효 기준선(mean_embed)을 내부(+0.089)·외부(+0.165) 모두 **CI 비중첩**으로 상회한다.

2. **ER·PR은 형태학 신호가 실재하나, 분자 아형 지식에 추가 정보를 주지 못한다 (SIGNAL, NOT ADDITIVE).**
   - 신호 실재: mean-pooling 대비 외부에서 **크게 유의**하게 우세(ER +0.128, PR +0.223, 둘 다 p≈0). 즉 attention MIL이 단순 평균풀링을 넘는 형태학 정보를 실제로 뽑는다.
   - 그러나 비가산: **subtype_only가 외부에서 유의하게 역전**(ER −0.067, PR −0.134, p≈0). 아형을 이미 아는 상황에서 H&E가 더 얹어주는 것이 없다.
   - ⚠️ "ER/PR은 baseline에 그냥 진다"는 서술은 **부정확** — mean_embed 축에서는 이긴다. 위 두 문장을 함께 써야 정확하다.

3. **HER2는 reject.** 외부 AUC 0.530(random 수준)이며 **mean_embed조차 이기지 못한다**(−0.054, ns). 어떤 기준선에서도 우위 없음.

4. **Limitation (필수 병기):** subtype_only 역전은 **CPTAC 외부에서만** 발생하고 내부에서는 동등하다(ER p=0.613). site_confound(UNI 사이트 판별 AUC 0.9977)를 감안할 때 **사이트/배치 아티팩트 기여 가능성**을 배제할 수 없다. 외부 역전을 "형태학 무용"의 근거로 과대해석하지 않는다.

---

## 산출물
- `paired_meanembed_{er,pr,her2}_{val,cptac_external}.json` — braveji 신규 6건.
- `run_meanembed_paired.py` — 재현 스크립트(sjpark `MeanEmbedBaseline` 재사용, 정렬 가드 포함).
- 인용: `experiments/sjpark/*_clam_uni_v2/paired_significance{,_external}.json`(subtype_only), `pam50_clam_mb_uni_v1_4class/paired_significance_{internal,external}.json`.

## 후속 (다른 담당)
- sjpark: `run_baselines.py`가 **mean_embed proba를 저장하도록 개선** 권장(이 공백의 근본 원인). 저장되면 Critic이 매번 재생성할 필요 없음.
- PAM50 pass 승격 잔여 = commit_hash 회귀·faithfulness 플래그(sjpark), #5 bio sub-check 배정(jhans) — BIOP02-56 참조.
