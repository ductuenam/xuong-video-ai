"""Dựng lớp hình (render/hinh-cam.mp4) bằng HyperFrames thay cho Remotion, rồi trả lại dây chuyền chính.
  python dung_hf.py <thư mục dự án> [--tu chuan-bi|bundle|anh-tinh|render|tiep] [--den <bước>] [--het]

Dùng chung toàn bộ dữ liệu của skill video-ngan-nguoi-noi: doan.json, loi.txt, canh.json, props.json, public/.
Mã cảnh vẫn là engine/src/MoHinh.tsx của skill chính, chạy qua lớp thay thế shim/ nên không phải vẽ lại cảnh nào.

  chuan-bi  chạy dung.py của skill chính đến bước canh (master, phụ đề, props.json) nếu chưa có
  bundle    đóng app.js + font cục bộ + index.html vào render/hf/, liên kết public/ thành render/hf/assets/
  anh-tinh  ảnh soát khung 92% mỗi cảnh → soat-tinh-hf-*.jpg (cùng mốc với ảnh soát Remotion)
  render    npx hyperframes render → render/hinh-cam.mp4 (không tiếng)
  tiep      chạy dung.py của skill chính từ bước tron: trộn âm, tờ soát, nghiệm thu, gắn nhận diện

Mặc định dừng sau anh-tinh để xem ảnh soát. Ổn thì: --tu render. Thêm --het để chạy một mạch."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SKILL_CHINH = Path.home() / ".claude" / "skills" / "video-ngan-nguoi-noi"
sys.path.insert(0, str(SKILL_CHINH / "scripts"))
from chung import GOC_SKILL, doc, ghi, ho_so  # noqa: E402

ENGINE_HF = Path.home() / ".video-ngan" / "engine-hf"
HF = [str(ENGINE_HF / "node_modules" / "hyperframes" / "bin" / "hyperframes.mjs")]
BUOC = ["chuan-bi", "bundle", "anh-tinh", "render", "tiep"]
TRUONG_KENH = ["ten", "chuLinhVat", "nhanCanhAI", "nhanAnhAI", "mauChinh", "mauPhu", "mauBia"]
MOI_TRUONG = {**os.environ, "HYPERFRAMES_NO_TELEMETRY": "1", "DO_NOT_TRACK": "1", "HYPERFRAMES_NO_UPDATE_CHECK": "1"}


def chay(cmd, **k):
    return subprocess.run([str(x) for x in cmd], check=True, **k)


def chrome():
    f = ENGINE_HF / "chrome.txt"
    if not f.exists():
        sys.exit("✘ Chưa cài engine dự phòng. Chạy: python cai_dat_hf.py")
    return f.read_text(encoding="utf-8").strip()


def b_chuan_bi(da):
    if (da / "props.json").exists() and (da / "props.json").stat().st_mtime >= (da / "canh.json").stat().st_mtime:
        print("props.json đã mới hơn canh.json, bỏ qua")
        return
    chay([sys.executable, SKILL_CHINH / "scripts" / "dung.py", da, "--den", "canh"], cwd=SKILL_CHINH / "scripts")


def lien_ket(nguon, dich):
    """Nối public/ sang assets/: liên kết cứng từng file (không tốn chỗ), khác ổ thì chép."""
    shutil.rmtree(dich, ignore_errors=True)
    for f in nguon.rglob("*"):
        if f.is_file():
            d = dich / f.relative_to(nguon)
            d.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(f, d)
            except OSError:
                shutil.copy2(f, d)


def b_bundle(da, h):
    if not (ENGINE_HF / "node_modules").exists():
        sys.exit("✘ Chưa cài engine dự phòng. Chạy: python cai_dat_hf.py")
    # Mã cảnh lấy từ skill chính mỗi lần dựng: sửa MoHinh.tsx ở đó là bản dự phòng có luôn
    shutil.copytree(GOC_SKILL / "engine" / "src", ENGINE_HF / "src", dirs_exist_ok=True)
    ghi(ENGINE_HF / "src" / "kenh.json", {k: h[k] for k in TRUONG_KENH})
    ra = da / "render" / "hf"
    ra.mkdir(parents=True, exist_ok=True)
    chay(["node", ENGINE_HF / "dong_bundle.mjs", ra], cwd=ENGINE_HF)
    lien_ket(da / "public", ra / "assets")
    p = doc(da / "props.json")
    du_lieu = json.dumps(p, ensure_ascii=False).replace("</", "<\\/")
    (ra / "index.html").write_text(f"""<!doctype html>
