# Lệnh Muse mẫu cho video KOL review nghỉ dưỡng

Thao tác Muse (đính ảnh, gửi, tải về, lỗi thường gặp): `lam-tren-muse.md`. Mọi lệnh viết **một dòng** (Enter là gửi). Thay phần trong `<…>`.

## Mục lục
- L0. Bối cảnh minh họa (chỉ video thử / khi chủ khu chưa gửi ảnh)
- L1. Tờ KOL: trang điểm + bộ đồ (gửi người dùng duyệt)
- L2. Đặt KOL vào bối cảnh (ảnh khung đầu từng cảnh)
- L3. Clip nói (3–4 clip mỗi tin)
- L4. Tạo lại một ảnh / một clip

## L0. Bối cảnh minh họa

Không đính ảnh. Muse trả ảnh 9:16 khoảng 1152×2048. Mỗi tin 3–4 ảnh; xin thêm bằng tin tiếp theo trong cùng đoạn chat ("tiếp ảnh 5 đến 7, cùng khu nghỉ đó").

```
Tạo 4 ảnh riêng, mỗi ảnh khung dọc 9:16, là ảnh chụp bằng điện thoại của CÙNG MỘT khu nghỉ dưỡng trên đồi thông nhìn ra biển ở Việt Nam: các căn nhà gỗ hình chữ A mái tôn đen, mặt tiền gỗ nâu đỏ, cửa kính khung đen, có số phòng 07 nhỏ trên cửa, đèn mây đan hình chuông treo trước cửa, sàn hiên gỗ, lan can sắt đen. Ảnh không có người, không chữ, không logo. Ánh sáng tự nhiên, màu thật, như chủ khu tự chụp gửi. ẢNH 1: đứng trên hiên nhìn thẳng vào mặt tiền nhà chữ A số 07, cửa kính mở hé, đèn mây sáng, trời nắng trong. ẢNH 2: cầu thang sắt bậc gỗ đi lên giữa vườn cây, dây đèn bóng tròn vàng giăng trên tán cây, phía sau là dãy nhà chữ A trên cột, chiều muộn. ẢNH 3: hiên gỗ trước nhà chữ A, hai cánh cửa kính mở, một ghế mây và bàn trà nhỏ, đèn mây treo trên đầu, nắng chiều vàng. ẢNH 4: phòng ngủ bên trong nhà chữ A, trần gỗ dốc hai bên, giường trắng gọn, gương tròn viền mây, vài tranh nhỏ treo tường, cửa kính tam giác nhìn ra cây xanh, ánh sáng ban ngày. Bốn ảnh phải cùng một khu, cùng màu gỗ, cùng kiểu đèn.
```
Tin tiếp theo (cùng đoạn chat):
```
Tạo tiếp 3 ảnh riêng, khung dọc 9:16, cùng khu nghỉ ở các ảnh trên, không người, không chữ. ẢNH 5: ban công gỗ lan can trắng có một chiếc võng, dây đèn bóng tròn, nhìn ra đồi thông và mái nhà chữ A, trời trong. ẢNH 6: điểm ngắm cảnh trên đỉnh đồi, nhìn xuống vịnh biển xanh ngọc có đảo nhỏ và vài thuyền, cây thông và hoa dại phía trước, nắng đẹp. ẢNH 7: sàn gỗ ngắm hoàng hôn trên biển, trời hồng cam, mặt biển lấp lánh, lan can gỗ, ghế lười. Màu gỗ và kiểu lan can khớp với các ảnh trước.
```
Đặt tên `boi-canh/bc1…bc7.png`. Chủ khu gửi ảnh thật thì bỏ L0, đổi ảnh khách thành `boi-canh/bcN.png` (cắt về 9:16 bằng `cat_916.py`).

## L1. Tờ KOL (trang điểm + bộ đồ)

Đính **ảnh 1 = ảnh chuẩn KOL** (`assets/anh-goc-kol.png`). Học phong cách mẫu: tông kem – trắng – be, đồ linen, satin, đi biển nhẹ nhàng.

