"""Đo chữ tiêu đề trên cảnh bằng đúng phông và cỡ chữ của engine, báo dòng nào sẽ tràn xuống dòng.
Chạy trong lap_canh.py trước bước bundle, để khỏi mất một vòng dựng ảnh tĩnh (khoảng 6 phút với video 90 giây).
Đã gặp ở 23-skill-ben-trong: "MÀ KHÔNG ĐƯỢC GỌI?", "3 ĐIỀU HAY HIỂU SAI" trên clip xuống ba dòng che mặt;
"Không đọc hết một lúc" trên nền sáng xuống hai dòng, dòng cam bị thẻ che.
Không tải được phông (mất mạng) thì chỉ cảnh báo, không chặn."""
import json

# Khớp engine/src/MoHinh.tsx: ChuLon (cảnh clip) và TieuDe (cảnh nền sáng)
# "rong" là độ rộng tối đa còn vừa một dòng, đo 13/11/2026 trên 18 tiêu đề đã dựng (23-skill-ben-trong):
# cảnh clip có nền, vừa đến 972px, tràn từ 997px; nền sáng, vừa đến 1000px, tràn từ 1003px.
KIEU_CLIP = {"fontSize": 104, "italic": True, "ls": -1.5, "rong": 1020}
KIEU_CLIP_NEN = {"fontSize": 92, "italic": True, "ls": -1.5, "rong": 985}
KIEU_SANG = {"fontSize": 84, "italic": False, "ls": -1, "rong": 1001}
CANH_CLIP = {"flow-chu", "nguoi-chu", "bieu-tuong"}
KHONG_TIEU_DE = {"nguoi", "nguoi-so", "ket-phe", "ket-comment", "ten-cong-cu", "repo", "terminal"}
SAT = 0.96  # trên 96% độ rộng thì vừa nhưng sát mép: chỉ nhắc


def cac_dong(canh):
    """Danh sách (số cảnh, trường, chữ, kiểu) cần đo."""
    ra = []
    for i, c in enumerate(canh, 1):
        loai = c.get("loai")
        if loai in KHONG_TIEU_DE:
            continue
        if loai in CANH_CLIP:
            kieu = KIEU_CLIP_NEN if (c.get("nen") or loai == "nguoi-chu") else KIEU_CLIP
        else:
            kieu = KIEU_SANG
        for k in ("tren", "duoi"):
            if c.get(k):
                ra.append((i, loai, k, str(c[k]), kieu))
    return ra


def kiem_tieu_de(canh):
    """Trả về (lỗi, cảnh báo)."""
    dong = cac_dong(canh)
    if not dong:
        return [], []
    try:
        from playwright.sync_api import sync_playwright
        html = ("<link href='https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,900;1,900&display=block' rel='stylesheet'>"
                "<body></body>")
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            pg.set_content(html)
            # Phông chia theo bảng chữ (latin, vietnamese): phải nạp kèm chữ có dấu thì mới tải đủ
            pg.wait_for_load_state("networkidle")
            nap = pg.evaluate("""async () => { const m = 'AaĐđỆệỮữ'; const r = await Promise.all([
                document.fonts.load('900 40px Montserrat', m), document.fonts.load('italic 900 40px Montserrat', m)]);
                return r.every((x) => x.length > 0); }""")
            if not nap:
                raise RuntimeError("không nạp được Montserrat")
            do = pg.evaluate("""(ds) => ds.map(([chu, co, nghieng, ls]) => {
                const s = document.createElement('span');
                s.textContent = chu;
                s.style.cssText = `font-family:Montserrat;font-weight:900;font-size:${co}px;letter-spacing:${ls}px;white-space:nowrap;font-style:${nghieng ? 'italic' : 'normal'}`;
                document.body.appendChild(s);
                const w = s.getBoundingClientRect().width; s.remove(); return w; })""",
                [[d[3], d[4]["fontSize"], d[4]["italic"], d[4]["ls"]] for d in dong])
            b.close()
    except Exception as e:  # noqa: BLE001
        return [], [f"chưa đo được độ rộng tiêu đề ({type(e).__name__}), soát kỹ ảnh tĩnh"]
    loi, nhac = [], []
    for (i, loai, k, chu, kieu), w in zip(dong, do):
        if w > kieu["rong"]:
            loi.append(f"cảnh {i} ({loai}) {k} «{chu}» rộng {w:.0f}px, chỗ chỉ {kieu['rong']}px: sẽ xuống dòng. Rút gọn chữ")
        elif w > kieu["rong"] * SAT:
            nhac.append(f"cảnh {i} ({loai}) {k} «{chu}» rộng {w:.0f}px, sát mép {kieu['rong']}px")
    return loi, nhac


if __name__ == "__main__":
    import sys
    from pathlib import Path
    c = json.loads((Path(sys.argv[1]) / "canh.json").read_text(encoding="utf-8"))["canh"]
    l, n = kiem_tieu_de(c)
    print("\n".join(["✘ " + x for x in l] + ["⚠ " + x for x in n]) or "✔ tiêu đề vừa một dòng")
