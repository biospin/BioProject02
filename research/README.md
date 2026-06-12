# research/ — 선행연구 조사 & 분석

BIOP02 선행연구. **2단계 분석 정책:**

- **Tier 1 (전 논문 one-each 요약):** [`_index/reading_list.md`](_index/reading_list.md) — 영역별 모든 논문의 importance·초록·scoop 플래그. 머신 인덱스 = [`_index/papers.csv`](_index/papers.csv) (95편).
- **Tier 2 (focus 논문 상세 멀티렌즈):** `<주제>/<저자-연도-id>/` 폴더 — BioProject01 방식 `paper-info.yaml` + `*_core.md` + `*_lens-academic.md` + `*_lens-industry.md` + `*_methodology-brief.md`.

전략 종합·실험 설계: [`novelty_positioning.md`](novelty_positioning.md) (타겟 저널 npj Precision Oncology).

## 디렉토리 구조

```
research/
  _index/            # reading_list.md (전 논문 요약), papers.csv (인덱스)
  novelty_positioning.md
  <주제>/
    <저자-연도-id>/  # focus 논문 상세분석 5파일
```

## 주제(topic) 폴더 ↔ 영역코드 매핑

| 폴더 | 영역코드 | 내용 |
|---|---|---|
| `foundation-models/` | FM | 병리 파운데이션 모델(임베딩 백본) |
| `phenotype-prediction/` | PHENO | H&E→분자표현형 예측 |
| `wsi-mil/` | MIL | WSI attention MIL |
| `morphology-drug/` | DRUG | 형태→약물반응·DepMap/GDSC |
| `datasets-benchmarks/` | DATA | 데이터셋·DB·벤치마크 |
| `rigor-leakage/` | RIGOR | site 교란·누수·일반화 |
| `hypothesis-support/` | HYPO | 치료가설 근거(LINCS·CTRP·organoid) |
| `knowledge-bases/` | KB | actionability·경로 KB(OncoKB·OpenTargets·Reactome) |
| `uncertainty-interpretability/` | UQ | 불확실성·calibration·해석성 |
| `preprocessing/` | PREP | stain 정규화·tiling |
| `ai-agents/` | AGENT | AI 에이전트·LLM-as-judge |

(빈 주제 폴더는 focus 논문이 생기면 생성)

## 현재 focus 논문 (Tier 2 완료)

| 논문 | 주제 | 역할 |
|---|---|---|
| `morphology-drug/dawood-2024-hids` | DRUG | 최고 scoop(동일저널) → Exp3 end-to-end baseline |
| `phenotype-prediction/tafavvoghi-2024-jpi` | PHENO | 직접 baseline(동일코호트·공개코드, macro-F1 0.727=bar) |
| `foundation-models/chen-2024-uni` | FM | 1순위 백본 |
| `wsi-mil/lu-2021-clam` | MIL | MIL baseline + 전처리 precedent |
| `rigor-leakage/howard-2021-site-signatures` | RIGOR | 엄밀성 #1 앵커 → Exp2 |

## focus 후보 (다음 Tier 2 대상)
subramanian-2017-lincs(2nd 가설경로), chakravarty-2017-oncokb(plausibility), gottweis-2025-coscientist(시스템 framing scoop), olsson-2022-conformal(불확실성), tcga-cdr-liu-2018(라벨 소스).
