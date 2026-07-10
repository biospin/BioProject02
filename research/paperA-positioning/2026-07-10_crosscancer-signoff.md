# Cross-cancer 트랙 사인오프 (Leader 결정 기록) — 2026-07-10

> **결정권자:** kkkim(Project Leader). **상태: Leader 승인(2026-07-10), 팀 헤드업 대기.**
> 관련: `2026-07-10_future-crosscancer-data.md`(후보·다운로드) · `2026-07-10_future-crosscancer-automation-plan.md`(자동화) · `2026-07-10_subtype-decision-map.md` §6(스쿱·원리).

## 1. 결정
타암종 cost-of-substitution 일반화를 **별도 트랙(Paper C 후보)** 으로 착수한다. **Papers A·B는 BRCA-only 유지** — 이 트랙은 A/B에 흡수하지 않는다.

## 2. Governance (Absolute Prohibition 처리)
- CLAUDE.md Absolute Prohibition: *"❌ Pan-cancer expansion — BRCA-only through Paper B."*
- **이 결정은 그 룰을 A/B 안에서 깨지 않는다.** cross-cancer는 **A/B와 분리된 별도/후속 트랙**이므로 "Papers A·B는 BRCA-only"와 충돌하지 않음.
- **권고 CLAUDE.md 반영(팀 합의 후):** Absolute Prohibitions에 각주 — *"cross-cancer는 Papers A·B 스코프 밖의 별도 트랙(Paper C)으로만 허용, Leader 승인 2026-07-10."* (지금 바로 CLAUDE.md 수정은 팀 프로젝트 파일이라 헤드업 후.)

## 3. 스코프·제약
- 목적: BRCA cost-of-substitution 결정지도를 타암종으로 일반화 → "표적 변이 축=H&E-blind / 형태학 축=triageable" 원리 stress-test.
- 제약 유지: **hypothesis_only · 비-DRP · per-experiment Critic 가드**. (BRCA와 동일 규칙.)
- 차별자: Arslan/Kather 예측지도 대비 **"AUC를 치료결정 fidelity 비용으로 변환"** (스쿱 회피).

## 4. 시퀀싱 (Paper A·발표 안 건드림)
- **Phase 0(지금 착수, GPU 0):** config-driven runner 스캐폴드 — 스코프 위반 아님(준비/코드).
- **Phase 1(사인오프 확정 + Paper A receptor 라우팅·발표 후, 또는 유휴 GPU):** 폐 NSCLC 파일럿. GPU 경쟁 있으므로 #biop02-alerts 슬롯 예약.
- Phase 2 대장 → Phase 3 cross-cancer decision map.

## 5. 담당
- 총괄/임베딩: kkkim · 모델(MIL): sjpark · 치료축 매핑/세포주: jhans · Critic: braveji. (BRCA 트랙 여력 확보 후 투입.)

## 6. 남은 사람 액션 (Leader=kkkim)
- [ ] **팀 헤드업** — 주간싱크/#biop02-general에 "cross-cancer 별도 트랙 착수, A/B는 BRCA-only 유지, GPU는 유휴 슬롯" 공유(공유 자원 가시성).
- [ ] (합의 후) CLAUDE.md Absolute Prohibitions 각주 반영.
- [ ] JIRA 에픽 확인/조정(생성됨: 아래).

## 7. 상태
- Leader 승인: **2026-07-10.** 팀 헤드업: 대기. Phase 0 스캐폴드: 착수(별도 커밋). JIRA 에픽: 생성.
