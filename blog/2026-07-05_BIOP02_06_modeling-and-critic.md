# 표현형 예측 모델과 Critic 7항목 교차리뷰

> 한 줄 요약: H&E 병리 슬라이드로 유방암 분자 표현형을 예측하는 모델을 단순 MLP부터 attention MIL(CLAM-SB)까지 단계적으로 구축했고, 그 결과를 'Owner ≠ Reviewer' 원칙에 따라 7항목으로 교차리뷰해 최종 'caution' 판정을 내렸다. 이 글은 기준선의 성격을 잘못 읽으면 부당한 실패 판정이 나올 수 있다는 점, 그리고 HER2의 외부 검증 실패라는 한계를 어떻게 드러냈는지를 정리한다.

## 핵심 개념

병리 슬라이드 한 장은 조직을 크게 확대한 이미지다. 이것을 컴퓨터가 다루려면 먼저 숫자 벡터, 즉 임베딩으로 바꾼다. 임베딩은 슬라이드를 요약한 숫자 목록이라고 볼 수 있다.

그 숫자에서 유방암의 분자 표현형(예: ER/PR/HER2 상태, PAM50 아형)을 예측하는 모델을 만든다. 가장 단순한 모델부터 시작해 점차 정교하게 확장한다.

결과가 나와도 곧바로 공유하지 않는다. 다른 사람이 7가지 항목으로 검토한 뒤에야 공유한다. 이 글은 그 검토 과정을 다룬다.

## 이유 / 배경

SpatialPathoAgent(BioProject02)는 H&E 병리 슬라이드(WSI) → 형태 임베딩 → 분자 표현형 예측 → 치료 가설로 이어지는 파이프라인이다. 유방암(BRCA) 전용이며, 약물의 화학 구조를 입력으로 넣지 않는다. 즉 약물 반응 예측(drug response prediction) 모델이 아니다. 출력은 모두 hypothesis_only(가설 수준)로 표시한다. 대상은 TCGA-BRCA 약 1010장의 슬라이드다.

모델링에는 한 가지 원칙이 있다. 건너뛰기 금지. 가장 단순한 MLP 기준선부터 시작해 attention MIL로 넘어간다. 모델링 담당은 sjpark다.

- MLP(다층 퍼셉트론) 기준선: 슬라이드 전체를 평균 낸 임베딩 한 벡터를 받아 표현형을 예측하는 가장 단순한 신경망.
- MIL(multiple instance learning, 다중 인스턴스 학습): 슬라이드 하나를 수천 개 타일이 담긴 가방(bag)으로 본다. 어떤 타일이 중요한지 모델이 스스로 가중치(attention)를 학습해 가방 전체의 라벨을 예측한다. 여기서는 CLAM-SB 구조를 쓴다. 중요하게 본 타일의 attention을 이미지 위에 색으로 그리면(attention map) 모델의 판단 근거를 시각적으로 확인할 수 있다.

결과를 공유하기 전에는 반드시 과학적 비평(Scientific Critic) 7항목을 통과해야 한다. 핵심 규칙은 Owner ≠ Reviewer, 즉 자기 결과를 자기가 검토하는 것을 금지한다. 모델링 결과(sjpark)의 교차리뷰 담당은 kkkim이다.

## 진행 단계

모델링 산출 이력은 다음과 같이 쌓였다.

- BIOP02-42: ER status MLP (UNI v1)
- BIOP02-46: PR/HER2 status MLP + PAM50 5-class MLP
- BIOP02-50: subtype_only 기준선 + bootstrap 신뢰구간 + PAM50 AUPRC 추가, HER2 해석 보강
- BIOP02-47/53: CLAM-SB attention MIL — ER/PR/HER2 × UNI v1/v2, early stopping, CPTAC 외부검증, attention map 시각화, subtype_only 기준선 비교

Critic 7항목 체크리스트는 다음과 같다.

① 데이터 누수 ② 기준선 비교(무작위·subtype-only·pixel-mean) ③ 반사실 점검(중요 특징 제거 시 순위 변화) ④ 교차데이터셋 일관성 ⑤ 생물학적 타당성 ⑥ 'drug response prediction' 표현 금지 ⑦ 클레임 레벨(hypothesis_only 원칙)

