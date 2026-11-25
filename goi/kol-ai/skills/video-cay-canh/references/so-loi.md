# Sổ lỗi

Mỗi khi người dùng chê hoặc Claude tự bắt lỗi, ghi một dòng vào cuối bảng và sửa luôn chỗ gây lỗi (mô tả mẫu, script hoặc SKILL.md) để video sau không lặp lại.

| Ngày | Lỗi | Nguyên nhân | Đã sửa ở đâu |
|---|---|---|---|
| 19/11/2026 | Cảnh sân nhà "đơn giản, ít cây" | Mô tả ảnh ngắn, không nêu tầng cây | `kho-canh.md` mục Gu; `lap_lenh.py` chặn mô tả < 80 ký tự |
| 19/11/2026 | Phòng trong nhà "lộn xộn, không đâu vào đâu" | Nhồi nhiều thứ, không trục nhìn | `kho-canh.md`: trong nhà phải gọn, một trục nhìn |
| 19/11/2026 | Máy zoom hơi nhanh | Muse đi sâu hơn lệnh | Làm chậm 0,85 trong `dung.py`; lệnh dặn "một phần tư quãng đường" |
| 20/11/2026 | Clip tự nhảy sang góc khác giữa chừng (2/10 clip) | Tật của Muse Video | `kiem_clip.py` dò nhảy cảnh và tự ghi đoạn giữ |
| 20/11/2026 | Tải nhầm một ảnh 4 lần | Khung xem ảnh cũ còn trong trang | `lam-tren-muse.md`: lấy ảnh có src mới |
| 20/11/2026 | Muse chặn tạo video "country or region" | Tài khoản bị xếp vùng chưa mở | Dùng tài khoản dự phòng; tài khoản bị chặn chỉ làm ảnh |
| 20/11/2026 | Muse chỉ tạo 4 ảnh mỗi lượt | Giới hạn của Muse | `lap_lenh.py` chia lượt 4 cảnh |
| 20/11/2026 | File tải về nằm lại bừa trong Downloads | `gom_file.py` chỉ chép | `gom_file.py` chuyển hẳn file gốc vào `tai-ve-goc/` của dự án |
| 20/11/2026 | Video không nhạc thì im, khách tưởng hỏng | Gói không kèm nhạc vì nhạc trend có bản quyền | Kèm nhạc CC0 (nay là 8 bài cắt sẵn đoạn hay) trong `nhac-mau/`, `dung.py` tự lót khi `thu_muc_nhac` để trống |
| 22/11/2026 | Video thử bị chê "cực kỳ chán" dù hình đẹp | Nhạc CC0 chọn theo tên bài, không đo: tối, đục (430–630 Hz), lót từ đoạn dạo đầu | Thay 8 bài sáng cắt sẵn đoạn hay; `dung.py` chọn theo không khí cảnh và có cổng đo nhạc (lô chốt 14/14 qua, video bị chê 2/2 trượt) |
| 22/11/2026 | Cảnh lối trúc thua lô đã duyệt | Toàn một màu xanh, không nước, không đèn: giống rừng hoang hơn sân vườn có thiết kế | `kho-canh.md` mục "Ba thứ phải có"; `lap_lenh.py` nhắc khi thiếu ánh sáng có hướng, điểm nhấn màu, nước |
| 23/11/2026 | Không ai so video thử với video đã duyệt | Thiếu người chấm so mẫu | Agent `sku-cc-cham-so-mau` + `to_so_sanh.py`; chỉ giao khi không thua mặt nào |
| 23/11/2026 | Ảnh sảnh trong nhà: nửa dưới là sàn trống, mặt quầy gỗ trơn | Mô tả không nói tiền cảnh | Trong nhà phải tả bồn cây thấp dày ở tiền cảnh, phủ kín mặt quầy; sửa ảnh bằng cách đính kèm ảnh cũ và tả chỗ cần phủ |
| 23/11/2026 | Lệnh "trượt ngang" nhưng máy đẩy thẳng vào bể cá, phải cắt còn 7,6 giây | Muse thích tiến vào vật sáng nhất | Ghi rõ "giữ nguyên khoảng cách, KHÔNG tiến vào bể, bể và hàng cây luôn trọn khung đến hết video" |
| 23/11/2026 | Hạt sáng bay lơ lửng trông giả; mặt ao đứng yên | Câu chung "ánh sáng lung linh"; lệnh máy không nói nước | Câu chung đổi thành "nước gợn, ánh sáng đổi rất nhẹ, không có hạt sáng bay"; cảnh có ao phải ghi "mặt ao gợn, cá bơi" |
| 23/11/2026 | Cảnh sảnh có bể thủy sinh làm 3 vòng vẫn thua (5 → 7,5 → bỏ): máy quay lệch vào bể, cây rời khung, nhảy cảnh | Bể sáng xanh hút máy Muse; góc chính diện thì phẳng, góc chéo thì máy rẽ vào bể | Cảnh trong nhà có bể: để bể là phần nhỏ của khung, cây và đèn là chủ thể; ưu tiên cảnh ngoài trời có nước cho video mẫu |
