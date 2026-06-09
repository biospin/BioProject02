# chen-2024-uni — Industry / Engineering Lens

## 접근 & 게이팅 (Access)
- **HuggingFace gated repo**: `MahmoodLab/uni` (원본 UNI, ViT-L/16, **1024-dim**, 03/2024 공개). 후속 `MahmoodLab/UNI2-h` (ViT-h/14, 1536-dim, 01/2025)는 별도 모델.
- **게이팅 절차**: HF model page에서 access 요청 → 승인 후 User Access Token으로 로그인하여 weight 다운로드. CLAUDE.md대로 **institutional email로 신청** (gmail/naver 불가), token은 git commit 금지(`~/.claude/settings.json` 또는 shell env만).
- **License CC-BY-NC-ND 4.0**: 비상업·연구용. 우리 publication-only 스코프와 일치.

## 로딩 & 임베딩 (Loading)
- **`timm.create_model()`** 로 아키텍처 지정 후 weight 자동 다운로드(huggingface_hub cache), 또는 `hf_hub_download()` + `torch.load()`.
- **전처리**: resize→224 center-crop→tensor→**ImageNet mean (0.485,0.456,0.406) / std (0.229,0.224,0.225)** 정규화. **별도 stain-norm 없음** — 우리 default 파이프라인과 정확히 일치.
- 출력: 패치당 **1024-dim** 벡터. CLAM/ABMIL aggregator 입력으로 직결.

## 파이프라인 fit (BIOP02)
- `agents/embedding/scripts/extract_uni.py` 가 본 recipe를 그대로 구현: tile_wsi.py(256×256@20×, Otsu mask, per-patient cap 5000) → UNI encoder → `outputs/.../features.npy` (N×1024).
- **GPU**: A100 80GB 1장으로 ViT-L 추론은 batch 단위로 충분. HF 승인 대기 중에는 `extract_dummy.py`(torch.randn(N,1024))로 Modeling Agent unblock — dummy도 동일 **1024-dim**이라 교체가 무손실.

## 사전 추출 임베딩 (Pre-extracted features)
- Mahmood Lab가 **TCGA / CPTAC / PANDA 25,000+ WSI embedding**을 `MahmoodLab/UNI2-h-features` 데이터셋으로 공개. 단 이는 **UNI2-h(1536-dim)** 기준 — 원본 UNI(1024-dim)와 dim이 달라 우리 backbone과 직접 호환 안 됨. 빠른 부트스트랩엔 유용하나, BIOP02 default(1024-dim UNI)와 일관성 유지하려면 **자체 추출 권장**.

## 운영 메모
- 버전 혼동 주의: 문서/코드에서 `uni`(1024) vs `UNI2-h`(1536) 명확히 구분. paper-info.yaml은 priority-1 = 1024-dim 원본 UNI 기준.
