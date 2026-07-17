# 인용 재검증 감사 (Citation Re-Verification Audit) — 2026-07-17

> 목적: 이전 참고문헌 감사가 5건의 인용 오류(Sharifi-Noghabi 연도+PMC, 실존 없는 "Williams 2022", Path2Space 1저자 "Kaminski" 오기, MAKO 스코프 오해)를 잡았고, **"제공된 식별자 다수가 틀렸으니 나머지 인용도 유사 오류를 가질 수 있다"**는 경고를 남겼다. 이에 따라 3개 포지셔닝 문서의 **나머지 인용을 실제 권위 소스(Crossref API + NCBI eutils/PubMed/PMC)로 1건씩 재검증**한다.
> 방법: 각 인용의 DOI→Crossref(1저자·연도·저널·권/쪽·제목), PMID/PMCID→NCBI esummary로 대조. **양성 검증한 것만 "정확/오류"로 단정하고, 검증 불가는 "미확인"으로 남긴다(추정·창작 금지).**
> 범위: `therapeutic_layer_strengthening.md`, `paperA-positioning/2026-07-10_novelty-scoop-analysis.md`, `paperC-positioning/2026-07-12_CRC-LUNG-ST-scoop-and-data.md`. 이미 `research/*/paper-info.yaml`로 검증된 논문은 문서가 상충 식별자로 인용한 경우에만 재검증.

## 요약 (counts)
- **정확(verified OK): 33건** — 식별자(DOI/PMID/PMCID/PII) 보유 인용 전부 포함. 신규 오류 **0건**.
- **오류(error): 0건** (신규). 이전 5건은 `CITATION_CORRECTIONS_2026-07-17.md`에서 이미 정정됨(재검증 결과 정정본이 맞음 — 아래 참조).
- **미확인(unverified): 1건** — Ding 2025(Cancer Biol Med, 특정 논문 확인 불가). *문서가 `[snippet, unverified]`로 자체 플래그했던 Lancet Oncol 2025·PANProfiler은 본 감사에서 독립 검증에 성공 → 정확으로 승격.*
- **자원(비-서지): 1건** — DepMap/Chronos(포털, 논문 인용 아님).
- **핵심 결론:** 이전 감사의 "나머지도 틀릴 수 있다" 경고에 대한 답 = **나머지 식별자-보유 인용은 모두 정확.** 특히 (1) 정정 문서가 후속 재검증 대상으로 남겨둔 **Farahmand PMC10221954는 정확함을 확인**(open item 종결), (2) 문서가 unverified로 남겼던 **Lancet Oncol 2025·PANProfiler도 실존·서지 일치 확인**. 오류는 이미 잡힌 5건에 국한.
- **참고(범위 명확화):** 감사 지시가 예시로 든 "Coudray"는 3개 문서에 없음 — 문서는 **Couture**(npj Breast Cancer 2018, 검증됨)를 인용. 지시의 Coudray(Nat Med 2018, `phenotype-prediction/coudray-2018-natmed/`)는 이 3개 문서에 미인용이라 대상 아님(이름 혼동으로 판단). Liu Cell 2018은 문서 표기 PII `S0092-8674(18)30229-0`가 Crossref alternative-id `S0092867418302290`와 일치함까지 확인.

---

## 감사 표

