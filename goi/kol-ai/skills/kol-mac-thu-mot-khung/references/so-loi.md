# Sổ lỗi — KOL mặc thử một khung

Đọc trước khi viết lời và lệnh. Mỗi lỗi mới: ghi ở đây, sửa lệnh mẫu hoặc script, đóng gói lại skill.

| Ngày | Lỗi | Nguyên nhân | Cách chặn |
|---|---|---|---|
| 23/11 | Agent mới tạo gọi bằng tên báo "không tìm thấy" | Agent chỉ nạp khi mở phiên mới | Gọi `general-purpose`, dặn đọc tệp agent và đóng đúng vai |
| 23/11 | Lời nói "đã bán hơn sáu mươi nghìn chiếc" cho riêng mẫu BB89 | Trang Shopee gộp nhiều dòng áo | Ghi vào mục Không nói; chỉ nói số đã bán khi trang chỉ có một mẫu |
| 23/11 | Shopee hồ sơ chưa đăng nhập không hiện Đã bán, đánh giá | Shopee ẩn khi chưa đăng nhập | Dùng hồ sơ đã đăng nhập (deviceId 05741574 ngày 23/11) |
| 23/11 | Mục Chất liệu ghi "Nỉ", mô tả ghi "dù" | Nhà bán điền sai thuộc tính | Cụm "nỉ" nằm trong danh sách cấm của `viet_lenh.py` khi mâu thuẫn |
| (kế thừa) | Mặt Muse "giống" theo agent mà anh nói "không giống" | Agent chấm tổng thể | Anh duyệt mặt bắt buộc; agent so từng nét, giữ đúng tỉ lệ khi ghép tờ |
| (kế thừa) | Đầu gối hồng ở ảnh gốc thành thâm trên clip | Muse làm đậm vùng hồng | Soi gối ở ảnh gốc; nhờ Muse "chỉ sửa da hai chân giống ảnh 2" (chan-chuan.png). Khung một khung cắt giữa đùi nên gối ra ngoài khung |
| (kế thừa) | Tạo lại cảnh cùng tên tệp, Muse hiện bản cũ | Muse lưu đệm theo tên | Đặt tên mới `-b`, `-c`, so md5 |
| 23/11 | Muse thêm túi khóa ở bắp tay (kiểu MA-1) dù lệnh ghi "không túi ngực" | Muse hiểu "bomber" theo mẫu MA-1 | Chọn ảnh không có túi tay; thêm vào chi_tiet_khoa: "không có túi ở tay áo" |
| 23/11 | `cat_khung.py` đoán tâm người lệch (kx 0,115) | Giá treo áo làm lệch độ tương phản | Luôn mở `xem-khung.jpg`; ghi tay `--kx` = tâm người − kh/2 |
| 23/11 | Khung kh 0,62 chỉ tới mép quần short, khác mẫu | Áo dáng dài phủ hông | Mặc định kh 0,68 (thấy quần và một phần đùi như mẫu) |
| 23/11 | Đính ảnh cận màu khác (ảnh khóa áo đen) dễ làm Muse đổi màu | Ảnh nhà bán chỉ có cận màu đen | Ghi rõ trong lệnh "ảnh 3 chỉ để xem cổ, khóa, KHÔNG lấy màu" (ảnh AK01 ra đúng màu rêu) |
| 23/11 | Ảnh gốc son đỏ tươi quá đậm (agent chấm trang điểm 3/5), mắt hẹp hơn chuẩn | Lệnh ghi "son hồng đỏ tươi" | Lệnh mới: son hồng san hô nhạt như ảnh chuẩn, KHÔNG son đỏ, mắt hai mí rõ, cười vừa |
| 23/11 | Nhờ Muse "chỉ sửa môi và mắt" (đính ảnh tham chiếu mặt khác) làm mặt tròn, bè, mất cằm thon (mặt 4 → 3) | Muse vẽ lại cả mặt theo ảnh tham chiếu | Sửa trang điểm thì đính kol-chuan.png làm ảnh mặt chuẩn, lệnh "mặt giống hệt ảnh mặt chuẩn: trái xoan, cằm thon"; sau mỗi lần sửa phải chấm lại mặt |
| 23/11 | Lượt 3: đính kol-chuan làm mặt mốc + ảnh v1, lệnh "chỉ sửa mặt giống hệt ảnh 1" → mặt 2/5 và 3/5 (mắt to tròn kẻ đuôi, mũi to, nốt ruồi lạ) | Mỗi lần Muse sửa mặt là vẽ lại mặt, càng sửa càng xa chuẩn | Không sửa mặt nhiều vòng. Ảnh gốc phải ra đúng mặt ngay lần đầu: dùng nguyên lệnh ảnh của gói AB-VID-02 ("giữ CHÍNH XÁC khuôn mặt, trang điểm…"), KHÔNG thêm câu "trang điểm lại"; chỉ nêu màu son trùng ảnh chuẩn |
| 23/11 | Clip Muse lần 1: mặt bầu, cằm ngắn, mắt hẹp từ giây 0,75 (mặt 3/5 cả 2 clip); s1 nhắm mắt, đổi mặt ngay sau quay lưng | Lệnh chỉ đính ảnh khung, câu "mắt hiền, không mở to mắt tròn" làm mắt hẹp; quay lưng 2,4 giây | Đính thêm ảnh 2 = mat-chuan.png (chỉ giữ mặt); câu mặt: trái xoan, má không bầu, mắt to hai mí như ảnh 2; quay lưng ≤ 1,5 giây |
| 23/11 | Lệnh "nói nhanh 5,5 chữ/giây, hết lời trước 8,8 giây" Muse vẫn nói 4,6–4,8 chữ/giây, hết lời ~9,9 giây | Giới hạn của Muse | Chấp nhận ~4,7 chữ/giây; không tăng tốc giọng bằng máy; muốn nhanh hơn thì thêm chữ chứ không ép giây |
| 23/11 | Cảnh khoe lưng riêng (s3): xoay lại thì tóc dài sóng thành tóc ngắn ngang vai, son nhạt hơn cảnh nói | Muse vẽ lại mặt và tóc sau khi xoay | Chỉ lấy đoạn trước khi xoay và lúc quay lưng; cắt về cảnh nói trước lúc xoay lại |
| 23/11 | Chỗ nối giữa các clip lộ khác son, khác kẻ mắt (agent chặn mặt 3/5) | Mỗi clip Muse trang điểm hơi khác | Ít chỗ nối có mặt nhất có thể; đè cảnh quay lưng lên chỗ cần che |
| 23/11 | Đè đầu s2 lên cuối s1 rồi s2 lại bắt đầu từ 0,3 → lặp 0,26 giây | Hai mốc chồng nhau | Đoạn chèn kết thúc đúng mốc vào của đoạn sau (cùng một số giây) |
