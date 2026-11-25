"""Tải gói tài nguyên goi/vN lên Cloudflare R2, rồi kiểm lại bằng sha256.

Dùng thay rclone (máy có Smart App Control chặn rclone). Cần thư viện boto3:
    python -m pip install --user boto3
Chạy KHÔNG có cờ -I (cờ -I bỏ qua thư viện cài --user):

    python -X utf8 cong-cu/tai_len_r2.py                      # xem trước, không gửi gì lên mạng
    python -X utf8 cong-cu/tai_len_r2.py --ghi                # tải lên (hỏi khóa R2, gõ ẩn)
    python -X utf8 cong-cu/tai_len_r2.py --kiem-cong-khai     # tải về qua tên miền công khai, so sha256

Khóa R2 (Access Key ID, Secret) lấy từ biến môi trường R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY
nếu có, không thì hỏi lúc chạy. Khóa không bao giờ được ghi xuống tệp.

Luật: gói đã có trên R2 mà khác sha256 thì DỪNG (phiên bản đã phát hành là khóa, không ghi đè).
"""
import argparse
import getpass
import hashlib
import json
import os
import sys
import time
import urllib.request

from chung import GOI, PHIEN_BAN

TAI_KHOAN = '4fce95ab370dfe8ed4458cc0ba0adae6'
BUCKET = 'xuong-video-ai'
TEN_MIEN = 'taivido.zenotera.com'
THU_MUC_R2 = 'xuong-video'          # đường dẫn trên R2: xuong-video/vN/<tệp>
KHUC = 64 * 1024 * 1024             # tải theo khúc 64 MB


def doc_sha(thu_muc):
    p = thu_muc / 'SHA256SUMS.txt'
    if not p.exists():
        sys.exit(f'Không thấy {p}. Đóng gói bằng dong_goi.py trước.')
    sha = {}
    for dong in p.read_text(encoding='utf-8').splitlines():
        if dong.strip():
            h, ten = dong.split(None, 1)
            sha[ten.strip()] = h
    return sha


def ds_tep(thu_muc, sha):
    tep = [thu_muc / ten for ten in sorted(sha)] + [thu_muc / 'SHA256SUMS.txt']
    for t in tep:
        if not t.exists():
            sys.exit(f'Thiếu tệp {t}')
    return tep


def khoa(ten_bien, nhan, an):
    gia_tri = os.environ.get(ten_bien, '').strip()
    if gia_tri:
        return gia_tri
    gia_tri = (getpass.getpass if an else input)(f'{nhan}: ').strip()
    if not gia_tri:
        sys.exit(f'Chưa nhập {nhan}.')
    return gia_tri


def ket_noi():
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        sys.exit('Thiếu boto3. Cài: python -m pip install --user boto3  (rồi chạy lại KHÔNG có cờ -I)')
    return boto3.client(
        's3',
        endpoint_url=f'https://{TAI_KHOAN}.r2.cloudflarestorage.com',
        aws_access_key_id=khoa('R2_ACCESS_KEY_ID', 'R2 Access Key ID', False),
        aws_secret_access_key=khoa('R2_SECRET_ACCESS_KEY', 'R2 Secret Access Key (gõ ẩn)', True),
        region_name='auto',
        config=Config(request_checksum_calculation='when_required',
                      response_checksum_validation='when_required',
                      retries={'max_attempts': 10, 'mode': 'standard'}),
    )


def tren_r2(s3, key):
    from botocore.exceptions import ClientError
    try:
        return s3.head_object(Bucket=BUCKET, Key=key)
    except ClientError as e:
        if e.response.get('Error', {}).get('Code') in ('404', 'NoSuchKey', 'NotFound'):
            return None
        raise


class TienDo:
    def __init__(self, ten, tong):
        self.ten, self.tong, self.da, self.lan_cuoi = ten, tong, 0, 0.0

    def __call__(self, n):
        self.da += n
        bay_gio = time.time()
        if bay_gio - self.lan_cuoi >= 2 or self.da >= self.tong:
            self.lan_cuoi = bay_gio
            print(f'  {self.ten}: {self.da / 1e6:,.0f}/{self.tong / 1e6:,.0f} MB ({100 * self.da / self.tong:.0f}%)',
                  flush=True)


