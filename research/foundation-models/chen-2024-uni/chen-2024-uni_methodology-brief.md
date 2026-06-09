# chen-2024-uni — Methodology Brief (adopted recipe + Exp1)

## 우리가 채택하는 정확한 recipe (Adopted preprocessing/embedding)
UNI 논문이 직접 정당화하는 설정을 BIOP02 default로 고정한다.

| 단계 | 설정 | 근거 (paper) |
|---|---|---|
| Tiling | **256×256 px @ 20×**, Otsu tissue mask, per-patient cap 5000 | UNI pretrain tile = 256×256 @ 20× |
| Stain norm | **없음 (없이 진행)** | UNI은 ImageNet mean/std만 사용, dedicated stain-norm 미적용 |
| 입력 정규화 | resize→224 center-crop, **ImageNet mean (0.485,0.456,0.406) / std (0.229,0.224,0.225)** | GitHub transform |
| Encoder | **DINOv2 ViT-L/16, `MahmoodLab/uni`** | 본 논문 |
| Embedding | 패치당 **1024-dim** → slide-level은 CLAM/ABMIL aggregation | tile encoder만 제공 |

→ 즉 "256×256@20×, no stain-norm, ImageNet-norm, 1024-dim"이라는 우리 파이프라인 default는 UNI 논문 설정의 **직접 복제**이며, stain-norm 생략은 임의 결정이 아니라 backbone 설계에 정합한 선택이다.

## Exp1 — Backbone comparison (이 논문의 역할 = 우리 backbone)
**가설**: 어떤 성능 gain이든 그 출처는 *FM 임베딩 자체*이지, MIL/분류기 트릭이 아니다.

**Arms (동일 tiling·split·BRCA phenotype 라벨 고정)**:
1. **UNI (1024-dim)** — 본 논문, 우리 primary backbone.
2. **ImageNet ViT/ResNet backbone** — Dawood 류 regime. FM 사전학습 없는 supervised-ImageNet feature.
3. **Tafavvoghi XGBoost** — hand-crafted / non-FM feature baseline.

**비교 방식**: 세 arm 모두 동일 downstream head로 ER status 등 BRCA molecular phenotype 예측. 동일 데이터/split에서 UNI > ImageNet-backbone > XGBoost 순의 gain이 나오면 "**FM이 gain의 source**"라는 주장 성립.

**Critic 연계 (7-point)**: (2) baseline comparison = 본 Exp1 자체. (6) DRP framing 금지 — drug feature 입력 없음, hypothesis-only 유지. (1) data leakage = patient-level split 고정 후.

**Few-shot 검증**: UNI의 4-shot/8× label-efficiency 주장을 우리 ~150-slide small-N에서 재확인 — label-efficient transfer가 작은 subset에서 실제로 유지되는지가 Exp1 부가 출력.
