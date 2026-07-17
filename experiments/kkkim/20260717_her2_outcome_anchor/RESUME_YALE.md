# Yale HER2 앵커 — 재개 가이드 (2026-07-17)

> Paper 구조 결정(`../../research/paperC-positioning/PAPER_STRUCTURE_DECISION_2026-07-17.md`)의 A2/A3/A4 실행.
> 목표: Yale trastuzumab 코호트 H&E → UNI 임베딩 → (frozen phenotype 모델 적용) → 항HER2 축이 실제 pCR을 층화하는지 검정(Exp-OUTCOME).

## 데이터 (TCIA HER2-TUMOR-ROIS, 개방 CC BY 4.0, ~40GB)
- **273 subjects**: Yale HER2 192(HER2+ 93/HER2- 99) + **Yale trastuzumab-response 85(responder 36 / non 49)** + TCGA HER2 182.
- **앵커의 핵심 = Yale 85 trastuzumab 케이스**(실제 치료결과 라벨 보유). TCGA 182는 우리 BRCA 코호트와 중복 가능·치료결과 없음 → 앵커엔 불필요.
- 포맷: SVS(WSI) + XML(ROI). 임상 라벨: XLSX(~15KB, "Follow-Up/Molecular Test/Measurement" = responder/non-responder).
- 컬렉션 페이지: https://www.cancerimagingarchive.net/collection/her2-tumor-rois/

## ⚠️ 다운로드 블로커 (headless 미해결)
TCIA 이 컬렉션은 **IBM Aspera Connect(브라우저 플러그인)** 또는 **PathDB**로만 받게 돼 있음. 이 서버엔 **aspera CLI 없음**, NBIA REST API는 pathology 미지원(빈 응답), PathDB 직접 URL 미검증. → **무단 headless 다운로드 불가**(억지로 띄우면 깨진 잡). 아래 옵션 중 택1로 언블록 필요:

| 옵션 | 방법 | 난이도 |
|---|---|---|
| **A. aspera-cli 설치 + faspex 토큰** | IBM Aspera `ascp` 설치 후, TCIA 컬렉션의 faspex 다운로드 링크/토큰(브라우저에서 1회 취득)으로 ascp 전송 | 중 (토큰 취득에 브라우저 1회) |
| **B. 로컬 PC에서 Aspera로 받아 서버 업로드** | 브라우저 Aspera로 로컬 다운로드 → `scp`/rsync로 `~/data/yale_raw/` | 하 (확실) |
| **C. PathDB API 역설계** | pathdb.cancerimagingarchive.net 컬렉션 node 찾아 SVS 직접 URL 확보 | 상 (미검증) |

**권장 = 옵션 B**(가장 확실). 로컬에서 Yale SVS 받아 서버 `~/data/yale_raw/`로 올리면 아래 파이프라인 즉시 실행.

## 파이프라인 (WSI 도착 후, GPU 서버에서 즉시)
1. `~/data/yale_raw/`에 SVS 배치.
2. `yale_manifest.csv` 생성 — 컬럼 `slide_path`(+ 선택 `slide_id`,`case_id`). 예:
   ```
   slide_path,slide_id,case_id
   /home/kkkim/data/yale_raw/xxx.svs,xxx,<case>
   ```
   (Yale 85 trastuzumab 케이스만 우선. 임상 XLSX의 case↔responder 매핑으로 case_id 맞춤.)
3. **detached 실행:** `bash experiments/kkkim/20260717_yale_anchor/run_yale_embed.sh`
   - setsid로 SSH 끊겨도 생존. 재개 가능(파일 존재 시 skip). 완료 시 `YALE_EMBED_DONE.json`.
   - 출력 임베딩: `/workspace/data/cache/biop02/yale/uni_v1/`, manifest `embedding_manifest_yale_uni.csv`.
   - 타일 규격 = 프로젝트 표준(256×256 @ 20×/0.5mpp, Otsu, per-slide cap 5000, UNI 1024-d).
4. GPU 예약: 실행 전 `#biop02-alerts`에 인덱스 예약(현재 3장 유휴).

## 다음 (임베딩 후 — A3/A4)
- **A3(sjpark):** frozen phenotype 모델(TCGA 학습, `experiments/sjpark/*_clam_uni_v2/`)을 Yale 임베딩에 적용 → 항HER2 축 점수(HER2 확률). **Yale 미세조정 금지**(frozen).
- **A4(jhans):** 축 점수 → 실제 pCR 층화. Primary = AUROC + bootstrap 95% CI(2000, 환자단위). Baseline = 예측 HER2 확률 단독(DeLong). **반증조건(사전등록):** 축 AUC 95% CI가 0.5 포함 OR HER2-prob baseline 미상회 → 치료층은 phenotype 이상 정보 없음(음성보고). 설계 정본 = `../../research/therapeutic_layer_strengthening.md` Exp-OUTCOME.
- claim_level=hypothesis_only, 코호트수준 층화(개인 benefit 아님).

## 현재 상태
- ✅ GPU 3장 유휴 · spatialpatho env(torch 2.6+cu124, cuda 3dev) · 디스크(~/data 3.1T, /workspace 214G) 확인.
- ✅ 출력/스테이징 디렉토리 생성 · 검증된 런처(`run_yale_embed.sh`) 준비.
- ⏸ **WSI 다운로드 대기**(위 옵션 택1). 그 외 GPU-side 준비 완료.
