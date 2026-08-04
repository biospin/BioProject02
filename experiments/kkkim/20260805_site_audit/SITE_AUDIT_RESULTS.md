# BIOP02-121 MUST #2 — site/batch confounding 감사

> 기존 site-disjoint holdout 예측만 사용(재학습 없음). TSS=TCGA 바코드 2번째 필드.
> **판독 규칙**: within-site AUROC가 pooled와 비슷하면(작은 drop) site 교란 아님. eta²(참-음성)이 크면 점수가 라벨과 무관한 site 신호를 실어나름(누출). ✅powered / ⚠️exploratory.

## 표. endpoint별 site 감사

| endpoint | 암종 | 검정력 | n_site | pooled AUROC | within-site AUROC (drop) | 단일site 양성독점 | 단일클래스 site수 | eta²(음성) | eta²(전체) |
|---|---|:--:|--:|--:|--|--:|--:|--:|--:|
| braf_v600e | COLORECTAL | ⚠️ | 21 | 0.868 | 0.889 (-0.021) | 0.400 | 7 | 0.078 | 0.052 |
| lauren_diffuse | GASTRIC_STAD | ✅ | 11 | 0.536 | 0.783 (-0.247) | 0.355 | 1 | 0.284 | 0.235 |
| msi_h | GASTRIC_STAD | ⚠️ | 13 | 0.860 | 0.861 (-0.000) | 0.375 | 2 | 0.079 | 0.168 |
| erbb2_amp | GASTRIC_STAD | ⚠️ | 13 | 0.644 | 0.677 (-0.033) | 0.500 | 4 | 0.305 | 0.276 |
| ebv | GASTRIC_STAD | ⚠️ | 12 | 0.948 | 0.929 (+0.018) | 0.571 | 3 | 0.169 | 0.098 |
| hpv_pos | HEADNECK_HNSC | ✅ | 15 | 0.959 | 0.966 (-0.006) | 0.192 | 2 | 0.108 | 0.099 |
| egfr_amp | HEADNECK_HNSC | ⚠️ | 15 | 0.602 | 0.531 (+0.071) | 0.235 | 3 | 0.155 | 0.196 |
| grade_high | HEADNECK_HNSC | ✅ | 15 | 0.815 | 0.850 (-0.035) | 0.220 | 1 | 0.093 | 0.093 |
| histology_lusc | LUNG_NSCLC | ✅ | 37 | 0.939 | — | 0.157 | 27 | 0.128 | 0.705 |
| egfr_activating | LUNG_NSCLC | ⚠️ | 37 | 0.851 | 0.789 (+0.062) | 0.200 | 19 | 0.468 | 0.473 |
| kras_g12c | LUNG_NSCLC | ⚠️ | 37 | 0.681 | 0.406 (+0.275) | 0.214 | 19 | 0.468 | 0.458 |

## 판독 (실측)

- **두경부 HPV — site 인공물 아님(가장 중요).** pooled 0.959 → within-site 0.966(drop −0.006, 사실상 무), eta²(음성) 0.108, 단일site 양성독점 0.192로 낮다. site를 상수로 고정해도 신호가 그대로 유지되므로, HPV 확증은 기관·스캐너 batch가 아니라 형태(바이러스축)에서 온다. **122 외부검증 면제 협상의 정량 근거.**
- **폐 LUSC 조직형(양성대조) — site 구성 편중은 예상된 것.** 37개 site 중 27개가 단일 조직형(eta²_all 0.705). LUSC/LUAD가 기관별로 몰려 있어 within-site(양·음성 공존 site) 계산이 불가(—). 조직형은 검출돼야 하는 양성대조라 이 편중 자체는 문제 아니나, 조직형이 강한 site 상관물임을 보여 #7(조직형 교란)과 정합.
- **위 Lauren — 음성의 정체가 site 일반화 실패임을 계량 확인.** pooled 0.536인데 within-site 0.783(drop −0.247). 즉 **형태 신호가 site 안에는 있으나 site간 라벨편중으로 일반화가 무너진다**(eta² 음성 0.284, 단일클래스 site 존재). A3 진단(Lauren 특이 site-교란)의 정량 확증 — "형태에 전혀 안 보임"이 아니라 "site를 넘어 일반화 안 됨"으로 음성을 정밀화.
- **두경부 grade_high — 깨끗.** within 0.850 vs pooled 0.815(drop −0.035 유지), eta²(음성) 0.093 낮음.
- **폐 KRAS — site+조직형 이중 교란(exploratory).** pooled 0.681 → within-site 0.406(붕괴), eta²(음성) 0.468(매우 높음=점수가 라벨 무관 site 신호를 실어나름). #7의 조직형 인공물 판정과 겹쳐 KRAS는 형태 상관물 축 승격 불가가 이중으로 확정. EGFR도 eta²(음성) 0.468로 site 신호가 크나 within-site 0.789로 잔존.

> ⚠️ **within-site AUROC 안정성 주의**: 암종당 site가 많아 site별 표본이 작다(특히 exploratory·Lauren n=58). within-site 값은 소수 site에 좌우될 수 있어 방향 지표로 읽고, 확정은 재학습 LOSO(후속)로 한다.

## 122(외부검증 면제) 연결

- 이건규 122 판정: "(B) — #2 site 감사 결과에 조건부. 면제 협상 = LOSO 성능저하 작음 + label-site confounding 없음 + held-out site calibration 유지".
- 본 감사의 within-site AUROC 유지(=LOSO 근사) + 앵커 eta²(음성) 작음 + 앵커 label-site 편중 작음이 **면제 협상의 정량 근거**가 된다. 반대로 편중이 크면 그 endpoint는 외부검증 없이 승격 불가.

## 재학습 필요 후속 (여기서 안 함, 명시)

- 임베딩→TSS site-예측 모델(batch 학습 여부 직접 검정), 전면 LOSO 재학습, site-stratified label permutation 재학습. GPU 재학습 자원 필요 → braveji와 큐 협의.

> claim_level: hypothesis_only · 리뷰: braveji. 재학습 후속은 별도.