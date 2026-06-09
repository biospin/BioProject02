# BIOP02 SpatialPathoAgent — 선행연구 리스트 (인덱스 + 초록)

작성 2026-06-09 (kkkim). 5개 영역 × literature-scout 병렬 조사. DOI는 가능한 한 검증했으며, 미검증/preprint는 `unverified` 표기 — **인용 전 CrossRef 재확인 필수**. 머신 인덱스는 [`papers.csv`](papers.csv).

상세 멀티렌즈 분석(BioProject01 방식: `_core.md` + `_lens-academic.md` + `_lens-industry.md` + `_methodology-brief.md`)은 다음 단계. 지금은 **리스트 + 초록**.

---

## ⭐ 핵심 종합 — novelty / scoop 판단

**형태(H&E)→분자표현형 예측은 이미 포화 상태(scoop 위험 큼).** 따라서 BIOP02의 형태→표현형 컴포넌트 자체는 novelty가 아니며, 단독 기여로 내세우면 리뷰를 못 넘긴다.

- **직접 scoop 후보 (BRCA subtype/receptor from H&E):** `couture-2018`, `naik-2020`(ER/PR MIL), `gamble-2021`(ER/PR/HER2 + 형태해석), **`shamai-2024`**(가장 최신, IHC 오진까지 탐지), **`tafavvoghi-2024`**(★동일 TCGA-BRCA+CPTAC 코호트 + 공개코드 → 가장 위험한 직접 baseline).
- **치료-링크 scoop (부분):** `farahmand-2022`(HER2→trastuzumab 반응 예측), **`dawood-2024`**(★H&E→약물민감도, TCGA-BRCA 427약물 — 형태→약물 영역 최강 scoop).
- **방어 가능한 white space:** 단일 논문이 다루지 않은 **통합 시스템** — 파운데이션 임베딩 → 명시적 분자표현형(중간단계) → DepMap PRISM+GDSC 전이 → **랭킹된 hypothesis-only 치료가설 + PRISM↔GDSC 일관성 검증 + 독립 Scientific Critic 게이트** (약물 구조 입력 없음 = DRP 아님).
- **정직한 포지셔닝:** 기여 = "새 method"가 아니라 **system / evaluation / governance**. `tafavvoghi-2024`·`dawood-2024`를 경쟁자가 아니라 baseline으로 인용하고, 그 위에 표현형-매개 framing + Critic 가드레일 + cross-DB 일관성을 delta로.

---

## 1. 병리 파운데이션 모델 (FM) — 임베딩 백본

벤치마크(`campanella-2025`, `neidlinger-2024`) 수렴 신호: **Virchow2 / Prov-GigaPath / UNI / H-optimus-0** 상위 클러스터. BRCA H&E엔 **UNI**(CLAUDE.md 1순위, TCGA/CPTAC 사전임베딩 존재) + **Prov-GigaPath**(슬라이드 인코더 내장)가 안전, **Virchow2**(최고 타일 점수), **H-optimus-0/Phikon-v2**(개방 라이선스 baseline).

