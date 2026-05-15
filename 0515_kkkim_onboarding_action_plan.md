# SpatialPathoAgent — 5/15 onboarding 결정 및 액션 플랜 (kkkim)

> **작성일**: 2026-05-15 (첫 정기 미팅 당일)
> **Owner**: 김가경 (kkkim, Embedding Agent)
> **목적**: 프로젝트 이름 변경 + 새 역할 분담 확정 + license/모델 결정 + 본인 1주 액션 정리
> **선행 정본**: `00_master_plan_v3.1.md`, `PROJECT_PLAN.md`, `4_homework_public.md`

---

## 1. 프로젝트 정보 update

### 1.1 이름 변경
- 기존: SpatialPathoAgent
- **변경**: **프로젝트#02 - SpatialPathoAgent**

### 1.2 멤버 (6명 확정)

| Functional Role | 담당자 | HF/Server ID | SSH 포트 | 주요 역할 |
|---|---|---|---|---|
| Data Agent | 류재면 | jamie | 2201 | TCGA / CPTAC / DepMap 데이터 수집, label 정의, split 관리 |
| Embedding Agent | **김가경** | **kkkim** | 2202 | H&E WSI tiling, UNI/CONCH/EXAONE/Virchow embedding 생성 |
| Modeling Agent | 박세진 | sjpark | 2204 | Morphology embedding 기반 phenotype prediction |
| Therapeutic Evidence Agent | 서정한 | jhans | 2206 (예정) | Phenotype → pathway → drug hypothesis + evidence 구조화 |
| Scientific Critic Agent | 이건규 | gglee | 2203 | 정량 검증, claim 검토, DRP 오해 차단, hallucination 점검 |
| Orchestrator | 지용기 | braveji | 2205 | Pipeline 조정, 결과 합성, 실험 registry 관리 |

### 1.3 v3 시절 PROJECT_PLAN.md와의 변경점

| 변경 | 사유 |
|---|---|
| 1인 1역할로 정리 | PROJECT_PLAN의 이건규(리더+Critic+Embedding 3역) → 리더+Critic 2역. 김가경(Embedding+Therapeutic Evidence 2역) → Embedding 1역. 부담 분산 |
| 서정한 신규 합류 | Therapeutic Evidence 전담 owner. 5/12 Kickoff 이후 합류 |
| ID 체계 변경 | gkkim → kkkim, gklee → gglee, jmryu → jamie, ykji → braveji, sjpark 유지. 서정한은 jhans 신규 |

> **5/15 미팅에서 공식화 필요**: PROJECT_PLAN.md §0 리더십, §6 Appendix 역할 매핑, §1 Slot 3 분배 등 5개 항목 갱신 필요. ykji(braveji)가 5/22 전 회의록 + AGENTS.md v0.2에 반영.

---

## 2. PROJECT_PLAN.md / 4_homework_public.md ↔ v3.1 정합성 검토

### 2.1 일치 (변경 불필요)

- Paper A 16주 공식 + 12주 stretch — 양쪽 일치
- Sprint 0 = 5/12 (Kickoff) ~ 5/22 — 일치
- 매주 금요일 미팅 cadence — 일치
- Critic을 architecture에 박기 (cross-review owner ≠ author) — 일치
- DRP framing 회피 + counterfactual mandatory + hypothesis-only claim — 일치
- raw / processed / embedding / experiments S3 layout — 일치

### 2.2 PROJECT_PLAN이 더 구체적 (v3.2로 흡수 권장)

- GPU spec: A100 80GB × 1, 24 CPU, 188 GiB RAM, 2 TB root
- 서버: IP `61.109.239.220`, SSH key only
- 데이터 저장 정책: raw=S3 only / cache LRU 200 GB / embedding 영구
- GPU 시간 슬롯: 09–13 / 13–17 / 17–21 / 21–01
- dbGaP controlled access PI 사인 필요 (학생 단독 X)

### 2.3 v3.1이 더 구체적 (PROJECT_PLAN 보강 필요)

- Funding / OA 조건 사전 lock (v3.1 §12.7)
- CPTAC paired ~120명 Paper A 포함
- ConsensusTME + tumor purity covariate mandatory (Track B)
- SCAN-B default external + METABRIC fallback
- W6 12주 fallback 결정 시점 매커니즘

### 2.4 정합 안 됨 (선택 필요)

| 영역 | 차이 | 결정 |
|---|---|---|
| Critic checklist 항목 수 | PROJECT_PLAN 7항목 vs v3.1의 정량 5 + 정성 9 = 14항목 | gglee(Critic owner)가 5/22까지 mapping 1쪽 작성 후 lock |