<html><head><meta charset="utf-8"><link rel="stylesheet" href="fonts.css">
<style>html,body{{margin:0;background:#FFF3EA}}#root{{position:relative;width:1080px;height:1920px;overflow:hidden}}#app{{position:absolute;inset:0}}</style></head>
<body>
<div id="root" data-composition-id="root" data-width="1080" data-height="1920" data-start="0" data-duration="{p['thoiLuongGiay']}" data-fps="30"><div id="app"></div></div>
<script>window.__PROPS__ = {du_lieu};</script>
<script src="app.js"></script>
</body></html>
""", encoding="utf-8")
    print("trang:", ra / "index.html")


def b_anh_tinh(da):
    import cv2
    import numpy as np
    ra = da / "render" / "hf" / "anh-tinh"
    shutil.rmtree(ra, ignore_errors=True)
    for f in da.glob("soat-tinh-hf-*.jpg"):
        f.unlink()
    chay(["node", ENGINE_HF / "chup_khung.mjs", da / "render" / "hf" / "index.html", da / "props.json", ra, chrome()], cwd=ENGINE_HF)
    o = []
    for f in sorted(ra.glob("*.jpg")):
        a = cv2.resize(cv2.imdecode(np.fromfile(f, "u1"), 1), (432, 768), interpolation=cv2.INTER_AREA)
        cv2.putText(a, f.stem, (8, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 3)
        o.append(a)
    cot = 5
    while len(o) % cot:
        o.append(np.zeros_like(o[0]))
    for n, i in enumerate(range(0, len(o), cot), 1):
        cv2.imencode(".jpg", np.hstack(o[i:i + cot]), [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tofile(str(da / f"soat-tinh-hf-{n}.jpg"))
        print("ảnh soát:", da / f"soat-tinh-hf-{n}.jpg")


def b_render(da, docker=False):
    ra = da / "render" / "hinh-cam.mp4"
    tam = da / "render" / "hinh-cam-hf.mp4"
    tam.unlink(missing_ok=True)
    try:
        chay(["node", *HF, "render", da / "render" / "hf", "-o", tam, "--crf", "14", "--quality", "delivery", "--video-frame-format", "png", *(["--docker"] if docker else [])], cwd=da / "render" / "hf", env=MOI_TRUONG)
    except subprocess.CalledProcessError:
        print("✘ HyperFrames render hỏng. Gặp 'spawn EPERM': máy đang chặn tiến trình canh Chrome của HyperFrames,"
              " xem mục Lỗi đã gặp trong SKILL.md. Không sửa mã trong node_modules để lách.")
        raise
    # Kiểm cỡ khung và thời lượng trước khi thay hinh-cam.mp4 của dây chuyền chính
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(tam)], capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    w, hh, dai = j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"]["duration"])
    can = doc(da / "props.json")["thoiLuongGiay"]
    if (w, hh) != (1080, 1920) or abs(dai - can) > 0.1:
        sys.exit(f"✘ hinh-cam từ HyperFrames sai: {w}×{hh}, {dai:.2f} giây (cần 1080×1920, {can:.2f} giây)")
    tam.replace(ra)
    print("hinh-cam:", ra, f"{dai:.2f} giây")


def b_tiep(da):
    chay([sys.executable, SKILL_CHINH / "scripts" / "dung.py", da, "--tu", "tron"], cwd=SKILL_CHINH / "scripts")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("du_an")
    ap.add_argument("--tu", choices=BUOC, default="chuan-bi")
    ap.add_argument("--den", choices=BUOC)
    ap.add_argument("--het", action="store_true", help="không dừng ở bước anh-tinh")
    ap.add_argument("--docker", action="store_true", help="render trong container Docker (cần Docker Desktop đang chạy)")
    a = ap.parse_args()
    if not a.den:
        a.den = "anh-tinh" if not a.het and BUOC.index(a.tu) <= BUOC.index("anh-tinh") else "tiep"
    da = Path(a.du_an).resolve()
    h = ho_so(da)
    for f in ("doan.json", "loi.txt", "canh.json"):
        if not (da / f).exists():
            sys.exit(f"✘ Dự án thiếu {f}")
    dau = time.time()
    for b in BUOC[BUOC.index(a.tu):BUOC.index(a.den) + 1]:
        t0 = time.time()
        print(f"\n===== hf:{b}")
        try:
            {"chuan-bi": lambda: b_chuan_bi(da), "bundle": lambda: b_bundle(da, h), "anh-tinh": lambda: b_anh_tinh(da),
             "render": lambda: b_render(da, a.docker), "tiep": lambda: b_tiep(da)}[b]()
        except subprocess.CalledProcessError as e:
            sys.exit(f"\n✘ Dừng ở bước hf:{b} (mã {e.returncode}). Tổng {time.time() - dau:.0f} giây.")
        with (da / "thoi-gian.csv").open("a", encoding="utf-8") as g:
            g.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')},hf-{b},{time.time() - t0:.0f}\n")
        print(f"(hf:{b}: {time.time() - t0:.0f} giây)")
    if a.den == "anh-tinh":
        print(f"\nTổng {time.time() - dau:.0f} giây. Xem soat-tinh-hf-*.jpg, ổn thì chạy tiếp: python dung_hf.py \"{da}\" --tu render")


if __name__ == "__main__":
    main()
