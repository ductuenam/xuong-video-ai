"""Phần chính của bộ cài Xưởng Video AI (chung Windows và Mac). cai.ps1 / cai.sh gọi tệp này bằng Python riêng của xưởng.

    python -X utf8 cai_xuong.py --bo-nao <Bộ Não AI> --may <nơi đặt phần mềm> --nguon <mã xưởng> --uv <uv> [--goi nhe|du]

Chạy lại = cập nhật. Luật không đổi: mọi thứ có chữ `cua-toi` hoặc dòng `chu=hoc-vien` là của học viên, không bao giờ ghi đè;
tệp học viên tự thêm vào skill (ảnh KOL, brands riêng, cau-hinh.json) được giữ vì bộ cài chỉ chép đè tệp của kho, không xóa tệp lạ.
Bước nào hỏng mà không bắt buộc thì ghi ⚠ và cài tiếp; bước bắt buộc hỏng thì DỪNG kèm cách sửa.
"""
import argparse
import csv
import ctypes
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path

import an_toan  # cùng thư mục cai/: sao lưu tệp học viên đã sửa, Thùng rác, dò và dọn bộ cài cũ

WIN = sys.platform == 'win32'
MAC = sys.platform == 'darwin'
NODE_BAN = 'v22.12.0'
# ctranslate2 ghim 4.8.2: bản 4.9.1 mới ra bị Smart App Control chặn DLL (thử 25/11/2026), 4.8.2 chạy được.
# av ghim 19.0.2: av 18 bị Smart App Control chặn DLL; av 19 cần vá faster-whisper (va_faster_whisper). Thử 25/11/2026.
THU_VIEN = ['faster-whisper', 'ctranslate2==4.8.2', 'av==19.0.2', 'opencv-python', 'numpy', 'edge-tts', 'requests', 'google-auth', 'playwright', 'pillow']
DAU, CUOI = '<!-- XUONG-VIDEO:BEGIN -->', '<!-- XUONG-VIDEO:END -->'
canh_bao = []


def dung(loi):
    print(f'\nDỪNG: {loi}', flush=True)
    sys.exit(1)


def buoc(s):
    print(f'\n== {s}', flush=True)


def cb(s):
    canh_bao.append(s)
    print(f'⚠ {s}', flush=True)


def chay(cmd, **k):
    return subprocess.run([str(x) for x in cmd], **k)


# ---------------------------------------------------------------- máy

def ram_gb():
    try:
        if WIN:
            class M(ctypes.Structure):
                _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong), ('ullTotalPhys', ctypes.c_ulonglong),
                            ('ullAvailPhys', ctypes.c_ulonglong), ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                            ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong), ('x', ctypes.c_ulonglong)]
            m = M()
            m.dwLength = ctypes.sizeof(M)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return round(m.ullTotalPhys / 2 ** 30)
        if MAC:
            return round(int(subprocess.check_output(['sysctl', '-n', 'hw.memsize'])) / 2 ** 30)
    except Exception:
        pass
    return 8


def co_gpu():
    nv = shutil.which('nvidia-smi')
    return bool(nv) and chay([nv, '-L'], capture_output=True).returncode == 0


# ---------------------------------------------------------------- tải

def tai(url, dich: Path, sha=None, ten=''):
    """Tải có nối tiếp (đứt mạng thì chạy lại sẽ tải tiếp), kiểm sha256 nếu có."""
    dich.parent.mkdir(parents=True, exist_ok=True)
    if dich.exists() and sha and sha256(dich) == sha:
        return dich
    part = dich.with_name(dich.name + '.part')
    for lan in range(5):
        da = part.stat().st_size if part.exists() else 0
        req = urllib.request.Request(url, headers={'User-Agent': 'xuong-video-ai-cai/1.0', **({'Range': f'bytes={da}-'} if da else {})})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                if da and r.status != 206:
                    da = 0
                tong = da + int(r.headers.get('Content-Length') or 0)
                moc = time.time()
                with open(part, 'ab' if da else 'wb') as f:
                    while True:
                        k = r.read(1 << 20)
                        if not k:
                            break
                        f.write(k)
                        da += len(k)
                        if tong and time.time() - moc > 3:
                            moc = time.time()
                            print(f'   {ten or dich.name}: {da / 1e6:,.0f}/{tong / 1e6:,.0f} MB', flush=True)
            break
        except Exception as e:
            print(f'   mạng chập chờn ({e}), thử lại {lan + 1}/5...', flush=True)
            time.sleep(3 * (lan + 1))
    else:
        dung(f'Không tải được {url}. Kiểm mạng rồi dán lại câu lệnh (phần đã tải được giữ, sẽ tải tiếp).')
    if sha and sha256(part) != sha:
        part.unlink()
        dung(f'Tệp {dich.name} tải về bị hỏng (sai mã kiểm). Dán lại câu lệnh để tải lại.')
    part.replace(dich)
    return dich


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for k in iter(lambda: f.read(1 << 20), b''):
            h.update(k)
    return h.hexdigest()


def giai_nen(goi: Path, dich: Path):
    if goi.suffix == '.zip':
        with zipfile.ZipFile(goi) as z:
            z.extractall(dich)
    else:
        with tarfile.open(goi) as t:
            t.extractall(dich)


# ---------------------------------------------------------------- phần mềm

