# Tự tạo KOL riêng của bạn

Kho công khai **không kèm ảnh, mặt hay giọng của KOL nào** (ảnh KOL mẫu của An Bình AI đã được gỡ). Mỗi học viên tự tạo một KOL riêng, khác hẳn mọi người thật, rồi lưu đúng tên tệp skill cần.

## 5 bước

1. **Chọn phong cách:** lên Google Hình ảnh hoặc Pinterest, tìm "KOL thời trang Việt", "người mẫu lookbook", "outfit nghỉ dưỡng"... Lưu 3–5 ảnh để tham khảo PHONG CÁCH (tóc, trang phục, ánh sáng, bối cảnh). Không dùng mặt của người trong ảnh tham khảo.
2. **Cho AI tạo gương mặt khác hẳn:** trên Muse (muse.ai), Google Flow hoặc công cụ tạo ảnh bạn có, mô tả bằng lời một gương mặt mới (tuổi, dáng mặt, tóc, màu da, trang điểm nhẹ), toàn thân từ đỉnh đầu tới bàn chân, đứng thẳng nhìn máy, ánh sáng ban ngày mềm, phông/căn phòng cố định của shop. Không đính ảnh người thật, không ghi tên người nổi tiếng. Dùng mặt người thật (chủ shop, nhân viên) thì phải có đồng ý bằng văn bản của người đó.
3. **Chốt ảnh chuẩn:** tạo vài lượt, chọn MỘT ảnh: hai mắt mở, tay đủ ngón, da mịn tự nhiên, không nốt ruồi, chân và đầu gối sạch, khung đủ toàn thân. Ảnh này là "mặt chuẩn" — mọi video sau đều sửa từ ảnh này, không tạo mặt mới.
4. **Lưu đúng tên tệp** (xem mục dưới cho skill này).
5. **Kiểm:** chạy script khóa mặt của skill để cắt mặt chuẩn, mở ảnh xem khung cắt có đúng mặt và chân không.

Nhớ gắn nhãn nội dung AI khi đăng (KOL ảo), và không để KOL giống người nổi tiếng.

## Tên tệp skill `kol-mac-thu-mot-khung` cần

Đặt trong thư mục `thu_muc_kol` (khai trong `cau-hinh.json`, mẫu ở `cau-hinh.mau.json`):

| Tệp | Là gì |
|---|---|
| `kol.json` | Chép từ `assets/kol.mau.json`, điền tên KOL, giọng, mô tả mặt, phòng, chân |
| `kol-chuan.png` | Ảnh chuẩn toàn thân đã chốt ở bước 3 |
| `mat-chuan.png`, `chan-chuan.png`, `xem-chuan.jpg` | Tự sinh: `python -X utf8 scripts/khoa_mat.py chuan <thu_muc_kol>` (chỉnh `kx_chuan` trong `kol.json` nếu khung lệch) |
