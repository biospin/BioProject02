# CLAM — Core Summary

**Lu MY, Williamson DFK, Chen TY, Chen RJ, Barbieri M, Mahmood F. (2021).**
*Data-efficient and weakly supervised computational pathology on whole-slide images.*
Nature Biomedical Engineering. DOI: 10.1038/s41551-020-00682-w · preprint arXiv:2004.09666 ·
code: https://github.com/mahmoodlab/CLAM (GPLv3, non-commercial academic)

## 한 줄 요약 (one-line)
CLAM = **Clustering-constrained Attention Multiple Instance Learning** — slide-level label만으로
(ROI/patch annotation 없이) WSI를 분류하는 attention-MIL framework이자, 그 전후의
**tissue segmentation → tiling → feature extraction** 전처리 toolkit.

## Problem
WSI는 gigapixel이고 patch/ROI 단위 annotation은 비싸다. 기존 weak supervision (instance-level
MIL)은 데이터 비효율적이고 multi-class subtyping에 약하다. CLAM은 **slide label만** 쓰면서
data-efficient하게 학습하는 것을 목표로 한다.

## Method (핵심 구조)
1. **Tissue segmentation + patching** — background/hole을 제외하고 segmented tissue에서
   fixed-magnification patch 좌표를 추출 (`create_patches_fp.py`).
2. **Frozen feature extraction** — 각 patch를 ImageNet-pretrained ResNet50 truncated backbone으로
   1024-dim feature로 변환 (학습 중 encoder는 고정 = bag-of-features).
3. **Attention pooling** — gated-attention network (Ilse 2018 ABMIL 계열)이 각 patch에 attention
   score를 부여하고, attention-weighted sum으로 slide-level representation을 만든다.
   → "high diagnostic value"인 sub-region을 자동 식별.
4. **Instance-level clustering constraint** — attention이 높은/낮은 대표 patch들을 pseudo-label로
   삼아 보조 clustering loss를 건다. feature space를 refine하고 더 separable하게 만드는 것이 핵심
   차별점 (vs. 순수 ABMIL).
5. **Multi-class support** — CLAM-SB (single attention branch, binary/공유) 와 CLAM-MB
   (multi-branch, class별 attention branch)로 multi-class subtyping을 지원.

## Validation (실제 평가)
세 종류 분석으로 검증: **RCC subtyping**, **NSCLC subtyping**, **breast lymph node metastasis
detection**. 핵심 주장 — slide label만으로 data-efficient하게 강력한 성능을 내고,
**independent test cohort, cell-phone microscopy 이미지, biopsy**로도 일반화/적응됨
(domain adaptation·generalization 입증). *정확한 AUC 수치·slide 수는 Nature 본문 IdP 뒤라
WebFetch로 확정 못 함 — 인용 시 본문/표 직접 확인 필요.*

## Why it matters here (BIOP02)
- **MIL baseline**: 병리 attention-MIL의 사실상 표준. 우리 slide-level phenotype head의 비교 대상.
- **Preprocessing 선례**: Otsu 기반 tissue mask + 고정 배율 tiling + frozen-encoder 추출 —
  우리 Otsu-mask tiling 설계와 1:1로 대응.
- **Toolkit 재사용 가능**: segmentation/patching/feature-extraction 단계가 모듈화되어 UNI/CONCH
  encoder swap 지원.