def ffmpeg_node(may: Path):
    """Dùng ffmpeg/node có sẵn trên máy nếu chạy được; thiếu thì tải bản chạy ngay vào thư mục xưởng."""
    bin_ = []
    # ffmpeg
    fdir = may / 'ffmpeg'
    tim = next(iter(fdir.rglob('ffmpeg.exe' if WIN else 'ffmpeg')), None) if fdir.exists() else None
    if not tim and shutil.which('ffmpeg') and shutil.which('ffprobe'):
        tim = Path(shutil.which('ffmpeg'))
    if not tim:
        print('Tải FFmpeg (khoảng 100 MB)...', flush=True)
        if WIN:
            giai_nen(tai('https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip', may / 'tai-ve' / 'ffmpeg.zip', ten='ffmpeg'), fdir)
        elif MAC:
            for ten in ('ffmpeg', 'ffprobe'):
                giai_nen(tai(f'https://evermeet.cx/ffmpeg/getrelease/{ten}/zip', may / 'tai-ve' / f'{ten}.zip', ten=ten), fdir / 'bin')
                os.chmod(fdir / 'bin' / ten, 0o755)
        tim = next(iter(fdir.rglob('ffmpeg.exe' if WIN else 'ffmpeg')), None)
    if not tim or chay([tim, '-version'], capture_output=True).returncode:
        dung(f'Không chạy được FFmpeg ({tim}). Máy có thể đang chặn (Smart App Control, diệt virus). Chụp màn hình gửi người hướng dẫn.')
    bin_.append(str(tim.parent))
    # node
    ndir = may / 'node'
    node = next(iter(ndir.glob('*/node.exe' if WIN else '*/bin/node')), None) if ndir.exists() else None
    if not node and shutil.which('node'):
        r = chay(['node', '-v'], capture_output=True, text=True)
        if r.returncode == 0 and int(re.sub(r'\D.*', '', r.stdout.strip().lstrip('v')) or 0) >= 18:
            node = Path(shutil.which('node'))
    if not node:
        print(f'Tải Node {NODE_BAN} (khoảng 30 MB)...', flush=True)
        kien = 'arm64' if platform.machine().lower() in ('arm64', 'aarch64') else 'x64'
        ten = f'node-{NODE_BAN}-win-x64.zip' if WIN else f'node-{NODE_BAN}-darwin-{kien}.tar.gz'
        giai_nen(tai(f'https://nodejs.org/dist/{NODE_BAN}/{ten}', may / 'tai-ve' / ten, ten='node'), ndir)
        node = next(iter(ndir.glob('*/node.exe' if WIN else '*/bin/node')), None)
    if not node or chay([node, '-v'], capture_output=True).returncode:
        dung(f'Không chạy được Node ({node}). Chụp màn hình gửi người hướng dẫn.')
    bin_.append(str(node.parent))
    for d in reversed(bin_):
        os.environ['PATH'] = d + os.pathsep + os.environ['PATH']
    print(f'✔ FFmpeg: {tim}\n✔ Node: {node}')
    return bin_


def thu_vien(uv, gpu):
    goi = THU_VIEN + (['nvidia-cublas-cu12', 'nvidia-cudnn-cu12'] if gpu else [])
    r = chay([uv, 'pip', 'install', '--python', sys.executable, '-q', *goi])
    if r.returncode:
        dung('Không cài được thư viện Python. Kiểm mạng rồi dán lại câu lệnh.')
    print('✔ thư viện Python:', ', '.join(goi))
    va_faster_whisper()
    vc_runtime(uv)
    # Kiểm thật: thư viện nạp được DLL không (thiếu Visual C++, bị Smart App Control chặn). Trước đây chỉ ⚠ ở bước Whisper
    # rồi hỏng lúc làm video đầu tiên.
    r = chay([sys.executable, '-c', 'import ctranslate2, onnxruntime, cv2, av, faster_whisper'], capture_output=True, text=True)
    if r.returncode:
        loi = (r.stderr.strip().splitlines() or ['?'])[-1]
        dung(f'Thư viện của xưởng chưa chạy được trên máy này ({loi}). '
             + ('Nếu có chữ "Application Control" là Windows đang chặn (Smart App Control hoặc diệt virus): chụp màn hình gửi người hướng dẫn. '
                'Nếu có chữ "DLL load failed": cài bộ Visual C++ của Microsoft tại https://aka.ms/vs/17/release/vc_redist.x64.exe '
                '(bấm Có khi Windows hỏi), rồi dán lại câu lệnh.' if WIN else 'Chụp màn hình gửi người hướng dẫn.'))
    print('✔ thư viện nạp được (nghe giọng, xử lý hình, âm thanh)')
    if chay([sys.executable, '-m', 'playwright', 'install', 'chromium'], capture_output=True).returncode:
        cb('Chưa tải được trình duyệt chụp trang web (chỉ cần khi làm video có chụp web); lần dùng đầu sẽ tự tải.')


def va_faster_whisper():
    """faster-whisper 1.2.1 gọi av.open(..., metadata_errors=...), av 19 bỏ tham số này nên transcribe(<tên tệp>) đổ
    TypeError (skill KOL, ab-edit). Không ghim av cũ được: av 18 bị Smart App Control chặn DLL (thử 25/11/2026).
    Vá đúng chỗ đó trong venv của xưởng; chạy lại bộ cài thì vá lại."""
    import importlib.util
    spec = importlib.util.find_spec('faster_whisper')
    if not spec or not spec.submodule_search_locations:
        return
    f = Path(list(spec.submodule_search_locations)[0]) / 'audio.py'
    s = f.read_text(encoding='utf-8')
    if 'metadata_errors="ignore"' in s:
        f.write_text(s.replace(', metadata_errors="ignore"', ''), encoding='utf-8')
        print('✔ vá faster-whisper cho khớp thư viện âm thanh av 19')


# Không chép vcruntime140: Python gốc đã mang bản 14.42 và đang dùng nó (chép đè lỗi WinError 32, thử 25/11/2026);
# msvcp140 14.51 nạp được cùng vcruntime 14.42 (đã đo).
VC_DLL = ('msvcp140', 'concrt140', 'vcomp140')


