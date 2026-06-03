# GPU MIG 파티션 정책 — BIOP02-51

**작성:** braveji (ykji) | **작성일:** 2026-06-03  
**근거:** Sprint 0/1 pilot wall-clock 측정 결과 (PILOT_REPORT.md, embedding_batch_runbook.md)

---

## 1. Sprint 1 wall-clock 측정 요약

| 작업 | 측정값 | 비고 |
|---|---|---|
| 1 slide tiling | 5.6 s | CPU, Aperio 40× SVS 1.6GB |
| 1 slide UNI v1 embedding | 125.6 s | A100 80GB full, batch=64, 5000 tiles |
| batch당 시간 | ~1.54 s/batch | 64 tiles/batch |
| **150장 전체 추산** | **~5.5시간** | Paper A 최소 규모 |
| **300장 전체 추산** | **~10.5시간** | 현재 검토 규모 |

UNI v1 (ViT-L/16) VRAM 사용량: 모델 로드 ~1.5 GB + 배치 처리 ~2–3 GB → **실사용 ≈ 4–5 GB**  
(A100 80GB 대비 실제 점유율 < 10%)

---

## 2. A100 80GB MIG 프로파일 옵션

| 옵션 | 구성 | 인스턴스당 메모리 | 동시 사용자 | embedding 속도 (추산) |
|---|---|---|---|---|
| **A** MIG 없음 (현행) | 1× 7g.80gb | 80 GB | 1명 독점 | 125.6 s/slide (기준) |
| **B** 2× 3g.40gb | 2 인스턴스 | 40 GB | 2명 | ~150–160 s/slide |
| **C** 3× 2g.20gb | 3 인스턴스 | 20 GB | 3명 | ~180–210 s/slide |
| **D** 7× 1g.10gb | 7 인스턴스 | 10 GB | 최대 7명 | ~300–400 s/slide |

> MIG compute slice 감소에 따른 속도 저하는 선형보다 완만하지만, 메모리 대역폭 제한이 주요 병목.

---

## 3. 결정 및 근거

### Sprint 1–2 (현재 ~ 2026-06-19): **MIG 없이 full GPU 유지**

**이유:**
1. **embedding이 최우선 병목.** 300장 × 125.6s = 10.5시간. MIG 적용 시 300장 기준 12–17시간으로 증가, Sprint 1 마감(6/05) 및 Sprint 2(6/19)에 영향.
2. **MLP training은 GPU 비의존적.** sjpark의 ER status MLP는 dummy embedding으로 CPU 학습 가능 (`--smoke_test`). 실제 embedding이 완료된 후 전환.
3. **동시 GPU 작업 수요 없음.** Sprint 1에서 GPU 집약 작업은 kkkim embedding 단독.

**운영 방식:**
- kkkim이 3개 연속 슬롯(12시간) 예약 → 300장 일괄 처리
- 슬롯 예약은 `#biop02-alerts`에 최소 24시간 전 공지

### Sprint 3+ (2026-07-03~): **2× 3g.40gb 전환 검토**

**조건:** 아래 조건을 모두 충족할 때 MIG 전환을 재논의한다.
- embedding 전체 완료 (sprint 2 종료 후)
- sjpark + jhans + kkkim이 동시에 GPU를 사용하는 실험이 주 2회 이상 발생
- 각 작업의 VRAM 요구량이 40GB 이하임을 확인

**전환 명령 (참고용, 서버에서 root 실행):**
```bash
# MIG 모드 활성화 (재부팅 또는 프로세스 없을 때)
sudo nvidia-smi -i 0 -mig 1

# 2× 3g.40gb 파티션 생성
sudo nvidia-smi mig -cgi 3g.40gb,3g.40gb -C

# 확인
nvidia-smi -L
```

---

## 4. 슬롯 예약 규칙 업데이트

현행 4시간 슬롯에 아래 규칙을 추가한다.

| 규칙 | 내용 |
|---|---|
| embedding 연속 슬롯 | 최대 3 슬롯(12시간) 연속 예약 허용. 단, 24시간 전 `#biop02-alerts` 공지 필수 |
| MIG 전환 시 | 전체 팀 동의 후 braveji가 서버에서 실행, `#biop02-general` 공지 |
| MIG 해제 시 | 마찬가지로 braveji 실행 + 공지 |

---

## 5. 재검토 시점

- Sprint 2 종료 (2026-06-19) 이후 embedding 완료 여부 확인
- Sprint 3 시작 미팅에서 MIG 전환 여부 최종 결정