def tai_len(pb, tep, sha):
    from boto3.s3.transfer import TransferConfig
    s3 = ket_noi()
    cau_hinh = TransferConfig(multipart_threshold=KHUC, multipart_chunksize=KHUC, max_concurrency=4)
    for t in tep:
        key = f'{THU_MUC_R2}/{pb}/{t.name}'
        h = sha.get(t.name) or hashlib.sha256(t.read_bytes()).hexdigest()
        co = tren_r2(s3, key)
        if co:
            sha_cu = co.get('Metadata', {}).get('sha256')
            if sha_cu == h and co['ContentLength'] == t.stat().st_size:
                print(f'Bỏ qua (đã có, khớp sha256): {key}')
                continue
            sys.exit(f'DỪNG: {key} đã có trên R2 nhưng khác tệp ở máy (sha {sha_cu}). '
                     f'Phiên bản đã phát hành không ghi đè; tăng phiên bản mới.')
        loai = 'application/zip' if t.suffix == '.zip' else 'text/plain; charset=utf-8'
        print(f'Tải lên {key} ...', flush=True)
        s3.upload_file(str(t), BUCKET, key, Config=cau_hinh,
                       ExtraArgs={'ContentType': loai, 'Metadata': {'sha256': h}},
                       Callback=TienDo(t.name, t.stat().st_size))
        co = tren_r2(s3, key)
        if not co or co['ContentLength'] != t.stat().st_size:
            sys.exit(f'LỖI: {key} trên R2 không đúng dung lượng sau khi tải.')
        print(f'  Xong {key}')
    print('Đã tải đủ. Kiểm tải về qua tên miền: python -X utf8 cong-cu/tai_len_r2.py --kiem-cong-khai')


def kiem_cong_khai(pb, tep, sha, ten_mien):
    loi = 0
    for t in tep:
        url = f'https://{ten_mien}/{THU_MUC_R2}/{pb}/{t.name}'
        h = hashlib.sha256()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'xuong-video-ai-kiem/1.0'})
            with urllib.request.urlopen(req, timeout=60) as r:
                while True:
                    khuc = r.read(1 << 20)
                    if not khuc:
                        break
                    h.update(khuc)
        except Exception as e:
            print(f'LỖI tải {url}: {e}')
            loi += 1
            continue
        mong = sha.get(t.name) or hashlib.sha256(t.read_bytes()).hexdigest()
        dung = h.hexdigest() == mong
        loi += not dung
        print(f'{"ĐÚNG" if dung else "SAI "}  {url}')
    print('KIỂM CÔNG KHAI: ĐẠT' if not loi else f'KIỂM CÔNG KHAI: {loi} LỖI')
    return loi


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--phien-ban', help='vd v1; mặc định lấy phien_ban_tai_nguyen trong PHIEN_BAN.json')
    ap.add_argument('--ghi', action='store_true', help='tải lên thật')
    ap.add_argument('--kiem-cong-khai', action='store_true', help='tải về qua tên miền công khai và so sha256')
    ap.add_argument('--ten-mien', default=TEN_MIEN)
    a = ap.parse_args()

    pb = a.phien_ban or json.loads(PHIEN_BAN.read_text(encoding='utf-8'))['phien_ban_tai_nguyen']
    thu_muc = GOI / pb
    sha = doc_sha(thu_muc)
    tep = ds_tep(thu_muc, sha)

    if a.kiem_cong_khai:
        sys.exit(1 if kiem_cong_khai(pb, tep, sha, a.ten_mien) else 0)

    print(f'Bucket {BUCKET} · tên miền {a.ten_mien} · phiên bản {pb}')
    tong = 0
    for t in tep:
        tong += t.stat().st_size
        print(f'  {t.stat().st_size / 1e6:9,.1f} MB  {THU_MUC_R2}/{pb}/{t.name}  →  https://{a.ten_mien}/{THU_MUC_R2}/{pb}/{t.name}')
    print(f'  Tổng {tong / 1e9:.2f} GB')
    if not a.ghi:
        print('Chế độ xem trước: chưa gửi gì. Thêm --ghi để tải lên.')
        return
    tai_len(pb, tep, sha)


if __name__ == '__main__':
    main()
