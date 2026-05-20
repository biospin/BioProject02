# S3 / NAS / MinIO 스토리지 비교안 (v0.1)

> 작성: 2026-05-16 braveji (ykji) | 5/22 미팅 결정 안건 (BIOP02-14)

---

## 요구사항 요약

| 항목 | 내용 |
|---|---|
| Raw WSI (TCGA-BRCA ~150장) | 읽기 전용, 원격 접근 |
| Processed/Tiled cache | LRU 200 GB, 빠른 I/O 필요 |
| Embedding (영구 보존) | 고속 랜덤 접근, `.npy` 파일 다수 |
| 서버 환경 | A100 서버 1대, 2 TB root 디스크 |
| 팀원 수 | 6명 동시 접근 |
| 예산 | 최소화 (학술 연구) |

---

## 옵션별 비교

### Option A — AWS S3 (퍼블릭 클라우드)

| 항목 | 내용 |
|---|---|
| **용도** | Raw WSI 원격 저장 (현재 계획) |
| **비용** | ~$0.023/GB-월 (S3 Standard), 150 slides × 평균 1 GB = ~$3.5/월 |
| **접근 방식** | `aws s3 cp` / `rclone` / S3FS-FUSE 마운트 |
| **장점** | TCGA open-access 데이터 직접 링크 가능, 팀원 어디서든 접근 |
| **단점** | egress 비용 (서버 → S3 읽기 반복 시 과금), 레이턴시 |
| **권장 용도** | Raw WSI read-only 저장소 |

**TCGA open access:** GDC Data Portal에서 직접 `s3://gdc-tcga-phs000178-open/` 접근 가능 (읽기 무료).

---

### Option B — 로컬 NAS (서버 내 디스크)

| 항목 | 내용 |
|---|---|
| **용도** | `/data/cache/` LRU 200 GB, embedding 영구 보존 |
| **비용** | 서버 2 TB 디스크 내 할당 (추가 비용 없음) |
| **접근 방식** | 로컬 파일시스템 직접 |
| **장점** | 최고 I/O 속도 (NVMe 기준 수 GB/s), 레이턴시 없음, 비용 없음 |
| **단점** | 2 TB 한계, 디스크 장애 시 복구 불가 (RAID 없음), 서버 1대 의존 |
| **권장 용도** | Processed tile cache + Embedding 영구 저장 |

---

### Option C — MinIO (자체 호스팅 S3 호환)

| 항목 | 내용 |
|---|---|
| **용도** | 서버 내 S3 호환 오브젝트 스토리지 |
| **비용** | 오픈소스 무료, 서버 디스크 사용 |
| **접근 방식** | S3 API 호환 (`boto3`, `rclone`, AWS CLI 그대로 사용) |
| **장점** | S3 인터페이스 유지 → 나중에 실제 S3로 마이그레이션 용이, 버저닝/접근 로그 가능 |
| **단점** | 추가 설정/운영 부담 (Docker 컨테이너 구동), 디스크 한계는 동일 |
| **권장 용도** | Embedding 영구 저장 (S3 인터페이스 원할 경우) |

---

## 권장안 (3-tier)

```
[Raw WSI]          AWS S3 / GDC 직접 접근 (read-only, 추가 저장 없음)
                       ↓ rclone / aws s3 cp (필요 시만)
[Tile cache]       /data/cache/  (로컬 NAS, LRU 200 GB)
                       ↓ 학습 시 직접 접근
[Embedding 영구]   /data/embeddings/  (로컬 NAS, 별도 파티션)
```

- **Raw WSI:** GDC public S3 직접 접근 or rclone으로 필요 슬라이드만 pull → `/data/cache/` 임시 보관
- **Tile cache:** `/data/cache/` 200 GB LRU. 가득 차면 오래된 것 삭제. Raw WSI는 언제든 재다운로드 가능.
- **Embedding:** `/data/embeddings/` 영구 보존. Sprint 1 완료 후 크기 측정 (~150 slides × 5K tiles × 1K dim × float32 = ~3 GB).

MinIO는 **Sprint 1 이후 필요 시 도입 결정** (현재는 로컬 NAS로 충분할 가능성 높음).

---

## 현재 운영 중인 스토리지 — NCP Object Storage

> Confluence [데이터 저장소(S3)](https://biospin-ai.atlassian.net/wiki/spaces/VC/pages/20086785/S3) 페이지 기준

팀은 AWS S3가 아닌 **Naver Cloud Platform(NCP) Object Storage**를 사용 중입니다.  
AWS CLI를 그대로 사용하되 `--endpoint-url`만 NCP로 변경합니다.

### 연결 설정 (최초 1회)

```bash
# AWS CLI 설치
python -m venv myenv
source myenv/bin/activate
pip install awscli

# NCP IAM 자격증명 설정 (키는 NCP 콘솔 → 마이페이지 → 인증키 관리에서 발급)
aws configure
# AWS Access Key ID:     <NCP_ACCESS_KEY>
# AWS Secret Access Key: <NCP_SECRET_KEY>
# Default region name:   [Enter — 공란]
# Default output format: [Enter — 공란]

# ~/.bashrc에 endpoint alias 추가 (매번 --endpoint-url 생략 가능)
export AWS_METADATA_SERVICE_TIMEOUT=10
alias aws="aws --endpoint-url=https://kr.object.ncloudstorage.com"
source ~/.bashrc
```

> **주의:** IAM 키는 절대 git commit 금지. 서버 `~/.bashrc` 또는 `~/.aws/credentials`에만 보관.

### 주요 명령어

```bash
# 기본 버킷: biospin
aws s3 ls                                          # 버킷 목록 조회
aws s3 ls s3://biospin/                            # biospin 버킷 내 파일 목록
aws s3 cp <local_path> s3://biospin/<파일명>        # 오브젝트 업로드
aws s3 cp s3://biospin/<파일명> <local_path>        # 오브젝트 다운로드
aws s3 rm s3://biospin/<파일명>                     # 오브젝트 삭제
aws s3 cp empty.txt s3://biospin/<폴더명>/          # 디렉토리 생성 (빈 파일 업로드)
```

### Windows용 GUI 뷰어

- **S3 Browser**: https://s3browser.com/ 다운로드 후 NCP endpoint 입력

### 3-tier에서의 위치

| 레이어 | 스토리지 | 비고 |
|---|---|---|
| Raw WSI (원본) | **NCP biospin 버킷** | read-only, rclone으로 pull |
| Tile cache | `/data/cache/` 로컬 | LRU 200 GB |
| Embedding (영구) | `/data/embeddings/` 로컬 | Sprint 1 후 NCP 백업 검토 |

---

## 5/22 미팅 결정 사항

- [ ] Raw WSI 접근 방식 최종 결정: GDC 직접 or S3 복사
- [ ] `/data/cache/` LRU 200 GB 정책 lock
- [ ] Embedding 저장 경로 확정 (`/data/embeddings/` 또는 MinIO)
- [ ] MinIO 도입 여부: Sprint 1 결과 보고 후 결정 or 지금 설치

---

## 변경 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v0.1 | 2026-05-16 | 최초 작성. 3-tier 권장안 포함. |
| v0.2 | 2026-05-20 | NCP Object Storage 운영 정보 추가 (Confluence 데이터 저장소(S3) 페이지 기준). |
