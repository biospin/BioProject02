# INFRA_PRIVATE (예시) — 실값은 공개 저장소에 두지 않는다

CLAUDE.md의 `<PLACEHOLDER>` 실값을 담는 개인/사내 config 예시. **이 example만 커밋**하고, 실값 파일(`INFRA_PRIVATE.md` 또는 `~/.claude/biop02_infra.local`)은 `.gitignore`로 추적 제외한다.

```
SERVER_IP=<본 서버 공인 IP>
SERVER_INTERNAL_IP=<내부망 IP>
SSH_PORT_kkkim=<port>   # 팀원별
SSH_PORT_braveji=<port>
...
EMAIL_kkkim=<gmail>     # JIRA/Atlassian 계정
...
INSTITUTIONAL_EMAIL=<기관 이메일>   # HF 게이팅 신청용
```

접속: `ssh -p $SSH_PORT_<본인> <계정>@$SERVER_IP`
