"""An toàn dữ liệu học viên khi cài, cập nhật, dọn bản cũ (25/11/2026, xem docs/KE_HOACH_CAI_CAP_NHAT_AN_TOAN.md).

- SaoLuu: nhớ dấu vân tay mọi tệp của kho đã cài (<Xưởng>/.dau-van-tay.json). Trước khi thay một tệp của kho:
  học viên đã sửa (khác vân tay) hoặc chưa có vân tay (bản cài trước 0.2.7) thì cất bản đang có vào <Xưởng>/.sao-luu/<giờ>/.
- vao_thung_rac: dọn = chuyển vào Thùng rác (Windows Recycle Bin, Mac Trash), không xóa hẳn.
- do_ban_cu / don_ban_cu: dò dấu vết bộ cài cũ ngày 24/11 (chỉ đọc), và khi học viên đã OK thì cứu đồ học viên
  vào Xưởng, kiểm đủ, rồi mới đưa phần của bộ cài cũ vào Thùng rác.

Biến môi trường chỉ để thử trên bộ não giả: XUONG_NHA (thư mục nhà giả), XUONG_THU_RAC (thư mục thay Thùng rác).
"""
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

WIN = sys.platform == 'win32'
MAC = sys.platform == 'darwin'
BO_QUA = ('node_modules', '__pycache__', '.cache')  # tệp sinh ra khi chạy, không phải đồ học viên


def sha(p: Path):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for k in iter(lambda: f.read(1 << 20), b''):
            h.update(k)
    return h.hexdigest()


def co_bo_qua(rel: Path):
    return any(x in BO_QUA for x in rel.parts) or rel.suffix == '.pyc'


def dung_luong(p: Path):
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob('*') if f.is_file()) if p.is_dir() else 0


def mb(n):
    return f'{n / 1e6:,.0f} MB' if n < 1e9 else f'{n / 1e9:,.1f} GB'


def nha():
    return Path(os.environ.get('XUONG_NHA') or Path.home())


# ---------------------------------------------------------------- sao lưu theo dấu vân tay

class SaoLuu:
    def __init__(self, bo_nao: Path, xuong: Path, xem=False):
        self.bo_nao, self.xuong, self.xem = bo_nao, xuong, xem
        self.tep_vt = xuong / '.dau-van-tay.json'
        try:
            self.cu = json.loads(self.tep_vt.read_text(encoding='utf-8')).get('tep', {})
        except Exception:
            self.cu = {}
        self.moi = {}
        self.thu_muc = xuong / '.sao-luu' / time.strftime('%Y-%m-%d_%H%M%S')
        self.hv_sua, self.chua_ro = [], []

    def _rel(self, p: Path):
        try:
            return p.relative_to(self.bo_nao).as_posix()
        except ValueError:
            return p.as_posix()

    def _cat(self, p: Path, rel: str):
        if self.xem:
            return
        d = self.thu_muc / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, d)

    def chep(self, src: Path, dich: Path):
        """Chép một tệp của kho vào chỗ cài; cất bản đang có nếu học viên đã sửa hoặc chưa rõ."""
        rel, h_moi = self._rel(dich), sha(src)
        if dich.is_file():
            h = sha(dich)
            if h != h_moi:
                vt = self.cu.get(rel)
                if vt is None:
                    self.chua_ro.append(rel)
                    self._cat(dich, rel)
                elif h != vt:
                    self.hv_sua.append(rel)
                    self._cat(dich, rel)
        if not self.xem:
            dich.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dich)
        self.moi[rel] = h_moi

    def chep_thu_muc(self, src: Path, dich: Path):
        """Chép skill: tệp của kho thay (có sao lưu như trên), tệp học viên tự thêm giữ nguyên."""
        for f in sorted(src.rglob('*')):
            if f.is_file() and not co_bo_qua(f.relative_to(src)):
                self.chep(f, dich / f.relative_to(src))

    def cat_truoc_khi_ghi(self, p: Path):
        """Cất một tệp sắp được ghi lại (ví dụ chỉ mục tài nguyên có dòng của học viên)."""
        if p.is_file():
            self._cat(p, self._rel(p))

    def ghi(self):
        if self.xem:
            return
        self.cu.update(self.moi)
        self.tep_vt.write_text(json.dumps({'_ghi_chu': 'Bộ cài ghi: mã kiểm từng tệp của kho đã cài, để biết tệp nào học viên '
                                           'đã sửa (sẽ được cất vào .sao-luu trước khi thay). Đừng sửa tay.', 'tep': self.cu},
                                          ensure_ascii=False, indent=0), encoding='utf-8')


