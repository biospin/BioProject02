# HER2 실제 치료결과 앵커 — 재개 가이드 (2026-07-17)

> Paper 구조 결정(`../../research/paperC-positioning/PAPER_STRUCTURE_DECISION_2026-07-17.md`)의 A2/A3/A4.
> 목적: Yale trastuzumab 코호트 H&E → UNI 임베딩 → (frozen phenotype 모델 적용) → **H&E-유래 항HER2 축이 실제 pCR을 층화하는지** 검정(Exp-OUTCOME).

## 데이터 (TCIA HER2-TUMOR-ROIS, 개방 CC BY 4.0)
- **276 slides** = Yale trastuzumab_response 85(★앵커, responder 36/non 49) + Yale HER2 191.
- **다운로드 = PathDB JSON API(headless, Aspera 불필요)** — 방법은 memory `infra-tcia-pathdb-download`. 매니페스트: `yale_download.csv`(url), `yale_manifest.csv`(slide_path).

## 실행
```bash
setsid bash experiments/kkkim/20260717_her2_outcome_anchor/run_outcome_anchor.sh </dev/null >>experiments/kkkim/20260717_her2_outcome_anchor/pipeline.log 2>&1 &
```
- **앵커 우선**: trastuzumab 85 다운로드→임베딩 완주 후 HER2 191. setsid로 세션 끊겨도 생존, 재개가능(파일 존재 시 skip). 완료 sentinel `YALE_PIPELINE_DONE.json`.
- 출력 임베딩: `/workspace/data/cache/biop02/yale/uni_v1/<id>_uni_embeddings.npy`, manifest `.../yale/embedding_manifest_yale_uni.csv`. 타일 규격=프로젝트 표준(256×256@20×/0.5mpp, Otsu, cap 5000, UNI 1024d).
- env=`/opt/envs/spatialpatho/bin/python`(conda run 아님 — detached 셸에 conda PATH 없음).
- 로그 확인: `tail -f .../pipeline.log`. 진행: `ls /workspace/data/cache/biop02/yale/uni_v1/*_uni_embeddings.npy | wc -l`.

## 다음 (임베딩 후 — A3/A4)
- **A3(sjpark):** frozen phenotype 모델(TCGA 학습 `experiments/sjpark/*_clam_uni_v2/`)을 Yale 임베딩에 적용 → 항HER2 축 점수. **Yale 미세조정 금지.**
- **A4(jhans):** 축 점수 → pCR 층화. Primary=AUROC+bootstrap 95%CI(2000, 환자단위). **★검정 정밀화(Farahmand 심층분석):** 성공=frozen-transfer AUROC가 **Farahmand trastuzumab CV AUC 0.80[CI 0.69–0.88]에 근접/겹침**(그들=in-cohort CV천장, 우리=out-of-cohort로 더 어려움). 진짜 신호검정=**DeLong vs HER2-확률 baseline**(코호트 전부 HER2+). 사전등록 반증조건: 축 AUC CI가 0.5 포함 OR HER2-prob baseline 미상회 → 음성보고. 설계정본=`../../research/therapeutic_layer_strengthening.md` §A Exp-OUTCOME + `../../research/phenotype-prediction/farahmand-2022-modpathol/*_methodology-brief.md`.
- claim_level=hypothesis_only, 코호트수준 층화(개인 benefit 아님), power gate 후 본문 승격.

## 런타임 파일(gitignore)
`pipeline.log`·`YALE_PIPELINE_DONE.json`·`_man_*.csv`·`_out_*.csv`·`coords/`·임베딩(/workspace)은 커밋 안 함. tracked=스크립트·매니페스트·이 문서.

## 발견한 버그(수정됨, 재발방지)
1. wget 타임아웃 부재→무인 hang. `--timeout=120 --tries=5 --waitretry=15 --read-timeout=180` 추가.
2. `local coh="$1" man="...${coh}..."` 같은줄 자기참조→`set -u`서 unbound var로 임베딩 단계 사망(다운로드는 됐는데 임베딩 0). local 선언 분리.
3. python csv.writer `\r\n`→bash read가 파일명에 `\r` 부착→openslide "missing". CSV는 unix 줄바꿈.
