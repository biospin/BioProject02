# 논문 방향 (Paper Direction) — 확정본

> 2026-07-12 기준 권위 요약. 세부 계획=`FLAGSHIP_PLAN.md`, 사전등록 법칙=`../../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md`, 결정지도=`../../experiments/crosscancer/CROSS_CANCER_DECISION_MAP.md`, 결정 로그=`../../experiments/crosscancer/PROGRESS_DECISIONS.md`.
> 이 문서는 "무엇을 왜 쓰는가"를 한눈에 정리한다. 완결 문장·기술 용어 유지.

## 한 문단 요지
H&E 전(全)슬라이드 영상으로 분자 표현형을 예측하는 연구는 이미 포화됐다. 그런데 이 분야는 "예측된다"를 "임상적으로 대체 가능하다"와 혼동해 왔다. 우리는 치료 결정 경로에서 **H&E가 분자검사를 언제 값싸게 대신할 수 있는지의 다암종 결정지도**를 제시하고, 그 대체 가능 경계가 **분자 변이가 H&E 해상도에서 보이는 형태학적 상관물을 갖는지**라는 사전등록 법칙으로 예측됨을 5개 암종에서 보인다. 멀티에이전트 파이프라인은 인프라이지 기여가 아니다.

## 용어 정의 (Terminology) — 근거 기반, 첫 등장 시 정의
- **형태학적 상관물(morphological correlate)**: 어떤 분자 변이가 H&E에서 알아볼 수 있는 조직·세포 형태 특징(조직 구조·핵 형태·기질·면역침윤·점액 등)으로 나타나는 것. 병리학 표준 용어이다([Modern Pathology, "The Continuing Role of Morphology in the Molecular Age"](https://www.nature.com/articles/3880295); [J Pathol, Cifci 2022](https://pathsocjournals.onlinelibrary.wiley.com/doi/full/10.1002/path.5898)). 변이는 이 상관물을 "가진다 / 없다 / 부분적으로 가진다"로 서술한다.
- **표준 용어 규칙**: 못 보는 상태는 "**형태학적 상관물이 없다(lacks a morphological correlate) / 형태학적으로 뚜렷하지 않다**"로 쓴다. 초기에 썼던 "형태학적 침묵·조용·silent"은 비공식 축약이며 정식 서술에서 쓰지 않는다. **"silent"은 유전학의 동의돌연변이(silent mutation)와 혼동**되고, "morphologically occult/silent"은 이 맥락에서 표준 용어로 문헌 확인되지 않으므로 채택하지 않는다.
- **원칙(전 세션 적용)**: 용어는 지어내지 않는다. 새 용어는 문헌·기존 네이밍을 먼저 검증하고 그 형태로만 쓰며, 처음 등장할 때 정의부터 한다.

## 제목(가안)
"When can H&E substitute for molecular testing? A cross-cancer decision map of morphological substitutability" (확정 전).

## 핵심 기여
1. **cost-of-substitution 프레임워크** — 예측충실도와 치료 라우팅 정확도를 분리해, "예측된다"와 "대체 가능하다"를 구분한다.
2. **형태학적 상관물 치환가능성 법칙** — 대체 가능 여부를 사전에 예측하는 법칙(사후 서술 아님). 폐·위·두경부에서 held-out 검정한다.
3. **다암종 결정지도** — 유방·폐·대장·위·두경부에서 어느 마커가 H&E로 저비용 대체 가능하고 어느 마커가 분자검사 필수인지 지도화한다.
4. **AI 결정 레이어** — 치환가능성 스코어 + 보정/기권(도메인 취약성 대응). 배포 가능한 결정지원.

## 두 층위 프레임워크 (절대 융합 금지)
- **표1 — 예측충실도(prediction-fidelity)**: H&E가 분자 아형을 복원하는가(아형↔아형). 유방 PAM50 ↔ 대장 CMS ↔ 폐 전사체 아형 ↔ 위 Lauren ↔ 두경부.
- **표2 — 라우팅 치환비용(routing-cost)**: 그 예측으로 치료를 배정할 때 잃는 결정 정확도(마커↔마커). 유방 수용체 ↔ 대장 MSI/RAS ↔ 위 HER2-amp/MSI ↔ 두경부 HPV/EGFR.
- 두 값을 하나의 "비용" 숫자로 합치지 않는다(층위 오류 방지). 예후용 아형(CMS 등)의 예측 AUROC를 치료 비용으로 승격하지 않는다.

## 사전등록 법칙 (봉인됨, 결과 전)
대체가능(저비용)=형태를 바꾸거나 형태와 연동된 변이(발현/증폭+구조, 면역연동 MSI, 조직형). 분자검사 필수(고비용)=형태학적 상관물이 없는 변이(HER2 증폭, RAS 점변이). 등급적=부분 상관물(폐 EGFR). **법칙은 "치환가능성" 경계이지 "생물학적 상관물 부재"가 아니다** — 고해상 기술이 미세 상관물을 찾아도 반증되지 않는다.
- 이미 관측(부합): 유방 ER 0.901/HER2 0.599, 대장 MSI 0.918/all-RAS 0.705/BRAF 0.882, CMS1 0.912/CMS4 0.661.
- held-out(봉인): 폐 EGFR 등급적 0.75-0.89 > KRAS ≤0.65; **위 HER2-amp ≤0.65(유방 0.599 복제=최강 교차장기 검정)**; 두경부 HPV ≥0.80 > EGFR.

## 5개 암종 설계 (왜 각각)
| 암종 | 역할 | 대체가능축(가시) | 필수축(blind) |
|---|---|---|---|
| 유방(anchor) | 원 관찰 | ER·PAM50 | **HER2(증폭)** |
| 폐 | 가장 깨끗한 이중축 | LUAD/LUSC·TRU | EGFR(등급적)·KRAS |
| 대장 | 중간비용 calibration | MSI-H | **all-RAS(점변이)** |
| 위 | **법칙 교차장기 복제** | MSI·Lauren·EBV | **HER2-amp(=유방 복제)** |
| 두경부 | 새 종류 가시축(바이러스) | **HPV** | EGFR |
5개까지가 "대비로 법칙 검정 + pan-cancer 아틀라스로 안 흩는" 경계.

## AI 결정 레이어
- 치환가능성 스코어 지수 = f(예측 AUROC, 라우팅 오배정비용, 형태상관물 강도, 도메인강건성).
- 보정 + 기권(selective/conformal) — OOD·불확실 시 분자검사로. **CPTAC 도메인 붕괴가 동기.**
- (stretch) Value-of-Information 검사주문 정책. **RL 제외**(단일스텝 미스매치). DRP 경계: "검사 주문 여부"에만.

## 저널·IF
모달 IF 6-12(npj Precision Oncology·Genome Medicine·EBioMedicine·Cell Reports Medicine), 스트레치 12-16(Nature Communications·npj Digital Medicine·Med). 20+ 비현실(전향적 검증/새 능력 필요). 상향 조건: 폐·위·두경부 held-out이 법칙을 확증 + AI 레이어가 "새 능력"으로 읽힐 것.

## 최신 기술 없이 강한 이유 (방어)
H&E-우선은 약점이 아니라 명제다 — 가장 값싸고 보편적인 modality가 표준검사를 언제 대신하나. 멀티오믹스/공간전사체를 핵심 modality로 쓰면 배포성 전제를 스스로 부정한다. proteomics/ATAC 추가는 off-thesis(그 마커가 실재함은 기지사실). 단 CPTAC proteomics로 "HER2 단백질은 상승했으나 H&E엔 형태학적 상관물이 없다"를 보조 확인해 decoupling만 굳힌다.

## 현재 상태 (2026-07-12)
- ✅ 유방(기존)·대장 Part A/B MIL 완료. 사전등록 법칙 봉인. 5개 암종·AI 레이어 방향 확정.
- 🔄 폐 임베딩(858/1050) + 아형 라벨 확보됨 → 폐 MIL(법칙 held-out) 대기. mean_cost 임상거리·shuffle-null 5-seed(GPU). 위·두경부 데이터/임베딩/MIL 파이프라인 자율 실행. CPTAC proteomics 확인.
- ⏳ AI 레이어 구현(결과 안착 후) → Critic 7항목 → figure → 통합 원고 → paper-critic.

## 정직한 한계 (원고에 명시)
- **대장 ST 메커니즘 = NULL**(Visium 55µm 해상도가 핵 텍스처 미만). 메커니즘 그림은 유방 ERBB2 floor가 담당, 대장은 MIL로만. Su IMC 재시도는 옵션.
- **RAS 상관물 부재는 점변이라 프록시(MAPK/EREG) 경유** — 유방 증폭보다 덜 깨끗, exploratory.
- **저검정력 endpoint**(CMS1/CMS3/MSI/BRAF, n_pos 15~21) exploratory 표기.
- **CPTAC 외부 전이는 도메인 시프트로 붕괴**(+Fernandez-Romero 2026 이미 출판) — 예측검증 실패이나 "치환 도메인 취약" 증거로 재활용.
- **hypothesis_only, 후향적, 전향적 검증 필요.**