```
Sửa ảnh 1. Giữ CHÍNH XÁC gương mặt của cô gái trong ảnh 1: khuôn mặt trái xoan thon, mắt to hai mí, sống mũi, đôi môi, mái thưa mỏng, tóc nâu đen dài uốn sóng lớn, nụ cười, tuổi và vóc dáng; không được thành người khác. Trang điểm lại cho xinh hơn một chút kiểu Hàn đi biển: nền căng bóng nhẹ, má hồng đào, môi hồng cam có độ bóng, kẻ mắt mảnh, mi cong, lông mày tự nhiên; da mặt trắng sáng, mịn màng, đều màu, xinh, KHÔNG nốt ruồi, không chấm nâu, không tàn nhang, không mụn, nhưng vẫn là da người thật không bóng nhựa. Đổi bối cảnh thành hiên gỗ khu nghỉ có cây xanh, ánh sáng ban ngày mềm. Tạo 3 ảnh riêng, khung dọc 9:16, toàn thân từ đỉnh đầu tới bàn chân, đứng thoải mái nhìn thẳng máy cười tươi, mỗi ảnh một bộ đồ: ẢNH 1: áo hai dây linen màu kem cổ chữ V kín đáo, sơ mi linen trắng rộng khoác ngoài mở cúc (khoác ngay ngắn trên hai vai), chân váy linen màu be dài quá gối xẻ tà nhẹ bên hông, kính râm gọng nâu cài trên đầu, dép sandal quai mảnh màu be. ẢNH 2: đầm maxi linen trắng hai dây dáng suông, mũ cói rộng vành cầm tay, dép sandal màu be. ẢNH 3: áo croptop dệt kim màu kem tay ngắn, quần ống rộng linen màu be cạp cao, sơ mi linen trắng khoác ngoài, kính râm cài đầu, dép sandal. Không hình xăm, không vòng cổ to, không chữ, không logo.
```
Lưu `kol/1-bo1.png`, `kol/2-bo2.png`, `kol/3-bo3.png`. Chạy `khoa_mat.py kol`, giao `nd-soi-mat-kol` chấm, rồi gửi **người dùng duyệt** (mặt + trang điểm + chọn bộ đồ) qua điều phối. Chưa duyệt chưa sang L2.

## L2. Đặt KOL vào bối cảnh

Mỗi tin tối đa 4 ảnh đính: **ảnh 1 = ảnh KOL bộ đồ đã duyệt**, ảnh 2–4 = bối cảnh. Mỗi tin ra 3 ảnh khung đầu.

```
Ảnh 1 là cô gái người mẫu (giữ CHÍNH XÁC gương mặt, trang điểm, kiểu tóc, màu da, vóc dáng và TOÀN BỘ trang phục như ảnh 1: <mô tả bộ đồ>). Ảnh 2, 3, 4 là ba chỗ trong khu nghỉ. Tạo 3 ảnh riêng, khung dọc 9:16, đặt cô ấy vào đúng từng chỗ, giữ nguyên bối cảnh như ảnh gốc (đồ vật, màu gỗ, ánh sáng), như ảnh bạn đi cùng chụp bằng điện thoại cầm tay ngang ngực. Ánh sáng trên người khớp ánh sáng của chỗ đó, có bóng đổ thật, người đúng tỉ lệ với cửa và ghế. ẢNH A (bối cảnh ảnh 2): <cỡ cảnh, tư thế, tay, đạo cụ>. ẢNH B (ảnh 3): <…>. ẢNH C (ảnh 4): <…>. Mặt nhìn thẳng máy, mắt mở to, cười mỉm vừa phải; da mặt trắng sáng, mịn màng, đều màu, xinh, KHÔNG nốt ruồi, không chấm nâu, không tàn nhang, không mụn, nhưng vẫn là da người thật không bóng nhựa; tay đủ năm ngón. Không hình xăm, không thêm phụ kiện, không chữ.
```
Tư thế mẫu (học từ video mẫu):
- c1 cửa nhà chữ A: trung cảnh từ gối lên, đứng trên hiên trước cửa, tay phải giơ vẫy chào, tay trái cầm mũ cói.
- c2 cầu thang đèn dây: toàn thân đứng trên bậc thứ ba, tay trái vịn lan can, tay phải giơ ngang vai.
- c3 hiên: ngồi trên ghế mây bắt chéo chân, người hơi nghiêng về máy, tay phải chỉ lên đèn mây.
- c4 phòng ngủ: ngồi mép giường, trung cảnh từ đùi lên, hai tay đặt trên gối, mũ cói đặt trên giường.
- c5 ban công: trung cảnh, tựa nhẹ lan can trắng, quay người về máy.
- c6 đỉnh đồi: trung cảnh từ hông lên, vịnh biển phía sau, gió nhẹ làm tóc bay.
- c7 hoàng hôn: trung cảnh, hai tay ôm trái dừa xanh có ống hút trước bụng, trời hồng cam phía sau.
- c8 cửa nhà chữ A (kết): toàn thân đứng giữa khung trước cửa mở, hai tay buông.
Lưu `anh-kol/k1…k8.png`, chạy `khoa_mat.py kol` lại, soi mặt từng ảnh trước khi tạo clip.

## Bài học video thử 23/11 (đọc trước L2, L3)

