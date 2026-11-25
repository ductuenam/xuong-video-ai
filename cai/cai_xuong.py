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
    ten = 'large-v3' if (ram >= 16 or gpu) else 'small'
    print(f'Tải mô hình nghe lời Whisper "{ten}" ({"khoảng 3 GB" if ten == "large-v3" else "khoảng 500 MB"}, chỉ lần đầu)...', flush=True)
    if chay([sys.executable, '-c', f"from faster_whisper.utils import download_model; download_model('{ten}')"]).returncode:
        cb(f'Chưa tải được mô hình Whisper "{ten}"; lần làm video đầu sẽ tự tải.')
    return ten


# ---------------------------------------------------------------- bộ não

def tim_xuong(bo_nao: Path):
    """Ngăn xưởng: dùng lại ngăn đã cài (có xuong.json); không thì 08_XUONG_VIDEO, trùng số thì lấy số trống kế tiếp."""
    for d in sorted(bo_nao.glob('*_XUONG_VIDEO')):
        if (d / 'xuong.json').exists():
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


def chep_de(src: Path, dich: Path):
    """Chép skill: tệp của kho chép đè, tệp học viên tự thêm (không có trong kho) giữ nguyên."""
    for f in src.rglob('*'):
        if '__pycache__' in f.parts:
            continue
        d = dich / f.relative_to(src)
        if f.is_dir():
            d.mkdir(parents=True, exist_ok=True)
        else:
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


def tai_nguyen(nguon: Path, may: Path, xuong: Path, goi_canh: str):
    pb = json.loads((nguon / 'PHIEN_BAN.json').read_text(encoding='utf-8'))
    da = json.loads((xuong / 'xuong.json').read_text(encoding='utf-8')) if (xuong / 'xuong.json').exists() else {}
    can = [f'kho-canh-{goi_canh}', 'nhac-am']
    ptn = pb['phien_ban_tai_nguyen']
    if da.get('phien_ban_tai_nguyen') == ptn and da.get('may', {}).get('goi_tai_nguyen') == goi_canh:
        print(f'✔ tài nguyên {ptn} đã có, bỏ qua tải')
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
            with open(dich / 'chi-muc.csv', encoding='utf-8-sig') as f:
                hv = [x for x in csv.DictReader(f) if x.get('chu') == 'hoc-vien']
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
    import chung as kho_chung
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

    buoc('1/7 Kiểm máy')
    ram, gpu = ram_gb(), co_gpu()
    trong = shutil.disk_usage(bo_nao).free / 2 ** 30
    goi_canh = a.goi or ('du' if ram >= 16 and trong >= 6 else 'nhe')
    print(f'Hệ điều hành {platform.system()} {platform.release()} · RAM {ram} GB · ổ bộ não còn {trong:.0f} GB · '
          f'{"có" if gpu else "không có"} GPU NVIDIA → kho cảnh gói "{goi_canh}"')
    if trong < 2:
        dung(f'Ổ chứa bộ não chỉ còn {trong:.1f} GB. Cần ít nhất 2 GB trống.')

    buoc('2/7 Phần mềm (FFmpeg, Node, thư viện Python)')
    bin_ = ffmpeg_node(may)
    thu_vien(a.uv, gpu)

    buoc('3/7 Bộ dựng video Remotion')
    eng = engine(nguon, may)

    buoc('4/7 Ngăn xưởng trong bộ não')
    xuong = tim_xuong(bo_nao)
    mau = nguon / 'xuong-mau' / '08_XUONG_VIDEO'
    chep_khong_de(mau, xuong)
    chi_muc_xuong(mau / 'CHI_MUC_XUONG.md', xuong / 'CHI_MUC_XUONG.md')
    shutil.copy2(mau / 'CHUAN_BI_THEM.md', xuong / 'CHUAN_BI_THEM.md')
    ban_do_bo_nao(bo_nao, xuong)
    for d in ('du-an', 'thanh-pham', 'anh-video-cua-toi'):
        (xuong / d).mkdir(exist_ok=True)
    hs = xuong / 'ho-so-kenh.json'
    if not hs.exists():
        shutil.copy2(nguon / 'goi' / 'video-nguoi-noi' / 'skills' / 'video-ngan-nguoi-noi' / 'references' / 'ho-so-kenh.mau.json', hs)
    print('✔ ngăn xưởng:', xuong)

    buoc('5/7 Kho tài nguyên (cảnh, nhạc, tiếng)')
    ptn = tai_nguyen(nguon, may, xuong, goi_canh)

    buoc('6/7 Skill, agent, mô hình nghe lời')
    claude = bo_nao / '.claude'
    goi_da, da_chep = [], []
    dk_skill = {}
    for gj in sorted((nguon / 'goi').glob('*/goi.json')):
        g = json.loads(gj.read_text(encoding='utf-8'))
        for s in g.get('skills', []):
            chep_de(gj.parent / 'skills' / s, claude / 'skills' / s)
            da_chep.append(s)
            dk = g.get('dieu_kien_theo_skill', {})
            if dk.get(s) or dk.get('*'):
                dk_skill[s] = dk.get(s) or dk.get('*')
        for f in sorted((gj.parent / 'agents').glob('*.md')):
            (claude / 'agents').mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, claude / 'agents' / f.name)
        goi_da.append(g['ma'])
        print(f'✔ gói {g["ma"]}: {len(g.get("skills", []))} skill, {len(list((gj.parent / "agents").glob("*.md")))} agent')
    # Skill trùng tên cài chung cho cả máy (~/.claude/skills) được Claude dùng TRƯỚC bản trong bộ não (thử 25/11/2026:
    # bản cũ chung máy làm video BNI tạo thư mục ảnh ngoài bộ não). Không tự xóa thư mục ngoài bộ não, chỉ báo.
    chung_may = Path.home() / '.claude' / 'skills'
    trung = [s for s in da_chep if (chung_may / s / 'SKILL.md').exists()]
    if trung:
        cb(f'Máy có bản CŨ cài chung của skill {", ".join(trung)} ở {chung_may}. Claude sẽ dùng bản cũ đó thay vì bản mới '
           f'trong bộ não. Claude: hỏi người dùng rồi chuyển các thư mục đó vào Thùng rác (không xóa hẳn), sau đó mở lại Claude.')
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
    print('\nĐÓNG HẲN Claude rồi mở lại đúng thư mục bộ não để Claude nhận skill và agent mới.')
    print('Thử ngay: "Dựng video giới thiệu bản thân cho tôi theo cấu trúc BNI".')
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