| 문헌(문서 표기) | 위치 | 검증결과 | 정확 서지(오류 시)/근거 | 조치 |
|---|---|---|---|---|
| **Farahmand, Mod Pathol 2022 / PMC10221954** | therapeutic §A, Sources | **정확** | PMC10221954 = Farahmand S, *Mod Pathol* 35(1):44–51, 2022 (epub 2021-09-07), DOI 10.1038/s41379-021-00911-w. PMID/PMC 대조 일치 | **정정 불요.** 정정문서 후속권고(§23 "PMC10221954 재검증") **종결** |
| **Sammut, Nature 601:623 (2022)** | therapeutic §A, Sources | **정확** | Sammut, Stephen-John, *Nature* 601(7894):623–629, 2022, DOI 10.1038/s41586-021-04278-5 | — |
| **Huang, npj PO 7:14 (2023) IMPRESS** | therapeutic §A; novelty §8 | **정확** | Huang, Zhi, *npj Precision Oncology* 7, article 14, 2023, DOI 10.1038/s41698-023-00352-5 (권7·article-no 14 일치) | — |
| **Liu, Cell (2018) TCGA-CDR** | therapeutic §A, Sources | **정확** | Liu, Jianfang, *Cell* 173(2):400–416.e11, 2018, DOI 10.1016/j.cell.2018.02.052 (TCGA Pan-Cancer Clinical Data Resource) | — |
| **Sharifi-Noghabi 2021, bbab294** | therapeutic §B | **정확**(기정정) | Sharifi-Noghabi, Hossein, *Brief Bioinform* 22(6) bbab294, 2021, DOI 10.1093/bib/bbab294 | 이미 정정됨 — 유지. (⚠️ 본문 수치 CTRPv2→gCSI 0.40±0.21·GDSCv1→gCSI 0.26±0.16는 이전 감사 검증치이며 **본 감사에서 원문 수치까지 재확인하진 않음** — 식별자만 검증) |
| **Koudijs 2023, bbac490 (reversal caveat)** | therapeutic §B 축3 | **정확** | Koudijs, Karel K M, *Brief Bioinform* 24, 2023, "Validation of transcriptome signature reversion for drug repurposing in oncology", DOI 10.1093/bib/bbac490 — 제목이 문서의 "reversal 과대평가 경고" 프레이밍과 정합 | — |
| **Dawood 2024, npj PO** | therapeutic §C; novelty §2/§3/§7 | **정확** | Dawood, Muhammad, *npj Precision Oncology* 8, 2024, "Cancer drug sensitivity prediction from routine histology images", DOI 10.1038/s41698-023-00491-9 | — |
| **Lamb 2006 CMap · Subramanian 2017 LINCS** | therapeutic §B/Sources | **정확(기존 paper-info)** | 문서가 식별자 없이 인용, `hypothesis-support/*paper-info.yaml` 존재·비상충 → 지시대로 재검증 생략 | — |
| **Xu 2021, BCNB** | therapeutic §A | **정확** | Xu, *Front Oncol* 2021, "Predicting Axillary Lymph Node Metastasis in Early Breast Cancer Using Deep Learning on Primary Tumor Biopsy Slides" (BCNB 데이터셋 원논문). 1저자 Xu·연도 2021 일치 | — |
| **DepMap / Chronos** | therapeutic §B 축2, Sources | **자원(비-서지)** | 포털·알고리즘 자원(depmap.org). 특정 논문 인용 아님 → 서지 감사 대상 아님 | (선택) 알고리즘 인용 필요 시 Dempster 2021 *Genome Biol* 명시 |
| **Fernandez-Romero 2026, MBEC / PMID 42113320 / PMC13269319** | novelty §0/§2/§4①/§7 | **정확** | Fernandez-Romero, Jesus, *Med Biol Eng Comput* 64:2321–2331, 2026, DOI 10.1007/s11517-026-03590-4. PMID·PMCID 모두 동일 논문으로 해석(vol 64 일치) | — |
| **Shamai 2024, Commun Med 4** | novelty §2/§4③/§7 | **정확** | Shamai, Gil, *Communications Medicine* 4, 2024, DOI 10.1038/s43856-024-00695-5 (receptor status + misdiagnosis) | — |
| **Arslan/Kather 2024, Commun Med 4** | novelty §2/§4④/§7 | **정확** | Arslan, Salim, *Communications Medicine* 4, 2024, "systematic pan-cancer study on DL-based prediction of multi-omic biomarkers", DOI 10.1038/s43856-024-00471-5 (1저자 Arslan; Kather group 귀속 타당) | — |
| **Naik 2020, ReceptorNet Nat Commun 11** | novelty §4⑤/§7 | **정확** | Naik, Nikhil, *Nature Communications* 11, 2020, DOI 10.1038/s41467-020-19334-3 | — |
| **Couture 2018, npj Breast Cancer** | novelty §7 | **정확** | Couture, Heather D., *npj Breast Cancer* 4, 2018, DOI 10.1038/s41523-018-0079-1 | — |
| **MAKO = Kaczmarzyk, npj Dig Med 9:149 (2026)** | novelty §4⑦/§8 | **정확** | Kaczmarzyk, Jakub R., *npj Digital Medicine* 9, article 149, DOI 10.1038/s41746-025-02334-2, "…recurrence risk in breast cancer using pathology foundation models" (제목이 ROR-P/재발위험 프레이밍과 정합; 이전 스코프 정정 유효) | — (§4⑦의 arXiv 2604.24679는 문서가 unverified로 자체 표기; 저널판이 확정본) |
| **Lancet Oncol 2025 (recurrence/chemo benefit)** | novelty §4⑥/§7 Sources | **정확**(승격) | PII S1470-2045(25)00727-2 → DOI 10.1016/S1470-2045(25)00727-2 = **Shamai** et al., *The Lancet Oncology*, "Deep learning on histopathological images to predict breast cancer recurrence risk and chemotherapy benefit"(제목 문서와 정합). 문서 unverified 플래그 해제 가능 | 문서 `[snippet, unverified]` 제거 가능. (경미: online-first 2025 / Crossref-issued 2026 — 인용연도 확인. 1저자 Shamai — #3 Shamai와 동일그룹) |
| **PANProfiler Breast, Clin Breast Cancer 2025** | novelty §2/§4⑧ | **정확**(승격) | PII S1526-8209(25)00168-5 = PMID **40645910**, *Clinical Breast Cancer* 2025, "A Deep-Learning Solution Identifies HER2 Negative Cases and Provides ER and PR Results From H&E-Stained Breast Cancer Specimens: A Blind Validation Study"(문서 "PANProfiler blind validation"과 정합) | 문서 `[snippet, unverified]` 제거 가능 |
| **고위험 ER+/HER2− image analysis (PMC11616316)** | novelty §2(b) body + §7 Sources | **정확** | PMC11616316 = Lee DN, *Breast Cancer Res* 26, 2024, "Image analysis-based identification of high risk ER-positive, HER2-negative breast cancers" (문서 "이미지 기반 고위험 ER+/HER2−" 정합) | — |
| **LumA subtype purity (medRxiv 2023)** | novelty §2(b) body + §7 Sources | **정확** | DOI 10.1101/2023.02.27.23286511 = Kumar, *medRxiv* 2023, "Quantification of Subtype Purity in Luminal A Breast Cancer Predicts Clinical Characteristics and Survival" (문서 "LumA subtype purity/admixture, medRxiv 2023" 정합) | — |
| **Breast Cancer Research 2020, intrinsic-subtype ITH (PMC6988279)** | novelty §3 body | **정확** | PMC6988279 = Jaber MI, *Breast Cancer Res* 22, 2020, "A deep learning image-based intrinsic molecular subtype classifier of breast tumors reveals tumor heterogeneity" (문서 "이미지 기반 intrinsic-subtype 분류가 ITH 드러냄" 정합) | — |
| **npj PO 2023, routine-H&E luminal 예후 (s41698-023-00472-y)** | novelty §3 body | **정확** | DOI 10.1038/s41698-023-00472-y = Wahab, *npj Precision Oncology* 2023, "AI-enabled routine H&E image based prognostic marker for early-stage luminal breast cancer" (문서 "routine-H&E 조기 luminal 예후 마커" 정합) | — |
| **Corsello, Nat Cancer 2020 (PMID 32613204)** | novelty §9 | **정확** | Corsello SM, *Nat Cancer* 1:235–248, 2020, "Discovering the anti-cancer potential of non-oncology drugs…" (PRISM 원자원) | — |
| **Lin 2025, BCRT (10.1007/s10549-025-07817-0)** | novelty §9 | **정확** | Lin, Hao-Kuen, *Breast Cancer Res Treat* 214:319–327, 2025 (1저자 Lin; 문서 "Lin/Dai/Pusztai" 정합) | — |
| **Ding/Shao/Yu, Cancer Biol Med 2025 (22/12/1605)** | novelty §9 | **미확인** | PubMed·Crossref(ISSN 2095-3941)에서 해당 CRC-dependency+PRISM 논문을 특정 못함. *Cancer Biol Med*·vol 22(2025)는 실재하나 특정 서지 미확인. **오류로 단정 안 함** | 서지 재확인(권/쪽/DOI 확보) — D3 드롭 트랙이라 우선순위 낮음 |
| **Sannigrahi, Mol Oncol 2023 (PMC10850805)** | novelty §9 | **정확(경미)** | PMC10850805 = Sannigrahi MK, *Mol Oncol* 18, **epub 2023-12-13 / print 2024-02**, "…prioritizing cancer type-specific therapeutic vulnerabilities using DepMap". 문서 "2023"은 online-first 연도로 방어 가능(정식 인용연도는 2024) | (선택) 연도 2024로 표기 통일 |
| **Jurj 2025 (PMC12471285)** | novelty §9 | **정확** | PMC12471285 = Jurj ED, *Medicina (Kaunas)* 61, 2025, "Redefining Breast Cancer Care by Harnessing Computational Drug Repositioning" (리뷰; 문서 "리뷰 Jurj 2025" 정합) | — |
| **Path2Space = Shulman, Cell 189 (2026)** | CRC-LUNG S1, Sources | **정확**(기정정) | Shulman, Eldad D., *Cell* 189:4225–4240.e25, 2026, DOI 10.1016/j.cell.2026.04.023 — 정정문서 #4(Kaminski→Shulman) **재검증 확정** | 이미 정정됨 — 유지 |
| **Valdeolivas 2024, npj PO 8:10** | CRC-LUNG S2, Sources | **정확** | Valdeolivas, Alberto, *npj Precision Oncology* 8, article 10, 2024, DOI 10.1038/s41698-023-00488-4 (권8·article-no 10 일치) | — |
| **Yang, JITC 2025 13:e013763 / PMID 41475845 / PMC12766835** | CRC-LUNG S3, Sources | **정확** | Yang, Sheng, *J Immunother Cancer* 13:e013763, 2025, DOI 10.1136/jitc-2025-013763 (KRAS-mut 면역억제 niche). PMID 41475845·PMC12766835 모두 동일 논문 | — (1저자 Yang; 문서 "Yang, Gu, Miao" 정합) |
| **Pelka, Cell 2021 184:4734 (PMID 34450029)** | CRC-LUNG S4, Sources | **정확** | Pelka K, *Cell* 184:4734–4752.e20, 2021, "Spatially organized multicellular immune hubs in human colorectal cancer" | — |
| **imCMS = Sirinukunwattana, Gut 2021** | CRC-LUNG §1, Sources | **정확** | Sirinukunwattana, *Gut* 70(3):544–554, DOI 10.1136/gutjnl-2019-319866 (imCMS). Crossref issued=2020(online-first), 정식 print=**Gut 2021** → 문서 "2021" 정확 | — |
| **Kather MSI, Nat Med 2019** | CRC-LUNG §1, Sources | **정확** | Kather, Jakob Nikolas, *Nat Med* 25:1054–1056, 2019, DOI 10.1038/s41591-019-0462-y | — |
| **Su 2025, npj PO (PMC11973205)** | CRC-LUNG 부록, Sources | **정확** | Su, Andrew, *npj Precision Oncology* 9, 2025, DOI 10.1038/s41698-025-00853-5, "single-cell spatial landscape of stage III colorectal cancers". PMC11973205 일치 | — |
| **GSE285505 연관 논문 (PMID 41276505)** | CRC-LUNG 부록 | **정확(데이터셋 정합)** | PMID 41276505 = Iwane K, *Nat Commun* 16:11590, 2025, "Targeting fibroblast derived thrombospondin 2… tumor front" — 문서의 "TSP2 invasive front" 라벨과 정합. 데이터셋 포인터로 올바름 | — (문서가 저자명 미표기; 필요 시 Iwane 2025 명시) |

---

## 검증하지 않은 항목(범위 밖) 및 사유
- **arXiv 프리프린트 id** (novelty §3 `2604.01798` NSGA-II, §4⑦ `2604.24679` MAKO-arXiv, §8 `2505.14730` TNBC-pCR; CRC-LUNG `2605.02660` MSI-FM; §3 `2505.13400` Robin·`2504.17967` PharmaSwarm): 문서가 이미 `[snippet, unverified]`/`[VERIFY id]`로 자체 플래그. MAKO는 저널판(위) 확정으로 대체 가능. 나머지는 인용 전 확인 필요(플래그 유지).
- **데이터 accession** (Zenodo 6337925/7551712/11402686/13901180, EGA EGAS00001004582, GSA HRA011642, GEO GSE285505/GSE226997/GSE132465, SCP1162, dbGaP phs002371, TCIA HER2-TUMOR-ROIS): 문헌 서지가 아닌 데이터 접근자 → 본 인용감사 범위 밖(별도 데이터 가용성 검증은 원문 각주에 기록됨).
- **본문 정량 수치**(예: Sharifi-Noghabi cross-domain 상관계수, Farahmand AUC≈0.80, Fernandez-Romero RPD/R²): 식별자 검증에 집중했고 원문 수치 재추출은 하지 않음(0.40±0.21 등은 이전 감사 검증치, Farahmand 0.80은 `phenotype-prediction/farahmand-2022-modpathol/paper-info.yaml`과 정합).

## 조치 권고 (kkkim)
1. **오류 0건** — 3개 문서의 식별자-보유 인용은 원문 그대로 두어도 됨. 별도 정정 불필요.
2. **`CITATION_CORRECTIONS_2026-07-17.md` §23 후속권고 종결** — "Farahmand PMC10221954 등 일괄 재검증"은 본 감사로 완료(Farahmand·Sharifi-Noghabi·Koudijs·Path2Space·MAKO 모두 정정본이 정확).
3. **미확인 1건**: **Ding 2025(Cancer Biol Med)** — §9 D3(드롭 트랙)이라 급하지 않으나 본문 인용 시 권/쪽/DOI 확보 필요.
4. **문서 플래그 갱신 가능**: novelty §4⑥ Lancet Oncol 2025(=Shamai, *Lancet Oncol*)·§4⑧ PANProfiler(=PMID 40645910, *Clin Breast Cancer*)는 본 감사에서 실존·서지 확인됨 → `[snippet, unverified]` 해제 가능. (인용연도는 online-first/print 확인 권장.)
5. (선택) 경미 표기 통일: Sannigrahi 연도 2023→2024(print), GSE285505 데이터 포인터에 Iwane 2025 저자 병기.
