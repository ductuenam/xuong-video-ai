"""Bước 4: nhập tài nguyên đã nén + đã gắn nhãn vào kho chuẩn, cấp mã mới, ghi chỉ mục.

    python -I -X utf8 cong-cu/nhap_kho.py --loai canh --nhan <nhan.csv>          # chạy thử, chỉ in
    python -I -X utf8 cong-cu/nhap_kho.py --loai canh --nhan <nhan.csv> --ghi    # ghi thật

nhan.csv (UTF-8, có tiêu đề), mỗi dòng một tệp:
    tep_goc   tên tệp nguồn. canh: nằm trong nguon-moi/_da-nen/; nhac, am: nằm trong nguon-moi/<loai>/
    nhom      nhóm có sẵn (xem CHI_MUC.md) hoặc nhóm mới; ten_nhom bắt buộc nếu nhóm mới
    slug      mô tả ngắn cho tên tệp: chữ thường không dấu, nối '-', tối đa 32 ký tự
    goi       'nhe;du' (vào cả gói nhẹ) hoặc 'du' (mặc định)
    nguon, giay_phep   ví dụ 'Muse', 'kho-chung' / 'pixabay'
    + mọi cột nhãn của loại đó (mo_ta, tu_khoa bắt buộc; xem docs/QUY_CHUAN_MO_RONG.md mục 3b, 3c)
Mã cấp tiếp theo số lớn nhất hiện có, không bao giờ dùng lại. Không đụng dòng chu=hoc-vien.
"""
import argparse
import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chung import BAN_CHUAN, CHI_MUC, LOAI, NGUON_MOI, cot_cua, doc_csv, ffprobe_giay, ghi_csv, sinh_md  # noqa: E402

BAT_BUOC = {'canh': ['mo_ta', 'tu_khoa', 'mau', 'chuyen_dong', 'cho_chu', 'doi_noi_dung', 'hop_video', 'co_dau_chu'],
            'nhac': ['mo_ta', 'tu_khoa', 'nhip_bpm', 'nang_luong', 'tam_trang', 'hop_video', 'doan', 'bat_dau_goi_y', 'do_lon_lufs'],
            'am': ['mo_ta', 'tu_khoa', 'giay', 'diem_nhan_s', 'do_lon', 'dung_khi']}


TU_DIEN_P = Path(__file__).resolve().parents[1] / 'goi' / 'video-nguoi-noi' / 'skills' / 'video-ngan-nguoi-noi' / 'references' / 'tu-dien-am.json'


