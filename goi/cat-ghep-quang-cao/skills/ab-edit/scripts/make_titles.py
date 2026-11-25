"""Dựng khối chữ thành clip ProRes 4444 nền trong suốt (lớp trên cùng), font + màu theo thương hiệu. Port từ make-titles.py v2.
  python make_titles.py titles.json --out <thư mục> --brand _mau [--only id1,id2] [--anh 0.5,1.5] [--jobs 3] [--fps 50 --w 1440 --h 1800]
titles.json: [{"id":"t1","kind":"title|serif|hook|badge|stamp|wipe|duo|labels|note|cta","dur":3.2, ...}] (xem references/chuan-dung-video-ads.md mục 5)
--anh: chỉ chụp ảnh PNG tại các giây đó để duyệt nhanh (không quay clip)."""
import argparse
import concurrent.futures as cf
import json
import os
import shutil
import subprocess
from pathlib import Path

from chung import CFG, SKILL, doc_brand, tim_ffmpeg

QUAY = SKILL / "scripts" / "vendor" / "quay-html.mjs"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--only")
    ap.add_argument("--brand")
    ap.add_argument("--anh")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--fps", type=int, default=50)
    ap.add_argument("--w", type=int, default=1440)
    ap.add_argument("--h", type=int, default=1800)
    a = ap.parse_args()
    tpl = (SKILL / "scripts" / "titles" / "template.html").read_text(encoding="utf-8")
    items = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    brand = doc_brand(a.brand).get("chu", {})
    if a.only:
        items = [i for i in items if i["id"] in a.only.split(",")]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, CHROME=CFG.get("chrome", ""), FFMPEG=tim_ffmpeg())
    node = shutil.which("node") or "node"

    def job(it):
        cfg = dict(it, W=a.w, H=a.h, brand=brand)
        html = out / f"{it['id']}.html"
        html.write_text(tpl.replace("/*CFG*/{}/*CFG*/", json.dumps(cfg, ensure_ascii=False)), encoding="utf-8")
        cmd = [node, str(QUAY), "--trang", str(html), "--out", str(out / f"{it['id']}.mov"), "--dur", str(it["dur"]),
               "--w", str(a.w), "--h", str(a.h), "--fps", str(a.fps), "--alpha"]
        if a.anh:
            cmd += ["--anh", a.anh]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        return it["id"], r.returncode, (r.stderr or r.stdout or "")[-400:]

    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for i, rc, err in ex.map(job, items):
            print(("ok   " if rc == 0 else "LỖI ") + i, err.strip() if rc else "")


if __name__ == "__main__":
    main()
