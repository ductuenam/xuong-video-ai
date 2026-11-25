# CẦN CHUẨN BỊ THÊM (Claude đọc khi một việc cần thứ người dùng tự lo)

Xưởng đã cài **đủ mọi skill** ngay từ đầu. Phần lớn việc (edit video, video BNI, video người nói, cắt livestream, biến thể quảng cáo) **không cần chuẩn bị gì thêm**. Vài việc nâng cao cần tài khoản hoặc khóa riêng của người dùng, Claude không tự tạo hay mua thay được.

## Luật cho Claude

1. Trước khi làm, tra skill đó cần gì: `dieu_kien_theo_skill` trong `xuong.json` (bộ cài chép từ `goi.json`).
2. **Kiểm lại thật lúc đó** theo cột "Cách kiểm" bên dưới. Không tin trạng thái cũ vì người dùng có thể đã bổ sung.
3. **Đủ rồi** → làm luôn theo ý người dùng, không hỏi thêm.
4. **Thiếu** → dừng việc đó và báo bằng tiếng Việt dễ hiểu, mỗi thứ thiếu gồm: thiếu gì, để làm phần nào, cách chuẩn bị (từng bước ngắn), có tốn phí không. Đồng thời **đề xuất cách làm được ngay** với thứ đang có (cột "Làm tạm"). Người dùng chuẩn bị xong thì kiểm lại rồi làm tiếp.
5. Không tự mua, không tự đăng ký, không nhập mật khẩu thay người dùng. Khóa và tệp khóa chỉ ghi đường dẫn vào cấu hình, không chép nội dung khóa vào chat hay tài liệu.
6. Nội dung chưa rõ (thiếu thông tin sản phẩm, giá, liên hệ, video gốc…) thì làm như vậy: tìm trong bộ não trước (`BAN_DO_BO_NAO.md`), không có thì hỏi hoặc đề xuất cho người dùng chọn. Không bịa.

## Danh mục

| Mã | Cần cho | Là gì | Cách kiểm | Cách chuẩn bị | Phí | Làm tạm |
|---|---|---|---|---|---|---|
| `khoa-google-vertex` | `anh-bia-video` (vẽ hình AI cho ảnh bìa) | Tệp khóa tài khoản dịch vụ Google Cloud + mã project đã bật Vertex AI | Cấu hình `anhAI` có `khoa` (đường dẫn tệp .json có thật) và `project` | Tạo project Google Cloud, bật thanh toán và Vertex AI API, tạo tài khoản dịch vụ, tải tệp khóa .json, rồi báo Claude đường dẫn tệp và mã project | Có, tính theo số ảnh tạo (xem bảng giá Google Cloud) | Làm bìa bằng khung hình chụp từ chính video + chữ, không cần vẽ AI |
| `tai-khoan-muse` | Mọi skill gói `kol-ai` (KOL bán quần áo, lookbook, mặc thử, review nghỉ dưỡng, cây cảnh) | Tài khoản muse.ai đã đăng nhập trên Chrome | Mở muse.ai qua Claude in Chrome, thấy ô "Nhắn tin" (đã đăng nhập) | Đăng ký và đăng nhập muse.ai trên Chrome | Có (gói của Muse) | Làm video người nói hoặc video ghép cảnh từ kho có sẵn |
| `claude-in-chrome` | Mọi skill gói `kol-ai` | Tiện ích Claude in Chrome đã cài và kết nối | `list_connected_browsers` thấy ít nhất một trình duyệt | Cài tiện ích Claude in Chrome trên Chrome, đăng nhập cùng tài khoản Claude | Không (đi theo gói Claude) | Như trên |
| `ram-16gb-nen-co` | `ab-edit` khi cắt livestream dài | Máy từ 16 GB RAM để chạy nhận dạng giọng mô hình lớn | `xuong.json › may.ram_gb` | Không bắt buộc | Không | Máy 8 GB vẫn chạy, dùng mô hình nhỏ hơn, chậm hơn; chia livestream thành đoạn 20–30 phút |

Thêm skill mới cần thứ gì mới: thêm một dòng vào bảng này và mã đó vào `dieu_kien_theo_skill` của `goi.json`.
