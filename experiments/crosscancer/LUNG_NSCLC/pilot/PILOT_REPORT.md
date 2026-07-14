# Cross-Cancer Phase 1 GPU Pilot — TCGA-LUAD (Lung NSCLC)

**목표:** BRCA용 WSI→타일→UNI 임베딩 파이프라인이 **타암종(폐) 슬라이드에서 무수정으로 GPU까지 end-to-end 작동**하는지 소수 슬라이드로 실증. 전체 코호트 아님.

**판정: PASS.** 15/15 슬라이드가 다운로드→타일링→UNI 임베딩까지 코드 수정 0으로 통과. 모든 임베딩 shape=(N, 1024), 전량 finite.

## 환경
- GPU: **cuda:0 단독** (`CUDA_VISIBLE_DEVICES=0`), RTX A6000 49GB. GPU 1,2는 미사용.
- UNI v1: 로컬 HF 캐시 재사용 (`models--MahmoodLab--UNI/.../pytorch_model.bin`, offline). **HF 토큰 불필요** — BRCA에서 받은 캐시 그대로 폐에 재사용됨.
- torch 2.6.0+cu124, timm 1.0.27, openslide 1.4.3, Python /home/kkkim/miniconda3.
- 타일 설정: BRCA와 **동일** (`agents/embedding/configs/tile_config.yaml` — 256×256 @ 20×(0.5 mpp), Otsu, cap 5000). 암종별 수정 없음.
- git commit: `17e0ef7`

## 데이터 (GDC REST, open access)
- 소스: GDC API `files` 엔드포인트, filter `cases.project.project_id=TCGA-LUAD ∧ data_format=SVS ∧ data_type="Slide Image" ∧ access=open`, 파일명 `-DX`(진단 슬라이드).
- 가용 진단 슬라이드 58장 중 **최소 용량 15장** 선정(파일럿 바운드). 다운로드 = `/data/<file_id>` REST(gdc-client 대체), **md5 15/15 검증**.
- 다운로드: **15장 / 총 242.3 MB**.

## 결과
- 타일: 슬라이드당 **33–1705개**, 총 **4688개**. (소형 슬라이드 10장 L0≈2500px → 33–68타일; 정규 크기 5장 → 141–1705타일.)
- 임베딩: **15/15 성공**, 전부 `(N, 1024)`, **finite=True 전량**. 총 19.2 MB.
- 임베딩 소요(직렬 합) ≈ 192s (모델 로드 ~6s/슬라이드 포함). 최대 슬라이드(1705 타일) 37s.

| slide (TCGA barcode) | raw MB | tiles | emb shape | finite | tile s | emb s |
|---|--:|--:|---|:--:|--:|--:|
| TCGA-05-4384-01Z-00-DX1 | 10.1 | 68 | (68, 1024) | ✓ | 4.1 | 7.4 |
| TCGA-05-4390-01Z-00-DX1 | 11.2 | 48 | (48, 1024) | ✓ | 2.9 | 7.0 |
| TCGA-05-4410-01Z-00-DX1 | 14.2 | 67 | (67, 1024) | ✓ | 3.7 | 7.3 |
| TCGA-05-4425-01Z-00-DX1 | 6.4 | 33 | (33, 1024) | ✓ | 2.1 | 6.9 |
| TCGA-05-5420-01Z-00-DX1 | 12.1 | 58 | (58, 1024) | ✓ | 3.5 | 7.2 |
| TCGA-05-5423-01Z-00-DX1 | 11.7 | 55 | (55, 1024) | ✓ | 3.4 | 7.1 |
| TCGA-05-5425-01Z-00-DX1 | 9.2 | 45 | (45, 1024) | ✓ | 2.3 | 7.1 |
| TCGA-05-5428-01Z-00-DX1 | 9.0 | 41 | (41, 1024) | ✓ | 2.8 | 7.0 |
| TCGA-05-5429-01Z-00-DX1 | 8.7 | 46 | (46, 1024) | ✓ | 2.9 | 6.9 |
| TCGA-05-5715-01Z-00-DX1 | 8.0 | 57 | (57, 1024) | ✓ | 3.6 | 7.2 |
| TCGA-44-7661-01Z-00-DX1 | 15.1 | 1705 | (1705, 1024) | ✓ | 1.2 | 37.4 |
| TCGA-55-8204-01Z-00-DX1 | 30.3 | 537 | (537, 1024) | ✓ | 2.2 | 19.2 |
| TCGA-55-8207-01Z-00-DX1 | 8.8 | 141 | (141, 1024) | ✓ | 2.7 | 10.0 |
| TCGA-55-8505-01Z-00-DX1 | 37.6 | 662 | (662, 1024) | ✓ | 3.7 | 21.8 |
| TCGA-99-7458-01Z-00-DX1 | 49.9 | 1125 | (1125, 1024) | ✓ | 2.6 | 32.3 |

## 막힌 것 / 우회
- **gdc-client**: pip 미배포(`No matching distribution`). 바이너리 대신 **GDC REST `/data` 직접 다운로드**로 우회 — 정상 작동, md5 검증.
- **GDC API `in` 연산자 버그**: Data Release 45.0에서 `{"op":"in",...}` 필터가 HTTP 500(internal server error) 반환. `{"op":"=",...}` + `and` 조합으로 우회 성공. (재사용 시 주의)
- **HF 토큰/openslide/UNI 캐시**: 막힌 것 없음. 파이프라인 무수정 작동.

## LRU 정책 적용
- raw `.svs` 15장(232 MB) 임베딩 성공 후 삭제. **coords(15) + embeddings(15) 보존.** 크기·md5는 `gdc_manifest.json`에 기록.

## 결론
BRCA 전용으로 작성된 타일링·UNI 추출 코드가 **폐 NSCLC 슬라이드에서 한 줄도 고치지 않고 GPU까지 작동**함을 실증. 파이프라인은 암종 불문(cancer-agnostic)임이 확인됨. 이는 파이프라인 이식성 검증일 뿐 — 폐 코호트 분석/모델링/성능 주장 아님(hypothesis/infra only).
