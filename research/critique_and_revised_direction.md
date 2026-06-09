# BIOP02 — 외부 어드버서리 리뷰 종합 & 수정 방향 (v0.2, 2026-06-10)

paper-critic + reviewer(npj Prec Onc) + research-methodologist 3개 병렬 리뷰 + Leader 자체 리뷰의 종합. **응원 아님 — 약한 관절을 찾는 기록.**

## 수렴된 평결 (3개 에이전트 일치)

> **치료-가설 층이 가장 약하고·가장 scoop당했고·가장 검증 불가능 — 현재 "뻔한 걸 복잡하게(trivial dressed up)".** 출판 가능한 척추 = **Exp1+Exp2+Exp3 (정직한 site-통제 평가 + auditability)**, 치료층 아님.
> reviewer 평결: **Major revision (2.5/5)**. Exp3 없으면 minimal set = "Dawood를 제대로 한 것"(rigor 논문, method 아님). 통계·재현성은 prior art보다 확실히 우수.

## 치명적 구멍 (우선순위)

1. **auditability ↔ richness 모순 (★최중요).** "풍부한 표현형 예측"으로 거친-표현형 문제를 고치면, 그 50–200유전자 시그니처가 **두 번째 블랙박스** → Exp3의 FAS(오류를 명명된 표현형 head로 귀속) 논지가 증발. **"해석가능 6-bit 병목"과 "전이에 충분히 풍부"는 동시 불가. 축을 골라야 한다.** (Leader 제안의 자기모순 — paper-critic 적발.)
2. **검증 불가능한 치료층.** 환자 치료결과 라벨 0 → CPTAC는 표현형만 검증, 치료가설은 논문 내 **반증 불가**. SoC 재현=순환(KB에 SoC 인코딩). → **실제 결과 앵커 최소 1개 필요**(TCGA-CDR 생존 PFI/DFI로 수렴축 층화, 또는 Farahmand식 retrospective pCR/trastuzumab-response).
3. **경로 독립성 환상 + Critic 순환.** 모든 경로가 같은 예측 표현형 공유 → 같은 H&E 오류 상속; PRISM/GDSC/CTRP near-collinear(triple-counting). 진짜 독립=viability vs LINCS *readout*뿐. Critic(Exp5)을 OncoKB로 채점하는데 Exp4 성공도 KB-enrichment로 정의 → **known-knowledge 필터지 falsifiability 도구 아님**. → (a) Exp4 **phenotype-shuffle null**(수렴이 셔플하면 붕괴해야), (b) Critic ground truth를 **가설 생성 KB와 분리**.
4. **flagship 역설.** 가설이 가치있는 곳(표적 SoC 없는 TNBC/Basal)이 정확히 표현형 예측이 가장 약한 곳(HER2-E F1 0.545, Basal 약함) → abstention gate가 flagship 대부분 기각 → 결국 HER2+/Luminal(=뻔함)에서만 작동 시연.
5. **TNBC subgroup 검정력 붕괴 (정량).** TCGA-BRCA TNBC ~110–150명 → site-disjoint test 0.15 → **test에 ~15–20명** → bootstrap CI 반폭 ±0.15–0.20, "0.70 vs 0.85 구분 불가". **standalone TNBC subgroup AUROC 주장 = 불가능.** → TNBC는 **가설-생성 showcase**(PARP/platinum/LAR 농축)로만, subgroup AUROC 헤드라인 금지.
6. **scope 모순.** Leader의 1010 override vs 문서들의 "~150–250" 불일치 + 1010이 Exp2가 단속하는 leakage-규율과 충돌하는 모양새. → 전 문서 n 재고정 + 일관화.
7. **Critic-as-method 얇음** (co-scientist scoop) → 거버넌스를 *rigor 기능*으로 강등(헤드라인 아님).

## 수정된 척추 (제안)

**헤드라인 = 치료 파이프라인이 아니라 "엄밀성·auditability 방법론".** 치료층은 *경계 명시된 illustrative 다운스트림 모듈*로 강등.

