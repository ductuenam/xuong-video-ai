# Lệnh mẫu Muse (đã chạy đạt)

Mọi lệnh dưới đây do `scripts/viet_lenh.py` sinh ra từ `kol.json` và `video.json`. Tệp này để đọc hiểu và để sửa tay khi cần. **Giữ nguyên các đoạn Cách nói, QUAN TRỌNG, Nét mặt, Mắt, Tay**: đó là phần đã thử nhiều vòng mới đạt.

## Mục lục
- Bước 0: dựng KOL (`lenh-kol.txt`)
- Bước 2: ảnh KOL mặc sản phẩm (`lenh-anh.txt`)
- Bước 4: tin 1, 3 cảnh nói (`tin1.txt`)
- Bước 4: tin 2, 2 cảnh cận (`tin2.txt`)
- Tạo lại một cảnh
- Lời mẫu đã đạt

## Bước 0: dựng KOL

Một tin, không đính ảnh (hoặc đính 1 ảnh chân dung người thật đã đồng ý). Muse trả 4 ảnh; chọn 1 ảnh mặt rõ, hai mắt mở, tay đủ ngón, toàn thân từ đỉnh đầu tới chân, phòng gọn. Lưu thành `kol-chuan.png` trong `thu_muc_kol`.

```
Tạo 4 ảnh chụp chân thực, khung dọc 9:16, mỗi ảnh là cùng MỘT người: <mô tả người>. Cô ấy đứng toàn thân giữa khung, từ đỉnh đầu tới bàn chân, trong <mô tả phòng>. Trang phục nền đơn giản: <trang phục nền>. Tư thế đứng thẳng thoải mái nhìn thẳng máy, hai tay buông tự nhiên, cười nhẹ mím môi, mắt mở tự nhiên. Máy đặt ngang ngực, ánh sáng ban ngày mềm, ảnh như chụp bằng điện thoại, da thật có lỗ chân lông, da mặt trắng sáng mịn đều màu, KHÔNG nốt ruồi, không chấm nâu, không tàn nhang, không mụn, không vết thâm, màu tự nhiên. Không chữ, không logo, không giống bất kỳ người nổi tiếng nào. Bốn ảnh khác nhau nhẹ về gương mặt để tôi chọn một.
```

Phòng nên có: tường màu trơn sáng (kem, be), một giá treo quần áo ở mép trái, một chậu cây nhỏ ở mép phải, sàn gỗ. Các vật cố định này giúp mọi video sau nhận ra cùng một "phòng livestream" và giúp soát xem Muse có vẽ lệch phòng không.

## Bước 2: ảnh KOL mặc sản phẩm

Đính **ảnh 1 = `kol-chuan.png`**, rồi 1–2 ảnh sản phẩm của nhà bán (đã cắt bỏ mặt người mẫu và chữ quảng cáo). Muse trả 2 ảnh; chọn ảnh mặt giống `kol-chuan.png` nhất, đúng màu và chi tiết sản phẩm.

```
Sửa ảnh 1 (ảnh người mẫu). Giữ CHÍNH XÁC khuôn mặt, đường nét, trang điểm, kiểu tóc, màu da, tuổi và vóc dáng của cô ấy, giữ nguyên căn phòng: <mô tả phòng>. Chỉ thay toàn bộ trang phục cho đúng như sản phẩm ở các ảnh sau (ảnh của nhà bán): <mô tả trang phục>. Bỏ hết trang phục cũ, không thêm túi, không thêm vòng cổ. Tư thế: đứng giữa khung nhìn thẳng máy, thoải mái, hai tay buông tự nhiên, cười nhẹ mím môi. Khung dọc 9:16, TOÀN THÂN từ đỉnh đầu tới bàn chân, giày nằm trọn trong khung, máy ngang ngực. Ảnh chụp điện thoại chân thực, màu tự nhiên, đúng màu sản phẩm, không chữ, không logo lạ. Tạo 2 ảnh để tôi chọn.
```

Mô tả trang phục viết đủ: màu, chất liệu, cổ, tay, dáng (ôm/rộng), chiều dài, chi tiết (cúc, khóa, túi, dây rút), đồ phối bên trong, quần/váy, giày. Áo khoác thì phối áo trong và quần/váy hợp với áo; váy liền, chân váy thì đổi cả bộ theo ảnh phối của nhà bán.

