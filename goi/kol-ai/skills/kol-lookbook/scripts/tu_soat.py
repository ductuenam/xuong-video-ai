"""Cổng tự soát TRƯỚC khi gọi 3 agent chấm (mỗi lỗi ở đây từng làm mất điểm ở các video mẫu).

Dùng:
  python tu_soat.py ke-hoach.json            # soát kế hoạch + clip nguồn (chạy TRƯỚC khi dựng, nhanh)
  python tu_soat.py ke-hoach.json --video    # thêm soát thành phẩm "ra" trong kế hoạch (sau khi dựng)

Kiểm (mỗi dòng LỖI là lỗi đã từng bị agent trừ điểm):
  1. Tổng hình ≤ nhạc còn lại sau nhac_tu (hình dài hơn nhạc → nhạc lặp ở cuối).
  2. Mỗi cảnh là số NGUYÊN phách (nửa phách bị chấm lệch nhịp) và ≥ 1,5 giây, trừ cảnh cuối.
  3. Điểm vào không nằm trong khúc đứng yên đầu clip (Muse hay đứng yên 2–5 khung đầu).
  4. Ảnh góc: ước phần trăm hộp ảnh góc nằm đè lên người/áo trong clip nguồn (so với màu nền ở mép phải).
     > 20% là LỖI (bản đạt ở 12%) (video mẫu 2: ma-nơ-canh đè vạt măng tô, che giày, chìm vào áo cùng màu).
  5. (--video) Khung gần trùng nhau trong thành phẩm (khựng 1 khung sau cú cắt).
  6. Xuất tờ mắt ở đầu/cuối mọi cảnh có mặt → <thư mục tạm>/mat-diem-cat.jpg để người dựng xem bằng mắt.
In ra "ĐẠT" hoặc danh sách LỖI; mã thoát 1 nếu có LỖI.
"""
import argparse, io, json, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

PHACH = 0.46875  # mặc định; kế hoạch có "phach" thì dùng giá trị đó
sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import cau_hinh
TAM = Path(cau_hinh()["thu_muc_tam"])


def do_dai(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, timeout=60)
    return float(r.stdout.strip())


def khung(clip, t, w=1080, h=1920):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", str(clip), "-frames:v", "1",
                        "-vf", f"scale={w}:{h}", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, timeout=60).stdout
    return Image.open(io.BytesIO(b)).convert("RGB")


