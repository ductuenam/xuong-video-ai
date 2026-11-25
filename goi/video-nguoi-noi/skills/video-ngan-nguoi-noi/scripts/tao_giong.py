"""Tạo giọng đọc qua API Vibi, tải về máy.
  python tao_giong.py <thư mục dự án> --chu-file doc-tts.txt --ra giong
  python tao_giong.py <thư mục dự án> --chu "Một câu" --ra sua-cau-3
  python tao_giong.py <thư mục dự án> --lay "<tên task đã tạo>" --ra giong
Đọc giongAI trong ho-so-kenh.json: {"khoa": "<file chứa API key>", "provider": "minimax", "voice_id": "...", "model": "speech-2.8-hd", "ngon_ngu": "Vietnamese", "toc": 1.09}
Mỗi ký tự 1 credit khi kiểm 06/11/2026. --cam-xuc gửi emotion của MiniMax; đo 07/11/2026 qua Vibi chưa thấy tác dụng, thẻ (laughs), (sighs) cũng bị bỏ. Muốn có cảm xúc thì viết lời có thán từ, dấu chấm than, câu hỏi tu từ. Viết tắt hay đọc sai thì sửa trong bản đọc, phụ đề vẫn theo loi.txt. Không in key ra màn hình.
Trước khi gửi, script tự thay cách đọc trong references/da-chot.json (AI thành Ây‑Ai...) và kiểm luật cảm xúc bằng kiem_chot.py;
sai luật thì dừng, không tốn credit. Chữ thật sự gửi đi lưu ở <ra>.da-gui.txt.
Vibi lỗi 401/403/5xx hoặc mất mạng thì tự chuyển sang giongAI.duPhong (ai33.pro, cùng giọng nhân bản), không đổi giọng khác."""
import argparse
import json
import sys
import time
from pathlib import Path

import requests

from kiem_chot import kiem_doc, loai_du_an, sua_doc

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GOC = "https://api.vibi.pro"


def tim_ho_so(da):
    for x in [da, *da.parents]:
        f = x / "ho-so-kenh.json"
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8"))
    sys.exit("✘ Không thấy ho-so-kenh.json ở dự án hoặc thư mục cha.")


ap = argparse.ArgumentParser()
ap.add_argument("du_an")
ap.add_argument("--chu")
ap.add_argument("--chu-file")
ap.add_argument("--lay", help="không tạo mới, tải task đã có theo tên")
ap.add_argument("--ra", required=True, help="tên file ra, tính từ dự án, không cần đuôi")
ap.add_argument("--toc", type=float)
ap.add_argument("--cam-xuc", choices=["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm", "fluent"], help="cảm xúc cả đoạn; bỏ trống thì máy tự chọn theo lời")
a = ap.parse_args()
da = Path(a.du_an).resolve()
cfg = tim_ho_so(da).get("giongAI")
# Học viên mới (24/11/2026): chưa có giongAI hoặc file khóa Vibi không có thật thì dùng giọng miễn phí, không dừng.
if not cfg or (cfg.get("provider") != "edge" and not Path(str(cfg.get("khoa", ""))).is_file()):
    print("• Chưa có giọng nhân bản (giongAI thiếu hoặc không thấy file khóa): dùng giọng AI miễn phí vi-VN-HoaiMyNeural."
          " Muốn giọng nam đặt giongAI {\"provider\": \"edge\", \"voice_id\": \"vi-VN-NamMinhNeural\"}.")
    cfg = {"provider": "edge", "voice_id": "vi-VN-HoaiMyNeural", "toc": 1.0}
# provider "edge": giọng AI miễn phí của Microsoft (vi-VN-HoaiMyNeural nữ, vi-VN-NamMinhNeural nam), không cần khóa.
# Dùng cho học viên chưa có giọng nhân bản (24/11/2026). Vẫn qua cổng luật đã chốt và ghi .da-gui.txt như giọng trả phí.
MIEN_PHI = cfg.get("provider") == "edge"
dau = {} if MIEN_PHI else {"xi-api-key": Path(cfg["khoa"]).read_text(encoding="utf-8").strip()}