def vc_runtime(uv):
    """Bộ nghe giọng (ctranslate2) và bộ dò tiếng nói (onnxruntime) cần msvcp140.dll, msvcp140_1.dll của Microsoft; Python
    của xưởng chỉ mang vcruntime140. Máy chưa cài Visual C++ Redistributable thì lỗi DLL (học viên gặp với bộ cài cũ,
    25/11/2026; bộ cài cũ bắt cài vc_redist, hiện bảng hỏi quyền quản trị). Cách không cần quyền: gói msvc-runtime (DLL
    Microsoft có chữ ký) rồi chép CẢ BỘ vào thư mục Python gốc (sys.base_prefix): python.exe của venv chỉ là lối gọi, tiến
    trình thật chạy từ thư mục gốc nên Windows tìm DLL ở đó trước System32 (đã đo GetModuleFileName). Máy đã có
    Visual C++ thì không đụng. XUONG_THU_VCRT=1: ép chạy để thử."""
    if not WIN:
        return
    he = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32'
    goc = Path(sys.base_prefix)
    if (all((he / f'{x}.dll').exists() for x in ('msvcp140', 'msvcp140_1')) or (goc / 'msvcp140_1.dll').exists()) \
            and not os.environ.get('XUONG_THU_VCRT'):
        return
    print('Máy chưa có bộ Visual C++ của Microsoft: chép bản đi kèm cho xưởng (không cần quyền quản trị)...', flush=True)
    chay([uv, 'pip', 'install', '--python', sys.executable, '-q', 'msvc-runtime'])
    nguon = Path(sys.prefix) / 'Scripts'
    dll = [f for f in nguon.glob('*.dll') if f.name.lower().startswith(VC_DLL)]
    if not any(f.name.lower() == 'msvcp140_1.dll' for f in dll):
        return  # bước kiểm thư viện ngay sau sẽ DỪNG kèm cách cài tay
    for f in dll:
        try:
            shutil.copy2(f, goc / f.name)
        except OSError:
            pass  # tệp đang được dùng: bản trong thư mục gốc vẫn chạy; bước kiểm thư viện ngay sau sẽ bắt nếu thiếu
    print(f'✔ Visual C++ cho xưởng: {len(dll)} tệp vào {goc}')


def engine(nguon: Path, may: Path):
    src = nguon / 'goi' / 'video-nguoi-noi' / 'skills' / 'video-ngan-nguoi-noi' / 'engine'
    dich = may / 'engine'
    shutil.copytree(src, dich, dirs_exist_ok=True)
    npm = shutil.which('npm.cmd' if WIN else 'npm')
    npx = shutil.which('npx.cmd' if WIN else 'npx')
    if not (dich / 'node_modules').exists():
        print('Cài Remotion (bộ dựng video, vài phút)...', flush=True)
        if chay([npm, 'install', '--no-audit', '--no-fund', '--loglevel=error'], cwd=dich).returncode:
            dung('Không cài được Remotion (npm install). Kiểm mạng rồi dán lại câu lệnh.')
    if chay([npx, 'remotion', 'browser', 'ensure'], cwd=dich, capture_output=True).returncode:
        cb('Chưa tải được trình duyệt dựng hình của Remotion; lần dựng đầu sẽ tự tải.')
    print('✔ Remotion:', dich)
    return dich


def whisper(ram, gpu):
    # GPU mà RAM dưới 8 GB thì vẫn small: học viên máy 3,9 GB tải large-v3 3 GB rồi không mở được (25/11/2026, bộ cài cũ)
    ten = 'large-v3' if (ram >= 16 or (gpu and ram >= 8)) else 'small'
    print(f'Tải mô hình nghe lời Whisper "{ten}" ({"khoảng 3 GB" if ten == "large-v3" else "khoảng 500 MB"}, chỉ lần đầu)...', flush=True)
    if chay([sys.executable, '-c', f"from faster_whisper.utils import download_model; download_model('{ten}')"]).returncode:
        cb(f'Chưa tải được mô hình Whisper "{ten}"; lần làm video đầu sẽ tự tải.')
    return ten


# ---------------------------------------------------------------- bộ não

def xuong_da_cai(bo_nao: Path):
    """Ngăn xưởng đã cài: thư mục con có xuong.json của bộ cài (kể cả khi học viên đã đổi tên ngăn), ưu tiên *_XUONG_VIDEO."""
    ung = sorted(d for d in bo_nao.iterdir() if d.is_dir() and (d / 'xuong.json').is_file() and (d / 'tai-nguyen').is_dir())
    ung.sort(key=lambda d: not d.name.endswith('_XUONG_VIDEO'))
    return ung[0] if ung else None


def tim_xuong(bo_nao: Path):
    """Ngăn xưởng: dùng lại ngăn đã cài; không thì 08_XUONG_VIDEO, trùng số thì lấy số trống kế tiếp."""
    if (d := xuong_da_cai(bo_nao)):
        return d
    so = {int(m.group(1)) for d in bo_nao.iterdir() if d.is_dir() and (m := re.match(r'^(\d{2})_', d.name))}
    n = 8
    while n in so:
        n += 1
    return bo_nao / f'{n:02d}_XUONG_VIDEO'


def chep_khong_de(src: Path, dich: Path):
    """Chép thư mục mẫu: tệp chưa có thì chép, có rồi thì giữ (của học viên)."""
    for f in src.rglob('*'):
        d = dich / f.relative_to(src)
        if f.is_dir():
            d.mkdir(parents=True, exist_ok=True)
        elif not d.exists():
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, d)


def thay_khoi(tep: Path, khoi: str, tao_moi_dau=''):
    """Ghi khối giữa hai dấu XUONG-VIDEO; lần sau thay đúng khối đó, không đụng phần còn lại."""
    cu = tep.read_text(encoding='utf-8') if tep.exists() else tao_moi_dau
    moi = f'{DAU}\n{khoi.strip()}\n{CUOI}'
    if DAU in cu and CUOI in cu:
        cu = cu[:cu.index(DAU)] + moi + cu[cu.index(CUOI) + len(CUOI):]
    else:
        cu = cu.rstrip() + '\n\n' + moi + '\n'
    tep.write_text(cu, encoding='utf-8', newline='\n')


def chuoi_bo_sung(pb, tu, den):
    """Các gói bổ sung nối từ bản học viên đang có tới bản mới nhất (v1→v2→v3). Thiếu một mắt xích thì None (tải gói đủ)."""
    bs = pb.get('goi_bo_sung') or {}
    chuoi, cur = [], tu
    while cur != den:
        g = next((x for x in bs.values() if isinstance(x, dict) and x.get('tu') == cur), None)
        if not g or len(chuoi) > 50:
            return None
        chuoi.append(g)
        cur = g['den']
    return chuoi or None


def tep_cua_goi(nguon: Path, goi_canh: str):
    """Đường dẫn trong zip (tai-nguyen/<loai>/<tep>) mà máy này cần theo chỉ mục mới: cảnh đúng gói nhẹ/đủ, mọi nhạc, tiếng."""
    hop = set()
    for loai in ('canh', 'nhac', 'am'):
        with open(nguon / 'tai-nguyen' / loai / 'chi-muc.csv', encoding='utf-8-sig') as f:
            for x in csv.DictReader(f):
                if x.get('chu', 'kho') != 'kho' or (loai == 'canh' and goi_canh not in x.get('goi', '').split(';')):
                    continue
                for cot in ('tep', 'xem_truoc'):
                    if x.get(cot):
                        hop.add(f'tai-nguyen/{loai}/{x[cot]}')
    return hop


