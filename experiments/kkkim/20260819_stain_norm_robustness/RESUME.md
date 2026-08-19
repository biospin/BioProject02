# 염색정규화 강건성 (BIOP02-147) — 재개 노트

착수 2026-08-19 · owner kkkim · Paper C/A · GPU 반납 전 완료 목표(8/28).

## 목적
Methods M2 한계("H&E 염색정규화 미적용")에 대한 강건성. 리뷰어 반박("결과가 스캐너/염색 아티팩트 아니냐") 방어.
**경로 A(BRCA 앵커)** — 교차암 raw 소실로 헤드라인(HPV·폐) 불가, BRCA raw(1010장)만 present. HER2 음성앵커(0.599)·ER(0.901)·PAM50이 염색정규화 후에도 보존되는지 검정.

## 실측·주의
- **coords는 short-name**(`TCGA-3C-AALI-01Z-00-DX1_coords.json`), raw/임베딩은 **long-name(해시 포함)**. 혼동 주의(스모크 1차 실패 원인).
- coords 1010개, raw 1010/1010 매칭 확인. `~/data/tiles/*_coords.{npy,json}`.
- 스모크 통과: 128타일 shape (128,1024) finite, Macenko fail 0/128, ~0.18s/타일.
- torchstain 1.3.0 설치(spatialpatho env). reference = `reference_tile.png`(TCGA-3C-AALI tile_idx 3024, 조직밀도 상위1/3 고정).

## 실행 상태
- 3-GPU 샤드 백그라운드 착수(2026-08-19 18:14): shard0/1/2 → GPU0/1/2, 337+337+336.
- 출력: `~/data/embeddings/biop02/tcga/uni_stainnorm_v1/*_uni_stainnorm_embeddings.npy`
- 로그: `queue_shard{0,1,2}.log`, 완료표시 `queue_shard{N}.status`. 재개 시 기존 skip.
- 예상 ~17-20h(3-GPU). ⚠️ **이 출력도 백업 대상 신규 임베딩**(BIOP02-146).

## 추출 완료 후 (다음 단계)
1. CLAM 재학습: ER/HER2/PAM50, **split_policy_v0 folds 동일**(hash 5995f29d3978b831). 모델링 스크립트 확인 필요.
2. 정규화 전(baseline `/workspace/.../uni_v1`) vs 후(stainnorm) AUROC 대조표.
3. 판정: HER2 near-chance 보존(=앵커 염색 강건) · ER 고성능 보존(=파이프라인 유효).
4. 5-artifact + critic_status(Owner≠Reviewer 서명) + metrics.json commit_hash.

## 재개 명령
```bash
PY=/opt/envs/spatialpatho/bin/python
for s in 0 1 2; do setsid $PY run_stainnorm_queue.py --shard $s --nshards 3 --device cuda:$s > shard${s}.out 2>&1 & done
```
