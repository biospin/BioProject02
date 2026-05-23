# Pilot WSI Upload Guide

이 문서는 맥북에 다운로드한 pilot `.svs` 1장을 서버로 업로드하고, 다음 세션에서 바로 이어서 타일링을 실행하기 위한 절차입니다.

## 현재 파일

맥북 로컬 파일:

```bash
~/project/data/cache/biop02/pilot_wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs
```

서버 업로드 대상:

```bash
/workspace/data/cache/biop02/pilot_wsi/
```

서버 산출물 경로:

```bash
/workspace/data/cache/biop02/pilot_tiles/
/workspace/data/cache/biop02/pilot_embeddings/
/workspace/data/cache/biop02/logs/
```

## 서버 폴더

서버에는 아래 폴더를 만들어 둔다.

```bash
ssh -p 2205 kkkim@121.126.38.195

mkdir -p /workspace/data/cache/biop02/pilot_wsi
mkdir -p /workspace/data/cache/biop02/pilot_tiles
mkdir -p /workspace/data/cache/biop02/pilot_embeddings
mkdir -p /workspace/data/cache/biop02/logs
```

확인:

```bash
ls -ld /workspace/data/cache/biop02 \
  /workspace/data/cache/biop02/pilot_wsi \
  /workspace/data/cache/biop02/pilot_tiles \
  /workspace/data/cache/biop02/pilot_embeddings \
  /workspace/data/cache/biop02/logs
```

## 맥북에서 서버로 업로드

이 명령은 서버가 아니라 **맥북 터미널**에서 실행한다.

```bash
rsync -avP -e "ssh -p 2205" \
  ~/project/data/cache/biop02/pilot_wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs \
  kkkim@121.126.38.195:/workspace/data/cache/biop02/pilot_wsi/
```

`-P` 옵션이 있으므로 중간에 끊겨도 같은 명령을 다시 실행하면 이어서 전송된다.

진행률이 보이지 않고 오래 멈춘 것처럼 보이면 다른 맥북 터미널에서 서버 파일 크기를 확인한다.

```bash
ssh -p 2205 kkkim@121.126.38.195 \
  "ls -lh /workspace/data/cache/biop02/pilot_wsi/"
```

또는:

```bash
ssh -p 2205 kkkim@121.126.38.195 \
  "du -h /workspace/data/cache/biop02/pilot_wsi/* 2>/dev/null"
```

정말 멈춘 경우 현재 `rsync`를 `Ctrl+C`로 중단하고, 더 자세한 로그로 다시 실행한다.

```bash
rsync -avvvP -e "ssh -p 2205" \
  ~/project/data/cache/biop02/pilot_wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs \
  kkkim@121.126.38.195:/workspace/data/cache/biop02/pilot_wsi/
```

## 업로드 완료 확인

서버에서:

```bash
ssh -p 2205 kkkim@121.126.38.195

ls -lh /workspace/data/cache/biop02/pilot_wsi/
```

대상 파일:

```bash
/workspace/data/cache/biop02/pilot_wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs
```

## 타일링 실행

서버에서:

```bash
cd ~/project/BioProject02

export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}

~/miniconda3/bin/python agents/embedding/scripts/tile_wsi.py \
  --slide /workspace/data/cache/biop02/pilot_wsi/TCGA-3C-AALI-01Z-00-DX1.F6E9A5DF-D8FB-45CF-B4BD-C6B76294C291.svs \
  --config agents/embedding/configs/tile_config.yaml \
  --out /workspace/data/cache/biop02/pilot_tiles/TCGA-3C-AALI-01Z-00-DX1_coords.npy
```

결과 확인:

```bash
ls -lh /workspace/data/cache/biop02/pilot_tiles/
```

예상 산출물:

```bash
TCGA-3C-AALI-01Z-00-DX1_coords.npy
TCGA-3C-AALI-01Z-00-DX1_coords.json
```

## 더미 임베딩 생성

서버에서:

```bash
~/miniconda3/bin/python agents/embedding/scripts/extract_dummy.py \
  --coords /workspace/data/cache/biop02/pilot_tiles/TCGA-3C-AALI-01Z-00-DX1_coords.npy \
  --out_dir /workspace/data/cache/biop02/pilot_embeddings/
```

결과 확인:

```bash
ls -lh /workspace/data/cache/biop02/pilot_embeddings/
```

## 다음 세션에서 바로 확인할 것

서버에서 아래 명령부터 실행한다.

```bash
ls -lh /workspace/data/cache/biop02/pilot_wsi/
ls -lh /workspace/data/cache/biop02/pilot_tiles/
ls -lh /workspace/data/cache/biop02/pilot_embeddings/
```

업로드된 `.svs`가 있으면 타일링부터 이어서 진행한다. `pilot_tiles`에 `coords.npy`와 `coords.json`이 이미 있으면 더미 임베딩부터 이어서 진행한다.

## 원칙

- `.svs`, `.npy` 같은 대용량 파일은 git repo에 넣지 않는다.
- git repo `BioProject02`는 코드, config, 문서만 관리한다.
- 데이터 namespace는 소문자 `biop02`로 통일한다.
- 현재 서버에는 `/data/cache`가 없으므로 pilot 데이터는 `/workspace/data/cache/biop02`를 사용한다.
