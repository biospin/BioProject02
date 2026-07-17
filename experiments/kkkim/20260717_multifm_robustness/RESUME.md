# 다중 FM 견고성 (Virchow2) — 재개 가이드

**세션이 끊겨도 이 문서만 읽으면 이어서 할 수 있다.** 착수 2026-07-17 · owner kkkim · Paper C · **JIRA BIOP02-101**.

## 0. 지금 뭐가 돌고 있나

```bash
pgrep -fa run_multifm.py          # master 1 + worker 3(GPU 0/1/2)
tail -f experiments/kkkim/20260717_multifm_robustness/master.log
tail experiments/kkkim/20260717_multifm_robustness/MULTIFM_HEARTBEAT.log
```

죽었으면 **그냥 다시 띄우면 된다**(idempotent — 완료 임베딩 자동 스킵):
```bash
cd ~/project/BioProject02/experiments/kkkim/20260717_multifm_robustness
setsid nohup /opt/envs/spatialpatho/bin/python run_multifm.py > master.log 2>&1 < /dev/null &
```

## 1. 목적과 **주장 한계** (중요)

Paper C의 법칙(치환가능성 결정지도)이 **FM을 바꿔도 유지되는가** = 모델 비의존성 검정.
헤드라인은 여전히 **UNI v1(1024-d)**. Virchow2(2560-d)는 견고성 검증용(CLAUDE.md FM 표).

> ⚠️ **이 작업의 산출물은 임베딩까지다.** "법칙이 모델 비의존적이다"는 주장은 **sjpark의 downstream
> CLAM 재학습**(Virchow2 공간에서)이 있어야 성립한다. 임베딩만으로는 아무것도 검정되지 않았다 =
> **미검증**. 임베딩 완료 = sjpark 언블록이지 결과가 아니다.

## 2. 순서 (가치 우선)

| 순 | 코호트 | N | raw | 왜 이 순서 |
|---|---|---|---|---|
| 1 | **BRCA** | 1010 | ✅ 로컬(`~/data/tcga_brca_wsi`) | anchor(Fig2/Fig3의 집). 네트워크 무의존 → 가장 먼저 결과 |
| 2 | **HEADNECK_HNSC** | 472 | GDC 다운로드 | 법칙의 **유일한 powered CONFIRM**(HPV 0.9594) |
| 3 | COLORECTAL | 622 | GDC | |
| 4 | GASTRIC_STAD | 442 | GDC | |
| 5 | LUNG_NSCLC | 1052 | GDC | 최대 → 최후 |

BRCA는 기존 UNI manifest에 **coords 컬럼이 없어** 재타일링이 필요하다(→ `coords_v2/`).

## 3. ⚠️ raw 보관 정책 — CLAUDE.md와 충돌하는 예외

**Leader(kkkim) 결정 2026-07-17: "rawdata 지워도 된다고 해서 지우지 않았나? 프로젝트 끝나기 전까지는 조심해야 할듯."**

- 이 드라이버는 임베딩 후 **raw .svs를 삭제하지 않는다**. (원 드라이버 `run_embed_crosscancer.py`는 LRU 삭제했고, 그래서 cross-cancer raw가 전부 사라져 지금 재다운로드가 필요해졌다.)
- CLAUDE.md `Absolute Prohibitions`의 **`❌ raw WSI 전량 영구 보관`과 충돌** → **프로젝트 기간 한정 예외**로 운용. 논문 종료 시 정리한다.
- 대신 **디스크 가드**: `~/data` 여유 < **300GB**면 **삭제가 아니라 정지** + `DISK_GUARD_TRIPPED` 파일 생성 + 로그. **사람이 판단한다.**

### 디스크 산수 (2026-07-17 실측)
- `~/data` 여유 **3,271 GB**. cross-cancer 2,588장 × TCGA WSI 평균 ~1GB ≈ **2.6TB** → **빠듯하다.**
- 가드가 걸리면 선택지: (a) 완료 코호트의 raw만 선별 삭제(임베딩·coords는 영구) (b) 다른 볼륨 (c) 남은 코호트 포기.
- **가드 발동 시 자동으로 아무것도 지우지 않는다** — 이게 이 설계의 요점.

## 4. 검증된 것 / 안 된 것 (정직 보고)

**실측 검증 완료(2026-07-17):**
- Virchow2 가중치: HF 캐시가 **`.incomplete` 부분파일이었음**(610M) → 재다운로드로 `model.safetensors` 2,525MB 확보. ⚠️ **`du` 크기만 보고 "캐시 완료"로 판단하면 안 된다** — 실제로 이 착각을 했다.
- 추출기 스모크: raw token `(32, 261, 1280)` = CLS 1 + **register 4** + patch 256 → `cat[CLS, mean(patch)]` = **(32, 2560)**, finite, 타일간 상이.
- 드라이버 E2E: BRCA 최소 슬라이드 1장 → `(99, 2560)` finite, **raw 1010장 보존 확인**.

**미검증:**
- 전체 코호트 완주 · GDC 재다운로드 경로(BRCA는 로컬이라 아직 download() 미실행) · 디스크 가드 실제 발동
- **downstream 재학습(sjpark) — 이게 없으면 법칙 주장 불가**

## 5. ⚠️ Virchow2 함정 (다음 사람에게)

`output[:, 1:]`을 평균하면 **register token 4개가 섞여 조용히 틀린 임베딩**이 나온다. patch는 반드시 `output[:, 5:]`. `extract_virchow2.py`의 `N_REGISTER=4` 참조.

## 6. 완료 후 할 일

1. manifest 작성: `embedding_manifest_virchow2.csv` (경로는 `/workspace/...` 절대경로 — CLAUDE.md 공유 규칙)
2. **sjpark에게 JIRA 통지** — Virchow2 공간 CLAM 재학습 요청(= 실제 견고성 검정)
3. UNI vs Virchow2 결정지도 대조 → Paper C 모델 비의존성 섹션
4. 산출물 `claim_level: hypothesis_only` · `critic_status` 필드 유지

## 7. 경로

| | |
|---|---|
| 임베딩 | `/workspace/data/cache/biop02/<cancer>/virchow2/` |
| coords | `/workspace/data/cache/biop02/<cancer>/coords_v2/` |
| raw | BRCA=`~/data/tcga_brca_wsi` · 그 외=`~/data/crosscancer_raw/<cancer>/` |
| 드라이버 | `run_multifm.py` · 추출기 `agents/embedding/scripts/extract_virchow2.py` |
| 로그 | `master.log` · `MULTIFM_HEARTBEAT.log` · `worker_<cancer>_gpu<i>.log` |
| 완료 표식 | `DONE_<cancer>` · `MASTER_DONE` · 중단 표식 `DISK_GUARD_TRIPPED` |
