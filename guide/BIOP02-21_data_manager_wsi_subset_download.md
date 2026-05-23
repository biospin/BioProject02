# BIOP02-21 Data Manager Guide: TCGA-BRCA WSI Subset Download

이 문서는 BIOP02-21 데이터 담당자가 TCGA-BRCA WSI를 서버에 준비할 때 사용할 전달용 가이드입니다.

## 결론

- TCGA WSI 전체 1133장 다운로드는 하지 않는다.
- Paper A 범위에 맞춰 데이터 담당자가 확정한 manifest 또는 약 150장 subset만 다운로드한다.
- `/workspace/data/cache/biop02`는 임시 캐시 성격으로 사용한다.
- 원본 WSI 장기 보존 위치는 데이터 담당자가 관리하는 S3/NAS/read-only 원본 저장소로 둔다.
- Embedding 산출물은 영구 보존 대상으로 별도 관리한다.

## 현재 상태

Pilot 1장은 이미 준비되어 있으며, kkkim은 이 1장으로 타일링/임베딩 작업을 이어가면 된다.

```bash
/workspace/data/cache/biop02/pilot_wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs
```

파일럿 산출물 경로:

```bash
/workspace/data/cache/biop02/pilot_tiles/
/workspace/data/cache/biop02/pilot_embeddings/
/workspace/data/cache/biop02/logs/
```

## 권장 데이터 레이아웃

Subset 원본 WSI 캐시는 아래처럼 별도 디렉터리로 둔다.

```bash
/workspace/data/cache/biop02/tcga_brca_wsi_subset/
```

Manifest와 다운로드 로그는 같은 namespace 아래에 둔다.

```bash
/workspace/data/cache/biop02/manifests/
/workspace/data/cache/biop02/logs/
```

예상 구조:

```text
/workspace/data/cache/biop02/
  pilot_wsi/
  pilot_tiles/
  pilot_embeddings/
  tcga_brca_wsi_subset/
  manifests/
  logs/
```

## Manifest 요구사항

데이터 담당자는 다운로드 전에 subset manifest를 확정한다. 최소 컬럼:

```csv
case_id,slide_id,file_name,source_path,split,notes
TCGA-3C-AALI,TCGA-3C-AALI-01Z-00-DX1,TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs,/wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs,pilot,pilot slide
```

권장:

- Paper A subset은 약 150장으로 제한한다.
- 환자 단위 중복/누수를 피하기 위해 `case_id` 기준으로 split을 관리한다.
- 같은 환자의 DX1/DX2가 모두 있을 경우 포함 정책을 명시한다.
- manifest 파일명에는 날짜와 이슈 번호를 포함한다.

예:

```bash
/workspace/data/cache/biop02/manifests/BIOP02-21_tcga_brca_wsi_subset_2026-05-23.csv
```

## Synology NAS 공유 링크에서 받을 경우

현재 공유 링크:

```text
https://radisen-nas2.direct.quickconnect.to:5001/sharing/I1KGZnZWx
```

공유 폴더는 `/wsi`이며, 전체 파일 수는 1133개로 확인되었다. 전체 다운로드 금지.

Synology FolderSharing API 호출 방식:

1. 공유 세션 로그인

```bash
curl -L -c /tmp/syno_share.cookies \
  -X POST \
  --data 'api=SYNO.Core.Sharing.Login&version=1&method=login&sharing_id="I1KGZnZWx"&password=""' \
  'https://radisen-nas2.direct.quickconnect.to:5001/webapi/entry.cgi/SYNO.Core.Sharing.Login'
```

2. `/wsi` 파일 목록 조회

```bash
curl -L -b /tmp/syno_share.cookies \
  'https://radisen-nas2.direct.quickconnect.to:5001/webapi/entry.cgi?api=SYNO.FolderSharing.List&version=2&method=list&_sharing_id="I1KGZnZWx"&offset=0&limit=100&sort_by=name&sort_direction=asc&folder_path="/wsi"'
```

3. 단일 파일 다운로드

`SYNO.FolderSharing.Download`은 `dlink`에 파일 경로의 UTF-8 hex 값을 넣어야 한다.

예:

```bash
FILE='/wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs'
HEX=$(node -e "console.log(Buffer.from(process.argv[1], 'utf8').toString('hex'))" "$FILE")

curl -L -C - -b /tmp/syno_share.cookies \
  -o /workspace/data/cache/biop02/tcga_brca_wsi_subset/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs \
  "https://radisen-nas2.direct.quickconnect.to:5001/webapi/entry.cgi?api=SYNO.FolderSharing.Download&version=2&method=download&_sharing_id=\"I1KGZnZWx\"&dlink=\"$HEX\"&mode=download&stdhtml=false"
```

