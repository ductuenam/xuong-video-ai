"""Bóc file quay thành các đảo tiếng để chọn lần nói tốt nhất.
  python boc_loi.py <thư mục dự án>
Đọc doan.json › nguon. Ghi boc-loi-<số>.txt, mỗi dòng: [từ giây - đến giây] lời nghe được.
Lấy điểm vào theo từ đầu tiên nghe được, không lấy theo đảo năng lượng."""
import sys
from pathlib import Path

from chung import doc
from whisper_vi import nghe

KHE = 0.35

da = Path(sys.argv[1])
cfg = doc(da / "doan.json")
goi_y = (da / "goi-y.txt").read_text(encoding="utf-8").strip() if (da / "goi-y.txt").exists() else None
for n, f in enumerate(cfg["nguon"]):
    W = [w for s in nghe(f, goi_y=goi_y) for w in s["words"]]
    dao, hien = [], []
    for w in W:
        if hien and w["start"] - hien[-1]["end"] > KHE:
            dao.append(hien)
            hien = []
        hien.append(w)
    if hien:
        dao.append(hien)
    dong = [f"[{d[0]['start']:.2f} - {d[-1]['end']:.2f}] {''.join(x['word'] for x in d).strip()}" for d in dao]
    (da / f"boc-loi-{n}.txt").write_text("\n".join(dong), encoding="utf-8")
    print(f"nguồn {n}: {len(dao)} đảo tiếng, ghi boc-loi-{n}.txt")