- **chen-2024-uni** (상, Nat Med): UNI — DINOv2로 10만+ WSI·1억+ 패치 사전학습한 ViT-L 타일 인코더(1024d). 34개 과제에서 이전 인코더 능가, 라벨 효율적 전이 강함. *우리 1순위 백본.*
- **xu-2024-provgigapath** (상, Nature): Prov-GigaPath — 13억 타일·17만 WSI, ViT 타일 인코더 + LongNet 슬라이드 인코더. 26개 과제 SOTA, mutation/biomarker 예측 강함. *슬라이드-레벨 표현형 예측에 강력.*
- **vorontsov-2024-virchow** (상, Nat Med): Virchow — MSK 150만 WSI, 632M ViT-H. pan-cancer 0.949 AUC. **Apache 2.0**(라이선스 관대) → 출판 친화적.
- **zimmermann-2024-virchow2** (상, arXiv·unverified): mixed-magnification 310만 WSI 확장. 다수 벤치마크 타일-레벨 평균 1위. *라이선스 확인 필요.*
- **campanella-2025-clinicalbench** (상, Nat Commun): 공개 FM 임상 벤치마크. UNI·Prov-GigaPath가 biomarker/치료결과 예측에 일관 강세 → **백본 선택 근거**.
- **lu-2024-conch** (중, Nat Med): CONCH — vision-language(512d), 117만 image-caption. zero-shot·텍스트 검색 가능하나 순수 백본으론 UNI보다 약함.
- **saillard-2024-hoptimus0** (중, 모델공개·unverified): ViT-Giant 1.1B, **MIT 라이선스**(개방). 벤치마크 상위. *peer-review 논문 없음 → 모델 릴리스로 인용.*
- **filiot-2024-phikonv2** (중, arXiv·unverified): 공개데이터만으로 학습한 ViT-L(1024d), biomarker 예측 특화. *투명·재현 가능한 개방 baseline.*
- **lgai-2025-exaonepath2** (중, arXiv·unverified): EXAONE Path 2.0(768d, CLAUDE.md 3순위). 3.7만 WSI로 end-to-end 슬라이드 감독, 10개 biomarker SOTA. NC 라이선스(학술 적합).
- **neidlinger-2024-fmbenchmark** (중, arXiv·unverified): 두 번째 독립 벤치마크. Virchow2/H-optimus-0 평균 선두, GigaPath/UNI 근접.
- **wang-2022-ctranspath** (하, Med Image Anal): CTransPath — CNN+Swin SSL 인코더. 과거 표준이나 현재 FM에 밀림 → 비교점/legacy baseline.

## 2. H&E → 분자표현형 예측 (PHENO) — ★scoop 밀집 구역

- **couture-2018-npjbc** (상·SCOOP, npj Breast Cancer): TMA로 BRCA 등급·ER·조직형·PAM50 intrinsic subtype 예측. 형태가 intrinsic subtype 정보 담음을 보인 시초. *형태→subtype의 정전 prior art.*
- **naik-2020-natcommun** (상·SCOOP, Nat Commun): MIL로 H&E WSI에서 ER(+PR) 상태 예측, TCGA-BRCA+외부 코호트. *우리 ER/PR MIL과 직접 겹침.*
- **shamai-2024-commsmed** (상·SCOOP, Commun Med): 최신 ER/PR/HER2 from H&E + IHC 오진 탐지까지. *현재 SOTA, 가장 높은 기준선.*
- **gamble-2021-commsmed** (상·SCOOP, Commun Med): Google, ER/PR/HER2 예측 + 각 호출의 형태학적 근거 제시(해석성). *biomarker+형태해석 최근접 prior art.*
- **tafavvoghi-2024-jpi** (상·SCOOP-DIRECT, J Pathol Inform): 4개 분자 subtype(LumA/B/HER2-E/Basal) 예측, **동일 TCGA-BRCA+CPTAC-BRCA + HER2-Warwick, 공개코드(github.com/uit-hdl/BC_MolSubtyping)**. macro-F1 0.73. *가장 위험한 직접 baseline — 반드시 벤치마크 비교.*
- **schmauch-2020-he2rna** (중, Nat Commun): HE2RNA — WSI에서 RNA-Seq 발현 예측, 학습표현이 소규모 코호트로 전이. *PAM50(발현정의)·전이 개념과 직접 평행.*
- **kather-2020-actionable** (중, Nat Cancer): pan-cancer 5천+ 환자, H&E에서 mutation·subtype·발현 signature·biomarker(BRCA ER 포함) 추론. *feasibility 핵심 인용.*
- **fu-2020-pcchip** (중, Nat Cancer): PC-CHiP, 17,355 TCGA 슬라이드·28암종. 학습 형태특징이 genomic aberration·발현·예후와 상관. *형태→분자상관 mechanistic 근거.*
- **coudray-2018-natmed** (중, Nat Med): 폐암 H&E에서 driver mutation 예측(DeepPATH). genotype-from-morphology 시초 PoC(장기는 다름).
- **kather-2019-msi** (중, Nat Med): GI암 H&E에서 MSI(면역항암 적격) 예측. "biomarker→치료적합성" 서사의 원형. *단 ICI 권고 framing은 우리 금지사항(Prohibition).*
- **farahmand-2022-modpathol** (중·SCOOP-THERAPY, Mod Pathol): HER2 상태 + **trastuzumab 반응** 예측(AUC 0.80). *biomarker→치료결과 결합 — 우리 치료가설 목표와 부분 겹침. 차이=cell-line 전이·hypothesis-only·다약물 랭킹.*
- **shamai-2019-jamano** (하, JAMA Netw Open): TMA 기반 호르몬 상태 형태분자 프로파일링(MBMP). 초기 priority 인용(WSI/FM 이전).

