# split_policy_v0 — TCGA-BRCA / CPTAC-BRCA Data Split Policy

> **상태: v0 DRAFT — data-owner (kkkim) sign-off 필요.** 서명 전까지 manifest의 `split` 컬럼은 잠정.
> Sign-off 후 fold 정의를 **동결(lock)**, 정의 해시를 모든 `metrics.json`에 기록한다 (CLAUDE.md "locked after sign-off, no changes").
>
> 근거: Bussola 2020 (patient-level), Yagis 2021 (leakage 29–55% 부풀림), Howard 2021 (site signature + PreservedSiteCV).
> 연계: research/experiment_plan.md **Exp2**, Critic 7-point **#1 (data leakage)**.

---

## 0. 한 줄 요약 / Headline

**Split unit = patient (`case_id`), 절대 slide/tile 아님.** 그 위에 **TCGA submitting-site (TSS) disjoint** 를 강제한다.
Preferred = Howard PreservedSiteCV (QP로 class-balance 최대화), fallback = site-grouped greedy.
CPTAC-BRCA는 학습/튜닝에 일절 노출하지 않는 **외부 hold-out test**다.

---

## 1. Split unit (잠금 불변식 / hard invariant)

| 규칙 | 근거 |
|---|---|
| 1 환자(`case_id` = `TCGA-XX-XXXX` 12자 prefix)의 **모든** 슬라이드는 **동일 fold**에 묶인다. | Bussola 2020: slide/tile split은 환자 정체성 누수 → 낙관 편향. |
| split 결정은 **patient 수준**에서만 일어난다. slide_id, tile, file 단위 분배 **금지**. | Yagis 2021: leakage가 정확도를 29–55% 부풀림. |
| 동일 환자의 **DX1/DX2(같은 환자 다중 진단 슬라이드)** 도 분리 금지 — 같은 `case_id`이면 같은 fold. | 환자 disjoint 전제. |

**Critic #1 통과 조건 1: patient-overlap(train∩val∩test by `case_id`) == 0** (hard assert, 빌드 시 + CI).

---

## 2. Site-disjoint splitting (핵심 / the core upgrade)

현재 `build_manifest.py`의 `split_for()`는 `sha256(seed:case_id)` **hash split**으로, **site 통제가 전혀 없다.** 이를 site-aware 로직으로 교체한다.

### 2.1 Site key 추출 (TSS code)

TCGA barcode `TCGA-XX-XXXX`의 두 번째 토큰 `XX` = **Tissue Source Site (TSS) code**.
이것이 submitting institution의 proxy이며, scanner/staining/fixation 시그니처를 운반한다 (Howard 2021).

```
case_id  = "TCGA-A2-A0CM"  →  tss_code = "A2"
```

manifest에 **`tss_code` 컬럼을 신설**한다.

### 2.2 Preferred — Howard PreservedSiteCV (QP)

- 각 환자를 `tss_code`로 그룹화 → **한 site는 한 fold에만** 배정.
- 배정을 quadratic program으로 풀어 fold별 **ER/PR/HER2/PAM50 class 비율 불균형(MSE)을 최소화**.
- 구현: `github.com/fmhoward/PreservedSiteCV` 포팅 (QP solver = cvxpy 또는 quadprog).
- 출력: 각 환자 → fold 라벨. site는 fold 경계를 절대 넘지 않는다.

### 2.3 Fallback — site-grouped greedy

QP solver 미가용 시:
1. site를 환자 수 내림차순 정렬.
2. 가장 작은 누적 환자 수를 가진 fold에 site를 통째로 greedy 배정 (LPT bin-packing).
3. 결과 fold별 class 비율을 리포트 — QP 대비 불균형이 크면 v0.1에서 QP로 승격.

### 2.4 Hard assert

> **한 `tss_code`가 train·val·test 중 둘 이상에 등장하면 빌드 실패 (assert + non-zero exit).**

**Critic #1 통과 조건 2: site-disjoint == True** (한 site = 한 fold).

---

## 3. Fractions, seed, fold 정의

