"""Phần dùng chung cho mọi công cụ làm kho: đường dẫn, đọc/ghi chỉ mục, sinh CHI_MUC.md.
Chạy riêng tệp này = sinh lại CHI_MUC.md của cả 3 loại từ chi-muc.csv:
    python -I -X utf8 cong-cu/chung.py
"""
import csv
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]           # thư mục kho mã xuong-video-ai
# Hai biến môi trường XUONG_KHO_NANG, XUONG_REPO chỉ dùng khi chạy thử trên bản sao trong %TEMP%\zaios_<việc>\
_GOC = Path(os.environ.get('XUONG_REPO', REPO))
KHO_NANG = Path(os.environ.get('XUONG_KHO_NANG', REPO / '_kho-nang'))  # lối tắt sang E:\xuong-video-ai-kho
BAN_CHUAN = KHO_NANG / 'ban-chuan' / 'tai-nguyen'     # video, nhạc, tiếng đã chuẩn
GOI = KHO_NANG / 'goi'                                # goi/v1, goi/v2 ...
BAO_CAO = KHO_NANG / 'bao-cao'
NGUON_MOI = KHO_NANG / 'nguon-moi'
CHI_MUC = _GOC / 'tai-nguyen'                         # chỉ mục (đi lên GitHub)
PHIEN_BAN = _GOC / 'PHIEN_BAN.json'
LOAI = {'canh': 'CA', 'nhac': 'NH', 'am': 'AM'}


def doc_csv(p):
    with open(p, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def ghi_csv(p, rows, cols):
    with open(p, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def cot_cua(p):
    with open(p, encoding='utf-8-sig') as f:
        return next(csv.reader(f))


def ffprobe_giay(p):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'default=nw=1:nk=1', str(p)], capture_output=True, text=True).stdout
    return float(out.strip())


# ---------- Sinh CHI_MUC.md (AI đọc tệp này để chọn tài nguyên) ----------

DAU = {
    'canh': ['# CHỈ MỤC CẢNH TRÁM (video dọc 9:16, 8–10 giây, không có mặt người thật)', '',
             '> AI đọc tệp này để chọn cảnh, không mở lần lượt video. Muốn nhìn thì mở `xem-truoc/<mã>.jpg`.'],
    'nhac': ['# CHỈ MỤC NHẠC NỀN', '',
             '> Giấy phép Pixabay: dùng trong video được, **không phát lại nguyên tệp**. Chi tiết: `NGUON.md`.'],
    'am': ['# CHỈ MỤC TIẾNG HIỆU ỨNG', '',
           '> ⚠ Chưa rõ nguồn và giấy phép: xác minh hoặc thay bằng tiếng CC0 trước khi phát hành.'],
}
CHU_GIAI = {
    'canh': 'Cột: **Máy** = chuyển động máy quay · **Chữ** = chỗ trống đặt phụ đề · **Dấu** = chữ/dấu in sẵn trong hình (`khong` = sạch; cảnh có `dau-sao` cần che hoặc cắt góc phải dưới nếu video cần sạch). Đầy đủ cột (màu, đổi nội dung, loại video hợp) ở `chi-muc.csv`.',
    'nhac': 'Cột: **Nhịp** = số nhịp/phút ước bằng máy · **Sức** = `vua`/`manh`/`tang-dan` · **Bắt đầu** = giây nên bắt đầu cắt nhạc. Các đoạn của bài và độ lớn ở `chi-muc.csv` (cột `doan`, `do_lon_lufs`). Nhạc luôn hạ khoảng −21 dB dưới giọng nói.',
    'am': 'Cột: **Giây** = độ dài · **Điểm nhấn** = giây mạnh nhất, đặt trùng lúc hình đổi · **Dùng khi** = tình huống hợp. Độ lớn và lời khuyên tăng/giảm ở `chi-muc.csv` (cột `do_lon`).',
}
BANG = {  # (tiêu đề cột, hàm lấy giá trị)
    'canh': [('Mô tả', lambda r: r['mo_ta'].replace('|', '/') + (' *(đổi cảnh %s)*' % r['doi_noi_dung'][3:] if r.get('doi_noi_dung', 'khong') not in ('', 'khong') else '')),
             ('Từ khóa', lambda r: r['tu_khoa'].replace(';', ', ')),
             ('Máy', lambda r: r.get('chuyen_dong', '')), ('Chữ', lambda r: r.get('cho_chu', '')),
             ('Dấu', lambda r: r.get('co_dau_chu', ''))],
    'nhac': [('Mô tả', lambda r: r['mo_ta']), ('Từ khóa', lambda r: r['tu_khoa'].replace(';', ', ')),
             ('Nhịp', lambda r: r.get('nhip_bpm', '')), ('Sức', lambda r: r.get('nang_luong', '')),
             ('Hợp video', lambda r: r.get('hop_video', '').replace(';', ', ')), ('Bắt đầu', lambda r: r.get('bat_dau_goi_y', ''))],
    'am': [('Mô tả', lambda r: r['mo_ta']), ('Từ khóa', lambda r: r['tu_khoa'].replace(';', ', ')),
           ('Giây', lambda r: r.get('giay', '')), ('Điểm nhấn', lambda r: r.get('diem_nhan_s', '')),
           ('Dùng khi', lambda r: r.get('dung_khi', ''))],
}


def sinh_md(loai):
    rows = [r for r in doc_csv(CHI_MUC / loai / 'chi-muc.csv') if r.get('chu') != 'hoc-vien' and r.get('trang_thai', 'dung') == 'dung']
    nhom = {}
    for r in rows:
        nhom.setdefault((r['nhom'], r['ten_nhom']), []).append(r)
    thu_tu = sorted(nhom.items(), key=lambda x: (-len(x[1]), x[0][0]))
    out = DAU[loai] + ['', 'Tổng: %d. Cột "Nhẹ" ★ = có trong gói nhẹ. Tên tệp = `<mã>_<mô-tả-ngắn>`; AI tìm theo mã và mô tả trong bảng này, không đoán theo tên tệp.' % len(rows), '',
                       '| Nhóm | Ý nghĩa | Số |', '|---|---|---|']
    out += ['| `%s` | %s | %d |' % (k, ten, len(rs)) for (k, ten), rs in thu_tu]
    out += ['', CHU_GIAI[loai], '']
    cot = BANG[loai]
    for (k, ten), rs in thu_tu:
        out += ['## %s (`%s`)' % (ten, k), '',
                '| Mã | Nhẹ | ' + ' | '.join(c for c, _ in cot) + ' |',
                '|---|---|' + '---|' * len(cot)]
        for r in rs:
            out.append('| %s | %s | ' % (r['ma'], '★' if 'nhe' in r['goi'] else '') + ' | '.join(f(r) for _, f in cot) + ' |')
        out.append('')
    out += ['## Của riêng học viên',
            'Nằm ở `cua-toi/<nhom>/`, mã có thêm chữ `U` phía trước (ví dụ `U%s0001`), dòng có `chu=hoc-vien`. Bản cập nhật không ghi đè.' % LOAI[loai], '']
    (CHI_MUC / loai / 'CHI_MUC.md').write_text('\n'.join(out), encoding='utf-8', newline='\n')
    return len(rows)


if __name__ == '__main__':
    for l in LOAI:
        print(l, sinh_md(l), 'dong')
