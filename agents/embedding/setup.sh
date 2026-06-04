#!/usr/bin/env bash
# BIOP02-26 — Embedding Agent 환경 셋업
# Ubuntu 22.04, Python 3.10, CUDA 12.4 (A100 80GB)
# 전제: ~/miniconda3 설치 완료
set -e

CONDA_PYTHON=~/miniconda3/bin/python
CONDA_PIP=~/miniconda3/bin/pip
export LD_LIBRARY_PATH=~/miniconda3/lib:${LD_LIBRARY_PATH:-}

echo "=== [1/3] conda 확인 ==="

if [ ! -f "$CONDA_PYTHON" ]; then
    echo "  [오류] ~/miniconda3 가 없습니다. 먼저 Miniconda를 설치하세요:"
    echo "    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh"
    echo "    bash ~/miniconda.sh -b -p ~/miniconda3"
    exit 1
fi

echo "  conda python: $($CONDA_PYTHON --version)"

echo ""
echo "=== [2/3] 패키지 설치 ==="

# libvips (pyvips 의존성) — conda-forge
source ~/miniconda3/etc/profile.d/conda.sh
conda install -c conda-forge pyvips -y 2>&1 | grep -E "done|error|Error" || true

# PyTorch (CUDA 12.4)
$CONDA_PIP install --quiet torch torchvision \
    --index-url https://download.pytorch.org/whl/cu124

# 병리 이미지 처리 (pyvips는 conda-forge에서 설치됨 — 중복 설치 금지)
$CONDA_PIP install --quiet openslide-python openslide-bin

# 파운데이션 모델 관련
$CONDA_PIP install --quiet timm huggingface_hub transformers
# CONCH (MahmoodLab/CONCH) — HF 승인 후 설치
$CONDA_PIP install --quiet git+https://github.com/mahmoodlab/CONCH.git || \
    echo "  [warn] CONCH 설치 실패 — HF 접근 권한 확인 후 수동 설치: pip install git+https://github.com/mahmoodlab/CONCH.git"

# 유틸리티
$CONDA_PIP install --quiet numpy tqdm pillow

echo ""
echo "=== [3/3] 설치 확인 ==="

$CONDA_PYTHON - <<'EOF'
checks = []

def check(name, fn):
    try:
        fn()
        checks.append(f"  [OK] {name}")
    except Exception as e:
        checks.append(f"  [FAIL] {name}: {e}")

# pyvips는 torch보다 먼저 import — torch의 libjpeg가 먼저 로드되면 libvips와 충돌
import pyvips
checks.append(f"  [OK] pyvips {pyvips.__version__}")

check("torch + CUDA", lambda: (
    __import__("torch"),
    print(f"       torch={__import__('torch').__version__}, CUDA={__import__('torch').cuda.is_available()}")
))
check("timm",            lambda: __import__("timm"))
check("huggingface_hub", lambda: __import__("huggingface_hub"))
check("openslide",       lambda: __import__("openslide"))
check("numpy",           lambda: __import__("numpy"))
check("PIL",             lambda: __import__("PIL"))

for c in checks:
    print(c)
EOF

echo ""
echo "setup.sh 완료. 이후 스크립트 실행 시 ~/miniconda3/bin/python 사용."
