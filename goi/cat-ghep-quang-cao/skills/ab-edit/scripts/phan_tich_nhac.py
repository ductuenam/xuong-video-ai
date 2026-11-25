""""Nghe" nhạc nền trong kho bằng máy: có lời hay không, nhịp, cảm xúc, nhạc cụ, đường năng lượng → thẻ nhạc cho từng bài.
Chỉ đọc kho. Kết quả lưu .cache/nhac_phan_tich.json (bài đã phân tích thì bỏ qua), kho_tai_nguyen.py đọc file này để ghi vào Obsidian.
  python phan_tich_nhac.py              # phân tích mọi bài nhạc nền chưa có thẻ (dùng danh sách từ kho_tai_nguyen cache)
  python phan_tich_nhac.py <file...>    # phân tích file lẻ, in thẻ
Chạy bằng Python .avs (cần torch, transformers, librosa, faster-whisper). Mô hình: MIT/ast-finetuned-audioset (AudioSet 527 nhãn).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).parent))
from chung import tim_ffmpeg  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
CFG = json.loads((SKILL / "config.json").read_text(encoding="utf-8"))
KHO = Path(CFG["kho_tai_nguyen"])
CACHE_KHO = SKILL / ".cache" / "kho_tai_nguyen.json"
OUT = SKILL / ".cache" / "nhac_phan_tich.json"
AST = "MIT/ast-finetuned-audioset-10-10-0.4593"

LA_SFX = ("sfx", "sound effect", "kho-am-thanh")
LA_NHAC = ("nhạc", "music", "xu hướng")
GIONG = ["Singing", "Vocal music", "Rapping", "Choir", "Male singing", "Female singing", "Child singing", "Speech", "Humming", "A capella"]
CAM_XUC = {"Happy music": "vui", "Sad music": "buồn", "Tender music": "êm dịu", "Exciting music": "sôi động",
           "Angry music": "gắt", "Scary music": "rùng rợn", "Funny music": "hài hước"}
VI = {"Piano": "piano", "Electric piano": "piano điện", "Guitar": "guitar", "Acoustic guitar": "guitar mộc", "Electric guitar": "guitar điện",
      "Bass guitar": "bass", "Drum kit": "trống", "Drum": "trống", "Drum machine": "trống điện tử", "Synthesizer": "synth", "Keyboard (musical)": "phím",
      "Orchestra": "dàn nhạc", "Violin, fiddle": "violin", "Bowed string instrument": "dây kéo", "String section": "dàn dây", "Cello": "cello",
      "Brass instrument": "kèn đồng", "Trumpet": "trumpet", "Saxophone": "saxophone", "Flute": "sáo", "Harp": "hạc cầm", "Ukulele": "ukulele",
      "Bell": "chuông", "Glockenspiel": "chuông gõ", "Marimba, xylophone": "marimba", "Whistling": "huýt sáo", "Clapping": "vỗ tay",
      "Pop music": "pop", "Rock music": "rock", "Electronic music": "điện tử", "Hip hop music": "hip hop", "Jazz": "jazz", "Funk": "funk",
      "Classical music": "cổ điển", "Ambient music": "ambient", "Soundtrack music": "nhạc phim", "Film score": "nhạc phim", "Background music": "nhạc nền",
      "Theme music": "nhạc chủ đề", "Jingle (music)": "jingle", "Electronic dance music": "EDM", "House music": "house", "Techno": "techno",
      "Dubstep": "dubstep", "Reggae": "reggae", "Country": "country", "Blues": "blues", "Soul music": "soul", "Rhythm and blues": "R&B",
      "Folk music": "dân gian", "Christmas music": "giáng sinh", "Lullaby": "ru", "New-age music": "new age", "Disco": "disco",
      "Music of Asia": "nhạc Á", "Chinese music": "nhạc Hoa", "Music of Latin America": "latin", "Video game music": "nhạc game",
      "Dance music": "nhạc nhảy", "Orchestral music": "giao hưởng", "Middle Eastern music": "Trung Đông", "Carnatic music": "nhạc Ấn",
      "Music of Bollywood": "Bollywood", "Wedding music": "nhạc cưới", "Children's music": "thiếu nhi", "Lo-fi": "lo-fi"}
BO_NHAN = {"Music", "Musical instrument", "Plucked string instrument", "Percussion", "Speech", "Silence", "Inside, small room"}
BIA = ("subscribe", "ghiền mì gõ", "đăng ký kênh", "cảm ơn các bạn đã theo dõi", "hẹn gặp lại", "like", "share", "la la")
VACH = "▁▂▃▄▅▆▇█"


def doc(file, sr):
    raw = subprocess.run([tim_ffmpeg(), "-nostdin", "-v", "error", "-i", str(file), "-vn", "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


_M = {}


def ast():
    if "ast" not in _M:
        import torch
        from transformers import ASTFeatureExtractor, ASTForAudioClassification
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        _M["ast"] = (ASTFeatureExtractor.from_pretrained(AST), ASTForAudioClassification.from_pretrained(AST).to(dev).eval(), dev)
    return _M["ast"]


def whisper():
    if "wh" not in _M:
        from whisper_vi import model
        _M["wh"] = model()
    return _M["wh"]


def nhan_ast(y16):
    """8 đoạn 10s rải đều → xác suất trung bình + cực đại của 527 nhãn."""
    import torch
    fe, m, dev = ast()
    n = len(y16) / 16000
    L = 10.0
    starts = np.linspace(0, max(0.0, n - L), num=8 if n > 20 else 1)
    wins = [y16[int(s * 16000): int((s + L) * 16000)] for s in starts]
    x = fe(wins, sampling_rate=16000, return_tensors="pt")
    with torch.no_grad():
        p = torch.sigmoid(m(**{k: v.to(dev) for k, v in x.items()}).logits).cpu().numpy()
    id2 = m.config.id2label
    return {id2[i]: (float(p[:, i].mean()), float(p[:, i].max())) for i in range(p.shape[1])}


def nghe_loi(y16):
    """Whisper 3 đoạn 25s → số từ có nghĩa (bỏ câu 'bịa' quen thuộc)."""
    n = len(y16) / 16000
    tu, mau = 0, []
    for frac in (0.2, 0.5, 0.8):
        s = max(0, frac * n - 12.5)
        seg = y16[int(s * 16000): int((s + 25) * 16000)]
        out, _ = whisper().transcribe(seg, vad_filter=True, beam_size=1, condition_on_previous_text=False)
        for sg in out:
            t = sg.text.strip()
            if not t or any(b in t.lower() for b in BIA) or sg.no_speech_prob > 0.6 or sg.avg_logprob < -1.0:
                continue
            tu += len(t.split())
            mau.append(t)
    return tu, " / ".join(mau)[:120]


KK_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
NOT = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def do_librosa(y, sr):
    import librosa
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)
    best = max([(np.corrcoef(np.roll(KK_MAJ, k), chroma)[0, 1], NOT[k], "trưởng") for k in range(12)]
               + [(np.corrcoef(np.roll(KK_MIN, k), chroma)[0, 1], NOT[k], "thứ") for k in range(12)])
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=sr // 2)[0]          # 2 giá trị / giây
    db = 20 * np.log10(np.maximum(rms, 1e-5))
    cen = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())
    ons = librosa.onset.onset_detect(y=y, sr=sr, units="time")
    n = len(y) / sr
    # đường năng lượng 12 ô + đỉnh (trung bình trượt 6s)
    k = max(1, len(db) // 12)
    o = [db[i * k:(i + 1) * k].mean() for i in range(12) if len(db[i * k:(i + 1) * k])]
    lo, hi = min(o), max(o)
    vach = "".join(VACH[int((v - lo) / max(hi - lo, 1e-6) * 7)] for v in o)
    sm = np.convolve(db, np.ones(12) / 12, mode="same")
    dinh = float(np.argmax(sm) / 2)
    vao = next((i / 2 for i, v in enumerate(db) if v > db.max() - 12), 0.0)  # đến khi nhạc "vào" đủ
    return {"bpm": round(tempo), "giong": f"{best[1]} {best[2]}", "mode": best[2], "db": round(float(np.median(db)), 1),
            "dong": round(float(np.percentile(db, 90) - np.percentile(db, 10)), 1), "sang": round(cen), "nhip_go": round(len(ons) / n, 2),
            "vach": vach, "dinh": round(dinh, 1), "vao": round(vao, 1)}


def the_nhac(file):
    y16 = doc(file, 16000)
    y22 = doc(file, 22050)
    lb = do_librosa(y22, 22050)
    nh = nhan_ast(y16)
    giong = max(nh[g][1] for g in GIONG if g in nh)
    hat = max(nh[g][1] for g in GIONG if g in nh and g != "Speech")
    tu, mau = nghe_loi(y16)
    # có lời: AST thấy giọng hát, hoặc Whisper nghe ra nhiều chữ có nghĩa.
    # Ngưỡng thử trên cặp Champions có lời/không lời (hát 0,12 / 0,01) và Taught Her How To Leave (Whisper 52 chữ)
    if hat > 0.09 or tu >= 10:
        loi = "co"
    elif hat > 0.04 or tu >= 4 or nh.get("Speech", (0, 0))[1] > 0.5:
        loi = "nghi"
    else:
        loi = "khong"
    cx = sorted(((v[0], CAM_XUC[k]) for k, v in nh.items() if k in CAM_XUC), reverse=True)
    cam = [c for p, c in cx if p > 0.08][:2] or [cx[0][1]]
    top = sorted(((v[0], k) for k, v in nh.items() if k not in BO_NHAN and k not in CAM_XUC and k not in GIONG and k in VI), reverse=True)
    nc = list(dict.fromkeys(VI[k] for p, k in top if p > 0.04))[:4]
    nhip = "chậm" if lb["bpm"] < 85 else "vừa" if lb["bpm"] < 118 else "nhanh"
    nang = "êm" if lb["db"] < -24 else "vừa" if lb["db"] < -16 else "mạnh"
    return {"loi": loi, "hat": round(hat, 2), "giong_max": round(giong, 2), "whisper_tu": tu, "whisper_mau": mau,
            "cam_xuc": cam, "nhac_cu": nc, "nhip": nhip, "nang": nang, **lb,
            "goi_y": goi_y(cam, nc, nhip, nang, lb["mode"])}


def goi_y(cam, nc, nhip, nang, mode):
    g = []
    if any(c in cam for c in ("êm dịu", "buồn")) or (nhip == "chậm" and nang == "êm"):
        g.append("kể chuyện, tâm sự, bài học")
    if any(c in cam for c in ("vui", "sôi động")) and nhip != "chậm":
        g.append("giới thiệu, tích cực, CTA")
    if "nhạc phim" in nc or "dàn nhạc" in nc or "giao hưởng" in nc:
        g.append("hook kịch tính, cao trào")
    if "hài hước" in cam:
        g.append("hài, vui nhộn")
    if any(c in cam for c in ("rùng rợn", "gắt")):
        g.append("hồi hộp, cảnh báo")
    if not g:
        g.append("nền chung, doanh nghiệp" if mode == "trưởng" else "suy ngẫm, trầm")
    return g


def ds_nhac():
    c = json.loads(CACHE_KHO.read_text(encoding="utf-8"))["files"]
    out = []
    for rel, v in c.items():
        thu_muc = str(Path(rel).parent).lower()
        g = v["info"].get("giay") or 0
        la_video = v["info"].get("w")
        if la_video or any(k in thu_muc for k in LA_SFX):
            continue
        if any(k in thu_muc for k in LA_NHAC) or g > 30:
            out.append((rel, v["khoa"]))
    return sorted(out)


def main():
    if len(sys.argv) > 1:
        for f in sys.argv[1:]:
            print(f, json.dumps(the_nhac(Path(f)), ensure_ascii=False, indent=1))
        return
    kq = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    ds = [(r, k) for r, k in ds_nhac() if kq.get(r, {}).get("khoa") != k]
    print(f"{len(ds)} bài cần phân tích (đã có {len(kq)})", flush=True)
    for i, (rel, khoa) in enumerate(ds, 1):
        try:
            t = the_nhac(KHO / rel)
        except Exception as e:  # file hỏng không làm dừng cả lượt
            print(f"  ✘ {rel}: {e}", flush=True)
            continue
        kq[rel] = {"khoa": khoa, **t}
        dau = {"khong": "🎻", "nghi": "❓", "co": "🎤"}[t["loi"]]
        print(f"  {i:3d}/{len(ds)} {dau} {Path(rel).stem[:40]:40s} {t['bpm']:3d}bpm {t['nhip']:5s} {','.join(t['cam_xuc']):18s} {','.join(t['nhac_cu'])}", flush=True)
        if i % 10 == 0:
            OUT.write_text(json.dumps(kq, ensure_ascii=False), encoding="utf-8")
    OUT.write_text(json.dumps(kq, ensure_ascii=False), encoding="utf-8")
    print(f"✔ {len(kq)} bài → {OUT}")


if __name__ == "__main__":
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    main()