def ke_hoach_tai(pb, da, goi_canh):
    """Cần tải gì: ('khong', [], 0) | ('bo-sung', [gói...], MB) | ('du', [tên gói...], MB). da = xuong.json đang có."""
    ptn, cu = pb['phien_ban_tai_nguyen'], da.get('phien_ban_tai_nguyen')
    cung_goi = da.get('may', {}).get('goi_tai_nguyen') == goi_canh
    if cu == ptn and cung_goi:
        return 'khong', [], 0
    chuoi = chuoi_bo_sung(pb, cu, ptn) if cu and cung_goi else None
    if chuoi:
        return 'bo-sung', chuoi, sum(g['mb'] for g in chuoi)
    can = [f'kho-canh-{goi_canh}', 'nhac-am']
    return 'du', can, sum(pb['goi_tai_nguyen'][t]['mb'] for t in can)


def o_trong_gb(p: Path):
    """Dung lượng trống (GB) của ổ chứa p. XUONG_THU_O_TRONG chỉ để thử."""
    return float(os.environ.get('XUONG_THU_O_TRONG') or shutil.disk_usage(p).free / 2 ** 30)


def kiem_o(may: Path, xuong: Path, mb_tai: int):
    """Trước khi tải: gói zip nằm ở thư mục phần mềm, giải nén vào xưởng. Cùng ổ thì cần gấp đôi. Dư thêm 1 GB."""
    if not mb_tai:
        return
    may.mkdir(parents=True, exist_ok=True)
    cung_o = os.path.splitdrive(str(may.resolve()))[0].lower() == os.path.splitdrive(str(xuong.resolve()))[0].lower() if WIN \
        else os.stat(may).st_dev == os.stat(xuong).st_dev
    for noi, can in ([(xuong, mb_tai * 2)] if cung_o else [(may, mb_tai), (xuong, mb_tai)]):
        con = o_trong_gb(noi)
        if con < can / 1024 + 1:
            dung(f'Ổ chứa {noi} còn {con:.1f} GB, cần khoảng {can / 1024 + 1:.1f} GB để tải và giải nén {mb_tai} MB tài nguyên. '
                 'Dọn bớt ổ (đổ Thùng rác, xóa video cũ không cần) rồi gõ lại lệnh cập nhật. Chưa có gì bị thay đổi.')


def tai_nguyen(nguon: Path, may: Path, xuong: Path, goi_canh: str, sl=None):
    pb = json.loads((nguon / 'PHIEN_BAN.json').read_text(encoding='utf-8'))
    da = json.loads((xuong / 'xuong.json').read_text(encoding='utf-8')) if (xuong / 'xuong.json').exists() else {}
    ptn = pb['phien_ban_tai_nguyen']
    kieu, ds, mb_tai = ke_hoach_tai(pb, da, goi_canh)
    kiem_o(may, xuong, mb_tai)
    chuoi = ds if kieu == 'bo-sung' else None
    can = ds if kieu == 'du' else []
    if kieu == 'khong':
        print(f'✔ tài nguyên {ptn} đã có, bỏ qua tải')
    elif chuoi:
        # Đang ở bản cũ: chỉ tải gói bổ sung (tệp mới/đổi), lọc theo gói nhẹ/đủ bằng chỉ mục mới của kho
        hop = tep_cua_goi(nguon, goi_canh)
        for g in chuoi:
            print(f'Tải gói bổ sung {g["tu"]} → {g["den"]} ({g["mb"]} MB)...', flush=True)
            z = tai(g['url'], may / 'tai-ve' / Path(g['url']).name, sha=g['sha256'], ten=f'bổ sung {g["den"]}')
            moi = 0
            with zipfile.ZipFile(z) as zf:
                for m in zf.infolist():
                    if m.is_dir() or 'cua-toi' in m.filename or m.filename not in hop:
                        continue
                    d = xuong / m.filename
                    d.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(m) as s, open(d, 'wb') as o:
                        shutil.copyfileobj(s, o, 1 << 20)
                    moi += 1
            print(f'✔ bổ sung {g["den"]}: {moi} tệp mới hoặc đã đổi')
            z.unlink()
    else:
        for ten in can:
            g = pb['goi_tai_nguyen'][ten]
            print(f'Tải gói {ten} ({g["mb"]} MB)...', flush=True)
            z = tai(g['url'], may / 'tai-ve' / Path(g['url']).name, sha=g['sha256'], ten=ten)
            moi = giu = 0
            with zipfile.ZipFile(z) as zf:
                for m in zf.infolist():
                    if m.is_dir() or 'cua-toi' in m.filename:
                        continue
                    d = xuong / m.filename
                    if d.exists() and d.stat().st_size == m.file_size:
                        giu += 1
                        continue
                    d.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(m) as s, open(d, 'wb') as o:
                        shutil.copyfileobj(s, o, 1 << 20)
                    moi += 1
            print(f'✔ {ten}: {moi} tệp mới, {giu} tệp đã có')
            z.unlink()  # gói zip đã giải nén, xóa cho nhẹ máy
    # Chỉ mục: dòng của kho (lọc theo gói nhe/du, bỏ dòng ẩn) + giữ nguyên dòng của học viên
    for loai in ('canh', 'nhac', 'am'):
        src, dich = nguon / 'tai-nguyen' / loai, xuong / 'tai-nguyen' / loai
        dich.mkdir(parents=True, exist_ok=True)
        with open(src / 'chi-muc.csv', encoding='utf-8-sig') as f:
            r = csv.DictReader(f)
            cot, kho = r.fieldnames, [x for x in r if goi_canh in x.get('goi', '').split(';')]
        hv = []
        if (dich / 'chi-muc.csv').exists():
            # Giữ MỌI dòng không phải của kho (kể cả dòng học viên ghi thiếu nhãn chu=hoc-vien); cất bản cũ trước khi ghi lại
            with open(dich / 'chi-muc.csv', encoding='utf-8-sig') as f:
                ma_kho = {x['ma'] for x in kho}
                hv = [x for x in csv.DictReader(f) if (x.get('chu') or '').strip() != 'kho' and x.get('ma') not in ma_kho]
            if hv and sl:
                sl.cat_truoc_khi_ghi(dich / 'chi-muc.csv')
        with open(dich / 'chi-muc.csv', 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=cot, extrasaction='ignore')
            w.writeheader()
            w.writerows(kho + hv)
        thieu = [x['ma'] for x in kho if x.get('trang_thai', 'dung') == 'dung' and not (dich / x['tep']).exists()]
        if thieu:
            cb(f'{loai}: {len(thieu)} tệp trong chỉ mục chưa có trên máy ({", ".join(thieu[:5])}...)')
        (dich / 'cua-toi').mkdir(exist_ok=True)
    # Sinh CHI_MUC.md từ chỉ mục vừa ghi, bằng đúng hàm của người làm kho
    os.environ['XUONG_REPO'] = str(xuong)
    sys.path.insert(0, str(nguon / 'cong-cu'))
    import importlib
    import chung as kho_chung
    kho_chung = importlib.reload(kho_chung)  # đường dẫn đọc lúc nạp: nạp lại cho đúng xưởng này
    for loai in ('canh', 'nhac', 'am'):
        kho_chung.sinh_md(loai)
    return ptn