## Bước 4: tin 1, 3 cảnh nói

Đính ảnh 1 `goc-tren.png`, ảnh 2 `goc-toan.png`. Ví dụ đầy đủ (video mẫu váy len):

```
Tạo 3 video riêng bằng Muse Video, mỗi video 10 giây, một cảnh liền, giữ nguyên tỉ lệ dọc 9:16 của ảnh, giữ nguyên khuôn mặt, tóc, chiếc váy len nâu và căn phòng như ảnh. Đặt tên tệp: video 1 → s1-noi.mp4, video 2 → s2-noi.mp4, video 3 → s3-xoay.mp4. Video 1 và video 2 dùng ảnh 1 làm khung hình đầu tiên; video 3 dùng ảnh 2 làm khung hình đầu tiên. Máy quay đứng yên tuyệt đối, không zoom. Cách nói: như một người bán hàng livestream chuyên nghiệp đang lên sóng chốt đơn, nhiệt tình, tự tin, hào hứng thật sự; nói nhanh và liền mạch khoảng 5,5 chữ mỗi giây, nhấn mạnh từ khóa, lên giọng ở câu hỏi kéo khách như "đúng không cả nhà"; giọng nữ miền Bắc trẻ, rõ từng chữ; KHÔNG điệu, không nũng nịu, không làm giọng trẻ con, không kéo dài cuối câu; nói ngay từ khung đầu, không ngập ngừng, đọc đúng từng chữ như lời, không thêm không bớt, không lặp chữ nào. QUAN TRỌNG: nói hết lời trước giây 8,5, chữ cuối nói rõ trọn vẹn, sau đó im lặng hoàn toàn, chỉ cười nhẹ nhìn máy đến hết video. Nét mặt: luôn tươi, cười khi nói, lông mày thả lỏng để yên, KHÔNG nhíu mày, không nhăn trán, không nheo mắt; năng lượng nằm ở giọng nói và đôi tay, không nằm ở lông mày. Mắt: mở to tự nhiên, nhìn thẳng máy, chỉ chớp hai mắt cùng lúc và chớp thưa, khoảng 3 đến 4 giây mới chớp một lần, không nhắm mắt khi cười hay khi nhấn giọng, không nháy một mắt. Tay luôn có động tác như người livestream, đổi động tác khoảng mỗi 1,5 giây, không đặt tay lên ngực. Trang phục luôn giữ nguyên: váy len lông thỏ màu nâu mocha, ôm dáng, cổ cao ba phân, tay dài, dài tới mắt cá, giày cao gót đen. Không nhạc nền, không chữ, không phụ đề. VIDEO 1: giây 0-1,5 hơi nghiêng người về phía máy, tay phải vẫy nhẹ chào; giây 1,5-3,5 tay phải ngửa mở ra ngang eo như giới thiệu; giây 3,5-5,5 hai tay vuốt nhẹ hai bên hông váy từ eo xuống; giây 5,5-8,5 tay phải chỉ nhẹ về phía máy khi hỏi; giây 8,5-10 im lặng, hai tay đặt nhẹ hai bên eo, cười nhìn máy. Lời VIDEO 1: "…" VIDEO 2: … VIDEO 3: … Gửi đủ 3 video, xong chỉ báo kích thước và thời lượng.
```

Vì sao có từng đoạn:
- **Câu nét mặt** là bắt buộc. Thiếu nó, lệnh "năng lượng cao" làm KOL nhíu mày, nheo mắt suốt cảnh. Có nó vẫn còn khoảng 1/5 cảnh hơi căng lông mày: phủ bằng cảnh cận hoặc tạo lại riêng cảnh đó.
- **Động tác cuối cảnh chuẩn bị cho cú chuyển:** cảnh 1 kết hai tay ở eo (để cắt sang cận bàn tay chạm chi tiết ở eo); cảnh 2 kết hai tay buông, đứng yên (để lùi máy sang toàn thân).
- **Tay đổi động tác mỗi 1,5 giây:** cảnh 1 mở bằng nghiêng người vẫy chào; cảnh 2 có một động tác khoe chi tiết (giơ cổ tay, chạm cúc, nắm chân váy).

