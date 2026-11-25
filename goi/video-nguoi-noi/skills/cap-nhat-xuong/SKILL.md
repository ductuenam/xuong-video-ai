---
name: cap-nhat-xuong
description: Cập nhật Xưởng Video AI lên bản mới nhất. Không có gì mới thì báo ngay; có mã mới thì thay mã, có cảnh/nhạc mới thì chỉ tải phần bổ sung và tự đặt đúng chỗ trong 08_XUONG_VIDEO. Không đụng video, mẫu, cảnh riêng của học viên. Dùng khi học viên gõ "/cap-nhat-xuong", "cập nhật xưởng", "cập nhật Xưởng Video AI", "xưởng có gì mới", "có bản mới chưa". Gõ "cài lại xưởng" thì cài lại toàn bộ.
---

# Cập nhật Xưởng Video AI

Học viên không cần làm gì ngoài việc gõ lệnh này. Bạn (Claude) làm hết, báo lại bằng tiếng Việt dễ hiểu, ngắn.

## Các bước

1. Kiểm thư mục đang mở là **Bộ Não AI** (có `INDEX.md` và ngăn `*_XUONG_VIDEO`). Không phải thì dừng, nhắc học viên mở đúng thư mục bộ não rồi gõ lại.
2. Chạy **đúng một lệnh** theo máy, ngay trong thư mục bộ não, **chạy nền và chờ xong** (không chạy lại giữa chừng):
   - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.ps1 | iex"`
   - Mac: `curl -fsSL https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.sh | bash`
   - Học viên nói "cài lại xưởng" (xưởng hỏng, muốn cài lại từ đầu): đặt biến `XUONG_CAI_LAI=1` trước lệnh (Windows: `$env:XUONG_CAI_LAI='1'; ` đứng trước; Mac: `XUONG_CAI_LAI=1 bash` thay cho `bash`).
3. Đọc kết quả:
   - Có dòng **"ĐÃ LÀ BẢN MỚI NHẤT"**: báo một câu "Xưởng đang là bản mới nhất (bản …), không cần làm gì." Xong.
   - Có dòng **"ĐÃ CẬP NHẬT"**: chép lại các dòng "Có gì mới" bằng lời dễ hiểu (mỗi ý một dòng). Nhắc: **đóng Claude rồi mở lại** để dùng skill mới.
   - Có dòng **⚠**: giải thích ngắn và làm theo dòng đó; **hỏi học viên trước khi xóa hay chuyển thứ gì**.
   - Có dòng **DỪNG**: làm đúng hướng dẫn trong dòng đó; không tự sửa tệp của xưởng.

## Luật

- Không xóa, không ghi đè: video trong `du-an/`, `thanh-pham/`; mẫu `mau-cua-toi`; mọi thứ có `cua-toi`; dòng chỉ mục `chu=hoc-vien`. Bộ cài đã giữ những thứ này, bạn không tự dọn thêm.
- Không tải gì ngoài lệnh trên, không cài thêm phần mềm khác.
- Mạng đứt giữa chừng: gõ lại lệnh, bộ cài tải tiếp phần còn thiếu.
