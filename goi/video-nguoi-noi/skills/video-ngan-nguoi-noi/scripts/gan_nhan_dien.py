"""Gắn nhận diện kênh vào video đã nghiệm thu: watermark suốt video, intro (khi video đủ dài), outro.
  python gan_nhan_dien.py <thư mục dự án>
Đọc render/ra.mp4, ghi render/thanh-pham.mp4. Đây là file bàn giao.
Cấu hình ở "nhanDien" của hồ sơ kênh (đường dẫn tính từ thư mục hồ sơ):
  watermark       ảnh PNG 600×224 kín khung, phủ đúng nhãn tên kênh ở góc dưới phải (nhãn đó che logo Flow, nghiem_thu kiểm trên ra.mp4)
  watermarkKhung  [x, y, rộng] trên khung 1080×1920, mặc định [756, 1668, 300]
  intro, outro    video dọc 1080×1920 có tiếng
  introKhiDaiHon  chỉ gắn intro khi video dài hơn số giây này, mặc định 60 (video ngắn cần vào thẳng móc câu)
Hồ sơ không có "nhanDien" thì chép nguyên ra.mp4 sang thanh-pham.mp4.
Tiếng intro, outro được chỉnh về gần độ to của video (LUFS) để không giật tai."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from chung import duong_dan, ho_so

KHUNG_MAC_DINH = [756, 1668, 300]


def do_dai(f):
    return float(json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(f)],
                                           capture_output=True, text=True).stdout)["format"]["duration"])


def co_tieng(f):
    return "audio" in subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(f)],
                                     capture_output=True, text=True).stdout


def lufs(f):
    s = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(f), "-af", "ebur128=framelog=quiet", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", s)
    return float(m[-1]) if m else None


def gan(du_an, h=None):
    da = Path(du_an).resolve()
    h = h or ho_so(da)
    vao, ra = da / "render" / "ra.mp4", da / "render" / "thanh-pham.mp4"
    if not vao.exists():
        sys.exit(f"✘ Chưa có {vao}, chạy dựng trước.")
    nd = h.get("nhanDien") or {}
    if not nd:
        shutil.copy2(vao, ra)
        print("Hồ sơ không có nhanDien: thanh-pham.mp4 là bản chép của ra.mp4")
        return ra
    tep = {k: duong_dan(h, nd[k]) for k in ("watermark", "intro", "outro") if nd.get(k)}
    # Video giới thiệu bản thân của học viên (24/11/2026): hồ sơ mẫu còn đường dẫn logo, intro, outro chưa có file thật.
    # Loại gioi-thieu thì bỏ qua file thiếu thay vì dừng; video kênh vẫn dừng để bắt hồ sơ sai.
    from kiem_chot import loai_du_an
    # Video "edit" từ file quay của học viên cũng vậy (thử máy sạch 24/11/2026 bị dừng ở đây vì thiếu watermark)
    gioi_thieu = bool({"gioi-thieu", "edit"} & set(loai_du_an(Path(vao).resolve().parent.parent).split()))
    for k, f in list(tep.items()):
        if not f.exists():
            if gioi_thieu:
                print(f"• bỏ qua nhanDien.{k}: chưa có file {f}")
                del tep[k]
                continue
            sys.exit(f"✘ nhanDien.{k} không thấy file: {f}")
    dai = do_dai(vao)
    co_intro = "intro" in tep and dai > float(nd.get("introKhiDaiHon", 60))
    phan = ([tep["intro"]] if co_intro else []) + [vao] + ([tep["outro"]] if "outro" in tep else [])
    goc = lufs(vao)

    lenh = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y"]
    for f in phan:
        lenh += ["-i", str(f)]
    if "watermark" in tep:
        lenh += ["-i", str(tep["watermark"])]
    loc, nhan = [], []
    for i, f in enumerate(phan):
        v = f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p,setsar=1"
        if f == vao and "watermark" in tep:
            x, y, w = nd.get("watermarkKhung", KHUNG_MAC_DINH)
            loc.append(f"[{len(phan)}:v]scale={w}:-1[wm]")
            loc.append(f"{v}[n{i}];[n{i}][wm]overlay={x}:{y}:format=auto[v{i}]")
        else:
            loc.append(f"{v}[v{i}]")
        if co_tieng(f):
            chinh = ""
            if f != vao and goc is not None:
                lf = lufs(f)
                if lf is not None:
                    chinh = f",volume={goc - 1 - lf:.2f}dB"  # thấp hơn video 1 LU
            loc.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo{chinh}[a{i}]")
        else:
            loc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{do_dai(f):.3f}[a{i}]")
        nhan.append(f"[v{i}][a{i}]")
    loc.append("".join(nhan) + f"concat=n={len(phan)}:v=1:a=1[v][a];[a]alimiter=limit=0.95:level=0[ao]")
    lenh += ["-filter_complex", ";".join(loc), "-map", "[v]", "-map", "[ao]", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
             "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(ra)]
    subprocess.run(lenh, check=True)

    # Kiểm: đủ độ dài, có tiếng, đúng khung
    can = sum(do_dai(f) for f in phan)
    thuc = do_dai(ra)
    kt = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(ra)],
                        capture_output=True, text=True).stdout.strip()
    loi = []
    if abs(thuc - can) > 0.25:
        loi.append(f"độ dài {thuc:.2f} giây, cần {can:.2f}")
    if not co_tieng(ra):
        loi.append("mất tiếng")
    if kt != "1080,1920":
        loi.append(f"khung {kt}")
    if loi:
        sys.exit("✘ Gắn nhận diện lỗi: " + "; ".join(loi))
    print(f"✔ thanh-pham.mp4 {thuc:.1f} giây: {'intro + ' if co_intro else ''}video{' có watermark' if 'watermark' in tep else ''}"
          f"{' + outro' if 'outro' in tep else ''}" + ("" if co_intro or "intro" not in tep else f" (bỏ intro vì video {dai:.0f} giây ≤ {nd.get('introKhiDaiHon', 60)})"))
    return ra


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gan(sys.argv[1])
