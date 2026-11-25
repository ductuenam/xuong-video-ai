"""Lập ke-hoach.json tự động từ clip nói: mỗi cảnh cắt 2–3 cú ở chỗ ngắt hơi, cú sau đẩy gần hơn (như mẫu).

  lap_ke_hoach.py <thư mục video> [--nhan-o-anh "Bối cảnh minh họa"] [--nhac <mp3>] [--chi c1,c2,...]
Đọc video.json (thứ tự cảnh, clip, bối cảnh) và loi.json (lời, thẻ kết). Whisper nghe từng clip để lấy mốc chữ.
Có thể ghi đè từng cảnh bằng "cat" trong video.json: [[tu, den, zoom], ...].
Ra ke-hoach.json (sửa tay được) rồi chạy dung_video.py.
"""
import argparse, json, re
from pathlib import Path
from chung import doc_json, ghi_json, do_dai

ZOOM = [1.0, 1.12, 1.2]   # trong một khối cú sau luôn gần hơn (đẩy vào như mẫu), không bao giờ lùi ra

def moc_chu(p):
    from faster_whisper import WhisperModel
    global _m
    try: _m
    except NameError:
        try: _m = WhisperModel("large-v3", device="cuda", compute_type="float16")
        except Exception: _m = WhisperModel("medium", device="cpu", compute_type="int8")
    seg, _ = _m.transcribe(str(p), language="vi", word_timestamps=True, beam_size=5)
    return [(w.word.strip(), w.start, w.end) for s in seg for w in s.words]

