# 01 — 2-레이어 아키텍처: 분석 파이프라인 + 논문 생산 하네스

## 핵심 설계 결정

AI Scientist를 **하나의 거대한 자율 에이전트로 만들지 않았다.** 대신 **책임이 다른 두 레이어를 분리**하고, 위 레이어가 아래 레이어의 산출물을 소비하도록 설계했다.

```
┌─────────────────────────────────────────────────────────────────┐
│  레이어 B — 논문 생산 하네스 (paper-production harness)           │
│  결과 → 논문·그림·검수·발표. .claude/agents/ + .claude/skills/    │
│  literature-scout · novelty-strategist · research-methodologist  │
│  manuscript-writer · paper-critic · reviewer · presenter · design│
│  입구 = paper-production-orchestrator (Skill, 메인 루프가 실행)   │
└───────────────────────────▲─────────────────────────────────────┘
                            │  result 파일 + consolidated summary 소비
                            │  (도메인 슬롯 spatialpatho-analyst 가 다리)
┌───────────────────────────┴─────────────────────────────────────┐
│  레이어 A — 도메인 분석 파이프라인 (analysis pipeline)           │
│  H&E WSI → 임베딩 → 분자 표현형 예측 → 치료 근거 랭킹            │
│  agents/data · agents/embedding · agents/modeling ·              │
│  agents/therapeutic_evidence · agents/critic                    │
│  결과물 = experiments/<user>/<date>/ 5종 아티팩트               │
└─────────────────────────────────────────────────────────────────┘
```

근거: `docs/HARNESS.md` 서두 경고 — *"이건 논문 **생산** 하네스다. 기존 **분석 파이프라인**(`agents/<role>/`)을 대체하지 않는다 — 그 위에 얹혀 결과를 논문으로 쓰는 레이어이고, 분석 레이어는 도메인 슬롯 `spatialpatho-analyst`가 대표한다."*

## 왜 두 레이어로 나눴나

1. **재사용성.** 레이어 B(문헌·집필·검수·발표)는 도메인과 무관한 **연결조직(connective tissue)** 이다. `docs/HARNESS.md`의 로스터에서 대부분 멤버가 "재사용"으로 표시된다. 다른 논문/프로젝트(BIOP01 등)에 그대로 복사 가능. 도메인 특수성은 **단 하나의 슬롯** `spatialpatho-analyst`에 격리된다.
2. **관심사 분리.** 분석 레이어는 "숫자가 맞나"(누수·baseline·재현성)를 책임지고, 생산 레이어는 "그 숫자를 정직하게 논문으로 쓰나"를 책임진다. 검증 게이트가 두 레이어 경계에 놓인다(아래).
3. **성숙도 차이 흡수.** 프로젝트는 분석 진행 단계라 집필-단계 산출물(manuscript/figures)이 아직 없다. 생산 레이어는 `<FILL>` 플레이스홀더로 **미리 배선만 해두고**, 실제 경로는 첫 write-up-ready 결과가 나오면 팀이 채운다 (`docs/HARNESS.md` §4 "현재 하네스 상태").

## 레이어 A — 도메인 분석 파이프라인

역할별 워크스페이스(`agents/<role>/`)로 구성. 의존성 체인이 있다 (`CLAUDE.md` *Agent Dependency Chain*):

```
data (manifest + split_policy_v0)
  └→ embedding (어떤 슬라이드 tiling할지 결정)
        └→ modeling (dummy 임베딩 → 실제 임베딩 교체 후 학습)
              └→ therapeutic_evidence (DepMap/GDSC 전이)
                    └→ critic → critic_report.json
                          └→ orchestrator (등록·공유)
```

파이프라인의 과학적 목표: **H&E WSI → 형태학 임베딩 → 분자 표현형 예측(ER/PR/HER2·PAM50) → DepMap/GDSC 전이 → 순위화된 치료 가설.** 이것은 **약물반응예측(DRP)이 아니다** — 약물 구조 입력 없음, 가설 출력 전용 (`CLAUDE.md`, `README.md`).

**모든 실험은 5종 아티팩트로 봉인된다** (`AGENTS.md` §5): `config.yaml · model.pt · metrics.json · predictions.npy · critic_report.json` + `metrics.json` 안에 `commit_hash`. 이 강제 산출물 계약이 "실험을 실제로 수행했다"의 재현 가능한 증거가 된다.

## 레이어 B — 논문 생산 하네스

레이어 A가 만든 result 파일을 소비해 논문·그림·발표를 생산한다. 표준 경로 (`docs/HARNESS.md` §2):

```
research-methodologist / literature-scout / novelty-strategist   (기획·근거)
   └─▶ spatialpatho-analyst ──▶ result files + summary            (분석·검증)
   └─▶ manuscript-writer ──▶ manuscript (+ figure 스크립트 → figures)  (집필·그림)
   └─▶ paper-critic (+ agents/critic/ 체크리스트) ──▶ reviewer    (심사)
            └─▶ (수정) manuscript-writer
   └─▶ [검증 게이트: headline AUC/AUPRC 재계산] ──▶ presenter      (검증→발표)
```

## 두 레이어 경계의 두 게이트 (사람이 통과시킨다)

레이어 경계는 **자동화하지 않은 사람 게이트** 두 개로 지킨다 (`docs/HARNESS.md` §2, `CLAUDE.md` 사람 승인 게이트):

1. **검증 게이트 (verify-gate).** 커밋·공개 전, headline AUC/AUPRC를 모델 eval 출력에서 **결정론적으로 재계산**해 요약과 대조. 캐시·이전 세션 출력을 그대로 믿지 않는다. 실패하면 멈추고 사람에게 보고.
2. **공개 게이트 (publication gate).** 저자·소속·저자순서·corresponding email·IP·GPU 제공처(Modulabs) 확정 전까지 공개 보류. 팀 프로젝트라 저자-대면 내용은 팀 합의 필요.

→ 다음: [02_agents_and_roster.md](02_agents_and_roster.md)
