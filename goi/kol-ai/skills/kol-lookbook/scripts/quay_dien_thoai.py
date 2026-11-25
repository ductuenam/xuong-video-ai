"""Hậu kỳ "quay bằng điện thoại thật" cho video AI: máy rung tay rất nhẹ, hạt hình mịn, tương phản nhẹ.

Vì sao: video AI đứng yên tuyệt đối trông "hơi AI". Clip Muse đứng yên tuyệt đối,
hình mịn bóng, không hạt: mắt người xem nhận ra ngay là AI. Rung tay nhẹ + hạt hình làm giống điện thoại kê tay/chân máy rẻ.

Dùng: python quay_dien_thoai.py vao.mp4 ra.mp4 [--rung 0.012] [--hat 7]
--rung: biên độ trôi khung (tỉ lệ khung, 0.012 = 1,2%); --hat: độ hạt (noise alls).
Âm thanh giữ nguyên.
Bài học: hạt dày làm video "không HD". Nguyên nhân cũ: hạt nhiễu 12 + nén crf 21 trần 14 Mbps làm nhòe chi tiết
(clip Muse chỉ 720p, phóng lên 1080p). Đổi mặc định: hạt 5 (video mẫu 2; hạt 3 bị chấm da mịn kiểu lọc), cas 0,6 sau khi phóng lanczos, crf 17, trần 24 Mbps.
"""
import argparse, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("vao"); ap.add_argument("ra")
ap.add_argument("--rung", type=float, default=0.012)
ap.add_argument("--hat", type=int, default=5)
ap.add_argument("--net", type=float, default=0.6)  # cas (làm nét thích ứng) sau khi phóng 720→1080; unsharp gây quầng quanh tóc
a = ap.parse_args()
z = 1 + 2.2 * a.rung
r = a.rung
# trôi khung là tổng nhiều sóng sin lệch pha, chậm (giống tay cầm), không giật
x = f"(iw-ow)/2+iw*{r}*(0.55*sin(t*1.7)+0.3*sin(t*3.9+1.3)+0.15*sin(t*7.3+0.4))"
y = f"(ih-oh)/2+ih*{r}*(0.5*sin(t*1.3+2.1)+0.35*sin(t*3.1+0.7)+0.15*sin(t*6.7+2.9))"
vf = (f"scale=iw*{z}:ih*{z}:flags=lanczos,crop=iw/{z}:ih/{z}:{x}:{y},scale=1080:1920:flags=lanczos,cas={a.net},"
      f"eq=contrast=1.04:saturation=0.97,noise=alls={a.hat}:allf=t,vignette=PI/7,format=yuv420p")
r_ = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.vao, "-vf", vf, "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-maxrate", "24M", "-bufsize", "48M", "-movflags", "+faststart",
                     "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                     # cờ trên chỉ ghi được colorspace; gắn đủ cả 3 vào luồng H.264 để điện thoại không lệch màu (video mẫu 2)
                     "-bsf:v", "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1",
                     "-c:a", "copy", a.ra], capture_output=True, text=True, timeout=900)
if r_.returncode:
    sys.exit(r_.stderr[-1500:])
print("Xong", a.ra)
