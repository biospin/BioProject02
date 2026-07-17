# fernandez-romero-2026-domaingen — Lens: Industry / Reproducibility

## 코드 가용성
- **공개(Code Availability 명시).** 저자 스크립트는 **CLAM repo fork + PathBench-MIL** 기반.
  - https://github.com/BIGS-investigacion/CLAiMem-ALL.git
  - https://github.com/BIGS-Investigacion/PathBench-MIL.git
- MIL 백본(CLAM/TransMIL/DSMIL)이 모두 오픈소스 표준 구현이라 파이프라인 재현 장벽 낮음. (repo 내용·라이선스·실제 실행성은 미검증 → 재사용 전 확인)

## 데이터 가용성
- **명시적 Data Availability 문장 없음([미확인 — NOT FOUND]).** 단 두 코호트 모두 공개 리소스:
  - **TCGA-BRCA**(1,522 slide / 1,079 pt, FFPE) — GDC portal, 우리 Paper A scope와 동일 출처.
  - **CPTAC-BRCA**(387 flash-frozen slide / 120 pt) — IDC `gs://` bucket, 우리 외부검증과 동일 출처.
- **핵심:** 그들의 외부 코호트가 **flash-frozen**이라 FFPE↔frozen 준비 차이가 도메인 시프트에 섞임. 우리 CPTAC 사용 시 조직준비 축을 통제·명시해야 그들과 차별.

## FM 스택 대비
- 그들 13 FM ⊇ 우리 승인 FM 상당수: **UNI, CONCH, Virchow2, UNI-2, Prov-GigaPath** 모두 포함(+ Hibou/H-optimus-0/Phikon v2/Musk/CTransPath/RetCCL/ResNet-50).
- **Virchow v2가 그들 mean-rank 1위(2.00)** → 우리 "SOTA 다중 FM 견고성 검증"에서 Virchow2를 강 baseline으로 잡는 근거. 단 그들 결론은 "최고 FM도 외부에서 붕괴" → **FM 교체로 도메인 문제 못 푼다**는 게 우리 결정레이어(보정/기권) 정당화.

## 재현성 평가
- 지표: **ER/PR/HER2 PR-AUC, PAM50 macro-F1**, 열화 = **RPD=(Q_CV−Q_HO)/Q_CV**. 표준 정의라 우리 파이프라인에서 재계산·대조 가능.
- tile **128 µm/~20×** — 우리 tile_config(256×256 @ 20×, ≈128µm FoV)와 **사실상 동일 FoV** → 임베딩 스케일 호환, 우리 캐시 재사용에 유리.
- 리스크: 픽셀 크기·정규화·per-model split 디테일이 원문 inline graphic/repo 의존 → repo를 source-of-truth로 확인해야 정확 재현.

## 우리가 바로 재사용/참조할 것
1. **RPD 지표**를 우리 cost-of-substitution의 "prediction-fidelity 열화" 보조축으로 재계산(단, 우리 헤드라인은 routing-cost).
2. **도메인 시프트 요인분해**(staining/feature-space=80%)를 **AI 결정레이어의 OOD 트리거 설계**에 참조.
3. **Virchow v2 벤치**를 우리 다중-FM 강건성(Paper C 모델 비의존성) baseline으로 인용.

## 산업/거버넌스 메모
- 그들은 예측 정확도만 출력 → 우리는 동일 임베딩 위에서 **routing-cost + calibration/abstention**를 내되 `hypothesis_only` + Critic pass 후 공유(DRP 프레이밍 금지).

## 검증 플래그
- Code Availability(CLAM fork + PathBench-MIL, 2 GitHub URL) = PMC quote-demand 확인. **Data Availability 문장 = NOT FOUND**. repo 실제 실행성·라이선스 = 미검증.