## 3. WSI Multiple Instance Learning (MIL) — 슬라이드 집계

추천 baseline: **ABMIL(Ilse 2018, gated-attention)**를 1차 attention-MIL baseline("MLP→attention MIL" 진행과 정확히 일치) + **CLAM(Lu 2021)** 표준 비교. TransMIL·DTFD-MIL은 "단순 attention으로 충분한가" 비교(특히 DTFD는 ~150슬라이드 소코호트에 적합).

- **ilse-2018-abmil** (상, ICML·unverified): attention-MIL 정전. 학습가능·순열불변 (gated) attention pooling + 해석성. *우리 1차 attention-MIL baseline.*
- **lu-2021-clam** (상, Nat Biomed Eng): CLAM — 슬라이드 라벨만으로 약지도 분류, attention pooling + instance clustering, 다중클래스 지원. 표준 파이프라인. *PAM50 다중클래스에 표준 비교.*
- **shao-2021-transmil** (상, NeurIPS·unverified): TransMIL — i.i.d. 가정 깨고 타일 간 상관 모델링(self-attention+PPEG+Nyström). 표준 transformer-MIL 집계자.
- **li-2021-dsmil** (중, CVPR·unverified): DSMIL — max-pool critical instance + attention 이중스트림, SSL 대비학습 타일특징. 추가 비교자.
- **zhang-2022-dtfdmil** (중, CVPR·unverified): DTFD-MIL — pseudo-bag으로 소코호트 문제 완화, 이중티어 distillation. *~150슬라이드 BRCA에 직접 관련.*
- **wagner-2023-transformer** (하, Cancer Cell·unverified): 완전 transformer 추출+집계로 대장암 biomarker 예측. transformer-MIL 방향 지지(BRCA 아님 → 맥락).

## 4. 형태/전사체 → 약물반응 · DepMap/GDSC 전이 (DRUG)

- **dawood-2024-hids** (상·SCOOP-HIGHEST, npj Precision Oncology): ★최근접 prior work. H&E WSI(TCGA-BRCA 551) → 427약물 민감도(cell-line 발현 매핑 imputation) → SlideGraph∞ GNN. *반드시 "최초 H&E→약물민감도" framing 회피; 표현형-중간단계·Critic 게이트·PRISM/GDSC 일관성을 delta로.*
- **corsello-2020-prism** (상, Nat Cancer): PRISM — 4,518약물 × 578 cell line viability. 분자특징으로 선택적 민감도 예측. *DepMap PRISM 정의 인용.*
- **iorio-2016-gdsc** (상, Cell): GDSC pharmacogenomic landscape. cell line이 종양 oncogenic 변이 재현 → 전이의 생물학적 근거. *GDSC 정의 인용.*
- **geeleher-2014-transfer** (상, Genome Biol): 종양 발현 → cell-line 유래 약물민감도 전이의 방법론 원형(Dawood가 차용). *우리 표현형→민감도 bridge의 개념적 조상.*
- **yang-2013-gdsc** (중, NAR): GDSC DB 원 논문. Iorio 2016과 함께 GDSC provenance.
- **geeleher-2014-prrophetic** (중, PLOS ONE): pRRophetic R 패키지 — 발현→cell-line 민감도 imputation 표준 도구.
- **barretina-2012-ccle** (중, Nature): CCLE — 947 cell line 멀티오믹스+약리. DepMap 기반.
- **tsherniak-2017-depmap** (중, Cell): DepMap 정의(RNAi/CRISPR dependency). 약물민감도 전이 보완하는 dependency framing.
- **pcr-nac-brca-2022** (중, The Breast·unverified): biopsy WSI로 BRCA NAC pCR 예측. *대조: 관측된 반응 라벨 사용 vs 우리는 라벨 없이 cell-line 전이로 가설.*
- **sharifi-2019-moli** (하·DRP-CONTRAST, Bioinformatics): MOLI — 멀티오믹스 DRP. *Prohibition #6 대조: 우리는 약물구조/약물별 오믹스 입력 없음.*
- **deepdr-2024-library** (하·DRP-CONTRAST, unverified): 약물+세포 인코더 DRP 라이브러리. 우리가 의도적으로 안 쓰는 mainstream DRP 대조.

