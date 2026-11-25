"""Cổng thử trước MỖI lần phát hành: cài, cập nhật, dọn bản cũ trên thế giới tí hon trong %TEMP%\\zaios_thu_cap_nhat\\.
Không đụng kho thật, R2, thư mục nhà thật, Thùng rác thật. Xem docs/KE_HOACH_CAI_CAP_NHAT_AN_TOAN.md mục 6.

    python -X utf8 cong-cu/thu_cap_nhat.py

Cần mạng một lần (tải mã bộ cài cũ 24/11 từ GitHub để dựng máy có bản cũ). Các bước nặng (thư viện, Remotion, Whisper,
dựng thử) được thay bằng bản giả; phần đó thử thật riêng khi cài trên bộ não giả. In ĐẠT/HỎNG từng mục, cuối cùng ĐẠT HẾT.
"""
import contextlib
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

KHO = Path(__file__).resolve().parents[1]
T = Path(os.environ.get('TEMP', '/tmp')) / 'zaios_thu_cap_nhat'
if T.exists():
    shutil.rmtree(T)
R, KN, MAY, NHA, RAC = T / 'repo', T / 'kn', T / 'may', T / 'nha', T / 'rac'
B = T / 'Bộ Não Thử'
os.environ.update(XUONG_NHA=str(NHA), XUONG_THU_RAC=str(RAC))
for k in ('XUONG_XEM', 'XUONG_DON_BAN_CU', 'XUONG_CAI_LAI', 'XUONG_THU_O_TRONG'):
    os.environ.pop(k, None)
