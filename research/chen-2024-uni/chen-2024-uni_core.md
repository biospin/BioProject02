# chen-2024-uni — Core Summary

**Towards a general-purpose foundation model for computational pathology**
Chen RJ et al., *Nature Medicine* 2024. DOI 10.1038/s41591-024-02857-3.

## 핵심 (What UNI is)
UNI는 **DINOv2 self-supervised ViT-Large/16** 기반의 병리 tile-level foundation model이다.
H&E 패치를 **1,024-dim** embedding으로 변환하는 순수 **tile encoder** (slide-level aggregator는 별도, 예: CLAM/ABMIL).
Pretraining은 **Mass-100K** — **20개 organ type**, **100,426개 진단 H&E WSI**에서 추출한 **100,130,900개(>100M) tile** (256×256 @ 20×) 위에서 라벨 없이 수행됐다.

## 왜 중요 (Why it matters)
- **Label-efficient transfer**: 4-shot 세팅에서 UNI를 따라잡으려면 차순위 encoder가 **클래스당 최대 8배** 더 많은 예시를 필요로 함. Prostate grading에서 모든 few-shot 구간에 걸쳐 **2배 label-efficient**.
- **Data scaling이 성능을 견인**: Mass-1K→22K **+4.2%**, Mass-22K→100K **+3.7%** — pretraining 규모가 곧 transfer 품질.
- **광범위 평가**: **34개** computational pathology task. CAMELYON16 AUROC **0.966** (pathologist 수준 상회), OncoTree 43-class top-5 acc **93.8%** / AUROC **0.976**, prostate ISUP grading quadratic-weighted κ **0.946**.

## 핵심 디자인 결정 (Key design choices)
- **No dedicated stain normalization** — inference 전처리는 224로 resize/center-crop 후 **ImageNet mean/std** 정규화만 사용. 별도 H&E stain-norm 없음.
- **Tile = 256×256 @ 20×** (high-res fine-tuning에 512 사용).
- Self-supervised → 라벨/주석 비용 없이 대규모 다장기 일반화.

## BIOP02 한 줄 (One-liner for us)
UNI는 우리 파이프라인의 **default tile encoder**: 256×256@20× 패치 → 1024-dim → CLAM-style MIL → BRCA molecular phenotype. 본 논문이 "stain-norm 없이도 강한 transfer"를 직접 근거로 제공한다.
