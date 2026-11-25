# Soát độ thật và sổ lỗi

Lỗi "lộ AI" là lỗi trái với cách quần áo và cơ thể vận hành ngoài đời. Người xem bỏ qua được ánh sáng hơi giả, nhưng thấy ngay một động tác vô lý (ví dụ dây rút ở gấu áo mà tay lại kéo tận trên ngực). Đọc hết tệp này trước khi viết lời và lệnh.

## Viết hành động sao cho ít lỗi
1. Mỗi động tác ghi rõ **tay chạm đâu, đi hướng nào, dừng ở đâu**. Không viết chung chung như "khoe cạp quần".
2. Tránh cho tay thao tác chi tiết nhỏ (dây rút, cúc, khóa). Cần nhắc thì để lời nói nhắc, tay chỉ chạm nhẹ đúng chỗ.
3. Không cho hai tay cùng cầm một chi tiết nhỏ (cổ tay áo, cúc): vải dễ vo thành cục, bàn tay lẫn vào vải.
4. Không đặt tay lên ngực, không chạm cổ áo: dễ làm vạt bung, dễ nhắm mắt khi cười.
5. Cảnh xoay: nghiêng 45 độ rồi quay lại, không quay lưng, không bước.

## Cổng khóa mặt (bắt buộc, `scripts/khoa_mat.py`)

KOL là gương mặt của shop: một cảnh sai mặt là hỏng cả video. Cổng chạy 3 lần: ảnh gốc (`anh`), các clip (`clip`), trước khi lưu kho (`kiem`). Người chấm là người soát độc lập, không phải người vừa tạo ảnh.

| Mục | 5 | 4 | 3 trở xuống = CHẶN |
|---|---|---|---|
| Mặt (từng cảnh) | chắc chắn cùng người với mặt chuẩn | cùng người, khác nhẹ do góc, biểu cảm | trông như người khác; mặt bè/gầy đi; đổi mắt, mũi, môi, mái, độ dài/kiểu tóc |
| Da mặt (cùng các tệp chấm mặt) | trắng sáng mịn đều màu, sạch | đạt, khác nhẹ do ánh sáng | có nốt ruồi, chấm nâu, tàn nhang, mụn, vết thâm nhìn thấy được; da xỉn, sạm |
| Chân (ảnh gốc, cảnh 3, cận dưới) | thon, sáng mịn đều màu như chân chuẩn, đầu gối sáng | đạt, khác nhẹ do ánh sáng | da sẫm hay đỏ hơn mặt, đầu gối thâm, chân to, vết, sần, gân |
| Mẫu áo (ảnh gốc) | đúng từng chi tiết ảnh nhà bán | lệch rất nhỏ không ai để ý (hoa văn cúc) | sai kiểu cổ, thiếu/thừa cúc, túi, sai dài, sai màu |

Sau khi người soát chấm đạt, **người dùng phải tự xem tờ so mặt và duyệt** (`khoa_mat.py duyet`): máy và agent chấm "giống" chưa đủ, chủ shop là người biết mặt KOL của mình.

Chân bị che hết (váy dài, quần dài) thì chấm `chan=0` (không thấy). Máy đo màu da chân (L, a) so với chân chuẩn; vượt ngưỡng thì in CẢNH BÁO, người chấm phải soi đầu gối và ghi `--ghi` lý do mới qua.

## Danh sách soát (trên bảng 4 khung/giây, ghi lỗi kèm giây)

**Mặt và mắt:** cùng một người suốt video, so với `mat-chuan.png` trên tờ `khoa-mat/to-mat.jpg`; mắt mở khi nối cảnh; không nhíu mày, không nheo, không nháy một mắt; răng, tai, bông tai, tóc không đổi. **Da mặt:** phóng to từng ô mặt, da trắng sáng mịn; thấy nốt ruồi, chấm nâu, tàn nhang, mụn (kể cả chỉ hiện ở vài giây) là CHẶN, sửa ảnh gốc bằng Muse hoặc tạo lại cảnh.

**Chân:** trên `khoa-mat/to-chan.jpg`, chân sáng mịn đều màu như chân chuẩn, đầu gối không thâm, không đỏ; tất, bốt, giày đúng như ảnh gốc suốt cảnh.