## 5. 데이터셋 · DB · 벤치마크 (DATA)

- **tcga-cdr-liu-2018** (상, Cell): TCGA-CDR — 11,160 환자 표준화 생존 엔드포인트(OS/PFI/DFI/DSS). *leakage-safe 임상라벨 표준 (우리가 받은 clinical_patient_brca의 상위 통합표).*
- **tcga-brca-2012** (상, Nature): TCGA-BRCA 코호트 정의 — WSI + ER/PR/HER2/PAM50 라벨, 4개 subtype. *주 학습 코호트 marker paper.*
- **parker-2009-pam50** (상, JCO): PAM50 — 50유전자 intrinsic subtype 분류기. *PAM50 라벨 정의 기준.*
- **hest-1k-jaume-2024** (상, NeurIPS): HEST-1k — 1,229 ST+WSI 페어 + HEST-Benchmark(형태→발현). *FM 임베딩 외부 벤치마크.*
- **cptac-mertins-2016** (중, Nature): CPTAC-BRCA proteogenomics. *외부검증 코호트(TCGA train→CPTAC test), 영상은 NCI IDC.*
- **cbioportal-cerami-2012** / **gao-2013** (중, Cancer Discov / Sci Signal): cBioPortal — TCGA/CPTAC mutation·CNA·발현·임상/IHC 라벨 접근층(+API). 둘 함께 인용.
- **camelyon16-bejnordi-2017** (하, JAMA): CAMELYON16 — 림프절 전이 WSI 벤치마크. tiling/약지도 sanity.
- **pcam-veeling-2018** (하, MICCAI): PatchCamelyon — 327k 패치 이진분류. 임베딩 linear-probe 빠른 점검.
- **bach-aresta-2019** (하, Med Image Anal): BACH — BRCA 조직 4분류. 유방 형태 인코더 검증.
- **breakhis-spanhol-2016** (하, IEEE TBME): BreakHis — BRCA 양/악성 현미경 이미지. 보조 인코더 검증.

---

## 검증 플래그 (인용 전 확인)
- `unverified` DOI: Virchow2, H-optimus-0, Phikon-v2, EXAONE Path 2.0, Neidlinger, ABMIL/TransMIL/DSMIL/DTFD(학회 proceedings — DOI 없음, arXiv/proceedings URL로 인용), Wagner 2023, pcr-nac-brca-2022, DeepDR, shamai-2019(article ID로 추정).
- 학회논문은 `10.xxxx` DOI 날조 금지 — proceedings/arXiv로 인용.
- CrossRef 확인됨: UNI, Prov-GigaPath, Virchow, CONCH, Campanella, CLAM, Naik 2020, Gamble 2021, Shamai 2024, Kather 2020, Tafavvoghi 2024, Farahmand 2022, Corsello 2020, Iorio 2016, Liu 2018, TCGA 2012, Parker 2009, Mertins 2016, Cerami 2012, Gao 2013.

---

# 추가 6영역 (v0.2, 2026-06-09) — C(레드오션 정교화)·D(치료가설 근거)에서 도출

