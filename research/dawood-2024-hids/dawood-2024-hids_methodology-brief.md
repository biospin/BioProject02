# dawood-2024-hids — Methodology Brief (구현·비교 가이드)

우리가 **Exp3(end-to-end baseline)**와 **Exp4(라벨 route 비교)**에서 직접 구현/비교할 방법.

## A. CTRP ridge-imputation 라벨 (재구현 대상)
```
cell-line gene expression  ──ridge regression──▶  CTRP AUC-DRC (per compound)
        │ (학습된 회귀계수)
        ▼
TCGA-BRCA patient expression  ──apply──▶  imputed sensitivity (427 compounds)
```
- 입력: cell-line 발현 X, CTRP AUC-DRC y (427 화합물).
- 모델: 화합물별 linear **ridge regression** (geeleher-2014-transfer 계보).
- 출력: 환자별 imputed sensitivity → image 모델의 **연속 라벨**(ranking target).
- 우리 작업: 이 route를 우리 multi-route(PRISM/GDSC/CTRP) 중 **CTRP route reference**로 구현하고, route 간 일치도(Critic checklist #4 cross-dataset)를 측정.

## B. End-to-end 이미지 모델 (대조군 재현)
- 전처리: TIAToolbox U-Net tissue seg → **512×512 @ 0.25µm/px** patch.
- feature: **ImageNet ShuffleNet** → 1024-d (우리 FM 백본 UNI/CONCH 대비 ablation 축).
- graph: Delaunay triangulation(≤4000px) patch graph.
- GNN: **SlideGraph∞**, EdgeConv L=1,2,3, node score 집계 → WSI-level.
- loss: **pairwise ranking loss** (환자 sensitivity 순위 비교).
- 검증(원논문): **5-fold CV / 80:20**, LOSO ablation — 외부검증 없음.

## C. BIOP02 Exp 연계
- **Exp3 — End-to-end baseline:** 위 B를 our pipeline에 통합해 *phenotype-intermediate vs end-to-end* 직접 비교. 동일 TCGA-BRCA subset·동일 CTRP 라벨로 공정 비교.
- **Exp4 — Route convergence:** A의 CTRP route를 PRISM·GDSC route와 합쳐 multi-route 수렴(우리 차별점) 검증; 단일 route(HiDS) 대비 robustness 측정.
- **외부검증 확장:** 두 Exp 모두 **CPTAC-BRCA 외부 테스트**를 추가해 HiDS가 결여한 generalization 증거 확보.
- **거버넌스:** 출력은 ranked **hypothesis-only**; "drug response prediction"·"personalized therapy" 표현 금지, Critic pass 후에만 `#biop02-experiments` 공유.

## 검증 플래그
모든 파라미터(512px@0.25µm, ShuffleNet 1024-d, Delaunay 4000px, EdgeConv L=1,2,3, pairwise ranking, 5-fold CV, n=551, 427/186)는 PMC10771481 본문에서 직접 확인. 외부·임상 독립 코호트 없음 / 분자구조 입력 없음 = 확인됨.
