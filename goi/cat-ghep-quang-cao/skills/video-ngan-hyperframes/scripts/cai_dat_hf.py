"""Cài engine dự phòng HyperFrames vào <thư mục máy>/engine-hf (khóa `may` trong .claude/xuong-video.json; không có thì ~/.video-ngan/engine-hf) (cạnh engine Remotion), tải Chrome riêng, kiểm môi trường.
  python cai_dat_hf.py
Cần Node ≥ 22 và FFmpeg đã có trên máy (skill video-ngan-nguoi-noi đã cài). Chạy lại bao nhiêu lần cũng được."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def cau_hinh_xuong():
    """Đọc <bộ não>/.claude/xuong-video.json do bộ cài ghi: từ thư mục skill đi lên, rồi từ thư mục đang mở đi lên.
    Thêm thư mục ffmpeg, node của xưởng vào đầu PATH của tiến trình này."""
    for goc in (Path(__file__).resolve(), Path.cwd().resolve()):
        for p in (goc, *goc.parents):
            f = p / ".claude" / "xuong-video.json"
            if f.is_file():
                c = json.loads(f.read_text(encoding="utf-8"))
                for d in reversed(c.get("bin", [])):
                    if d and d not in os.environ.get("PATH", "").split(os.pathsep):
                        os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
                return c
    return {}


XUONG_CFG = cau_hinh_xuong()
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GOC = Path(__file__).resolve().parent.parent
# engine-hf nằm trong thư mục máy của bộ cài (xuong-video.json › may); không có thì chỗ cũ ~/.video-ngan/engine-hf
ENGINE_HF = (Path(XUONG_CFG["may"]) if XUONG_CFG.get("may") else Path.home() / ".video-ngan") / "engine-hf"
NPM = "npm.cmd" if sys.platform == "win32" else "npm"
NODE_HF = [str(ENGINE_HF / "node_modules" / "hyperframes" / "bin" / "hyperframes.mjs")]
MOI_TRUONG = {**os.environ, "HYPERFRAMES_NO_TELEMETRY": "1", "DO_NOT_TRACK": "1", "HYPERFRAMES_NO_UPDATE_CHECK": "1"}


def main():
    v = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.strip()
    if not v or int(v.lstrip("v").split(".")[0]) < 22:
        sys.exit(f"✘ Cần Node ≥ 22, máy đang có {v or 'chưa cài'}.")
    if not shutil.which("ffmpeg"):
        sys.exit("✘ Chưa có FFmpeg trên PATH.")
    ENGINE_HF.mkdir(parents=True, exist_ok=True)
    shutil.copytree(GOC / "engine-hf", ENGINE_HF, dirs_exist_ok=True)
    print("Cài gói (hyperframes, react, font tiếng Việt)…")
    subprocess.run([NPM, "install", "--no-fund", "--no-audit"], cwd=ENGINE_HF, check=True)
    print("Tải Chrome riêng cho HyperFrames…")
    subprocess.run(["node", *NODE_HF, "browser", "ensure"], cwd=ENGINE_HF, check=True, env=MOI_TRUONG)
    duong = subprocess.run(["node", *NODE_HF, "browser", "path"], cwd=ENGINE_HF, capture_output=True, text=True, env=MOI_TRUONG).stdout.strip().splitlines()[-1]
    if not Path(duong).exists():
        sys.exit(f"✘ Không thấy Chrome sau khi tải: {duong}")
    (ENGINE_HF / "chrome.txt").write_text(duong, encoding="utf-8")
    subprocess.run(["node", *NODE_HF, "doctor"], cwd=ENGINE_HF, env=MOI_TRUONG)
    print("✔ Engine dự phòng sẵn sàng:", ENGINE_HF)
    print("  Các dòng ✗ whisper-cpp, Kokoro, MusicGen, Docker là tùy chọn, skill không dùng.")


if __name__ == "__main__":
    main()