- Khung đầu **trung cảnh gần từ hông trở lên, mặt ≥ 1/5 bề ngang khung**. Toàn thân → Muse trôi mặt (5/8 clip vòng 1).
- Mỗi tin clip đính **ảnh bộ đồ đã duyệt ở cuối** làm "ảnh tham chiếu gương mặt, không dùng làm khung".
- **MÁY CỐ ĐỊNH**; câu "trôi lại gần" làm Muse đẩy sát mặt rồi vẽ lại mặt và cả nền.
- Câu than → Muse diễn mặt ấm ức: viết câu than thành câu hỏi vui ngắn, dặn cười dịu suốt clip.
- Thêm: tròng mắt nâu đen không lens; son hồng cam không đỏ; kính tròng nâu không tráng gương.
- Một tin 2 clip ổn hơn 3; Muse có lúc chỉ trả 1/2 → nhắn "còn thiếu VIDEO 2".
- Có thể gộp "tạo ảnh khung đầu rồi dùng ảnh đó tạo video" trong một tin (Muse làm được, tiết kiệm một lượt).

## L3. Clip nói

Mỗi tin đính 3–4 ảnh khung đầu (`k1…`), ra 3–4 clip 10 giây 720×1280 có giọng. Lời lấy nguyên văn `loi.json`.

```
Tạo <n> video riêng bằng Muse Video, mỗi video 10 giây, một cảnh liền, giữ nguyên tỉ lệ dọc 9:16, giữ CHÍNH XÁC khuôn mặt, trang điểm, tóc, trang phục và bối cảnh như ảnh. Đặt tên tệp: video 1 → c1-noi.mp4, video 2 → c2-noi.mp4, video 3 → c3-noi.mp4. Video k dùng ảnh k làm khung hình đầu tiên. MÁY CỐ ĐỊNH như đặt trên chân máy ngang ngực, không đẩy vào mặt, không xoay, không cắt cảnh, bối cảnh giữ nguyên. Ảnh cuối CHỈ là ảnh tham chiếu gương mặt chuẩn. Cách nói: như cô gái trẻ đang đi chơi khu nghỉ quay vlog kể chuyện với người quen, giọng nữ miền Bắc trẻ, tươi, thân thiện, tự nhiên, có lên xuống giọng, nhấn nhẹ chữ quan trọng, chữ đệm cuối câu như nhá, đấy, thôi nói nhẹ và ngắn; ngắt hơi ngắn ở dấu phẩy và dấu chấm; tốc độ vừa khoảng 4,8 chữ mỗi giây, câu kể chậm hơn câu liệt kê; KHÔNG giọng đọc quảng cáo, không giọng livestream bán hàng, không điệu, không kéo dài cuối câu; nói ngay từ khung đầu, đọc đúng từng chữ như lời, không thêm không bớt, không lặp chữ. QUAN TRỌNG: nói hết lời trước giây 8,5, chữ cuối rõ trọn, sau đó im lặng, chỉ cười nhẹ nhìn máy đến hết video. Da mặt: da mặt trắng sáng, mịn màng, đều màu, xinh, KHÔNG nốt ruồi, không chấm nâu, không tàn nhang, không mụn, nhưng vẫn là da người thật không bóng nhựa. Nét mặt: luôn tươi, cười khi nói, lông mày thả lỏng, không nhíu mày, không nheo mắt. Mắt: mở tự nhiên nhìn thẳng máy, chớp hai mắt cùng lúc, chớp thưa. Tay có động tác theo lời, đổi khoảng mỗi 1,5–2 giây, tay đủ năm ngón. Không nhạc nền, không chữ, không phụ đề. VIDEO 1: <động tác theo giây>. Lời VIDEO 1: "<lời c1>" VIDEO 2: … Gửi đủ <n> video, xong chỉ báo kích thước và thời lượng.
```
Động tác khớp chữ (theo mẫu): vẫy khi chào; chỉ tay khi nói tới vật; đặt tay lên ngực "nó tự viết"; hai tay ngửa ở câu hỏi "lấy đâu ra"; hai tay làm khung ảnh ở chữ "chụp"; chỉ ra biển "chỗ nào đẹp"; xòe tay mời ở câu kết.

## L4. Tạo lại

Ngay trong đoạn chat đó, đính lại đúng ảnh khung đầu:
```
Tạo lại VIDEO <n> đúng y như lệnh trên, cùng ảnh, cùng lời. Lần trước <lỗi cụ thể, giây nào: mặt khác ảnh, đọc sai chữ…>. Lần này <cách tránh>. Chỉ tạo 1 video này, đặt tên c<n>-noi-b.mp4.
```
Đổi tên tệp mỗi lần (`-b`, `-c`) vì Muse hay hiện lại bản cũ. Tối đa 3 lần một cảnh rồi dừng, báo.