def tai(url, ra):
    r = requests.get(url, headers=dau, timeout=120)
    r.raise_for_status()
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_bytes(r.content)
    print(f"✔ {ra} {len(r.content) // 1024} KB")


ra = da / (a.ra + ".mp3")


def tao_du_phong(chu, ra, ly_do):
    """Vibi lỗi (bảo trì 503, 401, 5xx) thì tạo bằng nguồn dự phòng trong giongAI.duPhong (ai33.pro / OpenSpeaker,
    cùng giọng nhân bản của người dẫn). Thêm 21/11/2026 sau 2 lần Vibi bảo trì MiniMax nhiều giờ trong một ngày."""
    dp = cfg.get("duPhong")
    if not dp:
        sys.exit(f"✘ Vibi lỗi ({ly_do}) và hồ sơ chưa có giongAI.duPhong. Đặt lệnh canh 15 phút rồi thử lại.")
    k = Path(dp["khoa"]).read_text(encoding="utf-8-sig").strip()
    goc = dp.get("api", "https://api.ai33.pro")
    print(f"⚠ Vibi lỗi ({ly_do}), chuyển sang dự phòng {goc} giọng {dp['voice_id']}")
    r = requests.post(f"{goc}/v3/text-to-speech", headers={"xi-api-key": k}, timeout=120,
                      data={"text": chu, "voice_id": dp["voice_id"], "speed": str(a.toc or dp.get("toc", cfg.get("toc", 1.0))),
                            "with_transcript": "false", "file_name": ten_task(a.ra).replace("/", "_")})
    if r.status_code >= 300 or not r.json().get("success"):
        sys.exit(f"✘ Dự phòng cũng lỗi HTTP {r.status_code}: {r.text[:200]}")
    ma = r.json()["task_id"]
    (da / (a.ra + ".task-du-phong.txt")).write_text(ma, encoding="utf-8")
    print(f"đã gửi dự phòng {len(chu)} ký tự, mã {ma}")
    for _ in range(200):
        time.sleep(3)
        t = requests.get(f"{goc}/v1/task/{ma}", headers={"xi-api-key": k}, timeout=60).json()
        if t.get("status") == "done":
            print("credit dự phòng:", t.get("credit_cost"))
            ra.parent.mkdir(parents=True, exist_ok=True)
            b = requests.get(t["metadata"]["audio_url"], timeout=120)
            b.raise_for_status()
            ra.write_bytes(b.content)
            print(f"✔ {ra} {len(b.content) // 1024} KB (nguồn: dự phòng)")
            sys.exit(0)
        if t.get("status") in ("failed", "error"):
            sys.exit(f"✘ Task dự phòng lỗi: {str(t.get('error_message') or t)[:200]}")
    sys.exit("✘ Dự phòng quá 10 phút chưa xong.")

# Tên task trên Vibi kèm tên thư mục dự án: tên trần "giong/ca-bai" trùng giữa các video, --lay từng tải nhầm giọng
# video 27 sang video 28 (21/11/2026).
ten_task = lambda ten: f"{da.name}/{ten}"
if a.lay:
    ds = requests.get(f"{GOC}/v1/history", headers=dau, timeout=60).json()["tasks"]
    t = next((x for x in ds if x.get("name") == ten_task(a.lay) and x.get("status") == "completed"), None)
    if not t:
        sys.exit(f"✘ Không thấy task hoàn thành tên {a.lay}. File trên Vibi tự xóa sau 48 giờ.")
    tai(t["result"]["audio_url"], ra)
    sys.exit(0)

chu = a.chu or (da / a.chu_file).read_text(encoding="utf-8").strip()
# Cổng luật đã chốt (references/da-chot.json): tự thay cách đọc, kiểm cảm xúc. Lỗi thì dừng trước khi tốn credit.
chu, thay = sua_doc(chu)
for t in thay:
    print("  tự thay:", t)
