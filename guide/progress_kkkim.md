# kkkim 작업 진행 로그

## 2026-05-17 (Sprint 0)

### 완료한 작업

| JIRA | 태스크 | 커밋 |
|---|---|---|
| BIOP02-25 | HF 5종 모델 접근 권한 신청 및 전종 승인 | 13ce19d |
| BIOP02-26 | agents/embedding/setup.sh 작성 및 전 패키지 설치 확인 | e3badf7 |
| BIOP02-28 | agents/embedding/scripts/extract_dummy.py 작성 및 동작 확인 | e3badf7 |

**서버 환경 확인 완료 (BIOP02-25 포함)**
- /workspace/agents/embedding/ 생성
- nvidia-smi: A100 80GB PCIe, CUDA 12.4, 유휴 상태
- df -h: 1.9TB 총 용량, 27GB 사용 중

**HF 모델 승인 현황**
- UNI v1 (MahmoodLab/UNI) ✅
- CONCH (MahmoodLab/CONCH) ✅
- EXAONE Path 2.0 — 공개 모델 ✅
- Virchow2 (paige-ai/Virchow2) ✅
- UNI2-h (MahmoodLab/UNI2-h) ✅
- 상세 내용: guide/hf_model_access.md

**환경 설치 현황 (~/miniconda3)**
- torch 2.6.0+cu124, CUDA=True ✅
- pyvips 3.1.1 ✅
- timm, huggingface_hub, openslide, numpy, PIL ✅
- 주의: pyvips는 torch보다 먼저 import 필요 (libjpeg 충돌 방지)
- 주의: LD_LIBRARY_PATH=~/miniconda3/lib 우선 설정 필요

---

### 미완료 — 내일 할 것

| JIRA | 태스크 | 기한 | 비고 |
|---|---|---|---|
| BIOP02-27 | tile_config.yaml + tile_wsi.py | 5/19 | 다음 작업 |
| — | schemas/hypothesis.schema.json v0.1 | 5/21 | gglee draft 받은 후 진행 |
| — | README.md (agents/embedding/) | BIOP02-26,27,28 완료 후 | 한꺼번에 작성 |

---

### 보류 중

- **GitHub push 대기**: braveji에게 kakyungkim 계정 write 권한 요청 중
  - 로컬 커밋 2개가 push되지 않은 상태 (13ce19d, e3badf7)
  - 권한 받는 즉시: `git push origin main`

---

## 내일 시작하는 법

```bash
# 1. 서버 접속
ssh -p 2202 kkkim@61.109.239.220

# 2. 프로젝트 이동
cd ~/project/BioProject02

# 3. braveji가 권한 줬으면 push 먼저
git push origin main

# 4. 다음 작업 시작 (BIOP02-27)
git checkout -b feat/BIOP02-27-kkkim-tile-wsi

# 5. Claude Code 실행
claude
```
