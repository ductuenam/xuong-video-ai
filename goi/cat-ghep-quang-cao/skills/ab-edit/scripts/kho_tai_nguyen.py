"""Lập danh mục kho tài nguyên dựng video (nhạc, SFX, video cảnh trám, font, icon) và ghi thành ghi chú Obsidian.
Chỉ đọc kho, không sửa/xoá gì trong kho. Thêm tài nguyên mới vào kho rồi chạy lại là danh mục tự cập nhật.
  python kho_tai_nguyen.py            # quét + ghi ghi chú vào vault
  python kho_tai_nguyen.py --in       # chỉ in tóm tắt, không ghi
Đường dẫn lấy từ config.json: kho_tai_nguyen, obsidian_vault, obsidian_thu_muc.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SKILL = Path(__file__).resolve().parent.parent
CFG = json.loads((SKILL / "config.json").read_text(encoding="utf-8"))
KHO = Path(CFG["kho_tai_nguyen"])
VAULT = Path(CFG["obsidian_vault"])
RA = VAULT / CFG.get("obsidian_thu_muc", "00-Inbox/AI/Claude/Kho tai nguyen video")
CACHE = SKILL / ".cache" / "kho_tai_nguyen.json"

AUDIO = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
VIDEO = {".mp4", ".mov", ".webm", ".mkv"}
FONT = {".ttf", ".otf"}
BO_QUA = {".git", "node_modules", "__pycache__", ".github"}
NHAC_TOI_THIEU = 30  # audio dài hơn 30s coi là nhạc nền, ngắn hơn là SFX

# Nhận diện nguồn + bản quyền theo từ khoá trong đường dẫn (chữ thường). Thứ tự = ưu tiên.
NGUON = [
    (("snaptik", "fsave", "xu hướng"), "TikTok/Reels tải về", "⛔ Có bản quyền của người khác — chỉ tham khảo, KHÔNG ghép vào video ads"),
    (("nhạc facebook",), "Facebook Sound Collection", "⚠️ Chỉ dùng cho video đăng Facebook/Instagram"),
    (("youtube-music",), "YouTube Audio Library", "⚠️ Tự do trên YouTube; một số bài yêu cầu ghi nguồn — kiểm tra trước khi đăng nền tảng khác"),
    (("mixkit",), "Mixkit", "✅ Mixkit Free License — dùng thương mại, không cần ghi nguồn"),
    (("pixabay", "pixapay"), "Pixabay", "✅ Pixabay Content License — dùng thương mại miễn phí"),
    (("pexels",), "Pexels", "✅ Pexels License — dùng thương mại miễn phí"),
    (("kho-am-thanh-113",), "Gói SFX 113 file (chưa rõ nguồn)", "❓ Chưa rõ nguồn — hỏi lại nơi tải trước khi chạy ads"),
]
THU_VIEN = {  # font/icon: tên thư mục chứa (viết liền, chữ thường) → (mô tả, giấy phép). Thứ tự = ưu tiên.
    "bevietnampro": ("Be Vietnam Pro — font tiếng Việt, phụ đề/nhãn", "SIL OFL"),
    "montserrat": ("Montserrat — tiêu đề/hook", "SIL OFL"),
    "oswald": ("Oswald — chữ đứng, hẹp", "SIL OFL"),
    "plusjakarta": ("Plus Jakarta Sans — giao diện hiện đại", "SIL OFL"),
    "barlow": ("Barlow (+Condensed) — số liệu, nhãn", "SIL OFL"),
    "inter": ("Inter — giao diện/UI", "SIL OFL"),
    "manrope": ("Manrope — giao diện", "SIL OFL"),
    "lucide": ("Lucide — icon nét mảnh (có lucide-react)", "ISC"),
    "phosphor": ("Phosphor — icon 6 độ dày", "MIT"),
    "fluentemojianimated": ("Fluent Emoji động (PNG động)", "MIT"),
    "fluentemoji": ("Microsoft Fluent Emoji 3D/flat/màu (SVG/PNG)", "MIT"),
    "linemd": ("Line MD — icon nét có hiệu ứng vẽ (SVG động)", "MIT"),
    "meteocons": ("Meteocons — icon thời tiết động (Lottie JSON)", "MIT"),
}
LA_SFX = ("sfx", "sound effect", "kho-am-thanh")      # thư mục SFX → luôn xếp vào SFX dù file dài
LA_NHAC = ("nhạc", "music", "xu hướng")                # thư mục nhạc/âm thanh trend → luôn xếp vào nhạc


def nguon(rel, ten_file=()):
    s = (rel + " " + " ".join(ten_file)).lower()
    for kw, ten, bq in NGUON:
        if any(k in s for k in kw):
            return ten, bq
    return "Chưa rõ", "❓ Chưa rõ nguồn"


def gon(s):
    return "".join(c for c in s.lower() if c.isalnum())


def thu_vien(rel):
    s = gon(rel)
    for kw, v in THU_VIEN.items():
        if kw in s:
            return v
    return ("", "")


def la_nhac(m):
    thu_muc = str(Path(m[0]).parent).lower()
    if any(k in thu_muc for k in LA_SFX):
        return False
    return any(k in thu_muc for k in LA_NHAC) or (m[3].get("giay") or 0) > NHAC_TOI_THIEU


def rut_gon(nhom):
    """Đường dẫn thư mục → tên ngắn: bỏ hậu tố tải về Google Drive."""
    return "/".join(p.split("-2026")[0] for p in nhom.split("/"))


def tim_ffprobe():
    p = shutil.which("ffprobe")
    if not p:
        sys.exit("Không thấy ffprobe trong PATH")
    return p


def do_media(ffprobe, f):
    r = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                        "-of", "json", str(f)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        j = json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"loi": True}
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), None)
    return {"giay": round(float(j.get("format", {}).get("duration", 0) or 0), 1),
            "w": v.get("width") if v else None, "h": v.get("height") if v else None}


def quet():
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    cu = set(cache.get("files", {}))
    ffprobe = tim_ffprobe()
    files, media, font, icon, zips, tong = {}, [], defaultdict(list), defaultdict(Counter), [], [0, 0]
    for dp, dn, fn in os.walk(KHO):
        dn[:] = [d for d in dn if d not in BO_QUA]
        for n in fn:
            p = Path(dp) / n
            rel = p.relative_to(KHO).as_posix()
            ext = p.suffix.lower()
            try:
                st = p.stat()
            except OSError:
                continue
            tong[0] += 1
            tong[1] += st.st_size
            phan = rel.split("/")
            goc = "/".join(phan[:2]) if len(phan) > 2 else phan[0]
            if ext in AUDIO or ext in VIDEO:
                khoa = f"{st.st_size}-{int(st.st_mtime)}"
                c = cache.get("files", {}).get(rel)
                info = c["info"] if c and c.get("khoa") == khoa else do_media(ffprobe, p)
                files[rel] = {"khoa": khoa, "info": info}
                media.append((rel, ext, st.st_size, info))
            elif ext in FONT:
                font[goc].append(n)
            elif ext in {".svg", ".json", ".png", ".gif", ".webp"}:
                icon[goc][ext] += 1
            elif ext == ".zip":
                zips.append((rel, st.st_size, p.with_suffix("").exists()))
    moi = sorted(set(files) - cu) if cu else []
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps({"files": files, "ngay": dt.date.today().isoformat()}, ensure_ascii=False), encoding="utf-8")
    return media, font, icon, zips, tong, moi


def phut(g):
    g = int(round(g or 0))
    return f"{g // 60}:{g % 60:02d}"


def mb(b):
    return f"{b / 1e6:,.0f} MB" if b < 1e9 else f"{b / 1e9:,.2f} GB"


def ten_dep(rel):
    s = Path(rel).stem.removesuffix(" (1)")
    for bo in ("mixkit-", " Free Stock Video", "FSave.com_", "snaptik.vn_"):
        s = s.replace(bo, "")
    s = s.rsplit("-", 1)[0] if s.split("-")[-1].isdigit() else s
    p = s.split("-", 2)  # gói 113: "click-032-camera-shutter" → "camera-shutter"
    return p[2] if len(p) == 3 and p[1].isdigit() else s


def fm(type_, summary, tags):
    return (f"---\ntype: {type_}\nsummary: \"{summary}\"\nstatus: review\ntags: [{', '.join(tags)}]\n"
            f"source: \"Quét tự động {KHO} bằng ab-edit/scripts/kho_tai_nguyen.py\"\n"
            f"created_by: Claude\nconfidence: high\nupdated: {dt.date.today().isoformat()}\n---\n\n")


HUB = "Kho tai nguyen video - Tong quan"
DAU = (f"> Ghi chú **tự sinh** — đừng sửa tay (lần chạy sau sẽ ghi đè). Muốn thêm ghi chú riêng: viết vào [[{HUB}]] phần *Ghi chú riêng*.\n"
       f"> Kho: `{KHO}` · quét {dt.datetime.now():%d/%m/%Y %H:%M}\n\n")


NHAC_PT = SKILL / ".cache" / "nhac_phan_tich.json"   # thẻ nhạc do phan_tich_nhac.py sinh
ICON_LOI = {"khong": "🎻", "nghi": "❓", "co": "🎤"}
NHAC = "Kho tai nguyen video - Nhac nen"


def ghi_chu_nhac(nhac):
    """→ {tên ghi chú: nội dung}: 1 ghi chú tổng (gợi ý chọn nhanh) + 1 ghi chú mỗi nguồn nhạc (bảng thẻ nhạc)."""
    pt = json.loads(NHAC_PT.read_text(encoding="utf-8")) if NHAC_PT.exists() else {}
    dbs = sorted(t["db"] for t in pt.values())
    nguong = (dbs[len(dbs) // 3], dbs[2 * len(dbs) // 3]) if len(dbs) >= 3 else (-99, 99)
    nang = lambda t: "êm" if t["db"] < nguong[0] else "mạnh" if t["db"] > nguong[1] else "vừa"   # so tương đối trong kho
    notes, tong_ket, goi_y = {}, [], defaultdict(list)
    for nhom, ds in sorted(gom(nhac).items()):
        ten, bq = nguon(nhom, [r for r, *_ in ds])
        tieu = f"{NHAC} - " + rut_gon(nhom).split("/")[-1][:40]
        dem = Counter(pt.get(r, {}).get("loi", "chua") for r, *_ in ds)
        out = [fm("nguon", f"Thẻ nhạc {len(ds)} bài nguồn {ten}: có lời hay không, nhịp, cảm xúc, nhạc cụ, năng lượng, hợp cho video nào.",
                  ["auto-video", "video", "nguon"]), f"# {tieu}\n\nThuộc [[{NHAC}]] · nguồn: {ten} · {bq}\n\n", DAU,
               "| Bài | Dài | Lời | Nhịp | Cảm xúc · nhạc cụ | Năng lượng | Hợp cho |\n|---|---|---|---|---|---|---|\n"]
        for rel, ext, sz, info in sorted(ds):
            t = pt.get(rel)
            if not t:
                out.append(f"| {ten_dep(rel)} | {phut(info.get('giay'))} | — | | chưa phân tích | | |\n")
                continue
            out.append(f"| {ten_dep(rel)} | {phut(info.get('giay'))} | {ICON_LOI[t['loi']]} | {t['bpm']} {t['nhip']} | "
                       f"{', '.join(t['cam_xuc'])} · {', '.join(t['nhac_cu'][:2])} | `{t['vach']}` {nang(t)} | {t['goi_y'][0]} |\n")
            if t["loi"] == "khong" and (info.get("giay") or 0) >= 45:
                for g in t["goi_y"]:
                    goi_y[g].append((rel, info.get("giay"), t, ten))
        notes[tieu] = "".join(out)
        tong_ket.append(f"| [[{tieu}]] | {ten} | {len(ds)} | {dem['khong']} | {dem['nghi']} | {dem['co']} | {dem['chua']} |\n")
    hub = [fm("muc-luc", "Tổng hợp nhạc nền trong kho: bao nhiêu bài không lời, gợi ý chọn nhanh theo loại video, bài có lời cần tránh.",
              ["auto-video", "video", "muc-luc", "nguon"]), f"# {NHAC}\n\nThuộc [[{HUB}]]\n\n", DAU,
           "Luật skill: **nhạc nền luôn không lời**. Thẻ nhạc do máy \"nghe\" (`phan_tich_nhac.py`): mô hình AudioSet nhận giọng hát/nhạc cụ/cảm xúc, "
           "Whisper nghe lời, librosa đo nhịp & năng lượng. 🎻 không lời · ❓ nghi có giọng (nghe thử) · 🎤 có lời (không dùng làm nhạc nền). "
           "Máy chấm vẫn có thể sai — bài quan trọng anh nghe lại.\n\n",
           "| Nguồn | Bản quyền | Bài | 🎻 | ❓ | 🎤 | chưa chấm |\n|---|---|---|---|---|---|---|\n", *tong_ket,
           "\n## Gợi ý chọn nhanh (🎻 không lời, dài ≥ 45s)\n"]
    for g, ds in sorted(goi_y.items(), key=lambda x: -len(x[1])):
        ds = sorted(ds, key=lambda x: -(x[1] or 0))[:8]
        hub.append(f"**{g}** ({len(goi_y[g])} bài): " + " · ".join(f"{ten_dep(r)} ({phut(s)}, {t['bpm']}bpm)" for r, s, t, _ in ds) + "\n\n")
    return {NHAC: "".join(hub), **notes}


def ghi_chu_sfx(sfx):
    out = [fm("nguon", f"Danh sách {len(sfx)} hiệu ứng âm thanh (SFX) trong kho tài nguyên video, gom theo nhóm và nguồn.",
              ["auto-video", "video", "nguon"]), "# Kho tai nguyen video - Hieu ung am thanh\n\n", DAU,
           "Mức âm tham khảo khi trộn: SFX −12…−16 dB so với giọng.\n\n"]
    goi = defaultdict(lambda: defaultdict(list))  # gói (2 cấp đầu) → thư mục con → file
    for x in sfx:
        phan = Path(x[0]).parent.as_posix().split("/")
        goi["/".join(phan[:2])]["/".join(phan[2:])].append(x[0])
    ten_trung = Counter(t for t in {(Path(x[0]).parent.as_posix(), ten_dep(x[0])) for x in sfx} for t in [t[1]])
    for g, con in sorted(goi.items()):
        tat_ca = [r for ds in con.values() for r in ds]
        ten, bq = nguon(g, tat_ca)
        out.append(f"## {rut_gon(g)} — {len(tat_ca)} file\n{ten} · {bq}\n\n")
        for c, ds in sorted(con.items()):
            tens = " · ".join(sorted({ten_dep(r) for r in ds}))
            out.append(f"- **{c}** ({len(ds)}): {tens}\n" if c else f"{tens}\n")
        out.append("\n")
    trung = sum(1 for n, k in ten_trung.items() if k > 1)
    if trung:
        out.append(f"> {trung} tên hiệu ứng có mặt ở hơn 1 thư mục — nhiều khả năng cùng 1 file chép sang nhiều nơi.\n")
    return "".join(out)


def ghi_chu_video(vid):
    out = [fm("nguon", f"Danh sách {len(vid)} video cảnh trám/overlay trong kho tài nguyên, có khổ dọc/ngang, độ phân giải và thời lượng.",
              ["auto-video", "video", "nguon"]), "# Kho tai nguyen video - Video canh tram\n\n", DAU]
    for nhom, ds in sorted(gom(vid).items()):
        ten, bq = nguon(nhom, [r for r, *_ in ds])
        out.append(f"## {rut_gon(nhom)} — {len(ds)} clip\n{ten} · {bq}\n\n| Clip | Khổ | Độ phân giải | Dài |\n|---|---|---|---|\n")
        for rel, ext, sz, info in sorted(ds):
            w, h = info.get("w"), info.get("h")
            kho = "chỉ tiếng" if not w else ("dọc" if h > w else "ngang" if w > h else "vuông")
            out.append(f"| {ten_dep(rel)} | {kho} | {f'{w}×{h}' if w else '—'} | {phut(info.get('giay'))} |\n")
        out.append("\n")
    return "".join(out)


def ghi_chu_font_icon(font, icon, cai_win):
    out = [fm("nguon", "Font chữ, bộ icon tĩnh/động và emoji trong kho tài nguyên video, kèm giấy phép và tình trạng cài trên Windows.",
              ["auto-video", "video", "thiet-ke", "nguon"]), "# Kho tai nguyen video - Font icon emoji\n\n", DAU,
           "## Font chữ\nChốt dùng (12/10/2026): **Montserrat Black** cho tiêu đề/hook, **Be Vietnam Pro Black** cho phụ đề/nhãn tiếng Việt.\n\n"
           "| Bộ font | Dùng cho | Số file TTF/OTF | Giấy phép | Cài Windows |\n|---|---|---|---|---|\n"]
    for goc, ds in sorted(font.items()):
        mota, gp = thu_vien(goc)
        ten = goc.split("/")[-1]
        cai = "✔" if any(Path(n).stem.lower().split("-")[0] in cai_win for n in ds) else "✘"
        out.append(f"| {ten} | {mota or '—'} | {len(ds)} | {gp or '❓'} | {cai} |\n")
    out.append("\n## Icon & emoji\n| Bộ | Mô tả | SVG | JSON | PNG | Giấy phép |\n|---|---|---|---|---|---|\n")
    for goc, c in sorted(icon.items()):
        if sum(c.values()) < 20 or goc in font:
            continue
        mota, gp = thu_vien(goc)
        out.append(f"| {goc} | {mota or '—'} | {c['.svg']:,} | {c['.json']:,} | {c['.png']:,} | {gp or '❓'} |\n")
    out.append("\nSố SVG của Line MD/Fluent tính cả file nguồn trong repo, số icon dùng được thực tế ít hơn.\n")
    return "".join(out)


def gom(ds):
    g = defaultdict(list)
    for x in ds:
        g[str(Path(x[0]).parent.as_posix())].append(x)
    return g


def ghi_chu_hub(nhac, sfx, vid, font, icon, zips, tong, moi):
    cu = (RA / f"{HUB}.md")
    rieng = "- (anh ghi thêm vào đây — phần này được giữ nguyên khi chạy lại)\n"
    if cu.exists():
        t = cu.read_text(encoding="utf-8")
        if "## Ghi chú riêng" in t:
            rieng = t.split("## Ghi chú riêng", 1)[1].split("\n## ", 1)[0].strip("\n") + "\n"
    ss = lambda ds: sum(x[2] for x in ds)
    gio = lambda ds: phut(sum(x[3].get("giay") or 0 for x in ds))
    doc = sum(1 for x in vid if x[3].get("h") and x[3]["h"] > x[3]["w"])
    out = [fm("muc-luc", "Mục lục kho tài nguyên dựng video (config.json › kho_tai_nguyen): nhạc nền, SFX, video cảnh trám, font, icon — số lượng, bản quyền, cách cập nhật.",
              ["auto-video", "video", "muc-luc", "nguon"]),
           f"# {HUB}\n\n", DAU,
           f"**Tổng:** {tong[0]:,} file · {mb(tong[1])}\n\n",
           "| Loại | Số lượng | Dung lượng | Chi tiết |\n|---|---|---|---|\n",
           f"| Nhạc nền (>{NHAC_TOI_THIEU}s) | {len(nhac)} bài · tổng {gio(nhac)} | {mb(ss(nhac))} | [[Kho tai nguyen video - Nhac nen]] |\n",
           f"| Hiệu ứng âm thanh | {len(sfx)} file | {mb(ss(sfx))} | [[Kho tai nguyen video - Hieu ung am thanh]] |\n",
           f"| Video cảnh trám/overlay | {len(vid)} clip ({doc} dọc, {len(vid) - doc} ngang) | {mb(ss(vid))} | [[Kho tai nguyen video - Video canh tram]] |\n",
           f"| Font | {len(font)} bộ · {sum(len(v) for v in font.values())} file | | [[Kho tai nguyen video - Font icon emoji]] |\n",
           f"| Icon/emoji | {len([c for c in icon.values() if sum(c.values()) >= 20])} bộ · {sum(c['.svg'] for c in icon.values()):,} SVG | | [[Kho tai nguyen video - Font icon emoji]] |\n\n",
           "## Bản quyền theo nguồn\n"]
    for kw, ten, bq in NGUON:
        out.append(f"- **{ten}**: {bq}\n")
    out.append("- **Font** (SIL OFL) và **icon** (MIT/ISC): dùng thương mại được.\n\n")
    if moi:
        out.append(f"## Mới thêm từ lần quét trước ({len(moi)})\n" + "".join(f"- `{m}`\n" for m in moi[:40])
                   + (f"- … và {len(moi) - 40} file nữa\n" if len(moi) > 40 else "") + "\n")
    trung = [z for z in zips if z[2]]
    if trung:
        out.append("## Có thể dọn (anh tự quyết, em không xoá)\nFile zip đã giải nén cạnh thư mục cùng tên:\n"
                   + "".join(f"- `{r}` ({mb(s)})\n" for r, s, _ in trung) + "\n")
    out.append("## Cách cập nhật\n1. Chép tài nguyên mới vào thư mục kho tài nguyên (mỗi nguồn 1 thư mục, tên thư mục có tên nguồn: mixkit, pixabay, pexels…).\n"
               "2. Nhắn Claude *\"cập nhật kho tài nguyên\"* — hoặc tự chạy `python \"%USERPROFILE%\\.claude\\skills\\ab-edit\\scripts\\kho_tai_nguyen.py\"`.\n"
               "3. Các ghi chú này tự ghi đè; phần *Ghi chú riêng* bên dưới được giữ lại.\n\n")
    out.append("## Ghi chú riêng\n" + rieng)
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="chi_in", action="store_true")
    a = ap.parse_args()
    if not KHO.is_dir():
        sys.exit(f"Không thấy kho: {KHO}")
    media, font, icon, zips, tong, moi = quet()
    am = [m for m in media if m[1] in AUDIO or (m[1] in VIDEO and not m[3].get("w"))]
    nhac = [m for m in am if la_nhac(m)]
    sfx = [m for m in am if m not in nhac]
    vid = [m for m in media if m[1] in VIDEO and m[3].get("w")]
    fdirs = [Path("C:/Windows/Fonts"), Path.home() / "AppData/Local/Microsoft/Windows/Fonts"]
    cai_win = {f.stem.lower().split("-")[0] for d in fdirs if d.exists() for f in d.iterdir()}
    print(f"{tong[0]:,} file · {mb(tong[1])} | nhạc {len(nhac)} · sfx {len(sfx)} · video {len(vid)} · font {len(font)} bộ · mới {len(moi)}")
    if a.chi_in:
        return
    RA.mkdir(parents=True, exist_ok=True)
    notes = {
        HUB: ghi_chu_hub(nhac, sfx, vid, font, icon, zips, tong, moi),
        **ghi_chu_nhac(nhac),
        "Kho tai nguyen video - Hieu ung am thanh": ghi_chu_sfx(sfx),
        "Kho tai nguyen video - Video canh tram": ghi_chu_video(vid),
        "Kho tai nguyen video - Font icon emoji": ghi_chu_font_icon(font, icon, cai_win),
    }
    for ten, nd in notes.items():
        (RA / f"{ten}.md").write_text(nd, encoding="utf-8")  # utf-8 không BOM theo luật vault
        print(f"  ✔ {ten}.md — {len(nd):,} ký tự" + ("  ⚠ >12.000" if len(nd) > 12000 else ""))
    print(f"→ {RA}")


if __name__ == "__main__":
    main()
