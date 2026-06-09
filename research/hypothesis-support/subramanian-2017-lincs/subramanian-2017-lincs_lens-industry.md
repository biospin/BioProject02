# Lens — Industry / Practical (clue.io access & query API)

## clue.io 플랫폼 (CLUE = Connectivity Map Linked User Environment)
- URL: https://clue.io — 웹 앱 + REST API + Docker 컨테이너 제공.
- 무료 학술 사용 가능(계정 필요). 우리 프로젝트는 **academic, publication-only**이므로
  라이선스 적합 (단, query 결과를 임상/상업 권고로 쓰는 것은 금지 — hypothesis_only).
- 핵심 앱: **Query** (외부 signature 업로드 → connectivity 순위), **Touchstone**
  (참조 perturbagen 간 관계), **Repurposing** (FDA/clinical 약물 annotation).

## 우리 실무 워크플로 (route 2)
```
predicted BRCA phenotype (e.g. ER+ / PAM50 Basal)
  └→ phenotype-associated DEG signature (up / down gene lists, ~150 each)
       └→ clue.io Query app  OR  /api/...  (gene-set query)
            └→ ranked perturbagens by tau (τ)
                 └→ select τ ≤ -90 (strong reversal) candidates
                      └→ intersect with route-1 (PRISM/GDSC) hits  ← Exp4 convergence
```

## Query 입력 형식 (실무 메모)
- 입력: **up-gene set + down-gene set** (HUGO symbol, 보통 각 ~10–150개).
  L1000 space(978 landmark 우선)에 매핑되는 유전자가 신뢰도 높음 — DEG 추릴 때
  landmark 멤버십을 우대.
- 출력: perturbagen × tau 행렬. **음(-) tau = signature 역전 = 후보**.
  cell line별 tau와 summary tau(median) 모두 확인 — BRCA-유사 cell line(MCF7, MDAMB231 등)
  context에서의 tau를 우선 본다.
- 배치 query는 API/Docker로 자동화; 결과는 `experiments/.../route2_clue/` 에 저장하고
  query gene set·날짜·clue build 버전을 metrics에 기록(재현성).

## 접근 시 주의
- API rate limit / 계정 토큰: HF·AWS 키와 동일하게 **git commit 금지**, 개인 env에만 저장.
- clue build 버전이 갱신되면 tau가 바뀔 수 있음 → build id를 결과에 고정 기록.
- 결과 공유는 critic pass 후 `#biop02-experiments` 에서만 (프로젝트 규칙).