VAI_THEO_SO = {'01': 'ho-so', '02': 'san-pham', '03': 'khach-hang', '04': 'giong-van', '05': 'quy-trinh', '06': 'media', '07': 'cong-ty'}


def ban_do_bo_nao(bo_nao: Path, xuong: Path):
    """Dò ngăn thật của bộ não (tên có thể khác nhau giữa các học viên), ghi BAN_DO_BO_NAO.md; giữ phần học viên tự gán vai."""
    idx = (bo_nao / 'INDEX.md').read_text(encoding='utf-8', errors='replace').splitlines() if (bo_nao / 'INDEX.md').exists() else []
    dong = []
    for d in sorted(x for x in bo_nao.iterdir() if x.is_dir() and re.match(r'^\d{2}_', x.name) and x != xuong):
        mo_ta = next((re.sub(r'[`*\[\]|#>-]+', ' ', l).replace(d.name, '').strip(' :—–./') for l in idx if d.name in l), '')
        dong.append(f'| {VAI_THEO_SO.get(d.name[:2], "khac")} | {d.name}/ | {mo_ta[:120]} |')
    p = xuong / 'BAN_DO_BO_NAO.md'
    giu = ''
    if p.exists() and 'Học viên đã trả lời' in (cu := p.read_text(encoding='utf-8')):
        giu = cu[cu.index('Học viên đã trả lời'):]
    p.write_text('\n'.join([
        '# BẢN ĐỒ BỘ NÃO (bộ cài tự dò, AI đọc khi cần lời và dữ liệu cho video)', '',
        f'> Ngày dò: {time.strftime("%Y-%m-%d")}. Khi `INDEX.md` của bộ não mới hơn ngày này, AI dò lại trước khi làm video.',
        '> Lời video chỉ lấy từ các ngăn dưới đây, không bịa. Thiếu thì hỏi, rồi đề nghị lưu vào đúng ngăn.', '',
        '| Vai trò | Ngăn thật trong bộ não | Mô tả từ INDEX.md |', '|---|---|---|', *dong, '',
        giu or 'Học viên đã trả lời gán vai trò (giữ lại khi dò lại):\n| Ngăn | Vai trò | Ngày |\n|---|---|---|\n']), encoding='utf-8', newline='\n')


def chi_muc_xuong(src: Path, dich: Path):
    """CHI_MUC_XUONG.md: mục 1–4 của bộ cài (thay mới), mục 5 của học viên (giữ)."""
    moi = src.read_text(encoding='utf-8')
    if dich.exists():
        cu = dich.read_text(encoding='utf-8')
        if '\n## 5.' in cu and '\n## 5.' in moi:
            moi = moi[:moi.index('\n## 5.')] + cu[cu.index('\n## 5.'):]
    dich.write_text(moi, encoding='utf-8', newline='\n')


def khoi_claude(xuong: Path, cfg: dict):
    py = cfg['python']
    return f"""## Xưởng Video AI (bộ cài ghi, cập nhật sẽ thay khối này)

- Mọi việc làm video: đọc `{xuong.name}/CHI_MUC_XUONG.md` trước tiên, rồi dùng đúng skill đã cài trong `.claude/skills/`.
- Chọn cảnh, nhạc, tiếng hiệu ứng qua `{xuong.name}/tai-nguyen/<canh|nhac|am>/CHI_MUC.md`; xem ảnh `tai-nguyen/canh/xem-truoc/<mã>.jpg` khi cần nhìn. Không mở lần lượt từng video, không đọc lướt thư mục phần mềm của xưởng.
- Lời trong video lấy từ ngăn 01–05 của bộ não (xem `{xuong.name}/BAN_DO_BO_NAO.md`). Không bịa; thiếu thì hỏi.
- Trước việc cần tài khoản, khóa hay máy mạnh: kiểm theo `{xuong.name}/CHUAN_BI_THEM.md`. Đủ thì làm luôn theo ý người dùng; thiếu thì báo cần chuẩn bị gì, có tốn phí không, và đề xuất cách làm được ngay với thứ đang có.
- Chạy script của skill xưởng bằng Python riêng của xưởng: `"{py}"` (ví dụ `"{py}" -X utf8 .claude/skills/video-ngan-nguoi-noi/scripts/bni.py ...`). FFmpeg và Node của xưởng ghi trong `.claude/xuong-video.json` mục `bin`.
- Mỗi video một thư mục `{xuong.name}/du-an/<ngày>_<tên>/`; thành phẩm chép ra `{xuong.name}/thanh-pham/`.
- Thứ có chữ `cua-toi` hoặc dòng `chu=hoc-vien` là của người dùng: không xóa, không ghi đè. Muốn đổi cách làm thì ghi vào `{xuong.name}/mau-cua-toi/`, không sửa skill gốc.
- Cập nhật xưởng: dán lại câu lệnh cài (trong `{xuong.name}/CHI_MUC_XUONG.md` cuối tệp)."""