BIOP02-53에서 리뷰어 kkkim이 sjpark의 CLAM MIL 결과를 교차리뷰했고, 최종 판정은 caution(주의)이었다. 항목별 결과는 다음과 같다.

- ① 데이터 누수: PASS. TSS(조직 출처 사이트) 37개가 train/val/test에 중복 0으로, site-disjoint(사이트가 서로 겹치지 않음)를 검증했다.
- ② 기준선 비교: PASS. ER의 AUROC는 0.901로 무작위 0.526, mean_embed 0.816보다 높았다. 다만 subtype_only(0.918)는 PAM50 아형을 입력으로 넣은 상한선(ceiling, `--aux_col pam50`)이지 바닥선(floor)이 아니다. 따라서 모델이 0.918을 넘지 못한 것은 한계(limitation)일 뿐 FAIL이 아니다.
- ③ 반사실 점검: N/A.
- ④ 교차데이터셋 일관성: CAUTION. ER은 외부 AUROC 0.894, PR은 0.778로 외부에서도 유지됐으나, HER2는 외부에서 거의 무작위였다(ext_auc 0.53, auprc 0.12). 실제 실패에 해당한다.
- ⑤ 생물학적 타당성: N/A(총괄 Critic braveji에게 위임).
- ⑥ DRP 표현: PASS.
- ⑦ 클레임 레벨: PASS(hypothesis_only 유지).

산출물은 `experiments/kkkim/20260703_critic_biop02-53/critic_report.json`(스키마 v0.1 유효)과 `REVIEW.md`이며, 커밋은 `3f45ffd`, PR은 #21이다. JIRA BIOP02-53 상태는 '진행 중 → 검토 중'으로 옮겼다. 최종 pass 승인은 총괄 Critic braveji가 맡는다. CPTAC 임시 라벨을 kkkim이 직접 만들었기 때문에, self-reference(자기 참조)를 피하려는 조치다.

## 배운 점 / 시행착오

이번 리뷰의 핵심은 두 가지다.

첫째, 상한선과 바닥선의 구분이다. ② 기준선 비교에서 subtype_only는 0.918로 모델(0.901)보다 높은 값을 냈다. 이 숫자만 보면 모델이 기준선을 넘지 못했으니 실패라고 판정하기 쉽다. 그러나 subtype_only는 PAM50 아형이라는 정답에 가까운 정보를 입력으로 넣은 상한선이다. 이미지만으로 예측하는 모델이 이를 넘지 못하는 것은 자연스러운 한계이지 규칙 위반이나 실패가 아니다. 이 구분을 놓쳤다면 부당한 FAIL로 이어질 수 있었다. 기준선을 비교할 때는 그 기준선이 넘어야 할 바닥선인지, 넘지 못해도 되는 상한선인지를 먼저 판단해야 한다.

둘째, 외부 검증에서 드러난 한계다. ④ 교차데이터셋에서 ER과 PR은 외부 데이터(CPTAC)에서도 성능이 유지됐다. 반면 HER2는 외부에서 거의 무작위(ext_auc 0.53, auprc 0.12) 수준으로 성능이 떨어졌다. 이는 명시해야 할 한계이므로, 전체 판정을 PASS가 아니라 caution으로 낮췄다.

정리하면 이번 리뷰는 두 판단을 함께 요구했다. 기준선의 성격을 정확히 읽어 부당한 실패 판정을 막는 것, 그리고 HER2 외부 실패 같은 한계는 정확히 짚어 기록하는 것이다.

## 결론

단순 MLP에서 CLAM attention MIL까지 단계적으로 구축한 표현형 예측 모델을, Owner ≠ Reviewer 원칙에 따라 7항목으로 교차리뷰했다. ER은 내부·외부 모두 견고했고 데이터 누수도 없었으나, HER2는 외부 검증에서 실패했기에 최종 판정은 caution이었다. 결과는 `critic_report.json`과 `REVIEW.md`로 남겼고(커밋 `3f45ffd`, PR #21), 최종 pass 승인은 self-reference를 피하기 위해 총괄 Critic braveji에게 넘겼다. 이번 리뷰는 부당한 실패 판정을 막는 판단과 실제 한계를 정확히 드러내는 판단을 함께 수행한 사례다.
