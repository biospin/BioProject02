# 규칙 조정 결정문 — CPTAC 라벨 임시 확보 (Embedding→Data 역할 한시 흡수)

**일자:** 2026-07-03 · **결정자:** kkkim (Project Leader + Embedding Agent) · **claim_level:** sanity (외부검증 입력 준비)

## 배경 (누구의 무엇이 지연되었나)
- **의존성:** BIOP02-53 "[S3] Attention MIL 학습 (TCGA train → **CPTAC test**)"(담당 sjpark, 진행 중)은 외부검증 **평가(AUC)**를 위해 CPTAC IHC(ER/PR/HER2)/PAM50 라벨이 필요하다.
- **소유 규칙:** CPTAC 임상 라벨은 **Data Agent(jamie)의 역할**이다(CLAUDE.md: manifests, clinical metadata, labels).
- **지연 사실:** S3 스프린트(2026-06-19 ~ 07-03) 종료 시점인 2026-07-03 기준, CPTAC 임상 라벨이 repo·`/workspace` 어디에도 존재하지 않음(IDC 인벤토리는 series 메타데이터뿐). 즉 S3 창 내내 이 Data 산출물이 미제공 상태였다. 임베딩 측(kkkim)은 동일 2026-07-03에 BIOP02-53(comment 10864)으로 라벨 공유를 공식 요청함.

## 결정 (사유)
**sjpark이 요청·의존하는 산출물(BIOP02-53)을, 제3자(Data Agent) 의존성 지연 때문에 지연시킬 수 없다.** 임베딩 입력(UNI/CONCH/CPTAC-UNI per-tile)은 이미 `/workspace`에 발행 완료했고, 남은 유일한 블로커가 CPTAC 라벨이므로, **Embedding Agent(kkkim)가 공개 데이터로 라벨을 한시적으로 확보**하여 sjpark의 타임라인을 보호한다.

- 선례: CLAUDE.md에서 Embedding Agent가 이미 "Data manifest/다운로드 역할 흡수"한 바 있음 — 본 조정은 그 연장선의 **한시적** 조치다.
- **소유권 불변:** CPTAC 라벨의 authoritative owner는 여전히 jamie(Data Agent). **jamie의 공식 라벨이 도착하면 그것으로 대체(supersede)** 한다. 본 공개본은 잠정치다.
- 원칙 조정은 리더(kkkim) 판단, 사유 명기 조건으로 승인.

## 확보 내역 (provenance)
- **출처:** cBioPortal `brca_cptac_2020` (Krug et al. 2020, *Cell*, "Proteogenomic Landscape of Breast Cancer").
- 파일: `data_clinical_patient.txt`(ER/PR/HER2), `data_clinical_sample.txt`(PAM50). git-LFS media 경로로 취득.
  - patient sha256 `d9b0dee7…a1275`, sample sha256 `f28568f1…896cd`
- **매핑:** 우리 slide case_id `01BR001` → cBioPortal PATIENT_ID `X01BR001`(X 접두).
  - 컬럼: ER=`ER_UPDATED_CLINICAL_STATUS`, PR=`PR_CLINICAL_STATUS`, HER2=`ERBB2_UPDATED_CLINICAL_STATUS`, PAM50=sample `PAM50`(Her2→HER2 정규화).
- **커버리지:** 653 CPTAC 슬라이드 중 **395장에 라벨 채움**(고유 종양 케이스 120/122 = cBioPortal 코호트 거의 전부). ER 387 · PR 375 · HER2 294 · PAM50 382.
- **미매칭 78 케이스**(01BR002 등): proteogenomic 종양 코호트(122명) 밖 = 공개 IHC/PAM50 없음(정상조직/코호트 외 추정; IDC series_description이 "tumor_tissue" 아님). 매핑 버그 아님, 데이터 한계.
- PAM50은 CPTAC에 Normal 없음(Basal/LumA/LumB/HER2 4클래스).

## 산출물
- `experiments/kkkim/20260703_cptac_labels/cptac_labels_cbioportal.csv` (case별 라벨 + 출처)
- `/workspace/data/cache/biop02/cptac_labels_cbioportal.csv` (팀 공유본)
- `/workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv` — er/pr/her2/pam50 컬럼 채움(395행)

## 후속
1. jamie가 authoritative CPTAC 라벨 제공 시 → 본 잠정본 대체, manifest 재생성.
2. sjpark: 라벨 있는 슬라이드로 cross-dataset 평가 진행 가능(라벨 없는 행은 평가에서 제외 = compare/probe가 자동 교집합).
3. Critic(braveji): 외부검증 결과 리뷰 시 라벨 출처(공개 cBioPortal 잠정본)와 커버리지(395/653) 명시 필요.
