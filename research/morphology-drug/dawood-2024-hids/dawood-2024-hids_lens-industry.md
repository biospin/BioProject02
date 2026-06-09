# dawood-2024-hids — Lens: Industry / Reproducibility

## 코드 가용성
- **GitHub: https://github.com/engrodawood/HiDS** — SlideGraph∞ 기반 파이프라인 공개.
- 인터랙티브 데모: http://tiademos.dcs.warwick.ac.uk/bokeh_app?demo=HiDS (결과 탐색용).
- 의존 도구 **TIAToolbox**(U-Net tissue seg, patch 추출)는 오픈소스 → 전처리 재현 용이.

## 데이터 가용성
- **TCGA-BRCA WSI: GDC portal** (https://portal.gdc.cancer.gov/) — open-access slides, 우리 Paper A scope(~150 slide subset)와 동일 출처.
- **CTRP** AUC-DRC + cell-line 발현 → ridge regression 라벨. 모두 공개 리소스라 라벨 재생성 가능.
- 주의: 본 논문은 936/551 환자 규모; 우리는 BIOP02 governance상 **TCGA 전수 다운로드 금지(~150 subset)**.

## 재현성 평가
- 백본이 **ImageNet ShuffleNet**이라 gated FM 승인 불필요 → 라벨 파이프라인만 갖추면 **즉시 재현 가능**(낮은 진입장벽).
- 그래프 구성 파라미터(Delaunay ≤4000px, EdgeConv L=1,2,3, pairwise ranking loss) 명시 → 모델 재현 명확.
- 리스크: CTRP imputation 라벨 버전·필터링 디테일이 코드 의존적 → repo 코드를 source-of-truth로 사용해야 일치.

## 우리가 바로 재사용/재현할 것 (Exp3)
1. **CTRP ridge-imputation 라벨 생성기** — cell-line 발현→AUC-DRC ridge → TCGA-BRCA 환자 imputed sensitivity. 우리 multi-route(PRISM/GDSC) 중 CTRP route의 reference 구현으로 채택.
2. **End-to-end baseline 재현** — ShuffleNet feature + SlideGraph∞ GNN을 **Exp3의 "end-to-end 대조군"**으로 그대로 reimplement (우리 phenotype-intermediate 파이프라인과 정면 비교).
3. **TIAToolbox 전처리 설정** — 512×512 @ 0.25µm tiling을 우리 tile_config(256×256 @ 20×)와 비교용 변형으로 참조.

## 산업/거버넌스 메모
- 본 논문은 직접 sensitivity 점수를 출력 → 우리는 동일 출력을 내되 **hypothesis-only claim_level + Scientific Critic pass** 후에만 공유(anti-DRP 규약 준수).
