# BIOP02 GPU 환경 — 공용 자원 안내 (canonical)

**작성:** kkkim | **작성일:** 2026-07-11 | **근거:** 크로스암종 임베딩·MIL 파이프라인 실측(현재 이 env로 가동 중)
**용도:** BIOP01쪽 공용 GPU env 가이드/Confluence stub([TODO — BIOP02 env])에 채울 canonical 소스. 팀 공용 자원 안내.

> ⚠️ **BIOP01과 한 env로 합치지 말 것(권장).** 근거는 §3. 공용 GPU 예절(슬롯 예약)만 공유.

---

## 1. 환경 스펙 (실측, GPU 작동 검증)

| 항목 | 값 |
|---|---|
| **conda env** | **`spatialpatho`** (BIOP02 전용 격리 env, 2026-07-11 클린 생성·검증) |
| **경로** | `/home/kkkim/miniconda3/envs/spatialpatho` |
| **활성화** | `conda activate spatialpatho` (또는 `/home/kkkim/miniconda3/envs/spatialpatho/bin/python`) |
| **Python** | 3.13.13 |
| **GPU** | RTX A6000 49GB × 3 |
| **드라이버 / CUDA / cuDNN** | 535.309.01 / **12.4** / 9.1.0 |
| **torch / torchvision** | **2.6.0+cu124 / 0.21.0+cu124** (`torch.cuda.is_available()=True`, 3 devices) |

> 재현(클린 설치):
> ```bash
> conda create -n spatialpatho python=3.13 -y && conda activate spatialpatho
> pip install torch==2.6.0+cu124 torchvision==0.21.0+cu124 --index-url https://download.pytorch.org/whl/cu124
> pip install timm==1.0.27 openslide-python==1.4.3 openslide-bin huggingface_hub==1.15.0 transformers==5.12.1 \
>             scikit-learn==1.9.0 pandas==2.2.3 scipy==1.18.0 pillow==12.2.0 opencv-python-headless==4.11.0.86 einops==0.8.2 safetensors==0.7.0 matplotlib
> ```
> ⚠️ 설치 함정: **openslide-python은 C 라이브러리 필요** → `openslide-bin`(번들 휠) 같이 설치(LD_LIBRARY_PATH 불필요). opencv는 4자리 버전 `opencv-python-headless==4.11.0.86`(서버=headless).

## 2. BIOP02 전용 GPU/DL 의존 (핵심 패키지, 정확 버전)

```text
torch==2.6.0+cu124        # 임베딩(UNI/CONCH forward) + MIL(CLAM/attention) 학습
torchvision==0.21.0+cu124
timm==1.0.27              # 파운데이션 모델(UNI ViT-L/16 등) 로드
openslide-python==1.4.3 + openslide-bin   # WSI 타일링 (C라이브러리 번들, pyvips 미사용)
huggingface_hub==1.15.0   # gated 가중치(UNI/CONCH, HF 승인 필요)
transformers==5.12.1
safetensors==0.7.0
einops==0.8.2
scikit-learn==1.9.0       # AUROC·평가 지표
numpy==2.4.4  pandas==2.2.3  scipy==1.18.0  matplotlib  pillow==12.2.0  opencv-python-headless==4.11.0.86  (+pyzipper: AES zip 해제 시)
```
- gated 모델 접근: `guide/hf_model_access.md` 참조(기관 이메일로 Mahmood Lab 승인).
- 설치 스크립트 `agents/embedding/setup.sh` 존재하나 **헤더가 Python 3.10/A100로 구버전** → 위 실측(3.13/A6000/cu124) 기준으로 갱신 필요(별도 태스크).

## 3. ⚠️ BIOP01 env 병합 비권장 (충돌 위험)

| | BIOP02 | BIOP01(RNA velocity) |
|---|---|---|
| torch | **cu124** (순수 torch) | **cu121** 빌드 |
| 프레임워크 | torch만 | **tf-keras 2.15.1**(CRAK-Velo가 `TF_USE_LEGACY_KERAS` 강제) + torch |
| 핵심 패키지 | timm·openslide·HF gated | scvelo·MoFlow·CRAK-Velo·cisTopic |

→ 한 env에서 cu121/cu124 + TF/torch 혼재는 깨지기 쉬움. **프로젝트별 env 분리 유지**가 안전.
서버엔 이미 별도 `torch` named env(`~/miniconda3/envs/torch`, `/opt/envs/torch`)도 있음(base와 별개).

## 4. 공용 GPU 예절 (BIOP01/02 공통 — 이건 공유)

- A6000 3장(`cuda:0/1/2`) 공용. **사용 전 `#biop02-alerts`에 GPU 인덱스 예약**(gpu.lock wrapper 준비 전까지).
- 장시간 임베딩은 슬롯 예약(참고: `guide/gpu_mig_policy.md`, `experiments/crosscancer/GPU_RESERVATION.md`).
- 자율 배치잡은 idempotent·per-slide LRU로 중단/재개 안전하게 설계(예: 크로스암종 임베딩 드라이버).

---
관련: `guide/gpu_mig_policy.md`(MIG 정책) · `guide/hf_model_access.md`(gated 모델) · `agents/embedding/setup.sh`(설치, 구버전 헤더).