novelty 종합·실험 설계는 [`../novelty_positioning.md`](../novelty_positioning.md) 참조. 아래는 영역별 핵심(상위 위주, 초록은 1–2문장 압축; 전체 인덱스는 papers.csv).

## 6. 엄밀성 — site 교란·누수·일반화 (RIGOR) ★우리 최강 방어축
- **howard-2021-site-signatures** (상, Nat Commun): TCGA가 제출기관별 histology 시그니처를 인코딩, 색정규화·증강으로도 안 지워짐 → 생존/변이/병기 예측 지표 부풀림. **quadratic-programming site-preserved split** 제안. *모든 ER/PR/HER2/PAM50 모델에 site-disjoint split 적용.*
- **bussola-2020-patientlevel** (상, medRxiv): 슬라이드/타일 pooling 후 random split = 누수. patient-level 분리가 최소요건. *split_policy_v0 정당화.*
- **dolezal-2022-uncertainty** (중, Nat Commun): dropout 신뢰도 threshold(train에서만 설정)로 high-confidence subset 보고 + 다기관 외부검증. *TCGA→CPTAC 외부검증 템플릿.*
- **murchan-2024-combat** (중): patch 임베딩에 ComBat 배치보정(train에서만 fit). site-disjoint split 보완책.
- **wagner-2023-reproducibility** (중, Mod Pathol): cpath 161편 중 ~42편만 코드 공개. 재현성 체크리스트 → 우리 experiment artifact 정책 동기.
- **yagis-2021-mri-leakage** (하): slice vs subject split이 정확도 29–55% 부풀림(타 모달리티 교차증거).
- **otalora-2019-stain-invariant** (하): domain-adversarial staining-invariant 학습. 증강/정규화는 site-split의 보완(대체 아님).

## 7. 치료가설 근거 — DepMap/GDSC 외 (HYPO)
- **subramanian-2017-lincs** (상, Cell): LINCS L1000 130만+ perturbation profile, clue.io 연결성 점수. *예측 표현형 시그니처를 역전시키는 약물 랭킹 = 민감도 전이와 독립적인 2번째 경로.*
- **lamb-2006-cmap** (상, Science): Connectivity Map 원형, KS 기반 연결성 점수. 시그니처-역전 패러다임의 방법론적 기원.
- **seashore-2015-ctrp** (중, Cancer Discov): CTRP — 860 cell line × 481 compound. *GDSC/PRISM와 독립인 3번째 일관성 DB.*
- **rees-2016-ctrp-moa** (중, Nat Chem Biol·unverified): basal 발현↔민감도 상관으로 MOA. CTRP 동반 인용.
- **vlachogiannis-2018-pdo** (중, Science): 환자유래 organoid가 임상반응 추적(GI). *cell-line 외 직교 모델계 — BRCA 아님, 방법론 선례로만.*
- **holbeck-2017-almanac** (하): NCI-ALMANAC 약물 조합. 조합 가설 확장 시만.

## 8. Actionability·경로 지식베이스 (KB) — Critic #5 생물학적 타당성
- **chakravarty-2017-oncokb** (상, JCO PO): 체세포 변이→FDA/가이드라인 약물(Level 1–4). *actionability oracle. 단 토큰/라이선스 gated.*
- **griffith-2017-civic** (상, Nat Genet): 오픈(CC0) 변이-약물-질병 evidence + provenance. OncoKB 교차검증 공개 소스.
- **ochoa-2023-opentargets** (상, NAR): target-disease 연관 점수 + tractability. "이 유전자가 이 질환의 신뢰할 표적인가" 정량 grounding.
- **freshour-2021-dgidb** (중, NAR): drug-gene interaction 41소스. 표현형 driver→약물 매핑 확장.
- **liberzon-2015-msigdb** (중, Cell Sys): Hallmark 50 gene set. pathway-activity 어휘.
- **gillespie-2022-reactome** (중, NAR): 큐레이션 human pathway. 약물 표적↔표현형 유전자 공유 경로 검증.
- **whirlcarrillo-2021-pharmgkb** (하)·**kanehisa-2000-kegg** (하): PGx / KEGG pathway·drug 보조.

