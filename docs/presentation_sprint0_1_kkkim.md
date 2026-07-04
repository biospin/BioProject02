# SpatialPathoAgent — Embedding Agent 작업 발표
**발표자:** Ka-Kyung Kim (kkkim) | **기준일:** 2026-06-05 | **범위:** Sprint 0–1

---

## 1. 내가 맡은 역할

**Embedding Agent** — H&E WSI를 받아 Foundation Model 임베딩 벡터를 뽑아내는 파이프라인 담당

```
H&E WSI (.svs)
    │
    ▼  tile_wsi.py
256×256 타일 좌표 (coords.npy)
    │
    ▼  extract_uni.py / extract_conch.py / extract_exaone.py
임베딩 벡터 (N × D float32 .npy)
    │
    ▼  →  sjpark (Modeling Agent) 입력
```

---

## 2. Sprint 0 작업 요약 (5/12 – 5/22)

### 2-1. Foundation Model 접근 권한 확보 (BIOP02-25)

HuggingFace 5종 동시 신청 → **전종 승인 완료**

| 우선순위 | 모델 | 차원 | 라이선스 |
|---|---|---|---|
| 1 | UNI v1 (`MahmoodLab/UNI`) | 1024 | CC-BY-NC-ND 4.0 |
| 2 | CONCH (`MahmoodLab/CONCH`) | 512 | CC-BY-NC-ND 4.0 |
| 3 | EXAONE Path 2.0 (`LGAI-EXAONE/EXAONE-Path-2.0`) | 768 | EXAONEPath NC |
| 4 | Virchow v1 (`paige-ai/Virchow`) | 1280 | Apache 2.0 |
| 5 | UNI2-h (`MahmoodLab/UNI2-h`) | 1536 | CC-BY-NC-ND 4.0 |

> 기관 이메일 필수 (gmail/naver 불가) — 개인 계정으로 신청 시 거절되는 사례 있음

---

### 2-2. 환경 구축 스크립트 (BIOP02-26)

`agents/embedding/setup.sh` — Ubuntu 22.04, Python 3.10, CUDA 12.4 기준

**설치 순서가 중요:** pyvips(conda-forge) → torch → openslide-python
- libjpeg 버전 충돌 방지를 위해 conda 순서 고정
- 재현 가능한 환경: `bash agents/embedding/setup.sh` 한 줄로 완료

---

### 2-3. WSI Tiling 파이프라인 (BIOP02-27)

`agents/embedding/scripts/tile_wsi.py`

**설정값 (tile_config.yaml):**

| 파라미터 | 값 | 이유 |
|---|---|---|
| tile_size | 256 px | Foundation model 입력 표준 |
| target_mpp | 0.5 μm/px (≈ 20×) | UNI/CONCH 학습 해상도 |
| Otsu tissue threshold | 10% | 배경 타일 제거 |
| per_patient_cap | 5,000 | 메모리·시간 균등화 |
| seed | 42 | 재현성 |

**핵심 버그 수정: MPP Scale 보정**

TCGA-BRCA 슬라이드 상당수가 40× 스캐너 (mpp=0.25)라 단순 읽기 시 해상도 불일치 발생

```python
# tile_wsi.py 핵심 로직
scale = target_mpp / actual_mpp   # 0.5 / 0.25 = 2.0
read_size = int(tile_size * scale)  # 512 px
# 512×512 읽고 256×256으로 리사이즈 → 유효 0.5 μm/px
```

- `coords.json`에 `scale`, `read_size` 기록 → 추출 스크립트가 자동 반영
- 20× / 40× 스캐너 모두 동일 결과 보장

---

### 2-4. Dummy Embedding (BIOP02-28)

`agents/embedding/scripts/extract_dummy.py`

- 목적: Modeling Agent (sjpark) 언블로킹 — 실제 HF 승인 전에도 MLP 학습 가능하게
- 출력: `torch.randn(N, 1024)` float32 → 실제 UNI 임베딩과 동일 shape

---

### 2-5. 1-Slide Pilot 완료 (BIOP02-30)

**파일:** `TCGA-3C-AALI-01Z-00-DX1.svs` (Aperio 40×, 1.6 GB, 101184×74432 px)

| 단계 | 결과 |
|---|---|
| Tiling | 후보 14,198장 → cap 5,000장 / **5.6초** |
| UNI v1 추출 | 5,000×1024 float32 / **125.6초** (A100, batch=64) |
| Dummy 추출 | 5,000×1024 float32 / 0.2초 |

**300장 전체 추산:** ~10시간 / 1010장 전체: ~35시간

---

## 3. Sprint 1 작업 요약 (5/22 – 6/05)

### 3-1. Manifest 생성 & 데이터 준비 (BIOP02-21, 83)

