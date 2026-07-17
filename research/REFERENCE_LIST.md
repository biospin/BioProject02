# BioProject02 참고문헌 리스트 (인용 대상)

> 논문 집필 시 실제 인용할 문헌을 섹션 역할별로 정리. 상태: **DEEP**(4-lens 심층)·brief(초록/약식)·stub(미분석). `research/<topic>/<slug>/`에 분석 존재.
> 자동생성(paper-info.yaml 기준) + 갭(인용됐으나 미분석)은 §마지막. 최종갱신 2026-07-17.


## §Intro/Related — H&E→분자 예측(선행·스쿱)  (phenotype-prediction, 11편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| **DEEP** | tafavvoghi-2024-jpi | 2024 | Journal of Pathology Informa | Deep learning-based classification of breast cancer  |
| brief | shamai-2024-commsmed | 2024 | Communications Medicine | Clinical utility of receptor status prediction and m |
| brief | farahmand-2022-modpathol | 2022 | Modern Pathology | Deep learning trained on H&E tumor ROIs predicts HER |
| brief | gamble-2021-commsmed | 2021 | Communications Medicine | Determining breast cancer biomarker status and assoc |
| brief | schmauch-2020-he2rna | 2020 | Nature Communications | A deep learning model to predict RNA-Seq expression  |
| brief | naik-2020-natcommun | 2020 | Nature Communications | Deep learning-enabled breast cancer hormonal recepto |
| brief | kather-2020-actionable | 2020 | Nature Cancer | Pan-cancer image-based detection of clinically actio |
| brief | fu-2020-pcchip | 2020 | Nature Cancer | Pan-cancer computational histopathology reveals muta |
| brief | kather-2019-msi | 2019 | Nature Medicine | Deep learning can predict microsatellite instability |
| brief | couture-2018-npjbc | 2018 | npj Breast Cancer | Image analysis with deep learning to predict breast  |
| brief | coudray-2018-natmed | 2018 | Nature Medicine | Classification and mutation prediction from non-smal |

## §Related/Paper B — H&E→약물·cell-line  (morphology-drug, 9편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| **DEEP** | dawood-2024-hids | 2024 | npj Precision Oncology | Cancer drug sensitivity prediction from routine hist |
| brief | pcr-nac-brca-2022 | 2022 | The Breast | Deep learning with biopsy whole slide images for pre |
| brief | corsello-2020-prism | 2020 | Nature Cancer | Discovering the anticancer potential of non-oncology |
| brief | tsherniak-2017-depmap | 2017 | Cell | Defining a Cancer Dependency Map (DepMap) |
| brief | iorio-2016-gdsc | 2016 | Cell | A Landscape of Pharmacogenomic Interactions in Cance |
| brief | geeleher-2014-transfer | 2014 | Genome Biology | Clinical drug response can be predicted using baseli |
| brief | geeleher-2014-prrophetic | 2014 | PLOS ONE | pRRophetic: an R package for prediction of clinical  |
| brief | yang-2013-gdsc | 2013 | Nucleic Acids Research | Genomics of Drug Sensitivity in Cancer (GDSC): a res |
| brief | barretina-2012-ccle | 2012 | Nature | The Cancer Cell Line Encyclopedia enables predictive |

## §Data — 코호트·라벨  (datasets-benchmarks, 7편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| brief | hest-1k-jaume-2024 | 2024 | NeurIPS 2024 | HEST-1k: A Dataset for Spatial Transcriptomics and H |
| **DEEP** | tcga-cdr-liu-2018 | 2018 | Cell | An Integrated TCGA Pan-Cancer Clinical Data Resource |
| brief | cptac-mertins-2016 | 2016 | Nature | Proteogenomics connects somatic mutations to signall |
| brief | cbioportal-gao-2013 | 2013 | Science Signaling | Integrative Analysis of Complex Cancer Genomics and  |
| brief | tcga-brca-2012 | 2012 | Nature | Comprehensive molecular portraits of human breast tu |
| brief | cbioportal-cerami-2012 | 2012 | Cancer Discovery | The cBio Cancer Genomics Portal: an open platform fo |
| brief | parker-2009-pam50 | 2009 | Journal of Clinical Oncology | Supervised Risk Predictor of Breast Cancer Based on  |

