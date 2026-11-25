"""Cài bộ công cụ trên máy mới, chạy một lần.
  python cai_dat.py [thư mục kênh]
Kiểm FFmpeg, Node, thư viện Python. THIẾU GÌ TỰ CÀI (winget, pip, npm) rồi kiểm lại; chép engine vào ~/.video-ngan/engine;
tạo ho-so-kenh.json mẫu (giọng AI miễn phí) và thư mục anh-video-cua-toi ở thư mục kênh.
Chỉ khi bị chặn (diệt virus như Bkav, thiếu quyền quản trị, không có winget) mới in đúng lệnh PowerShell để người dùng
tự dán (24/11/2026, người dẫn yêu cầu: kiểm xong thiếu gì Claude cài luôn).
Chỉ dùng thư viện chuẩn của Python để chạy được cả khi máy chưa có gì."""
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GOC = Path(__file__).resolve().parent.parent
ENGINE = Path.home() / ".video-ngan" / "engine"
THU_VIEN = {"faster_whisper": "faster-whisper", "cv2": "opencv-python", "numpy": "numpy", "google.auth": "google-auth",
            "requests": "requests", "playwright": "playwright", "edge_tts": "edge-tts"}
WINGET = {"ffmpeg": "Gyan.FFmpeg", "ffprobe": "Gyan.FFmpeg", "node": "OpenJS.NodeJS.LTS", "npm": "OpenJS.NodeJS.LTS"}
BREW = {"ffmpeg": "ffmpeg", "ffprobe": "ffmpeg", "node": "node", "npm": "node"}  # máy Mac (24/11/2026: lớp có học viên dùng MacBook)
MAC = sys.platform == "darwin"
CAI_HOMEBREW = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
DA_CAI_SAN = -1978335189  # mã winget: gói đã có
thieu, tu_dan = [], []