- jamie(Data Agent) manifest 지연 → 직접 착수
- TCGA CDR 임상 데이터 다운로드 및 분석
- **슬라이드 선별 전략:** ER- 전수(228장) + HER2+/ER+ + 나머지 ER+ → **1010장 최종 확정**
- NAS Synology API 다운로드 스크립트 작성 (openslide 유효성 검증 포함)
- 공용 경로 배포: `/workspace/data/cache/biop02/tcga_brca_final_manifest.csv`

---

### 3-2. Split Policy v1 생성 (BIOP02-41)

- Patient-level split (슬라이드 단위 아닌 환자 단위 — 데이터 누수 방지)
- ER- 클래스 소수 문제 → 전수 포함 결정 (JIRA 댓글로 근거 기록)
- 잠금 후 변경 불가: `split_policy_v1.csv` @ `/workspace/data/cache/biop02/`

---

### 3-3. 전체 1010장 Tiling 완료 (BIOP02-37)

```
완료: 1010/1010 (신규 510장 + 기존 skip 500장)
실패: 0장
로그: /home/kkkim/data/logs/tiling_1010.log
```

타일 저장 위치: `/home/kkkim/data/tiles/<slide_name>_coords.npy`

---

### 3-4. 추출 스크립트 3종 완성 (BIOP02-38, 48)

| 스크립트 | 모델 | 출력 차원 |
|---|---|---|
| `extract_uni.py` | UNI v1 | 1024 |
| `extract_conch.py` | CONCH | 512 |
| `extract_exaone.py` | EXAONE Path 2.0 | 768 |

공통 설계:
- `--tag` 기반 실험 디렉토리 자동 생성 (`--tag uni_v1` → `experiments/kkkim/uni_v1/`)
- `coords.json`의 `scale/read_size` 자동 반영 (MPP 보정 투명하게 전달)
- 배치 GPU 처리, tqdm 진행 표시, `.npy` + 메타 `.json` 동시 저장

**현재 상태:** GPU 슬롯 확보 대기 중 (타인 100% 점유) → 해제 즉시 UNI 전체 추출 착수

---

### 3-5. Critic 리뷰: sjpark MLP 결과 (BIOP02-39, 40)

cross-review 규칙: **owner ≠ reviewer** → kkkim이 sjpark 결과 리뷰

**7-point Critic Checklist 결과:**

| 항목 | 결과 | 비고 |
|---|---|---|
| 데이터 누수 | PASS | patient-level split 확인 |
| Baseline 비교 | PASS | random/subtype-only/pixel-mean 3종 |
| Counterfactual | CONDITIONAL | dummy embedding 단계 — 실제 임베딩 후 재확인 필요 |
| Cross-dataset | DEFERRED | DepMap/GDSC 미완 (jhans 담당) |
| 생물학적 타당성 | PASS | ER status → 형태 연관성 선행 연구 있음 |
| DRP 표현 금지 | PASS | "drug response prediction" 없음 |
| Claim-level | PASS | hypothesis_only 명시 |

→ **conditional_pass** — dummy 임베딩 결과이므로 실제 UNI 임베딩 후 재리뷰 조건부

---

### 3-6. 인프라 기여

- **mcp-atlassian 2.1.0 버그 패치** — `BIOP02` 같은 숫자 포함 프로젝트 키 처리 불가 버그
  - regex `^[A-Z]+-[0-9]+$` → `^[A-Z][A-Z0-9]*-[0-9]+$` 수정
  - JIRA MCP 직접 조작 가능해짐
- **Atlassian DNS 우회 절차** 문서화 (서버 DNS 미등록 시 `--resolve` IP 직접 지정)

---

## 4. 시행착오 & 레슨런

| # | 상황 | 내가 한 것 | 결과 / 레슨런 |
|---|---|---|---|
| 1 | HF 모델 접근 신청 | 개인 gmail로 신청 시도 | ❌ 거절 → **기관 이메일 필수**. 5종 동시 신청해서 첫 승인부터 바로 착수. |
| 2 | 환경 설치 | pyvips + openslide-python 동시 conda install | ❌ libjpeg 버전 충돌 → **설치 순서 고정**: pyvips(conda-forge) → torch → openslide |
| 3 | Tiling 해상도 | pilot 전 40× 슬라이드를 단순 읽기로 처리 | ❌ 해상도 2× 불일치 발견 → `scale = target_mpp / actual_mpp` 보정 로직 추가. **pilot 1장 먼저 실행하는 습관 중요** |
| 4 | 보정 전/후 타일 수 | 40× 슬라이드 보정 전 그리드 계산 | 후보 54,350장 → 보정 후 14,198장. 그리드 간격이 2배 넓어지는 것이 정상임을 이해하는 데 시간 소요 |
| 5 | jamie 의존성 블로킹 | manifest 기다리다 파이프라인 전체 멈춤 | ❌ → TCGA CDR 직접 분석해 manifest 대행 생성. **의존성 데드락 시 대행 범위를 미리 팀 합의 필요** |
| 6 | GPU 슬롯 경합 | 임베딩 추출 착수하려니 타인 100% 점유 | ❌ 지연 → **gpu.lock 래퍼 + Slack 슬롯 예약 체계가 없으면 무용지물**. braveji 담당이지만 조기 도입 촉구 필요 |
| 7 | mcp-atlassian 버그 | JIRA API 호출하니 0개 반환 | ❌ 원인 추적 → `BIOP02` 같은 숫자 포함 키 regex 미지원. 직접 패치. **오픈소스 도구는 검증 후 사용** |
| 8 | Atlassian DNS 오류 | curl로 API 호출 시 host resolve 실패 | Cloudflare DoH로 IP 조회 후 `--resolve` 사용. 동작 IP `13.227.180.4` 확인 |

