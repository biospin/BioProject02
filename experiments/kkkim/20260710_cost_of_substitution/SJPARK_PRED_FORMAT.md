# sjpark 예측 파일 요청 포맷 (C1 receptor-status 라우팅용) — JIRA BIOP02-53 #11006

`compute_cost.py`의 (B') 블록이 아래 파일이 나타나면 **자동 실행**한다.

**경로:** `experiments/sjpark/cptac_ext_predictions_indexed.csv`

**컬럼:**
| 컬럼 | 내용 |
|---|---|
| `slide_id` | CPTAC 슬라이드 ID(승격 매니페스트 `embedding_manifest_cptac_uni.csv`와 조인) |
| `er_pred_prob` | ER+ 예측 확률 0~1 (CLAM ER 모델, **재생성된 올바른 ER 예측**) |
| `her2_pred_prob` | HER2+ 예측 확률 0~1 |
| (선택) `pr_pred_prob`, `pam50_pred` | 있으면 무시 안 함 |

- 측정 라벨은 승격 매니페스트의 `er`/`her2`("Positive"/"Negative") + `has_er`/`has_her2`에서 읽음(sjpark가 라벨 넣을 필요 없음).
- 현재 `er_status_clam_uni_v2/predictions_ext.npy`는 손상(HER2와 동일, 294행) → **ER 재생성 + slide_id 인덱스**가 이 파일의 목적.
- 도착 즉시 `patient_routing_cost_receptor.json` 생성됨(PAM50 라우팅과 robustness 비교).