**Tay và cơ thể:** đủ 5 ngón, không xuyên vải, khớp gập đúng chiều; thao tác đúng vị trí chi tiết thật; chân không trượt trên sàn.

**Trang phục:** cúc, khóa giữ nguyên trạng thái; cổ, tay, gấu, logo không đổi hình, đổi màu; không mọc thêm lớp, không biến mất; màu cảnh cận khớp màu cảnh nói (Muse hay vẽ cận ngả vàng); quần/váy giữ dáng.

**Khung và phòng:** máy không zoom khi lệnh ghi đứng yên; cảnh cận không để mặt lọt vào khung; giá treo, chậu cây, tường không đổi chỗ, không biến mất; không có chữ, logo lạ.

**Lời và hình:** lời nói chi tiết gì thì hình có chi tiết đó; chỉ nói kiểu phối đang thấy trên hình; mọi ý có nguồn trong `nguon.md`.

## Sổ lỗi đã gặp (thêm dòng mỗi khi gặp lỗi mới)

| Loại | Lỗi | Cách phòng |
|---|---|---|
| Giọng | Lệnh "năng lượng cao" làm KOL nhíu mày, nheo mắt suốt cảnh | Luôn có câu nét mặt "lông mày thả lỏng… năng lượng nằm ở giọng nói và đôi tay"; còn căng thì phủ cận hoặc tạo lại cảnh đó |
| Giọng | Giọng "điệu điệu", cảm thán dồn dập bị chê không giống người bán thật | Bỏ "xinh xỉu", "dã man", chuỗi cảm thán; dùng khuôn lời livestream trong `lenh-mau.md` |
| Lời | Lời quá 44 chữ: Muse nói tới giây 9,98, chữ cuối bị cắt khi clip hết | 35–44 chữ mỗi cảnh (`viet_lenh.py` tự chặn). Lỡ rồi thì cắt tiếng ở khoảng lặng thật trước vế cuối |
| Lời | Lời dưới 35 chữ: Muse nói chậm, nghỉ giữa câu 1 giây | Viết đủ 35–44 chữ |
| Lời | Đọc "5XL" thành "năm ích xeo"; "shop" thành "sóc" | Viết theo cách đọc ("size em-mờ đến năm ích-xì-lờ", "nhà bán"). Whisper viết gọn lại nên không kiểm được bằng chữ: nhờ người dùng nghe |
| Lời | Muse đọc thừa tiếng ("dài dáng xòe" thành "dài ráng sáng xòe") hoặc lặp chữ ("tận tận") | `so_loi.py` báo THỪA; tạo lại đúng cảnh đó, ghi rõ cụm phải đọc; lặp trọn cụm thì cắt bằng `tim_khoang_ngat.py` + `nghe_thu.py` |
| Lời | Muse bỏ một vế, tự thêm ý không có nguồn ("khách mua về toàn khen…") | Soát bản Whisper với `nguon.md`; cắt phần tiếng sai, che hình bằng cảnh cận |
| Lời | Nói "phối quần bò, chân váy" trong khi hình chỉ có một kiểu phối | Chỉ nói kiểu phối đang thấy trên hình |
| Cận | Cảnh cận dưới: máy tự ngẩng lên, chân ra khỏi khung, mọc thêm hoa ở eo | Câu "máy khóa chặt trên chân máy…"; chỉ tin 1,5–2 giây đầu |
| Cận | Cảnh cận ống quần đổi áo ngắn tay thành dài tay sau giây 4,5 | Chỉ dùng đoạn đầu clip cận; soát bảng khung cả clip |
| Cận | Cận thân trên 8% thì phóng quá tay | Ghi "tối đa 5%, không tiến sát hơn" |
| Màu | Cảnh cận ngả vàng, "như một chiếc áo khác" | `khop_mau_can.py` khớp kênh màu theo vùng áo cảnh nói |
| Dựng | Điểm nối rơi đúng lúc chớp mắt | Xem `soi_mat.py`, dời điểm cắt sang khung mắt mở; đoạn nhắm 0,6–0,8 giây thì kéo cảnh cận phủ qua |
| Dựng | Cảnh nói ngay từ khung đầu, câu sau chen vào câu trước không có nhịp nghỉ | Chèn 0,25–0,3 giây lặng lấy từ đầu cảnh khác vào danh sách tiếng; hình cận phủ đoạn đó |
| Dựng | Cắt thẳng nửa người sang toàn thân bị nhảy hình | `lui_may.py` (máy lùi êm ra trong 0,9 giây) |
| Dựng | `ffmpeg -t` đặt sau `-i` làm cắt cụt đầu ra | Luôn đặt `-t` TRƯỚC `-i` |
| Dựng | Hai chữ đọc dính ("ngứa lên"), cắt ở chỗ âm thấp nhất vẫn sót nửa chữ | Cắt theo giờ bắt đầu chữ sau trong Whisper, rồi nghe lại 1,4 giây quanh chỗ cắt |
| Dựng | Mốc chữ Whisper trễ khoảng 0,2 giây | Chốt điểm cắt bằng mức âm 20–50 ms (`soat_lo.py` in sẵn) |
| Dựng | Ghép đoạn nghe thử dưới 2 giây, Whisper bịa câu "cảm ơn các bạn đã theo dõi" | Đoạn nghe thử dài từ 2 giây trở lên |
| Máy | Chạy 4–5 lệnh Whisper cùng lúc, máy nghẽn 8 phút | `so_loi.py` nhận nhiều cảnh, nạp mô hình một lần; không chạy song song |
| Mắt | Ghép vùng mắt từ khung khác để "vá" mắt: mắt vỡ, lệch biểu cảm | KHÔNG vá mắt. Chọn đoạn mắt tốt, phủ cận, hoặc tạo lại cảnh |
| Cận | Cảnh cận thân trên có tay chạm cúc: sau khoảng 0,75 giây cổ tay áo màu kem rủ thành vòng vải mềm (lỗi chặn) | Soi từng 0,25 giây đầu clip cận, chỉ dùng đoạn sạch; thiếu thời lượng thì làm chậm đoạn sạch (`minterpolate`, `-t` trước `-i`) hoặc dùng chính cảnh nói có động tác khoe chi tiết đúng lúc lời nói |
| Lời | Dùng lại lời của video cũ có câu không còn đúng ảnh mới ("mặc quần hay chân váy", "đi Đà Lạt" không có trong nguồn) | Mỗi video soát lại từng câu với `nguon.md` và với hình đang có, kể cả lời đã từng đạt |
| Lời | Cổng nguồn ngưỡng "còn quá 2 chữ" cho lọt ý bịa ngắn ("sắp hết", "hàng hiệu") | Ngưỡng 0 chữ có nghĩa ngoài bảng; thêm danh sách cụm luôn chặn (LUON_CHAN trong viet_lenh.py) |
| Mặt | Chạy thử với KOL mới do Muse tạo, mặt kém sang, không ai so với mặt chuẩn; người soát chỉ ghi "mặt giữ sát" | Cổng khóa mặt: tờ so mặt từng cảnh + phiếu điểm, dưới 4 là chặn; chọn KOL chuẩn có gương mặt ưa nhìn ngay ở Bước 0 |
| Chân | Chân trần da hồng sẫm, đầu gối thâm, chân to ở cận chân, vẫn được giao | Câu chân trong lệnh ảnh và lệnh clip (`mo_ta_chan`); tờ so chân và số đo màu da trong cổng khóa mặt |
| Áo | Áo dạ cổ lá sen bị vẽ thành cổ đứng, chấm là lỗi nhẹ rồi vẫn giao | `chi_tiet_khoa` trong video.json (ghi cả cái KHÔNG được thành); sai mẫu áo ở ảnh gốc là CHẶN |
| Chấm | Chấm điểm tuyệt đối 8,6/10 mà không đặt cạnh video mẫu, video thua mẫu vẫn qua | Người soát vòng 2 so thành phẩm cạnh 2 video trong `video-mau/`; kém ở mặt nào là chưa giao |
| Mặt | Lệnh giọng "hào hứng" làm cảnh nói nghiêng đầu mạnh, cười toác lộ lợi, mặt tròn bè, mắt mở tròn, mày nhướn: cổng khóa mặt chấm 3, phải tạo lại | Câu giữ mặt trong lệnh: mặt thon, mắt hiền, không mở to mắt tròn, không nhướn mày, không cười toác, đầu nghiêng tối đa 10 độ; cảnh 1 mở bằng đứng thẳng vẫy chào, không nghiêng người |
| Áo | Cảnh xoay: chân váy bí (gấu phồng) đổi thành váy xòe xếp ly giữa clip rồi đổi lại | Ghi kiểu váy vào `chi_tiet_khoa` kèm "không xếp ly, không xòe"; cổng khóa mặt soi cả trang phục cảnh 3 |
| Muse | Tạo lại một cảnh với cùng tên tệp: trang hiện bản cũ ở cả hai thẻ, tải nhầm bản cũ | Đặt tên mới khi tạo lại (`s3-xoay-b.mp4`), so md5 với bản cũ trước khi dùng |
| Cận | Cảnh xoay bị máy tự tiến vào từ giây 2, mất bốt và chân, mặt to dần | Câu "máy khóa chặt trên chân máy… luôn thấy toàn thân từ đỉnh đầu tới giày" trong lệnh cảnh 3 |
| Chân | Ảnh gốc qua cổng với đầu gối "hơi hồng", lên clip cận chân Muse phóng thành đầu gối sần, thâm (chặn 2 lần); sửa da bằng code ra màu cam | Bộ đồ lộ đầu gối: trước khi cắt ảnh, nhờ Muse sửa ảnh "chỉ sửa da hai chân giống da chân ở ảnh 2" (đính ảnh + `chan-chuan.png`), chọn ảnh đầu gối phẳng sáng; không sửa da bằng code |
| Mặt | Người soát thành phẩm thấy mặt cảnh 2 đầy hơn, son hồng tím dù cổng clip đã cho qua | Soát thành phẩm so cạnh video mẫu; lệnh tạo lại ghi rõ "son màu đúng như ảnh, mặt thon như ảnh" |
| Dựng | Cảnh lùi máy dùng `--tu 0.05` rồi kế hoạch lại bắt đầu từ 0,05: mất đầu hiệu ứng, lệch môi 0,05 giây | `lui_may.py --tu` đã cắt sẵn; trong kế hoạch, đoạn s3-lui bắt đầu từ 0 (hoặc lùi vào đúng khung mắt mở, giữ quy tắc giờ s3-lui = vị trí − lúc bắt đầu đoạn lặng) |
| Áo | Cận trên tạo từ ảnh gốc, còn cảnh nói Muse tự thêm chi tiết (cúc nhỏ trên nắp túi): ghép lại thì nắp túi, cổ tay, móng tay đổi giữa cảnh nói và cận (lỗi CHẶN) | Sau khi có cảnh nói, cắt ảnh khung đầu cận trên từ chính khung cảnh 2 (vùng dưới cằm, 9:16), rồi tạo cận từ ảnh đó; lệnh ghi rõ nắp túi, cổ tay, móng "y như ảnh" |
| Cận | Cận trên vẫn phóng gần dần sau giây 3–4 dù lệnh ghi tối đa 5% | Chỉ dùng 0,3–4 giây đầu của cận trên |
| Dựng | Kế hoạch 9 đoạn hình: mỗi đoạn làm tròn về khung 24/giây, hình hụt 0,1 giây so với tiếng, cuối video đứng hình | `dung_chen_can.py` có `-shortest` cắt tiếng bằng hình; lời cuối phải dứt trước đuôi ít nhất 0,1 giây |
| Dựng | Đoạn mặt nói giữa video dài 5,2 giây, cận không rơi đúng câu nói chi tiết: người chấm so sánh chấm thua video mẫu ở nhịp | Lấy mốc chữ từ `so_loi.py`, đặt cận đúng câu nói chi tiết (cúc, cổ, chất vải, túi); đoạn mặt giữa video không quá khoảng 3–4 giây; điểm nối lúc mắt mở |