def dung_thu(xuong: Path, may: Path):
    """Dựng thử 3 giây từ 1 cảnh + nhạc để chắc FFmpeg, kho tài nguyên chạy được."""
    with open(xuong / 'tai-nguyen' / 'canh' / 'chi-muc.csv', encoding='utf-8-sig') as f:
        c = next((x for x in csv.DictReader(f) if (xuong / 'tai-nguyen' / 'canh' / x['tep']).exists()), None)
    with open(xuong / 'tai-nguyen' / 'nhac' / 'chi-muc.csv', encoding='utf-8-sig') as f:
        n = next((x for x in csv.DictReader(f) if (xuong / 'tai-nguyen' / 'nhac' / x['tep']).exists()), None)
    if not c or not n:
        cb('Không dựng thử được: thiếu cảnh hoặc nhạc.')
        return False
    ra = may / 'dung-thu.mp4'
    r = chay(['ffmpeg', '-y', '-v', 'error', '-i', xuong / 'tai-nguyen' / 'canh' / c['tep'], '-i', xuong / 'tai-nguyen' / 'nhac' / n['tep'],
              '-t', '3', '-c:v', 'libx264', '-preset', 'veryfast', '-c:a', 'aac', '-shortest', ra], capture_output=True, text=True)
    if r.returncode or not ra.exists():
        cb(f'Dựng thử hỏng: {r.stderr[-300:]}')
        return False
    ra.unlink()
    return True


