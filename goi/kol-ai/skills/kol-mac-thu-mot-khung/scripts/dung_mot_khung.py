"""Dựng video KOL một khung: nối các đoạn cảnh nói, tiếng chạy liền, hình nối mềm (hòa hình ngắn), 1080x1920.

Dùng: python dung_mot_khung.py <ke-hoach.json> <ra.mp4> [--ban-thu]
ke-hoach.json:
{
  "doan": [["s1-noi.mp4", 0.00, 9.40], ["s2-noi.mp4", 0.05, 9.55]],   // [tệp, giây vào, giây ra] theo tiếng
  "mem": 0.24,          // độ dài hòa hình ở mỗi chỗ nối (giây); 0 = cắt thẳng như video mẫu (người dùng chê cắt nhảy)
  "lang_cuoi": 0.35,    // giữ thêm bao nhiêu giây sau chữ cuối của đoạn cuối
  "chen": [["s3-lung.mp4", 1.2, 6.4, 3.0]]   // tùy chọn: hình chèn đè (không tiếng) từ giây 1,2–6,4 của tệp, đặt ở giây 3,0 thành phẩm
}
Cách nối: hình đoạn trước kéo dài thêm `mem` giây sau điểm ra (lúc KOL đã im, cười nhẹ, về tư thế khung đầu),
hòa vào hình đoạn sau; tiếng đoạn sau bắt đầu đúng điểm vào, nên khẩu hình đoạn sau khớp tiếng.
Vì cả hai cảnh bắt đầu từ cùng ảnh goc-khung và cảnh 1 kết bằng đúng tư thế đó, chỗ nối gần như không thấy.
Ra: thành phẩm 1080x1920, 24 khung/giây, −14 LUFS, đỉnh ≤ −1,5 dBTP. In mốc chỗ nối trên thành phẩm.
Thư mục ke-hoach.json là thư mục video (tệp đoạn tính từ đó). Cổng khóa mặt (bước clip) phải qua mới dựng.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from khoa_mat import cong  # noqa: E402


def dai(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    return float(r.stdout.strip())


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    fk = Path(sys.argv[1]).resolve()
    d = fk.parent
    ra = Path(sys.argv[2]).resolve()
    kh = json.loads(fk.read_text(encoding="utf-8"))
    if "--ban-thu" in sys.argv:
        # Bản thử cho người dùng xem quyết khi cổng mặt chưa qua: tên tệp phải có "ban-thu", không lưu kho, không giao.
        if "ban-thu" not in ra.name:
            sys.exit("--ban-thu: tên thành phẩm phải chứa 'ban-thu'.")
        print("⚠ BẢN THỬ: bỏ qua cổng khóa mặt, chỉ để người dùng xem quyết.")
    else:
        cong(d, "clip")
    doan = kh["doan"]
    mem = float(kh.get("mem", 0.24))
    duoi = float(kh.get("lang_cuoi", 0.35))
    vao, loc, moc = [], [], []
    n = len(doan)
    dl = [dai(d / t) for t, _, _ in doan]
    # Hòa hình ở mỗi chỗ nối lấy từ đuôi lặng của đoạn trước (sau) và đầu lặng của đoạn sau (truoc).
    sau, truoc = [0.0] * n, [0.0] * n
    for i in range(n - 1):
        sau[i] = max(0.0, min(mem, dl[i] - doan[i][2] - 0.02))
        truoc[i + 1] = max(0.0, min(mem - sau[i], doan[i + 1][1]))
    dt = []
    for i, (tep, a, b) in enumerate(doan):
        cuoi = i == n - 1
        b_tieng = min(b + (duoi if cuoi else 0), dl[i])
        thieu = (b + duoi - b_tieng) if cuoi else 0.0  # nói sát mép clip: giữ khung cuối, thêm lặng
        hc = float(kh.get("hinh_cuoi_den", 0)) if cuoi else 0.0  # đoạn cuối: hình dừng ở giây này rồi giữ khung (né nháy mắt cuối clip)
        b_hinh = min(hc, b_tieng) if hc else b_tieng
        giu = (b_tieng - b_hinh) + (thieu if thieu > 0.02 else 0)
        vao += ["-i", str(d / tep)]
        loc.append(f"[{i}:v]trim={a - truoc[i]:.3f}:{b_hinh + sau[i]:.3f},setpts=PTS-STARTPTS,fps=24,"
                   f"scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,format=yuv420p"
                   + (f",tpad=stop_mode=clone:stop_duration={giu:.3f}" if giu > 0.02 else "") + f"[v{i}]")
        loc.append(f"[{i}:a]atrim={a:.3f}:{b_tieng:.3f},asetpts=PTS-STARTPTS,aresample=48000,"
                   f"afade=t=in:d=0.012,afade=t=out:st={max(0, b_tieng - a - 0.012):.3f}:d=0.012"
                   + (f",apad=pad_dur={thieu:.3f}" if thieu > 0.02 else "") + f"[a{i}]")
        dt.append(b_tieng - a + (thieu if thieu > 0.02 else 0))
    cur, tong = "v0", 0.0
    for i in range(1, n):
        tong += dt[i - 1]
        m = sau[i - 1] + truoc[i]
        if m > 0.01:
            loc.append(f"[{cur}][v{i}]xfade=transition=fade:duration={m:.3f}:offset={tong - truoc[i]:.3f}[x{i}]")
        else:
            loc.append(f"[{cur}][v{i}]concat=n=2:v=1:a=0[x{i}]")
        cur = f"x{i}"
        moc.append(round(tong, 2))
    # Chèn hình (không tiếng) đè lên thành phẩm, vd cảnh quay lưng che đoạn mắt nhắm: "chen": [[tệp, từ, đến, giây_vào], ...]
    for k, (tep, a, b, vao_tp) in enumerate(kh.get("chen", [])):
        j = n + k
        vao += ["-i", str(d / tep)]
        loc.append(f"[{j}:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS+{vao_tp:.3f}/TB,fps=24,"
                   f"scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,format=yuv420p[c{k}]")
        loc.append(f"[{cur}][c{k}]overlay=enable='between(t,{vao_tp:.3f},{vao_tp + b - a - 0.001:.3f})':eof_action=pass[o{k}]")
        cur = f"o{k}"
        moc.append(f"chèn {tep} {vao_tp:.2f}-{vao_tp + b - a:.2f}")
    loc.append("".join(f"[a{i}]" for i in range(len(doan))) + f"concat=n={len(doan)}:v=0:a=1,"
               "loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    cmd = ["ffmpeg", "-v", "error", "-y", *vao, "-filter_complex", ";".join(loc), "-map", f"[{cur}]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", str(ra)]
    r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=600)
    if r.returncode:
        sys.exit("ffmpeg lỗi:\n" + r.stderr[-2000:])
    print(f"Đã dựng {ra} ({dai(ra):.2f} giây). Chỗ nối (giây trên thành phẩm): {moc}")


if __name__ == "__main__":
    main()