# ---------------------------------------------------------------- Thùng rác

def vao_thung_rac(p: Path):
    """Chuyển tệp/thư mục vào Thùng rác. Trả True nếu đã đi khỏi chỗ cũ. Windows hỏi lại nếu quá to phải xóa hẳn."""
    p = p.resolve()
    thu = os.environ.get('XUONG_THU_RAC')
    if thu or MAC:
        rac = Path(thu) if thu else nha() / '.Trash'
        rac.mkdir(parents=True, exist_ok=True)
        dich, i = rac / p.name, 1
        while dich.exists():
            dich, i = rac / f'{p.stem} {i}{p.suffix}', i + 1
        shutil.move(str(p), str(dich))
        return not p.exists()
    if not WIN:
        return False
    import ctypes
    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [('hwnd', wintypes.HWND), ('wFunc', wintypes.UINT), ('pFrom', wintypes.LPCWSTR), ('pTo', wintypes.LPCWSTR),
                    ('fFlags', ctypes.c_uint16), ('fAnyOperationsAborted', wintypes.BOOL), ('hNameMappings', ctypes.c_void_p),
                    ('lpszProgressTitle', wintypes.LPCWSTR)]
    # FO_DELETE; FOF_ALLOWUNDO (vào Thùng rác) | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI | FOF_WANTNUKEWARNING
    # (quá to không vừa Thùng rác thì Windows hiện hộp hỏi, không lặng lẽ xóa hẳn)
    op = SHFILEOPSTRUCTW(None, 3, str(p) + '\0', None, 0x40 | 0x10 | 0x4 | 0x400 | 0x4000, False, None, None)
    ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    return not p.exists()


# ---------------------------------------------------------------- bộ cài cũ ngày 24/11

def _blob(p: Path):
    """Mã git-blob của tệp, và của bản đổi xuống dòng CRLF → LF (học viên tải bằng git trên Windows)."""
    b = p.read_bytes()
    ra = {hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()}
    if b'\r\n' in b:
        b2 = b.replace(b'\r\n', b'\n')
        ra.add(hashlib.sha1(b'blob %d\0' % len(b2) + b2).hexdigest())
    return ra


def _cua_ban_cu(dv, rel: str, p: Path):
    k = hashlib.sha1(rel.encode()).hexdigest()[:16]
    return bool(set(dv['tep'].get(k, [])) & _blob(p))