> H&E→**범주형 분자표현형**을 site-disjoint·CPTAC-외부검증 하에 정직하게 예측(Exp1/2, Tafavvoghi 0.727을 *공정 재측정* split에서 능가)하고, **표현형 병목이 end-to-end 대비 측정 가능한 오류-귀속성을 산다**(Exp3, TOST 동등정확도+FAS)는 것이 핵심 기여. 다운스트림 치료 모듈은 SoC를 *양성 대조*로 재현하고, **독립 readout(cell-line↔LINCS, shuffle-null 통과)이 수렴하는 후보축**을 TNBC에서 *가설로* 제시하되, 검정력이 없는 성능 주장은 명시적으로 사절하고 **실제 생존 결과(TCGA-CDR) 앵커 1개**로 최소 falsifiability를 확보한다. 기여 = 새 정확도가 아니라 **재현·반증 프로토콜과 그 임상 적용 경계의 명시**.

**핵심 포크: 병목을 범주형(해석가능, auditability 사수)으로 유지.** 발현 시그니처(Exp7)는 *전이 연료*로만 분리 사용(덜 해석가능함을 인정), 또는 thesis 청결 위해 **생략**.

## 필요한 추가·수정 (리뷰 기반)

| # | 항목 | 비고 / GPU |
|---|---|---|
| F1 | **Exp3을 Paper A에 포함** (보류 해제) — benchmark→method 전환의 유일 수단 (reviewer 강력) | ⚠️ Leader "Exp3 보류" 결정 역전 필요. GPU 큼 |
| F2 | **Exp4 phenotype-shuffle null** — 수렴이 셔플 시 붕괴 입증 | GPU 0 |
| F3 | **실제 결과 앵커**: TCGA-CDR PFI/DFI로 수렴축 생존 층화 (or retrospective pCR) | GPU 0 |
| F4 | **Critic ground truth ↔ 가설 KB 분리** (Exp5 비순환) | GPU 0 |
| F5 | **TNBC = 가설 showcase(Exp8)**, subgroup AUROC 금지; 정의=IHC-TNBC ∩ PAM50-Basal 합의셋, 불일치 13–22%는 audit 케이스 | GPU 0 |
| F6 | **scope 1010 ↔ 150-250 일관화**, 전 문서 n 재고정 | — |
| F7 | Critic/멀티에이전트 → rigor 기능 강등(헤드라인 제거) | — |
| F8(선택) | **Exp7 H&E→발현/pathway 회귀**(frozen UNI+회귀 head, per-sig Spearman, **ssGSEA train-only**) — *전이 연료 한정*, Schmauch/Dawood 중복(instrumental) | GPU ~0 |

## npj Prec Onc 수용 최소조건 (reviewer)
1. Exp2: site-disjoint 수치가 *공정 재측정* split에서 Tafavvoghi 0.727 능가(CI+DeLong). **경험적 바닥.**
2. Exp3: Dawood 충실 재현 대비 동등정확도·우월 auditability(TOST+FAS).
3. 치료층: 실제 결과 앵커 1개 + phenotype-shuffle null + KB-분리 Critic.
4. scope override 해소 + 전 문서 n 재고정.

## 가장 큰 방법론 리스크 (methodologist)
**연속 타깃 유도 시 leakage(ssGSEA 샘플상대 → train-only fit 필수) + TNBC n→0 함정.** 둘이 겹치면 "지지하는 듯하나 train-test 오염+저검정력 노이즈의 산물"인 가짜 결과. 완화: 모든 시그니처 변환 train-only, per-sig no-morphology+site-probe 바닥 보고, TNBC는 enrichment(Exp8)로만.

## Open Leader 결정 (다음 단계)
1. **헤드라인 재프레임** 수용? (치료 파이프라인 → 엄밀성/auditability 방법론, 치료=경계모듈)
2. **Exp3 보류 해제 → Paper A 포함?** (reviewer가 꼽은 단일 최중요 추가)
3. **Exp7(발현 시그니처)** 전이연료로 포함 vs 청결 위해 생략?
