"""Dựng video review nghỉ dưỡng từ clip Muse theo ke-hoach.json.

  dung_video.py <thư mục video> [--ke-hoach ke-hoach.json] [--chi-nen] [--chi-chu] [--nhap]

Bước 1 (nền): cắt từng đoạn clip (kèm tiếng của chính đoạn đó), phóng/đẩy khung, nối; thêm 0,9 giây mở đầu
"Ảnh chủ khu gửi" → nen.mp4. Whisper nghe nen.mp4, khớp với loi.json → phu-de.json (sửa tay được).
Bước 2 (chữ): phụ đề 2–4 chữ có từ khóa vàng, thẻ nhấn ý, ô ảnh góc, nhãn AI, nhãn KOL, thẻ kết,
nhạc nền dưới giọng, chuẩn −14 LUFS → thành phẩm (1080×1920, 24 hình/giây).
--nhap: bản nháp nhanh (crf cao) để soi.

ke-hoach.json (xem references/ke-hoach-mau.json):
{"mo_dau": {"anh": "boi-canh/bc1.png", "nhan": "Ảnh chủ khu gửi", "dai": 0.9},
 "doan": [{"tep": "c1.mp4", "tu": 0.2, "den": 1.6, "zoom": 1.0, "tam": [0.5, 0.42], "o_anh": "boi-canh/bc1.png"}, ...],
 "the": [{"chu": "CHƯA TỪNG ĐẾN ĐÂY!", "mau": "do", "khi_noi": "chưa đến bao giờ", "dai": 1.4}],
 "nhan_o_anh": "Ảnh chủ khu gửi", "goc_o_anh": "trai",
 "nhan_ai": "Video do AI tạo ra", "nhan_kol": "Người mẫu ảo do AI tạo ra",
 "the_ket": {"dong1": "...", "dong2": "...", "dai": 2.2},
 "nhac": {"tep": "...", "db": -21}, "ra": "thanh-pham.mp4"}
"""
import argparse, difflib, json, re, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from chung import doc_json, ghi_json, chay, do_dai, font, TAM

W, H, FPS = 1080, 1920, 24
VANG, DO, XANH = (255, 225, 74), (224, 33, 63), (22, 150, 127)
MAU = {"vang": (VANG, (20, 20, 20)), "do": (DO, (255, 255, 255)), "xanh": (XANH, (255, 255, 255))}
DUNG = set("và với là thì mà này kia đó đây cho của các những một em anh chị nó rồi cũng đã đang sẽ được ở trong ngoài lên xuống ra vào nhá nhé đấy thôi luôn cơ chứ nữa ơi".split())

# ---------- bước 1: nền ----------
def doc_anh(p):
    return Image.open(p).convert("RGB")

def phu_kin(img, w, h):
    s = max(w / img.width, h / img.height)
    i = img.resize((int(img.width * s + .5), int(img.height * s + .5)), Image.LANCZOS)
    x, y = (i.width - w) // 2, (i.height - h) // 2
    return i.crop((x, y, x + w, y + h))

