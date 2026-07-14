# 메커니즘 시연 대안 방법 조사 — "왜 MSI는 H&E로 보이고 HER2-증폭·RAS-점변이는 조용한가"

> `claim_level: hypothesis_only` · `critic_status: pending` · `evidence_strength: design-only(미실행)` · **커밋 금지**
> research-methodologist. 목적: 공간전사체(ST) 경로가 막힌 상황(대장 Visium 55µm NULL, `experiments/crosscancer/COLORECTAL/ST/README.md`)에서, **외부 substrate 없이 이미 학습된 UNI 임베딩 + CLAM-SB MIL로 치환가능성 법칙의 메커니즘 근거를 시연**할 대안 방법을 평가·설계한다.
> 참조: 사전등록 법칙 `../../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md` · 계획 `FLAGSHIP_PLAN.md`·`PAPER_DIRECTION.md` · ST 스쿱 `2026-07-12_CRC-LUNG-ST-scoop-and-data.md`.

---

## ⭐ 한 줄 판정

**최우선 = 단일 파이프라인 "해석가능 형태특징 상관(주축) + MIL attention 국소화(가시 반쪽) + 특징-절제 counterfactual(충실도 검증)".** 세 후보(#2·#1·#5b)를 별개 옵션이 아니라 **하나의 3단 파이프라인**으로 묶는다. 학습된 UNI+CLAM 그대로 재사용하고 추가 학습 0, 외부 *데이터셋* 0(단 핵검출/염색분해 front-end 도구는 필요, off-the-shelf), 8-15 마감 내 실행 가능. 세포 그래프(#3)·개념/프로토타입(#4)·생성형 diffusion counterfactual(#5a MoPaDi)은 마감·스쿱·부담으로 **드롭**.

**핵심 재프레이밍(가장 중요):** 이 과제가 요구하는 것은 "가장 값싼 해석법"이 아니라 **비대칭(asymmetry)을 보이는 법**이다 — MSI엔 형태 상관물이 **있고**(양성), HER2-증폭·RAS-점변이엔 **없다는 신뢰할 만한 NULL**(음성)을 같은 파이프라인으로 동시에 보여야 법칙의 메커니즘 근거가 된다. 이 기준으로 재랭킹하면 **attention(#1) 단독은 부적격**하다: attention은 AUROC와 무관하게 항상 가중치를 뱉으므로, near-random인 HER2(0.599)·RAS(0.705)에서 "모델이 아무 데도 주목 안 한다=조용"을 읽어낼 수 없다. attention은 **가시 반쪽의 국소화**일 뿐, 그 타일이 무엇인지(TIL? 점액?)는 해석가능 형태특징(#2)이 있어야 규정된다. 따라서 **#2가 load-bearing 주축, #1은 종속, #5b는 검증 레그**다.

---

## 후보 비교표

| # | 방법 | 원리 | 우리 데이터로 되나(UNI+CLAM) | 추가작업량 | 해상도 적합 | 8-15 마감 | 비대칭(가시+NULL) 시연력 | 최근접 선행(스쿱) |
|---|---|---|---|---|---|---|---|---|
| **2** | **해석가능 형태특징 상관** (TIL밀도·점액분율·핵 morphometry·tumor-stroma비 ↔ 마커) | 인간해석가능 정량특징을 뽑아 마커와 상관. MSI엔 상관·HER2/RAS엔 무상관 예측 → **falsifiable 비대칭**. FLAGSHIP AI레이어 "형태상관물 강도" 항목을 직접 채움 | ✅ (UNI 타일 좌표 재사용, 특징만 별도 산출) | **중**(핵검출/염색분해 front-end 필요, 학습 없음) | ✅ resolution-native(타일=20×) | ✅ | **★ 최고**(양성·NULL 둘 다 정량, 검정력 통제 가능) | **HistoAtlas**(arXiv 2603.16587), imCMS(Gut 2021), nuHIF(Diao 2021) |
| **1** | **MIL attention/saliency** (학습된 CLAM attention) | MSI+ 예측 시 상위 attention 타일 위치 매핑, RAS+와 대조. 상위 타일을 #2로 병리 해석 | ✅ (attention 이미 산출됨, 0 추가학습) | **소** | ✅ (모델이 실제 쓰는 타일) | ✅ | **부분**(가시 반쪽만; NULL은 못 보임 — near-random attention은 무의미) | SI-MIL(Nat 2024), PAMIL(MICCAI 2024), attention-MIL 해석 다수 |
| **5b** | **특징-절제 counterfactual** (attention 상위 타일 마스킹 / 해석특징 zero-out → 예측 붕괴) | 형태 상관물 제거 시 예측 붕괴 → **인과적** 근거. Critic #3 counterfactual과 직결. attention faithfulness(Deletion/Insertion-AUC) 검증 겸함 | ✅ (추론만 반복, 0 추가학습) | **소** | ✅ | ✅ | **검증용**(#1의 attention이 진짜 실린지 확인) | (일반 Deletion/Insertion 절제, 스쿱 낮음) |
| 3 | 세포 그래프/조직 아키텍처 (HoVer-Net 핵분할 → 세포 그래프 특징) | 세포 유형·공간배치 그래프 특징 | △ (front-end는 #2와 공유, 그래프 구성 추가) | **대**(그래프 파이프라인) | ✅ (세포해상도) | ⚠️ 빠듯 | 중(#2+그래프, 한계이득) | HistoAtlas·다수 cell-graph, 레드오션 |
| 4 | 개념/프로토타입 병목 (concept bottleneck·prototype MIL) | 사람정의 개념으로 예측 병목 | △ (재학습 필요) | **대**(재학습) | ✅ | ❌ 마감 밖 | 중(개념=형태상관물 후보) | GECKO(arXiv 2504.01009), label-free concept MIL(2501.02922) |
| 5a | 생성형 counterfactual (MoPaDi diffusion) | diffusion으로 이미지 변형해 예측 뒤집기 | ❌ (diffusion 학습 수주) | **매우 대** | ✅ | ❌ 마감 밖 | 높으나 **이미 스쿱**(MSI on CRC/breast/lung) | **MoPaDi**(bioRxiv 2024.10.29.620913) — MSI 이미 완료 |

**front-end 주의(정직):** #2·#3의 "외부 데이터 0"은 **외부 *데이터셋* 0**이지 **도구 0이 아니다.** TIL밀도·점액분율·핵 morphometry는 핵검출(HoVer-Net / CellViT / StarDist)이나 염색분해(Ruifrok–Johnston hematoxylin/eosin/DAB) front-end가 필요하다 — 모두 off-the-shelf·학습 불필요·오픈. #3(세포그래프)은 이 front-end를 #2와 공유하므로 "별도 무거운 옵션"이 아니라 **#2의 비싼 확장**이다(그래프 구성만 추가). 마감 내에는 #2까지, #3은 stretch.

---

## 권고 실행계획 — 하나의 3단 파이프라인 (무엇을, 어느 데이터로, 며칠)

**공통 데이터:** 이미 학습·임베딩 완료된 우리 코호트. 대장 CLAM-SB(523슬라이드, MSI 0.918 / all-RAS 0.705 / BRAF 0.882), 유방(ER 0.901 / HER2 0.599). **외부 substrate·재학습 없음.** 마커 라벨·split은 기존 잠금분 사용.

### 1단 (주축) — 해석가능 형태특징 ↔ 마커 상관, 비대칭 정량 · **약 3-4일**
- **특징(슬라이드/타일 단위):** ① TIL/림프구 밀도(핵검출→소형·고밀도 핵 분율), ② 점액 분율(염색분해 e/약염색 영역), ③ 핵 morphometry(면적·이심률·색질 이질성), ④ tumor-stroma 비. 전부 인간해석가능.
- **추정량:** 마커별 특징-예측 상관(슬라이드 라벨 vs 특징; AUROC 또는 상관계수) + **bootstrap 95% CI**. MSI엔 유의 상관(특히 TIL·점액), HER2-amp·RAS엔 무상관 예측.
- **비대칭 = 법칙의 falsifiable 형태.** BRAF(등급적, serrated/MSI 동반)는 중간 상관이어야 함(사전등록과 정합).

### 2단 (가시 반쪽 국소화) — CLAM attention → 형태 해석 · **약 1-2일**
- MSI+ 예측 슬라이드의 attention 상위 k% 타일을 추출해 **1단 특징으로 규정**(TIL 풍부? 점액? 수질형?). "attention이 어디에 실리나"를 병리학적으로 해석하고 RAS+와 대조.
- **주의:** HER2/RAS는 near-random이라 attention 해석을 **가시 반쪽(MSI)에만** 건다. 조용 반쪽의 근거는 1단 NULL이 담당하며, attention 부재로 조용을 주장하지 않는다.

### 3단 (충실도·인과 검증) — 특징-절제 counterfactual · **약 1-2일**
- attention 상위 타일 마스킹(또는 해석특징 zero-out) → 예측 AUROC 붕괴 곡선(Deletion-AUC). MSI 예측이 TIL/점액 타일 제거 시 붕괴하면 "상관물이 인과적으로 실린다" 확인. Critic #3(counterfactual) 직접 충족 + attention faithfulness 방어(리뷰어의 "attention is not explanation" 대응).

### NULL을 airtight하게 만드는 설계 (이게 #1 threat-to-validity)
리뷰어의 가장 강한 공격 = **"HER2/RAS 무상관은 조용이 아니라 저검정력(n_pos 작음)이다."** 우리 CRC ST NULL 문서가 depth-control·양성대조·림프구특이 체크로 null을 방어한 구조를 **그대로 이식**한다. "조용"은 단일 음성이 아니라 **연접(conjunction)**으로만 주장:
1. **near-random AUROC**(HER2 0.599 / RAS 0.705·오배정 0.416) — 예측 자체가 약함.
2. **해석특징 무상관** — 측정 가능한 특징이 마커와 상관 없음.
3. **양성대조(핵심):** *같은 파이프라인·비교 가능한 n*에서 MSI 상관을 회복 → NULL이 파이프라인 결함·검정력 부족이 아님을 증명.
- 추가: 특징이 실제로 측정됐다는 sanity(HER2 슬라이드에서도 TIL·핵특징은 정상 산출), 검정력 보고(n_pos, 검출 가능 최소효과크기), 프록시-선택 민감도.
- **CPTAC 보조:** "HER2 단백질↑ but H&E 침묵"(d≈4) 기존 결과를 decoupling 보조증거로 첨부(형태-분자 분리를 단백 층위에서 재확인). off-thesis 확장은 하지 않음.

**총 소요: 약 6-9일 (마감 8-15 내).** #3(세포그래프)·#4는 시간 남으면 stretch, 아니면 드롭.

---

## 스쿱 / 선행 (정직)

- **예측·해석 자체는 novelty 아님.** imCMS(Sirinukunwattana, Gut 2021)가 CMS별 형태 상관물을 이미 보고했고, attention-MIL 해석(Kather, SI-MIL 등), H&E→MSI 예측(Kather Nat Med 2019)은 포화.
- **HistoAtlas**(arXiv 2603.16587, 2026) — 38개 해석가능 histomic 특징을 pan-cancer로 분자프로그램·변이·면역아형에 연결. **#2 route의 가장 가까운 선행이자 최대 스쿱**. 차별화: 그들은 특징→분자 상관 *지도*(descriptive), 우리는 그 상관의 **유무(비대칭)를 사전등록 치환가능성 법칙의 메커니즘 근거**로 사용 — 직교 렌즈.
- **SI-MIL**(Nat Commun 2024) — deep MIL attention과 handcrafted 해석특징을 명시적으로 결합. **#1+#2 조합의 최근접 선행**. 차별화: 방법이 아니라 **프레이밍**(cross-marker 비대칭 = 법칙 메커니즘).
- **MoPaDi**(bioRxiv 2024.10.29.620913) — 생성형 counterfactual로 MSI를 CRC/breast/lung에서 이미 시연. **#5a는 스쿱+수주 학습 → 드롭.** 우리 #5b(특징-절제)는 생성형이 아니라 마스킹 절제라 별개·값쌈.
- **GECKO**(arXiv 2504.01009), label-free concept MIL(arXiv 2501.02922) — #4 개념병목의 선행, 재학습 필요 → 마감·스쿱으로 드롭.
- **우리 novelty 문장(반복):** 예측도 해석법도 아니라, **형태 상관물의 유무가 H&E의 분자검사 치환가능성을 결정한다는 사전등록 법칙의 메커니즘 근거로 이 상관/비대칭을 사용**하는 것. 방법은 기성, 기여는 프레이밍.

---

## 한계 (원고 명시)

- **저검정력.** HER2/RAS/일부 endpoint n_pos 작음(15~21). NULL은 위 3-연접 + 양성대조로만 방어하며, "조용"은 "저해상·저검정력에서 접근 불가"를 뜻하지 "생물학적 상관물 부재"가 아님(법칙 사전등록 §해석수준과 정합).
- **front-end 도구 의존.** 핵검출·염색분해 정확도가 특징 품질을 좌우. HoVer-Net/CellViT 등 도메인 시프트(TCGA H&E 염색편차)에 취약 → sanity·민감도 필요.
- **attention faithfulness 논쟁.** attention≠설명 비판이 있으므로 #3(Deletion/Insertion-AUC)로 반드시 검증. attention 단독 해석 주장 금지.
- **상관은 인과 아님.** #3 절제가 인과 방향을 보강하나 관측연구 한계 유지. hypothesis_only.
- **RAS 반쪽은 점변이라 본질적으로 덜 깨끗**(발현 불변, 하류 프록시 경유) — 유방 ERBB2 증폭보다 약함. exploratory·프록시로만 주장(사전등록 §주의와 정합).
- **claim_level: hypothesis_only, 후향적, 전향적 검증 필요. 커밋은 사람이.**

---

## Sources
- HistoAtlas (pan-cancer morphology↔molecular): [arXiv 2603.16587](https://arxiv.org/html/2603.16587)
- SI-MIL (self-interpretable MIL + handcrafted features): [PMC11601081](https://pmc.ncbi.nlm.nih.gov/articles/PMC11601081/)
- MoPaDi (counterfactual diffusion, MSI already done): [bioRxiv 2024.10.29.620913](https://www.biorxiv.org/content/10.1101/2024.10.29.620913v4)
- PAMIL (prototype attention MIL): [MICCAI 2024](https://papers.miccai.org/miccai-2024/587-Paper1022.html)
- GECKO (vision-concept pretraining): [arXiv 2504.01009](https://arxiv.org/pdf/2504.01009) · Label-free concept MIL: [arXiv 2501.02922](https://arxiv.org/pdf/2501.02922)
- Nuclear morphology HIF / genome instability: [PMID 38898127](https://pubmed.ncbi.nlm.nih.gov/38898127/)
- TIL architecture (breast, multiomics): [JCO CCI 2020](https://ascopubs.org/doi/10.1200/CCI.19.00126)
- imCMS: Sirinukunwattana et al., Gut 2021 · Kather MSI, Nat Med 2019 (선행 앵커, 본 조사 내 인용)
