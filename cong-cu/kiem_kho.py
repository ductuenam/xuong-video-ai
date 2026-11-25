"""Kiểm toàn bộ kho: chạy ĐẦU mỗi phiên làm kho và SAU mỗi lần nhập, đóng gói.

    python -I -X utf8 cong-cu/kiem_kho.py           # kiểm nhanh (chỉ mục ↔ tệp ↔ PHIEN_BAN)
    python -I -X utf8 cong-cu/kiem_kho.py --sau     # thêm: giải nén thử gói mới nhất, so từng tệp

Kiểm:
1. Mã duy nhất; mỗi dòng chỉ mục có tệp thật (và ảnh xem trước với cảnh); đủ cột nhãn bắt buộc.
2. Không có tệp mồ côi trong kho chuẩn (tệp có mà chỉ mục không ghi).
3. Gói mới nhất trong goi/: SHA256SUMS khớp tệp zip và khớp PHIEN_BAN.json.
4. Báo số tệp đang chờ trong nguon-moi/.
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chung import BAN_CHUAN, CHI_MUC, GOI, LOAI, NGUON_MOI, PHIEN_BAN, doc_csv  # noqa: E402
from nhap_kho import BAT_BUOC  # noqa: E402

loi = []
if not BAN_CHUAN.exists():
    sys.exit('Không thấy kho nặng tại %s. Lối tắt _kho-nang phải trỏ tới E:\\xuong-video-ai-kho' % BAN_CHUAN)
for L in LOAI:
    rows = [r for r in doc_csv(CHI_MUC / L / 'chi-muc.csv') if r.get('chu') != 'hoc-vien']
    ma = [r['ma'] for r in rows]
    if len(ma) != len(set(ma)):
        loi.append('%s: trùng mã' % L)
    co = set()
    for r in rows:
        co.add(r['tep'])
        if not (BAN_CHUAN / L / r['tep']).exists():
            loi.append('%s %s: thiếu tệp %s' % (L, r['ma'], r['tep']))
        if L == 'canh':
            co.add(r['xem_truoc'])
            if not (BAN_CHUAN / L / r['xem_truoc']).exists():
                loi.append('%s: thiếu ảnh xem trước' % r['ma'])
        thieu = [c for c in BAT_BUOC[L] if not r.get(c, '').strip()]
        if thieu:
            loi.append('%s %s: thiếu nhãn %s' % (L, r['ma'], thieu))
    that = {str(p.relative_to(BAN_CHUAN / L)).replace('\\', '/') for p in (BAN_CHUAN / L).rglob('*') if p.is_file()}
    for t in sorted(that - co):
        loi.append('%s: tệp mồ côi (chưa có trong chỉ mục) %s' % (L, t))
    print('%-5s %4d dòng chỉ mục, %4d tệp' % (L, len(rows), len(that)))

pb = json.loads(PHIEN_BAN.read_text(encoding='utf-8'))
vs = sorted((p for p in GOI.iterdir() if p.is_dir() and p.name[1:].isdigit()), key=lambda p: int(p.name[1:]))
moi = vs[-1]
sums = dict(l.split()[::-1] for l in (moi / 'SHA256SUMS.txt').read_text().splitlines() if l.strip())
for ten, g in pb['goi_tai_nguyen'].items():
    n = '%s-%s.zip' % (ten, moi.name)
    h = hashlib.sha256((moi / n).read_bytes()).hexdigest()
    if h != sums.get(n):
        loi.append('%s: zip không khớp SHA256SUMS' % n)
    if h != g['sha256'] or ('/%s/' % moi.name) not in g['url']:
        loi.append('PHIEN_BAN.json chưa trỏ đúng %s (chạy dong_goi.py --ghi-phien-ban)' % n)
print('gói mới nhất:', moi.name, '| các phiên bản:', [p.name for p in vs])

if '--sau' in sys.argv:
    tmp = Path(tempfile.mkdtemp(prefix='zaios_kiem-kho_'))
    try:
        for n in sums:
            with zipfile.ZipFile(moi / n) as z:
                z.extractall(tmp / n)
                for t in z.namelist():
                    if (tmp / n / t).read_bytes() != (BAN_CHUAN.parent / t).read_bytes():
                        loi.append('%s: %s khác bản chuẩn (kho đã đổi sau khi đóng gói?)' % (n, t))
                print('giải nén thử', n, len(z.namelist()), 'tệp')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

cho = [p for p in NGUON_MOI.rglob('*') if p.is_file()]
print('đang chờ trong nguon-moi:', len(cho), 'tệp')
print('\nKHO SẠCH' if not loi else '\nCÓ %d LỖI:\n  ' % len(loi) + '\n  '.join(loi))
sys.exit(1 if loi else 0)
