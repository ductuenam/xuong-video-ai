"""Chuyển cảnh "lùi máy": cảnh sau bắt đầu ở đúng khung của cảnh trước rồi máy lùi dần ra khung đầy đủ.

Vì sao: cắt thẳng từ cảnh nói nửa người sang cảnh toàn thân là hình nhảy, người xem thấy "chưa mượt".
Nếu cảnh toàn thân mở đầu bằng đúng vùng khung của cảnh nửa người
(ảnh nửa người được cắt ra từ ảnh toàn thân nên biết chính xác vùng đó) rồi mở dần ra, mắt người xem
thấy như người quay lùi lại, không phải cú cắt.

Dùng: python lui_may.py vao.mp4 ra.mp4 --khung 0.15,0,0.70,0.70 [--dai 0.9] [--tu 0]
--khung x,y,rộng,cao: vùng bắt đầu, tính theo tỉ lệ khung cảnh sau (ví dụ ảnh nửa người cắt 70% chiều cao,
căn giữa từ đỉnh ảnh toàn thân: 0.15,0,0.70,0.70). Máy lùi theo đường cong êm (ease-out) trong --dai giây.
--tu: cắt bỏ phần đầu cảnh sau trước khi làm hiệu ứng. Tiếng giữ nguyên.
"""
import argparse
import json
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vao")
    ap.add_argument("ra")
    ap.add_argument("--khung", required=True)
    ap.add_argument("--dai", type=float, default=0.9)
    ap.add_argument("--tu", type=float, default=0.0)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    kx, ky, kw, kh = [float(v) for v in a.khung.split(",")]
    s = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                   "stream=width,height", "-of", "json", a.vao],
                                  capture_output=True, text=True).stdout)["streams"][0]
    W, H = s["width"], s["height"]
    d = a.dai
    # p: 0 → 1 trong d giây, ease-out; khung = khung đầu * (1-p) + toàn khung * p
    p = f"if(lt(t\\,{d})\\,1-pow(1-t/{d}\\,3)\\,1)"
    # Bộ lọc crop của ffmpeg chỉ tính rộng/cao một lần, nên phóng cả khung theo từng khung hình
    # (scale eval=frame) rồi cắt cố định W×H, chỉ dời x, y theo thời gian.
    z = f"(1/{kw}*(1-{p})+{p})"
    vf = (f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame:flags=lanczos,"
          f"crop={W}:{H}:x='{kx}*{W}*{z}*(1-{p})':y='{ky}*{H}*{z}*(1-{p})',setsar=1")
    lenh = ["ffmpeg", "-v", "error", "-y"]
    if a.tu > 0:
        lenh += ["-ss", f"{a.tu:.3f}"]
    lenh += ["-i", a.vao, "-vf", vf, "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "copy", a.ra]
    subprocess.run(lenh, check=True)
    print(f"Xong {a.ra}: lùi máy từ khung {a.khung} ra toàn khung trong {d} giây")


if __name__ == "__main__":
    main()
