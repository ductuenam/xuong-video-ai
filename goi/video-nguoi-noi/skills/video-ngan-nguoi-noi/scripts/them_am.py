"""Học viên tự thêm nhạc nền, tiếng hiệu ứng vào kho của xưởng, theo đúng quy chuẩn của kho chung (25/11/2026).

  python them_am.py do <tệp> [<tệp> ...]          1. Đo bằng máy, vẽ ảnh dạng sóng + phổ, in bản nháp nhãn (JSON). Không ghi gì.
  python them_am.py ghi <nhan.json>               2. Kiểm nhãn, in trước sẽ thêm gì. Không ghi gì.
  python them_am.py ghi <nhan.json> --that        3. Học viên đã OK: chép tệp vào tai-nguyen/<loai>/cua-toi/<nhom>/, ghi chỉ mục.

Tệp nguồn nhận mọi định dạng ffmpeg đọc được, kể cả video (lấy phần tiếng). Nhạc đổi sang .mp3, tiếng sang .wav nếu cần.
nhan.json: một danh sách, mỗi phần tử là bản nháp của bước 1 đã điền đủ chỗ "<...>". Luật nhãn: references/tu-dien-am.json
(tâm trạng chỉ dùng từ trong từ điển, từ đồng nghĩa tự đổi; giấy phép phải hỏi học viên). AI không nghe được: tả theo số đo
và ảnh (Read ảnh), hỏi học viên bài có lời hát không, nguồn ở đâu. Không bao giờ sửa, đổi tên hay xóa tệp gốc của học viên.
Mã cấp mới: UNH0001, UAM0001... tăng dần, không dùng lại. Tệp đã có trong kho (cùng nội dung) thì báo mã cũ, không thêm lần hai."""
import argparse
import csv
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

import kho_am
from chung import XUONG

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SR = 22050
TIEN_TO = {"nhac": "NH", "am": "AM"}
BAT_BUOC = {"nhac": ["mo_ta", "tu_khoa", "nhip_bpm", "nang_luong", "tam_trang", "hop_video", "doan", "bat_dau_goi_y", "do_lon_lufs"],
            "am": ["mo_ta", "tu_khoa", "giay", "diem_nhan_s", "do_lon", "dung_khi"]}
COT_CHUNG = ["ma", "loai", "nhom", "ten_nhom", "mo_ta", "tu_khoa", "tep", "xem_truoc", "thong_so", "nguon", "giay_phep", "chu", "goi",
             "ngay_them", "trang_thai"]
CHO_DIEN = "<điền>"


def pcm(p):
    b = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(p), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True).stdout
    return np.frombuffer(b, np.float32)


def lufs(p):
    e = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(p), "-vn", "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", e)
    return float(m[-1]) if m else None


def kbps(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=bit_rate,codec_name", "-of", "json", str(p)],
                       capture_output=True, text=True)
    try:
        s = json.loads(r.stdout)["streams"][0]
        return int(s.get("bit_rate") or 0) // 1000, s.get("codec_name", "")
    except (ValueError, KeyError, IndexError):
        return 0, ""


def db(x):
    return 20 * np.log10(x + 1e-9)


def bpm(x):
    hop = 512
    n = len(x) // hop
    if n < 50:
        return None
    f = np.abs(np.fft.rfft(x[:n * hop].reshape(n, hop) * np.hanning(hop), axis=1))
    flux = np.maximum(0, np.diff(np.log1p(f), axis=0)).sum(1)
    flux -= flux.mean()
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    fps = SR / hop
    lo, hi = int(fps * 60 / 180), int(fps * 60 / 70)
    return int(round(60 * fps / (lo + np.argmax(ac[lo:hi]))))