## 9. 불확실성·해석성 (UQ) — 가설 게이팅
- **olsson-2022-conformal** (상, Nat Commun): conformal prediction으로 유한표본 coverage 보장, 신뢰불가 예측 flag(재학습 불필요). *저신뢰 표현형 가설 기각.*
- **dolezal-2022-uncertainty** (상): MC-dropout 신뢰도 게이팅(§6 참조).
- **guo-2017-calibration** (상, ICML): temperature scaling — 신뢰도 thresholding 전 최소 recalibration.
- **lakshminarayanan-2017-ensembles** (중)·**gal-2016-dropout** (중): deep ensemble / MC-dropout 불확실성 baseline.
- **wang-2025-truecam** (중, arXiv·preprint): FM WSI(UNI/CONCH)+OOD+conformal 통합 — **가장 가까운 blueprint, 인용+차별화 필수**.
- **angelopoulos-2021-conformal-intro** (중): conformal 구현 레시피.
- **graziani-2018-rcv** (중)·**kim-2018-tcav** (하): concept attribution(형태→분자상태 해석). 단 attention map은 필요조건일 뿐(오위치 가능) → 탐색적 flag로 제시.

## 10. Stain 정규화·전처리 (PREP)
- **macenko-2009** (상): de-facto 정규화 baseline(OD+SVD). robustness ablation 기준.
- **tellez-2019** (상, Med Image Anal): 정규화 vs 증강 결정적 비교 — **heavy stain augmentation이 단일 최선**, 증강+정규화 조합이 최고. *정규화 단독 의존 회피 근거.*
- **vahadane-2016** (중): 구조보존 정규화(2nd ablation 옵션). **reinhard-2001** (중): 최저비용 정규화(FM center-robustness +16% 보고).
- **dejong-2025-robustness** (하, arXiv): 10개 FM 모두 medical-center 시그니처 인코딩(UNI 포함), Robustness Index. site-aware split 정당화.

## 11. AI 에이전트·LLM-as-judge (AGENT) — 시스템/Critic 포지셔닝
- **gottweis-2025-coscientist** (상·SCOOP-FRAMING, arXiv): Google AI co-scientist — 전문 에이전트 generate-debate-evolve+토너먼트. *"멀티에이전트+critic 가설생성" framing을 선점·포섭. 우리는 도메인 거버넌스로만 차별화, 패러다임 발명 주장 금지.*
- **lu-2024-aiscientist** (상): Sakana 완전자동 연구 — 자율성 대조군(우리는 의도적 hypothesis-only·인간 거버넌스).
- **zheng-2023-llmjudge** (상, NeurIPS): LLM-as-judge 검증 + 편향(position/verbosity/self-enhancement). *Critic=LLM-judge 정당화 + owner≠reviewer 근거.*
- **panickssery-2024-selfpreference** (상, NeurIPS): LLM이 자기 출력을 인식·선호(인과 증거). *anti-self-reference 규칙의 가장 강한 단일 근거.*
- **qi-2024-biohypo** (중)·**su-2024-virsci** (중): 생의학 가설생성/멀티에이전트 idea novelty. 시스템-as-novelty는 crowded → 공학·거버넌스 기여로.
- **li-2024-judge-survey** (중)·**hkust-2025-sciagent-survey** (중)·**eval-2025-sakana** (하)·**guo-2024-multiagent-survey** (하): 서베이/비판 맥락.

> ⚠️ AGENT 영역 arXiv 다수 = preprint(DOI unverified). 미래 날짜 arXiv ID(2601.x 등 환각) 인용 금지 — 조사에서 제외 확인됨.

---

## 다음 단계
1. ✅ 추가 6주제 조사 완료 → 리스트 보강(v0.2)
2. 상위 우선순위(SCOOP 후보 Dawood·Tafavvoghi + 백본 UNI·CLAM + 엄밀성 Howard + 경로 Subramanian·OncoKB)부터 BioProject01 멀티렌즈 상세분석
3. ✅ 타겟 저널 = npj Precision Oncology / novelty·실험 = novelty_positioning.md
