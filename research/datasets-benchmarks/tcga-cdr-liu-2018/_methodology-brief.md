# Methodology Brief — BRCA endpoint selection & manifest join

## 1. 어떤 엔드포인트가 BRCA에 쓸 수 있나 / Usable endpoints for BRCA
TCGA-CDR 권고에 따른 BRCA 결정 (verified from paper):

| Endpoint | BRCA status | 근거 / Reason |
|---|---|---|
| **PFI** | ✅ **권장 / use** | 충분한 이벤트, 추적기간 적정 |
| **DFI** | ✅ **권장 / use** | disease-free 판정 후 진행 이벤트 충분 |
| **OS**  | ⚠️ **주의 / caution** | ~151 events / 1,097 cases — 이벤트 부족, 추적기간 부족 |
| **DSS** | ⚠️ **주의 / caution** | cause-of-death 불완전 + 이벤트 부족 |

**Decision for BIOP02:** primary survival target = **PFI** (가장 견고), 보조 =
**DFI**. OS/DSS는 **민감도 분석(sensitivity)**으로만 보고하고 주 결론에 사용하지 않는다.
PFI를 1차로 잡는 것이 Critic checklist #1(leakage) + 통계검정력 측면에서 가장 방어 가능.

## 2. 라벨 컬럼 / Label columns to pull (from Table S1 tab TCGA-CDR)
`bcr_patient_barcode`, `type`(=BRCA filter), `PFI`, `PFI.time`, `DFI`, `DFI.time`,
`OS`, `OS.time`, `DSS`, `DSS.time`. Event 컬럼은 0/1, `*.time`은 **days**.

## 3. 매니페스트 조인 / Manifest join (agents/data/)
우리 매니페스트 파이프라인은 **NAS WSI 인벤토리**(슬라이드 파일·배럴 ID)와 **TCGA-CDR**을
환자 단위로 결합한다:
1. WSI 파일명에서 환자 바코드 추출 (`TCGA-XX-XXXX`, 정규화: 대문자, 12자 prefix).
2. TCGA-CDR을 BRCA 행으로 필터 후 `bcr_patient_barcode`로 **left-join** (WSI 보유 환자
   기준). 1 patient ↔ N slides → join은 patient-level, 모델 split도 **patient-level**.
3. 결과 매니페스트 = `slide_path · patient_barcode · {ER,PR,HER2,PAM50} · {PFI,PFI.time,
   DFI,DFI.time}` — phenotype(IHC/PAM50) + outcome(CDR) 라벨 통합.

## 4. Leakage 가드 / Leakage guards
- **Patient-level split만** (한 환자 슬라이드가 train/test에 동시 등장 금지) — Howard 2021
  site-aware split과 결합.
- 라벨 정의 **단일 소스(CDR)** 고정 → train/test 간 endpoint 정의 드리프트 차단.
- censoring·event 컬럼은 CDR 원본 그대로 사용, 재정의 금지.

## 5. 한계 / Caveats
median follow-up ~22 mo로 짧음 → 장기 OS 결론 불가. BRCA 생존 분석은 **PFI/DFI 중심**,
외부검증(CPTAC) 시 동일 엔드포인트 정의를 강제 적용해야 비교 가능.