| 항목 | 값 | 비고 |
|---|---|---|
| train | **0.70** | site-disjoint 그룹 단위 배정이므로 ±5%p 흔들림 허용 (site는 쪼갤 수 없음). |
| val | **0.15** | calibration/conformal split은 train 내부에서 추가 분리 (§5). |
| internal test | **0.15** | TCGA 내부 held-out, site-disjoint. |
| external test | CPTAC-BRCA **전량** | TCGA와 site-disjoint 자동 성립 (다른 코호트). 학습/튜닝 비노출. |
| `--split-seed` | **42** | greedy tie-break + 보고용. QP는 결정적이므로 seed는 fallback 경로에만 영향. |

**원칙: site는 atomic.** 정확히 0.70을 맞추려 site를 쪼개지 **않는다** — disjointness가 fraction 정밀도보다 우선.
실제 달성된 fraction을 manifest 빌드 로그와 `split_manifest_meta.json`에 기록한다.

---

## 4. Per-target 라벨 결측 처리 (label-missingness)

TCGA biotab의 결측 토큰: `[not available] / [not applicable] / [unknown] / [discrepancy] / indeterminate / equivocal / not performed / na` (현 `MISSING` 집합 유지).

| Target | Keep / Exclude 규칙 |
|---|---|
| **ER status (IHC)** | binary (Positive/Negative). 결측 → 해당 환자를 **ER task에서 제외** (전체 제거 아님). |
| **PR status (IHC)** | 동일 (binary, 결측 시 PR task 제외). |
| **HER2 status (IHC)** | binary. `equivocal`(IHC 2+, FISH 미확정)은 **결측 처리** → HER2 task 제외 (소음 라벨 차단). |
| **PAM50 (4-class)** | LumA/LumB/HER2-E/Basal. Normal-like는 **제외** (형태학 신호 빈약, Tafavvoghi 정렬). PAM50은 biotab clinical_patient에 없음 → **별도 소스(TCGA-BRCA 2012 / cBioPortal)에서 환자 단위 join** 후 채움. |

**중요: 결측은 task별(per-target)로 행을 마스킹**하되 split 배정에는 영향을 주지 않는다.
즉 split은 환자 전체 집합에 대해 **한 번** 결정되고, 각 phenotype head는 자기 라벨이 있는 환자 부분집합에서만 학습/평가한다 → split 정의가 target마다 달라지는 것을 방지 (재현성).

`has_labels`(현 컬럼)에 더해 **`has_er / has_pr / has_her2 / has_pam50`** boolean 컬럼을 신설한다.

생존 엔드포인트(보조): PFI 1차, DFI 보조. OS/DSS는 sensitivity-only (TCGA-CDR Liu 2018: BRCA OS ~151 events → 검정력 부족). Paper A primary는 phenotype이며 생존은 후속.

---

## 5. Calibration / Conformal split (Olsson 연계)

conformal abstention (Olsson 2022) 을 위해 **train 내부에서** calibration set을 분리한다:
- train의 ~15% 를 **class-balanced** 로 calibration 으로 떼어냄 (ER/PR/HER2/PAM50 각 클래스가 충분히 포함).
- calibration도 **환자-disjoint + site-disjoint** 유지 (leakage 금지).
- calibration set 해시를 `metrics.json`의 `conformal.calibration_set_hash`에 기록.

---

## 6. Lock criteria & hash recording

split은 아래를 **모두** 만족할 때 잠근다:

1. patient-overlap == 0 (assert pass).
2. site-disjoint == True (assert pass).
3. fold별 ER/PR/HER2/PAM50 class 비율표가 첨부되고 data-owner(kkkim)가 검토.
4. site-classifier probe AUC (Exp2-A) 가 **사전 측정**되어 baseline으로 기록 (잠금 자체의 전제는 아니나 동봉).

**잠금 절차:**
```
split 정의(JSON: case_id → fold) → sha256 →  split_hash
```
- `split_hash` 를 `agents/data/manifests/split_manifest_meta.json` 에 기록.
- 이후 **모든** 실험의 `metrics.json` 에 `split_hash` 필드를 `commit_hash` 옆에 추가 기록.
- 잠금 후 split 변경 = 새 버전(v0.1) + 새 해시 + 재-sign-off. 기존 실험과 비교 불가로 명시.

---

## 7. Leakage checklist (binds Critic #1)

빌드 + CI 에서 자동 검사하고, 결과를 `split_manifest_meta.json`에 기록:

- [ ] **patient-overlap == 0** : `set(train.case_id) ∩ set(val.case_id) ∩ set(test.case_id) == ∅`.
- [ ] **site-disjoint == True** : 어떤 `tss_code`도 둘 이상 fold에 없음.
- [ ] **CPTAC 격리** : CPTAC 케이스가 TCGA train/val에 0건.
- [ ] **site-classifier probe AUC 보고** : FM 임베딩으로 submitting-site 예측 (one-vs-rest AUROC). Howard 기준선(0.964–0.998) 대비 residual site leakage 강도를 **숫자로** 리포트 (Exp2-A). 높을수록 site-aware split의 정당성이 강해짐.
- [ ] **라벨 정의 단일 소스** : ER/PR/HER2 = biotab IHC, PAM50 = 단일 외부 소스 고정 (train/test 간 정의 드리프트 차단).
- [ ] **temporal/parametric 채널 명시** : FM(UNI/CONCH)의 parametric 지식은 통제 불가 채널로 잔존 → de Jong 2025 (FM이 medical-center 시그니처 인코딩) 인용하고 floor로 site-probe AUC를 보고. stain normalization은 보조일 뿐 단독 방어 아님 (Howard #4).

---

## 8. `build_manifest.py` 에 필요한 구체적 변경

현재 코드 (branch `feat/BIOP02-21-kkkim-manifest-rebuild`)의 두 지점을 교체한다.

### 8.1 `tss_code` 컬럼 추가 (행 생성부)

각 출력 행에:
```python
"tss_code": r["case_id"].split("-")[1] if len(r["case_id"].split("-")) >= 2 else "",
```
그리고 `has_er / has_pr / has_her2 / has_pam50` boolean 컬럼을 추가, `fields` 리스트에 반영.

### 8.2 hash split → site-disjoint assignment 로 교체

현재:
```python
def split_for(case_id, seed, ratios):
    h = int(hashlib.sha256(f"{seed}:{case_id}".encode()).hexdigest(), 16)
    ...
```
→ 환자별 독립 hash 배정을 **제거**하고, 전체 환자×site×label 행렬을 받아 한 번에 배정하는 함수로 교체:
```python
def assign_site_disjoint_splits(rows, ratios, seed):
    """
    rows: per-patient records with tss_code + per-target labels.
    1) group patients by tss_code
    2) PreservedSiteCV QP (preferred) → minimize per-fold class-imbalance MSE
       fallback: greedy LPT bin-packing of whole sites
    3) assert: no tss_code spans >1 fold; no case_id spans >1 fold
    returns: {case_id: "train"|"val"|"test"}
    """
```
호출부에서 행별 `split_for(...)` 대신 사전 계산된 dict 를 lookup.

### 8.3 빌드 끝에 leakage assert + meta 기록

```python
assert no_site_crosses_folds(out_rows)
assert no_patient_crosses_folds(out_rows)
write_split_meta(out_rows, path="agents/data/manifests/split_manifest_meta.json")
# fields: split_hash, per-fold class balance, achieved fractions, n by site, policy="v0"
```

### 8.4 출력 컬럼 (신규)

`case_id, slide_id, slide_type, file_name, source_path, tss_code, er_status, pr_status, her2_status, pam50, has_er, has_pr, has_her2, has_pam50, split, has_labels`

---

## 9. Sign-off

| 역할 | 담당 | 상태 |
|---|---|---|
| Data-owner (작성/잠금) | kkkim | ☐ pending |
| Split critic (cross-review, owner≠reviewer) | braveji (Critic 총괄) — 바이오 sub-check sjpark | ☐ pending |

서명 전: 이 문서 = **v0 draft**, manifest split = 잠정.
서명 후: fold 정의 + `split_hash` 동결, 변경 시 새 버전.

## 10. Leader 결정 반영 (2026-06-10, kkkim)
- **Subset = 전체 1010 (full BRCA cohort)** — Paper A 범위를 1010으로 확정. ⚠️ CLAUDE.md "~150 subset" 금지조항(line 220/239) override → 거버넌스 갱신 필요. site-disjoint split 검정력 확보.
- **PAM50 소스 = cBioPortal TCGA-BRCA PAM50** (1순위, 분류기 정의 Parker 2009 인용); 커버리지 부족 시 TCGA RNA-seq + genefu(Parker centroids) fallback. → §4·§7 라벨 정책에 반영.
