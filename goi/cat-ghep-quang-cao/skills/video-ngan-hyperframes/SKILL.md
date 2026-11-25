---
name: video-ngan-hyperframes
description: Đường dự phòng cho skill video-ngan-nguoi-noi, dựng lớp hình của video ngắn bằng HyperFrames (HeyGen, giấy phép Apache-2.0, miễn phí cả doanh nghiệp) thay cho Remotion, giữ nguyên mọi mẫu cảnh, phụ đề, nhạc, nghiệm thu và nhận diện kênh. Dùng ngay khi Remotion lỗi, không render được, hỏng sau khi cập nhật, khi cần tránh giấy phép Remotion cho doanh nghiệp, khi người dùng nhắc HyperFrames, "render dự phòng", "bỏ Remotion", hoặc muốn so hai engine, kể cả khi không nói chữ "skill". Không dùng để viết kịch bản hay chọn cảnh: phần đó vẫn theo video-ngan-nguoi-noi.
---

# Dựng video ngắn bằng HyperFrames (dự phòng)

Skill này chỉ thay **một khâu** của `video-ngan-nguoi-noi`: tạo `render/hinh-cam.mp4` (lớp hình, không tiếng). Mọi thứ trước và sau giữ nguyên: kịch bản, `canh.json`, phụ đề, nhạc, `nghiem_thu.py`, watermark, intro, outro, bàn giao. Đọc SKILL.md của skill chính trước.

## Khi nào dùng

| Tình huống | Làm gì |
|---|---|
| Remotion chạy bình thường | Dùng skill chính, không cần skill này |
| Remotion lỗi bundle, render, hỏng sau cập nhật | Dựng bằng skill này, ghi lỗi Remotion vào `loi-da-gap.md` của skill chính |
| Cần dựng cho đơn vị không có giấy phép Remotion (công ty từ 4 người trở lên) | Dùng skill này cho cả video |
| Muốn so hai engine | Chạy cả hai, so `soat-tinh-*.jpg` với `soat-tinh-hf-*.jpg` |

## Cách hoạt động

Mã cảnh vẫn là `engine/src/MoHinh.tsx` của skill chính, không vẽ lại. `engine-hf/shim/remotion.tsx` thay các hàm của Remotion (khung hình, lò xo, nội suy, video, ảnh) để cùng đoạn mã chạy trong trang HyperFrames: HyperFrames gửi giây hiện tại qua sự kiện `hf-seek`, trang vẽ lại đúng khung đó. Thêm mẫu cảnh mới ở skill chính là bản dự phòng có luôn, không sửa gì ở đây.

Font Be Vietnam Pro và Montserrat lấy từ gói `@fontsource` cài cục bộ, render không cần mạng.

## Cài một lần

```bash
python scripts/cai_dat_hf.py
```

Cài vào `~/.video-ngan/engine-hf`, tải Chrome riêng của HyperFrames, chạy `hyperframes doctor`. Các dòng ✗ whisper-cpp, Kokoro, MusicGen, Docker là tùy chọn, skill không dùng. Phiên bản ghim trong `engine-hf/package.json`; nâng phiên bản thì phải chạy lại phần thử ở mục "Kiểm sau khi sửa".

## Dựng

Chuẩn bị dự án đúng như skill chính (`doan.json`, `loi.txt`, `canh.json`...). Mọi lệnh chạy từ thư mục `scripts/` của skill này, đặt `PYTHONUTF8=1`.

```bash
python dung_hf.py "<dự án>"
```

Lệnh tự chạy `dung.py --den canh` của skill chính nếu `props.json` cũ hơn `canh.json`, rồi đóng trang vào `render/hf/` và dừng ở ảnh soát `soat-tinh-hf-*.jpg` (khung 92% mỗi cảnh, cùng mốc với ảnh soát Remotion). Xem bằng mắt như luật của skill chính. Ổn thì:

```bash
python dung_hf.py "<dự án>" --tu render
```

Bước `render` ra `render/hinh-cam.mp4`, tự kiểm 1080×1920 và đúng thời lượng `props.json`. Bước `tiep` gọi `dung.py --tu tron` của skill chính: trộn âm, tờ soát, nghiệm thu, gắn nhận diện. Luật nghiệm thu và bàn giao giữ nguyên, không có ngoại lệ cho bản dự phòng.

Sửa chữ hoặc cảnh: sửa `canh.json`, chạy lại từ đầu (`chuan-bi` tự dựng lại `props.json`). Giờ từng bước ghi vào `thoi-gian.csv` với tiền tố `hf-`.

## Kiểm sau khi sửa

Sửa shim, nâng phiên bản HyperFrames hay React thì chạy lại trên một dự án đã duyệt (video 18 RAG là mẫu chuẩn): ảnh soát HyperFrames phải trùng ảnh soát Remotion ở mọi cảnh đồ họa. Ngày 10/11/2026 đo được độ lệch điểm ảnh trung bình 1,7 đến 2,3 trên các cảnh đồ họa. Cảnh có clip lệch nhiều hơn vì trình duyệt tua video không khớp khung, bản render thật do HyperFrames lấy khung bằng FFmpeg nên không bị.

## Lỗi đã gặp

- **`spawn EPERM` khi chụp hoặc render (10/11/2026).** Trên Windows, HyperFrames mở thêm một tiến trình node canh Chrome; dòng lệnh của tiến trình đó có đoạn PowerShell `Get-CimInstance … Stop-Process`. Môi trường chạy lệnh của app Claude chặn tiến trình này, dù Chrome tự mở bình thường. **Không** sửa mã trong `node_modules`, không giấu đoạn lệnh để qua bộ lọc: đó là lách cơ chế bảo vệ. Cách đúng, theo thứ tự:
  1. Người dùng chạy bước render trong Terminal của họ: `python dung_hf.py "<dự án>" --tu render`.
  2. Hoặc bật Docker Desktop rồi render trong container: `python dung_hf.py "<dự án>" --tu render --docker` (chậm hơn, chưa thử).
  3. Hoặc quay lại Remotion nếu Remotion vẫn chạy.
  Ảnh soát (`anh-tinh`) không dùng HyperFrames CLI nên không bị lỗi này.
- **HyperFrames đòi `window.__timelines`.** Trang dùng giao thức `hf-seek`, không có timeline GSAP; HyperFrames in cảnh báo `[StaticGuard] Missing window.__timelines` và `Math.random()` (của React). Cả hai là cảnh báo, không phải lỗi; mọi hình vẫn là hàm của thời gian.
- **Phiên bản phát hành rất dày** (nhiều bản mỗi ngày). Không tự nâng; ghim phiên bản đã thử.

## Chưa kiểm được

Tính đến 10/11/2026 đã kiểm: cài đặt, đóng trang, font tiếng Việt, ảnh soát 14/14 cảnh trùng Remotion. **Chưa render được MP4 trọn bài trong môi trường của app** vì lỗi `spawn EPERM` ở trên. Lần render đầu tiên ngoài môi trường đó phải nghiệm thu đủ như skill chính rồi mới bàn giao, và ghi kết quả vào đây.