def khung_mo_dau(d, md, tam):
    img = doc_anh(d / md["anh"])
    nen = phu_kin(img, W, H).filter(ImageFilter.GaussianBlur(38))
    nen = Image.blend(nen, Image.new("RGB", (W, H), (0, 0, 0)), 0.15)
    s = W / img.width
    nho = img.resize((W, int(img.height * s)), Image.LANCZOS)
    if nho.height > H * 0.62:
        nho = phu_kin(img, W, int(H * 0.62))
    nen.paste(nho, (0, (H - nho.height) // 2))
    p = tam / "mo-dau.png"; nen.save(p); return p

def lam_nen(d, kh, tam, nhap):
    doan_tep = []
    crf = "20" if nhap else "12"
    if kh.get("mo_dau"):
        md = kh["mo_dau"]; p = khung_mo_dau(d, md, tam); o = tam / "d00.mp4"
        chay(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", str(md.get("dai", 0.9)), "-i", str(p),
              "-f", "lavfi", "-t", str(md.get("dai", 0.9)), "-i", "anullsrc=r=48000:cl=stereo",
              "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-crf", crf, "-preset", "fast",
              "-c:a", "pcm_s16le", "-shortest", str(o.with_suffix(".mov"))])
        doan_tep.append(o.with_suffix(".mov"))
    # cân độ to: mỗi clip nguồn đưa về cùng mức −16 LUFS trước khi cắt (Muse mỗi clip to nhỏ khác nhau tới 6 dB)
    loi_to = {}
    for t in {dn["tep"] for dn in kh["doan"]}:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(d / t), "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
        loi_to[t] = max(-6.0, min(12.0, -16.0 - float(m[-1]))) if m else 0.0
    print("  cân độ to (dB):", {k: round(v, 1) for k, v in sorted(loi_to.items())})
    for i, dn in enumerate(kh["doan"], 1):
        src = d / dn["tep"]; z = float(dn.get("zoom", 1.0)); cx, cy = dn.get("tam", [0.5, 0.45])
        z2 = float(dn.get("zoom_cuoi", z)); dai = round((dn["den"] - dn["tu"]) * FPS) / FPS   # tròn số khung: tiếng hình không lệch dồn
        if abs(z2 - z) < 1e-3:
            vf = (f"crop=iw/{z}:ih/{z}:max(0\\,min(iw-iw/{z}\\,iw*{cx}-iw/{z}/2)):max(0\\,min(ih-ih/{z}\\,ih*{cy}-ih/{z}/2)),")
        else:   # đẩy máy chậm trong đoạn
            zz = f"({z}+({z2}-{z})*t/{dai})"
            vf = (f"scale={W}:{H}:flags=lanczos,scale=w='trunc({W}*{zz}/2)*2':h='trunc({H}*{zz}/2)*2':eval=frame:flags=lanczos,"
                  f"crop={W}:{H}:x='max(0,min(iw-{W},iw*{cx}-{W}/2))':y='max(0,min(ih-{H},ih*{cy}-{H}/2))',")
        if abs(z2 - z) < 1e-3:
            vf += f"scale={W}:{H}:flags=lanczos,"
        vf += f"unsharp=5:5:0.6,fps={FPS},format=yuv420p"
        giu = float(dn.get("giu", 0))   # giữ khung cuối của CHÍNH cú này (cùng độ phóng) — không dùng ảnh khác, tránh nhảy hình
        if giu > 0:
            vf += f",tpad=stop_mode=clone:stop_duration={giu:.3f}"
            fa = fa.replace(f"apad=whole_dur={dai:.3f},atrim=0:{dai:.3f}", f"apad=whole_dur={dai + giu:.3f},atrim=0:{dai + giu:.3f}")
            dai = round((dai + giu) * FPS) / FPS
        fa = f"volume={loi_to[dn['tep']]:.2f}dB,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={max(0, dai - 0.03):.3f}:d=0.03,apad=whole_dur={dai:.3f},atrim=0:{dai:.3f}"
        o = tam / f"d{i:02d}.mp4"
        if dn.get("anh_phu"):   # phủ hình bằng ảnh (ảnh chủ khu gửi / bối cảnh), tiếng vẫn của clip: đẩy chậm kiểu Ken Burns
            nfr = round(dai * FPS)
            chay(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(d / dn["anh_phu"]), "-ss", f"{dn['tu']:.3f}", "-t", f"{dai:.3f}", "-i", str(src),
                  "-filter_complex", f"[0:v]scale={W*2}:{H*2},zoompan=z='1.02+0.09*on/{nfr}':x='iw/2-(iw/zoom/2)+12*sin(on/9)':y='ih/2-(ih/zoom/2)':d={nfr}:s={W}x{H}:fps={FPS},format=yuv420p[v];[1:a]{fa}[a]",
                  "-map", "[v]", "-map", "[a]", "-ac", "2", "-c:v", "libx264", "-crf", crf, "-preset", "fast",
                  "-c:a", "pcm_s16le", "-frames:v", str(nfr), "-t", f"{dai:.4f}", str(o.with_suffix(".mov"))])
            doan_tep.append(o.with_suffix(".mov")); continue
        chay(["ffmpeg", "-y", "-v", "error", "-ss", f"{dn['tu']:.3f}", "-t", f"{dai - giu:.3f}", "-i", str(src),
              "-vf", vf, "-af", fa, "-ac", "2", "-c:v", "libx264", "-crf", crf, "-preset", "fast",
              "-c:a", "pcm_s16le", "-frames:v", str(round(dai * FPS)), "-t", f"{dai:.4f}", str(o.with_suffix(".mov"))])
        o = o.with_suffix(".mov")   # tiếng PCM: không lệch khung đệm AAC khi nối nhiều đoạn
        doan_tep.append(o)
    ds = tam / "ds.txt"
    ds.write_text("".join(f"file '{p.as_posix()}'\n" for p in doan_tep), encoding="utf-8")
    nen = d / "nen.mp4"
    td = float(kh.get("toc_do", 1.0))   # >1 nói nhanh hơn (giữ cao độ). Mẫu 4,6 chữ/giây; Muse thường 3,6–4,1
    loc = ["-vf", f"setpts=PTS/{td}", "-af", f"atempo={td}"] if abs(td - 1) > 1e-3 else []
    chay(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(ds), *loc, "-c:v", "libx264", "-crf", crf,
          "-preset", "fast", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", str(nen)])
    print("→ nen.mp4", f"{do_dai(nen):.2f} giây")
    return nen

# ---------- phụ đề: khớp Whisper với lời đã viết ----------
def chuan(t):
    return re.sub(r"[^\wÀ-ỹ]", "", t.lower())

def lam_phu_de(d, nen):
    from faster_whisper import WhisperModel
    lj = doc_json(d / "loi.json")
    tu_khoa = {chuan(k) for c in lj["canh"] for k in c.get("tu_khoa", [])}
    hien = [t for c in lj["canh"] for t in c["loi"].split()]
    goc = [chuan(t) for t in hien]
    try: m = WhisperModel("large-v3", device="cuda", compute_type="float16")
    except Exception: m = WhisperModel("medium", device="cpu", compute_type="int8")
    seg, _ = m.transcribe(str(nen), language="vi", word_timestamps=True, beam_size=5)
    w = [(chuan(x.word), x.start, x.end) for s in seg for x in s.words if chuan(x.word)]
    sm = difflib.SequenceMatcher(a=goc, b=[t for t, _, _ in w], autojunk=False)
    moc = [None] * len(goc)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1): moc[i1 + k] = (w[j1 + k][1], w[j1 + k][2])
        elif op == "replace" and j2 > j1:
            a0, a1 = w[j1][1], w[j2 - 1][2]; n = i2 - i1
            for k in range(n): moc[i1 + k] = (a0 + (a1 - a0) * k / n, a0 + (a1 - a0) * (k + 1) / n)
    # nội suy chữ không nghe được
    for i in range(len(moc)):
        if moc[i] is None:
            tr = next((moc[j][1] for j in range(i - 1, -1, -1) if moc[j]), 0.0)
            sa = next((moc[j][0] for j in range(i + 1, len(moc)) if moc[j]), tr + 0.3)
            moc[i] = (tr, min(sa, tr + 0.3))
    # tách theo dấu câu thành vế, rồi chia đều mỗi vế thành cụm 2–4 chữ
    ve, cur = [], []
    for i, t in enumerate(hien):
        cur.append(i)
        if re.search(r"[.,?!…:;]$", t) or i == len(hien) - 1:
            ve.append(cur); cur = []
    cum = []
    for v in ve:
        n = len(v); k = max(1, -(-n // 4))
        if n >= 5 and n % 4 == 1: k = max(k, 2)
        co = [n // k + (1 if j < n % k else 0) for j in range(k)]
        p = 0
        for c in co:
            cum.append(v[p:p + c]); p += c
    GHEP = {"tất bật", "nổi tiếng", "du lịch", "điện thoại", "hoàng hôn", "phòng ngủ", "người mẫu", "mẫu ảo", "giới thiệu",
            "kịch bản", "bình luận", "nghỉ dưỡng", "vịnh biển", "đồi thông", "hình dung", "đón khách", "dọn phòng", "khu nghỉ",
            "đèn mây", "ghế mây", "thời gian", "video mới", "đều tay", "chữ a"}
    for k in range(len(cum) - 1):   # ranh giới cắt ngang từ ghép: dời chữ đầu cụm sau lên cụm trước (hoặc ngược lại)
        a, b = cum[k], cum[k + 1]
        if a and b and f"{chuan(hien[a[-1]])} {chuan(hien[b[0]])}" in GHEP:
            if len(a) <= 3 or len(b) == 1: a.append(b.pop(0))
            else: b.insert(0, a.pop())
    cum = [c for c in cum if c]
    gop = []
    for c in cum:   # vế 1 chữ gộp vào cụm trước nếu cụm trước còn chỗ
        if len(c) == 1 and gop and len(gop[-1]) < 5: gop[-1] += c
        else: gop.append(c)
    cum = gop
    pd = []
    for k, c in enumerate(cum):
        bd = moc[c[0]][0] - 0.05
        kt = moc[cum[k + 1][0]][0] - 0.05 if k + 1 < len(cum) else moc[c[-1]][1] + 0.5
        kt = min(kt, moc[c[-1]][1] + 0.6)
        chu = [hien[i] for i in c]
        vt = [j for j, i in enumerate(c) if goc[i] in tu_khoa]
        if not vt:
            ung = [(len(goc[i]), j) for j, i in enumerate(c) if goc[i] not in DUNG]
            vt = [max(ung)[1]] if ung else []
        vang = vt[:1]
        if vang:
            j = vang[0]
            if j + 1 < len(c) and f"{goc[c[j]]} {goc[c[j + 1]]}" in GHEP: vang.append(j + 1)
            elif j > 0 and f"{goc[c[j - 1]]} {goc[c[j]]}" in GHEP: vang.insert(0, j - 1)
        pd.append({"tu": round(bd, 2), "den": round(kt, 2), "chu": chu, "vang": vang})
    ghi_json(d / "phu-de.json", pd)
    print(f"→ phu-de.json {len(pd)} cụm (khớp lời {sm.ratio():.0%}); sửa tay được rồi chạy --chi-chu")

# ---------- bước 2: lớp chữ ----------
def f(ten, co): return ImageFont.truetype(font(ten), co)

def anh_phu_de(chu, vang):
    ft = f("BeVietnamPro-ExtraBold.ttf", 66)
    cach = 16; rong = [ft.getbbox(t)[2] for t in chu]
    tong = sum(rong) + cach * (len(chu) - 1)
    im = Image.new("RGBA", (tong + 40, 120), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    bong = Image.new("RGBA", im.size, (0, 0, 0, 0)); db = ImageDraw.Draw(bong)
    x = 20
    for j, t in enumerate(chu):
        db.text((x + 3, 24), t, font=ft, fill=(0, 0, 0, 150))
        x += rong[j] + cach
    im = Image.alpha_composite(im, bong.filter(ImageFilter.GaussianBlur(4))); dr = ImageDraw.Draw(im)
    x = 20
    for j, t in enumerate(chu):
        dr.text((x, 18), t, font=ft, fill=VANG if j in vang else (255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0))
        x += rong[j] + cach
    return im

def o_bo(chu, nen, mau_chu, co, nghieng=0.0, hoa=True, dem=(26, 14)):
    ft = f("BeVietnamPro-Black.ttf" if hoa else "BeVietnamPro-ExtraBold.ttf", co)
    t = chu.upper() if hoa else chu
    b = ft.getbbox(t); w, h = b[2] - b[0] + dem[0] * 2, b[3] - b[1] + dem[1] * 2
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([10, 14, w + 10, h + 14], radius=h // 3, fill=(0, 0, 0, 90))
    dr.rounded_rectangle([10, 10, w + 10, h + 10], radius=h // 3, fill=nen + (255,))
    dr.text((10 + dem[0] - b[0], 10 + dem[1] - b[1]), t, font=ft, fill=mau_chu)
    return im.rotate(nghieng, resample=Image.BICUBIC, expand=True) if nghieng else im

def anh_o_goc(p, nhan):
    img = doc_anh(p); rong = 260; img = phu_kin(img, rong, int(rong * 0.78))
    vien, day = 9, 40
    im = Image.new("RGBA", (rong + vien * 2, img.height + vien + day), (255, 255, 255, 255))
    im.paste(img, (vien, vien)); dr = ImageDraw.Draw(im)
    dr.text((vien + 2, img.height + vien + 8), nhan, font=f("BeVietnamPro-Bold.ttf", 19), fill=(30, 30, 30))
    b = Image.new("RGBA", (im.width + 16, im.height + 16), (0, 0, 0, 0)); ImageDraw.Draw(b).rectangle([8, 12, im.width + 8, im.height + 12], fill=(0, 0, 0, 110))
    b = b.filter(ImageFilter.GaussianBlur(5)); b.alpha_composite(im, (8, 8)); return b

def the_ket(dong1, dong2):
    f1, f2 = f("BeVietnamPro-Black.ttf", 40), f("BeVietnamPro-Bold.ttf", 32)
    w = max(f1.getbbox(dong1)[2], f2.getbbox(dong2)[2]) + 70; h = 150
    im = Image.new("RGBA", (w + 20, h + 50), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.rounded_rectangle([10, 14, w + 10, h + 14], radius=26, fill=(0, 0, 0, 90))
    dr.rounded_rectangle([10, 10, w + 10, h + 10], radius=26, fill=XANH + (255,))
    dr.text(((w + 20 - f1.getbbox(dong1)[2]) // 2, 34), dong1, font=f1, fill=(255, 255, 255))
    dr.text(((w + 20 - f2.getbbox(dong2)[2]) // 2, 92), dong2, font=f2, fill=VANG)
    cx = (w + 20) // 2; dr.polygon([(cx - 20, h + 18), (cx + 20, h + 18), (cx, h + 44)], fill=VANG)
    return im

def tim_giay(pd, cum_chu):
    muc = [chuan(t) for t in cum_chu.split()]
    phang = [(chuan(t), c["tu"]) for c in pd for t in c["chu"]]
    for i in range(len(phang) - len(muc) + 1):
        if [x for x, _ in phang[i:i + len(muc)]] == muc: return phang[i][1]
    return None

def lop_chu(d, kh, nen):
    pd = doc_json(d / "phu-de.json"); dai = do_dai(nen); lop = []   # (tu, den, anh RGBA, x, y)
    md = kh.get("mo_dau", {}); t0 = md.get("dai", 0) if md else 0
    if md:
        im = o_bo(md.get("nhan", "Ảnh chủ khu gửi"), VANG, (20, 20, 20), 40, hoa=False)
        lop.append((0, t0, im, (W - im.width) // 2, 150))
    moc_k0, tt, truoc = [], t0, None
    for dn in kh["doan"]:
        if dn["tep"] != truoc or dn.get("anh_phu"): moc_k0.append(tt)
        truoc = dn["tep"] if not dn.get("anh_phu") else None
        tt += round((dn["den"] - dn["tu"]) * FPS) / FPS / float(kh.get("toc_do", 1.0))
    for c in pd:   # phụ đề không tràn sang cảnh/ảnh sau
        c = dict(c); c["den"] = min([c["den"]] + [m for m in moc_k0 if c["tu"] + 0.2 < m])
        im = anh_phu_de(c["chu"], c["vang"]); im.info['khong_mo'] = True; lop.append((c["tu"], c["den"], im, (W - im.width) // 2, int(H * 0.775) - im.height // 2))
    y_the = int(H * 0.705) - 60
    if kh.get("nhan_kol"):
        im = o_bo(kh["nhan_kol"], XANH, (255, 255, 255), 36, hoa=False)
        lop.append((t0, t0 + 1.7, im, (W - im.width) // 2, y_the))
    moc_khoi, tt, truoc = [], t0, None   # mốc bắt đầu từng khối cảnh (theo tốc độ)
    for dn in kh["doan"]:
        if dn["tep"] != truoc: moc_khoi.append(tt)
        truoc = dn["tep"]; tt += round((dn["den"] - dn["tu"]) * FPS) / FPS / float(kh.get("toc_do", 1.0))
    ds_the = kh.get("the")
    if ds_the is None and (d / "loi.json").exists():   # mặc định lấy thẻ từ loi.json
        ds_the = [c[k] for c in doc_json(d / "loi.json")["canh"] for k in ("the", "the2") if c.get(k)]
    for th in ds_the or []:
        g = th.get("tu") if "tu" in th else tim_giay(pd, th["khi_noi"])
        if g is None: print("  ! không tìm thấy chỗ nói:", th.get("khi_noi")); continue
        nen_m, chu_m = MAU[th.get("mau", "vang")]
        im = o_bo(th["chu"], nen_m, chu_m, 54, nghieng=th.get("nghieng", 3), dem=(30, 16))
        het = min([g + th.get("dai", 1.5)] + [m - 0.04 for m in moc_khoi if m > g + 0.3])
        lop.append((g, het, im, (W - im.width) // 2, y_the - 10))
    # ô ảnh góc ở đầu mỗi khối có "o_anh"
    t = t0
    for dn in kh["doan"]:
        if dn.get("anh_phu") and dn.get("nhan_phu", "boi-canh" in dn["anh_phu"]):   # phủ ảnh bối cảnh: nhãn vàng như mở đầu
            im = o_bo(kh.get("nhan_o_anh", "Ảnh chủ khu gửi"), VANG, (20, 20, 20), 40, hoa=False)
            lop.append((t, t + (dn["den"] - dn["tu"]) / float(kh.get("toc_do", 1.0)), im, (W - im.width) // 2, 150))
        if dn.get("o_anh"):
            im = anh_o_goc(d / dn["o_anh"], kh.get("nhan_o_anh", "Ảnh chủ khu gửi"))
            x = 22 if dn.get("goc", kh.get("goc_o_anh", "trai")) == "trai" else W - im.width - 22
            lop.append((t, t + dn.get("dai_o_anh", 1.9), im, x, 112))
        t += round((dn["den"] - dn["tu"]) * FPS) / FPS / float(kh.get("toc_do", 1.0))
    if kh.get("nhan_ai"):
        im = o_bo(kh["nhan_ai"], (12, 12, 12), (255, 255, 255), 26, hoa=False, dem=(16, 9))
        lop.append((0, dai + 1, im, 18, 26))
    if kh.get("the_ket"):
        tk = kh["the_ket"]; im = the_ket(tk["dong1"], tk["dong2"])
        lop.append((dai - tk.get("dai", 2.2), dai + 1, im, (W - im.width) // 2, int(H * 0.735) - im.height))
    return lop

def tron_tieng(d, kh, nen, tam):
    """Giọng + nhạc chạy suốt (nhỏ dần 0,9 giây cuối), rồi bù độ to cố định về −14 LUFS (không nén động, nhạc không bị chìm)."""
    tho = tam / "tieng-tho.wav"; ra = tam / "tieng.wav"; nh = kh.get("nhac"); dai = do_dai(nen)
    if nh:
        fc = (f"[1:a]volume={nh.get('db', -8)}dB,afade=t=in:d=0.4,afade=t=out:st={dai - 0.9:.2f}:d=0.9,atrim=0:{dai:.3f}[n];"
              f"[0:a]highpass=f=70[g];[g][n]amix=inputs=2:duration=first:normalize=0[a]")
        chay(["ffmpeg", "-y", "-v", "error", "-i", str(nen), "-stream_loop", "-1", "-i", nh["tep"], "-filter_complex", fc,
              "-map", "[a]", "-ar", "48000", "-t", f"{dai:.3f}", str(tho)])
    else:
        chay(["ffmpeg", "-y", "-v", "error", "-i", str(nen), "-vn", "-ar", "48000", str(tho)])
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tho), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); bu = (-14.0 - float(m[-1])) if m else 0.0
    chay(["ffmpeg", "-y", "-v", "error", "-i", str(tho), "-af", f"volume={bu:.2f}dB,alimiter=limit=0.89:level=false", "-ar", "48000", str(ra)])
    return ra

def ghep(d, kh, nen, tam, nhap):
    lop = lop_chu(d, kh, nen); tieng = tron_tieng(d, kh, nen, tam)
    lop = [(a, b, np.asarray(im, dtype=np.float32), x, y, im.info.get('khong_mo', False)) for a, b, im, x, y in lop]
    ra = d / kh.get("ra", "thanh-pham.mp4")
    if nhap: ra = ra.with_name(ra.stem + "-nhap.mp4")
    vao = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(nen), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    ra_p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-i", str(tieng), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "24" if nhap else "17",
                             "-preset", "veryfast" if nhap else "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                             "-movflags", "+faststart", "-shortest", str(ra)], stdin=subprocess.PIPE)
    n, kich = 0, W * H * 3
    while True:
        b = vao.stdout.read(kich)
        if len(b) < kich: break
        t = n / FPS; fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
        for a, bb, im, x, y, km in lop:
            if a <= t < bb:
                vao_dan = 1.0 if (km or bb - a >= 30) else min(1.0, (t - a) / 0.12)
                h, w = im.shape[:2]; x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
                if x1 <= x0 or y1 <= y0: continue
                s = im[y0 - y:y1 - y, x0 - x:x1 - x]; al = s[..., 3:4] / 255.0 * vao_dan
                fr[y0:y1, x0:x1] = fr[y0:y1, x0:x1] * (1 - al) + s[..., :3] * al
        ra_p.stdin.write(fr.astype(np.uint8).tobytes()); n += 1
    ra_p.stdin.close(); ra_p.wait(); vao.wait()
    print("→", ra, f"{do_dai(ra):.2f} giây, {n} khung")

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("thu_muc"); a.add_argument("--ke-hoach", default="ke-hoach.json")
    a.add_argument("--chi-nen", action="store_true"); a.add_argument("--chi-chu", action="store_true"); a.add_argument("--nhap", action="store_true")
    x = a.parse_args(); d = Path(x.thu_muc).resolve(); kh = doc_json(d / x.ke_hoach)
    TAM.mkdir(parents=True, exist_ok=True); tam = Path(tempfile.mkdtemp(prefix="dung-", dir=TAM))
    if not x.chi_chu:
        nen = lam_nen(d, kh, tam, x.nhap); lam_phu_de(d, nen)
    nen = d / "nen.mp4"
    if not x.chi_nen:
        ghep(d, kh, nen, tam, x.nhap)
