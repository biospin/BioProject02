# 형태학적 상관물 치환가능성 법칙 — 검정 현황 (2026-07-12, 회의용)

> 슬라이드용 정직 요약. claim_level: hypothesis_only. 상세=`../../experiments/crosscancer/*/full/LAW_TEST.md`, `SUBSTITUTABILITY_LAW_PREREGISTRATION.md`.

## 한 줄
**법칙은 검정력 충분한 유방·대장에서 확립. held-out(폐·위)은 방향적으로 corroborate하나 변이축 유병률이 낮아 저검정력 → INCONCLUSIVE.** 반증 트리거는 어디에도 없음(법칙 반증 아님), 그러나 held-out 확증도 아님.

## 암종별 현황
| 암종 | 역할 | 핵심 관측 | 검정력 | 판정 |
|---|---|---|---|---|
| 유방 | 확립(내부) | ER 0.90 가시 · **HER2 0.60 blind** · PAM50 0.76 | 충분 | **법칙 성립** |
| 대장 | 확립(내부) | MSI 0.92 가시 · **all-RAS 0.71**(bag-size 교란有) · CMS1 0.91 | 충분 | **법칙 성립** |
| 폐 | held-out #1 | 조직형 0.925(**양성대조 PASS**) · EGFR 0.81 · KRAS 0.65 · TRU 0.83 | 변이축 n_pos 14-15 | 방향 consistent, **INCONCLUSIVE** |
| 위 | held-out #2 | **HER2-amp 0.585**(유방과 함께 near-chance) · MSI 0.80 · EBV 0.87 · **Lauren 0.61 양성대조 FAIL** | n_pos 7-24 | consistent, **INCONCLUSIVE** |
| 두경부 | 대기 | HPV/EGFR | 임베딩 미완(회의 후) | 미착수 |

## held-out 두 검정의 정직한 메시지
- **폐**: 양성대조(조직형 0.925)가 통과해 **파이프라인 정상성 확립**. 변이축은 점추정이 법칙 방향(EGFR>KRAS, EGFR 등급적)과 일치하나 n_pos 14-15로 **확증·반증 모두 불가**. TRU-최고 예측은 점추정 미스(PP가 더 높음).
- **위**: **HER2 증폭이 유방·위 두 장기에서 모두 near-chance(≤0.65)=H&E-blind** → "증폭≠형태" 원리와 consistent. ⚠️ 단 (i) n_pos=14 exploratory라 "consistent with"까지만(0.585≈0.599의 정밀 근접은 우연, 증거 아님), (ii) **사전 양성대조(Lauren)가 라벨 희소로 실패** → 파이프라인 정상성은 MSI/EBV(real CI가 0.5 배제)로 de facto 확보(폐보다 약한 발판).

## 왜 held-out이 저검정력인가 (구조적, 정직히 제시)
표적 변이(EGFR·KRAS·HER2-amp)는 유병률 10%대 → 대형 코호트(폐 1050·위 440)에서도 holdout 양성 14-24명. **변이축의 held-out 확증은 근본적으로 어렵다.** 확증에는 (a) 다기관 코호트로 양성 확대, (b) 검정력 좋은 축(조직형·MSI·HPV) 전면화가 필요.

## 회의 프레이밍 (권장)
"법칙은 검정력 있는 유방·대장에서 섰다. 다른 장기(폐·위)에서 **같은 방향의 점추정**을 봤고 — 특히 **HER2 증폭이 유방·위 둘 다 H&E-blind** — 이는 corroboration이나 저검정력이라 확증은 아니다. 정직하게 '확립+방향적 corroboration'으로 제시하며, 확증용 후속(다기관·well-powered 축)을 설계한다." **과대주장(복제 확증) 금지.**