def do_ban_cu(bo_nao: Path, nguon: Path):
    """Chỉ đọc. Trả các thứ bộ cài cũ để lại, mỗi thứ kèm dung lượng."""
    dv = json.loads((nguon / 'cai' / 'ban-cu-24-11.json').read_text(encoding='utf-8'))
    h = nha()
    ket = {'skill': [], 'agent': [], 'video_ai': [], 'goi_kho': [], 'sao_luu_cu': [], 'la': [], '_dv': dv}
    for s in dv['skills']:
        d = h / '.claude' / 'skills' / s
        if not (d / 'SKILL.md').is_file():
            continue
        khop = sum(_cua_ban_cu(dv, f'.claude/skills/{s}/{f.relative_to(d).as_posix()}', f)
                   for f in d.rglob('*') if f.is_file() and not co_bo_qua(f.relative_to(d)))
        (ket['skill'] if khop >= 3 else ket['la']).append(d)
    for a in dv['agents']:
        a = a.removesuffix('.md')  # danh sách trong ban-cu-24-11.json ghi kèm đuôi
        f = h / '.claude' / 'agents' / f'{a}.md'
        if f.is_file():
            (ket['agent'] if _cua_ban_cu(dv, f'.claude/agents/{a}.md', f) else ket['la']).append(f)
    for d in dict.fromkeys([bo_nao.parent / 'Video-AI', bo_nao / 'Video-AI']):
        if d.is_dir() and ((d / 'ho-so-kenh.json').is_file() or (d / 'kho-canh').is_dir()):
            ket['video_ai'].append(d)
    for cho in ('Downloads', 'Desktop', 'Documents'):
        if (h / cho).is_dir():
            ket['goi_kho'] += sorted(x for x in (h / cho).iterdir() if x.name.upper().startswith('KHO-HOC-VIEN')
                                     and (x.is_dir() or x.suffix.lower() == '.zip'))
    cl = h / '.claude'
    if cl.is_dir():
        # bộ cài cũ cất bản cũ ở ~/.claude/sao-luu-<tên>/<giờ>/skill|agent/...
        ket['sao_luu_cu'] = sorted(d for d in cl.glob('sao-luu-*') if d.is_dir() and (any(d.glob('*/skill')) or any(d.glob('*/agent'))))
    return ket


def co_ban_cu(ket):
    return any(ket[k] for k in ('skill', 'agent', 'video_ai', 'goi_kho', 'sao_luu_cu'))


def mo_ta_ban_cu(ket):
    """Các dòng mô tả cho học viên (dùng cho cả xem trước và cảnh báo)."""
    d = []
    if ket['skill']:
        d.append(f'{len(ket["skill"])} skill cũ cài chung cả máy ({mb(sum(map(dung_luong, ket["skill"])))}): Claude dùng nhầm bản cũ thay bản mới')
    if ket['agent']:
        d.append(f'{len(ket["agent"])} agent cũ cài chung cả máy')
    for x in ket['video_ai']:
        d.append(f'Thư mục {x} ({mb(dung_luong(x))}): video, ảnh, hồ sơ của anh/chị sẽ được CHUYỂN vào xưởng mới; bản chép kho cũ bỏ đi')
    for x in ket['goi_kho']:
        d.append(f'Gói kho cũ {x} ({mb(dung_luong(x))})')
    if ket['sao_luu_cu']:
        d.append(f'{len(ket["sao_luu_cu"])} thư mục sao lưu của bộ cài cũ (được chép giữ lại trong xưởng trước khi bỏ)')
    for x in ket['la']:
        d.append(f'KHÔNG đụng: {x} trùng tên đồ của bộ cài cũ nhưng nội dung khác (có thể anh/chị tự làm)')
    return d


def _chep_giu(src: Path, dich: Path, ds):
    """Chép, không đè: trùng tên thì thêm ' (ban cu)', ' (ban cu 2)'..."""
    i, d = 1, dich
    while d.exists():
        d = dich.with_name(f'{dich.stem} (ban cu{"" if i == 1 else " " + str(i)}){dich.suffix}')
        i += 1
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, d)
    ds.append((src, d))