## §Methods — 임베딩(FM)  (foundation-models, 10편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| brief | lgai-2025-exaonepath2 | 2025 | arXiv 2507.06639 | EXAONE Path 2.0: Pathology Foundation Model with End |
| brief | campanella-2025-clinicalbench | 2025 | Nature Communications | A clinical benchmark of public self-supervised patho |
| brief | zimmermann-2024-virchow2 | 2024 | arXiv 2408.00738 | Virchow2: Scaling Self-Supervised Mixed Magnificatio |
| brief | xu-2024-provgigapath | 2024 | Nature | A whole-slide foundation model for digital pathology |
| brief | vorontsov-2024-virchow | 2024 | Nature Medicine | A foundation model for clinical-grade computational  |
| brief | saillard-2024-hoptimus0 | 2024 | Model release | H-optimus-0: an open-source ViT-Giant pathology foun |
| brief | neidlinger-2024-fmbenchmark | 2024 | arXiv 2408.15823 | Benchmarking foundation models as feature extractors |
| brief | lu-2024-conch | 2024 | Nature Medicine | A visual-language foundation model for computational |
| brief | filiot-2024-phikonv2 | 2024 | arXiv 2409.09173 | Phikon-v2: A large and public feature extractor for  |
| **DEEP** | chen-2024-uni | 2024 | Nature Medicine | Towards a general-purpose foundation model for compu |

## §Methods — MIL 집계  (wsi-mil, 5편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| brief | zhang-2022-dtfdmil | 2022 | CVPR 2022 | DTFD-MIL: Double-Tier Feature Distillation MIL for W |
| brief | shao-2021-transmil | 2021 | NeurIPS 2021 | TransMIL: Transformer based Correlated MIL for WSI C |
| **DEEP** | lu-2021-clam | 2021 | Nature Biomedical Engineerin | Data-efficient and weakly supervised computational p |
| brief | li-2021-dsmil | 2021 | CVPR 2021 | Dual-stream MIL Network for WSI Classification with  |
| brief | ilse-2018-abmil | 2018 | ICML 2018 | Attention-based Deep Multiple Instance Learning |

## §Methods/Limitation — 누수·사이트 통제  (rigor-leakage, 4편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| brief | murchan-2024-combat | 2024 | J Pathol Inform | Deep feature batch correction using ComBat in comput |
| brief | wagner-2023-reproducibility | 2023 | Modern Pathology | Built to Last? Reproducibility and Reusability of De |
| **DEEP** | howard-2021-site-signatures | 2021 | Nature Communications | The impact of site-specific digital histology signat |
| brief | bussola-2020-patientlevel | 2020 | medRxiv | Patient-level data segregation is crucial in clinica |

## §AI layer — 보정·기권  (uncertainty-interpretability, 8편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| brief | wang-2025-truecam | 2025 | arXiv 2501.00053 | TRUECAM: Conformalized Uncertainty-Aware AI for Whol |
| **DEEP** | olsson-2022-conformal | 2022 | Nature Communications | Estimating diagnostic uncertainty in artificial inte |
| brief | dolezal-2022-uncertainty | 2022 | Nature Communications | Uncertainty-informed deep learning enables high-conf |
| brief | angelopoulos-2021-conformal-intro | 2021 | arXiv 2107.07511 | A Gentle Introduction to Conformal Prediction and Di |
| brief | graziani-2018-rcv | 2018 | MICCAI 2018 iMIMIC | Regression Concept Vectors for Bidirectional Explana |
| brief | lakshminarayanan-2017-ensembles | 2017 | NeurIPS 2017 | Simple and Scalable Predictive Uncertainty Estimatio |
| brief | guo-2017-calibration | 2017 | ICML 2017 | On Calibration of Modern Neural Networks |
| brief | gal-2016-dropout | 2016 | ICML 2016 | Dropout as a Bayesian Approximation: Representing Mo |

## §Paper B(보류) — 수렴 근거축  (hypothesis-support, 5편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| brief | vlachogiannis-2018-pdo | 2018 | Science | Patient-derived organoids model treatment response o |
| **DEEP** | subramanian-2017-lincs | 2017 | Cell | A Next Generation Connectivity Map: L1000 Platform a |
| brief | rees-2016-ctrp-moa | 2016 | Nature Chemical Biology | Correlating chemical sensitivity and basal gene expr |
| brief | seashore-2015-ctrp | 2015 | Cancer Discovery | Harnessing Connectivity in a Large-Scale Small-Molec |
| brief | lamb-2006-cmap | 2006 | Science | The Connectivity Map: using gene-expression signatur |

