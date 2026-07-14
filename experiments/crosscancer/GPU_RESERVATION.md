# GPU 예약 — cross-cancer 임베딩 (2026-07-11)

- **예약자:** kkkim (자율 배치잡)
- **GPU:** cuda:0 / 1 / 2 **전부** (3-worker 병렬 임베딩)
- **작업:** cross-cancer FULL 코호트 UNI 임베딩 — 폐(LUAD+LUSC ~1053장) → 대장(COAD+READ ~625장)
- **기간:** 2026-07-11 시작, 예상 wall ~1.5–3일(폐)+~1–2일(대장). GPU 서버 sunset 8/15 전 완료 목표.
- **로그:** experiments/crosscancer/full_run.out, EMBED_HEARTBEAT.log, <cancer>/full/master.log
- **중단 안전:** idempotent(임베딩 존재 시 스킵) — 재실행으로 이어받기 가능.
- ⚠️ 팀원(sjpark/braveji) GPU 필요 시 #biop02-alerts로 조율 요청. worker 1개만 kill하면 해당 shard만 지연(나머지 계속).
