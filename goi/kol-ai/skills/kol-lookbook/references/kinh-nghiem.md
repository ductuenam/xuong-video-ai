# Sổ kinh nghiệm — lỗi đã gặp khi làm video lookbook KOL AI và cách tránh

Mỗi dòng dưới đây từng làm video bị chấm trượt. Video mẫu đầu tiên mất 16 vòng sửa mới đạt; video thứ ba còn 5 vòng nhờ đọc sổ này trước khi làm. **Gặp lỗi mới thì ghi thêm một dòng vào cuối sổ.**

## Gương mặt (lỗi bị trừ nhiều nhất)
- **Ghép cảnh từ nhiều clip/nhiều ảnh gốc là ra "nhiều người".** Mỗi bộ chỉ MỘT clip máy tiến; mọi cảnh có mặt của bộ (toàn, máy tiến) cắt từ chính clip đó. Clip tạo lại thì cảnh toàn của bộ đó cũng phải lấy từ clip mới.
- **Không tả hình mặt bằng chữ** ("mặt tròn, má đầy" → AI phóng đại thành mặt bầu). Chỉ ghi "giữ Y HỆT ảnh 1 và ảnh 3, không tròn hơn, không gầy hơn, không già hơn".
- **Muse trôi mặt về cuối clip** (dài ra, cằm nhọn, già đi, mọc tàn nhang), từng cảnh nhìn riêng vẫn ổn — chỉ lộ khi đặt các bộ cạnh nhau. Luôn mở tờ "so mặt các bộ" mà `tu_soat.py` xuất ra; bộ nào lệch thì tạo lại clip tiến bộ đó.
- **Máy tiến sát mặt** làm mặt bè, da bóng dầu: lệnh máy chỉ tiến tới ngang eo.
- **Trang điểm phải cố định**: cùng màu son, không kẻ mắt đuôi dài ở mọi bộ (lệch son giữa các bộ bị chấm "khác người").
- Điểm chấm mặt dao động khoảng ±0,2 giữa các lần chấm cùng một video: đừng cố chỉnh dựng để kéo điểm mặt, hãy tạo lại clip bộ bị gọi tên nhiều lần.

## Chớp mắt
- Mở hoặc kết cảnh lúc đang chớp là lỗi CHẶN. Điểm vào ≥ 0,2 giây sau khi mắt mở lại, điểm ra ≥ 0,1 giây trước khi nhắm.
- **Không có cái chớp nào bắt đầu trong 0,3 giây đầu và 0,2 giây cuối cảnh** (chớp 0,08 giây sau điểm vào vẫn bị chặn).
- Clip Muse gần như luôn chớp ở 0,3–0,6 giây đầu → cảnh toàn lấy SAU cái chớp đó (~0,65 giây).
- Cho phép MỘT cái chớp ngắn giữa cảnh; né cái nhắm dài (> 0,3 giây, mi sụp) và hai cái chớp trong một cảnh.
- Lập bảng chớp bằng `bang_chop.py` (cảnh tiến) và vùng cắt cố định quanh đầu (cảnh toàn) trước khi chọn điểm cắt.

## Phụ kiện, trang phục
- Không túi, không vòng tay, không mũ, không cài tóc ngay từ ảnh gốc: túi lơ lửng, vòng tay tự mọc thêm là lỗi CHẶN hay gặp nhất.
- Phụ kiện có khóa kim loại hay bị vẽ thành logo hãng; dùng đồ trơn.
- Ảnh cận chân và ma-nơ-canh sửa TỪ ảnh toàn thân đã chốt (cùng giày, cùng tất, cùng gấu). Ma-nơ-canh phải có đủ chi tiết thấy ở cảnh chân (ví dụ tất trắng).
- Clip chân: "máy đứng yên tuyệt đối, chỉ từ gấu xuống giày, không bao giờ thấy tay, eo, áo, mặt" — câu "bước một bước về phía máy" làm Muse ngẩng máy lộ cả người.
- Clip chân Muse chỉ đứng yên khoảng 1,2–1,6 giây đầu rồi bắt đầu dồn trọng tâm: cảnh chân lấy từ đầu clip; kết lúc hai chân còn đặt xuống.

## Dựng và nhịp
- Mỗi cảnh là số NGUYÊN phách; nửa phách bị chấm lệch nhịp. Nhạc mà trống trầm rơi mỗi 4 phách thì cho mọi cảnh 4 phách (cảnh cuối được ngắn hơn).
- **Đổi bài nhạc là phải đo lại lưới phách** bằng `do_phach.py` (khung 5 ms). Đo thô (10 ms) từng ra sai nhịp → 6/8 điểm cắt trượt, bị chặn. Bài có hai ứng viên nhịp điểm sát nhau là bài nhịp không rõ: nên chọn bài khác.
- Cảnh dưới 1,5 giây bị trừ điểm (trừ cảnh cuối).
- Clip Muse đứng yên 2–5 khung đầu: `tu_soat.py` đo và báo, đặt điểm vào sau khúc đó.
- Ảnh góc: cảnh toàn và chân ở góc dưới phải, cảnh máy tiến ở góc trên phải (người choán ngang khung); cảnh chân nào giày chạm góc dưới thì đưa ảnh góc lên trên. Lề phải 40 px.
- Tổng hình ≤ độ dài nhạc còn lại (trừ `nhac_tu`), nếu không nhạc sẽ lặp ở cuối.
- Nền trong nhà nhiều chi tiết: ghi `"nen": "phong"` trong kế hoạch (phép đo "ảnh góc đè người" chỉ đúng với phông trơn) và soát ảnh góc bằng mắt.