def don_ban_cu(ket, xuong: Path, nguon: Path):
    """Học viên đã OK. Cứu đồ học viên vào Xưởng → kiểm đủ → mới đưa phần của bộ cài cũ vào Thùng rác.
    Trả (các dòng báo, có lỗi không). Kiểm không khớp thì không dọn gì."""
    dv, ngay = ket['_dv'], time.strftime('%Y-%m-%d_%H%M%S')
    chuyen = xuong / 'chuyen-tu-ban-cu' / ngay
    da = []  # (nguồn, đích) đã chép
    # 1. Cứu: tệp trong skill cũ không thuộc bộ cài cũ (cấu hình, KOL, video mẫu tự thêm, tệp gốc đã sửa)
    for d in ket['skill']:
        for f in sorted(d.rglob('*')):
            r = f.relative_to(d)
            if f.is_file() and not co_bo_qua(r) and not _cua_ban_cu(dv, f'.claude/skills/{d.name}/{r.as_posix()}', f):
                _chep_giu(f, chuyen / 'skills' / d.name / r, da)
    # Thư mục Video-AI: video, ảnh, hồ sơ về đúng chỗ trong xưởng; bản chép kho cũ thì bỏ
    mau_hs = nguon / 'goi' / 'video-nguoi-noi' / 'skills' / 'video-ngan-nguoi-noi' / 'references' / 'ho-so-kenh.mau.json'
    for d in ket['video_ai']:
        for f in sorted(d.rglob('*')):
            if not f.is_file():
                continue
            r = f.relative_to(d)
            rp = r.as_posix()
            if f.stat().st_size in dv['kho'].get(rp, []):
                continue  # bản chép kho cũ: kho mới đã có
            if r.parts[0] in ('du-an', 'anh-video-cua-toi', 'thanh-pham') and len(r.parts) > 1:
                _chep_giu(f, xuong / r, da)
            elif rp == 'ho-so-kenh.json':
                hs = xuong / 'ho-so-kenh.json'
                mac_dinh = not hs.exists() or (mau_hs.is_file() and hs.read_bytes() == mau_hs.read_bytes())
                if mac_dinh:
                    hs.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, hs)
                    da.append((f, hs))
                else:
                    _chep_giu(f, xuong / 'ho-so-kenh.ban-cu.json', da)
            else:
                _chep_giu(f, chuyen / 'Video-AI' / r, da)
    for d in ket['sao_luu_cu']:
        for f in sorted(d.rglob('*')):
            if f.is_file() and not co_bo_qua(f.relative_to(d)):
                _chep_giu(f, chuyen / 'sao-luu-cu' / d.name / f.relative_to(d), da)
    # 2. Kiểm: mọi tệp đã chép phải có ở đích, đúng cỡ
    hong = [str(s) for s, t in da if not t.is_file() or t.stat().st_size != s.stat().st_size]
    if hong:
        return [f'Chép đồ của anh/chị chưa đủ ({len(hong)} tệp, ví dụ {hong[0]}). Chưa dọn gì.'], True
    # 3. Đưa phần của bộ cài cũ vào Thùng rác
    bo = ket['skill'] + ket['agent'] + ket['video_ai'] + ket['goi_kho'] + ket['sao_luu_cu']
    da_bo, khong_bo, giai_phong = [], [], 0
    for x in bo:
        n = dung_luong(x)
        if vao_thung_rac(x):
            da_bo.append(x)
            giai_phong += n
        else:
            khong_bo.append(x)
    # 4. Nhật ký
    nk = xuong / 'NHAT_KY_DON_BAN_CU.md'
    dong = [f'\n## Dọn bản cũ {ngay}\n', f'Đã chép giữ {len(da)} tệp của anh/chị:']
    dong += [f'- `{s}` → `{t}`' for s, t in da] or ['- (không có)']
    dong += ['', 'Đã chuyển vào Thùng rác (lấy lại được: mở Thùng rác, chuột phải → Restore/Khôi phục):']
    dong += [f'- `{x}`' for x in da_bo] or ['- (không có)']
    if khong_bo:
        dong += ['', 'Chưa chuyển được (tệp đang mở?):'] + [f'- `{x}`' for x in khong_bo]
    nk.write_text((nk.read_text(encoding='utf-8') if nk.exists() else '# Nhật ký dọn bộ cài cũ\n') + '\n'.join(dong) + '\n',
                  encoding='utf-8')
    bao = [f'Đã chép giữ {len(da)} tệp của anh/chị' + (f' (video, ảnh vào du-an/, anh-video-cua-toi/; thứ khác ở {chuyen})' if da else ''),
           f'Đã chuyển {len(da_bo)} mục của bản cũ vào Thùng rác, giải phóng khoảng {mb(giai_phong)}',
           f'Nhật ký: {nk}']
    if khong_bo:
        bao.append(f'{len(khong_bo)} mục chưa chuyển được (đóng các cửa sổ đang mở chúng rồi cập nhật lại): {", ".join(map(str, khong_bo[:3]))}')
    return bao, bool(khong_bo)
