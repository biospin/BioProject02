# CPTAC 임베딩-라벨 재조인 (공식 라벨 v1 기준) — BIOP02-55 후속

담당: kkkim (Embedding) | 날짜: 2026-07-09 | 상태: **스테이징(미승격)** — PR #24 머지 후 공유 경로로 승격

## 목적
jamie 공식 CPTAC 라벨(BIOP02-55, PR #24, branch `feat/BIOP02-55-jamie-cptac-labels` @ `a6f8681`)이
kkkim 임시본(395/653, `039b93a`)을 대체함에 따라, CPTAC UNI 임베딩 매니페스트의 라벨을
공식본 기준으로 재생성한다. (jamie 문서 `agents/data/cptac_labels_v1.md` "대체 관계"에서 kkkim 후속으로 명시)

## 방법
- 슬라이드 앵커 = 기존 임시 매니페스트 `/workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv`
  (653 슬라이드, `slide_id,case_id,embedding_path,…,split`). 임베딩 실물은 그대로 재사용(재추출 없음).
- `case_id`로 공식 라벨표 `cptac_brca_clinical_labels_v1.csv`(198 case)를 조인.
- 출력 컬럼에 **task별 가용 플래그** 추가: `has_er/has_pr/has_her2/has_pam50/has_labels`
  (공식본은 HER2 `Equivocal`·PAM50 `Normal-like`를 지우지 않고 원값 보존 + 플래그로 사용 가능 여부 표시).
- 스크립트: `regen_join.py` (이 디렉터리).

## 결과
- CPTAC 슬라이드 653 → **653/653 전부 공식 case에 매칭**.
- 4종 라벨 완비(`has_labels=1`): **395/653** — 임시본과 동일 커버리지(jamie 독립 교차검증과 일치).
- **task별 가용(신규 정보):** has_er 387 · has_pr 375 · **has_her2 294** · has_pam50 382 (/653).
- **임시본 대비 값 변경: 40개 슬라이드** (HER2 30, PAM50 13; ER/PR 0).
  - 원인: 임시본이 HER2 `Equivocal`을 빈칸 처리 → 공식본은 값 보존 + `has_her2=0`.
  - 예) `01BR023_*`: temp HER2 빈칸 → official `Equivocal`(has_her2=0).

## 후속 함의 (중요)
- **HER2 외부검증(caution 항목)에 직접 영향.** sjpark의 BIOP02-53 CPTAC 외부 eval은
  이제 `has_her2=1`(294 슬라이드)만 대상으로 재실행해야 정확하다. 임시본은 equivocal을 빈칸으로
  흘려 HER2 평가 대상이 불명확했음. ER/PR/PAM50은 값 안정(ER/PR 변경 0).
- 재실행 후 `cross_validation_registry.jsonl` caution 엔트리 재검토(braveji/Critic).

## 승격 절차 (PR #24 머지 후)
```bash
# 머지 확정 후 공유 경로로 승격
cp experiments/kkkim/20260709_cptac_official_join/embedding_manifest_cptac_uni_v1.csv \
   /workspace/data/cache/biop02/embedding_manifest_cptac_uni.csv
# (기존 임시본 백업은 이 디렉터리 embedding_manifest_cptac_uni.temp395.csv)
```
현재는 공유 파일을 건드리지 않음 — 미머지 상태에서 sjpark 파이프라인이 흔들리지 않도록 스테이징만.

## 파일
- `embedding_manifest_cptac_uni_v1.csv` — 재생성본(653행, 공식 라벨 + has_* 플래그)
- `embedding_manifest_cptac_uni.temp395.csv` — 기존 임시본 백업
- `cptac_brca_clinical_labels_v1.csv` — jamie 공식 라벨(브랜치에서 추출)
- `regen_join.py` — 재생성 스크립트
