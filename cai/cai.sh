#!/usr/bin/env bash
# Bộ cài Xưởng Video AI cho macOS. Chạy trong thư mục Bộ Não AI (Claude mở đúng thư mục đó):
#   curl -fsSL https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.sh | bash
# Chạy lại cùng lệnh = cập nhật. Không cần Homebrew, Git, mật khẩu máy.
# Biến chỉ dùng khi thử: XUONG_NGUON, XUONG_MAY, XUONG_GOI (nhe|du).
set -euo pipefail

dung() { echo; echo "DỪNG: $1"; exit 1; }

BO_NAO="$(pwd)"
[ -f "$BO_NAO/INDEX.md" ] && ls -d "$BO_NAO"/01_* >/dev/null 2>&1 || \
  dung "Thư mục đang mở ($BO_NAO) không phải Bộ Não AI (cần có INDEX.md và ngăn 01_...). Mở Claude đúng thư mục Bộ Não AI rồi dán lại câu lệnh."

MAY="${XUONG_MAY:-$HOME/Library/Application Support/XuongVideoAI}"
mkdir -p "$MAY"
echo "Bộ não: $BO_NAO"
echo "Phần mềm của xưởng đặt ở: $MAY"

case "$(uname -m)" in
  arm64) UV_TEN="uv-aarch64-apple-darwin" ;;
  *) UV_TEN="uv-x86_64-apple-darwin" ;;
esac
UV="$MAY/uv/uv"
if [ ! -x "$UV" ]; then
  echo "Tải uv (trình quản lý Python, khoảng 20 MB)..."
  mkdir -p "$MAY/uv"
  curl -fsSL "https://github.com/astral-sh/uv/releases/latest/download/$UV_TEN.tar.gz" | tar -xz -C "$MAY/uv" --strip-components 1
fi
"$UV" --version >/dev/null || dung "Máy không chạy được uv ($UV)."

export UV_PYTHON_INSTALL_DIR="$MAY/python" UV_CACHE_DIR="$MAY/uv-cache"
PY="$MAY/venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "Cài Python 3.12 cho xưởng..."
  "$UV" venv --python 3.12 --python-preference only-managed "$MAY/venv" || dung "Không cài được Python 3.12 (kiểm mạng rồi dán lại câu lệnh)."
fi

NGUON="${XUONG_NGUON:-}"
if [ -z "$NGUON" ]; then
  echo "Tải mã Xưởng Video AI từ GitHub..."
  rm -rf "$MAY/nguon" "$MAY/nguon-moi"
  mkdir -p "$MAY/nguon-moi"
  curl -fsSL "https://codeload.github.com/ductuenam/xuong-video-ai/tar.gz/refs/heads/main" | tar -xz -C "$MAY/nguon-moi" --strip-components 1
  mv "$MAY/nguon-moi" "$MAY/nguon"
  NGUON="$MAY/nguon"
fi

THAM=(-X utf8 "$NGUON/cai/cai_xuong.py" --bo-nao "$BO_NAO" --may "$MAY" --nguon "$NGUON" --uv "$UV")
[ -n "${XUONG_GOI:-}" ] && THAM+=(--goi "$XUONG_GOI")
exec "$PY" "${THAM[@]}"
