"""Xuất thêm bản ngang 16:9 (1920×1080) từ video dọc đã nghiệm thu, cho YouTube thường hoặc quảng cáo khung ngang.
  python xuat_ngang.py <thư mục dự án>
Đọc render/thanh-pham.mp4 (đã có watermark, intro, outro), ghi render/thanh-pham-ngang.mp4.
Khung dọc giữ nguyên ở giữa, cao đủ 1080; hai bên là chính video đó phóng to, làm mờ, tối đi.
Không cắt khung dọc thành ngang: phụ đề, thẻ, mặt người dẫn đều nằm trọn trong khung dọc, cắt sẽ mất."""
import json
import subprocess
import sys
from pathlib import Path

from chung import chay, ffmpeg_ma_hoa


def main():
    da = Path(sys.argv[1]).resolve()
    vao = da / "render" / "thanh-pham.mp4"
    if not vao.exists():
        sys.exit(f"✘ Chưa có {vao}. Nghiệm thu đạt và gắn nhận diện xong mới xuất bản ngang.")
    ra = da / "render" / "thanh-pham-ngang.mp4"
    loc = ("[0:v]split=2[a][b];"
           "[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=40:2,eq=brightness=-0.18:saturation=0.85[nen];"
           "[b]scale=-2:1080[giua];"
           "[nen][giua]overlay=(W-w)/2:0,setsar=1,format=yuv420p[v]")
    chay(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", vao, "-filter_complex", loc, "-map", "[v]", "-map", "0:a?",
          *ffmpeg_ma_hoa(), "-r", "30", "-c:a", "copy", "-movflags", "+faststart", ra])
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration", "-of", "json", str(ra)], capture_output=True, text=True, check=True).stdout)
    hinh = next(s for s in j["streams"] if s["codec_type"] == "video")
    co_tieng = any(s["codec_type"] == "audio" for s in j["streams"])
    dai_vao = float(json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(vao)], capture_output=True, text=True, check=True).stdout)["format"]["duration"])
    dai = float(j["format"]["duration"])
    if (hinh["width"], hinh["height"]) != (1920, 1080) or not co_tieng or abs(dai - dai_vao) > 0.1:
        sys.exit(f"✘ Bản ngang sai: {hinh['width']}×{hinh['height']}, tiếng {co_tieng}, {dai:.2f}/{dai_vao:.2f} giây")
    print(f"✔ Bản ngang: {ra} ({dai:.1f} giây). Mở xem vài khung trước khi giao.")


if __name__ == "__main__":
    main()