---

## 3. License × Industry 이슈 — 결론 정리

### 3.1 발견된 issue (5/15 오전)

본 프로젝트 멤버 다수가 industry 소속. UNI/CONCH 등 SOTA pathology foundation model은 **CC-BY-NC-ND 4.0** (non-commercial only) license. Industry user의 사용 시 두 가지 레이어:

| 레이어 | 본질 |
|---|---|
| HF gate | Mahmood Lab의 접근 통제 (institutional email 필요) |
| License compatibility | 실제 사용 가능 여부 (use intent가 non-commercial인지) |

### 3.2 프로젝트 리더(gglee) 확인 — academic research 의도 명시

> "저희 목표가 아카데믹 리서치라 무관합니다! 유니나 콘치 말고도 엘지에서 공개한 엑사원 등을 사용하면 되서 안된다면 다른 수단 이용해도 될것같습니다. 사내에서 사용하실꺼라면 모델 몇개 따로 추천드리겟습니다! Virchow 라는 모델이 1,2 둘다 상업이용 가능하십이다."

→ **프로젝트 산출물은 publication only, non-commercial academic research로 위치 확정**

### 3.3 사실 확인 — Virchow license

리더 발언 중 사실 정정 필요 (참고용, 프로젝트 진행엔 무관):

| 모델 | License | Commercial 사용 |
|---|---|---|
| Virchow v1 | **Apache 2.0** | ⭕ OK |
| Virchow v2 | **CC-BY-NC-ND 4.0** | ❌ NOT OK |

