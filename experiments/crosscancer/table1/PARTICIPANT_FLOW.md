# Participant flow — 5암종 (TRIPOD+AI 13b 짝)

`n식별` = patient_labels.csv/manifest에 라벨이 조인된 환자 수(=GDC 매니페스트에서 H&E 슬라이드+임상데이터 결합 가능 subset, 이미 필터링된 상태 — raw GDC 전체 대비 제외 사유는 각 코호트 원 매니페스트 문서 참조). 여기서부터 아래로: 라벨 결측 없는 환자 → train/holdout 분리.

| 암종 | n(라벨 조인, 시작점) | n(슬라이드 보유) | n(train) | n(holdout=val+test) |
|---|---|---|---|---|
| 유방 | 1010 | 1010 | 707 | 303 |
| 폐 | 1050 | 1026 | 735 | 315 |
| 대장 | 534 | 523 | 374 | 160 |
| 위 | 440 | 439 | 308 | 132 |
| 두경부 | 523 | 468 | 366 | 157 |

엔드포인트별 최종 분석 대상(holdout denominator)은 Table 1b 참조 — 암종 안에서도 엔드포인트마다 라벨 결측 패턴이 달라 holdout n이 다르다(예: 위 lauren_diffuse n=58 vs msi_h n=107, 같은 GASTRIC holdout 132명 중 라벨 있는 하위집합만).