def chia(words, dai_clip, lang_cat=0.45, ngan_nhat=1.3, la_cuoi=False):
    """Cắt clip thành các cú theo chỗ ngắt hơi: mỗi khoảng lặng > lang_cat giây là một điểm cắt và bị bỏ
    (giữ 0,06 giây trước chữ, 0,12 giây sau chữ) — nhịp nhanh, liền như video mẫu. Cú ngắn hơn ngan_nhat gộp với cú sau."""
    if not words: return [[0.0, min(dai_clip, 3.0)]]
    nhom = [[words[0]]]
    for a, b in zip(words, words[1:]):
        if b[1] - a[2] > lang_cat: nhom.append([b])
        else: nhom[-1].append(b)
    cus = [[max(0.0, g[0][1] - 0.15), min(dai_clip, g[-1][2] + (0.45 if g[-1][0].strip().endswith('?') else 0.22))] for g in nhom]
    gop = []
    for c in cus:
        if gop and c[0] - gop[-1][1] < 0.3 and (gop[-1][1] - gop[-1][0] < ngan_nhat or c[1] - c[0] < 0.8):
            gop[-1][1] = c[1]
        else:
            gop.append(list(c))
    gop[-1][1] = min(dai_clip, gop[-1][1] + 0.16)   # cuối cảnh thở thêm (mẫu ngắt 0,3–0,6 giây giữa cảnh)
    if la_cuoi: gop[-1][1] = min(dai_clip, words[-1][2] + 1.5)   # cảnh kết: giữ hình 1,5 giây sau chữ cuối cho thẻ kết
    # cú dài hơn 3,4 giây: chia tiếp thành cú liền thời gian (không mất tiếng), đổi cỡ khung = cú "đẩy vào" như mẫu
    ra = []
    for t, dn in gop:
        n = int((dn - t) // 3.2) + 1 if dn - t > 4.4 else 1
        if n == 1: ra.append([t, dn]); continue
        bien = [w[2] for w in words if t + 1.2 < w[2] < dn - 1.2]   # cắt ngay sau một chữ
        moc = [t]
        for k in range(1, n):
            dich = t + (dn - t) * k / n
            if bien: moc.append(min(bien, key=lambda b: abs(b - dich)))
        moc = sorted(set(moc)) + [dn]
        ra += [[moc[i], moc[i + 1]] for i in range(len(moc) - 1)]
    # tối đa 2 cú một khối (mẫu ~3 giây/cú): gộp cặp cú sát nhau nhất (khoảng hở nhỏ nhất)
    while len(ra) > 2:
        k = min(range(len(ra) - 1), key=lambda i: ra[i + 1][0] - ra[i][1])
        if ra[k + 1][0] - ra[k][1] > 0.3: break   # không gộp qua khoảng lặng đã cắt (sẽ hiện lại lặng dài)
        ra[k] = [ra[k][0], ra[k + 1][1]]; del ra[k + 1]
    return [[round(float(t), 2), round(float(dn), 2)] for t, dn in ra]

def lang_that(p, nguong=-35, toi_thieu=0.5):
    """Khoảng lặng thật trong tiếng clip (Whisper hay gộp lặng vào mốc chữ)."""
    import subprocess
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", f"silencedetect=n={nguong}dB:d={toi_thieu}", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    bd = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    kt = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(bd, kt))

def bo_lang(cus, lang):
    """Cắt bỏ khoảng lặng thật nằm giữa một cú, giữ 0,15 giây mỗi bên."""
    for s0, e0 in lang:
        moi = []
        for c in cus:
            t, dn = c[0], c[1]
            if t + 0.3 < s0 and e0 < dn - 0.3:
                moi += [[t, round(s0 + 0.15, 2), *c[2:]], [round(e0 - 0.15, 2), dn, *c[2:]]]
            else:
                moi.append(c)
        cus = moi
    return cus

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("thu_muc"); a.add_argument("--nhan-o-anh", default="Ảnh chủ khu gửi")
    a.add_argument("--nhac", default="tai-nguyen/nhac/beat-vlog.mp3"); a.add_argument("--ra", default="thanh-pham.mp4")
    x = a.parse_args(); d = Path(x.thu_muc); vj = doc_json(d / "video.json"); lj = doc_json(d / "loi.json")
    doan = []
    for c in vj["canh"]:
        clip = d / c["clip"]
        if not clip.exists(): print("! thiếu", c["clip"]); continue
        if c.get("cat"):
            cus = c["cat"]
        else:
            cus = chia(moc_chu(clip), do_dai(clip), la_cuoi=(c is vj['canh'][-1]))
            cus = bo_lang(cus, lang_that(clip))
            cus = [[t, dn, ZOOM[min(i, 2)]] for i, (t, dn) in enumerate(cus)]
        for i, cu in enumerate(cus):
            z = cu[2] if len(cu) > 2 else ZOOM[min(i, 2)]
            dn = {"tep": c["clip"], "tu": cu[0], "den": cu[1], "zoom": z, "tam": c.get("tam", [0.5, 0.33])}
            if len(cu) > 3 and cu[3]: dn["anh_phu"] = cu[3]   # phủ hình bằng ảnh, giữ tiếng (che đoạn mặt lỗi hoặc minh họa lời)
            if i == 0 and not dn.get("anh_phu"): dn["o_anh"] = c["boi_canh"]
            if i == len(cus) - 1 and len(cus) == 1: dn["zoom_cuoi"] = 1.12   # cú duy nhất thì đẩy chậm
            if i == len(cus) - 1 and c.get("giu_cuoi"): dn["giu"] = c["giu_cuoi"]   # cảnh kết: dừng hình trên khung cuối cho thẻ kết
            doan.append(dn)
        if c.get("den_toi_da"): cus = [[t, min(dn, c["den_toi_da"]), *r] for t, dn, *r in cus if t < c["den_toi_da"]]
        print(c["id"], [(round(u[0], 2), round(u[1], 2)) for u in cus])
    kh = {"mo_dau": {"anh": vj["canh"][0]["boi_canh"], "nhan": x.nhan_o_anh, "dai": 0.9}, "doan": doan,
          "nhan_o_anh": x.nhan_o_anh, "goc_o_anh": "trai", "nhan_ai": "Video do AI tạo ra", "nhan_kol": "Người mẫu ảo do AI tạo ra",
          "the_ket": {**lj.get("the_ket", {}), "dai": 2.2}, "nhac": {"tep": x.nhac, "db": -10}, "ra": x.ra, "toc_do": 1.0}
    ghi_json(d / "ke-hoach.json", kh)
    dai = 0.9 + sum(z["den"] - z["tu"] for z in doan)
    if dai > 54: kh["toc_do"] = round(min(1.09, dai / 54), 3)   # nhanh tối đa 8% cho vừa 53 giây
    ghi_json(d / "ke-hoach.json", kh)
    print("→ ke-hoach.json", len(doan), "đoạn, khoảng", round(dai, 1), "giây, toc_do", kh["toc_do"], "→", round(0.9 + (dai - 0.9) / kh["toc_do"], 1), "giây")