loi_chot = kiem_doc(chu, ca_bai=bool(a.chu_file), gioi_thieu="gioi-thieu" in loai_du_an(da).split())
if a.chu_file:
    from kiem_chot import kiem_ve
    for n in kiem_ve(chu)[1]:
        print("⚠ " + n)
if loi_chot:
    print("\n".join("✘ " + l for l in loi_chot))
    sys.exit("✘ Bản đọc chưa đúng luật đã chốt, chưa gửi. Sửa lời rồi chạy lại.")
ra.parent.mkdir(parents=True, exist_ok=True)
(da / (a.ra + ".da-gui.txt")).write_text(chu, encoding="utf-8")  # đúng chữ đã gửi đi, nghiệm thu đọc lại file này
if MIEN_PHI:
    try:
        import asyncio
        import edge_tts
    except ImportError:
        sys.exit("✘ Chưa có giọng miễn phí: chạy  pip install edge-tts  rồi chạy lại.")
    toc = a.toc or cfg.get("toc", 1.0)
    giong = cfg.get("voice_id") or "vi-VN-HoaiMyNeural"
    # Máy chủ giọng miễn phí hay trả về rỗng (NoAudioReceived) ngẫu nhiên: thử lại tối đa 20 lần (đo 24/11: lỗi theo đợt, 12 lần thử được 5, có lúc hỏng 10 lần liền)
    for lan in range(20):
        try:
            tam = ra.with_suffix(".tam.mp3")
            asyncio.run(edge_tts.Communicate(chu.replace("‑", "-"), giong, rate=f"{round((toc - 1) * 100):+d}%").save(str(tam)))
            tam.replace(ra)  # chỉ ghi file thật khi tạo xong, lần hỏng không để lại file rỗng
            break
        except Exception as e:
            ra.with_suffix(".tam.mp3").unlink(missing_ok=True)
            print(f"  lần {lan + 1}: {type(e).__name__}, thử lại")
            time.sleep(2)
    else:
        sys.exit("✘ Giọng miễn phí không trả về sau 20 lần (mạng hoặc máy chủ Microsoft). Đợi 1 phút rồi chạy lại.")
    print(f"✔ {ra} {ra.stat().st_size // 1024} KB (giọng miễn phí {giong})")
    sys.exit(0)
than = {"text": chu, "provider": cfg["provider"], "model_id": cfg["model"], "language_code": cfg["ngon_ngu"], "name": ten_task(a.ra),
        "voice_settings": {"speed": a.toc or cfg.get("toc", 1.0), "pitch": 0, "vol": 1.0, **({"emotion": a.cam_xuc} if a.cam_xuc else {})}}
try:
    r = requests.post(f"{GOC}/v1/text-to-speech/{cfg['voice_id']}", headers=dau, json=than, timeout=120)
except requests.RequestException as e:
    tao_du_phong(chu, ra, f"mạng: {type(e).__name__}")
if r.status_code in (401, 403) or r.status_code >= 500:
    tao_du_phong(chu, ra, f"HTTP {r.status_code} {r.text[:80]}")
if r.status_code >= 300:
    sys.exit(f"✘ HTTP {r.status_code}: {r.text[:300]}")
ma = r.json()["id"]
print(f"đã gửi {len(chu)} ký tự, mã {ma}")
for _ in range(120):
    time.sleep(3)
    t = next((x for x in requests.get(f"{GOC}/v1/history", headers=dau, timeout=60).json()["tasks"] if x["id"] == ma), None)
    if t and t["status"] == "completed":
        print("credit:", t.get("credits_deducted"))
        tai(t["result"]["audio_url"], ra)
        sys.exit(0)
    if t and t["status"] in ("failed", "error"):
        sys.exit(f"✘ Task lỗi: {t.get('error')}")
sys.exit("✘ Quá 6 phút chưa xong, xem lại trên Vibi.")