def dung_yen_dau(clip, n=12):
    """Số khung đầu clip gần như đứng yên (độ khác < 0,4 trên ảnh thu nhỏ xám)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-frames:v", str(n), "-vf", "scale=108:192,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, timeout=60).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, 192, 108).astype(float)
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    k = 0
    for x in d:
        if x < 0.4: k += 1
        else: break
    return k


def hop_goc(goc, p, cao, vt):
    im = Image.open(goc / p).convert("RGBA"); im = im.crop(im.getbbox())
    h = int(1920 * cao); w = int(im.width * h / im.height)
    x0 = 1080 - w - 40; y0 = int(1920 * 0.06) if vt == "tren" else 1920 - h - int(1920 * 0.03)
    return x0, y0, x0 + w, y0 + h


def phu_nguoi(im, hop):
    """Tỉ lệ điểm ảnh trong hộp khác màu nền (nền = trung vị từng hàng của dải 16 px sát mép phải)."""
    a = np.asarray(im).astype(int); x0, y0, x1, y1 = hop
    nen = np.median(a[:, -16:, :], axis=1)  # mỗi hàng một màu nền
    vung = a[y0:y1, x0:x1, :]; nen_v = nen[y0:y1][:, None, :]
    lech = np.abs(vung - nen_v).sum(axis=2)
    return float((lech > 60).mean())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ke_hoach"); ap.add_argument("--video", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    kp = Path(a.ke_hoach); goc = kp.parent; kh = json.loads(kp.read_text(encoding="utf-8"))
    loi, ghi = [], []
    doan = kh["doan"]; cao_chung = kh.get("goc_cao", 0.36)
    # 1. độ dài
    tong = sum(d["den"] - d["tu"] for d in doan)
    con = do_dai(kh["nhac"]) - kh.get("nhac_tu", 0.0)
    (loi if tong > con else ghi).append(f"tổng hình {tong:.2f} giây, nhạc còn {con:.2f} giây")
    # 2. phách, độ dài cảnh
    for i, d in enumerate(doan):
        dai = d["den"] - d["tu"]; ph = dai / kh.get("phach", PHACH)
        if abs(ph - round(ph)) > 0.02: loi.append(f"cảnh {i+1} ({d['clip']}) dài {ph:.2f} phách, không nguyên")
        if dai < 1.5 and i != len(doan) - 1: loi.append(f"cảnh {i+1} dài {dai:.2f} giây < 1,5 (chỉ cảnh cuối được ngắn)")
    # 3. khúc đứng yên đầu clip
    da_do = {}
    for i, d in enumerate(doan):
        c = goc / d["clip"]
        if c not in da_do: da_do[c] = dung_yen_dau(c)
        if d["tu"] < da_do[c] / 24 - 0.002: loi.append(f"cảnh {i+1}: vào {d['tu']} giây nằm trong {da_do[c]} khung đứng yên đầu {d['clip']} (đặt tu ≥ {da_do[c]/24:.3f})")
    # 4. ảnh góc đè người
    if kh.get("nen") == "phong":  # nền trong nhà nhiều chi tiết: mép phải không phải màu nền → phép đo báo sai (video mẫu 3 nền phòng khách)
        ghi.append("bỏ qua đo ảnh góc đè người vì nền trong nhà — PHẢI soát bằng mắt tờ khung đầu/cuối mọi cảnh")
    for i, d in enumerate([] if kh.get("nen") == "phong" else doan):
        p = kh.get("anh_goc", {}).get(str(d.get("bo")))
        if not p: continue
        hop = hop_goc(goc, p, d.get("goc_cao", cao_chung), d.get("goc_vi_tri", "duoi"))
        ts = np.linspace(d["tu"] + 0.05, d["den"] - 0.05, 4)
        pt = max(phu_nguoi(khung(goc / d["clip"], t), hop) for t in ts)
        dong = f"cảnh {i+1} ({d['clip']}, góc {d.get('goc_vi_tri','duoi')} {d.get('goc_cao', cao_chung)}): ảnh góc đè người/áo ~{pt*100:.0f}%"
        (loi if pt > 0.20 else ghi).append(dong + (" → đổi góc trên/dưới hoặc thu nhỏ" if pt > 0.20 else ""))
    # 5. khung gần trùng trong thành phẩm
    if a.video:
        ra = goc / kh["ra"]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ra), "-vf", "scale=108:192,format=gray", "-f", "rawvideo", "-"],
                             capture_output=True, timeout=300).stdout
        f = np.frombuffer(raw, np.uint8).reshape(-1, 192, 108).astype(float); dd = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
        lap = [i + 1 for i, x in enumerate(dd) if x < 0.4]
        (loi if lap else ghi).append(f"khung gần trùng trong thành phẩm: {lap or 'không có'}")
        ghi.append(f"thành phẩm dài {do_dai(ra):.2f} giây")
    # 6. tờ mắt điểm cắt (cảnh có mặt = clip tên chứa 'tien')
    TAM.mkdir(parents=True, exist_ok=True); hang = []
    for i, d in enumerate(doan):
        if "tien" not in Path(d["clip"]).stem: continue
        o = []
        for t in (d["tu"], d["tu"] + 1/24, d["tu"] + 2/24, d["den"] - 2/24, d["den"] - 1/24):
            im = khung(goc / d["clip"], t, 720, 1280); W, H = im.size
            g = np.asarray(im.convert("L")).astype(int); nen = g[5, 5]; top = 0
            for y in range(0, H, 4):
                if (np.abs(g[y, W//4:3*W//4:4] - nen) > 45).sum() > 4: top = y; break
            # bề ngang đầu = rộng nhất trong dải 0..18% chiều cao dưới đỉnh đầu (dòng ngay dưới đỉnh chỉ là chỏm tóc, rất hẹp)
            ws = []
            for y in range(top, min(H - 1, top + int(H * 0.18)), 6):
                xs = np.where(np.abs(g[y, ::2] - nen) > 45)[0] * 2
                if len(xs) > 2: ws.append((xs[-1] - xs[0], (xs[0] + xs[-1]) // 2))
            s, cx = max(ws) if ws else (160, W // 2); s = max(80, int(s))
            y0 = top + int(s*0.28); c = im.crop((cx - int(s*0.45), y0, cx + int(s*0.45), y0 + int(s*0.5))).resize((240, 132))  # mắt nằm ~0,45–0,6 bề ngang đầu dưới đỉnh
            ImageDraw.Draw(c).text((3, 3), f"c{i+1} {t:.2f}", fill="yellow"); o.append(c)
        r = Image.new("RGB", (240 * len(o), 132))
        for k, c in enumerate(o): r.paste(c, (240 * k, 0))
        hang.append(r)
    if hang:
        S = Image.new("RGB", (hang[0].width, 132 * len(hang)))
        for k, r in enumerate(hang): S.paste(r, (0, 132 * k))
        ra_mat = TAM / f"mat-diem-cat-{kp.stem}.jpg"; S.save(ra_mat, quality=88)
        ghi.append(f"tờ mắt điểm cắt (3 khung đầu, 2 khung cuối mỗi cảnh có mặt): {ra_mat}")
    # 7. Mặt lớn nhất mỗi bộ đặt cạnh nhau (video mẫu 3: Muse trôi mặt bộ 2, 3 dài và già hơn ở cuối cảnh tiến; từng cảnh
    #    nhìn riêng thì ổn, chỉ đặt cạnh nhau mới thấy). Khung = cuối cảnh tiến (mặt to nhất). MỞ tờ này trước khi gọi agent.
    mat = []
    neo = kh.get("mat_neo")
    if neo and (goc / neo).exists():
        im = Image.open(goc / neo).convert("RGB"); W, H = im.size; im = im.crop((int(W*0.12), 0, int(W*0.88), int(H*0.75))).resize((360, 407)); mat.append(("neo", im))
    for i, d in enumerate(doan):
        if "tien" not in Path(d["clip"]).stem or i % 3 != 2: continue
        im = khung(goc / d["clip"], d["den"] - 0.1, 720, 1280); W, H = im.size
        c = im.crop((int(W*0.12), 0, int(W*0.88), int(H*0.48))).resize((360, 407))  # cảnh tiến: mặt nằm nửa trên khung
        mat.append((f"bo{d.get('bo')} c{i+1} {d['den']-0.1:.2f}", c))
    if len(mat) > 1:
        S = Image.new("RGB", (360 * len(mat), 407))
        for k, (nhan, c) in enumerate(mat):
            S.paste(c, (360 * k, 0)); ImageDraw.Draw(S).text((360 * k + 4, 4), nhan, fill="yellow")
        ra_so = TAM / f"so-mat-cac-bo-{kp.stem}.jpg"; S.save(ra_so, quality=88)
        ghi.append(f"tờ so mặt các bộ (khung cuối cảnh tiến, đặt cạnh mặt neo) — PHẢI MỞ XEM: {ra_so}")
    for g_ in ghi: print("  ok ", g_)
    for l in loi: print("  LỖI", l)
    print("ĐẠT" if not loi else f"CHƯA ĐẠT: {len(loi)} lỗi")
    sys.exit(1 if loi else 0)


if __name__ == "__main__":
    main()
