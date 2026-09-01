# Fernandez-Romero et al., 2026 (MBEC domain generalisation) — lens: industry / reproducibility

> 근거: `_core.md` + 전문. 2026-09-02 전문 기반 재작성. 도구 선택, 재현 비용, 우리 파이프라인 적용 관점.

## 코드·프레임워크

- 공개 저장소 둘을 쓴다. CLAM 저장소 fork(`BIGS-investigacion/CLAiMem-ALL`)와 PathBench-MIL fork(`BIGS-Investigacion/PathBench-MIL`). 원문은 "all scripts are publicly available"이라고 적는다.
- 스택은 표준 조합이다. CLAM 전처리(조직 분할 포함), PathBench-MIL로 MIL 학습·튜닝, Optuna로 하이퍼파라미터 탐색, SlideFlow로 염색 정규화, scikit-learn으로 지표 계산.
- Optuna 설정은 본문에 있다. 50 trial, pruning 적용, validation set(학습셋의 10%)에서 mean average precision 최대화. 탐색 대상은 embedding dimension(z_dim 32~512)과 bag size(8~256) 둘뿐이고, 나머지(cross-entropy, ReLU, Adam)는 CLAM baseline 설정으로 고정한다.
- 저장소 실제 실행성, 라이선스, 커밋 상태는 확인하지 않았다. 재사용 전에 직접 봐야 한다.

## 데이터 가용성

- Data Availability 문장은 본문에 없다. 다만 두 코호트 모두 공개 리소스이고, 라벨 출처가 명시되어 있어 재구성은 가능하다. TCGA 라벨은 Thennavan et al. supplementary, CPTAC 라벨은 Krug et al.
- **주의할 필터**: TCGA에서 FFPE를 빼고 냉동만 남긴 결과가 1,522 슬라이드 / 1,079 환자다. 우리 TCGA-BRCA 코호트(진단 슬라이드 1,010 환자)와 포함 기준이 다르므로 환자 수를 나란히 놓고 비교하면 안 된다.

## 전처리 사양

| 항목 | 그들 | 우리 |
|---|---|---|
| 패치 추출 | 512×512 px @ 40× (육안 검토용), 이후 FM 입력에 맞춰 리스케일 | 256×256 px @ 20× |
| MIL 입력 타일 | 256×256 px / 128 µm @ 20× 고정 | 동일 FoV |
| 정규화 | 기본은 미적용. 별도 실험에서만 Macenko | 우리 파이프라인 설정 확인 필요 |
| FM 입력 해상도 | 각 FM 내부 리스케일(예: Virchow v2 224×224) | 동일 |

- FoV가 사실상 같으므로 임베딩 스케일은 호환된다. 우리 캐시를 재사용해 그들 설정을 흉내 내는 실험은 저렴하다.
- 형태 주석에는 40× 512×512 패치를 그대로 쓴다. 20× 표준 해상도의 두 배라 병리가 보기 좋다는 이유다.

## FM 스택 대비

- 그들 13종: ResNet-50(baseline), CTransPath, RetCCL, CONCH, UNI, Prov-GigaPath, Hibou-B, Hibou-L, H-optimus-0, Virchow v2, Phikon v2, Musk, UNI-2.
- 우리 승인 FM 상당수가 여기 포함된다. UNI, CONCH, Virchow v2, UNI-2, Prov-GigaPath.
- **실무 결론 1**: Virchow v2가 mean rank 2.00으로 1위이므로, 우리가 다중 FM 견고성을 볼 때 강한 baseline으로 쓸 근거가 된다. Ma et al.의 독립 보고와도 일치한다고 저자들이 적는다.
- **실무 결론 2**: 그렇다고 FM 교체가 도메인 문제를 풀지는 않는다. 13종 전부 외부에서 떨어지고, 우리가 쓰는 UNI는 HER2 상대 낙폭이 계산값 0.626으로 Virchow v2(0.451)보다 크다. "더 좋은 encoder"가 답이 아니라는 것이 우리 결정 레이어(보정·기권)의 정당화다.
- 2025년 초 이후 FM(H-optimus-1 등)은 빠져 있다. 최신 모델까지 포함한 비교는 아직 공백이다.

## 지표와 재계산 가능성

- PAM50 macro-F1, ER/PR/HER2 PR-AUC. AUROC는 쓰지 않는다.
- RPD = (Q_CV − Q_HO) / Q_CV. 정의가 단순해 우리 파이프라인에서도 그대로 계산할 수 있다. 다만 우리 지표는 AUROC이므로 같은 이름을 붙여 나란히 놓으면 오해를 부른다. 재계산한다면 우리 쪽에서도 macro-F1과 PR-AUC를 따로 뽑아야 한다.
- `원문 미확인:` 아키텍처별 클래스별 원값(Table S4), 염색 정규화 세부(Table S5), 유병률(Table S6), 코사인 거리(Table S7), 형태 유사도 행렬(Table S8), 일치도(Table S9)는 모두 Supplementary PDF(1.76 MB)에 있고 이 폴더에 없다. 필요하면 별도로 받아야 한다.

## 염색 정규화 재현 세부

- SlideFlow population-level preset v3. stain matrix는 H와 E 염색 벡터를 RGB 공간에 담은 3×2 행렬이고, 기준 최대 농도는 **[1.766, 1.280]**이다. TCGA 슬라이드 450장에서 뽑은 약 50,000 패치의 Macenko 분해 파라미터 평균으로 추정했다.
- 적용 시점이 중요하다. feature bag 생성 중 패치 단위로, 특징 추출 직전에 건다. 슬라이드 단위 사전 정규화가 아니다.
- 재현 시 유의: 정규화 효과가 클래스마다 부호가 갈린다. ER·PR 계열은 음수(손해), Luminal B·Normal-like는 양수. HER2-enriched는 어떤 아키텍처에서도 정확히 0이다. "정규화를 걸면 좋아진다"는 통념이 성립하지 않는 사례로 기록해 둘 만하다.

## 우리가 바로 쓸 것

1. **RPD를 보조축으로**. 우리 헤드라인은 라우팅 비용이지만, 예측 충실도 열화를 같은 자로 보고할 때 RPD 정의를 그대로 빌린다. 지표 차이는 각주로 명시한다.
2. **요인분해를 OOD 트리거 설계에 참조**. 특징공간 발산(클래스 중심점 코사인 거리)은 라벨 없이도 계산할 수 있으므로, 배치 시점의 기권 트리거 후보로 쓸 만하다. 그들 값 범위는 0.105~0.197이다.
3. **Virchow v2 벤치를 인용**. 우리 모델 비의존성 주장에 외부 근거로 붙인다.
4. **Macenko 정규화의 클래스 의존 효과**를 우리 전처리 결정의 반례로 인용한다.

## 거버넌스 메모

- 우리 산출물은 `hypothesis_only`를 유지하고 Critic 통과 전 공유하지 않는다. DRP 프레이밍, 약물 구조 입력, 다암종 일반화, ICI 관련 서술은 금지 사항 그대로다.
- 이 논문을 인용할 때도 "예측이 된다"를 우리 주장으로 옮겨 오지 않는다. 인용은 열화 사실과 요인분해까지다.
