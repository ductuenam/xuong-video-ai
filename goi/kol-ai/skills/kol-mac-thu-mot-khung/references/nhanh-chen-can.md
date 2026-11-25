# Nhánh "có chèn cận" (người dùng chọn 23/11/2026 cho AK01: "Làm cách c")

Dùng khi các clip Muse ra mặt hơi khác nhau (son, kẻ mắt) hoặc có đoạn mắt nhắm: KHÔNG cắt thẳng từ mặt clip này sang mặt clip khác. Mọi chỗ chuyển giữa đoạn có mặt đều đi qua một cảnh cận chi tiết áo (không mặt) hoặc cảnh quay lưng. Cách này đã đạt ở kol-ban-quan-ao / gói AB-VID-02.

## Ảnh cận
Cắt từ `goc-khung.png` (tư thế đứng yên, tay buông), khung 9:16, phóng 720×1280. Ba cận chuẩn cho áo khoác:
- `can-co.png`: cổ + đầu khóa + nửa ngực (x 190–530, y 400 trở xuống trong khung 720×1280).
- `can-tay.png`: cổ tay + bo tay một bên (x 0–290, y 760 trở xuống).
- `can-tui.png`: túi + bo gấu + quần (x 120–520, y 560 trở xuống).
Không lấy khung giữa lúc đang vung tay (mờ).

## Lệnh Muse cận (1 tin, 3 video, đính 3 ảnh theo thứ tự)
Mẫu AK01 nguyên văn ở cuối tệp. Câu bắt buộc: không nói, không nhạc; "mắt và mặt KHÔNG BAO GIỜ vào khung"; cận cổ "máy trôi rất chậm lại gần tối đa 5%"; cận tay và túi "máy khóa chặt, giữ nguyên khung như ảnh"; mô tả lại từng chi tiết áo; tay chạm nhẹ đúng chi tiết.
Lỗi đã gặp: sau giây ~8 Muse tự vẽ túi khóa trên tay áo (kiểu MA-1) ở clip bo tay và clip túi → chỉ dùng 1,5–7,5 giây đầu.

## Dựng (`ke-hoach.json`, khóa "chen")
- Tiếng 2 cảnh nói chạy liền; hình cận đè đúng lúc lời nói chi tiết đó (±0,5 giây): "bomber dù hai lớp" → cận cổ khóa; "bo tay" → cận bo tay; "bo gấu" → cận gấu; "hai túi" → cận túi.
- Cận dài 1,2–2,4 giây; cảnh quay lưng (s3, chỉ đoạn đã quay hẳn) đặt giữa hai cận để vào và ra lưng không lộ mặt.
- Đoạn mặt giữ lại phải mắt mở (xem phiếu soi mặt từng clip), chỗ nối 2 cảnh nói luôn nằm trong một cảnh cận.
- Mẫu AK01 v5: mặt s1 0–2,4 | cận cổ 2,4–4,0 | lưng 4,0–6,0 | cận tay 6,0–8,4 | mặt s1 8,4–9,1 | cận gấu 9,1–10,6 | mặt s2 10,6–13,9 | cận túi 13,9–15,2 | mặt s2 tới hết.

## Lệnh cận AK01 (nguyên văn)
Tạo 3 video riêng bằng Muse Video, mỗi video 10 giây, đây là cảnh cận chi tiết chiếc áo khoác bomber dù màu xanh rêu, KHÔNG nói, không giọng, không nhạc, không chữ, không phụ đề. Đặt tên tệp: video 1 → q1-can-co.mp4 (khung đầu là ảnh 1), video 2 → q2-can-tay.mp4 (khung đầu là ảnh 2), video 3 → q3-can-tui.mp4 (khung đầu là ảnh 3). Mỗi video là một cảnh liền duy nhất, không cắt cảnh, nền luôn là căn phòng đúng như ảnh. Giữ nguyên tỉ lệ dọc, màu xanh rêu, chất vải dù mờ không bóng và kiểu dáng áo đúng như ảnh: cổ bo dệt kim tròn sát cổ, khóa kéo kim loại bạc một đường thẳng chỉ một đầu khóa, hai túi xẻ chéo trơn ở thân dưới, bo tay và bo gấu dệt kim cùng màu, tay áo trơn, không chữ, không logo; quần short đen giữ nguyên. Máy không ngẩng lên, mắt và mặt KHÔNG BAO GIỜ vào khung. Bàn tay tự nhiên đủ năm ngón, da tay trắng mịn, ngón tay chạm nhẹ, không kéo áo, không xuyên vào vải, không thêm chi tiết nào. VIDEO 1 (ảnh 1, cận cổ và khóa): máy trôi rất chậm lại gần tối đa 5% trong cả video, không tiến sát hơn, rung tay rất nhẹ; giây 1-4 ngón trỏ tay phải chạm nhẹ cổ bo dệt kim rồi vuốt nhẹ xuống theo đường khóa kéo đến giữa ngực; giây 4-10 tay hạ xuống khỏi khung, áo đứng yên, người thở nhẹ. VIDEO 2 (ảnh 2, cận bo tay): máy khóa chặt, không ngẩng lên, không hạ xuống, giữ nguyên khung như ảnh 2 suốt 10 giây; giây 1-5 tay phải đưa vào khung nắm nhẹ bo tay dệt kim ở cổ tay trái, kéo nhẹ cho thấy độ co giãn rồi buông ra, bo tay trở lại như cũ; giây 5-10 tay buông tự nhiên. VIDEO 3 (ảnh 3, cận túi và bo gấu): máy khóa chặt, giữ nguyên khung như ảnh 3 suốt 10 giây, không ngẩng lên; giây 1-5 hai tay nhẹ nhàng cho vào hai túi xẻ chéo hai bên thân dưới rồi rút ra; giây 5-8 hai tay chạm nhẹ bo gấu hai bên hông; giây 8-10 tay buông tự nhiên. Gửi đủ 3 video, xong chỉ báo kích thước và thời lượng.

## Lỗi đã gặp khi dựng (AK01 v7 → v8)
- Hai cận liền nhau mà điểm cuối cận trước trùng điểm đầu cận sau: làm tròn khung lộ đúng 1 khung mặt nền (agent bắt ở 3,29 / 5,29 / 8,38) → mỗi cận dài thêm 0,06 giây đè lên cận sau. Kiểm bằng máy: so từng khung 24/giây của thành phẩm với cảnh nói gốc, không được trùng ngoài các đoạn mặt đã chọn.
- Cận chen giữa câu chốt khi tay đang ở hông → bị chê gượng; cận chỉ đặt lúc lời nói về chi tiết hoặc lúc tay đang đi tới chi tiết.
- Bản AK01 v8: mặt lên hình khoảng 40% thời lượng (mẫu 100%) — cái giá của nhánh chèn cận; báo người dùng.