# ---------------------------------------------------------------- chính

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bo-nao', required=True)
    ap.add_argument('--may', required=True)
    ap.add_argument('--nguon', required=True)
    ap.add_argument('--uv', required=True)
    ap.add_argument('--goi', choices=['nhe', 'du'])
    a = ap.parse_args()
    bo_nao, may, nguon = Path(a.bo_nao).resolve(), Path(a.may).resolve(), Path(a.nguon).resolve()
    pb = json.loads((nguon / 'PHIEN_BAN.json').read_text(encoding='utf-8'))

    # Cập nhật thường xuyên (/cap-nhat-xuong): đã đúng bản mới nhất và còn nguyên thì báo một dòng, không đụng gì.
    # XUONG_CAI_LAI=1 (người dùng nói "cài lại xưởng") thì chạy đủ các bước để sửa máy.
    # XUONG_XEM=1: chỉ xem trước sẽ làm gì, không thay đổi gì (Claude cho học viên xem rồi hỏi OK).
    # XUONG_DON_BAN_CU=1: học viên đã OK dọn bộ cài cũ ngày 24/11 (cứu đồ học viên trước, rồi Thùng rác).
    xem, don = bool(os.environ.get('XUONG_XEM')), bool(os.environ.get('XUONG_DON_BAN_CU'))
    x0 = xuong_da_cai(bo_nao)
    cu = json.loads((x0 / 'xuong.json').read_text(encoding='utf-8')) if x0 else {}
    ban_cu = cu.get('ngay_cai') and cu.get('phien_ban')
    cfg0 = bo_nao / '.claude' / 'xuong-video.json'
    try:
        con_nguyen = Path(json.loads(cfg0.read_text(encoding='utf-8'))['python']).exists() and \
            (bo_nao / '.claude' / 'skills' / 'video-ngan-nguoi-noi' / 'SKILL.md').exists()
    except Exception:
        con_nguyen = False
    vet = an_toan.do_ban_cu(bo_nao, nguon)
    moi_nhat = (not os.environ.get('XUONG_CAI_LAI') and con_nguyen and ban_cu == pb['phien_ban']
                and cu.get('phien_ban_tai_nguyen') == pb['phien_ban_tai_nguyen'])
    if xem:
        return xem_truoc(pb, cu, ban_cu, moi_nhat, bo_nao, x0, nguon, vet, a.goi)
    if moi_nhat:
        print(f'\n✔ ĐÃ LÀ BẢN MỚI NHẤT (mã {pb["phien_ban"]}, tài nguyên {pb["phien_ban_tai_nguyen"]}). Không có gì mới, không cần làm gì.')
        return bao_ban_cu(vet, don, x0, nguon)

    buoc('1/7 Kiểm máy')
    ram, gpu = ram_gb(), co_gpu()
    trong = shutil.disk_usage(bo_nao).free / 2 ** 30
    # Chọn gói cảnh theo ổ trống, không theo RAM: cảnh chỉ chiếm ổ, mỗi video dùng vài cảnh (đổi 25/11/2026; trước đây
    # máy dưới 16 GB RAM, tức đa số học viên, chỉ nhận 64 cảnh). Đang dùng gói nhẹ mà nay đủ ổ thì lên gói đủ một lần.
    goi_canh = a.goi or ('du' if trong >= 6 else 'nhe')
    print(f'Hệ điều hành {platform.system()} {platform.release()} · RAM {ram} GB · ổ bộ não còn {trong:.0f} GB · '
          f'{"có" if gpu else "không có"} GPU NVIDIA → kho cảnh gói "{goi_canh}"')
    if trong < 2:
        dung(f'Ổ chứa bộ não chỉ còn {trong:.1f} GB. Cần ít nhất 2 GB trống.')
    if any(k in str(bo_nao).lower() for k in DONG_BO):
        cb('Bộ não đang nằm trong thư mục đồng bộ mây (OneDrive, Google Drive, iCloud, Dropbox). Xưởng sẽ thêm 1–2 GB tài nguyên '
           'và video: đồng bộ chậm, tốn dung lượng mây, có lúc tệp "chỉ trên mây" làm dựng lỗi. Nên chuyển bộ não ra thư mục '
           'thường (ví dụ D:\\Bo-Nao-AI) rồi cập nhật lại. Claude: chỉ giải thích, không tự chuyển.')
    if ram < 8:
        cb(f'Máy có {ram} GB RAM (nên từ 8 GB). Vẫn làm được video BNI, edit video ngắn nhưng chậm: khi dựng hãy đóng bớt '
           f'Chrome và ứng dụng khác. Dùng mô hình nghe giọng nhỏ "small" cho vừa máy.')

    buoc('2/7 Phần mềm (FFmpeg, Node, thư viện Python)')
    bin_ = ffmpeg_node(may)
    thu_vien(a.uv, gpu)

    buoc('3/7 Bộ dựng video Remotion')
    eng = engine(nguon, may)

    buoc('4/7 Ngăn xưởng trong bộ não')
    xuong = tim_xuong(bo_nao)
    mau = nguon / 'xuong-mau' / '08_XUONG_VIDEO'
    chep_khong_de(mau, xuong)
    sl = an_toan.SaoLuu(bo_nao, xuong)
    chi_muc_xuong(mau / 'CHI_MUC_XUONG.md', xuong / 'CHI_MUC_XUONG.md')
    sl.chep(mau / 'CHUAN_BI_THEM.md', xuong / 'CHUAN_BI_THEM.md')
    ban_do_bo_nao(bo_nao, xuong)
    for d in ('du-an', 'thanh-pham', 'anh-video-cua-toi'):
        (xuong / d).mkdir(exist_ok=True)
    hs = xuong / 'ho-so-kenh.json'
    if not hs.exists():
        shutil.copy2(nguon / 'goi' / 'video-nguoi-noi' / 'skills' / 'video-ngan-nguoi-noi' / 'references' / 'ho-so-kenh.mau.json', hs)
    print('✔ ngăn xưởng:', xuong)

    buoc('5/7 Kho tài nguyên (cảnh, nhạc, tiếng)')
    ptn = tai_nguyen(nguon, may, xuong, goi_canh, sl)

    buoc('6/7 Skill, agent, mô hình nghe lời')
    claude = bo_nao / '.claude'
    goi_da, da_chep = [], []
    dk_skill = {}
    for gj in sorted((nguon / 'goi').glob('*/goi.json')):
        g = json.loads(gj.read_text(encoding='utf-8'))
        for s in g.get('skills', []):
            sl.chep_thu_muc(gj.parent / 'skills' / s, claude / 'skills' / s)
            da_chep.append(s)
            dk = g.get('dieu_kien_theo_skill', {})
            if dk.get(s) or dk.get('*'):
                dk_skill[s] = dk.get(s) or dk.get('*')
        for f in sorted((gj.parent / 'agents').glob('*.md')):
            sl.chep(f, claude / 'agents' / f.name)
        goi_da.append(g['ma'])
        print(f'✔ gói {g["ma"]}: {len(g.get("skills", []))} skill, {len(list((gj.parent / "agents").glob("*.md")))} agent')
    sl.ghi()
    if sl.hv_sua:
        cb(f'Anh/chị đã sửa {len(sl.hv_sua)} tệp gốc của xưởng ({", ".join(sl.hv_sua[:3])}{"..." if len(sl.hv_sua) > 3 else ""}). '
           f'Bản mới đã thay; bản anh/chị sửa được cất ở {sl.thu_muc}. Muốn giữ cách làm riêng lâu dài thì nói '
           f'"Lưu kiểu video này của tôi" (cất vào mau-cua-toi, cập nhật không đụng tới).')
    elif sl.chua_ro:
        print(f'✔ cất {len(sl.chua_ro)} tệp bản trước vào {sl.thu_muc} (phòng khi cần lấy lại)')
    wm = whisper(ram, gpu)
    cfg = {'_ghi_chu': 'Bộ cài Xưởng Video AI ghi tệp này; skill đọc để biết xưởng, phần mềm ở đâu. Chạy lại câu lệnh cài sẽ ghi lại.',
           'phien_ban': pb['phien_ban'], 'phien_ban_tai_nguyen': ptn, 'xuong': str(xuong), 'may': str(may),
           'python': sys.executable, 'bin': bin_, 'engine': str(eng), 'whisper_model': wm, 'goi_canh': goi_canh, 'ram_gb': ram}
    (claude / 'xuong-video.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')

    buoc('7/7 Ghi sổ, nối vào bộ não, dựng thử')
    xj = json.loads((xuong / 'xuong.json').read_text(encoding='utf-8'))
    dk = {k: v for k, v in xj.get('dieu_kien', {}).items()}
    dk['ram-16gb-nen-co'] = 'co' if ram >= 16 else 'khong'
    for k in ('khoa-google-vertex', 'tai-khoan-muse', 'claude-in-chrome'):
        dk.setdefault(k, 'kiem-khi-lam')
        if dk[k] == 'chua-kiem':
            dk[k] = 'kiem-khi-lam'
    xj.update({'phien_ban': pb['phien_ban'], 'phien_ban_tai_nguyen': ptn, 'thu_muc_xuong': xuong.name, 'may_video': str(may),
               'may': {'he_dieu_hanh': platform.system(), 'ram_gb': ram, 'goi_tai_nguyen': goi_canh, 'gpu_nvidia': gpu},
               'whisper': wm, 'goi_da_cai': goi_da, 'dieu_kien_theo_skill': dk_skill, 'dieu_kien': dk,
               'ngay_cai': time.strftime('%Y-%m-%d %H:%M')})
    (xuong / 'xuong.json').write_text(json.dumps(xj, ensure_ascii=False, indent=2), encoding='utf-8')
    thay_khoi(bo_nao / 'CLAUDE.md', khoi_claude(xuong, cfg))
    thay_khoi(bo_nao / 'INDEX.md', f'- `{xuong.name}/` — Xưởng Video AI: làm video bằng một câu nói. Đọc `{xuong.name}/CHI_MUC_XUONG.md` trước.')
    ok = dung_thu(xuong, may)

    print('\n' + '=' * 60)
    print('XƯỞNG SẴN SÀNG' if ok and not canh_bao else ('XƯỞNG ĐÃ CÀI (có lưu ý bên dưới)' if ok else 'CÀI XONG NHƯNG DỰNG THỬ CHƯA ĐẠT'))
    print('=' * 60)
    print(f'Ngăn xưởng: {xuong}\nPhần mềm: {may}\nKho cảnh gói "{goi_canh}", tài nguyên {ptn}, Whisper "{wm}"')
    print('\nLàm được ngay: Edit video, video giới thiệu bản thân BNI, video người nói, cắt livestream, biến thể quảng cáo.')
    can = []
    if dk['ram-16gb-nen-co'] != 'co':
        can.append('Cắt livestream dài: máy nên có 16 GB RAM (máy này chạy được nhưng chậm, nên cắt từng đoạn).')
    can.append('Ảnh bìa vẽ AI: cần khóa Google Vertex (xem CHUAN_BI_THEM.md).')
    can.append('Video KOL AI, cây cảnh: cần tài khoản Muse + Claude in Chrome (xem CHUAN_BI_THEM.md).')
    print('Muốn làm thêm thì cần chuẩn bị:\n  - ' + '\n  - '.join(can))
    for s in canh_bao:
        print('⚠', s)
    if ban_cu and ban_cu != pb['phien_ban']:
        print(f'\nĐÃ CẬP NHẬT {ban_cu} → {pb["phien_ban"]}. Có gì mới:')
        for d in co_gi_moi(pb, ban_cu):
            print(f'  - {d}')
    rc = bao_ban_cu(vet, don, xuong, nguon)
    print('\nĐÓNG HẲN Claude rồi mở lại đúng thư mục bộ não để Claude nhận skill và agent mới.')
    print('Thử ngay: "Dựng video giới thiệu bản thân cho tôi theo cấu trúc BNI".')
    return 2 if not ok else rc


