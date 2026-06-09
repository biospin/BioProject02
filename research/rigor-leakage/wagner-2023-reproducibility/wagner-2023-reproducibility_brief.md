# wagner-2023-reproducibility — brief

핵심 기여(core contribution): 전산병리(cpath) 분야 딥러닝 논문의 재현성·재사용성을 체계적으로 점검하여, 다수 연구가 코드·데이터·모델을 충분히 공개하지 않아 결과를 재현하기 어렵다는 점을 정량화한다. The survey reviews a large set of cpath deep-learning papers and finds that only a minority release code (reading_list 기준 161편 중 약 42편만 코드 공개), undermining reproducibility and reusability, and proposes practical checklists for sharing code, weights, and split definitions.

방법 요지(method): 출판된 cpath 연구들을 코드 공개 여부·데이터 접근성·문서화 기준으로 분류·집계하고, 재현 가능한 파이프라인을 위한 권고(체크리스트)를 제시한다. DOI는 csv 기준 unverified(Modern Pathology fulltext URL로 인용).

BIOP02 관련성(RIGOR — split/leakage 엄밀성): SpatialPathoAgent는 모든 실험 디렉터리에 `config.yaml`·`model.pt`·`metrics.json`·`predictions.npy`·`critic_report.json` 5종 산출물 + git commit hash를 강제한다. 본 논문은 이 **experiment artifact 정책의 직접적 동기**이며, 재현성을 거버넌스로 내재화하여 Scientific Critic 게이트와 함께 결과 신뢰성을 보장하는 근거로 인용된다.
