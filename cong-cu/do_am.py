"""Bước 2 (nhạc, tiếng): đo bằng máy để gắn nhãn cho đúng, không tả theo tên tệp.

    python -I -X utf8 cong-cu/do_am.py                      # đo mọi .mp3/.wav trong nguon-moi/nhac và nguon-moi/am
    python -I -X utf8 cong-cu/do_am.py <thu_muc> [<thu_muc_anh>]

In ra mỗi tệp: độ dài (giây), độ lớn LUFS, đỉnh dB; với bài > 20 giây thêm nhịp/phút ước lượng
(có thể gấp đôi hoặc một nửa nhịp thật, cần đối chiếu cảm giác) và độ lớn từng 2 giây (để tách đoạn
dạo, beat, lắng, cao trào). Lưu ảnh dạng sóng + phổ <tên>.png vào nguon-moi/_do-am/ để AI nhìn
(Read ảnh) mà tả âm thanh. Tiếng ngắn dưới 0,4 giây có LUFS -70 là do quá ngắn, dùng đỉnh dB thay.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from chung import NGUON_MOI  # noqa: E402

SR = 11025


def pcm(p):
    b = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(p), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(b, np.float32)


def lufs(p):
    e = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', str(p), '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    l = [x for x in e.splitlines() if x.strip().startswith('I:')]
    return l[-1].split()[1] if l else '?'


def bpm(x):
    hop = 256
    n = len(x) // hop
    f = np.abs(np.fft.rfft(x[:n * hop].reshape(n, hop) * np.hanning(hop), axis=1))
    flux = np.maximum(0, np.diff(np.log1p(f), axis=0)).sum(1)
    flux -= flux.mean()
    ac = np.correlate(flux, flux, 'full')[len(flux) - 1:]
    fps = SR / hop
    lo, hi = int(fps * 60 / 180), int(fps * 60 / 70)
    return int(round(60 * fps / (lo + np.argmax(ac[lo:hi]))))


def main():
    dirs = [Path(sys.argv[1])] if len(sys.argv) > 1 else [NGUON_MOI / 'nhac', NGUON_MOI / 'am']
    anh = Path(sys.argv[2]) if len(sys.argv) > 2 else NGUON_MOI / '_do-am'
    anh.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for d in dirs:
        for p in sorted(d.rglob('*')):
            if p.suffix.lower() not in ('.mp3', '.wav'):
                continue
            x = pcm(p)
            dur = len(x) / SR
            r = {'giay': round(dur, 2), 'lufs': lufs(p), 'dinh_db': float(round(20 * np.log10(np.abs(x).max() + 1e-9), 1))}
            if dur > 20:
                w = SR * 2
                r['nhip_bpm_uoc'] = bpm(x)
                r['do_lon_moi_2s'] = [int(round(20 * np.log10(np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-9))) for i in range(0, len(x) - w, w)]
            print(p.name, json.dumps(r, ensure_ascii=False))
            fig, ax = plt.subplots(2, 1, figsize=(12, 5))
            ax[0].plot(np.arange(len(x)) / SR, x, lw=.3)
            ax[0].set_xlim(0, dur)
            ax[0].set_title(p.name)
            ax[1].specgram(x, NFFT=512, Fs=SR, noverlap=256, cmap='magma')
            ax[1].set_xlim(0, dur)
            plt.tight_layout()
            plt.savefig(anh / (p.name + '.png'), dpi=70)
            plt.close()


if __name__ == '__main__':
    main()