def kiem_tu_dien(L, n):
    """Nhạc, tiếng phải dùng từ trong từ điển chung (tu-dien-am.json), giống luật của công cụ học viên them_am.py.
    tam_trang: từ đồng nghĩa tự đổi về từ chuẩn (ghi ngược vào n), từ lạ thì báo lỗi."""
    if L == 'canh':
        return []
    import json
    td = json.loads(TU_DIEN_P.read_text(encoding='utf-8'))
    loi, ten = [], n['tep_goc']
    gp = n.get('giay_phep', '').strip()
    if gp not in td['giay_phep_dung_duoc'] + list(td['giay_phep_khac']):
        loi.append('%s: giấy phép %r ngoài từ điển' % (ten, gp))
    if L == 'am':
        return loi
    chuan, la = [], []
    for x in re.split(r'[;,]', n.get('tam_trang', '')):
        x = x.strip()
        k = x if x in td['tam_trang'] else td['gop'].get(x)
        if x and not k:
            la.append(x)
        elif k and k not in chuan:
            chuan.append(k)
    if la:
        loi.append('%s: tâm trạng ngoài từ điển: %s' % (ten, la))
    n['tam_trang'] = ';'.join(chuan[:3])
    if n.get('nang_luong', '').strip() not in td['nang_luong']:
        loi.append('%s: nang_luong %r ngoài từ điển' % (ten, n.get('nang_luong')))
    la = [x for x in n.get('hop_video', '').split(';') if x.strip() and x.strip() not in td['hop_video']]
    if la:
        loi.append('%s: hop_video ngoài từ điển: %s' % (ten, la))
    return loi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--loai', required=True, choices=list(LOAI))
    ap.add_argument('--nhan', required=True)
    ap.add_argument('--ghi', action='store_true')
    a = ap.parse_args()
    L = a.loai
    p_cm = CHI_MUC / L / 'chi-muc.csv'
    cols = cot_cua(p_cm)
    rows = doc_csv(p_cm)
    nhan = doc_csv(a.nhan)
    nguon_dir = NGUON_MOI / ('_da-nen' if L == 'canh' else L)
    ten_nhom = {r['nhom']: r['ten_nhom'] for r in rows}
    so = max([int(r['ma'][2:]) for r in rows if r['ma'].startswith(LOAI[L])] + [0])
    hom_nay = datetime.date.today().isoformat()
    loi, moi, doi = [], [], []
    for n in nhan:
        src = nguon_dir / n['tep_goc']
        if not src.exists():
            loi.append('không thấy tệp %s' % src)
            continue
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', n.get('slug', '')) or len(n['slug']) > 32:
            loi.append('%s: slug sai luật' % n['tep_goc'])
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+){0,2}', n.get('nhom', '')):
            loi.append('%s: nhóm sai luật' % n['tep_goc'])
        tn = ten_nhom.get(n['nhom']) or n.get('ten_nhom', '').strip()
        if not tn:
            loi.append('%s: nhóm mới %s thiếu ten_nhom' % (n['tep_goc'], n['nhom']))
        thieu = [c for c in BAT_BUOC[L] if not n.get(c, '').strip()]
        if thieu:
            loi.append('%s: thiếu nhãn %s' % (n['tep_goc'], thieu))
        loi += kiem_tu_dien(L, n)
        so += 1
        ma = '%s%04d' % (LOAI[L], so)
        tep = '%s/%s_%s%s' % (n['nhom'], ma, n['slug'], src.suffix.lower())
        giay = ffprobe_giay(src)
        r = {c: '' for c in cols}
        r.update({c: n[c].strip() for c in cols if c in n and n[c].strip()})
        r.update(ma=ma, loai=L, nhom=n['nhom'], ten_nhom=tn, tep=tep, chu='kho', ngay_them=hom_nay, trang_thai='dung',
                 goi=n.get('goi') or 'du', nguon=n.get('nguon', ''), giay_phep=n.get('giay_phep', ''))
        if L == 'canh':
            r['xem_truoc'] = 'xem-truoc/%s.jpg' % ma
            r['thong_so'] = '720x1280;24fps;%ds' % round(giay)
        else:
            r['thong_so'] = '%ss' % (round(giay) if L == 'nhac' else '%.2f' % giay)
        ten_nhom[n['nhom']] = tn
        moi.append((src, r))
        doi.append({'loai': L, 'ma': ma, 'ma_cu': '', 'tep_goc': n['tep_goc'], 'tep_moi': tep})
    for _, r in moi:
        print(r['ma'], r['tep'], '|', r['mo_ta'][:60])
    if loi:
        sys.exit('DỪNG, chưa ghi gì:\n  ' + '\n  '.join(loi))
    if not a.ghi:
        print('Chạy thử xong (%d tệp). Thêm --ghi để nhập thật.' % len(moi))
        return
    for src, r in moi:
        dst = BAN_CHUAN / L / r['tep']
        if dst.exists():
            sys.exit('Đã có ' + str(dst))
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        if L == 'canh':
            anh = BAN_CHUAN / L / r['xem_truoc']
            anh.parent.mkdir(parents=True, exist_ok=True)
            t = min(3.0, ffprobe_giay(dst) / 2)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', str(dst), '-frames:v', '1', '-vf', 'scale=360:-2',
                            '-q:v', '4', str(anh)], stdin=subprocess.DEVNULL)
            if not anh.exists():
                print('⚠ chưa tạo được ảnh xem trước', anh)
    ghi_csv(p_cm, rows + [r for _, r in moi], cols)
    p_doi = CHI_MUC / '_doi-chieu' / 'bang-doi-ten.csv'
    ghi_csv(p_doi, doc_csv(p_doi) + doi, cot_cua(p_doi))
    sinh_md(L)
    print('Đã nhập %d tệp, đã ghi chi-muc.csv, bang-doi-ten.csv, CHI_MUC.md.' % len(moi))


if __name__ == '__main__':
    main()
