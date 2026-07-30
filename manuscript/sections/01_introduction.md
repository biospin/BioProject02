# Introduction (집필 골격)

> 근거: literature-scout 산출물 [../../research/paperC-positioning/](../../research/paperC-positioning/) (scoop·gap 분석), [../../research/REFERENCE_LIST.md](../../research/REFERENCE_LIST.md)(77편). 인용은 verify_citations.py 기계 검증 후에만 확정.

H&E 조직 이미지에서 종양의 분자 상태를 예측하는 연구는 성숙한 분야다. 미세위성 불안정성·유전자 변이·발현 아형이 딥러닝으로 예측되어 왔고[Coudray 2018, Kather 2019·2020, Naik 2020], 병리 파운데이션 모델(UNI, Virchow 등)이 그 성능을 끌어올렸으며, 최근에는 분자 아형과 약물 감수성으로까지 확장되었다[Fernandez-Romero 2026, Dawood 2024]. "예측된다"는 명제는 이미 널리 입증되었다.

그러나 예측된다는 것이 분자검사를 임상적으로 대체해도 된다는 것을 뜻하지는 않는다. 예측 성능만 보고하는 관행은 대체가 초래하는 임상적 비용 — 잘못된 예측으로 치료를 배정했을 때의 손실 — 을 침묵한다. 이 간극이 이 논문의 자리다.

우리는 cost-of-substitution 프레임을 제안한다. 예측 오류를 치료 라우팅의 오분류 비용으로 환산해, 각 분자 축에서 H&E가 값싸게 대신될 수 있는지 아니면 분자검사가 필수인지를 정한다. 기준은 예측 가능성이 아니라 대체 안전성이다. 이 프레임은 약물 반응을 예측하지 않으며, 마커에서 치료 배정으로의 치환비용만 조작화한다.

이를 유방을 앵커로 한 다섯 암종(폐·대장·위·두경부)의 사전등록된 형태학적 상관물 법칙으로 검정한다([../../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md](../../experiments/crosscancer/SUBSTITUTABILITY_LAW_PREREGISTRATION.md)). 이는 열린 pan-cancer 아틀라스 확장이 아니라 법칙을 검정하기 위한 의도된 경계이며, 예측을 결과 이전에 봉인하는 사전등록으로 확증 강도를 확보한다.

이 논문의 기여는 다섯이다. (i) 다섯 암종의 치환비용 결정지도, (ii) 형태에 보이지 않는 축의 정직한 음성(위 Lauren diffuse), (iii) 유방 HER2 대체불가를 공간전사체 하한과 실제 치료결과로 비용 증명, (iv) Yale 실제 pCR 앵커, (v) 예측 정확도 경쟁이 아니라 "언제 대체가 안전한가"라는 다른 질문의 정립이다. 유방-only 예측[Fernandez-Romero 2026]이나 약물 감수성 예측[Dawood 2024]과 우리의 차별점은 교차암종 치환비용 결정지도, 사전등록 법칙, 그리고 실제-결과 앵커에 있다.

> 인용[대괄호]은 [../../research/REFERENCE_LIST.md](../../research/REFERENCE_LIST.md) 기준이며, 최종 확정 전 `agents/critic/scripts/verify_citations.py`로 기계 검증한다(눈으로 통과시키지 않는다).
