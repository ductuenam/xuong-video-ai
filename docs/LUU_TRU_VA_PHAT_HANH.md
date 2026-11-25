---
status: draft
version: 0.1.0
updated: 2026-11-25
---

# LƯU TRỮ VÀ PHÁT HÀNH

## 1. So sánh nơi để kho tài nguyên (bản v1 sau khi nén: 882 MB đủ, 217 MB nhẹ, 18 MB nhạc + tiếng)

| Nơi | Tải tự động bằng script | Giới hạn | Bản quyền nhạc Pixabay | Kết luận |
|---|---|---|---|---|
| **Cloudflare R2** | Tốt: đường dẫn thẳng, tải tiếp khi đứt mạng, nhanh ở Việt Nam | Gói miễn phí (theo bảng giá Cloudflare tại thời điểm viết, Founder kiểm lại khi tạo): 10 GB lưu trữ, **không tính phí băng thông tải ra**, khoảng 10 triệu lượt đọc/tháng | Để ở đường dẫn không công bố; không nằm trong kho mã công khai | **Chọn làm nơi chính** |
| GitHub Releases | Tốt | Mỗi tệp tối đa 2 GB, miễn phí | **Công khai cho mọi người**, trái điều khoản "không phát lại nguyên tệp" của Pixabay và dòng "không đăng lại nguyên bộ" của gói | Chỉ dùng cho bộ cài và mã |
| Google Drive | **Kém**: tệp lớn hiện trang cảnh báo quét virus, hay báo "vượt hạn mức tải" khi cả lớp tải cùng lúc | Hạn mức tải theo ngày không công bố | Như R2 | Bỏ |

## 2. Cách bố trí đề xuất

- **Mã:** kho GitHub công khai `ductuenam/xuong-video-ai`, chính là thư mục này (trừ `phieu/` nội bộ; xem `.gitignore`).
- **Tài nguyên:** R2, gắn tên miền riêng (ví dụ `tai.zenotera.com`; tên miền phải đang quản lý trên Cloudflare). Đường dẫn chứa số phiên bản, không bao giờ ghi đè tệp cũ:
  ```
  xuong-video/v1/kho-canh-du-v1.zip      882 MB (226 cảnh, kèm ảnh xem trước)
  xuong-video/v1/kho-canh-nhe-v1.zip     217 MB (64 cảnh, kèm ảnh xem trước)
  xuong-video/v1/nhac-am-v1.zip          khoảng 18 MB
  xuong-video/v1/SHA256SUMS.txt
  ```
- **Phần mềm máy** (Python, FFmpeg, Node, Whisper): bộ cài tải thẳng từ nguồn chính hãng. Không tự lưu lại bản sao để khỏi phải tự cập nhật bản vá bảo mật.
- `PHIEN_BAN.json` ghi đường dẫn, sha256, dung lượng từng gói. Đổi kho = tăng `v2`, sửa `PHIEN_BAN.json`; học viên chạy lại câu lệnh là lên bản mới.

## 3. Quy trình phát hành một bản

1. Sửa mã trong thư mục này; chạy thử bộ cài trên bộ não giả trong `%TEMP%` (Windows) và một máy Mac.
2. Nếu kho tài nguyên đổi: làm theo `BAN_DO_KHO.md` mục 5 (`cong-cu/dong_goi.py --phien-ban vN --ghi-phien-ban` dựng gói và ghi sha256), Founder tải lên R2 ở thư mục phiên bản mới.
3. Cập nhật `PHIEN_BAN.json`, đẩy lên GitHub, gắn nhãn phiên bản.
4. Chạy lại câu lệnh cài trên một bộ não đã có video và mẫu riêng: kiểm không mất tệp nào của học viên.
5. Báo lớp: "dán lại câu lệnh cài để cập nhật".

## 4. Việc Founder phải tự làm (Claude không làm thay)

- Tạo bucket R2, gắn tên miền, bật đọc công khai cho bucket đó.
- Tạo kho GitHub `ductuenam/xuong-video-ai` và cho phép đẩy mã.
- Quyết định có giữ 3 bài nhạc Pixabay hay thay bằng nhạc CC0.
