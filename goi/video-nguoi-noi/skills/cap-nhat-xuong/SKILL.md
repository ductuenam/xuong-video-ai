---
name: cap-nhat-xuong
description: Cập nhật Xưởng Video AI lên bản mới nhất, luôn cho học viên xem trước và hỏi OK. Không có gì mới thì báo ngay; có mã mới thì thay mã, có cảnh/nhạc mới thì chỉ tải phần bổ sung và tự đặt đúng chỗ. Không bao giờ xóa video, ảnh, mẫu, cảnh riêng của học viên; tệp gốc học viên đã sửa được cất sao lưu. Dọn bộ cài cũ ngày 24/11 nếu học viên đồng ý. Dùng khi học viên gõ "/cap-nhat-xuong", "cập nhật xưởng", "cập nhật Xưởng Video AI", "xưởng có gì mới", "có bản mới chưa", "dọn bản cũ", "cài lại xưởng".
---

# Cập nhật Xưởng Video AI

Học viên chỉ cần gõ lệnh này. Bạn (Claude) làm hết, báo lại bằng tiếng Việt dễ hiểu, ngắn. **Mọi thay đổi đều hỏi OK trước.**

## Lệnh cài (gọi tắt là LỆNH)

Chạy ngay trong thư mục bộ não, chạy nền và chờ xong, không chạy lại giữa chừng:
- Windows, công cụ PowerShell: `powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.ps1 | iex"`
- Windows, công cụ Bash: cùng lệnh trên.
- Mac: `curl -fsSL https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.sh | bash`

Đặt biến cho LỆNH (biến chỉ có hiệu lực trong đúng lần chạy đó):
- PowerShell: `$env:XUONG_XEM='1'; ` đặt trước LỆNH. Lần chạy sau ở cửa sổ mới, biến không còn.
- Bash (Windows hoặc Mac): `XUONG_XEM=1 ` đặt trước `powershell ...`; Mac: `curl ... | XUONG_XEM=1 bash`.

## Các bước

1. Kiểm thư mục đang mở là **Bộ Não AI** (có `INDEX.md` và ngăn `01_...`). Không phải thì dừng, nhắc mở đúng thư mục bộ não rồi gõ lại.
2. **Xem trước:** chạy LỆNH với `XUONG_XEM=1`. Lệnh in khối `XEM TRƯỚC`, không thay đổi gì.
   - Có `ĐÃ LÀ BẢN MỚI NHẤT` và không có mục "Bản cũ": báo một câu "Xưởng đang là bản mới nhất (bản …), không cần làm gì." Xong.
   - Có bản mới: kể ngắn cho học viên: bản đang có → bản mới, **có gì mới** (từng ý một dòng), sẽ tải khoảng bao nhiêu MB, tệp gốc nào học viên đã sửa sẽ được cất sao lưu, những gì giữ nguyên. Hỏi: **"Cập nhật nhé?"**
3. Học viên OK → chạy LỆNH **không** có `XUONG_XEM`. Đọc kết quả:
   - `ĐÃ CẬP NHẬT`: chép lại "Có gì mới" bằng lời dễ hiểu. Nhắc **đóng hẳn Claude rồi mở lại**.
   - Dòng `⚠`: giải thích ngắn, làm theo dòng đó; hỏi học viên trước khi xóa hay chuyển thứ gì.
   - Dòng `DỪNG`: làm đúng hướng dẫn trong đó (ví dụ ổ đầy: chỉ học viên dọn ổ). Không tự sửa tệp của xưởng.
4. **Bản cũ 24/11** (khối `PHÁT HIỆN BẢN CŨ` hoặc mục "Bản cũ" trong xem trước): đọc danh sách cho học viên bằng lời dễ hiểu: video, ảnh, hồ sơ, cấu hình KOL của họ sẽ được **chép giữ vào xưởng mới và kiểm đủ trước**, phần còn lại của bản cũ vào **Thùng rác** (lấy lại được), giải phóng bao nhiêu GB; phần mềm đã cài giữ nguyên để dùng lại. Hỏi riêng: **"Dọn bản cũ nhé?"** OK thì chạy LỆNH với `XUONG_DON_BAN_CU=1` (cách đặt biến như `XUONG_XEM`). Báo lại các dòng `✔`; nhắc đóng và mở lại Claude. Không OK thì thôi, xưởng mới vẫn chạy.
5. Học viên nói **"cài lại xưởng"** (xưởng hỏng): xem trước như bước 2, OK thì chạy LỆNH với `XUONG_CAI_LAI=1` (chạy đủ các bước sửa máy, vẫn giữ đồ học viên, không tải lại tài nguyên đã có).

## Luật

- Không tự xóa, chuyển hay sửa: video trong `du-an/`, `thanh-pham/`; `anh-video-cua-toi/`; `mau-cua-toi/`; mọi thứ có `cua-toi`; dòng chỉ mục của học viên; các ngăn khác của bộ não. Bộ cài đã giữ những thứ này; bạn không tự dọn thêm.
- Không tải gì ngoài LỆNH, không cài thêm phần mềm khác, không gỡ phần mềm đã có.
- Mạng đứt giữa chừng: gõ lại, bộ cài tải tiếp phần còn thiếu.
- Muốn lấy lại tệp đã cất: `<Xưởng>/.sao-luu/<ngày giờ>/` (tệp gốc đã sửa) hoặc Thùng rác (bản cũ đã dọn); nhật ký ở `<Xưởng>/NHAT_KY_DON_BAN_CU.md`.
