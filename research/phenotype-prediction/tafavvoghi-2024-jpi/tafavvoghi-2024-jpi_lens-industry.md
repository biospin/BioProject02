# tafavvoghi-2024-jpi — Lens: Industry / Reproducibility

## 재사용 자산 (Public code as baseline)
- **Repo:** `github.com/uit-hdl/BC_MolSubtyping` — PyTorch (torch 1.9.0 / torchvision 0.10.0, Py3.6.9), **GNU GPLv3**.
- **포함:** `train.py`, `test.py`, `parse_config.py`, `datahandler` 전처리/augmentation, JSON config 템플릿, CSV data-description 스펙. **train + inference 코드 모두 포함**, MultiStainDeepLearning 기반 "MultiModel" 아키텍처.
- **미포함:** 실제 BRCA 데이터셋(annotation 포함)은 사용자가 직접 공급해야 함 — 우리는 jamie의 TCGA-BRCA manifest + CPTAC로 채운다.

## Baseline 재현 평가 (Runnable?)
**Runnable as a baseline = Yes**, 단 정합 비용 존재:
- 라이선스 **GPLv3 copyleft** — baseline 재현/비교 용도는 안전하나, 우리 파이프라인에 코드를 직접 흡수하면 copyleft 전파. → **별도 `baselines/tafavvoghi/` 디렉토리에 격리 실행**, 우리 학습 코드와 import 경계 분리 권장.
- 환경이 오래됨(torch 1.9 / Py3.6.9) → A100 80GB 서버에서 **전용 conda env 또는 컨테이너 pin**으로 재현. 우리 메인 env와 충돌 금지.
- 데이터·split이 코드에 없음 → 우리가 **CSV/JSON config로 cohort·tile path 정의**해야 동작. 이때 우리 split 정책(site-stratified)을 주입해 *우리 조건*에서 baseline을 재측정.

## 재현성 리스크
- 원논문은 **외부 test split·site confound 통제가 없어**, repo 기본 설정으로 돌리면 0.727이 *낙관적으로* 재현될 수 있음. → 우리는 동일 코드를 **harder split**에서 돌려 baseline을 *공정 조건*으로 재보정.
- HER2-Warwick(71 WSI)는 별도 challenge 데이터 — 접근/정합 비용. 핵심 baseline은 TCGA(980)+CPTAC(382)로 충분.

## BIOP02 운영 함의
- baseline 실행은 **GPU 슬롯 예약(`#biop02-alerts`)** 후 격리 env에서; 결과는 **Critic pass 전까지 `#biop02-experiments` 공유 금지**.
- baseline 재현 수치는 `experiments/<user>/<date>/metrics.json`에 `embedding_model: tafavvoghi-cnn-baseline`, `commit_hash` 기록 — 우리 UNI+MIL 결과와 동일 schema로 직접 대조.
- 산출물은 진단 아형까지만; 우리의 therapeutic 단계는 **hypothesis-only**, DRP 표현 금지 거버넌스 적용.

## 검증 플래그
Repo 메타(GPLv3, PyTorch, train/test 코드, MultiModel, 데이터 미포함)는 GitHub WebFetch 확인. 논문 수치는 PMC11667687 확인.
