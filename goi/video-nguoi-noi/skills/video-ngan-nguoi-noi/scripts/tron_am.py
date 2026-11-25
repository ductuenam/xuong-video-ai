"""Trộn âm theo timeline.json: giọng giữ nguyên, nhạc thấp hơn giọng theo nhacDuoiGiong của hồ sơ (mặc định 10 LU), tiếng hiệu ứng khoảng -14 dBFS.
  python tron_am.py <thư mục dự án>
nhac.txt của dự án: mã bài trong tai-nguyen/nhac/chi-muc.csv (kho chung hoặc của học viên), hoặc tên trong boNhac của hồ sơ
(giá trị là file, hoặc {"file", "tu"} để bỏ đoạn đầu). Bài trong chỉ mục tự bắt đầu ở cột bat_dau_goi_y.
Nhạc tự cắt đúng độ dài video; bài ngắn hơn video thì tự nối vòng có mờ chồng 2 giây.
Cảnh trong canh.json có thể thêm: am (thay tiếng lúc vào cảnh), amMoc (phát ở mỗi mốc của cảnh). Giá trị là tên trong boTieng
của hồ sơ, hoặc mã / mô tả tên tệp trong tai-nguyen/am/chi-muc.csv (ví dụ AM0012, dong-xu-roi-nay).
Tiếng có cột diem_nhan_s thì giây mạnh nhất được đặt trùng đúng lúc hình đổi, và phát đủ tới sau điểm nhấn.
Trong boTieng, giá trị là file (phát 1,2 giây đầu hoặc tới sau điểm nhấn) hoặc {"file", "dai"} để phát dai giây.
Ghi render/ra.mp4."""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import kho_am
from chung import XUONG, doc, duong_dan, ho_so
from kiem_chot import kiem_nhac

da = Path(sys.argv[1])
h = ho_so(da)
T = doc(da / "timeline.json")
GIONG_HET, TONG, MOC = T["het_tieng"], T["tong"], T["moc"]
bo_nhac, bo_tieng = h.get("boNhac", {}), h.get("boTieng", {})
chon = (da / "nhac.txt").read_text(encoding="utf-8").strip() if (da / "nhac.txt").exists() else ""
loi_nhac = kiem_nhac(chon)  # luật đã chốt số 11, máy kiểm (references/da-chot.json → nhacDuocDung)
if loi_nhac:
    sys.exit("✘ " + loi_nhac)
muc = bo_nhac.get(chon)
dong_nhac = kho_am.tim("nhac", chon) if chon else None
if not muc and dong_nhac and dong_nhac["_file"].is_file():  # bài trong chỉ mục: bắt đầu ở giây gợi ý (bỏ đoạn dạo quá nhỏ)
    muc = {"file": str(dong_nhac["_file"]), "tu": kho_am.so(dong_nhac.get("bat_dau_goi_y")) or 0}
if not muc and XUONG and chon:  # máy cũ chưa có chỉ mục: tìm theo mã trong <xưởng>/tai-nguyen/nhac (tệp <mã>_*.mp3, nhạc của tôi: <mã>.mp3)
    tim_nhac = next(iter(sorted((XUONG / "tai-nguyen" / "nhac").rglob(f"{chon}_*.mp3")) + sorted((XUONG / "tai-nguyen" / "nhac").rglob(f"{chon}.mp3"))), None)
    if tim_nhac:
        muc = {"file": str(tim_nhac), "tu": 9.5 if chon == "NH0003" else 0}  # NH0003 vào nhịp muộn: bắt đầu từ giây 9,5
nhac_tu = muc.get("tu", 0) if isinstance(muc, dict) else 0  # bài vào nhịp muộn thì bỏ đoạn đầu
nhac = str(duong_dan(h, muc["file"] if isinstance(muc, dict) else muc)) if muc else str(duong_dan(h, h["nhac"])) if h.get("nhac") else chon
if not nhac or not Path(nhac).is_file():
    # Máy học viên mới chưa có kho nhạc (thử máy sạch 24/11/2026 bị dừng ở đây): dựng chỉ có giọng, không dừng
    print(f"⚠ chưa có file nhạc '{chon}' ({nhac}): video chỉ có giọng. Nhạc nằm ở tai-nguyen/nhac/ trong Xưởng; thiếu thì chạy lại câu lệnh cài Xưởng Video AI rồi dựng lại.")
    nhac = None
