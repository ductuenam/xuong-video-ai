"""Bước 5: đóng 3 gói zip cho một phiên bản tài nguyên và ghi mã kiểm vào PHIEN_BAN.json.

    python -I -X utf8 cong-cu/dong_goi.py --phien-ban v2            # đóng gói vào _kho-nang/goi/v2/
    python -I -X utf8 cong-cu/dong_goi.py --phien-ban v2 --ghi-phien-ban   # và cập nhật PHIEN_BAN.json

Luật:
- Mỗi phiên bản một thư mục goi/vN; thư mục đã có thì DỪNG (bản đã phát hành là khóa, không đóng đè).
- Zip kiểu store (không nén lại), gốc trong zip là tai-nguyen/..., ngày giờ cố định nên đóng lại ra đúng sha256.
- kho-canh-du: mọi cảnh + ảnh xem trước. kho-canh-nhe: cảnh có goi chứa 'nhe'. nhac-am: nhạc + tiếng.
- Chỉ đóng dòng chu=kho, trang_thai=dung. Không đưa chỉ mục vào zip (chỉ mục đi theo GitHub).
- Từ v2: đóng thêm bo-sung-<bản trước>-<bản này>.zip, chỉ tệp mới hoặc đã đổi; --ghi-phien-ban ghi vào mục goi_bo_sung.
  Học viên đang ở bản trước chỉ tải gói này (vài chục MB) thay vì tải lại gói đủ (thêm 25/11/2026). Tải lên R2 cả gói này.
"""
import argparse
import hashlib
import json
import sys
import zipfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chung import BAN_CHUAN, CHI_MUC, GOI, PHIEN_BAN, doc_csv  # noqa: E402

NGAY = (2026, 11, 25, 0, 0, 0)


def dong(p, ds):
    with zipfile.ZipFile(p, 'w', zipfile.ZIP_STORED) as z:
        for t in ds:
            zi = zipfile.ZipInfo(t, NGAY)
            zi.external_attr = 0o644 << 16
            z.writestr(zi, (BAN_CHUAN.parent / t).read_bytes())
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phien-ban', required=True, help='ví dụ v2')
    ap.add_argument('--ghi-phien-ban', action='store_true')
    a = ap.parse_args()
    v = a.phien_ban
    ra = GOI / v
    if ra.exists():
        sys.exit('DỪNG: %s đã có. Bản đã phát hành không đóng đè; dùng số phiên bản mới.' % ra)

    def dong_kho(loai):
        return [r for r in doc_csv(CHI_MUC / loai / 'chi-muc.csv') if r.get('chu') == 'kho' and r.get('trang_thai', 'dung') == 'dung']
    canh = dong_kho('canh')
    thieu = [r['ma'] for r in canh if not (BAN_CHUAN / 'canh' / r['tep']).exists() or not (BAN_CHUAN / 'canh' / r['xem_truoc']).exists()]
    am = [('nhac', r) for r in dong_kho('nhac')] + [('am', r) for r in dong_kho('am')]
    thieu += [r['ma'] for l, r in am if not (BAN_CHUAN / l / r['tep']).exists()]
    if thieu:
        sys.exit('DỪNG: chỉ mục trỏ tới tệp không có: %s' % thieu)

    def ds_canh(rs):
        return sorted(['tai-nguyen/canh/' + r['tep'] for r in rs] + ['tai-nguyen/canh/' + r['xem_truoc'] for r in rs])
    goi = {'kho-canh-du': ds_canh(canh),
           'kho-canh-nhe': ds_canh([r for r in canh if 'nhe' in r['goi']]),
           # nhạc trước, tiếng sau, mỗi loại xếp theo tên (giữ đúng thứ tự của v1)
           'nhac-am': [t for l in ('nhac', 'am') for t in sorted('tai-nguyen/%s/%s' % (l, r['tep']) for ll, r in am if ll == l)]}
    ra.mkdir(parents=True)
    ket = {}
    for ten, ds in goi.items():
        p = ra / ('%s-%s.zip' % (ten, v))
        h = dong(p, ds)
        mb = round(p.stat().st_size / 1e6)
        ket[ten] = (p.name, h, mb)
        print('%-26s %4d tệp %5d MB  %s' % (p.name, len(ds), mb, h))
    # Gói bổ sung: chỉ tệp mới hoặc đã đổi so với bản trước (học viên đang ở bản trước tải gói này, không tải lại gói đủ).
    # So theo CRC và cỡ trong zip của bản trước. Bản trước = bản đang ghi trong PHIEN_BAN.json.
    pb0 = json.loads(PHIEN_BAN.read_text(encoding='utf-8'))
    truoc = pb0.get('phien_ban_tai_nguyen')
    bo_sung = None
    if truoc and truoc != v and (GOI / truoc).is_dir():
        cu = {}
        for z in (GOI / truoc).glob('*.zip'):
            if z.name.startswith('bo-sung-'):
                continue
            with zipfile.ZipFile(z) as zf:
                cu.update({i.filename: (i.CRC, i.file_size) for i in zf.infolist()})
        tat_ca = sorted(set(goi['kho-canh-du']) | set(goi['nhac-am']))
        moi = []
        for t in tat_ca:
            b = (BAN_CHUAN.parent / t).read_bytes()
            if cu.get(t) != (zlib.crc32(b), len(b)):
                moi.append(t)
        p = ra / ('bo-sung-%s-%s.zip' % (truoc, v))
        h = dong(p, moi)
        mb = max(1, round(p.stat().st_size / 1e6))
        bo_sung = (truoc, p.name, h, mb)
        print('%-26s %4d tệp %5d MB  %s  (chỉ tệp mới/đổi so với %s)' % (p.name, len(moi), mb, h, truoc))
        ket_bs = {p.name: h}
    else:
        ket_bs = {}
    (ra / 'SHA256SUMS.txt').write_text(''.join('%s  %s\n' % (h, n) for n, h, _ in ket.values())
                                       + ''.join('%s  %s\n' % (h, n) for n, h in ket_bs.items()), encoding='utf-8', newline='\n')

    if a.ghi_phien_ban:
        pb = json.loads(PHIEN_BAN.read_text(encoding='utf-8'))
        for ten, (n, h, mb) in ket.items():
            g = pb['goi_tai_nguyen'][ten]
            g['url'] = g['url'].rsplit('/', 2)[0] + '/%s/%s' % (v, n)
            g['sha256'], g['mb'] = h, mb
        if bo_sung:
            tu, n, h, mb = bo_sung
            goc_url = pb['goi_tai_nguyen']['nhac-am']['url'].rsplit('/', 2)[0]
            pb.setdefault('goi_bo_sung', {})['%s-%s' % (tu, v)] = {
                'tu': tu, 'den': v, 'url': '%s/%s/%s' % (goc_url, v, n), 'sha256': h, 'mb': mb}
        pb['phien_ban_tai_nguyen'] = v
        PHIEN_BAN.write_text(json.dumps(pb, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
        print('Đã cập nhật PHIEN_BAN.json sang', v)


if __name__ == '__main__':
    main()
