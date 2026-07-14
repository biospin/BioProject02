# Critic G2 — 재검토 (remediation 검증)

> reviewer: **braveji** · 2026-07-14 · 검토 대상: main `d086abc` (PR #21 병합 후)
> 선행: [`CRITIC_REVIEW_G2_braveji.md`](./CRITIC_REVIEW_G2_braveji.md) · [`CRITIC_REVIEW_G2_ADDENDUM.md`](./CRITIC_REVIEW_G2_ADDENDUM.md) · [`critic_report.json`](./critic_report.json)
> **판정: `critic_status: reject` 유지 — 단 5개 블로커 중 3개 해소, 남은 2개는 기계적.**

---

## 먼저 — kkkim님이 실제로 고쳤습니다

지적을 문서로 받아넘기지 않고 **산출물을 고쳤습니다.** 세 커밋이 그 증거입니다.

| 커밋 | 내용 |
|---|---|
| `52e2644` | **BLOCKER-5 해소** — 임베딩 43G(2,588건) `/workspace` 이관 + manifest 경로 재작성 |
| `ea03cee` | **BLOCKER-2·4 해소** — 문서를 정본 JSON에 동기화 |
| `b38c7de` | **BLOCKER-1 부분 해소** — 위암 erbb2 'blind 적중' 채점 철회 + 폐 정본 봉인 |

스코어보드 헤더가 `critic_status: reject → remediation 중`으로 정직하게 바뀐 것도 확인했습니다. **이건 좋은 대응입니다.**

---

## 블로커별 검증

### ✅ BLOCKER-5 (재현 불가) — **해소**

`embedding_path` 2,588건 전부 개인 홈 → `/workspace/data/cache`:

| 암종 | 경로 | 건수 |
|---|---|---|
| LUNG_NSCLC | `/workspace/data/cache/...` | 1052 |
| COLORECTAL | `/workspace/data/cache/...` | 622 |
| HEADNECK_HNSC | `/workspace/data/cache/...` | 472 |
| GASTRIC_STAD | `/workspace/data/cache/...` | 442 |

**이것이 가장 중요한 해소입니다.** Owner≠Reviewer가 구조적으로 복구됐고, 남은 remediation을 owner 아닌 사람도 실행할 수 있게 됐습니다.

> ⚠️ **미검증 1건:** 경로 문자열은 재작성됐으나 **실파일이 그 경로에 실제로 존재하는지는 확인하지 못했습니다** — 제 계정에 SSH 키가 없어(`Permission denied (publickey)`) 서버 접근이 안 됩니다. kkkim님이 `ls /workspace/data/cache/biop02/crosscancer/` 결과를 한 번 붙여주시면 완결됩니다.

### ✅ BLOCKER-2 (폐 정본 불일치) — **해소**

문서가 정본 JSON과 일치합니다:

| endpoint | 정본 JSON | 문서 |
|---|---|---|
| histology_lusc | 0.939 | ✅ 0.939 |
| egfr_activating | 0.8518 | ✅ 0.8518 |
| kras_g12c | 0.6809 | ✅ 0.6809 |

LAW_TEST 상단에 재동기화 배너도 달렸고, **"0.939 ≥ 0.93 명확 적중 — 1차(stale) 문서의 'CI 상한으로 구제'는 정본에서 불필요"** 로 정정됐습니다. 예상대로 **정정이 결과를 개선**했습니다.

### ✅ BLOCKER-4 (대장 5-seed 실패 은폐) — **해소**

스코어보드 결론 6번에 `cms1_vs_rest 0.912 < 0.936 FAIL · cms4_vs_rest 0.661 < 0.773 FAIL`이 명시됐고, *"이전 대장 LAW_TEST에 '미실시(non-blocking)'로 잘못 기술되고 스코어보드 인용 0이던 것을 정정"* 이라고 자진 기록됐습니다.

### 🟡 BLOCKER-1 (위암) — **부분 해소**

- ✅ **erbb2 '적중' 채점 철회 완료.** LAW_TEST에 *"shuffle-null 0.6406 → real↔null 마진 0.004 = 자기 순열 위로 신호 0. 예측적중 채점은 무효"* 명시. 스코어보드 결론 2번의 인용도 **[인용 철회]** 로 표기.
- ❌ **위암 `lauren_diffuse` 양성대조 실패(0.5364, null 0.8232)의 원인 진단은 미완.** bag-size 교란인지, 라벨 품질인지, 56% 결손(holdout 58/132) 때문인지 구분되지 않았습니다.

### ❌ BLOCKER-3 (pixel-mean · subtype-only baseline) — **미해소**

7-point #2가 요구하는 3종 중 여전히 shuffle-null만 존재합니다. **#2는 계속 `reject`입니다.**

### ❌ BLOCKER-4-2 (5-seed null을 폐·위·두경부에) — **미해소**

`critic_robustness.json`이 세 암종 어디에도 없습니다. **sealed-forward 3암종 전 endpoint의 우연배제가 확립되지 않았습니다 — Paper C의 유일한 검정력 있는 확증인 두경부 HPV 0.9594를 포함해서입니다.**

---

## 🔴 신규 지적 — 표와 본문이 서로 모순됩니다

스코어보드 **결론 1번**:

> ⚠️ **단 HPV 포함 폐·위·두경부 전 endpoint는 단일시드 shuffle-null만 있어 우연배제가 ≥5-seed로 확립되지 않았다**

스코어보드 **표 17행**:

> | 두경부 | **HPV** | … | **0.9594** | **26** | **충분** | sealed | **✅ CONFIRM (≥0.80)** |

**같은 문서가 "우연배제 미확립"이라 쓰고, 표에서는 `✅ CONFIRM` 도장을 찍고 있습니다.** 독자는 표를 봅니다. 본문의 경고는 표의 체크마크를 이기지 못합니다.

이건 제가 지적한 패턴의 재발입니다 — **낙관적 표기는 눈에 띄지 않아 살아남고, 비관적 단서는 각주로 밀린다.**

**HPV 행의 판정을 `✅ CONFIRM` → `provisional (우연배제 미확립 — 5-seed 대기)` 로 내려야 합니다.** 이 한 줄이 문서의 자기모순을 없앱니다.

---

## 재판정 — `reject` 유지, 그러나 승격 경로는 짧습니다

| 판정 | 조건 |
|---|---|
| **현재: `reject`** | 표가 `✅ CONFIRM`을 주장하는데 본문 스스로 "우연배제 미확립"이라 인정 — **문서가 자기 근거를 넘어선 주장을 하고 있음** |
| **→ `caution`** | **HPV 행을 `provisional`로 하향** (편집 1건). 그러면 문서는 근거 이상을 주장하지 않게 되고, "법칙 방향 일관·이분법 미확립"이라는 기존 결론은 5-seed 없이도 방어 가능합니다 |
| **→ `pass`** | ① `critic_robustness_probe.py`를 폐·위·두경부에 실행 (5-seed null + pixel-mean/bag-size baseline 동시 해소) ② 위암 lauren 원인 진단 ③ 커버리지 비무작위 결손 분석 |

**`caution`까지는 편집 한 줄, `pass`까지는 스크립트 한 번**입니다. 블로커 5가 풀려서 이제 그 스크립트를 owner 아닌 사람도 돌릴 수 있습니다.

---

## kkkim님께 — 실행 명령

`experiments/crosscancer/critic_robustness_probe.py`가 main에 있습니다. 임베딩이 `/workspace`로 왔으니 바로 실행됩니다.

```bash
# GPU 예약 후 (#biop02-alerts)
conda activate /opt/envs/spatialpatho
cd experiments/crosscancer

python critic_robustness_probe.py --cancer HEADNECK_HNSC --device cuda:0   # ★ HPV — 최우선
python critic_robustness_probe.py --cancer GASTRIC_STAD  --device cuda:1   # ★ lauren 진단
python critic_robustness_probe.py --cancer LUNG_NSCLC    --device cuda:2
# → <cancer>/full/critic_robustness.json
```

**한 번의 실행이 BLOCKER-3과 BLOCKER-4-2를 동시에 닫습니다:**

| 산출 | 닫는 블로커 |
|---|---|
| **[B]** 5-seed shuffle-null → `real > null_mean + 2·null_sd` 판정 | **BLOCKER-4-2** — 우연배제 확립 (HPV 포함) |
| **[C]** `n_tiles`-only baseline ★ | **BLOCKER-1** — 위암 lauren이 bag-size 산물인지 판별 |
| **[D]** mean-embed baseline | **BLOCKER-3** — 7-point #2 (pixel-mean 대응물) |
| **[E]** `spearman(label, n_tiles)` | **BLOCKER-1** — 라벨-타일수 원천 교란 여부 |

**우선순위는 두경부(HPV)입니다.** Paper C의 유일한 검정력 있는 확증이므로, 여기서 5-seed를 통과하면 헤드라인이 서고, 실패하면 논문의 뼈대를 다시 짜야 합니다. 먼저 알아야 합니다.

---

## 총평

제가 `reject`를 낸 뒤 kkkim님이 **하루 만에 블로커 3개를 실제로 고쳤습니다.** 특히 43GB 임베딩 이관(BLOCKER-5)은 귀찮은 일인데 해주셨고, 그게 나머지를 풀 열쇠였습니다.

남은 건 **표기 한 줄과 스크립트 한 번**입니다. Paper C는 지금 "정직하게 절제된 결론"과 "그 결론을 받치는 근거" 사이의 간극이 처음으로 좁혀지고 있습니다.