# Bài không đủ dài cho video (tính từ giây bắt đầu): lùi giây bắt đầu; vẫn thiếu thì nối vòng bài có mờ chồng
# "Hết" = giây cuối còn nghe rõ (bỏ đuôi tắt dần, đuôi im), để video không kết vào chỗ bài đã tắt và chỗ nối vòng không hụt câm.
DAI_NHAC = kho_am.do_dai(nhac) if nhac else None
HET_NHAC = (kho_am.het_tieng(nhac) or DAI_NHAC) if DAI_NHAC else None
SO_VONG, MO_CHONG, DOAN_VONG = 1, 2.0, None
if HET_NHAC:
    if nhac_tu + TONG > HET_NHAC:
        nhac_tu = max(0.0, min(nhac_tu, HET_NHAC - TONG))
    if TONG > HET_NHAC - nhac_tu:
        if HET_NHAC - nhac_tu < 6:  # đoạn từ giây bắt đầu quá ngắn: nối cả bài từ đầu
            nhac_tu = 0.0
        DOAN_VONG = (nhac_tu, HET_NHAC)  # mỗi vòng là đoạn [bắt đầu, hết]
        dai_doan = HET_NHAC - nhac_tu
        MO_CHONG = min(2.0, dai_doan / 3)
        SO_VONG = math.ceil((TONG + 0.3 - MO_CHONG) / (dai_doan - MO_CHONG))
        nhac_tu = 0.0
        print(f"• bài nhạc nghe rõ {dai_doan:.0f} giây, video {TONG:.0f} giây: nối vòng {SO_VONG} lần, mờ chồng {MO_CHONG:.1f} giây")
DUOI_GIONG = h.get("nhacDuoiGiong", 10)  # nhạc thấp hơn giọng bao nhiêu LU; 22 dB từng làm nhạc gần như không nghe thấy
mac_dinh = str(duong_dan(h, h["tiengChuyenCanh"])) if h.get("tiengChuyenCanh") else ""
if not Path(mac_dinh).is_file():
    mac_dinh = None
DAI_TIENG = 1.2  # tiếng chuyển cảnh chỉ cần ngắn; tiếng dài khai "dai" trong boTieng
canh = doc(da / "props.json")["canh"] if (da / "props.json").exists() else []
hinh, master, ra = str(da / "render/hinh-cam.mp4"), str(da / "render/master.mp4"), str(da / "render/ra.mp4")


def do(file, loc):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", file, "-af", loc, "-vn", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr


def tieng(ten):
    """Trả về (file, số giây phát, giây điểm nhấn trong tệp). Tìm trong boTieng của hồ sơ trước, rồi trong chỉ mục tai-nguyen/am."""
    dai_khai = None
    if ten in bo_tieng:
        muc = bo_tieng[ten]
        f = str(duong_dan(h, muc["file"] if isinstance(muc, dict) else muc))
        dai_khai = muc.get("dai") if isinstance(muc, dict) else None
        dong = kho_am.theo_tep("am", f)
    else:
        dong = kho_am.tim("am", ten)
        if not dong:
            print(f"⚠ không có tiếng '{ten}' trong boTieng của hồ sơ ({', '.join(bo_tieng) or 'trống'}) "
                  "hay trong tai-nguyen/am/chi-muc.csv: bỏ tiếng này")
            return None
        f = str(dong["_file"])
    if not Path(f).is_file():
        print(f"⚠ thiếu file tiếng '{ten}' ({f}): bỏ tiếng này")
        return None
    giay = kho_am.so(dong.get("giay")) if dong else None
    nhan = kho_am.so(dong.get("diem_nhan_s")) if dong else None
    nhan = nhan if nhan and nhan > 0.05 and (not giay or nhan < giay) else 0.0
    if dai_khai:
        dai = float(dai_khai)
    else:
        dai = max(DAI_TIENG, nhan + 0.5)  # phát tới sau điểm nhấn nửa giây (đặt tách ở giây 1,75 từng bị cắt mất)
        dai = min(dai, giay) if giay else dai
    if nhan > dai - 0.1:  # khai dai ngắn hơn điểm nhấn: không đặt theo điểm nhấn
        nhan = 0.0
    return f, round(dai, 2), round(nhan, 2)


if mac_dinh:
    bo_tieng.setdefault("_mac_dinh", h["tiengChuyenCanh"])
TIENG_MAC_DINH = tieng("_mac_dinh") if mac_dinh else None

# Danh sách (giây hình đổi, (file, số giây phát, điểm nhấn)) cần phát
phat = []
for t in MOC:
    c = next((x for x in canh if abs(x["tu"] - t) < 0.02), {})
    phat.append((t, tieng(c["am"]) if c.get("am") else (TIENG_MAC_DINH if mac_dinh else None)))
for c in canh:
    if c.get("amMoc"):
        phat += [(c["tu"] + m, tieng(c["amMoc"])) for m in c.get("moc", []) if isinstance(m, (int, float)) and m >= 0.25]
