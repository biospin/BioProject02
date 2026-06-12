# ochoa-2023-opentargets — brief

Ochoa 등(2023, Nucleic Acids Research)은 차세대 **Open Targets Platform**을 기술한 논문으로, 유전체·문헌·약리·발현 등 다양한 증거를 통합해 **target-disease 연관 점수**와 표적의 **tractability(약물화 가능성)**를 정량적으로 제공하는 공개 플랫폼을 재설계·재구축했다. 핵심 기여는 "특정 유전자가 특정 질환의 신뢰할 만한 치료 표적인가"를 증거 가중 점수로 표준화해 질의 가능하게 한 것이다. BIOP02 관련성(KB=actionability·경로 grounding): BIOP02가 예측한 BRCA 분자표현형이 시사하는 표적/약물 가설에 대해, Open Targets는 **target↔BRCA 연관의 정량적 grounding**과 tractability 근거를 제공한다 — 약물 랭킹이 단지 cell-line 민감도 아티팩트가 아니라 질환-표적 생물학으로 뒷받침되는지를 Critic checklist #5(생물학적 타당성)에서 점검하는 데 쓰인다. 공개 점수·출처를 통해 추적가능한 근거를 남긴다. 출력은 hypothesis-only 랭킹임에 유의. *DOI unverified — 인용 전 CrossRef 재확인 필요.*

In short: Open Targets supplies evidence-weighted target-disease association scores and tractability, letting BIOP02 quantitatively ground whether a hypothesis target is a credible BRCA target (Critic #5) rather than a cell-line artifact — traceable, hypothesis-only. (unverified)
