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

## 다음 단계
1. 추가 주제 조사(아래 §추가 주제) → 리스트 보강
2. 상위 우선순위(특히 SCOOP 후보 + 우리 백본/baseline)부터 BioProject01 멀티렌즈 상세분석으로 확장
3. 타겟 저널 확정 후 related-work 초안에 연결