def anh(x, dich, ten):
    """Ảnh 1200x500: trên là dạng sóng, dưới là phổ (vạch ngang = có cao độ, loang đều = tiếng ồn), vạch dọc mỗi giây/10 giây."""
    from PIL import Image, ImageDraw
    W, H1, H2 = 1200, 200, 300
    im = Image.new("RGB", (W, H1 + H2), (18, 18, 24))
    d = ImageDraw.Draw(im)
    n = len(x)
    cot = np.array_split(np.abs(x), W) if n >= W else [np.abs(x)] * W
    for i, c in enumerate(cot):
        v = float(c.max()) if len(c) else 0
        d.line([(i, H1 // 2 - v * H1 / 2), (i, H1 // 2 + v * H1 / 2)], fill=(90, 190, 255))
    nfft = 1024
    so_khung = max(1, (n - nfft) // 256)
    buoc = max(1, so_khung // W)
    khung = [x[i * 256: i * 256 + nfft] for i in range(0, so_khung, buoc)]
    if khung and len(khung[0]) == nfft:
        S = db(np.abs(np.fft.rfft(np.array(khung) * np.hanning(nfft), axis=1))).T[::-1]
        S = np.clip((S - (S.max() - 80)) / 80, 0, 1)
        S = np.array(Image.fromarray((S * 255).astype(np.uint8)).resize((W, H2)))
        mau = np.stack([S, (S * 0.6).astype(np.uint8), (255 - S) // 3], -1)
        im.paste(Image.fromarray(mau.astype(np.uint8)), (0, H1))
    dur = n / SR
    moc = 1 if dur <= 12 else 10
    for s in np.arange(0, dur, moc):
        xx = int(s / dur * W)
        d.line([(xx, 0), (xx, 8)], fill=(255, 255, 255))
        d.text((xx + 2, 8), f"{s:g}s", fill=(200, 200, 200))
    d.text((6, H1 - 14), ten[:80], fill=(255, 220, 120))
    dich.parent.mkdir(parents=True, exist_ok=True)
    im.save(dich)


def do(p):
    """Số đo một tệp + bản nháp nhãn."""
    x = pcm(p)
    if len(x) < SR * 0.05:
        return {"tep": str(p), "loi": "không đọc được tiếng trong tệp này (hỏng hoặc không có tiếng)"}
    dur = len(x) / SR
    loai = "nhac" if dur >= 30 else "am"
    dinh = float(db(np.abs(x).max()))
    w = int(SR * 0.05)
    rms = np.array([np.sqrt(np.mean(x[i:i + w] ** 2)) for i in range(0, len(x) - w + 1, w)]) if len(x) > w else np.array([np.abs(x).max()])
    rdb = db(rms)
    nhan = round(float(np.argmax(rms)) * 0.05, 2)
    song = np.where(rdb > rdb.max() - 40)[0]
    dau_im = round(float(song[0]) * 0.05, 2) if len(song) else 0.0
    cuoi_im = round(dur - (float(song[-1]) + 1) * 0.05, 2) if len(song) else 0.0
    l = lufs(p)
    kb, codec = kbps(p)
    canh_bao = []
    if np.mean(np.abs(x) > 0.995) > 0.001:
        canh_bao.append("nhiều chỗ chạm trần (bẹt đỉnh): có thể đã méo, nghe thử trước khi dùng")
    if codec == "mp3" and 0 < kb < 128:
        canh_bao.append(f"mp3 {kb} kbps: chất lượng thấp")
    if cuoi_im > 1.5:
        canh_bao.append(f"đuôi im {cuoi_im:g} giây")
    if dau_im > 1.0:
        canh_bao.append(f"đầu im {dau_im:g} giây")
    r = {"tep": str(p), "loai": loai, "giay": round(dur, 2), "lufs": l, "dinh_db": round(dinh, 1), "kbps": kb,
         "dau_im_s": dau_im, "cuoi_im_s": cuoi_im, "diem_nhan_s": nhan, "canh_bao": canh_bao}
    if loai == "nhac":
        w2 = SR * 2
        moi_2s = [int(round(float(db(np.sqrt(np.mean(x[i:i + w2] ** 2)))))) for i in range(0, len(x) - w2 + 1, w2)]
        r["do_lon_moi_2s"] = moi_2s
        r["nhip_bpm_uoc"] = bpm(x)
        trung = float(np.median(moi_2s)) if moi_2s else 0
        bd = next((i * 2 for i, v in enumerate(moi_2s) if v >= trung - 8), 0)  # bỏ đoạn dạo nhỏ hơn hẳn phần chính
        r["bat_dau_goi_y"] = bd
    ten_anh = kho_am.khong_dau(Path(p).stem)[:60] or "am"
    dich = (XUONG / ".tam" / "do-am" / f"{ten_anh}.png") if XUONG else Path(p).with_suffix(".do-am.png")
    try:
        anh(x, dich, Path(p).name)
        r["anh"] = str(dich)
    except Exception as e:  # noqa: BLE001 - thiếu Pillow thì vẫn có số đo
        r["anh"] = f"(không vẽ được ảnh: {e})"
    r["nhap"] = ban_nhap(r)
    return r


def do_lon_chu(l, dinh):
    if l is None:
        return "vua"
    if l < -26:
        return f"nho (LUFS {l:.0f}; máy tự tăng khi trộn)"
    if l > -14 or dinh > -0.1:
        return f"rat-to (LUFS {l:.0f}, đỉnh {dinh:.0f} dB; máy tự hạ khi trộn)"
    return f"vua (LUFS {l:.0f})"


def ban_nhap(r):
    if r["loai"] == "nhac":
        return {"tep": r["tep"], "loai": "nhac", "nhom": "nen-video-ngan", "slug": CHO_DIEN, "mo_ta": CHO_DIEN, "tu_khoa": CHO_DIEN,
                "nhip_bpm": f"~{r['nhip_bpm_uoc']}" if r.get("nhip_bpm_uoc") else "", "nang_luong": CHO_DIEN, "tam_trang": CHO_DIEN,
                "hop_video": CHO_DIEN, "doan": CHO_DIEN, "bat_dau_goi_y": r.get("bat_dau_goi_y", 0), "do_lon_lufs": r["lufs"],
                "nguon": CHO_DIEN, "giay_phep": CHO_DIEN}
    return {"tep": r["tep"], "loai": "am", "nhom": CHO_DIEN, "slug": CHO_DIEN, "mo_ta": CHO_DIEN, "tu_khoa": CHO_DIEN, "giay": r["giay"],
            "diem_nhan_s": r["diem_nhan_s"], "do_lon": do_lon_chu(r["lufs"], r["dinh_db"]), "dung_khi": CHO_DIEN,
            "nguon": CHO_DIEN, "giay_phep": CHO_DIEN}


def sha(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for k in iter(lambda: f.read(1 << 20), b""):
            h.update(k)
    return h.hexdigest()


def doc_tho(loai):
    """Mọi dòng (kể cả dòng ẩn) và tên cột của chỉ mục; chưa có tệp thì cột chuẩn."""
    f = kho_am.goc(loai) / "chi-muc.csv"
    if not f.is_file():
        return [], COT_CHUNG + BAT_BUOC[loai][2:]
    with f.open(encoding="utf-8-sig", newline="") as g:
        rd = csv.DictReader(g)
        return list(rd), list(rd.fieldnames or [])


def kiem(n, loai_ds):
    """Trả về (dòng đã chuẩn hóa, lỗi, nhắc)."""
    loi, nhac = [], []
    p = Path(n.get("tep") or "")
    loai = n.get("loai")
    if loai not in TIEN_TO:
        return None, [f"{p.name}: loai phải là nhac hoặc am"], []
    if not p.is_file():
        loi.append(f"không thấy tệp {p}")
    d = {k: (str(v).strip() if v is not None else "") for k, v in n.items()}
    cho = [k for k, v in d.items() if CHO_DIEN in v]
    if cho:
        loi.append(f"{p.name}: còn chỗ chưa điền: {', '.join(cho)}")
    thieu = [c for c in BAT_BUOC[loai] + ["slug", "nhom"] if not d.get(c)]
    if thieu:
        loi.append(f"{p.name}: thiếu {', '.join(thieu)}")
    if d.get("slug") and (not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", d["slug"]) or len(d["slug"]) > 32):
        goi_y = kho_am.khong_dau(d["slug"])[:32].strip("-")
        loi.append(f"{p.name}: slug '{d['slug']}' sai luật (chữ thường không dấu, nối '-', tối đa 32 ký tự); gợi ý: {goi_y}")
    d["nhom"] = kho_am.khong_dau(d.get("nhom"))
    if d["nhom"] and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+){0,2}", d["nhom"]):
        loi.append(f"{p.name}: nhóm '{d['nhom']}' phải 1–3 từ không dấu nối '-'")
    co_nhom = {r.get("nhom"): r.get("ten_nhom") for r in loai_ds[loai]}
    if loai == "am":
        co_nhom.update(kho_am.TU_DIEN["nhom_am"])
    if d["nhom"] and d["nhom"] not in co_nhom and not d.get("ten_nhom"):
        loi.append(f"{p.name}: nhóm mới '{d['nhom']}' cần ten_nhom (tiếng Việt); nhóm có sẵn: {', '.join(sorted(co_nhom))}")
    d["ten_nhom"] = d.get("ten_nhom") or (co_nhom.get(d["nhom"]) or "").split(":")[0]
    d["tu_khoa"] = ";".join(dict.fromkeys(k for k in (kho_am.khong_dau(x) for x in re.split(r"[;,]", d.get("tu_khoa", ""))) if k))
    gp = kho_am.khong_dau(d.get("giay_phep"))
    hop_le = set(kho_am.TU_DIEN["giay_phep_dung_duoc"]) | set(kho_am.TU_DIEN["giay_phep_khac"])
    if gp and gp not in hop_le:
        loi.append(f"{p.name}: giấy phép '{d['giay_phep']}' không hiểu; dùng một trong: {', '.join(sorted(hop_le))}")
    elif gp == "chua-ro":
        nhac.append(f"{p.name}: giấy phép chưa rõ: thêm được vào kho nhưng máy sẽ không cho dùng trong video đăng công khai")
    d["giay_phep"] = gp
    if loai == "nhac":
        tam, la = kho_am.chuan_tam(d.get("tam_trang"))
        if la:
            loi.append(f"{p.name}: tâm trạng không có trong từ điển: {', '.join(la)}; chỉ dùng: {', '.join(kho_am.TAM_TRANG)}")
        d["tam_trang"] = ";".join(tam[:3])
        if d.get("nang_luong") and d["nang_luong"] not in kho_am.TU_DIEN["nang_luong"]:
            loi.append(f"{p.name}: nang_luong chỉ nhận {', '.join(kho_am.TU_DIEN['nang_luong'])}")
        hv = [kho_am.khong_dau(x) for x in re.split(r"[;,]", d.get("hop_video", "")) if x.strip()]
        la = [x for x in hv if x not in kho_am.TU_DIEN["hop_video"]]
        if la:
            loi.append(f"{p.name}: hop_video không hiểu: {', '.join(la)}; chỉ dùng: {', '.join(kho_am.TU_DIEN['hop_video'])}")
        d["hop_video"] = ";".join(dict.fromkeys(hv))
    for c in ("bat_dau_goi_y", "giay", "diem_nhan_s", "do_lon_lufs"):
        if c in BAT_BUOC[loai] and d.get(c) and kho_am.so(d[c]) is None:
            loi.append(f"{p.name}: {c} phải là số")
    return d, loi, nhac


def ghi(nhan, that):
    ds = json.loads(Path(nhan).read_text(encoding="utf-8"))
    ds = ds if isinstance(ds, list) else [ds]
    tho = {l: doc_tho(l) for l in TIEN_TO}
    loai_ds = {l: tho[l][0] for l in TIEN_TO}
    da_co = {}  # sha1 tệp nguồn (cột dau_van_tay, có cả khi đã đổi định dạng) -> mã; tệp trong kho so theo dung lượng rồi sha1
    theo_co = {}
    for l in TIEN_TO:
        for r in loai_ds[l]:
            if r.get("dau_van_tay"):
                da_co[r["dau_van_tay"]] = r["ma"]
            f = kho_am.goc(l) / (r.get("tep") or "")
            if r.get("tep") and f.is_file():
                theo_co.setdefault(f.stat().st_size, []).append((f, r["ma"]))
    so = {l: max([int(r["ma"][3:]) for r in loai_ds[l] if re.fullmatch(rf"U{TIEN_TO[l]}\d{{4}}", r.get("ma", ""))] + [0]) for l in TIEN_TO}
    loi_tong, ke_hoach = [], []
    for n in ds:
        d, loi, nhac = kiem(n, loai_ds)
        for x in nhac:
            print("⚠", x)
        if loi:
            loi_tong += loi
            continue
        src = Path(d["tep"])
        d["dau_van_tay"] = sha(src)
        trung = da_co.get(d["dau_van_tay"]) or next((ma for f, ma in theo_co.get(src.stat().st_size, []) if sha(f) == d["dau_van_tay"]), None)
        if trung:
            print(f"• {src.name}: đã có trong kho, mã {trung}; không thêm lần hai")
            continue
        da_co[d["dau_van_tay"]] = "(cùng lượt này)"
        l = d["loai"]
        so[l] += 1
        ma = f"U{TIEN_TO[l]}{so[l]:04d}"
        duoi = src.suffix.lower() if src.suffix.lower() in ((".mp3",) if l == "nhac" else (".wav", ".mp3")) else (".mp3" if l == "nhac" else ".wav")
        ke_hoach.append((l, ma, d, src, f"cua-toi/{d['nhom']}/{ma}_{d['slug']}{duoi}"))
    if loi_tong:
        print("✘ CHƯA GHI GÌ. Sửa các chỗ sau trong", nhan)
        for x in loi_tong:
            print("  -", x)
        return 1
    if not ke_hoach:
        print("• không có gì mới để thêm")
        return 0
    for l, ma, d, src, tep in ke_hoach:
        them = d.get("tam_trang") if l == "nhac" else d.get("dung_khi")
        print(f"{'✔ thêm' if that else '• sẽ thêm'} {ma} ({'nhạc' if l == 'nhac' else 'tiếng'}, nhóm {d['nhom']}): {d['mo_ta'][:70]} · {them} → tai-nguyen/{l}/{tep}")
    if not that:
        print("Chưa ghi gì. Học viên OK thì chạy lại với --that.")
        return 0
    gio = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    for l in sorted({k[0] for k in ke_hoach}):
        rows, cols = tho[l]
        f_cm = kho_am.goc(l) / "chi-muc.csv"
        if f_cm.is_file():
            sl = XUONG / ".sao-luu" / gio / "tai-nguyen" / l
            sl.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f_cm, sl / "chi-muc.csv")
        moi = []
        for l2, ma, d, src, tep in ke_hoach:
            if l2 != l:
                continue
            dich = kho_am.goc(l) / tep
            dich.parent.mkdir(parents=True, exist_ok=True)
            if src.suffix.lower() == dich.suffix.lower():
                shutil.copy2(src, dich)
            else:
                ma_hoa = ["-c:a", "libmp3lame", "-b:a", "192k"] if dich.suffix == ".mp3" else ["-c:a", "pcm_s16le"]
                subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(src), "-vn", *ma_hoa, str(dich)], check=True)
            giay = kho_am.do_dai(dich) or 0
            kb, _ = kbps(dich)
            r = {**{k: v for k, v in d.items() if k not in ("tep", "slug")}, "ma": ma, "loai": l, "tep": tep, "xem_truoc": "",
                 "thong_so": (f"{kb}kbps;" if kb else "") + f"{giay:.0f}s" if l == "nhac" else f"{giay:.2f}s",
                 "chu": "hoc-vien", "goi": "", "ngay_them": datetime.date.today().isoformat(), "trang_thai": "dung"}
            moi.append(r)
        for c in [k for r in moi for k in r]:
            if c not in cols:
                cols.append(c)
        tam = f_cm.with_suffix(".csv.tam")
        f_cm.parent.mkdir(parents=True, exist_ok=True)
        with tam.open("w", encoding="utf-8-sig", newline="") as g:
            w = csv.DictWriter(g, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows + moi)
        tam.replace(f_cm)
        md = kho_am.goc(l) / "CHI_MUC.md"
        cu = md.read_text(encoding="utf-8") if md.is_file() else ""
        if "## Của riêng học viên" not in cu:
            cu += "\n## Của riêng học viên\n"
        dong = [f"- `{r['ma']}` ({r['nhom']}) {r['mo_ta']}" + (f" · tâm trạng: {r.get('tam_trang', '')} · hợp: {r.get('hop_video', '')}"
                                                                if l == "nhac" else f" · dùng khi: {r.get('dung_khi', '')} · điểm nhấn {r.get('diem_nhan_s', '')} s")
                for r in moi]
        md.write_text(cu.rstrip("\n") + "\n" + "\n".join(dong) + "\n", encoding="utf-8")
    print(f"✔ Đã thêm {len(ke_hoach)} tệp. Chỉ mục cũ cất ở .sao-luu/{gio}/. Gọi bằng mã (ghi vào nhac.txt, hoặc 'am' của cảnh).")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("viec", choices=["do", "ghi"])
    ap.add_argument("tep", nargs="+")
    ap.add_argument("--that", action="store_true", help="ghi thật (chỉ sau khi học viên OK)")
    a = ap.parse_args()
    if not XUONG:
        sys.exit("✘ Chưa cài Xưởng Video AI: hãy chạy lại câu lệnh cài Xưởng Video AI.")
    if a.viec == "do":
        kq = [do(Path(t)) for t in a.tep]
        print(json.dumps(kq, ensure_ascii=False, indent=1))
        print("\nTừ điển tâm trạng:", ", ".join(kho_am.TAM_TRANG), "| sức:", ", ".join(kho_am.TU_DIEN["nang_luong"]),
              "| hợp video:", ", ".join(kho_am.TU_DIEN["hop_video"]), "| nhóm tiếng:", ", ".join(kho_am.TU_DIEN["nhom_am"]),
              "| giấy phép:", ", ".join(kho_am.TU_DIEN["giay_phep_dung_duoc"]) + ", chua-ro")
        return 0
    return ghi(a.tep[0], a.that)


if __name__ == "__main__":
    sys.exit(main())
