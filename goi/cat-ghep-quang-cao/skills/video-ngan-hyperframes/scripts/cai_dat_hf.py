"""Cài engine dự phòng HyperFrames vào ~/.video-ngan/engine-hf (cạnh engine Remotion), tải Chrome riêng, kiểm môi trường.
  python cai_dat_hf.py
Cần Node ≥ 22 và FFmpeg đã có trên máy (skill video-ngan-nguoi-noi đã cài). Chạy lại bao nhiêu lần cũng được."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GOC = Path(__file__).resolve().parent.parent
ENGINE_HF = Path.home() / ".video-ngan" / "engine-hf"
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
