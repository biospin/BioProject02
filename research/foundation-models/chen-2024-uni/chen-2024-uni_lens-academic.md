# chen-2024-uni — Academic Lens

## 왜 이 backbone인가 (Why UNI as our primary backbone)
BIOP02는 H&E WSI → FM embedding → BRCA molecular phenotype → DepMap/GDSC **가설 생성**(hypothesis-only, not DRP)이다. 임베딩 backbone에 요구되는 것은 (1) 라벨 부족 환경에서의 강한 transfer, (2) BRCA를 포함한 다장기 일반화, (3) 재현 가능한 공개 weight다. UNI는 세 조건을 모두 충족한다.

- **Label efficiency가 결정적**: 우리 Paper A scope는 **~150 TCGA-BRCA slide subset**으로 의도적으로 작다. UNI는 4-shot에서 차순위 encoder 대비 클래스당 최대 **8배** 적은 예시로 동등 성능, prostate grading에서 **2배** label-efficient — small-N 레짐에 정확히 맞는 특성.
- **검증된 일반화**: **34개 task**, 20 organ, CAMELYON16 AUROC **0.966** 등 폭넓은 벤치마크. BRCA molecular phenotype prediction은 UNI의 평가 범위와 정합적인 다운스트림 transfer 과제.
- **독립 벤치마크 지지**: Campanella 2025, Neidlinger 2024는 UNI를 Prov-GigaPath·Virchow2·H-optimus-0와 함께 **top cluster**로 보고. 단일 논문 자평이 아니라 외부 검증된 backbone이라 Critic 7-point 중 baseline-comparison 논거가 견고하다.

## License & citation
- **License: CC-BY-NC-ND 4.0** — academic non-commercial, derivative 배포 제한. BIOP02는 **publication-only / academic research only** 스코프이므로 적합 (CLAUDE.md governance와 일치). 상업적 사용·재배포 금지 조항은 우리 산출물(논문/그림)에는 무관.
- **인용 형식**: Chen RJ, Ding T, Lu MY, et al. *Towards a general-purpose foundation model for computational pathology.* Nat Med. 2024. doi:10.1038/s41591-024-02857-3.
- 모델 사용 시 HuggingFace `MahmoodLab/uni` repo와 본 논문을 함께 인용.

## 학술적 주의 (Caveats)
- UNI는 **tile encoder일 뿐** — slide-level 결론은 aggregator(CLAM, lu-2021-clam) 선택에 좌우되므로 ablation 분리 필요.
- Stain-norm 미적용은 본 논문에서 정당화되나, TCGA↔CPTAC site-shift는 별도 cross-dataset 검증(Sprint 3) 대상.