`-C -` 옵션을 사용하면 중단 후 재실행 시 이어받을 수 있다.

## 실행 전 확인

```bash
df -h /workspace/data/cache/biop02
du -sh /workspace/data/cache/biop02/* 2>/dev/null
```

현재 프로젝트 정책상 `/workspace/data/cache/biop02`는 캐시 영역이므로 200GB 내외를 넘기지 않는 것이 원칙이다. Subset 다운로드 전에 예상 용량을 계산하고, 초과 시 S3/NAS 원본 저장 정책을 먼저 확정한다.

## 완료 후 검증

```bash
find /workspace/data/cache/biop02/tcga_brca_wsi_subset -maxdepth 1 -type f -name '*.svs' | wc -l
du -sh /workspace/data/cache/biop02/tcga_brca_wsi_subset
ls -lh /workspace/data/cache/biop02/tcga_brca_wsi_subset | head
```

Manifest와 실제 파일명을 비교한다.

```bash
python - <<'PY'
import csv
from pathlib import Path

manifest = Path('/workspace/data/cache/biop02/manifests/BIOP02-21_tcga_brca_wsi_subset_2026-05-23.csv')
data_dir = Path('/workspace/data/cache/biop02/tcga_brca_wsi_subset')

expected = []
with manifest.open() as f:
    for row in csv.DictReader(f):
        expected.append(row['file_name'])

missing = [name for name in expected if not (data_dir / name).exists()]
extra = [p.name for p in data_dir.glob('*.svs') if p.name not in set(expected)]

print(f'expected={len(expected)}')
print(f'missing={len(missing)}')
print(f'extra={len(extra)}')
if missing:
    print('missing examples:', missing[:10])
if extra:
    print('extra examples:', extra[:10])
PY
```

## kkkim 작업 범위

kkkim은 현재 pilot 1장으로 다음 작업을 진행한다.

```bash
cd ~/project/BioProject02

export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}

~/miniconda3/bin/python agents/embedding/scripts/tile_wsi.py \
  --slide /workspace/data/cache/biop02/pilot_wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs \
  --config agents/embedding/configs/tile_config.yaml \
  --out /workspace/data/cache/biop02/pilot_tiles/TCGA-3C-AALI-01Z-00-DX1_coords.npy
```

Subset 전체 다운로드 및 manifest 관리는 데이터 담당자 책임으로 둔다.

## Jira Comment Template

BIOP02-21에 아래 내용을 코멘트로 남기고 데이터 담당자에게 assign한다.

```text
BIOP02-21 데이터 준비 범위 재확인 요청

현재 NAS 공유 링크에는 /wsi 아래 TCGA-BRCA WSI 1133개가 있으나, 프로젝트 문서 기준으로 TCGA WSI 전체 다운로드는 금지되어 있습니다. Paper A 범위는 약 150장 subset이므로, 전체 다운로드 대신 데이터 담당자가 확정한 manifest/subset 기준으로만 다운로드해 주세요.

요청 사항:
1. Paper A용 TCGA-BRCA WSI subset manifest 확정
   - 권장 컬럼: case_id, slide_id, file_name, source_path, split, notes
   - 환자 단위 split 누수 방지
   - DX1/DX2 중복 포함 정책 명시

2. 다운로드 대상
   - 전체 1133장 다운로드 금지
   - 확정 manifest에 포함된 약 150장만 다운로드

3. 서버 경로
   - manifest: /workspace/data/cache/biop02/manifests/
   - subset WSI cache: /workspace/data/cache/biop02/tcga_brca_wsi_subset/
   - logs: /workspace/data/cache/biop02/logs/

4. 저장 정책
   - /workspace/data/cache/biop02 는 cache 영역으로 보고 200GB 내외 원칙 준수
   - 원본 WSI 장기 보존은 S3/NAS/read-only 원본 저장소 정책으로 별도 관리
   - embedding 산출물은 영구 보존 대상으로 별도 관리

5. 참고
   - kkkim 작업 범위는 이미 준비된 pilot 1장으로 타일링/임베딩 파일럿을 진행하는 것
   - pilot WSI 경로:
     /workspace/data/cache/biop02/pilot_wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs

상세 가이드는 repo의 guide/BIOP02-21_data_manager_wsi_subset_download.md 를 참고해 주세요.
```