## §Paper B(보류) — 생성/채점 KB  (knowledge-bases, 6편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| brief | ochoa-2023-opentargets | 2023 | Nucleic Acids Research | The next-generation Open Targets Platform: reimagine |
| brief | gillespie-2022-reactome | 2022 | Nucleic Acids Research | The Reactome Pathway Knowledgebase 2022 |
| brief | freshour-2021-dgidb | 2021 | Nucleic Acids Research | Integration of the Drug-Gene Interaction Database (D |
| brief | griffith-2017-civic | 2017 | Nature Genetics | CIViC is a community knowledgebase for expert crowds |
| **DEEP** | chakravarty-2017-oncokb | 2017 | JCO Precision Oncology | OncoKB: A Precision Oncology Knowledge Base |
| brief | liberzon-2015-msigdb | 2015 | Cell Systems | The Molecular Signatures Database (MSigDB) Hallmark  |

## §Critic/거버넌스(방법)  (ai-agents, 8편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| brief | hkust-2025-sciagent-survey | 2025 | arXiv 2503.24047 | Towards Scientific Intelligence: A Survey of LLM-bas |
| **DEEP** | gottweis-2025-coscientist | 2025 | arXiv preprint (not peer-rev | Towards an AI co-scientist |
| brief | su-2024-virsci | 2024 | ACL 2025 | Many Heads Are Better Than One: Improved Scientific  |
| brief | qi-2024-biohypo | 2024 | COLM 2024 | Large Language Models as Biomedical Hypothesis Gener |
| brief | panickssery-2024-selfpreference | 2024 | NeurIPS 2024 | LLM Evaluators Recognize and Favor Their Own Generat |
| brief | lu-2024-aiscientist | 2024 | arXiv 2408.06292 | The AI Scientist: Towards Fully Automated Open-Ended |
| brief | li-2024-judge-survey | 2024 | arXiv 2411.16594 | From Generation to Judgment: Opportunities and Chall |
| brief | zheng-2023-llmjudge | 2023 | NeurIPS 2023 | Judging LLM-as-a-Judge with MT-Bench and Chatbot Are |

## §Methods — stain norm  (preprocessing, 4편)

| 상태 | 문헌 | 연도 | venue | 제목 |
|---|---|---|---|---|
| brief | tellez-2019 | 2019 | Medical Image Analysis | Quantifying effects of data augmentation and stain c |
| brief | vahadane-2016 | 2016 | IEEE TMI | Structure-Preserving Color Normalization and Sparse  |
| brief | macenko-2009 | 2009 | IEEE ISBI 2009 | A Method for Normalizing Histology Slides for Quanti |
| brief | reinhard-2001 | 2001 | IEEE CG&A | Color Transfer between Images |

---
**분석 완료 총 77편** (DEEP 10 · brief 67 · stub 0)
---

## 갭 초록분석 — 완료 (2026-07-17, 실제 초록 fetch + Crossref 대조)

인용됐으나 미분석이던 문헌 8편의 초록분석 완료. **적대적 검증으로 우리 문서 인용 오류 5건 발견 → `CITATION_CORRECTIONS_2026-07-17.md`.**

| 상태 | 문헌(확정 서지) | slug | 우리 논문에서 |
|---|---|---|---|
| brief | **Fernandez-Romero 2026** — Domain generalisation…FM (Med Biol Eng Comput 64) | fernandez-romero-2026-domaingen | 최근접 스쿱(유방 subtype, 외부열화) → 치환프레임 pivot |
| brief | **Kaczmarzyk 2026 (MAKO)** — ROR-P 재발위험 예측 (npj Digital Med 9:149) | kaczmarzyk-2026-mako | "예측 포화" 근거(⚠️ subtype 아니라 ROR-P) |
| brief | **Shulman 2026 (Path2Space)** — AI 공간전사체 (Cell 189, 교신 Ruppin) | shulman-2026-path2space | 반대방향(복원 vs 치환 audit) ⚠️문서엔 "Kaminski" 오기 |
| brief★ | **Farahmand 2022** (Mod Pathol 35:44) | farahmand-2022-modpathol | **Yale 앵커 head-to-head 바 = trastuzumab반응 CV AUC 0.80** (HER2 CV0.90/외부0.81) |
| brief | **Huang 2023 (IMPRESS)** (npj PO 7:14) | huang-2023-impress | 타겟저널 선례. HER2+ 0.90/TNBC 0.77(dev), ⚠️TNBC 외부 0.59 붕괴 |
| brief | **Sammut 2022 (TransNEO)** (Nature 601:623) | sammut-2022-transneo | 2차 앵커·다중오믹 pCR 외부 AUC 0.87 |
| brief | **Sharifi-Noghabi 2021** (Brief Bioinform 22(6) bbab294) | sharifi-noghabi-2021-crossdataset | 약물축 독립성 ⚠️문서 인용 오류(연도·PMC·수치) |
| NOT FOUND | ~~Williams 2022 LINCS~~ | williams-2022-lincs-reversal | 실존 미확인 — 서지 재확인 or 삭제 |

> ⚠️ **인용 오류 5건은 `CITATION_CORRECTIONS_2026-07-17.md` 참조** — 논문 집필 전 정정 필수.

## ★ 이 논문(C flagship + 유방 anchor + Yale outcome) 핵심 인용 (요약)

- **차별화 대상(스쿱):** dawood-2024-hids(H&E→약물), Fernandez-Romero 2026(유방 subtype), MAKO 2026 → "예측은 포화, 우리는 치환-비용 결정프레임".
- **실증 이빨:** Farahmand 2022(Yale, head-to-head) + Huang 2023/Sammut 2022(neoadjuvant 결과).
- **방법 백본:** chen-2024-uni(임베딩) · lu-2021-clam(MIL) · howard-2021(사이트누수 통제) · parker-2009-pam50/tcga-brca-2012(라벨).
- **cross-cancer 선행:** kather-2019-msi · coudray-2018 · (대장 imCMS·Buikhuisen 등 추가 갭 가능).

---

## 심층분석(4-lens) 후보 — 재선정 (2026-07-17)

**선정 기준:** ① 정밀 차별화가 필요한 스쿱 ② 재현/head-to-head 벤치마크가 필요한 방법·baseline. **이미 DEEP인 것 제외**(UNI·CLAM·Howard·Dawood·LINCS·OncoKB·TCGA-CDR·tafavvoghi·conformal·co-scientist). 현재 논문 = C flagship(치환비용 결정지도) + 유방 anchor + Yale 실제결과 앵커, B엔진 보류.

### Tier 1 — 핵심 (앵커·스쿱 방어, 없으면 논문 방어 불가)
| 후보 | 왜 심층 | 산출(methodology-brief) |
|---|---|---|
| **Farahmand 2022** (Mod Pathol) | **우리가 임베딩 중인 바로 그 Yale 데이터로 H&E→HER2+trastuzumab 반응**을 한 head-to-head. 그들 방법·AUC를 정밀히 알아야 우리 항HER2 축 결과를 위치지음 | tumor-ROI 파이프라인·HER2 AUC·trastuzumab-반응 AUC = 우리가 넘어야 할 바 |
| **Fernandez-Romero 2026** | A→C 흡수를 촉발한 **유방 subtype 예측 스쿱**. 리뷰어 "이미 됐잖아" 방어의 정밀 근거 | 그들(예측) vs 우리(치환비용) 차별화 표 |

### Tier 2 — 높은 값 (벤치마크·저널 선례)
| 후보 | 왜 심층 | 산출 |
|---|---|---|
| **MAKO 2026** | H&E→ER/PR/HER2/PAM50 벤치마크 선점 → "예측은 포화" 주장의 정량 근거 | 선행 성능 바 표 |
| **Huang 2023 (IMPRESS)** | **타겟저널(npj PO)**의 H&E→치료반응 게재 선례(n~126) | 우리 논문 구조·수용 바 모델링 |

### Tier 3 — 조건부
- **Sammut 2022 (TransNEO)** — 2차 아웃컴 앵커로 실제 채택 시에만.
- **cross-cancer 선행 심층**(kather-2019-msi DEEP 승격 + imCMS/Sirinukunwattana·Buikhuisen 신규) — flagship의 대장/타암종 결정지도에 깊은 선행 절이 필요할 때만.

> 실행 게이트: 초록분석(진행 중) 결과로 각 후보의 정체·관련성 확정 → 그 뒤 go 결정. 심층분석 실행 = 분석 하네스(BIOP01 `kkkim-paper-agent` 브랜치) 복원 후 4-lens 파이프라인.
