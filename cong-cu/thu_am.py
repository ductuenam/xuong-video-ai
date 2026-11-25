"""Bộ thử cố định cho nhạc nền, tiếng hiệu ứng (bản 0.2.8): chạy trước mỗi lần phát hành, cùng với thu_cap_nhat.py.

    python -X utf8 cong-cu/thu_am.py

Dựng một bộ não giả trong %TEMP%\\zaios_thu_am (skill chép vào .claude/skills như bộ cài làm), nhạc và tiếng tự tạo bằng ffmpeg:
  A  từ điển tâm trạng: từ đồng nghĩa đổi về từ chuẩn, từ lạ bị báo
  B  quyền nhạc theo chỉ mục: cc0/pixabay dùng được, chua-ro và bài ngoài chỉ mục bị chặn, gọi được bằng mô tả tên tệp
  C  bni.chon_nhac: đúng tâm trạng, bài đủ dài được xếp trước
  D  tron_am: bài ngắn hơn video tự nối vòng (không có khoảng câm), giây mạnh nhất của tiếng trùng lúc hình đổi,
     tiếng gọi bằng mã và bằng mô tả trong chỉ mục, tiếng khai trong hồ sơ cũng lấy được điểm nhấn
  E  them_am.py: đo, chặn nhãn sai, xem trước không ghi, ghi thật, không thêm trùng, mã mới gọi được ngay
  F  cong-cu/chung.sinh_md giữ dòng học viên khi bộ cài sinh lại CHI_MUC.md
In ĐẠT HẾT khi mọi phép thử đạt."""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "goi" / "video-nguoi-noi" / "skills" / "video-ngan-nguoi-noi"
GOC = Path(tempfile.gettempdir()) / "zaios_thu_am"
NAO = GOC / "Bo-Nao-Thu"
XUONG = NAO / "08_XUONG_VIDEO"
SC = NAO / ".claude" / "skills" / "video-ngan-nguoi-noi" / "scripts"
KQ = []


def dat(ten, ok, chi_tiet=""):
    KQ.append(ok)
    print(("ĐẠT  " if ok else "HỎNG ") + ten + (f"  ({chi_tiet})" if chi_tiet and not ok else ""))


def ff(*a):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *map(str, a)], check=True)