DONG_BO = ('onedrive', 'google drive', 'googledrive', 'my drive', 'icloud', 'mobile documents', 'dropbox')


def co_gi_moi(pb, ban_cu):
    so = lambda s: tuple(int(x) for x in re.findall(r'\d+', s))  # noqa: E731
    moi = [d for b, d in sorted((pb.get('co_gi_moi') or {}).items(), key=lambda x: so(x[0])) if so(b) and so(ban_cu) < so(b)]
    return [x for d in moi for x in (d if isinstance(d, list) else [d])] or ['Sửa lỗi nhỏ, chạy ổn định hơn.']


def bao_ban_cu(vet, don, xuong, nguon):
    """Có dấu vết bộ cài cũ 24/11: chưa được OK thì liệt kê để Claude hỏi học viên; đã OK (XUONG_DON_BAN_CU=1) thì dọn."""
    if not an_toan.co_ban_cu(vet):
        if don:
            print('✔ Không còn dấu vết bộ cài cũ, không cần dọn.')
        return 0
    if don and xuong:
        print('\n== Dọn bộ cài cũ (anh/chị đã đồng ý)')
        bao, loi = an_toan.don_ban_cu(vet, xuong, nguon)
        for d in bao:
            print(('⚠ ' if loi else '✔ ') + d)
        if not loi:
            print('ĐÃ DỌN BẢN CŨ. Đóng hẳn Claude rồi mở lại để chỉ còn skill mới.')
        return 1 if loi else 0
    print('\n⚠ PHÁT HIỆN BẢN CŨ (bộ cài làm video ngày 24/11) trên máy:')
    for d in an_toan.mo_ta_ban_cu(vet):
        print('   -', d)
    print('   Đề xuất: chép giữ video, ảnh, hồ sơ, cấu hình riêng của anh/chị vào xưởng mới, kiểm đủ, rồi chuyển phần còn lại '
          'của bản cũ vào Thùng rác (lấy lại được). Phần mềm đã cài (FFmpeg, Node, Python, mô hình nghe giọng) giữ nguyên để dùng lại.')
    print('   Claude: giải thích danh sách trên cho học viên, hỏi OK. Đồng ý thì chạy lại đúng lệnh cài với biến XUONG_DON_BAN_CU=1.')
    return 0


def xem_truoc(pb, cu, ban_cu, moi_nhat, bo_nao, x0, nguon, vet, goi=None):
    """XUONG_XEM=1: in việc sẽ làm, không thay đổi gì."""
    print('\n== XEM TRƯỚC (chưa thay đổi gì trên máy)')
    if moi_nhat:
        print(f'✔ ĐÃ LÀ BẢN MỚI NHẤT (mã {pb["phien_ban"]}, tài nguyên {pb["phien_ban_tai_nguyen"]}). Không có gì mới.')
    else:
        dang = f'mã {ban_cu}, tài nguyên {cu.get("phien_ban_tai_nguyen")}' if ban_cu else 'chưa cài'
        print(f'Bản đang có: {dang} → bản mới: mã {pb["phien_ban"]}, tài nguyên {pb["phien_ban_tai_nguyen"]}')
        if ban_cu and ban_cu != pb['phien_ban']:
            print('Có gì mới:')
            for d in co_gi_moi(pb, ban_cu):
                print(f'  - {d}')
        goi_canh = goi or ('du' if o_trong_gb(bo_nao) >= 6 else 'nhe')
        kieu, _, mb_tai = ke_hoach_tai(pb, cu, goi_canh)
        print({'khong': 'Tài nguyên: đã đủ, không tải.',
               'bo-sung': f'Tài nguyên: chỉ tải phần bổ sung khoảng {mb_tai} MB.',
               'du': f'Tài nguyên: tải gói {"đủ" if goi_canh == "du" else "nhẹ"} khoảng {mb_tai} MB (một lần).'}[kieu])
        if x0:
            sl = an_toan.SaoLuu(bo_nao, x0, xem=True)
            for gj in sorted((nguon / 'goi').glob('*/goi.json')):
                g = json.loads(gj.read_text(encoding='utf-8'))
                for s in g.get('skills', []):
                    sl.chep_thu_muc(gj.parent / 'skills' / s, bo_nao / '.claude' / 'skills' / s)
                for f in sorted((gj.parent / 'agents').glob('*.md')):
                    sl.chep(f, bo_nao / '.claude' / 'agents' / f.name)
            if sl.hv_sua:
                print(f'Tệp gốc anh/chị đã sửa, sẽ được CẤT vào {x0.name}/.sao-luu/ trước khi thay: {", ".join(sl.hv_sua)}')
        print('Giữ nguyên: video đã làm, ảnh riêng, mẫu riêng, cảnh/nhạc/tiếng anh/chị tự thêm, hồ sơ kênh, các ngăn khác của bộ não.')
    if an_toan.co_ban_cu(vet):
        print('\nBản cũ (bộ cài 24/11) còn trên máy, có thể dọn nếu anh/chị đồng ý:')
        for d in an_toan.mo_ta_ban_cu(vet):
            print('   -', d)
    print('\nClaude: tóm tắt các dòng trên cho học viên và hỏi OK. Đồng ý thì chạy lại đúng lệnh, bỏ biến XUONG_XEM.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
