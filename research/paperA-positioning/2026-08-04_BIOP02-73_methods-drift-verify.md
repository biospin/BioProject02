# BIOP02-73 Methods 정합 검수 (드리프트·인용) — 2026-08-04

> kkkim 섹션-오너 제출 전 검수(BIOP02-115 배정). `manuscript/sections/03_methods.md`의 타일링·임베딩(M1/M2)과 인접 수치를 **실제 config·코드·결과 JSON과 값 단위로 대조**했다. 지어낸 값 여부·드리프트 점검.

## 결과 — 드리프트 0 (전 항목 source 일치)

| Methods 서술 | 값 | Source (파일:줄) | 일치 |
|---|---|---|---|
| Tile size | 256×256 | `agents/embedding/configs/tile_config.yaml` `tile_size: 256` | ✅ |
| 배율/MPP | 20× (0.5 μm/px) | 〃 `target_mpp: 0.5` | ✅ |
| Tissue mask | Otsu (thr 0.1) | 〃 `otsu.tissue_threshold: 0.1` | ✅ |
| Per-patient cap | 5,000 | 〃 `per_patient_cap: 5000` | ✅ |
| 임베딩 UNI | 1024-d | `run_mil_cost.py:43` FM_SPEC uni dim 1024 | ✅ |
| 임베딩 Virchow2 | 2560-d (CLS+mean-patch, register 제외) | `extract_virchow2.py:36,64,68` | ✅ |
| 임베딩 UNI2-h | 1536-d | `run_mil_cost.py:46` | ✅ |
| 정규화 | ImageNet mean/std, stain norm 없음 | `extract_uni.py:88` (Macenko/Reinhard 부재) | ✅ |
| 슬라이드 수 대장/폐/위/두경부 | 523 / 1026 / 439 / 468 | 각 `<cancer>/full/mil_cost_results.json` `n_slides` | ✅ |
| CLAM hidden/att | 512 / 256 | `run_mil_cost.py:107` | ✅ |
| epoch / seed | 40 / 42 | `run_mil_cost.py:81,85` | ✅ |
| 부트스트랩 | 1000회 | `run_mil_cost.py:68` | ✅ |
| Yale pCR AUROC | 0.533 [0.411–0.653] | jhans 공식 A4(BIOP02-80, [0.411,0.653]) | ✅ |

## 반영한 것 (M2 갭 1건 — -73 드래프트가 이미 확정했으나 통합본 누락)
- `2026-07-16_BIOP02-73_methods-tiling-embedding-draft.md`가 "Methods에 stain normalization 미적용 명시"로 확정(§27)한 문장이 **통합 03_methods.md M2에 빠져 있었다.** 실제 코드(`extract_uni.py`)로 재확인 후 M2에 추가: ImageNet 채널 정규화·H&E 염색 정규화 미적용·염색 변이 미보정=한계. Virchow2 임베딩 구성(CLS+mean-patch, register 제외)도 한 문장 보강.
- 병리 FM 논문 리뷰어가 자주 묻는 항목이라 사전 보강 가치가 있다.

## 판정
M1/M2(타일링·임베딩) = **수치·인용 정합, 지어낸 값 없음.** -73 내용은 통합본에 실질 반영됨(+ 위 갭 보강). 서사 통합은 주저자(이건규, BIOP02-115) 몫. 제출 전 최종 재대조는 원고 확정 시 1회 더 권장.
