# CPTAC-BRCA IDC gs:// 버킷 접근방법 메모 (BIOP02-22)

담당: jamie (Data Agent) | 상태: 완료 | 관련: BIOP02-54 runbook(kkkim), BIOP02-55(임상 라벨)

## 1. 배경

CPTAC-BRCA는 TCGA-BRCA(학습/튜닝)와 분리된 **외부 hold-out 검증 코호트**다
(`split_policy_v0.md`). TCGA는 Synology NAS에 `.svs` 원본으로 있지만, CPTAC-BRCA는
**NCI Imaging Data Commons(IDC)** 의 공개 `gs://` 버킷에 있어 접근 방식이 다르다.
이 메모는 "그 버킷에 어떻게 접근하는가"만 1쪽으로 정리한다 — 임베딩 추출까지의
전체 파이프라인 상세는 `guide/runbooks/download_cptac_from_idc.md`를 참고.

## 2. 저장 형식 — DICOM-WSI (`.svs` 아님)

IDC의 CPTAC 시리즈는 `.svs` 단일 파일이 아니라 **DICOM-WSI**(시리즈 폴더 안에
여러 `.dcm` 조각)로 저장되어 있다. 컬렉션 id는 `cptac_brca`(소문자), 대상
modality는 `SM`(Slide Microscopy).

## 3. 접근 방법 — 인증 불필요

IDC는 공개 버킷이라 **GCP 인증 없이** 접근 가능하다. 공식 클라이언트
`idc-index`(내부적으로 `s5cmd` 사용)를 통해 SQL 질의 → 다운로드까지 처리한다.

```bash
pip install idc-index        # s5cmd 번들, 별도 인증 불필요
```

```python
from idc_index import IDCClient
client = IDCClient.client()
df = client.sql_query("""
    SELECT collection_id, PatientID, SeriesInstanceUID, SeriesDescription, series_size_MB
    FROM index
    WHERE collection_id = 'cptac_brca' AND Modality = 'SM'
""")
client.download_dicom_series(seriesInstanceUID, downloadDir)
```

- 다운로드 핸들 = `SeriesInstanceUID` (파일 경로가 아니라 이 UID로 지정)
- 재현 가능한 인벤토리 생성 스크립트: `agents/data/scripts/list_idc_cptac.py`
  → `agents/data/manifests/cptac_brca_idc_inventory.csv` (653 슬라이드 / 198 환자)

## 4. 접근 확인 근거 (실측)

- 2026-06-24, macmini에서 전체 흐름 실검증 완료 (`download_cptac_from_idc.md` §"DICOM-WSI 리더 — 검증됨"):
  `idc-index` 다운로드 → OpenSlide 4.0.1로 DICOM 정상 오픈(L0 17280×19316,
  MPP 0.25 정확 인식) → Otsu 타일링 → 임베딩 → raw 삭제, 전 구간 성공.
- 규모: 653 H&E 슬라이드 / 198 환자 / 총 ~120.2 GB.
- OpenSlide는 **4.0 이상**이어야 DICOM-WSI를 읽는다(`openslide-bin` 4.x). 3.x는 실패.

## 5. 데이터 관리 원칙 적용

- raw DICOM은 영구 보관하지 않는다 — 스트리밍 다운로드 → 타일링 → 임베딩 →
  즉시 삭제(agents/data/README.md 원칙과 동일).
- git에는 인벤토리 CSV(`cptac_brca_idc_inventory.csv`)와 재현 스크립트만 커밋한다.

## 참고

- 상세 파이프라인(다운로드→타일→임베딩→삭제, 서버 세팅): `guide/runbooks/download_cptac_from_idc.md`
- 인벤토리 생성: `agents/data/scripts/list_idc_cptac.py`
- 임상 라벨(별도 이슈): `agents/data/cptac_labels_v1.md` (BIOP02-55)
