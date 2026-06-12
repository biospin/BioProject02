# chakravarty-2017-oncokb — Lens: Industry / Access & License Gating

## 접근 경로 (Access)
- **웹 UI:** https://www.oncokb.org — 브라우저 조회는 무료(개별 변이 lookup).
- **Web API:** https://api.oncokb.org — **토큰 필수**. 기관/대학 이메일로 등록 + academic-use 라이선스 동의 → 승인 후 Account Settings에서 토큰 발급.
- **cBioPortal:** OncoKB 주석이 임베드되어 일부 actionability 표시를 무료로 노출.

## 라이선스 게이팅 (License gating — CRITICAL)
- **Academic:** 연구용은 **무료**. 단 토큰은 **6개월 만료** → 등록 이메일로 갱신 검증 후 자동 연장. 토큰은 **공개 repo·공유 금지**(우리 BIOP02 절대금지 규약과 동일 — git commit ❌).
- **Commercial / Hospital:** 별도 라이선스 계약 + **연간 라이선스 비용**(상업 조직, 병원 임상서비스/리포트).
- **벌크 다운로드 정책:** OncoKB는 **전체 주석 변이 다운로드를 미지원**(잦은 업데이트·umbrella term 로직 때문에 outdated/부정확 위험) → **API 조회를 권장**. 로컬 DB 사본은 라이선스 보유자 한정 case-by-case + 추가비용 — 사실상 재배포 불가.

## BIOP02에의 함의 (Implications)
1. **오라클은 쓰되 ship은 못 한다:** OncoKB 레벨을 grounding 기준으로 인용/조회는 가능하나, 주석 테이블을 우리 산출물에 **재배포 불가** → Critic gate를 OncoKB에 직접 의존하게 설계하면 재현/공개가 막힌다.
2. **토큰 운영:** kakyung.kim 기관 이메일(또는 팀 공용 institutional 메일)로 academic 토큰 발급, `~/.claude/settings.json`/개인 shell env에만 저장, 6개월 갱신 캘린더 등록.
3. **개방 floor 설계:** 실제 매칭 파이프라인은 **CIViC(CC0) + Open Targets + DGIdb**로 구성 → 누구나 재현 가능한 오픈 floor 확보. OncoKB는 **검증/캘리브레이션용 ceiling 레퍼런스**로만 호출.

## 정직성 메모 (Honesty)
OncoKB의 FDA-recognized Tx 레벨은 **게이트된 ceiling**이다. 오픈 라우트가 도달하는 범위(floor)를 ceiling으로 포장하지 말 것 — methodology-brief에서 잔여 gap을 정량·라벨링한다.