def py(*a, cwd=None):
    r = subprocess.run([sys.executable, "-X", "utf8", *map(str, a)], cwd=cwd or SC, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def goi(ma_lenh):
    """Chạy một đoạn Python trong thư mục scripts của skill giả (để chung.py tìm đúng bộ não giả)."""
    return py("-c", ma_lenh)


def ghi_csv(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with p.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def pcm(p, sr=22050, loc=None):
    b = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(p), "-vn", "-ac", "1", "-ar", str(sr), *(["-af", loc] if loc else []),
                        "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.float32)


def dung_the_gioi():
    if GOC.exists():
        shutil.rmtree(GOC)
    (NAO / ".claude").mkdir(parents=True)
    (NAO / ".claude" / "xuong-video.json").write_text(json.dumps({"xuong": str(XUONG), "bin": []}), encoding="utf-8")
    shutil.copytree(SKILL, NAO / ".claude" / "skills" / "video-ngan-nguoi-noi", ignore=shutil.ignore_patterns("__pycache__", "hoi_quy"))
    nh, am = XUONG / "tai-nguyen" / "nhac", XUONG / "tai-nguyen" / "am"
    (nh / "nen-video-ngan").mkdir(parents=True)
    (am / "giao-dien").mkdir(parents=True)
    # bài ngắn 20 giây có 6 giây đuôi im (như bài spa 67 giây): nối vòng phải bỏ đuôi im, không được hụt câm ở chỗ nối
    ff("-f", "lavfi", "-i", "sine=f=440:d=14", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono:d=6", "-filter_complex", "[0][1]concat=n=2:v=0:a=1",
       "-c:a", "libmp3lame", nh / "nen-video-ngan" / "NH0001_bai-ngan-vui.mp3")
    ff("-f", "lavfi", "-i", "sine=f=330:d=90", "-c:a", "libmp3lame", nh / "nen-video-ngan" / "NH0002_bai-dai-vui.mp3")
    ff("-f", "lavfi", "-i", "sine=f=500:d=90", "-c:a", "libmp3lame", nh / "nen-video-ngan" / "NH0003_bai-chua-ro.mp3")
    # Tiếng: im 1,0 giây rồi một tiếng tách 3 kHz dài 60 ms (điểm nhấn 1,0) — giống tiếng đặt tách, đồng xu vào muộn
    ff("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono:d=1.0", "-f", "lavfi", "-i", "sine=f=3000:d=0.06:r=44100",
       "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono:d=0.5", "-filter_complex", "[0][1][2]concat=n=3:v=0:a=1", am / "giao-dien" / "AM0001_tach-vao-muon.wav")
    chung = {"loai": "nhac", "nhom": "nen-video-ngan", "ten_nhom": "Nhạc nền video ngắn", "xem_truoc": "", "nguon": "thu", "chu": "kho",
             "goi": "nhe;du", "ngay_them": "2026-11-25", "trang_thai": "dung", "nhip_bpm": "~90", "nang_luong": "vua", "doan": "0-20 đều",
             "do_lon_lufs": "-14", "tu_khoa": "thu"}
    ghi_csv(nh / "chi-muc.csv", [
        {"ma": "NH0001", **chung, "mo_ta": "bài ngắn vui", "tep": "nen-video-ngan/NH0001_bai-ngan-vui.mp3", "thong_so": "128kbps;20s",
         "giay_phep": "pixabay", "tam_trang": "vui;tre-trung", "hop_video": "bni", "bat_dau_goi_y": "0"},
        {"ma": "NH0002", **chung, "mo_ta": "bài dài vui", "tep": "nen-video-ngan/NH0002_bai-dai-vui.mp3", "thong_so": "90s",
         "giay_phep": "cc0", "tam_trang": "vui-nhon", "hop_video": "bni", "bat_dau_goi_y": "2 hoặc 30"},
        {"ma": "NH0003", **chung, "mo_ta": "bài chưa rõ quyền", "tep": "nen-video-ngan/NH0003_bai-chua-ro.mp3", "thong_so": "90s",
         "giay_phep": "chua-ro", "tam_trang": "vui", "hop_video": "bni", "bat_dau_goi_y": "0"}])
    ghi_csv(am / "chi-muc.csv", [
        {"ma": "AM0001", "loai": "am", "nhom": "giao-dien", "ten_nhom": "Tiếng giao diện", "mo_ta": "tách vào muộn", "tu_khoa": "tach",
         "tep": "giao-dien/AM0001_tach-vao-muon.wav", "xem_truoc": "", "thong_so": "1.56s", "nguon": "thu", "giay_phep": "cc0",
         "chu": "kho", "goi": "nhe;du", "ngay_them": "2026-11-25", "trang_thai": "dung", "giay": "1.56", "diem_nhan_s": "1.00",
         "do_lon": "vua", "dung_khi": "thử"}])
    (XUONG / "ho-so-kenh.json").write_text(json.dumps({"ten": "Thu", "boNhac": {}, "boTieng": {
        "tach-cu": "tai-nguyen/am/giao-dien/AM0001_tach-vao-muon.wav"}}, ensure_ascii=False), encoding="utf-8")


def thu_tu_dien():
    rc, o = goi("import kho_am,json;print(json.dumps(kho_am.chuan_tam('Vui;tre-trung;Ấm áp;abc;nang-luong')))")
    dat("A từ điển: Vui, tre-trung, Ấm áp, nang-luong → vui, am-ap, soi-dong; 'abc' bị báo",
        rc == 0 and json.loads(o.strip().splitlines()[-1]) == [["vui", "am-ap", "soi-dong"], ["abc"]], o)


def thu_quyen():
    rc, o = goi("from kiem_chot import kiem_nhac as k;import json;print(json.dumps([k('NH0002'),k('NH0001'),k('NH0003'),k('xyz'),k(''),k('bai-dai-vui')]))")
    v = json.loads(o.strip().splitlines()[-1]) if rc == 0 else []
    dat("B quyền nhạc: cc0, pixabay đạt; chua-ro, ngoài chỉ mục, rỗng bị chặn; gọi bằng mô tả tên tệp đạt",
        len(v) == 6 and not v[0] and not v[1] and v[2] and "chưa rõ" in v[2] and v[3] and v[4] and not v[5], o)


def thu_chon():
    rc, o = goi("import bni;print(bni.chon_nhac({'tamTrang':'vui','doDai':60},{}), bni.chon_nhac({'tamTrang':'vui','doDai':30},{'tuan':[{'nhac':'NH0002'}]}))")
    v = o.strip().splitlines()[-1].split() if rc == 0 else []
    dat("C chọn nhạc: video 60 giây chọn bài đủ dài NH0002 (không chọn bài chưa rõ quyền)", v[:1] == ["NH0002"], o)
    dat("C chọn nhạc: bài vừa dùng tuần trước được đổi sang bài khác", v[1:2] == ["NH0001"], o)


def thu_tron():
    da = XUONG / "du-an" / "01-thu"
    (da / "render").mkdir(parents=True)
    T = 40
    ff("-f", "lavfi", "-i", f"color=c=black:s=320x568:d={T}:r=24", "-c:v", "libx264", "-pix_fmt", "yuv420p", da / "render" / "hinh-cam.mp4")
    # giọng 200 Hz trong 10 giây đầu, sau đó im (nhạc phải nhô lên và kéo tới hết video)
    ff("-f", "lavfi", "-i", "sine=f=200:d=10", "-af", f"apad=whole_dur={T}", "-c:a", "aac", da / "render" / "master.mp4")
    (da / "timeline.json").write_text(json.dumps({"het_tieng": 10, "tong": T, "moc": [5.0, 20.0, 30.0]}), encoding="utf-8")
    (da / "props.json").write_text(json.dumps({"canh": [{"tu": 5.0, "am": "AM0001"}, {"tu": 20.0, "am": "tach-vao-muon"},
                                                         {"tu": 30.0, "am": "tach-cu"}]}), encoding="utf-8")
    (da / "nhac.txt").write_text("NH0001", encoding="utf-8")
    rc, o = py(SC / "tron_am.py", da)
    ra = da / "render" / "ra.mp4"
    if rc or not ra.exists():
        dat("D trộn âm chạy được", False, o[-600:])
        return
    dat("D trộn âm chạy được, báo nối vòng bài 20 giây cho video 40 giây", "nối vòng" in o, o[-300:])
    sr = 22050
    nhac = pcm(ra, sr, "bandpass=f=440:w=60")
    w = sr // 2
    rms = [20 * np.log10(np.sqrt(np.mean(nhac[i:i + w] ** 2)) + 1e-9) for i in range(int(12 * sr), int(38 * sr), w)]
    dat("D nhạc không đứt sau giây 20 (nối vòng): mọi nửa giây từ 12 đến 38 đều có nhạc", min(rms) > -45, f"thấp nhất {min(rms):.1f} dB")
    sfx = pcm(ra, sr, "highpass=f=2500,highpass=f=2500")
    w = int(sr * 0.01)
    env = np.array([np.abs(sfx[i:i + w]).max() for i in range(0, len(sfx) - w, w)])
    dinh = []
    for t in (5.0, 20.0, 30.0):
        a, b = int((t - 1.5) * 100), int((t + 1.5) * 100)
        vung = env[a:b]
        dinh.append(round((a + int(np.argmax(vung > vung.max() / 2))) / 100, 2))  # lúc tiếng tách bắt đầu (điểm nhấn của tệp)
    lech = [abs(d - t) for d, t in zip(dinh, (5.0, 20.0, 30.0))]
    dat("D giây mạnh nhất của tiếng trùng lúc hình đổi (±0,08 s): gọi bằng mã, bằng mô tả, và tiếng khai trong hồ sơ",
        max(lech) <= 0.08, f"đỉnh ở {dinh}")


def thu_them():
    vao = GOC / "do-cua-hoc-vien"
    vao.mkdir()
    ff("-f", "lavfi", "-i", "sine=f=262:d=45", "-c:a", "aac", vao / "Nhạc Của Tôi.m4a")
    ff("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono:d=0.4", "-f", "lavfi", "-i", "sine=f=2000:d=0.05:r=44100",
       "-filter_complex", "[0][1]concat=n=2:v=0:a=1", vao / "ting.wav")
    rc, o = py(SC / "them_am.py", "do", vao / "Nhạc Của Tôi.m4a", vao / "ting.wav")
    try:
        kq = json.loads(o[:o.rindex("]") + 1])
    except ValueError:
        dat("E đo tệp của học viên", False, o[-500:])
        return
    nhap = [k["nhap"] for k in kq]
    dat("E đo: nhạc 45 giây nhận là nhac, tiếng ngắn là am, điểm nhấn tiếng ~0,4 s, có ảnh",
        [n["loai"] for n in nhap] == ["nhac", "am"] and abs(float(nhap[1]["diem_nhan_s"]) - 0.4) < 0.08 and Path(kq[0]["anh"]).is_file(), o[-400:])
    n0, n1 = nhap
    n0.update(slug="nhac-cua-toi-vui", mo_ta="Nhạc của tôi", tu_khoa="vui;cua-toi", nang_luong="vua", tam_trang="Vui;abc",
              hop_video="bni", doan="0-45 đều", nguon="tự làm", giay_phep="hoc-vien-tu-co")
    n1.update(nhom="giao-dien", slug="ting-cua-toi", mo_ta="Tiếng ting", tu_khoa="ting", dung_khi="hiện chữ", nguon="tự làm", giay_phep="cc0")
    f = GOC / "nhan.json"
    f.write_text(json.dumps([n0, n1], ensure_ascii=False), encoding="utf-8")
    cm = XUONG / "tai-nguyen" / "nhac" / "chi-muc.csv"
    truoc = cm.read_bytes()
    rc, o = py(SC / "them_am.py", "ghi", f, "--that")
    dat("E nhãn sai (tâm trạng 'abc' ngoài từ điển) bị chặn, không ghi gì", rc == 1 and "abc" in o and cm.read_bytes() == truoc, o[-300:])
    n0["tam_trang"] = "Vui;tre-trung"
    f.write_text(json.dumps([n0, n1], ensure_ascii=False), encoding="utf-8")
    rc, o = py(SC / "them_am.py", "ghi", f)
    dat("E xem trước: in 'sẽ thêm UNH0001, UAM0001', chưa ghi gì", rc == 0 and "UNH0001" in o and "UAM0001" in o and cm.read_bytes() == truoc, o[-300:])
    rc, o = py(SC / "them_am.py", "ghi", f, "--that")
    with cm.open(encoding="utf-8-sig") as g:
        r = next((x for x in csv.DictReader(g) if x["ma"] == "UNH0001"), {})
    tep = XUONG / "tai-nguyen" / "nhac" / r.get("tep", "-")
    dat("E ghi thật: tệp m4a đổi sang mp3 trong cua-toi/, dòng chu=hoc-vien, tâm trạng đã chuẩn 'vui', tệp gốc còn nguyên",
        rc == 0 and tep.is_file() and tep.suffix == ".mp3" and r.get("chu") == "hoc-vien" and r.get("tam_trang") == "vui"
        and "cua-toi/nen-video-ngan/" in r.get("tep", "") and (vao / "Nhạc Của Tôi.m4a").is_file(), o[-300:])
    md = (XUONG / "tai-nguyen" / "am" / "CHI_MUC.md").read_text(encoding="utf-8") if (XUONG / "tai-nguyen" / "am" / "CHI_MUC.md").exists() else ""
    dat("E CHI_MUC.md có dòng UAM0001 và chỉ mục cũ được sao lưu", "UAM0001" in md and any((XUONG / ".sao-luu").rglob("chi-muc.csv")), md[-200:])
    rc, o = py(SC / "them_am.py", "ghi", f, "--that")
    dat("E thêm lần hai cùng tệp: báo đã có, không cấp mã mới", "đã có trong kho" in o and "UNH0002" not in o, o[-300:])
    rc, o = goi("from kiem_chot import kiem_nhac as k;import kho_am;print(repr(k('UNH0001')), kho_am.tim('am','ting-cua-toi')['ma'])")
    dat("E bài học viên (hoc-vien-tu-co) dùng được ngay; tiếng gọi được bằng mô tả", rc == 0 and o.strip().endswith("'' UAM0001"), o[-300:])


def thu_sinh_md():
    sys.path.insert(0, str(REPO / "cong-cu"))
    os.environ["XUONG_REPO"] = str(XUONG)
    import importlib

    import chung
    importlib.reload(chung)
    chung.sinh_md("nhac")
    md = (XUONG / "tai-nguyen" / "nhac" / "CHI_MUC.md").read_text(encoding="utf-8")
    dat("F bộ cài sinh lại CHI_MUC.md vẫn liệt kê bài học viên và cột Tâm trạng", "UNH0001" in md and "Tâm trạng" in md, md[-300:])


def main():
    dung_the_gioi()
    thu_tu_dien()
    thu_quyen()
    thu_chon()
    thu_tron()
    thu_them()
    thu_sinh_md()
    print("\nKẾT QUẢ:", "ĐẠT HẾT" if all(KQ) else f"HỎNG {KQ.count(False)}/{len(KQ)}")
    return 0 if all(KQ) else 1


if __name__ == "__main__":
    sys.exit(main())