for d in ('cai', 'cong-cu', 'goi', 'xuong-mau', 'third_party'):
    shutil.copytree(KHO / d, R / d, ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy2(KHO / 'PHIEN_BAN.json', R / 'PHIEN_BAN.json')
BC_THAT = KHO / '_kho-nang' / 'ban-chuan' / 'tai-nguyen'
BC = KN / 'ban-chuan' / 'tai-nguyen'
ok = True


def kiem(dk, ten):
    global ok
    print(('ĐẠT  ' if dk else 'HỎNG ') + ten, flush=True)
    ok &= bool(dk)


def doc(p):
    with open(p, encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def ghi(p, cot, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, cot)
        w.writeheader()
        w.writerows(rows)


def anh_chup(goc: Path):
    """Ảnh chụp cây thư mục: {đường dẫn: (cỡ, thời điểm sửa)} để chứng minh 'không thay đổi gì'."""
    return {str(p): (p.stat().st_size, p.stat().st_mtime_ns) for p in goc.rglob('*') if p.is_file()}


# ---- thế giới tí hon: 2 cảnh nhẹ (+1 để dành cho v2), 1 nhạc, 1 tiếng, lấy tệp thật trong kho nặng
chon = {}
for loai, n in (('canh', 3), ('nhac', 1), ('am', 1)):
    cot, rows = doc(KHO / 'tai-nguyen' / loai / 'chi-muc.csv')
    rows = [r for r in rows if r['chu'] == 'kho' and 'nhe' in r['goi'].split(';') and r['trang_thai'] == 'dung'][:n]
    chon[loai] = (cot, rows)
    for r in rows:
        for c in ('tep', 'xem_truoc'):
            if r.get(c):
                (BC / loai / r[c]).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(BC_THAT / loai / r[c], BC / loai / r[c])
canh3 = chon['canh'][1].pop()
for loai, (cot, rows) in chon.items():
    ghi(R / 'tai-nguyen' / loai / 'chi-muc.csv', cot, rows)
env = dict(os.environ, XUONG_REPO=str(R), XUONG_KHO_NANG=str(KN))
pbp = R / 'PHIEN_BAN.json'


def sua_pb(**k):
    pb = json.loads(pbp.read_text(encoding='utf-8'))
    pb.update(k)
    pbp.write_text(json.dumps(pb, ensure_ascii=False, indent=2), encoding='utf-8')
    return pb


def dong_goi(v):
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', str(R / 'cong-cu' / 'dong_goi.py'), '--phien-ban', v, '--ghi-phien-ban'],
                       env=env, capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        sys.exit(r.stdout + r.stderr)
    pb = json.loads(pbp.read_text(encoding='utf-8'))
    for g in list(pb['goi_tai_nguyen'].values()) + [x for x in pb.get('goi_bo_sung', {}).values() if isinstance(x, dict)]:
        g['url'] = (KN / 'goi' / g['url'].rsplit('/', 2)[1] / g['url'].rsplit('/', 1)[1]).as_uri()
    pbp.write_text(json.dumps(pb, ensure_ascii=False, indent=2), encoding='utf-8')
    return pb


sua_pb(phien_ban_tai_nguyen='v0', phien_ban='0.9.0', co_gi_moi={'0.9.1': 'Dòng thử có gì mới của bản 0.9.1.'})
dong_goi('v1')

# ---- nạp bộ cài, thay các bước nặng bằng bản giả
sys.path.insert(0, str(R / 'cai'))
import cai_xuong as cx  # noqa: E402
import an_toan  # noqa: E402
cx.ffmpeg_node = lambda may: {}
cx.thu_vien = lambda uv, gpu: None
cx.engine = lambda nguon, may: MAY / 'engine'
cx.whisper = lambda ram, gpu: 'small'
cx.dung_thu = lambda xuong, may: True
cx.ram_gb = lambda: 8
B.mkdir(parents=True)
(B / 'INDEX.md').write_text('# Bộ não thử\n', encoding='utf-8')
(B / '01_THUONG_HIEU').mkdir()
(B / '01_THUONG_HIEU' / 'ho-so.md').write_text('Hồ sơ của học viên', encoding='utf-8')


def chay(**bien):
    for k in ('XUONG_XEM', 'XUONG_DON_BAN_CU', 'XUONG_CAI_LAI', 'XUONG_THU_O_TRONG'):
        os.environ.pop(k, None)
    os.environ.update(bien)
    sys.argv = ['cai_xuong.py', '--bo-nao', str(B), '--may', str(MAY), '--nguon', str(R), '--uv', 'uv', '--goi', 'nhe']
    cx.canh_bao.clear()
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = cx.main()
    except SystemExit as e:
        rc = e.code
    except RuntimeError as e:  # lỗi giả "mất điện" của mục T10
        rc = f'loi: {e}'
    finally:
        for k in bien:
            os.environ.pop(k, None)
    return rc, buf.getvalue()


# ================= T1 cài mới, T2 không có gì mới
rc, out = chay()
X = cx.xuong_da_cai(B)
kiem(rc == 0 and X and 'Tải gói kho-canh-nhe' in out, 'T1 cài mới: tải gói đủ, xưởng sẵn sàng')
kiem((X / '.dau-van-tay.json').is_file(), 'T3 chuẩn bị: bộ cài ghi dấu vân tay tệp đã cài')
rc, out = chay()
kiem('ĐÃ LÀ BẢN MỚI NHẤT' in out and 'Kiểm máy' not in out, 'T2 không có gì mới: báo một dòng, không chạy bước nào')

# ---- học viên tự thêm đồ, tự sửa skill gốc
rieng = X / 'tai-nguyen' / 'canh' / 'cua-toi' / 'canh-rieng.mp4'
rieng.parent.mkdir(parents=True, exist_ok=True)
rieng.write_bytes(b'video rieng')
cot, rows = doc(X / 'tai-nguyen' / 'canh' / 'chi-muc.csv')
rows.append({**rows[0], 'ma': 'HV0001', 'chu': 'hoc-vien', 'tep': 'cua-toi/canh-rieng.mp4'})
rows.append({**rows[0], 'ma': 'HV0002', 'chu': '', 'tep': 'cua-toi/canh-rieng.mp4'})  # quên ghi nhãn
ghi(X / 'tai-nguyen' / 'canh' / 'chi-muc.csv', cot, rows)
(X / 'thanh-pham' / 'video-cua-lan.mp4').write_bytes(b'thanh pham')
sk = B / '.claude' / 'skills' / 'video-ngan-nguoi-noi' / 'SKILL.md'
sk.write_text(sk.read_text(encoding='utf-8') + '\nLuật riêng của học viên: luôn dùng màu hồng.\n', encoding='utf-8')
(B / '.claude' / 'skills' / 'video-ngan-nguoi-noi' / 'ghi-chu-rieng.md').write_text('tệp học viên tự thêm', encoding='utf-8')

# ================= Founder ra bản mới: thêm 1 cảnh, sửa 1 tiếng, sửa skill gốc; mã 0.9.1
cot, rows = chon['canh']
ghi(R / 'tai-nguyen' / 'canh' / 'chi-muc.csv', cot, rows + [canh3])
am = BC / 'am' / chon['am'][1][0]['tep']
am.write_bytes(am.read_bytes() + b'\0' * 64)
skr = R / 'goi' / 'video-nguoi-noi' / 'skills' / 'video-ngan-nguoi-noi' / 'SKILL.md'
skr.write_text(skr.read_text(encoding='utf-8') + '\n<!-- sửa của bản 0.9.1 -->\n', encoding='utf-8')
sua_pb(phien_ban='0.9.1')
pb = dong_goi('v2')
with zipfile.ZipFile(KN / 'goi' / 'v2' / 'bo-sung-v1-v2.zip') as z:
    kiem(len(z.namelist()) == 3, 'dong_goi: gói bổ sung chỉ 3 tệp mới/đổi')
for z in list((KN / 'goi' / 'v2').glob('kho-*.zip')) + [KN / 'goi' / 'v2' / 'nhac-am-v2.zip']:
    z.unlink()  # chứng minh chỉ tải gói bổ sung

# ================= T8 xem trước: không thay đổi gì
truoc = anh_chup(B)
rc, out = chay(XUONG_XEM='1')
kiem(rc == 0 and 'XEM TRƯỚC' in out and 'bổ sung khoảng' in out and 'Dòng thử có gì mới' in out, 'T8 xem trước: báo bản mới, có gì mới, tải bao nhiêu')
kiem('video-ngan-nguoi-noi/SKILL.md' in out, 'T8 xem trước: báo trước tệp gốc học viên đã sửa sẽ được cất')
kiem(anh_chup(B) == truoc, 'T8 xem trước: không một tệp nào trong bộ não thay đổi')

# ================= T11 ổ đầy: DỪNG trước khi tải, không đụng gì
rc, out = chay(XUONG_THU_O_TRONG='0.5')
kiem(rc == 1 and 'DỪNG' in out and 'Chưa có gì bị thay đổi' in out, 'T11 ổ không đủ chỗ: DỪNG trước khi tải, nói rõ cần bao nhiêu')
kiem(not (X / 'tai-nguyen' / 'canh' / canh3['tep']).exists(), 'T11: chưa giải nén gì')

# ================= T10 đứt giữa chừng (sau khi tải tài nguyên), chạy lại thì đi tiếp
giu = cx.whisper
cx.whisper = lambda ram, gpu: (_ for _ in ()).throw(RuntimeError('mất điện giả'))
rc, out_dut = chay()
cx.whisper = giu
kiem(str(rc).startswith('loi') and 'Anh/chị đã sửa 1 tệp gốc' in out_dut, 'T3 có ⚠ báo học viên tệp gốc đã sửa được cất')
rc, out = chay()
kiem(rc == 0 and 'bổ sung v2: 3 tệp' in out, 'T10 + T4 đứt giữa chừng rồi chạy lại: tải tiếp gói bổ sung, xong')

# ================= kiểm sau cập nhật
kiem((X / 'tai-nguyen' / 'canh' / canh3['tep']).exists(), 'T4 cảnh mới nằm đúng chỗ')
kiem((X / 'tai-nguyen' / 'am' / chon['am'][1][0]['tep']).read_bytes() == am.read_bytes(), 'T4 tiếng đã sửa được thay bản mới')
kiem(rieng.read_bytes() == b'video rieng' and (X / 'thanh-pham' / 'video-cua-lan.mp4').exists(), 'T6 cảnh riêng, thành phẩm còn nguyên')
ma = {r['ma'] for r in doc(X / 'tai-nguyen' / 'canh' / 'chi-muc.csv')[1]}
kiem({'HV0001', 'HV0002', canh3['ma']} <= ma, 'T6 dòng học viên còn (cả dòng quên ghi nhãn), có dòng cảnh mới')
cat = list((X / '.sao-luu').rglob('video-ngan-nguoi-noi/SKILL.md'))
kiem(cat and 'màu hồng' in cat[0].read_text(encoding='utf-8'), 'T3 skill gốc học viên đã sửa: bản sửa được cất vào .sao-luu')
kiem('sửa của bản 0.9.1' in sk.read_text(encoding='utf-8'), 'T3 skill gốc đã lên bản mới')
kiem((B / '.claude' / 'skills' / 'video-ngan-nguoi-noi' / 'ghi-chu-rieng.md').exists(), 'T7 tệp học viên tự thêm trong skill còn nguyên')
kiem('ĐÃ CẬP NHẬT 0.9.0 → 0.9.1' in out and 'Dòng thử có gì mới' in out, 'in "Có gì mới" đúng bản')
kiem((B / '01_THUONG_HIEU' / 'ho-so.md').read_text(encoding='utf-8') == 'Hồ sơ của học viên', 'ngăn khác của bộ não không bị đụng')
rc, out = chay()
kiem('ĐÃ LÀ BẢN MỚI NHẤT (mã 0.9.1, tài nguyên v2)' in out, 'T2 sau cập nhật: lại báo mới nhất')

# ================= T13 học viên đổi tên ngăn xưởng
X2 = B / '08_VIDEO_CUA_TOI'
X.rename(X2)
sua_pb(phien_ban='0.9.2')
rc, out = chay()
kiem(rc == 0 and cx.xuong_da_cai(B) == X2 and not list(B.glob('*_XUONG_VIDEO')), 'T13 đổi tên ngăn xưởng: vẫn nhận đúng, không tạo xưởng thứ hai')
X = X2

# ================= T9 máy có bộ cài cũ 24/11
goc = re.search(r'github\.com/([\w.-]+/[\w.-]+)`, commit `(\w+)`', (KHO / 'third_party' / 'NGUON_GOC.md').read_text(encoding='utf-8'))
CU = T / 'ma-cu'
with urllib.request.urlopen(f'https://codeload.github.com/{goc[1]}/tar.gz/{goc[2]}', timeout=60) as r:
    with tarfile.open(fileobj=io.BytesIO(r.read())) as t:
        t.extractall(CU, filter='data')
CU = next(CU.iterdir())
cl = NHA / '.claude'
shutil.copytree(CU / '.claude' / 'skills', cl / 'skills')
shutil.copytree(CU / '.claude' / 'agents', cl / 'agents')
(cl / 'skills' / 'video-ngan-nguoi-noi' / 'engine' / 'node_modules' / 'x').mkdir(parents=True)
(cl / 'skills' / 'video-ngan-nguoi-noi' / 'engine' / 'node_modules' / 'x' / 'rac.js').write_text('rác', encoding='utf-8')
(cl / 'skills' / 'kol-ban-quan-ao' / 'kol.json').write_text('{"ten": "KOL của học viên"}', encoding='utf-8')
cfg = next((cl / 'skills' / 'ab-edit').glob('config.json'))
cfg.write_text(cfg.read_text(encoding='utf-8') + '\n', encoding='utf-8')  # học viên sửa tệp gốc
la = cl / 'skills' / 'anh-bia-video'
shutil.rmtree(la)
la.mkdir()
(la / 'SKILL.md').write_text('skill của chính học viên, trùng tên', encoding='utf-8')
(cl / 'sao-luu-cu' / '20261124-120000' / 'skill' / 'ab-edit').mkdir(parents=True)
(cl / 'sao-luu-cu' / '20261124-120000' / 'skill' / 'ab-edit' / 'SKILL.md').write_text('bản cũ', encoding='utf-8')
(cl / 'skills' / 'skill-khac-cua-hoc-vien').mkdir()
(cl / 'skills' / 'skill-khac-cua-hoc-vien' / 'SKILL.md').write_text('không liên quan', encoding='utf-8')
dv = json.loads((R / 'cai' / 'ban-cu-24-11.json').read_text(encoding='utf-8'))
VA = T / 'Video-AI'
for rel in ('du-an/01-bni/render/thanh-pham.mp4', 'anh-video-cua-toi/1-mo_cua-hang.jpg', 'ho-so-bni.md'):
    (VA / rel).parent.mkdir(parents=True, exist_ok=True)
    (VA / rel).write_bytes(b'do cua hoc vien ' + rel.encode())
(VA / 'ho-so-kenh.json').write_text('{"ten": "Kênh của học viên"}', encoding='utf-8')
mau_kho = sorted(dv['kho'])[:3]
for rel in mau_kho:  # bản chép kho cũ: đúng tên, đúng cỡ
    (VA / rel).parent.mkdir(parents=True, exist_ok=True)
    (VA / rel).write_bytes(b'\0' * dv['kho'][rel][0])
(VA / 'kho-canh' / 'canh-tu-them.mp4').write_bytes(b'canh hoc vien tu them')
(NHA / 'Downloads').mkdir(parents=True)
(NHA / 'Downloads' / 'KHO-HOC-VIEN (1).zip').write_bytes(b'zip gia')
(NHA / 'Downloads' / 'anh-gia-dinh.jpg').write_bytes(b'khong lien quan')

truoc_nha, truoc_va = anh_chup(NHA), anh_chup(VA)
rc, out = chay(XUONG_XEM='1')
kiem('Bản cũ (bộ cài 24/11)' in out and '8 skill cũ' in out and 'KHÔNG đụng' in out, 'T9 xem trước: liệt kê bản cũ (8 skill, 1 skill lạ không đụng)')
kiem(anh_chup(NHA) == truoc_nha and anh_chup(VA) == truoc_va, 'T9 xem trước: không đụng gì')
rc, out = chay()
kiem('PHÁT HIỆN BẢN CŨ' in out and anh_chup(NHA) == truoc_nha, 'T9 cập nhật thường: chỉ báo bản cũ, chưa dọn khi chưa OK')
rc, out = chay(XUONG_DON_BAN_CU='1')
kiem(rc == 0 and 'ĐÃ DỌN BẢN CŨ' in out, 'T9 dọn khi đã OK: xong')
chuyen = next((X / 'chuyen-tu-ban-cu').iterdir())
kiem((chuyen / 'skills' / 'kol-ban-quan-ao' / 'kol.json').is_file(), 'T9 cứu cấu hình KOL học viên tự tạo')
kiem((chuyen / 'skills' / 'ab-edit' / 'config.json').is_file(), 'T9 cứu tệp gốc học viên đã sửa')
kiem(not list(chuyen.rglob('node_modules')), 'T9 không chép rác node_modules')
kiem((X / 'du-an' / '01-bni' / 'render' / 'thanh-pham.mp4').is_file() and (X / 'anh-video-cua-toi' / '1-mo_cua-hang.jpg').is_file(),
     'T9 video, ảnh cũ chuyển vào đúng chỗ trong xưởng')
kiem('Kênh của học viên' in (X / 'ho-so-kenh.json').read_text(encoding='utf-8'), 'T9 hồ sơ kênh cũ thay hồ sơ mẫu trống')
kiem((chuyen / 'Video-AI' / 'kho-canh' / 'canh-tu-them.mp4').is_file() and not (chuyen / 'Video-AI' / mau_kho[0]).exists(),
     'T9 cảnh học viên tự thêm được cứu; bản chép kho cũ không chép')
kiem(not VA.exists() and not (NHA / 'Downloads' / 'KHO-HOC-VIEN (1).zip').exists(), 'T9 Video-AI, gói kho cũ vào Thùng rác')
kiem(not (cl / 'skills' / 'ab-edit').exists() and not (cl / 'agents' / 'video-dung.md').exists(), 'T9 skill, agent cũ vào Thùng rác')
kiem((la / 'SKILL.md').is_file() and (cl / 'skills' / 'skill-khac-cua-hoc-vien').is_dir() and (NHA / 'Downloads' / 'anh-gia-dinh.jpg').is_file(),
     'T9 skill trùng tên nội dung lạ, skill khác, tệp khác của học viên: không đụng')
kiem((RAC / 'Video-AI').is_dir() and (X / 'NHAT_KY_DON_BAN_CU.md').is_file(), 'T9 có trong Thùng rác (lấy lại được) và có nhật ký')
rc, out = chay()
kiem('PHÁT HIỆN BẢN CŨ' not in out, 'T9 lần sau: không còn dấu vết bản cũ')

# ================= XUONG_CAI_LAI
rc, out = chay(XUONG_CAI_LAI='1')
kiem(rc == 0 and 'Kiểm máy' in out and 'đã có, bỏ qua tải' in out, 'cài lại: chạy đủ bước, không tải lại tài nguyên')
print('\nKẾT QUẢ:', 'ĐẠT HẾT' if ok else 'CÓ MỤC HỎNG')
sys.exit(0 if ok else 1)
