# Runbook: Download WSI from Synology NAS

이 문서는 BIOP02에서 Synology NAS 공유 링크의 WSI 파일을 서버에서 직접 다운로드하는 방법을 기록한다.

## 원칙

- 전체 1133장 raw WSI를 한 번에 다운로드하지 않는다.
- BIOP02-21에서 확정한 manifest/subset의 `source_path`만 다운로드한다.
- raw `.svs`는 임시 cache로 보고, 타일링/embedding 추출 후 삭제 또는 LRU 정책에 따른다.
- 영구 보존 대상은 manifest, QC metadata, coords, embeddings, logs다.

## NAS 정보

공유 링크:

```text
https://radisen-nas2.direct.quickconnect.to:5001/sharing/I1KGZnZWx
```

공유 ID:

```text
I1KGZnZWx
```

공유 폴더:

```text
/wsi
```

확인된 전체 파일 수: 1133개. 전체 다운로드 금지.

## 1. 공유 세션 로그인

```bash
curl -L -c /tmp/syno_share.cookies \
  -X POST \
  --data 'api=SYNO.Core.Sharing.Login&version=1&method=login&sharing_id="I1KGZnZWx"&password=""' \
  'https://radisen-nas2.direct.quickconnect.to:5001/webapi/entry.cgi/SYNO.Core.Sharing.Login'
```

성공하면 `/tmp/syno_share.cookies`에 `sharing_sid`가 저장된다.

## 2. 파일 목록 조회

첫 100개 조회:

```bash
curl -L -b /tmp/syno_share.cookies \
  'https://radisen-nas2.direct.quickconnect.to:5001/webapi/entry.cgi?api=SYNO.FolderSharing.List&version=2&method=list&_sharing_id="I1KGZnZWx"&offset=0&limit=100&sort_by=name&sort_direction=asc&folder_path="/wsi"'
```

다음 페이지는 `offset=100`, `offset=200`처럼 증가시킨다.

## 3. 단일 파일 다운로드

`SYNO.FolderSharing.Download`은 `dlink`에 파일 경로의 UTF-8 hex 값을 넣어야 한다.

예시 파일:

```bash
FILE='/wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs'
OUT='/workspace/data/cache/biop02/tcga_brca_wsi_subset/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs'
HEX=$(node -e "console.log(Buffer.from(process.argv[1], 'utf8').toString('hex'))" "$FILE")

mkdir -p "$(dirname "$OUT")"

curl -L -C - -b /tmp/syno_share.cookies \
  -o "$OUT" \
  "https://radisen-nas2.direct.quickconnect.to:5001/webapi/entry.cgi?api=SYNO.FolderSharing.Download&version=2&method=download&_sharing_id=\"I1KGZnZWx\"&dlink=\"$HEX\"&mode=download&stdhtml=false"
```

`-C -` 옵션은 이어받기다. 중단되면 같은 명령을 다시 실행한다.

## 4. 원격 파일 크기 확인

전체를 받기 전에 첫 바이트만 요청해서 크기를 볼 수 있다.

```bash
FILE='/wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs'
HEX=$(node -e "console.log(Buffer.from(process.argv[1], 'utf8').toString('hex'))" "$FILE")

curl -I -L -b /tmp/syno_share.cookies \
  -H 'Range: bytes=0-0' \
  "https://radisen-nas2.direct.quickconnect.to:5001/webapi/entry.cgi?api=SYNO.FolderSharing.Download&version=2&method=download&_sharing_id=\"I1KGZnZWx\"&dlink=\"$HEX\"&mode=download&stdhtml=false"
```

응답의 `Content-Range` 끝 값이 전체 파일 크기다.

## 5. Manifest 기반 다운로드 스크립트 작성 원칙

- 입력 manifest의 `source_path`만 다운로드한다.
- 전체 `/wsi` 목록을 모두 다운로드 대상으로 사용하지 않는다.
- 출력 파일명은 manifest의 `file_name`을 사용한다.
- `curl -C -`로 이어받기를 지원한다.
- 완료 후 로컬 크기와 원격 크기를 비교한다.
- 성공/실패 로그를 남긴다.
- 타일링/embedding 추출 완료 후 raw `.svs`는 삭제 또는 LRU 처리한다.

권장 manifest 컬럼:

```csv
case_id,slide_id,file_name,source_path,split,priority,notes
```

권장 cache 경로는 BIOP02-82에서 확정되는 저장소 정책을 따른다. 임시 기본값:

```text
/workspace/data/cache/biop02/tcga_brca_wsi_subset/
```

## 6. 완료 검증

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

expected_set = set(expected)
missing = [name for name in expected if not (data_dir / name).exists()]
extra = [p.name for p in data_dir.glob('*.svs') if p.name not in expected_set]

print(f'expected={len(expected)}')
print(f'missing={len(missing)}')
print(f'extra={len(extra)}')
if missing:
    print('missing examples:', missing[:10])
if extra:
    print('extra examples:', extra[:10])
PY
```

## 참고

- 관련 Jira: BIOP02-21, BIOP02-82
- 관련 가이드: `guide/BIOP02-21_data_manager_wsi_subset_download.md`