Paige HF page (https://huggingface.co/paige-ai/Virchow2) 명시. Virchow2는 v1과 라이센스가 다름.

### 3.4 Foundation model 비교표 (breast cancer pathology, 2026-05-15 기준)

| 모델 | 라이센스 | 차원 | Owner | 본 프로젝트 사용 가능 | HF gate |
|---|---|---|---|---|---|
| **UNI v1** | CC-BY-NC-ND 4.0 | 1024 | Mahmood Lab | ⭕ (academic) | ⭕ |
| **UNI2-h** | CC-BY-NC-ND 4.0 | 1536 | Mahmood Lab | ⭕ (academic) | ⭕ |
| **CONCH** | CC-BY-NC-ND 4.0 | 512 | Mahmood Lab | ⭕ (academic) | ⭕ |
| **EXAONE Path 1.0** | EXAONEPath NC | 1024 | LG AI Research | ⭕ (academic) | ⭕ |
| **EXAONE Path 2.0** | EXAONEPath NC | 768 | LG AI Research | ⭕ (academic), SOTA on biomarker prediction | ⭕ |
| **EXAONE Path 2.5** | EXAONEPath NC | TBD | LG AI Research | ⭕ + multi-omics alignment 내장 (본 plan과 친화) | ⭕ |
| **Virchow v1** | Apache 2.0 | 1280 | Paige / MSR | ⭕ commercial-friendly fallback | ⭕ (명목상 institutional email) |
| **Virchow v2** | CC-BY-NC-ND 4.0 | 1280 | Paige / MSR | ⭕ (academic) | ⭕ |
| **Phikon / Phikon-v2** | Owkin non-commercial | 768 / 1024 | Owkin | ⭕ (academic) | △ less strict |
| **PLIP** | open | 512 | Stanford | ⭕ | ❌ |
| **ResNet50 ImageNet** | fully open | 2048 | various | ⭕ (성능 ↓) | ❌ |

---

## 4. 최종 모델 신청 전략 (5종 동시)

본 프로젝트가 academic research임이 확정되었으므로, **5종 동시 신청 후 가장 먼저 승인되는 모델로 5/22 pilot 진행**.

| Priority | 모델 | URL | 사유 |
|---|---|---|---|
| 1 | **UNI v1** | https://huggingface.co/MahmoodLab/UNI | v3.1 plan 기본, 가장 검증됨 |
| 2 | **CONCH** | https://huggingface.co/MahmoodLab/CONCH | UNI fallback, vision-language |
| 3 | **EXAONE Path 2.0** | https://huggingface.co/LGAI-EXAONE/EXAONE-Path-2.0 | 한국 도메인 친화 (institutional email 인식 ↑), SOTA biomarker |
| 4 | **Virchow v1** | https://huggingface.co/paige-ai/Virchow | Apache 2.0 안전, Paige 주 1회 일괄 승인 (관대) |
| 5 | UNI2-h (선택) | https://huggingface.co/MahmoodLab/UNI2-h | dim 1536, 가장 강력. 5/22 미팅 안건으로 UNI vs UNI2-h 비교 |

### Research use template (Industry-honest framing)

```
I am a member of the SpatialPathoAgent project, a non-commercial academic
research collaboration aiming for peer-reviewed publication on breast
cancer pathology. While I am affiliated with industry, this project is
explicitly conducted as academic research with no commercial product or
revenue intent. Output will be shared as bioRxiv preprint + journal
submission, with explicit disclaimer that hypotheses are "research only,
not for clinical decision support."

We use [MODEL_NAME] as a frozen tile-level feature extractor on H&E
whole-slide images from TCGA-BRCA and CPTAC-BRCA cohorts to predict
molecular phenotypes (proliferation, EMT, hypoxia, DNA repair, immune
signatures derived from RNA-seq and proteomics). We do not fine-tune,
redistribute, or use derivatives commercially. The team includes
researchers from both industry and academic affiliations collaborating
outside their day-to-day commercial activities, with proper attribution
to [MODEL_AUTHORS].
```

핵심 framing 단어:
- "non-commercial academic research collaboration"
- "no commercial product or revenue intent"
- "peer-reviewed publication"
- "outside their day-to-day commercial activities"
- "research only, not for clinical decision support"

---

## 5. HF account 정비 (어느 모델 가든 필수)

### 5.1 Naver 이메일 문제

**naver 등 개인 도메인은 거의 100% 거절** (Mahmood Lab 자동 규칙):
- `@gmail`, `@hotmail`, `@qq`, `@naver` → 자동 거절
- 자동 거절되면 큐 뒤로 밀려 1-3일 lead time이 1주로 늘어남

### 5.2 해결법 — 기존 HF 계정 그대로 두고 email만 변경

1. https://huggingface.co/settings/account 접속
2. **Emails** 섹션 → **"+ Add email"** → institutional email 입력 (예: `kkkim@<회사명>.com` 또는 academic team 도메인)
3. inbox에서 verification mail 클릭 (1-2분)
4. **"Make primary"** 클릭
5. naver는 secondary로 남겨둬도 무방
6. **Profile → Full name** 도 정식 영문 (`Gakyung Kim`, 약자 금지)

### 5.3 Institutional email 없을 경우

- 본인 소속 회사가 academic-recognized domain인지 IT 부서에 문의
- LG/SK 등 대기업 R&D 도메인은 보통 OK
- 작은 회사면 학교 동문 이메일 또는 academic collaborator의 이메일 협조 검토
- 정 안되면 본 프로젝트의 PI 후보(아직 미정)의 academic email 활용 옵션 검토

### 5.4 HF token 발급

https://huggingface.co/settings/tokens → **Create new token**
- Name: `spatial-pathoagent`
- Type: `Read`
- 생성된 토큰 `hf_xxx...` 즉시 password manager에 저장
- 절대 git commit 금지

---

## 6. HF form 위치 (별도 URL 없음)

신청 form은 model page 자체에 embedded gated form. 별도 URL 없음.

### 절차 (UNI 예시)

1. HF 로그인 상태로 https://huggingface.co/MahmoodLab/UNI 접속
2. 페이지 상단의 **"Access UNI"** 또는 **"Agree and access repository"** 박스
3. 박스 펼치면 form 필드 표시:
   - Full name (no abbreviations)
   - Current affiliation (no abbreviations)
   - Type of Affiliation: Industry / Academia / Other
   - Official institutional email
   - Research use (위 template)
4. 체크박스 3개 모두 체크 → **"Agree and access repository"**
5. 화면 상단에 "Your request is being reviewed" 메시지

### 거절 자동화 점검 사항

- ❌ `@gmail`, `@hotmail`, `@qq`, `@naver` primary
- ❌ "K. Kim" 약자
- ❌ "KAIST", "KU" 같은 affiliation 약자
- ❌ "I will use this for research" 같은 1줄 짧은 research use
- ❌ Email domain 인식 불가
- ✅ Institutional email + full name + affiliation spelled out + research use 1-2 문단

---

## 7. 5/15 ~ 5/22 (1주) 본인 액션 — 시간 boxed

### T-0: 지금 즉시 (미팅 전, 30분)

| Step | 액션 | 시간 |
|---|---|---|
| 1 | HF account institutional email 추가 + primary 변경 | 5분 |
| 2 | UNI 신청 | 5분 |
| 3 | CONCH 신청 | 3분 |
| 4 | EXAONE Path 2.0 신청 | 3분 |
| 5 | Virchow v1 신청 | 3분 |
| 6 | (선택) UNI2-h 신청 | 3분 |
| 7 | HF token 발급 + 저장 | 2분 |

### T+0: 오늘 미팅 중

본인 1분 progress (Slot 1):
```
"5종 foundation model 동시 신청 완료: UNI, CONCH, EXAONE Path 2.0,
Virchow v1, UNI2-h. HF account primary email institutional로 정비.
역할 분담 1인 1역할 정리로 Embedding 단독 owner 확정.
이전 Embedding 분담은 gglee와 함께였으나, 이제 단독으로 wall-clock 부담 증가 —
HF 승인 지연 시 dummy embedding(torch.randn)으로 sjpark unblock 가능."
```

### T+1: 오늘 밤 ~ 5/17 (주말, 2-3시간)

- SSH 접속 검증 (`ssh -p 2202 kkkim@61.109.239.220`)
- `whoami`, `nvidia-smi`, `df -h` 확인
- 막히면 braveji에게 슬랙 DM (SSH key가 새 ID에 등록 안 됐을 수 있음)
- `/workspace/agents/embedding/` 폴더 생성
- 환경 셋업 시작 (`setup.sh` 작성, openslide / libvips / timm / huggingface_hub)

### T+2: 5/18 (월) ~ 5/20 (수) — 평일 2-3시간/일

- `configs/tile_config.yaml` 작성 (256×256 @ 20×, Otsu mask, per-patient cap 5000)
- `scripts/tile_wsi.py` 작성 (tiling 함수)
- `scripts/extract_dummy.py` 작성 (dummy embedding, sjpark unblock용)
- jamie(jmryu)에게 TCGA-BRCA WSI 1장 샘플 요청

### T+3: 5/21 (목) — HF 승인 후 (또는 안 와도 진행)

- `scripts/extract_<model>.py` 작성 (UNI/CONCH/EXAONE/Virchow 중 승인된 모델)
- 1 slide pilot 실행 + `time` 명령으로 wall-clock 측정
- 측정 항목: 전체 시간 / patch 수 N / 1 patch 추출 시간 / 결과 파일 크기 / GPU memory peak

### T+4: 5/22 (금) walk-through 5분 발표

`outputs/pilot/PILOT_REPORT.md` 작성:
1. Setup (서버 + 환경 + HF 승인 시점 + 사용 모델)
2. Pilot 측정 결과 (wall-clock, GPU memory)
3. Scaling estimate (TCGA 150 + CPTAC paired 120 → 총 hours, GPU 슬롯 필요 수)
4. Decisions to make (UNI vs UNI2-h vs EXAONE 비교, per-patient cap, GPU fallback 필요성)
5. Blockers + Sprint 1 분배 의견

---

## 8. Risk / Fallback

| Risk | 대처 |
|---|---|
| HF 승인 5/22 전까지 안 옴 | dummy embedding(torch.randn)으로 sjpark의 MLP 흐름 unblock + pilot은 5/22 발표 보류 |
| UNI/CONCH reject (5종 모두 reject 가능성 거의 0) | EXAONE Path 2.0 또는 Virchow v1으로 swap |
| 1 slide pilot 시간 > 30분 | per-patient cap 조정 (5000 → 2000 검토), 5/22 미팅 안건 추가 |
| `kkkim` SSH 막힘 | braveji에게 슬랙 DM |
| openslide 시스템 lib 미설치 | braveji에게 sudo apt install 부탁 |
| GPU 점유 충돌 | 잠정 캘린더 룰, 본인 슬롯 5/18 13–17 / 5/19 09–13 권장 |
| institutional email 자체가 없음 | 본 risk가 발견되면 미팅에서 즉시 escalation, PI 후보 academic email 활용 검토 |

---

## 9. 미팅에서 발의할 신규 안건 (Slot 2 또는 §4 미정에 추가)

### 9-1. 1인 1역할 분담 lock 공식화 (5분)
- gglee: Critic 단독 + 리더 (Embedding 분담 해제)
- kkkim: Embedding 단독 (Therapeutic Evidence 분담 해제)
- jhans: Therapeutic Evidence 단독 (신규)
- 다른 멤버 변경 없음

### 9-2. License × academic 의도 명시 (2분)
- 리더 사전 확인 완료 (academic research 의도)
- Sprint 0 closeout 전 v3.1 §12.7 / §13 미정 항목에 "license × commercial intent decision = academic research only" 정식 lock

### 9-3. Funding / OA 조건 사전 lock (2분, v3.1 §12.7)
- 각자 본인 소속 OA office에 5/22 전까지 1회 문의
- 8개 체크리스트 (지원 출처 / acknowledgment 문구 / OA 협약 / 저널 제약 / COI / paper A vs B cover 등)
- gglee가 funding source 정확한 grant 번호 / acknowledgment 문구 / 저널 제약 5/22 전 공유

### 9-4. v3.1 정본화 (2분)
- v3.1 master plan (39KB, 5개 핵심 파일 + tasks/prompts)이 현재 outputs에만 있고 GitHub 미반영
- braveji가 5/22 전 mono-repo 만들고 commit
- PROJECT_PLAN과 v3.1 권한 위계: v3.1 = master plan(목표/원칙), PROJECT_PLAN = 운영 계획서(주차/액션). 충돌 시 v3.1 우선

### 9-5. EXAONE Path 2.5 검토 (1분)
- multi-omics alignment 내장 → 본 프로젝트의 RNA/Protein dual alignment narrative와 직접 연결
- UNI/CONCH ablation 비교 시 EXAONE Path 2.0/2.5도 후보로 포함
- 5/22 walk-through 후 결정

---

## 10. v3.1 → v3.2 patch 항목 (미팅 후 braveji 정리)

`00_master_plan_v3.1.md` 기준 다음 항목 patch:

| 위치 | 변경 |
|---|---|
| §4 | Agent 6개 모두 1인 1역할로 lock (서정한 jhans 추가) |
| §11.3 | 사람-역할 매칭 "1인 1역할" default로 안정화 |
| §13 | Open Decisions #16 funding lock 시점 명시, #20 신규 "license × commercial intent = academic only" |
| §13 | Open Decisions #21 신규 "Embedding model 최종 선택" — UNI vs UNI2-h vs EXAONE Path 2.0 vs Virchow v1, 5/22 pilot 결과 후 lock |

`03_model_design.md` §2 Embedding 모델 후보 표에 row 추가:

| 모델 | 출처 | 차원 | 라이센스 | 비고 |
|---|---|---|---|---|
| EXAONE Path 2.0 | LG AI Research | 768 | EXAONEPath NC | UNI 한국 도메인 fallback, biomarker SOTA, multi-omics alignment (v2.5)도 후보 |
| Virchow v1 | Paige / MSR | 1280 | Apache 2.0 | License worry-free fallback, UNI ablation 비교 |

`08_infra.md` §1 S3 layout + §6 환경에 추가:
- GPU 서버 spec (A100 80GB × 1, 24 CPU, 188 GiB RAM, 2 TB root, IP 61.109.239.220)
- SSH 포트 매핑 (jamie:2201, kkkim:2202, gglee:2203, sjpark:2204, braveji:2205, jhans:2206)
- 데이터 저장 정책: raw=S3 only, /data/cache LRU 200 GB, embedding 영구

---

## 11. Appendix — 빠른 참조

### 신청 URL 한꺼번에

```
HF account: https://huggingface.co/settings/account
HF token:   https://huggingface.co/settings/tokens

UNI:            https://huggingface.co/MahmoodLab/UNI
CONCH:          https://huggingface.co/MahmoodLab/CONCH
UNI2-h:         https://huggingface.co/MahmoodLab/UNI2-h
EXAONE Path 2.0: https://huggingface.co/LGAI-EXAONE/EXAONE-Path-2.0
Virchow v1:     https://huggingface.co/paige-ai/Virchow
```

### SSH 한 줄

```bash
ssh -p 2202 kkkim@61.109.239.220
```

### 1 slide pilot 측정 cheatsheet

```bash
# tiling
time python scripts/tile_wsi.py --slide /data/raw/tcga/sample.svs --config configs/tile_config.yaml --out outputs/pilot/coords.npy

# extraction (HF 승인 후)
time python scripts/extract_uni.py --slide /data/raw/tcga/sample.svs --coords outputs/pilot/coords.npy --out_dir outputs/pilot/

# GPU monitoring (다른 터미널)
watch -n 1 nvidia-smi
```

### 자주 쓰는 절대 금지 사항 (CLAUDE.md §8)

- ❌ HF token / AWS keys git commit
- ❌ drug feature (SMILES, fingerprint, learnable embedding) 모델 입력
- ❌ "patient-specific optimal treatment prediction" / "personalized therapy" 표현
- ❌ ICI / Pembrolizumab을 cell-line transfer로 추천
- ❌ Critic agent가 자기 임계값 / control 결정 (anti-self-reference)
- ❌ TCGA WSI 전체 다운로드 (Paper A는 150명 subset, 12주 compression은 80-100명)

---

## 12. 변경 이력

| 버전 | 일자 | 변경 |
|---|---|---|
| v0.1 | 2026-05-15 | 5/15 미팅 직전 onboarding 정리. License 이슈 + 모델 선택 + 본인 액션 |

