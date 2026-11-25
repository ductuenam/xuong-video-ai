"""Edit một file quay người nói thành video dọc có phụ đề, cảnh minh họa, nhạc nhẹ (câu lệnh "Edit video <file> cho tôi").

  Bước 1 (nghe, lọc, chia câu):
    python edit.py "<thư mục kênh>" "<file quay>" [--dai 30] [--tieu-de "DÒNG 1|DÒNG 2"] [--ten <tên dự án>]
  Bước 2 (dựng theo câu đã chọn và cảnh minh họa trong chon.json):
    python edit.py "<dự án>" --chon [--het]

Bước 1 tự làm, không hỏi duyệt:
  - Tạo <kênh>/du-an/<số>-edit-<tên>/, loai.txt = edit, nhac.txt. File có viền đen thì làm bản dọc nền mờ.
  - Nghe lời bằng Whisper, chia đảo tiếng (khe > 0,35 giây), BỎ: ậm ừ, đảo quá ngắn, lần nói hỏng (đảo sau mở đầu giống
    đảo trước, bỏ qua đảo ậm ừ ở giữa), chữ lặp liền nhau ("nhân viên nhân viên"), nói lại giữa đảo, lặp ở chỗ nối,
    câu Whisper bịa. Chỉ bỏ, không đảo, không thêm lời. Ghi bo-cat.txt.
  - Chia thành CÂU đánh số (đảo dài quá 9 giây tách ở chỗ ngừng dài nhất), ghi cau.json (máy đọc) và cau.txt (người đọc),
    và một chon.json nháp: không có --dai thì giữ mọi câu; có --dai thì lấy câu đầu và các câu kế tiếp cho tới gần đủ giây.
  - DỪNG để Claude sửa chon.json: chọn câu (bản 30 giây: móc câu → ý chính → kết trọn ý) và đặt cảnh minh họa.
Bước 2: từ chon.json lập doan.json, loi.txt, canh.json (mốc cảnh tự tính theo câu, không phải đếm dòng), chạy dung.py.

chon.json:
  {"tieuDe": "SỨC MẠNH|AI AGENT",
   "doan": [{"cau": 1},
            {"cau": 4, "chu": "agent là nhân viên có thể hỗ trợ chúng ta"},   # chỉ lấy khúc này trong câu 4 (khớp gần đúng)
            {"cau": 6, "minhHoa": {"loai": "flow-chu", "ten": "M01", "tren": "AGENT", "duoi": "NHÂN VIÊN AI"}},
            {"cau": 9, "minhHoa": {"loai": "danh-sach-buoc", "tren": "Agent làm gì", "buoc": [{"ten": "Kế toán"}, {"ten": "Nhân sự"}]}}]}
  - Câu đầu luôn là cảnh người nói có tiêu đề (nguoi-chu); thẻ tiêu đề hiện ở dòng có chữ của tiêu đề.
  - minhHoa nhận mọi loại cảnh trong references/mo-hinh-canh.md. Thiếu "moc" thì tự rải đều theo thời lượng câu.
    Cảnh dùng clip kho (flow-chu, ten-cong-cu) tự cắt ở ≤ 7,5 giây, phần còn lại của câu trở về người nói.
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ND = Path(__file__).resolve().parent
KHE = 0.35
AM_UM = {"ờ", "ừ", "ừm", "à", "ơ", "hừm", "ạ", "ư", "um", "uhm", "ừa", "ờm", "ầ", "ừa"}
NOI = {"và", "thì", "mà", "để", "của", "cho", "với", "nhưng", "là", "sẽ", "đã", "không", "các", "những", "một", "khi",
       "nếu", "vì", "nên", "trong", "tại", "từ", "đến", "về", "ở", "hay", "hoặc", "rằng", "được", "có"}
# Cảnh dùng clip kho dài 8 giây: phải ngắn hơn
CANH_CLIP = {"flow-chu", "ten-cong-cu"}
# chữ không thuộc tiếng Việt, Latin: Whisper lạc tiếng
CHU_LA = re.compile(r"[\u0370-\u03FF\u0400-\u04FF\u0590-\u06FF\u0E00-\u0E7F\u3040-\u30FF\u3400-\u9FFF\uAC00-\uD7AF]")
CLIP_TOI_DA = 7.5
# Trường danh sách quyết định số mốc của từng loại cảnh (thiếu "moc" thì tự rải đều)
SO_MOC = {"danh-sach-buoc": "buoc", "day-chuyen": "buoc", "khung-chat": "tin", "canh-bao": "dong", "bieu-do": "cot",
          "luoi-the": "sang", "nguoi-so": "the", "so-tay": None}
HAI_MOC = {"hai-phe", "truoc-sau", "hai-o-canh", "anh-goc"}
# Mặc định đã thử cho cảnh minh họa trên video người nói (24/11/2026)
MAC_DINH = {"flow-chu": {"nen": True, "y": 150, "viTriPhuDe": 1420}}


def khong_dau(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").replace("đ", "d")


def chu(w):
    return re.sub(r"[^\w]", "", w["word"].lower())


def ghi_json(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------------------------------------------------------- bước 1
def lam_du_an(a):
    kenh, f = Path(a.kenh).resolve(), Path(a.file).resolve()
    if (kenh / "INDEX.md").is_file() and (kenh / "01_CA_NHAN_VA_THUONG_HIEU").is_dir():
        # Thử máy học viên 24/11/2026: không bao giờ làm video bên trong Bộ Não AI; dùng Video-AI cạnh nó
        kenh = kenh.parent / "Video-AI"
        print(f"• thư mục đưa vào là bộ não: làm video ở {kenh} (ngoài bộ não)")
    if not (kenh / "ho-so-kenh.json").exists():
        r = subprocess.run([sys.executable, ND / "cai_dat.py", kenh])
        if r.returncode or not (kenh / "ho-so-kenh.json").exists():
            sys.exit(f"✘ {kenh} chưa có ho-so-kenh.json, chạy cai_dat.py \"{kenh}\" trước.")
    from nhap_kho import nhap
    nhap(kenh)  # có gói KHO-HOC-VIEN trong Downloads thì tự nhận nhạc, cảnh
    du_an = kenh / "du-an"
    du_an.mkdir(exist_ok=True)
    so = 1 + max([int(m.group(1)) for x in du_an.iterdir() if (m := re.match(r"(\d+)-", x.name))] or [0])
    ten = a.ten or re.sub(r"[^a-z0-9]+", "-", khong_dau(f.stem)).strip("-")[:30] or "video"
    if not a.ten and sum(c.isdigit() for c in ten) > len(ten) / 2:  # tên file Zalo toàn số: đặt theo ngày cho dễ đọc
        import datetime
        ten = "video-" + datetime.date.today().strftime("%d-%m")
    if a.dai:
        ten += f"-{a.dai}s"
    cu = sorted(du_an.glob(f"*-edit-{ten}"))
    da = cu[-1] if cu else du_an / f"{so:02d}-edit-{ten}"  # chạy lại cùng tên thì dùng lại dự án cũ
    da.mkdir(exist_ok=True)
    (da / "loai.txt").write_text("edit", encoding="utf-8")
    if not (da / "nhac.txt").exists():
        (da / "nhac.txt").write_text("beat-vlog", encoding="utf-8")
    print("dự án:", da)
    return kenh, f, da


def nguon_doc(da, f):
    """File quay có viền đen (màn hình ngang nằm trong khung dọc): cắt viền, đặt hình giữa, nền là chính hình làm mờ."""
    cd = subprocess.run(["ffmpeg", "-hide_banner", "-ss", "2", "-t", "8", "-i", str(f), "-vf", "cropdetect=24:2:0", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", cd)
    wh = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(f)],
                        capture_output=True, text=True).stdout.strip().split(",")
    if m and len(wh) == 2:
        cw, ch, cx, cy = map(int, m[-1])
        W, H = int(wh[0]), int(wh[1])
        if ch < 0.85 * H or cw < 0.85 * W:
            lam = da / "nguon-doc-x14.mp4"  # x14: dải giữa phóng 1,4 lần
            if not lam.exists():
                print(f"• file có viền đen (hình thật {cw}x{ch} trong {W}x{H}): làm bản dọc nền mờ")
                subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(f), "-filter_complex",
                                f"[0]crop={cw}:{ch}:{cx}:{cy},split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2[bg];"
                                f"[b]scale=1512:-2,crop=1080:ih[fg];[bg][fg]overlay=0:(H-h)/2,format=yuv420p",
                                "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-c:a", "aac", "-b:a", "192k", str(lam)], check=True)
            return lam
    return f


def khoang_lang(f):
    sd = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "silencedetect=noise=-32dB:d=0.25", "-vn", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return list(zip(map(float, re.findall(r"silence_start: ([\d.]+)", sd)), map(float, re.findall(r"silence_end: ([\d.]+)", sd))))


DEM = {"ờ", "à", "ừ", "ừm", "ơ", "ạ", "cái", "thì", "là", "mà", "ấy", "này", "kiểu"}


def bo_lap_lien(c):
    """Nói lại NGAY TRONG một đảo ("nhân viên nhân viên", "hi vọng rằng cái hi vọng rằng", "ở những cái phần này thì ... ở
    những cái phần này thì"): trả (j, i) để bỏ c[j:i] (lần đầu và mấy chữ chen giữa), giữ lần sau. Chữ chen chỉ được là từ
    đệm; cụm từ 5 chữ thì cho chen 3 chữ bất kỳ. Không bắt liệt kê thật ("kiểm tra email, kiểm tra chứng từ") và láy một chữ
    ("từ từ"). Gộp từ bo_lap_trong của phiên chính 24/11/2026."""
    for n in range(8, 1, -1):
        for g in range(0, (4 if n >= 5 else 2)):
            for i in range(0, len(c) - 2 * n - g + 1):
                chen = c[i + n:i + n + g]
                if c[i:i + n] == c[i + n + g:i + 2 * n + g] and all(c[i:i + n]) and (n >= 5 or all(x in DEM for x in chen)):
                    return i, i + n + g
    return None


def loc_dao(W, bo_cat):
    dao, hien = [], []
    for w in W:
        if hien and w["start"] - hien[-1]["end"] > KHE:
            dao.append(hien)
            hien = []
        hien.append(w)
    dao.append(hien)
    la_am_um = [not [chu(w) for w in d if chu(w)] or all(chu(w) in AM_UM for w in d if chu(w)) for d in dao]
    giu, bo = [], []
    for i, d in enumerate(dao):
        tu = [chu(w) for w in d if chu(w)]
        if la_am_um[i]:
            bo.append((d, "ậm ừ"))
            continue
        if d[-1]["end"] - d[0]["start"] < 0.3 and len(tu) <= 1:
            bo.append((d, "quá ngắn"))
            continue
        # nói lại: đảo sau (bỏ qua đảo ậm ừ xen giữa) mở đầu giống đảo này thì đảo này là lần hỏng.
        # Thử máy học viên 24/11/2026: "agent nó khác skill / ờ / agent nó khác skill" lọt vì chỉ xét đảo liền sau.
        sau = next((x for k, x in enumerate(dao[i + 1:i + 4], i + 1) if not la_am_um[k]), None)
        if sau:
            tu_sau = [chu(w) for w in sau if chu(w)]
            n = min(len(tu), len(tu_sau), 6)
            if n >= 2 and difflib.SequenceMatcher(None, tu[:n], tu_sau[:n]).ratio() >= 0.75 and len(tu) <= len(tu_sau) + 2:
                bo.append((d, "nói lại ở đảo sau"))
                continue
        giu.append(d)
    moi = []
    for d in giu:
        while (cat := bo_lap_lien([chu(w) for w in d])):
            j, i = cat
            bo.append((d[j:i], "nói hỏng, nói lại ngay"))
            print(f"• bỏ lần nói hỏng: {' '.join(w['word'].strip() for w in d[j:i])}")
            if j:
                moi.append(d[:j])
            d = d[i:]
        moi.append(d)
    giu = [d for d in moi if d]
    for k in range(len(giu) - 1):
        a_, b_ = [chu(w) for w in giu[k]], [chu(w) for w in giu[k + 1]]
        for n in range(min(8, len(a_) - 1, len(b_)), 0, -1):
            if a_[-n:] == b_[:n]:
                bo.append((giu[k][-n:], "lặp ở chỗ nối"))
                giu[k] = giu[k][:-n]
                print(f"• bỏ chữ lặp ở chỗ nối: {' '.join(b_[:n])}")
                break
    bo_cat.write_text("\n".join(f"[{d[0]['start']:.2f}-{d[-1]['end']:.2f}] ({ly}) " + " ".join(w['word'].strip() for w in d)
                                for d, ly in sorted(bo, key=lambda x: x[0][0]["start"]) if d)
                      or "(không bỏ đảo nào ngoài khoảng lặng)", encoding="utf-8")
    print(f"✔ {len(dao)} đảo tiếng, giữ {len(giu)}, bỏ {len(bo)} (xem bo-cat.txt)")
    return giu


def tach_cau(giu, toi_da=9.0):
    """Đảo dài quá toi_da giây thì tách ở khe giữa hai chữ dài nhất (cách hai đầu ≥ 3 chữ) để chọn câu cho mịn."""
    ra = []
    for d in giu:
        hang = [d]
        while hang:
            x = hang.pop(0)
            if x[-1]["end"] - x[0]["start"] <= toi_da or len(x) < 8:
                ra.append(x)
                continue
            # mỗi phần ≥ 3 giây; khe dài nhất, hòa (Whisper hay ghi khe 0) thì chỗ gần giữa nhất.
            # Thử 24/11/2026: lấy khe lớn nhất đầu tiên làm lời nói liền bị băm 3 chữ một câu (95 câu cho 117 giây).
            bd, kt = x[0]["start"], x[-1]["end"]
            cho = [i for i in range(3, len(x) - 2) if x[i]["start"] - bd >= 3 and kt - x[i - 1]["end"] >= 3] or list(range(3, len(x) - 2))
            # hòa khe thì ưu tiên tách TRƯỚC chữ nối (và, thì, mà...) trong khoảng giữa, tránh cắt đôi từ ghép "soạn hợp / đồng" (lần 4)
            giua = (bd + kt) / 2
            k = max(cho, key=lambda i: (round(x[i]["start"] - x[i - 1]["end"], 1),
                                        chu(x[i]) in NOI and abs(x[i]["start"] - giua) < (kt - bd) * 0.3,
                                        -abs(x[i]["start"] - giua)))
            hang[:0] = [x[:k], x[k:]]
    return ra


def buoc_1(a):
    from whisper_vi import nghe
    kenh, f0, da = lam_du_an(a)
    f = nguon_doc(da, f0)
    lang = khoang_lang(f)

    def co_tieng(a0, b0):
        return max(0.0, (b0 - a0) - sum(max(0.0, min(b0, y) - max(a0, x)) for x, y in lang))

    W = []
    luu = da / "nghe.json"  # chạy lại bước 1 không phải nghe lại (Whisper mất 1–2 phút)
    if luu.exists() and json.loads(luu.read_text(encoding="utf-8")).get("nguon") == str(f):
        W = json.loads(luu.read_text(encoding="utf-8"))["W"]
        print("• dùng lại lời đã nghe (nghe.json)")
    for s_ in ([] if W else nghe(str(f))):
        ws = [w for w in s_["words"] if w["word"].strip()]
        if ws and (CHU_LA.search(s_["text"]) or re.search(r"\b[A-Z]{4,}\b", s_["text"])):
            # Whisper lạc tiếng (chữ Hàn, Nga, chữ HOA vô nghĩa "GORDON", lần 3 thử 24/11/2026): nghe lại riêng đoạn này
            ss = max(0.0, ws[0]["start"] - 0.5)
            lai = [w for x in nghe(str(f), ss=ss, t=ws[-1]["end"] + 0.5 - ss, vad=False) for w in x["words"] if w["word"].strip()]
            if lai and not CHU_LA.search(" ".join(w["word"] for w in lai)):
                print(f"• nghe lại {ss:.1f}–{ws[-1]['end']:.1f} giây vì Whisper lạc tiếng: {s_['text'][:50]}")
                ws = lai
            else:
                print(f"⚠ đoạn {ss:.1f}–{ws[-1]['end']:.1f} giây Whisper vẫn lạc tiếng, đừng chọn câu ở đây: {s_['text'][:50]}")
        dai = (ws[-1]["end"] - ws[0]["start"]) if ws else 0
        if len(ws) >= 4 and dai > 0 and len(ws) / dai > 7:
            # Whisper ghi giờ dồn: câu BỊA (âm thanh gần như im) thì bỏ; câu THẬT bị dồn giờ thì nghe lại riêng vùng đó
            am = co_tieng(ws[0]["start"], ws[-1]["end"] + 1.0)
            if len(ws) / max(am, 0.01) > 9:
                print(f"• bỏ câu Whisper bịa ({len(ws)} chữ, chỉ {am:.2f} giây có tiếng): {s_['text'][:60]}")
                continue
            ss = max(0.0, ws[0]["start"] - 3.0)
            lai = [w for x in nghe(str(f), ss=ss, t=ws[-1]["end"] + 1.2 - ss, vad=False) for w in x["words"] if w["word"].strip()]
            if lai:
                W = [w for w in W if w["start"] < ss - 0.05]
                ws = lai
                print(f"• nghe lại vùng {ss:.1f}–{ws[-1]['end']:.1f} giây vì Whisper ghi giờ dồn")
            else:
                for w in ws:
                    w["don"] = True
        if W:
            ws = [w for w in ws if w["start"] >= W[-1]["end"] - 0.05]
        W += ws
    if W and not luu.exists() or W and json.loads(luu.read_text(encoding="utf-8")).get("nguon") != str(f):
        ghi_json(luu, {"nguon": str(f), "W": [{"word": w["word"], "start": w["start"], "end": w["end"], **({"don": True} if w.get("don") else {})} for w in W]})
    if not W:
        sys.exit("✘ Không nghe được lời nào trong file (file không có tiếng hoặc không phải tiếng Việt).")
    giu = loc_dao(W, da / "bo-cat.txt")
    cau = tach_cau(giu)
    ds = [{"so": i + 1, "bd": round(c[0]["start"], 2), "kt": round(c[-1]["end"], 2),
           "chu": " ".join(w["word"].strip() for w in c),
           "w": [{"word": w["word"], "start": round(w["start"], 3), "end": round(w["end"], 3), **({"don": True} if w.get("don") else {})} for w in c]}
          for i, c in enumerate(cau)]
    tong = sum(c["kt"] - c["bd"] for c in ds)
    # Khoảng lặng theo CÙNG bộ dò tiếng nói (VAD) với nghiem_thu.py: tiếng thở, ồn phòng trên -32 dB vẫn là "lặng" với VAD.
    # Bước 2 dùng để cắt sát mép đoạn và tách lặng > 0,6 giây (khối của phiên chính 24/11/2026: nghiệm thu ĐẠT ngay vòng đầu)
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    from whisper_vi import doc_am_thanh
    ts = get_speech_timestamps(doc_am_thanh(str(f)), VadOptions(threshold=0.5, min_silence_duration_ms=150, speech_pad_ms=0))
    lang_vad = [(x["end"] / 16000, y["start"] / 16000) for x, y in zip(ts, ts[1:]) if (y["start"] - x["end"]) / 16000 > 0.25]
    if ts:
        lang_vad = [(0.0, ts[0]["start"] / 16000)] + lang_vad + [(ts[-1]["end"] / 16000, 1e9)]
    ghi_json(da / "cau.json", {"nguon": str(f), "lang": lang, "lang_vad": [[round(x, 3), round(y, 3)] for x, y in lang_vad],
                               "dai": a.dai, "tieuDe": a.tieu_de or "", "cau": ds})
    (da / "cau.txt").write_text(
        f"# {len(ds)} câu, tổng lời {tong:.0f} giây" + (f"; cần chọn khoảng {a.dai} giây" if a.dai else "") + "\n"
        + "\n".join(f"[{c['so']:02d}] {c['bd']:6.1f}–{c['kt']:6.1f} ({c['kt'] - c['bd']:4.1f} giây) {c['chu']}" for c in ds) + "\n",
        encoding="utf-8")
    if a.dai:
        chon, t = [], 0.0
        for c in ds:
            if t >= a.dai * 0.9:
                break
            chon.append({"cau": c["so"]})
            t += c["kt"] - c["bd"]
    else:
        chon = [{"cau": c["so"]} for c in ds]
    if not (da / "chon.json").exists():
        ghi_json(da / "chon.json", {"tieuDe": a.tieu_de or "", "doan": chon})
    print(f"✔ cau.txt: {len(ds)} câu, tổng lời {tong:.1f} giây; chon.json nháp: {len(chon)} câu")
    print("BƯỚC 2: đọc cau.txt, sửa chon.json (chọn câu" + (f" cho đủ khoảng {a.dai} giây" if a.dai else "")
          + ", đặt 2–4 cảnh minhHoa), rồi chạy:")
    print(f'  python edit.py "{da}" --chon --het')
    return da


# ---------------------------------------------------------------- bước 2
def khop_khuc(ws, mau):
    """Khúc chữ liền nhau trong ws gần giống câu mẫu nhất (so không dấu)."""
    m = [khong_dau(x) for x in re.findall(r"\w+", mau)]
    t = [khong_dau(chu(w)) for w in ws]
    if not m:
        return ws
    tot, best = -1.0, (0, len(ws))
    for i in range(len(t)):
        for n in range(max(1, len(m) - 3), len(m) + 4):
            if i + n > len(t):
                break
            r = difflib.SequenceMatcher(None, t[i:i + n], m).ratio()
            if r > tot + 1e-9:
                tot, best = r, (i, i + n)
    if tot < 0.6:
        sys.exit(f"✘ chon.json: không tìm thấy khúc «{mau}» trong câu (giống nhất {tot:.0%}). Chép đúng chữ từ cau.txt.")
    return ws[best[0]:best[1]]


def chia_dong(tokens):
    """Ngắt dòng phụ đề ≤ 28 ký tự, ưu tiên ngắt trước chữ nối gần giữa; gộp mẩu dưới 10 ký tự vào dòng sau."""
    ve, hien = [], []
    for t in tokens:
        hien.append(t)
        if re.search(r"[.,!?;:]$", t):
            ve.append(hien)
            hien = []
    if hien:
        ve.append(hien)

    def chia(x):
        if len(" ".join(x)) <= 28 or len(x) < 4:
            return [x]
        giua = len(x) / 2
        cho = [i for i in range(2, len(x) - 1) if x[i].lower().strip(",.") in NOI]
        i = min(cho, key=lambda k: abs(k - giua)) if cho else round(giua)
        return chia(x[:i]) + chia(x[i:])

    dong = [y for v in ve for y in chia(v)]
    gon = []
    for x in dong:
        if gon and len(" ".join(gon[-1])) < 10 and len(" ".join(gon[-1] + x)) <= 28:
            gon[-1] = gon[-1] + x
        else:
            gon.append(x)
    return gon


def sua_chu(tok, ref, sua):
    """Sửa chữ Whisper nghe sai theo "sua" của chon.json ({"cô đây dần": "agent", "skin": "skill"}), so không phân biệt hoa
    thường, giữ dấu câu cuối. Sửa ở đây (không sửa tay loi.txt) để số dòng và mốc cảnh luôn khớp."""
    if not sua:
        return tok, ref
    luat = sorted(((k.lower().split(), v.split()) for k, v in sua.items()), key=lambda x: -len(x[0]))
    ot, orf, i = [], [], 0
    while i < len(tok):
        for sai, dung in luat:
            n = len(sai)
            doan = [re.sub(r"[.,!?;:]$", "", t).lower() for t in tok[i:i + n]]
            if n and doan == sai:
                cuoi = re.search(r"[.,!?;:]$", tok[i + n - 1])
                moi = dung[:]
                if cuoi and moi and not re.search(r"[.,!?;:]$", moi[-1]):
                    moi[-1] += cuoi.group(0)
                if i == 0 and tok[0][:1].isupper() and moi:
                    moi[0] = moi[0][:1].upper() + moi[0][1:]
                ot += moi
                orf += [ref[i]] * len(moi)
                i += n
                break
        else:
            ot.append(tok[i])
            orf.append(ref[i])
            i += 1
    return ot, orf


def moc_theo_loi(muc, tu_tg, goc, dai):
    """Mốc sáng từng mục = lúc người nói nói chữ đầu của mục (chấm bản 30 giây 24/11/2026: rải đều làm "Soạn hợp đồng"
    sáng sớm 1,7 giây). Trả None nếu không tìm đủ thì rải đều."""
    if not muc or not isinstance(muc, list):
        return None
    ra, tu_i = [], 0
    for m in muc:
        chu_m = m.get("ten") if isinstance(m, dict) else (m[-1] if isinstance(m, list) else m)
        k = [khong_dau(x) for x in re.findall(r"\w+", str(chu_m or ""))][:2]
        if not k:
            return None
        hit = next((i for i in range(tu_i, len(tu_tg)) if tu_tg[i][0] == k[0] and (len(k) < 2 or i + 1 < len(tu_tg) and tu_tg[i + 1][0] == k[1])), None)
        if hit is None:
            return None
        ra.append(round(min(max(0.2, tu_tg[hit][1] - goc - 0.15), max(dai - 0.3, 0.2)), 2))
        tu_i = hit + 1
    return ra


def nang_luong(f):
    """Năng lượng (dB) từng khung 10 ms của file (16 kHz mono)."""
    import numpy as np
    from whisper_vi import doc_am_thanh
    a = doc_am_thanh(str(f))
    n = len(a) // 160
    return 20 * np.log10(np.sqrt((a[:n * 160].reshape(n, 160) ** 2).mean(axis=1)) + 1e-9)


def trung(e, t0, t1, cuoi=True):
    """Chỗ cắt trong [t0, t1] giây: cuoi=True → mép cuối chữ (khung lặng ĐẦU TIÊN); cuoi=False → mép đầu chữ (ngay sau khung
    lặng CUỐI CÙNG). Lặng = dưới nền ồn (bách phân vị 15) + 12 dB. Không có khung lặng thì lấy chỗ trũng sâu nhất."""
    import numpy as np
    i0, i1 = max(0, int(t0 * 100)), min(len(e), int(t1 * 100))
    if i1 - i0 < 2:
        return None
    s = e[i0:i1]
    nguong = float(np.percentile(e, 15)) + 12
    # các quãng lặng liền nhau; khe ngừng giữa hai chữ thường là quãng DÀI nhất (phụ âm cuối "t", "c" chỉ trũng 1–2 khung)
    quang, bd = [], None
    for i, v in enumerate(list(s) + [1e9]):
        if v < nguong and bd is None:
            bd = i
        elif v >= nguong and bd is not None:
            quang.append((bd, i))
            bd = None
    quang = [q for q in quang if q[1] - q[0] >= 4]  # ≥ 40 ms: phụ âm cuối chỉ trũng 1–3 khung
    if quang:
        i = quang[0][0] if cuoi else quang[-1][1]
    else:
        # nói liền không có quãng lặng: chỗ trũng sâu nhất (làm mượt 3 khung)
        i = int(np.argmin(np.convolve(s, np.ones(3) / 3, mode="same")))
    return (i0 + i) / 100


def lap_tu_chon(cj, chon, nang=None):
    """Trả (doan, dong phụ đề, canh, giây, tốc độ). Tách riêng để hồi quy kiểm được không cần Whisper.
    nang: năng lượng 10 ms của file gốc (nang_luong) để cắt đúng chỗ trũng; None thì bám khoảng lặng silencedetect/VAD."""
    cau = {c["so"]: c for c in cj["cau"]}
    lang = [tuple(x) for x in cj.get("lang", [])]
    lang_vad = [tuple(x) for x in cj.get("lang_vad", [])]
    so_sau = {c["so"]: (cj["cau"][k + 1]["bd"] if k + 1 < len(cj["cau"]) else 1e9) for k, c in enumerate(cj["cau"])}
    khuc = []
    for x in chon["doan"]:
        if x["cau"] not in cau:
            sys.exit(f"✘ chon.json: không có câu {x['cau']} trong cau.txt")
        ws = cau[x["cau"]]["w"]
        if x.get("chu"):
            ws = khop_khuc(ws, x["chu"])
        goc_w = cau[x["cau"]]["w"]
        k_cuoi = next(i for i, w in enumerate(goc_w) if w is ws[-1])
        # khúc cắt giữa câu: giờ chữ kế tiếp, để điểm cắt rơi vào giữa khe chứ không cụt chữ cuối
        x["_ke"] = goc_w[k_cuoi + 1]["start"] if k_cuoi + 1 < len(goc_w) else None
        k_dau = next(i for i, w in enumerate(goc_w) if w is ws[0])
        x["_truoc"] = goc_w[k_dau - 1]["end"] if k_dau > 0 else None
        khuc.append((x, ws, so_sau[x["cau"]] if x["_ke"] is None else x["_ke"]))
    # doan: đúng giờ chữ đầu, chữ cuối; tách ở khoảng lặng THẬT > 0,45 giây bên trong
    doan, dong, moc_dong, tg = [], [], [], 0.0
    for x, ws, tran in khuc:
        a0, b0 = ws[0]["start"], ws[-1]["end"]
        con_tieng = not any(p <= b0 + 0.15 <= q or b0 <= p <= b0 + 0.15 for p, q in lang)
        # Chấm bản 30 giây lần 3 (24/11/2026, 7,5/10): giờ chữ của Whisper lệch nên cắt theo giờ chữ làm cụt đuôi "email",
        # "thôi", "báo giá" và lọt đầu chữ kế ("để", "xem"). Bám điểm cắt vào chỗ lặng THẬT gần nhất (silencedetect + VAD);
        # không có chỗ lặng thì dừng ngay trước chữ kế tiếp. lap_master.py đệm 0,06 giây đầu, 0,12 giây cuối.
        lang_tat = sorted(lang + lang_vad)
        ke = x["_ke"] if x.get("_ke") is not None else (tran if tran < 1e8 else None)
        # ưu tiên chỗ lặng ở SAU chữ cuối (lần 4: lấy chỗ lặng gần nhất phía trước làm mất chữ "thôi"); không có mới lùi
        sau_c = [p for p, q in lang_tat if b0 - 0.05 <= p <= b0 + 0.45 and (ke is None or p < ke + 0.05)]
        truoc_c = [p for p, q in lang_tat if b0 - 0.15 <= p < b0 - 0.05]
        cuoi = [min(sau_c)] if sau_c else ([max(truoc_c)] if truoc_c else [])
        if cuoi:
            b0 = cuoi[0] - 0.07
        elif ke is not None:
            b0 = min(b0, ke - 0.15)
        elif con_tieng and ws[-1].get("don"):
            sau = [p for p, q in lang if p > b0]
            b0 = min(sau[0] if sau else b0 + 1.5, tran - 0.1, b0 + 2.0)
        elif con_tieng:
            b0 -= 0.1
        tr = x.get("_truoc")
        if nang is not None:
            # Chấm lần 4 (7,5/10): 8/21 điểm cắt vẫn giữa tiếng vì khe giữa chữ chỉ 0,1–0,2 giây, silencedetect/VAD không thấy.
            # Đo năng lượng 10 ms ở file gốc, cắt vào chỗ trũng thật giữa chữ cuối và chữ kế (cách người chấm đo).
            r1 = ws[-1]["end"]
            t_c = trung(nang, r1 - 0.05, min(r1 + 0.45, ke + 0.15) if ke is not None else r1 + 0.45, cuoi=True)
            if t_c is not None:
                b0 = t_c + 0.03 - 0.12
            s0 = ws[0]["start"]
            t_d = trung(nang, s0 - (0.3 if tr is not None else 0.12), s0 + 0.1, cuoi=False)
            if t_d is not None:
                a0 = t_d - 0.03 + 0.06
        dau_l = [q for p, q in lang_tat if a0 - 0.45 <= q <= a0 + 0.15 and (tr is None or q > tr - 0.05)]
        if nang is not None:
            pass
        elif dau_l:
            a0 = max(dau_l) + 0.03
        elif tr is not None:
            a0 = max(a0, tr + 0.08)
        dau, sg = a0, []
        for p, q in [(p, q) for p, q in lang if p > a0 + 0.2 and q < b0 - 0.2 and q - p > 0.45]:
            sg.append([dau, p + 0.1])
            dau = q - 0.1
        sg.append([dau, b0])
        # cắt sát mép theo khoảng lặng (silencedetect + VAD), tách lặng VAD > 0,6 giây giữa đoạn, giữ 0,15 giây mỗi bên
        gon = []
        for d0, d1 in sg:
            for p, q in lang + lang_vad:
                if p <= d0 < q:
                    d0 = max(d0, q - 0.08)
                if p < d1 <= q:
                    d1 = min(d1, p + 0.12)
            dd0 = d0
            for p, q in lang_vad:
                if p > dd0 + 0.2 and q < d1 - 0.2 and q - p > 0.6:
                    gon.append([dd0, p + 0.15])
                    dd0 = q - 0.15
            if d1 - dd0 > 0.15:
                gon.append([dd0, d1])
        gon = gon or [[a0, b0]]
        doan += [[0, round(p, 2), round(q, 2)] for p, q in gon]
        bo_trong = (b0 - a0) - sum(q - p for p, q in gon)
        # phụ đề của khúc này; giờ mỗi dòng (trên dòng thời gian đã cắt, ước) để đặt cảnh clip ≤ 7,5 giây
        tok, ref = [], []
        for w in ws:
            t = w["word"].strip()
            if tok and re.match(r"^[.,%]\w", t):
                tok[-1] += t
            else:
                tok.append(t)
                ref.append(w)
        tok, ref = sua_chu(tok, ref, chon.get("sua", {}))
        dd = chia_dong(tok)
        k = 0
        tl = (b0 - a0) - bo_trong
        bat = []
        for d_ in dd:
            bat.append(ref[k]["start"] - a0)
            k += len(d_)
        co = (tl / max(b0 - a0, 0.01))
        x["_dong"] = (len(dong) + 1, len(dong) + len(dd))  # số dòng (đếm từ 1) của khúc
        x["_bat"] = [round(b * co, 2) for b in bat]          # giây bắt đầu từng dòng tính từ đầu khúc
        x["_dai"] = round(tl, 2)
        x["_tu"] = [(khong_dau(re.sub(r"[^\w]", "", t_)), round((r_["start"] - a0) * co, 2)) for t_, r_ in zip(tok, ref)]
        dong += [" ".join(d_) for d_ in dd]
        tg += tl
    # Hai đoạn liền nhau hoặc chồng nhau trong file gốc (khúc nối tiếp câu, điểm cắt bám chỗ trũng vượt sang khúc sau): gộp làm
    # một, vì lap_master.py đệm 0,06 + 0,12 giây ở mỗi mép sẽ phát lặp một mẩu âm (lần 4, 24/11/2026)
    gop_d = []
    for s_ in doan:
        if gop_d and s_[0] == gop_d[-1][0] and s_[1] <= gop_d[-1][2] + 0.2 and s_[2] > gop_d[-1][1]:
            gop_d[-1][2] = max(gop_d[-1][2], s_[2])
        else:
            gop_d.append(list(s_))
    doan = gop_d
    if dong:
        dong[0] = dong[0][:1].upper() + dong[0][1:]
    # Tốc độ nói (khối của phiên chính 24/11/2026): người mới hay nói chậm, ngập ngừng. Đo chữ/giây trên phần giữ lại; chậm hơn
    # nhịp video ngắn (khoảng 4,4 chữ/giây) thì tăng tốc cả hình lẫn tiếng (giữ cao độ), tối đa 1,2 lần. chon.json "toc" để ép.
    so_chu = sum(len(ws) for _, ws, _ in khuc)
    nhip = so_chu / max(tg, 0.01)
    toc = float(chon["toc"]) if chon.get("toc") else round(min(1.2, max(1.0, 4.4 / nhip)), 2)
    print(f"✔ nhịp nói {nhip:.1f} chữ/giây → tốc độ {toc}" + (" (tăng cho gọn, giọng giữ cao độ)" if toc > 1 else " (giữ nguyên)"))
    for x, _, _ in khuc:  # mốc cảnh tính trên dòng thời gian sau khi đổi tốc độ
        x["_bat"] = [round(b / toc, 2) for b in x["_bat"]]
        x["_dai"] = round(x["_dai"] / toc, 2)
        x["_tu"] = [(c_, round(s_ / toc, 2)) for c_, s_ in x["_tu"]]
    tg /= toc
    # canh
    tieu = (chon.get("tieuDe") or cj.get("tieuDe") or "").strip()
    if tieu:
        tren, _, duoi = tieu.partition("|")
    else:
        tu0 = re.sub(r"[.,!?]", "", dong[0]).split()
        tren, duoi = " ".join(tu0[:3]).upper(), " ".join(tu0[3:6]).upper()
    # thẻ tiêu đề hiện ở dòng nói đúng chữ của tiêu đề (thử máy học viên 24/11/2026: at cố định làm thẻ hiện trước giọng 2,2 giây)
    tu_tieu = {khong_dau(t) for t in re.findall(r"\w+", f"{tren} {duoi}") if len(t) > 2}
    at = next((i + 1 for i, d_ in enumerate(dong[:12]) if tu_tieu & {khong_dau(t) for t in re.findall(r"\w+", d_)}), 1)
    canh = []
    het1 = khuc[0][0]["_dong"][1] + 1
    canh.append({"loai": "nguoi-chu", "tu": 0, "den": min(max(het1, at + 2), len(dong) + 1), "tren": tren.strip(), "duoi": duoi.strip(), "at": at,
                 "viTriPhuDe": 1560})

    def them_nguoi(tu, den):
        if den <= tu:
            return
        if canh and canh[-1]["loai"] == "nguoi" and canh[-1]["den"] == tu:
            canh[-1]["den"] = den
        else:
            canh.append({"loai": "nguoi", "tu": tu, "den": den, "viTriPhuDe": 1560})

    bo_qua = set()
    for idx in range(1, len(khuc)):
        if idx in bo_qua:
            continue
        x = khuc[idx][0]
        d1, d2 = x["_dong"]
        tu = max(d1, canh[-1]["den"])
        if tu > d2:
            continue
        mh = x.get("minhHoa")
        if not mh:
            them_nguoi(tu, d2 + 1)
            continue
        mh = dict(mh)
        loai = mh["loai"]
        # "gop": n -> cảnh minh họa phủ luôn n khúc kế tiếp (vd danh sách việc nói qua 2 câu)
        bat, dai_tong, tu_tg = list(x["_bat"]), x["_dai"], list(x["_tu"])
        for g in range(1, int(mh.pop("gop", 0)) + 1):
            if idx + g >= len(khuc):
                break
            y = khuc[idx + g][0]
            bat += [dai_tong + b for b in y["_bat"]]
            tu_tg += [(c_, dai_tong + s_) for c_, s_ in y["_tu"]]
            dai_tong += y["_dai"]
            d2 = y["_dong"][1]
            bo_qua.add(idx + g)
        den = d2 + 1
        goc = bat[tu - d1]

        def ket(dn):  # giây kết thúc (tính từ đầu khúc) nếu cảnh dừng trước dòng dn
            return bat[dn - d1] if dn <= d2 else dai_tong
        if loai in CANH_CLIP:
            # clip kho dài 8 giây: cảnh kết trong 7,5 giây, phần còn lại của câu về người nói
            den = tu + 1
            while den <= d2 and ket(den + 1) - goc <= CLIP_TOI_DA:
                den += 1
        dai = ket(den) - goc
        c = {**MAC_DINH.get(loai, {}), **mh, "tu": tu, "den": den}
        n = None
        if "moc" not in mh:
            if loai in SO_MOC and SO_MOC[loai] and isinstance(mh.get(SO_MOC[loai]), list):
                n = len(mh[SO_MOC[loai]])
            elif loai in HAI_MOC:
                n = 2
            if n:
                c["moc"] = moc_theo_loi(mh.get(SO_MOC.get(loai) or "", []), tu_tg, goc, dai) or \
                    [round(0.3 + i * max(dai - 0.6, 0.5) / n, 2) for i in range(n)]
        canh.append(c)
        them_nguoi(den, d2 + 1)
    canh[-1]["den"] = "het"
    return doan, dong, canh, tg, toc


def buoc_2(a):
    da = Path(a.kenh).resolve()
    if not (da / "cau.json").exists():
        sys.exit(f"✘ {da} chưa có cau.json: chạy bước 1 trước (python edit.py \"<thư mục kênh>\" \"<file quay>\").")
    cj = json.loads((da / "cau.json").read_text(encoding="utf-8"))
    chon = json.loads((da / "chon.json").read_text(encoding="utf-8"))
    doan, dong, canh, tg, toc = lap_tu_chon(cj, chon, nang_luong(cj["nguon"]))
    ghi_json(da / "doan.json", {"nguon": [cj["nguon"]], "doan": doan, "toc": toc})
    (da / "loi.txt").write_text("\n".join(dong) + "\n", encoding="utf-8")
    ghi_json(da / "canh.json", {"canh": canh})
    # gợi ý tên riêng cho Whisper lúc nghiệm thu: lần 3 thử 24/11/2026 nhạc nền làm "agent" thành "agile", đủ lời tụt 91% → 81%
    goi = [v for v in (chon.get("sua") or {}).values()] + list(chon.get("goiY") or [])
    goi += [t for t in re.findall(r"\b[A-Za-z]{2,}\b", (chon.get("tieuDe") or "").replace("|", " "))]
    goi = list(dict.fromkeys(g.strip() for g in goi if g.strip()))
    if goi and not (da / "goi-y.txt").exists():
        (da / "goi-y.txt").write_text(", ".join(goi), encoding="utf-8")
    mh = sum(1 for c in canh if c["loai"] not in ("nguoi", "nguoi-chu"))
    print(f"✔ {len(chon['doan'])} khúc, khoảng {tg:.1f} giây lời; loi.txt {len(dong)} dòng; {len(canh)} cảnh, {mh} cảnh minh họa")
    if cj.get("dai") and abs(tg - cj["dai"]) > cj["dai"] * 0.25:
        print(f"⚠ dài {tg:.0f} giây, lệch xa mục tiêu {cj['dai']} giây: thêm hoặc bớt câu trong chon.json")
    if mh == 0 and len(dong) > 8:
        print("⚠ chưa có cảnh minh họa nào: video chỉ có người nói dễ nhàm, thêm 2–4 minhHoa trong chon.json")
    r = subprocess.run([sys.executable, ND / "dung.py", da, *(["--het"] if a.het else [])])
    sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kenh", help="bước 1: thư mục kênh; bước 2 (--chon): thư mục dự án")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--ten")
    ap.add_argument("--tieu-de")
    ap.add_argument("--dai", type=int, help="độ dài mong muốn (giây), vd 30")
    ap.add_argument("--chon", action="store_true", help="bước 2: dựng theo chon.json")
    ap.add_argument("--het", action="store_true")
    a = ap.parse_args()
    if a.chon:
        buoc_2(a)
    elif not a.file:
        sys.exit("✘ thiếu file quay. Bước 1: python edit.py \"<thư mục kênh>\" \"<file quay>\" [--dai 30]")
    else:
        buoc_1(a)


if __name__ == "__main__":
    main()
