# 다중 FM CLAM 재학습 실행법 (Paper C 모델 비의존성)

임베딩(다중 FM 파이프라인, `20260717_multifm_robustness`)이 끝나면, 같은 결정지도가
파운데이션 모델을 바꿔도 유지되는지 검정하기 위해 CLAM을 각 FM 공간에서 재학습한다.
학습 코드는 기존 `run_mil_cost.py`를 그대로 쓰되 `--fm`만 붙인다.

## 실행 (kkkim = Owner)

대장·폐 두 코호트가 대상이다(CANCER_CFG 기준). FM은 virchow2·uni2h.

```bash
cd ~/project/BioProject02/experiments/crosscancer
# 임베딩 완주 확인: /workspace/data/cache/biop02/<colorectal|lung_nsclc>/<virchow2|uni2h>/
for FM in virchow2 uni2h; do
  for C in COLORECTAL LUNG_NSCLC; do
    /opt/envs/spatialpatho/bin/python run_mil_cost.py --cancer $C --fm $FM --device cuda:0
  done
done
```

- 학습 시간: 코호트당 수 분~17분(UNI 실측 대장 3.5분·폐 17분, 차원 커도 비슷).
- 출력: `<cancer>/full/mil_cost_results_<fm>.json` (UNI 기존본을 덮지 않는다).
- 각 결과에 `fm`·`feature_dim`·`claim_level: hypothesis_only`·`critic_status: pending` 기록됨.

## 검증 (Owner ≠ Reviewer)

kkkim이 학습(Owner)했으므로 **크로스체크는 sjpark 또는 braveji(Reviewer)**가 한다.
- 결정론 재계산: 같은 seed(42)로 재실행 → AUROC byte-identical 확인.
- 핵심 질문: UNI 결정지도(mil_cost_results.json)의 순서·headline contrast가 virchow2·uni2h에서도
  유지되나. 유지되면 "법칙은 모델 비의존적" 근거. 어긋나면 정직하게 보고.

## 주의

- **이건 임베딩까지가 아니라 결과 주장 단계다.** critic_status pending으로 두고 Reviewer 서명 전
  본문 승격 금지.
- UNI(기본, `--fm` 생략)는 기존 동작 그대로 — 회귀 없음.
