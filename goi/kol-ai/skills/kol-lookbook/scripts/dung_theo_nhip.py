"""Dựng video thay đồ không lời: nối các đoạn clip, cắt cảnh đúng phách nhạc, lót nhạc.

Vì sao: video mẫu thay đồ (20/11/2026) không có lời, chỉ có nhạc sôi động khoảng 142 nhịp/phút,
và cú cắt duy nhất rơi đúng phách. Cắt lệch phách thì mắt và tai thấy "vấp".

Dùng: python dung_theo_nhip.py ke-hoach.json
ke-hoach.json:
{
  "nhac": "<thu_muc_nhac>/bai-co-quyen.mp3",
  "nhac_tu": 0.0,                 # bắt đầu nhạc từ giây này
  "ra": "td01.mp4",
  "doan": [                       # hình nối liền; "den" của mọi đoạn trừ đoạn cuối được dời tới phách gần nhất
    {"clip": "m1-mac.mp4", "tu": 0.0, "den": 9.6, "toc": 1.4},  # toc: tua nhanh (AI hay chậm hơn người thật)
    {"clip": "m2-lui.mp4", "tu": 0.0, "den": 4.0},
    {"clip": "m3-dang.mp4", "tu": 0.5, "den": 6.0}
  ],
  "khop_nhip": true,              # false: giữ nguyên số giây đã ghi
  # "noi_lien": true trong một đoạn: đoạn sau nối khung liền với nó (vd cảnh kéo khóa tạo từ khung cuối cảnh mặc áo), không dời về phách
  "lech_toi_da": 0.25,            # chỉ dời điểm cắt tối đa chừng này giây
  "mo_dau": 0.0, "tat_dan": 0.8   # giây tắt dần nhạc ở cuối
}
Xuất 1080x1920, 24 khung/giây như clip Muse (xuất 30 thì cứ 5 khung lặp 1, hình khựng đều, người soát bắt lỗi ở TD01 v2), nhạc cân về -14 LUFS. In mốc từng điểm cắt và phách gần nhất.
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np


def chay(lenh):
    r = subprocess.run(lenh, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)  # không lệnh nào treo vô hạn
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    return r.stdout


def do_dai(f):
    return float(chay(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).strip())


def luoi_phach(nhac, tu, dai, tam):
    """Ước lượng lưới phách (giây, tính từ đầu video) bằng tự tương quan đường onset."""
    wav = Path(tam) / "_nhac.wav"
    chay(["ffmpeg", "-v", "error", "-y", "-ss", str(tu), "-t", str(dai + 2), "-i", nhac, "-af", "lowpass=f=150", "-ac", "1", "-ar", "16000", str(wav)])  # phách lấy theo tiếng trống trầm; lấy cả dải thì dễ bắt nhầm phách lẻ (lệch nửa nhịp, video TD01)
    w = wave.open(str(wav))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float)
    w.close()
    hop = 160  # 10 ms
    e = np.array([np.sqrt((x[i:i + 512] ** 2).mean() + 1e-9) for i in range(0, len(x) - 512, hop)])
    o = np.maximum(0, np.diff(np.log1p(e)))
    o -= o.mean()
    ac = np.correlate(o, o, "full")[len(o) - 1:]
    lags = range(int(100 * 60 / 180), int(100 * 60 / 70) + 1)  # 70–180 nhịp/phút
    lag = max(lags, key=lambda l: ac[l])
    # pha: điểm bắt đầu cho tổng onset trên lưới lớn nhất
    pha = max(range(lag), key=lambda p: o[p::lag].sum())
    bpm = 6000 / lag
    # Phách = các cú trống trầm THẬT (đỉnh onset, cách nhau ít nhất 0,6 chu kỳ), không dùng lưới đều:
    # nhạc thật trôi nhịp, lưới đều 143 nhịp/phút lệch tới nửa phách sau 6 giây (video TD01, 20/11/2026).
    nguong = o.mean() + 1.5 * o.std()
    r = max(1, int(lag * 0.3))
    phach = [i / 100 for i in range(len(o)) if o[i] > nguong and o[i] == o[max(0, i - r):i + r + 1].max()]
    # cú trống yếu bị lọt ngưỡng: khoảng trống gấp 2–3 chu kỳ thì chia đều để điền phách thiếu
    T = lag / 100
    day = []
    for a, b in zip(phach, phach[1:]):
        day.append(a)
        n = round((b - a) / T)
        if n >= 2 and abs((b - a) / n - T) < 0.15 * T:
            day += [round(a + k * (b - a) / n, 3) for k in range(1, n)]
    phach = day + phach[-1:]
    if len(phach) < 4:
        phach = [(pha + k * lag) / 100 for k in range(int(len(o) / lag) + 2)]
    wav.unlink(missing_ok=True)
    return bpm, phach


def main():
    kh_path = Path(sys.argv[1])
    kh = json.loads(kh_path.read_text(encoding="utf-8"))
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    goc = kh_path.parent
    doan = kh["doan"]
    tong = sum((d["den"] - d["tu"]) / d.get("toc", 1.0) for d in doan)
    bpm, phach = luoi_phach(kh["nhac"], kh.get("nhac_tu", 0.0), tong, goc)
    print(f"(Tham khảo) máy dò nhạc khoảng {bpm:.0f} nhịp/phút, phách {60 / bpm:.3f} giây — nếu kế hoạch có \"phach\" và khop_nhip false thì dựng theo \"phach\" của kế hoạch, dòng này chỉ để đối chiếu")

    if kh.get("khop_nhip", True):
        lech = kh.get("lech_toi_da", 0.25)
        moc = 0.0
        for i, d in enumerate(doan[:-1]):
            toc = d.get("toc", 1.0)
            if d.get("noi_lien"):
                # đoạn sau bắt đầu đúng khung cuối đoạn này (clip nối khung): không dời, không phải chỗ cắt
                moc += (d["den"] - d["tu"]) / toc
                print(f"  Nối liền {i + 1}: giây {moc:.2f} (không cắt)")
                continue
            cat = moc + (d["den"] - d["tu"]) / toc
            gan = min(phach, key=lambda p: abs(p - cat))
            if abs(gan - cat) <= lech:
                d["den"] = round(d["den"] + (gan - cat) * toc, 3)
            moc += (d["den"] - d["tu"]) / toc
            print(f"  Cắt {i + 1}: giây {moc:.2f} (phách gần nhất {gan:.2f})")

    # Điểm cắt tính bằng SỐ KHUNG NGUYÊN trên thành phẩm (cộng dồn rồi mới làm tròn).
    # Vì sao: cắt từng đoạn bằng -t rồi làm tròn riêng từng đoạn thì sai số dồn lại, video mẫu 1 lệch phách tới +0,26 giây
    # và ảnh góc đổi sớm 3 khung so với cú cắt (người chấm dựng bắt lỗi CHẶN 21/11/2026).
    fps = kh.get("fps", 24)
    moc_ds, t0, f0 = [], 0.0, 0
    for d in doan:
        t0 += (d["den"] - d["tu"]) / d.get("toc", 1.0)
        f1 = round(t0 * fps)
        d["_khung"] = f1 - f0
        moc_ds.append({"clip": d["clip"], "bo": d.get("bo"), "tu": round(f0 / fps, 4), "den": round(f1 / fps, 4),
                       "khung_tu": f0, "khung_den": f1})
        f0 = f1
    (goc / (kh["ra"] + ".moc.json")).write_text(json.dumps(moc_ds, ensure_ascii=False, indent=1), encoding="utf-8")
    tam = goc / "_doan_tam"
    tam.mkdir(exist_ok=True)
    ds = []
    for i, d in enumerate(doan):
        ra = tam / f"d{i}.mp4"
        chay(["ffmpeg", "-v", "error", "-y", "-ss", f"{d['tu']:.3f}", "-t", f"{d['den'] - d['tu'] + 0.5:.3f}",
              "-i", str(goc / d["clip"]), "-an",
              "-vf", f"setpts=(PTS-STARTPTS)/{d.get('toc', 1.0)},scale=1080:1920:flags=lanczos,setsar=1,fps={fps},tpad=stop_mode=clone:stop=12",
              "-frames:v", str(d["_khung"]), "-r", str(fps),
              "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", str(ra)])
        ds.append(ra)
    ds_txt = tam / "ds.txt"
    ds_txt.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in ds), encoding="utf-8")
    hinh = tam / "hinh.mp4"
    chay(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(ds_txt), "-c", "copy", str(hinh)])
    dai = do_dai(str(hinh))
    nhac_dai = do_dai(kh["nhac"]) - kh.get("nhac_tu", 0.0)
    if dai > nhac_dai:
        print(f"CẢNH BÁO: hình {dai:.2f} giây dài hơn nhạc {nhac_dai:.2f} giây, nhạc sẽ lặp và hụt ở chỗ nối. Cắt hình ngắn lại.")
    td = kh.get("tat_dan", 0.8)
    ra = goc / kh["ra"]
    # nhạc ngắn hơn hình thì lặp lại (bài mẫu chỉ dài 15,2 giây)
    chay(["ffmpeg", "-v", "error", "-y", "-i", str(hinh), "-stream_loop", "-1", "-ss", str(kh.get("nhac_tu", 0.0)), "-i", kh["nhac"],
          "-filter_complex", f"[1:a]atrim=0:{dai:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-1.5:LRA=11,"
                             f"afade=t=out:st={max(0, dai - td):.3f}:d={td}[a]",
          "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-b:a", "192k", "-shortest", str(ra)])
    for p in ds + [ds_txt, hinh]:
        p.unlink(missing_ok=True)
    tam.rmdir()
    print(f"Xong {ra} dài {do_dai(str(ra)):.2f} giây")


if __name__ == "__main__":
    main()
