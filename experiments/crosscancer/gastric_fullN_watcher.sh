#!/bin/bash
# STAD 임베딩 442 완료 시 위암 MIL을 전체 N으로 재실행(낡은 337장 결과 갱신) + LAW_TEST 재생성.
# 체인(sh_chain)은 mil_cost_results.json 존재 시 skip하므로, 여기서 먼저 fresh full-N 결과를 만든다.
CC=/home/kkkim/project/BioProject02/experiments/crosscancer
LOG=$CC/GASTRIC_FULLN_WATCHER.log
PY=/home/kkkim/miniconda3/bin/python3
n0=$(ls $CC/GASTRIC_STAD/full/embeddings/*_uni_embeddings.npy 2>/dev/null|wc -l)
echo "[$(date '+%F %T')] armed: STAD 442 대기 (gastric full-N MIL). 현재 $n0/442" >> $LOG
while true; do
  n=$(ls $CC/GASTRIC_STAD/full/embeddings/*_uni_embeddings.npy 2>/dev/null|wc -l)
  if [ -f "$CC/GASTRIC_STAD/full/CANCER.done" ] || [ "$n" -ge 442 ]; then
    echo "[$(date '+%F %T')] STAD 완료(emb=$n). 90초 후 gastric full-N MIL(재배치·마스터전환 여유)." >> $LOG
    sleep 90
    # 낡은 결과 백업 후 재실행
    cp $CC/GASTRIC_STAD/full/mil_cost_results.json $CC/GASTRIC_STAD/full/mil_cost_results.partial337.json 2>/dev/null
    echo "[$(date '+%F %T')] RUN sh_mil_cost GASTRIC_STAD full-N on cuda:0" >> $LOG
    cd $CC && $PY sh_mil_cost.py --cancer GASTRIC_STAD --device cuda:0 >> $LOG 2>&1
    rc=$?
    echo "[$(date '+%F %T')] mil rc=$rc" >> $LOG
    $PY -c "import sys; sys.path.insert(0,'$CC'); import sh_chain; sh_chain.gen_law_test('GASTRIC_STAD'); print('LAW_TEST regenerated (full-N)')" >> $LOG 2>&1
    echo "[$(date '+%F %T')] gastric full-N held-out 완료. mil_cost_results.json + LAW_TEST.md 갱신됨. watcher 종료." >> $LOG
    break
  fi
  sleep 120
done