phat = sorted((x for x in phat if x[1]), key=lambda x: x[0])

lufs_nhac = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", do(nhac, "ebur128=framelog=quiet"))[-1]) if nhac else 0.0
lufs_giong = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", do(master, "ebur128=framelog=quiet"))[-1])
g_nhac = lufs_giong - DUOI_GIONG - lufs_nhac
files = sorted({x for _, x in phat})
# Video edit từ file quay: người nói liền, cảnh minh họa vào giữa câu nên tiếng chuyển cảnh đè chữ (bản 30 giây 24/11/2026,
# đủ lời tụt từ 95% trên master xuống 85% sau trộn). Đỉnh tiếng chuyển cảnh -24 dB thay vì -14 dB.
from kiem_chot import loai_du_an
DINH_SFX = -24 if "edit" in loai_du_an(da).split() else -14
g_sfx = {f: DINH_SFX - float(re.findall(r"max_volume: (-?[\d.]+) dB", do(f, "volumedetect"))[-1]) for f in {x[0] for x in files}}
print(json.dumps({"giong_lufs": lufs_giong, "nhac_lufs": lufs_nhac, "gain_nhac_db": round(g_nhac, 1), "so_tieng": len(phat),
                  "nhac_tu": round(nhac_tu, 2), "nhac_vong": SO_VONG}))

# Bài ngắn hơn video: nối chính nó SO_VONG lần, chỗ nối mờ chồng MO_CHONG giây
VONG = []
if nhac and SO_VONG > 1:
    VONG = [f"[2:a]atrim={DOAN_VONG[0]:.2f}:{DOAN_VONG[1]:.2f},asetpts=PTS-STARTPTS,asplit={SO_VONG}" + "".join(f"[v{i}]" for i in range(SO_VONG))]
    truoc = "[v0]"
    for i in range(1, SO_VONG):
        VONG.append(f"{truoc}[v{i}]acrossfade=d={MO_CHONG:.2f}:c1=tri:c2=tri[x{i}]")
        truoc = f"[x{i}]"
NGUON_NHAC = truoc if VONG else "[2:a]"
loc = [f"[1:a]apad=whole_dur={TONG}[g]"] + VONG + (["[g]asplit=2[g][gk]",
       # Nhạc tự nén xuống khi có giọng, nhô lên ở chỗ nghỉ để bài có nhịp thở
       f"{NGUON_NHAC}atrim={nhac_tu}:{nhac_tu + TONG},asetpts=PTS-STARTPTS,volume={g_nhac:.2f}dB[n0]",
       "[n0][gk]sidechaincompress=threshold=0.05:ratio=2.5:attack=15:release=300[n1]",
       f"[n1]volume='if(gt(t,{GIONG_HET}),min(1+(t-{GIONG_HET})*3,2.2),1)':eval=frame,afade=t=in:d=0.3,afade=t=out:st={TONG - 1.2}:d=1.2[n]"] if nhac else [])
vao = ["-i", hinh, "-i", master] + (["-i", nhac] if nhac else [])
GOC_SFX = 3 if nhac else 2
for k, (f, dai, nhan) in enumerate(files):
    vao += ["-i", f]
    dung = [i for i, x in enumerate(phat) if x[1] == (f, dai, nhan)]
    loc.append(f"[{GOC_SFX + k}:a]atrim=0:{dai},afade=t=out:st={max(0, dai - 0.3):.2f}:d=0.3,volume={g_sfx[f]:.2f}dB,asplit={len(dung)}" + "".join(f"[s{i}]" for i in dung))
for i, (t, (_, _, nhan)) in enumerate(phat):
    # Giây mạnh nhất của tiếng trùng lúc hình đổi; tiếng không có điểm nhấn thì vào sớm 0,12 giây như cũ.
    bat_dau = t - nhan if nhan else t - 0.12
    cat = max(0.0, -bat_dau)  # hình đổi sát đầu video: bỏ phần đầu tiếng cho điểm nhấn vẫn đúng giây
    loc.append(f"[s{i}]" + (f"atrim=start={cat:.3f},asetpts=PTS-STARTPTS," if cat else "") + f"adelay={int(max(0, bat_dau) * 1000)}:all=1[d{i}]")
loc.append("[g]" + ("[n]" if nhac else "") + "".join(f"[d{i}]" for i in range(len(phat))) + f"amix=inputs={(2 if nhac else 1) + len(phat)}:normalize=0:duration=first,alimiter=limit=0.84:level=0[a]")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *vao, "-filter_complex", ";".join(loc),
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-t", str(TONG), "-movflags", "+faststart", ra], check=True)
print("xong", ra)