## Bước 4: tin 2, 2 cảnh cận

Đoạn chat khác, đính ảnh 1 `can-tren.png`, ảnh 2 `can-duoi.png`.

```
Tạo 2 video riêng bằng Muse Video, mỗi video 10 giây, đây là cảnh cận chi tiết <tên trang phục>, KHÔNG nói, không giọng, không nhạc, không chữ. Đặt tên tệp: video 1 → q4-can-tren.mp4, video 2 → q5-can-duoi.mp4. Mỗi video là một cảnh liền duy nhất, không cắt cảnh, nền luôn là căn phòng đúng như ảnh. Giữ nguyên tỉ lệ dọc, màu, chất liệu và kiểu dáng trang phục đúng như ảnh. Máy không ngẩng lên, mắt và mặt không bao giờ vào khung. Bàn tay tự nhiên đủ năm ngón. VIDEO 1, khung đầu là ảnh 1 (cận thân trên): máy trôi rất chậm lại gần tối đa 5% trong cả video, không tiến sát hơn, rung tay rất nhẹ; <động tác cận trên> VIDEO 2 phải giữ nguyên khung hình như ảnh 2 suốt 10 giây: máy khóa chặt trên chân máy, không ngẩng lên, không hạ xuống, không tiến, không lùi, không thêm chi tiết nào; khung đầu là ảnh 2 (phần dưới và giày): <động tác cận dưới> Gửi đủ 2 video, xong chỉ báo kích thước và thời lượng.
```

- Cận trên ghi "tối đa 5%, không tiến sát hơn": 8% thì Muse phóng quá tay.
- Cận dưới phải có câu "máy khóa chặt…". Thiếu câu này Muse tự ngẩng máy lên, chân ra khỏi khung, có lần còn mọc thêm hoa ở eo. Có câu này vẫn có clip trôi từ giây 2,5: chỉ tin chắc 1,5–2 giây đầu, đặt cận dưới đúng câu ngắn nói về giày hoặc dáng dài.

## Tạo lại một cảnh

Ngay trong đoạn chat đó, đính lại đúng ảnh khung đầu:
```
Tạo lại VIDEO <n> đúng y như lệnh trên, cùng ảnh <n>, cùng lời. Lần trước <lỗi cụ thể, giây nào>. Lần này <cách tránh>, đọc đúng cụm "<cụm hay đọc sai>". Chỉ tạo 1 video này, đặt tên <tên tệp>.
```
Mỗi cảnh tạo lại tối đa 3 lần rồi dừng và báo, tránh tốn lượt vào lỗi model chưa làm được.

## Lời mẫu đã đạt

Ba cảnh của video mẫu váy len (40–43 chữ mỗi cảnh):
1. "Cả nhà ơi, trời lạnh thế này mà muốn mặc váy vẫn ấm thì xem ngay chiếc váy len này. Len lông thỏ, cổ ba phân kín gió, ôm dáng dài tới mắt cá, mặc lên tôn dáng hẳn đúng không cả nhà?"
2. "Các chị nhìn này, vải cầm nặng tay, mềm mịn, co giãn tốt, có bản xẻ tà sau đi lại thoải mái. Hơn trăm nghìn đơn rồi đấy cả nhà, khách khen chất dày dặn, mặc lên tôn dáng cực."
3. "Váy có màu nâu với màu đen, nhiều size, đi làm, đi chơi hay đi tiệc đều hợp. Chị em nào ưng thì nhắn ngay chiều cao cân nặng, em chọn size chuẩn cho từng người luôn nha cả nhà!"

Khuôn lời livestream:
- Mở bằng "Cả nhà ơi" hoặc câu hỏi trúng nhu cầu ("có phải chị em mình đang tìm…").
- Xen câu kéo khách: "đúng không cả nhà", "các chị nhìn cho em này".
- Nói số đơn đã bán đúng số "Đã bán" trên trang, viết bằng chữ ("hơn trăm nghìn đơn").
- Kết: "nhắn ngay… em tư vấn size chuẩn luôn nha cả nhà".
- Không bịa khan hiếm, không bịa giảm giá, không kể trải nghiệm mặc thử (người ảo chưa mặc).
