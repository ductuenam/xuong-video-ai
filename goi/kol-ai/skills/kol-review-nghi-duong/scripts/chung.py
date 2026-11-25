"""Hàm dùng chung cho skill kol-review-nghi-duong."""
import hashlib, json, os, subprocess, sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent          # thư mục skill
MO_HINH_MAT = GOC / "scripts" / "mo-hinh" / "face_detection_yunet_2023mar.onnx"
TAM = Path(os.environ.get("ND_TAM", "_tam-video/kol-nghi-duong"))

def font(ten="BeVietnamPro-ExtraBold.ttf"):
    """Tìm phông Be Vietnam Pro (cài cho người dùng) hoặc trong assets/fonts."""
    cho = [GOC / "assets" / "fonts" / ten,
           Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Windows/Fonts" / ten,
           Path("C:/Windows/Fonts") / ten]
    for p in cho:
        if p.exists():
            return str(p)
    for p in [Path("C:/Windows/Fonts/arialbd.ttf")]:
        if p.exists():
            return str(p)
    sys.exit(f"Không thấy phông {ten}. Chép tệp phông vào {GOC/'assets'/'fonts'}")

def doc_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def ghi_json(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for k in iter(lambda: f.read(1 << 20), b""):
            h.update(k)
    return h.hexdigest()

def chay(lenh, **kw):
    r = subprocess.run(lenh, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(f"Lệnh lỗi: {' '.join(map(str, lenh))[:300]}")
    return r

def do_dai(p):
    r = chay(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)])
    return float(r.stdout.strip())

def khung_tai(p, giay, rong=None):
    """Lấy 1 khung ảnh (numpy BGR) ở giây `giay`."""
    import cv2, numpy as np
    vf = ["-vf", f"scale={rong}:-2"] if rong else []
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{giay:.3f}", "-i", str(p), "-frames:v", "1",
                        *vf, "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    if not r.stdout:
        return None
    return cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR)

_det = None
def tim_mat(img):
    """Trả (x,y,w,h) mặt lớn nhất hoặc None (YuNet)."""
    global _det
    import cv2
    h, w = img.shape[:2]
    if _det is None:
        _det = cv2.FaceDetectorYN.create(str(MO_HINH_MAT), "", (w, h), 0.6)
    _det.setInputSize((w, h))
    _, faces = _det.detect(img)
    if faces is None or len(faces) == 0:
        return None
    f = max(faces, key=lambda f: float(f[14]))   # điểm tin cậy cao nhất (to nhất hay bắt nhầm cột gỗ)
    if float(f[14]) < 0.8:
        return None
    return tuple(int(v) for v in f[:4])

def cat_mat(img, co=240, le=0.45):
    """Cắt vuông quanh mặt (thêm lề cho tóc, cằm), đưa về co×co. None nếu không thấy mặt."""
    import cv2
    m = tim_mat(img)
    if m is None:
        return None
    x, y, w, h = m
    cx, cy = x + w / 2, y + h / 2 - h * 0.08
    c = max(w, h) * (1 + 2 * le)
    x0, y0 = int(max(0, cx - c / 2)), int(max(0, cy - c / 2))
    x1, y1 = int(min(img.shape[1], cx + c / 2)), int(min(img.shape[0], cy + c / 2))
    o = img[y0:y1, x0:x1]
    if o.size == 0:
        return None
    s = co / max(o.shape[:2])
    o = cv2.resize(o, (int(o.shape[1] * s), int(o.shape[0] * s)), interpolation=cv2.INTER_AREA)
    import numpy as np
    nen = np.full((co, co, 3), 30, np.uint8)
    nen[:o.shape[0], :o.shape[1]] = o
    return nen

def doc_anh_cv(p):
    """cv2.imread không đọc được đường dẫn có dấu tiếng Việt trên Windows → đọc qua numpy (cả webp)."""
    import cv2, numpy as np
    a = cv2.imdecode(np.fromfile(str(p), np.uint8), cv2.IMREAD_COLOR)
    if a is None:
        from PIL import Image
        a = cv2.cvtColor(np.array(Image.open(p).convert("RGB")), cv2.COLOR_RGB2BGR)
    return a

def ghi_anh_cv(p, img, chat=90):
    import cv2
    ok, b = cv2.imencode(Path(p).suffix or ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, chat])
    b.tofile(str(p))
