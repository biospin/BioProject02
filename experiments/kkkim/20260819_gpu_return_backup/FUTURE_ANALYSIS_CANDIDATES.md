# 추가 분석 후보 — GPU 반납 전/후 (BIOP02-146 연계)

> 작성 2026-08-19 (kkkim). 리뷰어 대비·논문 강화용 분석 후보 목록. GPU 반납(8월 마지막주) 기준으로 "지금 아니면 못 함"과 "다음 시즌(RunPod)" 구분.
> 원칙: 사전등록 확증 규칙은 사후 이동 금지 — 아래는 전부 **강건성/보강** 분석이지 판정기준 변경 아님.

## 채택 — 지금 진행 (BIOP02-147)

### 🥇 염색정규화 강건성
- **동기**: Methods M2가 "H&E 염색 정규화 미적용"을 한계로 명시. 리뷰어 반박("site-교란·HPV 확증이 스캐너/염색 아티팩트 아니냐") 정면 방어.
- ⚠️ **raw 제약 (2026-08-19 실측)**: 교차암 raw WSI 전량 소실(두경부·폐 `.svs` 0장, LRU 삭제분). **BRCA raw만 present(1010장)**, Yale 276장.
  - **경로 A (실행 가능·raw 있음)**: **BRCA 앵커** 염색정규화 — ER(0.901)·HER2(0.599 음성앵커)·PAM50 재추출·재평가. "앵커 음성이 염색 강건" = 헤드라인 주장(H&E가 HER2 대체 불가) 방어. Paper A(BRCA-only)에도 직결.
  - **경로 B (deferred)**: 헤드라인 교차암(HPV 두경부·폐 histology V=1.000) 염색정규화 — **raw 0.7–2TB 재다운로드 선행** → 8/28 전 + 백업 병행 비현실적 → **RunPod 다음 시즌**(어차피 재다운로드·재추출 시 함께).

## 후보 — 다음 시즌(RunPod) 또는 여력 시

### 🥈 shuffle-null 시드 확대 (5 → 20+)
- **동기**: M8이 "n_null=5 임계 불안정"을 한계로 명시(egfr_amp 허위 PASS 위험, HPV Virchow2 빠듯 FAIL 0.9199<0.9234). 시드 늘리면 confirm/reject 확정력↑.
- GPU 비용: 셔플 모델 재학습(임베딩 재사용 가능 → raw 재다운로드 불필요). **임베딩만 백업돼 있으면 RunPod에서 가능**.

### 🥉 Prov-GigaPath 4번째 FM
- **동기**: 승인됨(2026-07-12), 미실행. 모델 비의존성 근거 확장(현재 UNI/Virchow2/UNI2-h 3종).
- GPU 비용: 신규 FM 임베딩 추출 → raw 필요(교차암은 재다운로드). 스코프·백업부담↑ → 우선순위 낮음.

### 🥉 헤드라인 교차암 염색정규화 (= 경로 B 위)

## 비-GPU 마무리 백로그 (반납과 무관, 언제든)
- **인용 확정(하드 게이트)**: 참고문헌 5~7개(Coudray/Kather/Naik/Dawood/Fernandez-Romero/Klein/Farahmand) 리스트·DOI 확정 → `verify_citations.py` 기계검증. ⚠️ Dawood 연도 불일치(draft 2024 ↔ 134/144 논의 2026) 통일.
- **Table 1 코호트특성** — 5암종 n·유병률·split(매니페스트에서 생성). 유일하게 진짜 빠진 표.
- **operating-point 본문 반영** — 분석은 완료(`20260804_operating_point/`), R1 각주·Discussion에 미반영.
- **그림 라벨 정합** — 드래프트 "(예정)" 표기가 낡음(Fig1–5 실제 존재).
- **EN parity** — `manuscript_parity_ko_en.py`(국문 확정 후).
- **보고표준 체크리스트** — TRIPOD+AI·CLAIM 매핑표(Supplement).

## GPU 의존·타인 대기 (서버 살아있을 때)
- **BIOP02-123 Phase 2** (sjpark, GPU) — site 감사 Phase 2 → R1 각주·Discussion 갱신, 122 #1-강등 판정.
- **BIOP02-101/97** (braveji, GPU) — 다중FM Critic 최종 사인오프 → R5/SFig1 확정.
