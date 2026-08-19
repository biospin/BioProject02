# 임베딩·가중치 백업 인벤토리 — GPU 반납 대비 (BIOP02-146)

> 작성 2026-08-19 (kkkim, Embedding Agent). GPU 렌탈 서버(121.126.38.195)는 **8월 마지막 주 반납** — 목표 백업완료 8/28(금).
> ⚠️ **`/workspace`도 반납되는 그 서버 위에 있다.** "/workspace에 백업"은 서버가 사라지면 같이 사라진다. **진짜 백업 = 서버 밖**(git = 코드·manifest / 외부 저장소 = 임베딩·가중치).
> 상태: **아직 서버 밖으로 옮긴 임베딩 0** — 목적지 결정 대기(BIOP02-146 댓글). 이 문서는 무엇을·얼마나 옮겨야 하는지의 정본 목록.

## 1. 실측 처리량 (병목 판정)

- HDD(`sdb1`, 회전식) 순차읽기 = **127 MB/s** → 고유 ~300GB 읽기 **약 0.6시간**(읽기는 병목 아님).
- **병목 = 업로드(egress).** 서버 egress 도달 확인(github 200 / s3 307)이나 **전송 속도 미측정**(목적지 확정 후 2GB 실측 필요).
- 전송 수단 **미설치**(rclone/gdrive/gsutil/aws 없음), NAS **미마운트** — 목적지 결정 후 rclone 설치(바이너리)로 진행.

## 2. 고유 임베딩 인벤토리 (중복 제거 실측)

| 우선 | 위치 | 크기 | npy | 내용 | 재계산 비용 |
|---|---|---|---|---|---|
| 🥇 | `~/data/multifm_archive/brca/{virchow2,uni2h}` | **71G** | 2020 | 다중FM BRCA(1010×2) **유일본** | 최고(다중FM 재추출) |
| 🥇 | `/workspace/.../lung_nsclc` | 72G | 3156 | 폐 교차암(다FM) | 최고(폐 코호트 大) |
| 🥇 | `/workspace/.../colorectal` | 37G | 1875 | 대장 교차암 | 高 |
| 🥇 | `/workspace/.../headneck_hnsc` | 34G | 1416 | 두경부 교차암(HPV 헤드라인) | 高 |
| 🥇 | `/workspace/.../gastric_stad` | 28G | 1326 | 위 교차암 | 高 |
| 🥈 | `/workspace/.../uni_v1` | 18G | 1010 | BRCA UNI 헤드라인 | 中 |
| 🥈 | `~/data/embeddings/biop02/tcga/conch_v1` | 8.9G | 1010 | CONCH BRCA **유일본**(/workspace에 없음) | 中 |
| 🥉 | `/workspace/.../cptac_uni_v1` | 7.8G | 653 | CPTAC 외부검증 | 中 |
| 🥉 | `/workspace/.../yale` | 2.7G | 552 | Yale pCR 앵커 | 中 |
| — | `/workspace/.../crosscancer` | 43G | 2588 | ⚠️ 위 코호트와 중복 여부 미확정 — 전송 전 대조 | — |
| ✂️ 제외 | `~/data/embeddings/biop02/tcga/uni_v1` | 18G | 1010 | **/workspace/uni_v1과 완전중복** | — |
| ✂️ 제외 | `~/data/.../exaone_v2` | 8M | 0 | 빈 폴더(EXAONE는 slide-level 블로커) | — |

**고유 백업 총량 ≈ 280–320G**(crosscancer 43G 중복 확정 시 감소). raw `.svs`(tcga 975G·yale 37G)는 **백업 안 함 — 재다운로드**(§3).

## 3. 모델 가중치 (소형 — git/드라이브 즉시 가능)

- sjpark CLAM 체크포인트 `/workspace/agents/modeling/experiments/sjpark/*/model.pt` — 개당 2.6–7.1M, **총 <100M**. 서버에만 존재.
- 조치: 전량 외부 백업(용량 작아 git-LFS 또는 드라이브 즉시). 담당=sjpark(소유자)에게 리마인드, 없으면 kkkim이 스테이징.

## 4. 상태·다음 단계

- [x] 인벤토리·처리량 실측 (이 문서)
- [x] 데이터셋 재다운로드 인덱스 = [DATASET_DOWNLOAD_INDEX.md](../../../agents/data/manifests/DATASET_DOWNLOAD_INDEX.md)
- [ ] **목적지 결정**(BIOP02-146) — 클라우드(rclone) / 외장(이건규 도움) / 재추출 수용 중 택
- [ ] 목적지 확정 후: 2GB 업로드 실측 → 전송시간 산정 → 우선순위대로 전송 → **sha256 대조**
- [ ] GPU 의존 잔여작업(§ 아래)을 서버 살아있을 때 완료

## 5. 서버와 함께 사라지는 GPU 의존 작업 (지금 아니면 못 함)

- **BIOP02-101/97** braveji 다중FM Critic 사인오프 — `/workspace` GPU 재계산 대기(#75 오늘 "GPU 작업 대기 중"). 서버 반납 후 재계산 불가.
- **BIOP02-123 Phase 2** (sjpark, GPU) — 122 #1-강등 판정 게이트.
- **fig3_axis_cost** `caution_remediated_pending_signoff` → braveji 서명(#11916).
- gglee 컨테이너 전용: UCEC MSI 결과 JSON(0.6236/0.6710)·HPV site Cramér's V 원자료(초록 각주 0.378 ↔ 커밋 실측 0.397 드리프트, #144) — 컨테이너와 함께 소멸하므로 main 커밋 필요.