---

## 5. 팀원과의 연결 — 내가 어디에 물려 있나

```
[jamie]  manifest CSV + split_policy_v1
    │  (지연 시 kkkim 대행)
    ▼
[kkkim]  tiling 1010장  ✅ 완료
    │
    ├──→ [sjpark]  dummy embedding으로 MLP 스켈레톤 선착수 (BIOP02-32) ✅
    │        │  실제 UNI 임베딩 완료 후 → sjpark 재학습
    │        ▼
    │    [kkkim]  sjpark 결과 Critic 리뷰 (cross-review 페어링)
    │        │   conditional_pass → 실제 임베딩 후 재리뷰 조건부
    │        ▼
    │    [gglee]  최종 Critic sign-off → #biop02-experiments 공유 가능
    │
    ├──→ [braveji]  experiments/ 표준(--tag 기반), GPU 슬롯 정책 제공
    │               (gpu.lock 래퍼 대기 중 — 내 임베딩 추출 착수 조건)
    │
    └──→ [jhans]  DepMap/GDSC 연계 (BIOP02-52 진행 중)
                  Critic cross-dataset 항목 현재 DEFERRED
```

**핵심 포인트:**
- dummy embedding 먼저 제공 → sjpark가 내 실제 임베딩 기다리지 않고 파이프라인 선 구축
- manifest 대행 생성 → jamie sign-off만 받으면 바로 확정 (블로킹 없이 tiling 착수)
- Critic 페어링: **내가 sjpark 리뷰, jamie가 내 임베딩 결과 리뷰** (자기 리뷰 금지 규칙)

---

## 6. 전체 산출물 목록

| 산출물 | 경로 |
|---|---|
| 환경 스크립트 | `agents/embedding/setup.sh` |
| Tiling 스크립트 | `agents/embedding/scripts/tile_wsi.py` |
| 추출 스크립트 3종 | `agents/embedding/scripts/extract_{uni,conch,exaone}.py` |
| Dummy 추출 | `agents/embedding/scripts/extract_dummy.py` |
| 배치 실행 | `agents/embedding/scripts/run_batch_embedding.py` |
| Manifest 검증 | `agents/embedding/scripts/validate_batch_manifest.py` |
| Tiling 설정 | `agents/embedding/configs/tile_config.yaml` |
| Hypothesis schema | `schemas/hypothesis.schema.json` |
| Pilot 결과 보고서 | `PILOT_REPORT.md` |
| Manifest (공용) | `/workspace/data/cache/biop02/tcga_brca_final_manifest.csv` |
| Split policy v1 (공용) | `/workspace/data/cache/biop02/split_policy_v1.csv` |
| Tile 좌표 1010장 | `/home/kkkim/data/tiles/` |

---

## 7. 의존성 체인에서 내 위치

```
jamie: manifest + split_policy
    └→ [kkkim] tiling 1010장  ✅ 완료
         └→ [kkkim] UNI/CONCH/EXAONE 임베딩 추출  ⏳ GPU 대기
                   └→ sjpark: 실제 임베딩 MLP 학습
                              └→ gglee: 최종 Critic 리뷰
```

---

## 8. 다음 단계

1. GPU 슬롯 확보 → `extract_uni.py --tag uni_v1` 전체 1010장 실행 (~35시간)
2. CONCH / EXAONE Path 2.0 순차 추출 (멀티 모델 비교)
3. sjpark가 실제 임베딩으로 MLP 재학습 → Critic 재리뷰
4. Sprint 2: ER + PR + HER2 + PAM50 멀티 레이블 확장

---

## 참고: 핵심 수치 요약 (발표용)

| 항목 | 수치 |
|---|---|
| 전체 슬라이드 수 | 1,010장 |
| Tiling 완료 | 1,010/1,010 (실패 0) |
| 슬라이드당 타일 수 | 최대 5,000장 (Otsu 조직 마스크 후) |
| Pilot tiling 속도 | 5.6초/슬라이드 |
| UNI v1 추출 속도 | 125.6초/슬라이드 (A100, batch=64) |
| 전체 추출 추산 | ~35시간 (1010장 × 2분) |
| 임베딩 벡터 차원 | 1024 (UNI), 512 (CONCH), 768 (EXAONE) |
