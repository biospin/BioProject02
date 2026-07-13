# BIOP02-53 논의 요약 — 외부검증 결과 + 방향성

> 작성 sjpark · 2026-07-10 · 회의 논의용
> 대상 티켓: BIOP02-53 (Attention MIL, TCGA train → CPTAC test)
> 관련: BIOP02-56(Critic #3·#4), BIOP02-57(registry), BIOP02-91(cost-of-substitution), BIOP02-90(receptor 라우팅)

---

## 1. 외부검증 결과 — 4개 엔드포인트 (CLAM, TCGA→CPTAC)

| 엔드포인트 | 내부 AUC | 외부 AUC | 외부 baseline 비교 | 판정 |
|---|---|---|---|---|
| ER | 0.901 | 0.894 | subtype_only 0.962가 상회 | 신호 있으나 baseline 못 넘음 |
| PR | 0.777 | 0.778 | subtype_only 0.912가 상회 | 신호 있으나 baseline 못 넘음 |
| HER2 | 0.599 | 0.530 | 라벨 섞은 모델과 구분 안 됨(≈랜덤) | **NULL / reject** |
| PAM50 (4-class) | 0.805 | 0.818 | mean_embed 0.653 유의하게 상회 | **GENUINE (유일한 pass 후보)** |

**한 줄 결론:** 4개 중 **PAM50만** 형태학이 trivial baseline을 진짜로 상회. ER/PR은 신호는 있으나 (분자 subtype을 그대로 쓰는, 부분적으로 순환적인) baseline을 못 넘음. HER2는 신호 없음.

- PAM50은 정책(split_policy §4) 준수 위해 Normal 제외한 4-class로 재실행한 것이 기준. 5-class(0.759/0.722)는 정책 위반 → supersede.
- 단, "4-class가 5-class보다 낫다"는 비교는 라벨 공간이 달라 성립하지 않음(Critic 기각 수용). PAM50은 *자기 라벨 공간 안에서* baseline을 이겼다는 것이 유효한 주장.

## 2. 검증 신뢰성 (모두 통과)

site-disjoint 분할(병원·환자 교집합 0) · TCGA↔CPTAC 코호트 독립(0) · **label-shuffle(라벨 섞기) 대조로 leakage 배제** · paired bootstrap 유의성 검정 · counterfactual · Fig3/Fig4.
→ **결과는 버그·누수가 아니라 진짜**임이 정량으로 확인됨.

## 3. Critic 판정 (braveji)

ER caution · PR caution · **HER2 reject** · **PAM50 4-class = pass 후보 1순위**.
남은 sign-off 블로커는 전부 **kkkim 몫**: ① split_policy_v0 lock ② PAM50 라벨 소스 study_id 확정.
registry(BIOP02-57)는 append 방침 — 5-class caution→reject+superseded, 4-class 신규 cv-20260710.

## 4. 방향성 논의 (핵심)

- **Paper A(H&E→분자표현형 예측)는 novelty 소진.** 2026년 논문이 이미 동일 과제(TCGA→CPTAC, 13개 모델, HER2 실패까지)를 출판 → "정확도로는 못 이긴다."
- 새 악재가 아니라 **6월 초 전략문서(`research/novelty_positioning.md`)가 예견한 것의 실증.** 애초 차별점은 "더 나은 숫자"가 아니라 **재현·반증 가능 프로토콜**(외부검증·site 통제·Critic 게이트).
- **재정립 방향(kkkim, BIOP02-91): "cost-of-substitution".** 형태학의 가치를 정확도가 아니라 **"아형을 틀리면 치료가 얼마나 어긋나는가(치료 의사결정 비용)"**로 프레임.
- **프리모템 핵심 위험**(`guide/premortem_action_items_sjpark_20260710.md`): 형태학이 subtype 너머 정보를 안 주면 → 치료가설이 "가이드라인 재포장" → 반증 불가 → 리뷰어가 벨 근거 명확. 이 연쇄를 끊는 게 최우선.

## 5. 회의에서 결정할 것 (Open Questions)

1. **가장 중요한 질문:** H&E 형태학이 **PAM50 subtype을 넘는 무언가**를 준다는 걸 보일 수 있는가? 없다면 이미지 층의 존재 이유를 재정의해야 함.
2. Paper A를 **PAM50 중심**으로 재구성 + receptor는 정직하게 tempered로 갈지.
3. HER2: reject를 그대로 게재할지 vs EXAONE 재실험(비용: kkkim 리소스). — sjpark 의견은 정직한 negative result로 게재.
4. cost-of-substitution을 헤드라인으로 확정할지, 그러면 receptor 전제였던 **DepMap 전이(Paper B)를 PAM50 기반으로 재검토**할지.
5. 잔여 블로커 처리 일정: split lock·라벨 study_id(kkkim), 치료층 rule(jhans BIOP02-60).

---

*근거: BIOP02-53/56/57 코멘트, experiments/sjpark/(pam50_clam_mb_uni_v1_4class, fig4_external_sanity_lock, label_shuffle_multiseed_summary 등), research/novelty_positioning.md, guide/premortem_action_items_sjpark_20260710.md. 수치는 현재 분석 기준(후속 검증으로 갱신 가능).*
