---
description: 백그라운드 작업·진행사항 점검 — 임베딩/재학습/watchdog 생존 + 게이트 상태를 실측해 보고 ("진행 사항 알려줘")
argument-hint: (없음) | deep (게이트·PR·JIRA까지)
---

"진행 사항 알려줘 / 중간 과정 어떻게 돼?" 요청을 처리한다. **기억이 아니라 실측**으로 답한다(다른 창이 동시에 작업하므로 내 세션 기억은 최신이 아니다 — `docs/PITFALLS_REGISTRY.md` C2).

## 원칙
- **추정 금지.** 프로세스·파일 개수·로그 시각을 실제로 찍어서 보고한다.
- **"멈춤"과 "다른 단계"를 구분한다.** GPU 0%가 곧 정지가 아니다(다운로드·타일 구간). 판정 전에 ① 최근 로그 시각 ② raw 폴더 크기 증가 ③ 워커 CPU를 본다(PITFALLS T4).
- `pgrep -f`/`pkill -f`는 **자기 셸까지 매칭**한다 → `ps -eo pid,ppid,cmd | grep "[m]atch"` 로 확인(PITFALLS T3).

## 절차 (기본)

1. **프로세스 생존** — 래퍼 제외하고 python만:
   ```bash
   ps -eo pid,ppid,etime,cmd | grep "[r]un_multifm.py" | head
   ps -eo pid,cmd | grep -E "[m]ultifm_retrain_watcher|[w]atchdog_loop"
   ```
2. **임베딩 진척** (FM별 개수 vs 목표: BRCA 1010 / 두경부 472 / 대장 622 / 위 442 / 폐 1052):
   ```bash
   for c in brca colorectal gastric_stad headneck_hnsc lung_nsclc; do
     for fm in virchow2 uni2h; do echo "$c/$fm: $(ls /workspace/data/cache/biop02/$c/$fm 2>/dev/null | wc -l)"; done; done
   ```
3. **최근 활동 시각** — `tail -3 experiments/kkkim/20260717_multifm_robustness/master.log` 와 현재 시각 대조. 몇 분 공백은 정상(대형 슬라이드 다운로드).
4. **재학습 커버리지** — `ls experiments/crosscancer/*/full/mil_cost_results_*.json`. 러너 대상 = 대장·폐·두경부·위(2026-07-21 확장).
5. **watchdog 재기동 이력** — `tail experiments/kkkim/20260717_multifm_robustness/watchdog.log` (비어 있으면 master 무중단 = 정상).

## deep (인자에 `deep`)
6. **병합 게이트** — `experiments/crosscancer/MERGE_TO_MAIN_CHECKLIST.md` G1~G5 현재 상태.
7. **브랜치 드리프트** — `git fetch && git rev-list --count origin/main..HEAD` / `HEAD..origin/main`. 뒤처짐 5+ 면 merge 먼저.
8. **JIRA/PR** — `~/bin/jira-search`(MCP 불필요), `gh pr list`(gh가 PATH에 없을 수 있음).

## 보고 형식
- 표 하나(암종 × FM × 진척)와 **한 줄 판정**(정상 진행 / 정체 의심 / 중단).
- **이상이 있으면 원인 후보를 좁혀서** 보고한다("느림"이 아니라 "네트워크 바운드 다운로드 구간, GPU는 유휴가 정상").
- 다음 자동 트리거(예: 대장 622 채우면 재학습 자동 시작)를 함께 알린다.

> 참고: SessionStart 훅 `.claude/hooks/bg_jobs_check.sh`가 매 세션 시작에 한 줄 요약을 자동 출력한다. 이 커맨드는 그보다 깊은 점검용.
