# Cross-cancer 임베딩 — 재접속/이어하기 가이드 (2026-07-11)

> 자율 배치잡. 재접속 시 **① 상태 확인 → ② 중단됐으면 재기동**. idempotent라 완료분은 스킵.

## ① 상태 확인 (복붙)
```bash
cd /home/kkkim/project/BioProject02
echo "폐:  $(ls experiments/crosscancer/LUNG_NSCLC/full/embeddings/*.npy 2>/dev/null|wc -l) / 1053"
echo "대장: $(ls experiments/crosscancer/COLORECTAL/full/embeddings/*.npy 2>/dev/null|wc -l) / 625"
echo "마스터: $(ps -eo cmd|grep 'run_embed.*--cancers'|grep -v grep|wc -l) (2=정상) 워커: $(ps -eo cmd|grep 'worker --cancer'|grep -v grep|wc -l) (10=정상)"
tail -4 experiments/crosscancer/EMBED_HEARTBEAT.log
cat experiments/crosscancer/EMBED_ALL.done 2>/dev/null   # 있으면(그리고 임베딩수=목표면) 전량 완료
```
- **완료 판정:** `EMBED_ALL.done` 존재 **AND** 폐=1053·대장=625 근접. (⚠️ 스모크 때 만든 stale sentinel 가능 → 반드시 임베딩 수로 재확인.)
- 마스터 2·워커 10이면 정상 진행 중 → 그냥 두면 됨.

## ② 중단됐으면 재기동 (idempotent — 완료분 스킵, 손상파일 자동 재처리)
```bash
cd /home/kkkim/project/BioProject02
D=/home/kkkim/miniconda3/bin/python3
S=experiments/crosscancer/run_embed_crosscancer.py
# 혹시 좀비 있으면 먼저: pkill -9 -f 'run_embed_crosscancer.py'  (셸 self-match로 exit1 떠도 무시, 재확인)
setsid nohup $D $S --cancers LUNG_NSCLC  --shards 5 > experiments/crosscancer/full_run_lung.out 2>&1 </dev/null &
setsid nohup $D $S --cancers COLORECTAL --shards 5 > experiments/crosscancer/full_run_crc.out  2>&1 </dev/null &
```

## 설정/튜닝 메모 (재조정 시)
- **워커수 = `--shards N`** (암종당, GPU 0/1/2에 라운드로빈). 현재 **5/암종=10워커**.
- **thread limit OMP=4** (드라이버 내장) — 이거 없으면 워커 다수 임베딩 시 torch 스레드가 코어 전량 점유→load 폭발(실측 load 73). 유지할 것.
- **raw = SSD `/workspace/data/cache/biop02/_crosscancer_raw`** (HDD면 동시 다운로드 seek thrashing→정체. 실측 load 133). per-slide LRU(임베딩 후 즉시 삭제), 순간 점유 ~1GB.
- 튜닝 실측: HDD 18워커=thrash(load133) / SSD 10워커 무제한스레드=thrash(load73) / **SSD 6워커 OMP4=healthy(load5)** / SSD 10워커 OMP4=목표(load~25-30).
- 처리율 실측(6워커): ~2.7 slides/min. 10워커면 ~2배 기대. 사이즈순 정렬이라 후반(대형 슬라이드) 감속.

## 🤖 supervised 자동 체인 (임베딩 후 자동 실행 — 이미 detached 가동 중)

**`run_supervised_chain.py`**(pid는 `ps -eo pid,cmd|grep supervised_chain`)가 **각 암종 임베딩 master 종료를 감지하면(폐/대장 독립) 즉시** 그 암종에 대해:
1. `fetch_labels.py`(cBioPortal 라벨) → 2. `make_split.py`(site-disjoint) → 3. `run_mil_cost.py`(암종별 MIL+cost)
```bash
# 자동체인 상태
tail -6 experiments/crosscancer/SUPERVISED_HEARTBEAT.log
cat experiments/crosscancer/SUPERVISED_DONE.json 2>/dev/null        # 있으면 전체 완료+요약
cat experiments/crosscancer/LUNG_NSCLC/full/mil_cost_results.json 2>/dev/null   # 폐 결과
cat experiments/crosscancer/COLORECTAL/full/mil_cost_results.json 2>/dev/null   # 대장 결과
# 자동체인이 죽었으면 재기동(임베딩 완료 후엔 즉시 라벨→split→MIL):
setsid nohup /home/kkkim/miniconda3/bin/python3 experiments/crosscancer/run_supervised_chain.py > experiments/crosscancer/supervised_chain.out 2>&1 </dev/null &
# MIL만 다시(결과 존재 시 --force): python run_mil_cost.py --cancer LUNG_NSCLC --device cuda:0
```
**결과 해석(advisor 게이트):** 각 endpoint에 `real`·`shuffle_null` AUROC 동반. **histology 양성대조 AUROC≥0.75 = 파이프라인 정상**(H&E가 형태 봄). 변이(EGFR/KRAS/BRAF) `real`이 낮고 `shuffle_null`과 비슷 = **H&E-blind(가설확증)**; `real`도 낮은데 histology도 낮으면 = MIL 고장. cost = 측정vs예측 축라우팅 mis-route×치료거리.
검증(2026-07-11): 라벨 prevalence 게이트 **EGFR 10.2%(보정 후)·KRAS 12.4%·BRAF 9.0% 모두 OK**, split site-disjoint OK, MIL 스모크(val+test 합침) **histology real 0.954[0.90,0.99] vs shuffle 0.473** PASS. cost=버전A(targeted 3축 거리)+버전B(histology 포함 mis-route) 둘 다 산출. 상세결정=`PROGRESS_DECISIONS.md`.

## 완료 후 다음 단계 (수동 확인)
1. 분자 라벨(cBioPortal: 폐 EGFR/ALK/KRAS-G12C·histology, 대장 BRAF-V600E) + manifest 조인 — **BIOP02-95**
2. site-disjoint split 생성·검토 — BIOP02-95
3. MIL 학습(train_mil 재사용)→환자 라우팅 cost→cross-cancer 그림 — **BIOP02-96**
- 세포주 냉동지도·치료거리는 이미 완료(폐 frozen_map.json 0.914 / 대장 0.868).

JIRA: 에픽 **BIOP02-93** > 임베딩 **BIOP02-94**(진행중) / 라벨·split **-95** / MIL·cost **-96**.
