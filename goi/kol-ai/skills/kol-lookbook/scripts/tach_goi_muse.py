"""Tach tep goi-muse-*.bin (4 byte do dai dau + JSON [[ten,co]] + cac video noi tiep) thanh tung mp4.
Dung: python tach_goi_muse.py <thu-muc-ra> [tep.bin ...]  (khong ghi tep thi lay tat ca goi-muse-*.bin trong thu_muc_tai_ve cua cau-hinh.json)"""
import json, struct, sys, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chung import cau_hinh
ra = sys.argv[1]; tep = sys.argv[2:] or sorted(glob.glob(os.path.join(cau_hinh()['thu_muc_tai_ve'], 'goi-muse-*.bin')), key=os.path.getmtime)
os.makedirs(ra, exist_ok=True)
for t in tep:
    d = open(t, 'rb').read(); n = struct.unpack('>I', d[:4])[0]; head = json.loads(d[4:4+n]); p = 4+n
    for ten, co in head:
        open(os.path.join(ra, ten), 'wb').write(d[p:p+co]); p += co; print(t, '->', ten, co)