def lam_moi_path():
    """winget cài xong thì PATH của tiến trình này chưa có thư mục mới: đọc lại PATH của máy và người dùng."""
    if MAC:
        them = [x for x in ("/opt/homebrew/bin", "/usr/local/bin") if x not in os.environ.get("PATH", "")]
        os.environ["PATH"] = os.pathsep.join(them + [os.environ.get("PATH", "")])
        return
    if sys.platform != "win32":
        return
    import winreg
    phan = []
    for goc, khoa in ((winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                      (winreg.HKEY_CURRENT_USER, "Environment")):
        try:
            with winreg.OpenKey(goc, khoa) as k:
                phan.append(os.path.expandvars(winreg.QueryValueEx(k, "Path")[0]))
        except OSError:
            pass
    phan.append(str(Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links"))
    os.environ["PATH"] = ";".join(phan + [os.environ.get("PATH", "")])


def cai_winget(goi):
    lenh = f"winget install -e --id {goi} --accept-package-agreements --accept-source-agreements"
    if not shutil.which("winget"):
        tu_dan.append("# Máy chưa có winget: cài 'App Installer' trong Microsoft Store, rồi:\n    " + lenh)
        return False
    print(f"  → tự cài {goi} bằng winget (1–3 phút)...")
    r = subprocess.run(["winget", "install", "-e", "--id", goi, "--accept-package-agreements", "--accept-source-agreements", "--silent"])
    lam_moi_path()
    if r.returncode not in (0, DA_CAI_SAN):
        tu_dan.append(lenh)
        return False
    return True


def cai_brew(goi):
    lam_moi_path()
    lenh = f"brew install {goi}"
    if not shutil.which("brew"):
        dau = "# Máy Mac chưa có Homebrew: dán lệnh này, gõ mật khẩu máy khi được hỏi (bạn tự gõ, không đưa cho Claude):\n    " + CAI_HOMEBREW
        if dau not in tu_dan:
            tu_dan.append(dau)
        tu_dan.append(lenh)
        return False
    print(f"  → tự cài {goi} bằng Homebrew (1–5 phút)...")
    r = subprocess.run(["brew", "install", goi])
    lam_moi_path()
    if r.returncode:
        tu_dan.append(lenh)
        return False
    return True


def co(lenh):
    lam_moi_path()
    tim = shutil.which(lenh)
    if not tim and MAC and lenh in BREW:
        print(f"✘ {lenh} chưa có")
        if cai_brew(BREW[lenh]):
            tim = shutil.which(lenh)
    if not tim and sys.platform == "win32" and lenh in WINGET:
        print(f"✘ {lenh} chưa có")
        if cai_winget(WINGET[lenh]):
            tim = shutil.which(lenh)
    print(("✔ " if tim else "✘ ") + lenh + (f": {tim}" if tim else " vẫn chưa có"))
    if not tim:
        thieu.append(lenh)


def dung_cho_dan(lenh_ds):
    if MAC:
        print("\n✘ Chưa tự cài được hết. Mở ứng dụng Terminal (bấm Cmd + Space, gõ Terminal, Enter), dán lần lượt từng lệnh dưới đây:")
    else:
        print("\n✘ Máy chặn cài tự động (diệt virus như Bkav, hoặc thiếu quyền). Bấm Start, gõ PowerShell, chuột phải chọn "
              "'Run as administrator', dán lần lượt từng lệnh dưới đây:")
    for l in dict.fromkeys(lenh_ds):
        print("    " + l)
    print("Xong thì đóng hẳn Claude, mở lại, rồi nói với Claude: 'cài tiếp'.")
    sys.exit(1)


co("ffmpeg")
co("ffprobe")
co("node")
co("npm")
if thieu:
    dung_cho_dan(tu_dan or ([f"brew install {BREW[x]}" for x in thieu if x in BREW] if MAC else
                            [f"winget install -e --id {WINGET[x]}" for x in thieu if x in WINGET]))

can_pip = [p for m, p in THU_VIEN.items() if importlib.util.find_spec(m) is None]
co_gpu = shutil.which("nvidia-smi") is not None and subprocess.run(["nvidia-smi", "-L"], capture_output=True).returncode == 0
if co_gpu and importlib.util.find_spec("nvidia") is None:
    can_pip += ["nvidia-cublas-cu12", "nvidia-cudnn-cu12"]
print("✔ có GPU NVIDIA" if co_gpu else "⚠ không thấy GPU NVIDIA, phần nghe lời sẽ chạy CPU, chậm hơn nhiều")
if can_pip:
    print("Tự cài thư viện Python:", ", ".join(can_pip))
    # Python của Homebrew trên Mac chặn pip thường (externally-managed): thử thêm --break-system-packages
    if subprocess.run([sys.executable, "-m", "pip", "install", *can_pip]).returncode and \
            subprocess.run([sys.executable, "-m", "pip", "install", "--user", *can_pip]).returncode and \
            subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", *can_pip]).returncode:
        dung_cho_dan([(f'"{sys.executable}" -m pip install --user --break-system-packages ' if MAC else
                       f'& "{sys.executable}" -m pip install --user ') + " ".join(can_pip)])
    importlib.invalidate_caches()
    con = [p for m, p in THU_VIEN.items() if importlib.util.find_spec(m) is None]
    print("✔ đã cài xong thư viện Python" if not con else f"⚠ cài xong nhưng chưa nhận: {', '.join(con)} (mở lại Claude rồi chạy lại)")
if subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"]).returncode:
    print(f'⚠ Chưa tải được trình duyệt Playwright (chỉ cần khi chụp trang web). Tự dán sau:  & "{sys.executable}" -m playwright install chromium')
print("✔ thư viện Python đủ. Python dùng cho mọi lệnh sau:", sys.executable)

ENGINE.mkdir(parents=True, exist_ok=True)
shutil.copytree(GOC / "engine", ENGINE, dirs_exist_ok=True)
if not (ENGINE / "node_modules").exists():
    print("Tự cài Remotion (vài phút)...")
    if subprocess.run(["npm.cmd" if sys.platform == "win32" else "npm", "install", "--no-audit", "--no-fund"], cwd=ENGINE).returncode:
        dung_cho_dan([f'cd "{ENGINE}"; npm install --no-audit --no-fund'])
# Trình duyệt dựng hình của Remotion (khoảng 120 MB): tải luôn lúc cài, để lần dựng đầu trong lớp không phải chờ (24/11/2026)
if (ENGINE / "node_modules").exists():
    npx = "npx.cmd" if sys.platform == "win32" else "npx"
    if subprocess.run([npx, "remotion", "browser", "ensure"], cwd=ENGINE).returncode:
        print(f'⚠ Chưa tải được trình duyệt Remotion; lần dựng đầu sẽ tự tải. Hoặc tự dán:  cd "{ENGINE}"; npx remotion browser ensure')
    else:
        print("✔ Remotion và trình duyệt dựng hình đã sẵn sàng")
print("✔ engine:", ENGINE, "(dòng npm warn ... esbuild nếu có là cảnh báo bình thường, không phải lỗi)")

# Mô hình nghe lời Whisper large-v3 (khoảng 3 GB): tải luôn lúc cài ở nhà, tránh cả lớp cùng tải trên một mạng (24/11/2026)
print("Tải mô hình nghe lời Whisper large-v3 (khoảng 3 GB, chỉ lần đầu)...")
r = subprocess.run([sys.executable, "-c", "from faster_whisper.utils import download_model; print(download_model('large-v3'))"])
if r.returncode:
    print(f'⚠ Chưa tải được mô hình Whisper; lần làm video đầu sẽ tự tải. Hoặc tự dán:  & "{sys.executable}" -c "from faster_whisper.utils import download_model; download_model(\'large-v3\')"')
else:
    print("✔ mô hình Whisper đã sẵn sàng")

# Agent đi kèm gói (24/11/2026): video-dung (dựng) và video-cham-diem (chấm độc lập), chép vào ~/.claude/agents
AG = Path.home() / ".claude" / "agents"
AG.mkdir(parents=True, exist_ok=True)
for f in sorted((GOC / "agents").glob("*.md")):
    if (AG / f.name).exists():
        print("✔ agent đã có (giữ nguyên, không ghi đè):", f.stem)
        continue
    shutil.copy2(f, AG / f.name)
    print("✔ agent:", f.stem)

if len(sys.argv) > 1:
    kenh = Path(sys.argv[1])
    kenh.mkdir(parents=True, exist_ok=True)
    f = kenh / "ho-so-kenh.json"
    if f.exists():
        print("✔ đã có", f, "(giữ nguyên)")
    else:
        shutil.copy2(GOC / "references" / "ho-so-kenh.mau.json", f)
        print("✔ tạo", f, "(giọng AI miễn phí; có giọng nhân bản thì điền giongAI sau)")
    for x in ("kho-canh", "du-an", "anh-video-cua-toi"):
        (kenh / x).mkdir(exist_ok=True)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from nhap_kho import nhap
    nhap(kenh)  # có gói KHO-HOC-VIEN (Drive của lớp) trong Downloads thì giải nén cảnh, nhạc vào kênh
print("\n⚠ Agent mới (video-dung, video-cham-diem) chỉ nhận ở phiên Claude mở SAU khi cài: đóng hẳn Claude, mở lại.")
print("\nCài xong. Remotion, trình duyệt dựng hình và mô hình Whisper đã tải sẵn (nếu bước nào báo ⚠ thì lần làm video đầu sẽ tự tải). GPU NVIDIA giúp nhanh hơn nhiều, không có vẫn chạy được.")
