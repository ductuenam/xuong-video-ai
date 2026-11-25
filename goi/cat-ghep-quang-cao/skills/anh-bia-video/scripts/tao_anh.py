"""Tạo ảnh bằng Nano Banana qua API, có gắn ảnh tham chiếu giữ mặt.
  python tao_anh.py <thư mục dự án> --prompt "<prompt>" --ra public/bia-nen [--so 1] [--co 2K] [--ti-le 9:16] [--khong-mat]
Đọc trường anhAI và anhThamChieu trong ho-so-kenh.json. Đổi tài khoản: chỉ sửa anhAI, không sửa code.
  anhAI = {"kieu": "vertex", "khoa": "<đường dẫn file khóa service account>", "project": "<project id>", "model": "gemini-nano-banana-2.1"}
Không ghi nội dung khóa vào hồ sơ, chỉ ghi đường dẫn. Mã thoát 1 nghĩa là API từ chối hoặc không trả ảnh."""
import argparse
import base64
import json
import mimetypes
import sys
import time
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GIA_VAO, GIA_ANH_2K = 1.5 / 1e6, 0.0504  # USD theo bảng giá 11/2026, chỉ để ước tính
mimetypes.add_type("image/webp", ".webp")


def tim_ho_so(da):
    for x in [da, *da.parents]:
        f = x / "ho-so-kenh.json"
        if f.exists():
            return x, json.loads(f.read_text(encoding="utf-8"))
    sys.exit("✘ Không thấy ho-so-kenh.json ở dự án hoặc thư mục cha.")


def dau_cuoi_vertex(cfg):
    creds = service_account.Credentials.from_service_account_file(cfg["khoa"], scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    url = f"https://aiplatform.googleapis.com/v1/projects/{cfg['project']}/locations/global/publishers/google/models/{cfg['model']}:generateContent"
    return url, {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("du_an")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--ra", required=True, help="đường dẫn ra, tính từ dự án, không cần đuôi")
    ap.add_argument("--so", type=int, default=1)
    ap.add_argument("--co", default="2K")
    ap.add_argument("--ti-le", default="9:16")
    ap.add_argument("--khong-mat", action="store_true", help="không gắn ảnh tham chiếu")
    a = ap.parse_args()
    da = Path(a.du_an).resolve()
    goc, h = tim_ho_so(da)
    cfg = h.get("anhAI")
    if not cfg:
        sys.exit("✘ Hồ sơ kênh chưa có anhAI.")
    if cfg["kieu"] != "vertex":
        sys.exit(f"✘ Chưa hỗ trợ kiểu {cfg['kieu']}, cần viết thêm phần gọi API cho kiểu này.")
    parts = []
    if not a.khong_mat:
        for p in h.get("anhThamChieu", []):
            f = Path(p) if Path(p).is_absolute() else goc / p
            parts.append({"inlineData": {"mimeType": mimetypes.guess_type(f.name)[0], "data": base64.b64encode(f.read_bytes()).decode()}})
    parts.append({"text": a.prompt})
    than = {"contents": [{"role": "USER", "parts": parts}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": a.ti_le, "imageSize": a.co}}}
    url, dau = dau_cuoi_vertex(cfg)
    ra = da / a.ra
    ra.parent.mkdir(parents=True, exist_ok=True)
    co_loi = False
    for i in range(a.so):
        for cho in (30, 60, 120, 180, 0):  # 429 là hết hạn mức tạm thời của Google, chờ rồi thử lại
            r = requests.post(url, headers=dau, json=than, timeout=300)
            if r.status_code != 429 or not cho:
                break
            print(f"  hết hạn mức tạm thời, chờ {cho} giây")
            time.sleep(cho)
        if r.status_code != 200:
            print(f"✘ Lần {i + 1}: HTTP {r.status_code}: {r.text[:500]}")
            co_loi = True
            continue
        d = r.json()
        anh = [p["inlineData"] for c in d.get("candidates", []) for p in c.get("content", {}).get("parts", []) if "inlineData" in p]
        if not anh:
            ly_do = [c.get("finishReason") for c in d.get("candidates", [])]
            print(f"✘ Lần {i + 1}: không có ảnh. Lý do: {ly_do} {json.dumps(d.get('promptFeedback', {}), ensure_ascii=False)[:300]}")
            co_loi = True
            continue
        duoi = ".png" if "png" in anh[0]["mimeType"] else ".jpg"
        ten = ra.parent / (ra.name + (f"-{i + 1}" if a.so > 1 else "") + duoi)
        ten.write_bytes(base64.b64decode(anh[0]["data"]))
        print(f"✔ {ten} {json.dumps(d.get('usageMetadata', {}).get('totalTokenCount', '?'))} token")
    sys.exit(1 if co_loi else 0)


if __name__ == "__main__":
    main()