## Chất lượng hình
- Clip Muse chỉ 720p, phóng lên 1080p. Hạt hậu kỳ dày (mức 12) + nén mạnh làm video "không HD"; mức 5 + crf 17 + trần 24 Mb/s là cân bằng tốt; hạt 3 bị chấm "da mịn kiểu lọc".
- Gắn hệ màu bt709 (đã có trong `quay_dien_thoai.py`) để điện thoại không lệch màu.

## Muse
- Mỗi tin một yêu cầu, chờ xong mới gửi tin sau; gửi dồn bị "lỗi nội bộ".
- Tài khoản bị giới hạn số video trong 24 giờ (không báo trước giờ mở lại): chuẩn bị tài khoản thứ hai; hết lượt thì dừng, không cố gửi tiếp.
- Mỗi thẻ trình duyệt chỉ tự tải được một tệp: gom nhiều clip vào một gói `goi-muse-*.bin` rồi tách trên máy bằng `tach_goi_muse.py`.
- Khung chat chỉ giữ vài video gần nhất trong trang: cuộn ngược để nạp lại clip cũ trước khi gom (mã trong `muse-js.md`).
- Có nơi Muse báo không hỗ trợ ở quốc gia/khu vực của tài khoản: dùng tài khoản khác, đừng cố lách.
- Muse là trang https://muse.ai (đăng nhập sẵn trên trình duyệt có Claude in Chrome); meta.ai là trang khác, ở đó thấy "Đăng nhập" là bình thường.
- Đính ảnh lên Muse: Claude chỉ đính được tệp nằm trong thư mục làm việc của phiên (thư mục dự án đang mở). Chép ảnh cần đính vào một thư mục con của dự án trước khi đính.
- Tờ so mặt chính là cổng `khoa_mat.py` (dò mặt bằng OpenCV, cắt ô vuông quanh mặt). `so_mat_anh.py` chỉ để so nhanh các phương án: ảnh đầu tiên nên là ảnh toàn thân (`kol/kol-chuan.png`), không phải ảnh chân dung.
- Clip máy tiến hay trôi mặt ở 1,5 giây cuối (mặt dài ra, già đi): soi khung 9,6 giây; cảnh tiến lấy khúc trước 8,5 giây.
- Phông trơn: ảnh góc cảnh toàn để `goc_cao` 0,30 (0,38 chạm tay, váy ở cuối cảnh khi máy tiến làm người to ra; phép đo đè người của tu_soat chỉ đo khung đầu nên không bắt được).
- Clip tiến không có khúc sạch 4 phách thì dời bộ đó xuống cuối video, cảnh tiến 3 phách làm cảnh kết.
- Son đỏ, da mịn sinh ra ở bước CLIP (ảnh gốc vẫn son nhạt): lệnh clip phải giữ son đúng màu khung đầu. NHƯNG (23/11) đừng viết chữ "tàn nhang" trong lệnh clip dưới bất kỳ dạng nào: Muse vẽ tàn nhang dày dần phủ hai má. Ghi "da mặt giữ y hệt khung đầu, không thêm bất cứ đốm hay chấm nào lên da".
- Cảnh toàn lấy muộn (≥ 2,5 giây, máy đã tiến) thì tay và váy choán góc dưới phải: đưa ảnh góc lên trên 0,24, hoặc lấy cảnh toàn trước 2 giây.
- Clip chân không phải lúc nào cũng đứng yên ở đầu clip: ghép dải khung CẢ clip (mỗi 0,2 giây) rồi mới chọn khúc hai chân đặt yên.
- FFmpeg bản mới bỏ `-vsync`, dùng `-fps_mode`; trên Windows bộ lọc `drawtext` có thể lỗi Fontconfig — ghi nhãn giây bằng Python (PIL) thay vì drawtext.
- Video mẫu chạy thử (3 bộ, 22/11/2026): vòng 1 8,7 (son đỏ, da mịn — lệnh clip chưa giữ son/da), vòng 2 9,30 sau khi thêm câu giữ da/son vào lệnh clip. Lỗi nhẹ còn lại: son bộ 2–3 vẫn ngả đỏ gạch, khuyên tai to dần theo bộ — đã thêm "muted rose, không đỏ gạch" và "khuyên tai đúng cỡ đinh rất nhỏ" vào lệnh clip.
- Cảnh toàn cắt từ clip máy tiến vẫn đặt ảnh góc DƯỚI như mọi cảnh toàn (chỉ cảnh máy tiến mới đặt trên); dưới bị che thì lấy cảnh toàn sớm hơn (trước 2 giây) thay vì đổi vị trí.
- (23/11/2026, video thử KOL thương hiệu) Sửa đồ trên ảnh KOL chuẩn giữ mặt tốt hơn hẳn tạo người mới, nhưng Muse vẫn tự đổi TRANG ĐIỂM: thêm kẻ mắt đuôi sắc (mắt trông to/dài, già hơn), thêm nốt ruồi ở hàm, son và tàn nhang đậm hơn. Cổng khóa mặt chặn 2/3 bộ ở lượt đầu. Lệnh ảnh toàn thân phải có câu "KHÔNG kẻ mắt đuôi dài, KHÔNG nốt ruồi, son đúng độ đậm như ảnh 1" (phần tàn nhang ĐÃ THAY bằng luật da sạch ngày 23/11 ở cuối sổ: không tàn nhang, không nốt ruồi, không chấm nâu); tạo lại kèm câu nêu đích danh lỗi thì đạt.
- Ảnh KOL chuẩn có đầu gối hồng sẫm thì mọi chân sau đều sẫm theo. Sửa MỘT lần trên chính ảnh chuẩn: "CHỈ sửa da hai chân: trắng sáng mịn, đầu gối sáng không thâm…" — Muse giữ y mặt, chân sạch. Từ đó dùng ảnh đã sửa làm `kol-chuan.png`.
- Phông màu hồng/be trùng màu da làm bộ dò mặt theo màu da cắt nhầm: gói đã kèm mô hình dò mặt YuNet (`scripts/mo-hinh/`) nên tờ so cắt đúng mặt; đừng xóa thư mục này.
- Phép đo màu da chân bị nhiễu khi váy/quần màu nâu, be (vải lọt vùng màu da): cảnh báo "da sẫm" lúc đó là giả, người chấm soi phần da thật (cổ chân, mu bàn chân) rồi ghi lý do.
- (23/11) Clip máy tiến hay trôi mặt về nửa sau (tàn nhang dày, son cam, má phúng) dù ảnh khung đầu đã qua cổng: cổng bước clip chặn 2/3 clip lượt đầu. Tạo lại kèm câu nêu đích danh lỗi; nếu lại hỏng, viết lệnh GỌN hơn (bỏ câu về tàn nhang, thêm "mắt mở to tự nhiên, đầu thẳng không nghiêng") — bản gọn đạt ngay.
- (23/11) Áo len cổ cao làm Muse đẩy cằm, hàm bè ra (chặn 3 lần); vải len nâu/be hay loang mảng sẫm, nhờ Muse "chỉ sửa vải" thì nó vẽ lại cả mặt. Gặp mẫu như vậy: chọn biến thể cổ tròn / màu đen hoặc màu đậm đều của chính mẫu đó (ghi rõ trong nguon.md), đừng vá.
- (23/11) Gửi tin lúc Muse còn đang trả lời tin trước thì tin bị rơi mất (ô nhập trống nhưng không có trong khung chat). Sau mỗi lần gửi đọc 200 ký tự cuối khung chat để chắc tin đã vào.
- (23/11) Clip tiến chớp dày (khoảng mỗi 1,2 giây) thì không có cảnh toàn 4 phách nào chỉ một chớp: soi bảng chớp ngay khi tải clip; khoảng cách hai lần chớp liền nhau dưới 1,9 giây ở 0–3 giây đầu thì tạo lại clip tiến bộ đó (thêm "mắt mở to tự nhiên, ít chớp") trước khi cắt ghép, đừng nhận cảnh toàn 2 chớp. Còn cách cuối: cảnh toàn 3 phách nếu nhạc chậm đủ ≥ 1,5 giây.
- (23/11, chủ shop xem video thử, KHÔNG duyệt) "Mặt có nốt ruồi … tẩy đi, da phải xinh mịn trắng": KOL không được có nốt ruồi, chấm nâu, tàn nhang đậm, kể cả khi ảnh chuẩn có. Làm sạch da ảnh chuẩn một lần (lệnh Bước 0) và mọi lệnh có mặt chép câu da sạch; cổng và agent soi da chấm ≤ 3 nếu còn chấm.
- (23/11) Nhờ Muse "chỉ xóa tàn nhang, giữ 100% mặt" lần đầu thường chỉ làm MỜ chấm (cổng vẫn chặn); lần 2 ghi "xóa hết hoàn toàn, không chỉ làm mờ, trên cả hai má, mũi, cằm" thì sạch, mặt giữ nguyên. Ảnh KOL chuẩn làm sạch phải đưa chủ shop duyệt trước khi dùng làm chuẩn.
- (23/11) Lấy ảnh gốc từ trang Muse: chỉ lấy ảnh MỚI hiện ra sau khi bấm mở (mã trong muse-js.md), vì "ảnh lớn đầu tiên trong trang" có thể là ảnh cũ. Tải về rồi luôn ghép so trước khi dùng.
