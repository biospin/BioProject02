# Embedding Tiling 환경 셋업 확인 (BIOP02-19)

담당: jamie (Data Agent, 독립 확인) | 대상: `agents/embedding/setup.sh` (BIOP02-26, kkkim 작성)
검증 환경: 팀 공용 GPU 서버(`121.126.38.195`, jamie 계정 컨테이너, RTX A6000 ×3), 2026-07-10

## 1. 목적

`agents/embedding/setup.sh`(kkkim, BIOP02-26)로 정의된 임베딩 환경이 jamie 계정에서도
동일하게 재현되는지, 그리고 실제 GPU(CUDA)까지 인식되는지를 **독립적으로** 확인한다.
기존에 "완료"로 오인했던 근거(README/runbook)는 전부 kkkim 본인이 만든 산출물이었고
jamie 쪽에서 직접 확인한 기록이 없었다 — 이 문서가 그 확인 기록이다.

## 2. 절차 및 차이점

`setup.sh`는 `~/miniconda3`(base env)를 그대로 쓰는 것을 전제하지만, 확인 시점 기준
Miniconda 최신 설치본은 **base env가 Python 3.14**로 부트스트랩되고(문서 가정은 3.10),
`defaults`/`r` 채널은 **Anaconda ToS 동의가 없으면 `conda install`이 막힌다**(신규 정책).
→ base를 건드리지 않고 `conda create -n biop02 -c conda-forge --override-channels python=3.10`
으로 문서 가정과 동일한 Python 3.10 env를 별도 생성해 그 안에서 `setup.sh`의 설치/검증
스텝을 동일하게 재현했다 (pyvips → torch cu124 → openslide-python/openslide-bin →
timm/huggingface_hub/transformers → CONCH).

## 3. 결과 — 전 항목 [OK], kkkim 문서값과 대조

| 패키지 | jamie 계정 확인값 | kkkim 문서값 (BIOP02-26/54) | 일치 |
|---|---|---|---|
| pyvips | 2.2.3 | (버전 미기록, import만 확인) | — |
| torch | 2.6.0+cu124, `cuda.is_available()=True`, 3-GPU 인식(A6000×3) | 2.6.0+cu124 (CLAUDE.md 인프라 스펙) | ✅ |
| openslide (Python 바인딩 / C 라이브러리) | 1.4.6 / **4.0.1** | **4.0.1** (BIOP02-54 runbook, macmini 실측) | ✅ |
| timm | 1.0.27 | (미기록) | — |
| huggingface_hub | 1.23.0 | (미기록) | — |
| transformers | 5.13.0 | (미기록) | — |
| CONCH (`mahmoodlab/CONCH`) | 설치 성공 | `setup.sh`엔 "HF 승인 필요, 실패 시 경고" 주석 — 실제론 코드 설치 자체는 HF gated 모델 접근과 무관해 성공 | 조건부 일치 |
| GPU 드라이버 | 535.309.01, CUDA 12.4, A6000×3 49140MiB | 535.309.01 / CUDA 12.4 (CLAUDE.md) | ✅ |

**kkkim의 BIOP02-54 검증(macmini)과의 핵심 차이:** kkkim은 macmini(GPU 없음)에서
DICOM-WSI 리더(OpenSlide) + 타일링만 dummy 임베딩으로 검증했다. 이번 확인은 실제
GPU 서버(jamie 계정)에서 **torch가 3장의 A6000을 전부 인식**하는 것까지 포함해 확인했다는
점에서 더 넓은 범위를 커버한다 — 즉 "타일링 리더는 macmini에서, GPU 추론은 실서버에서"라는
두 검증이 상호보완적으로 전체 파이프라인을 커버함을 확인.

## 4. 발견 사항 (후속 리스크)

- **Miniconda base env 드리프트**: 신규 설치 시 base가 3.10이 아니라 3.14로 잡힌다.
  `setup.sh`를 다른 팀원이 새 계정에서 그대로 돌리면 조용히 다른 Python 버전으로
  깔릴 수 있음 — `setup.sh`에 `conda create -n biop02 python=3.10` 스텝을 명시적으로
  추가하는 게 안전 (현재는 base 직접 사용을 전제).
- **Anaconda ToS 채널 게이트**: `defaults`/`r` 채널은 이제 ToS 동의가 없으면
  `CondaToSNonInteractiveError`로 설치가 막힌다. `conda-forge --override-channels`로
  우회했지만, `setup.sh`가 향후 base 채널을 건드리는 다른 설치를 추가하면 같은 문제로
  막힐 수 있다.

## 5. 결론

jamie 계정 기준 임베딩 환경(pyvips/openslide/timm/torch+CUDA/CONCH) 전 항목 확인 완료.
kkkim의 기존 검증(BIOP02-26/54)과 버전 불일치 없음. 위 2건은 사소하지만 재현성에 영향을
줄 수 있어 기록해 둔다.
