# Sổ lỗi KOL review nghỉ dưỡng

Mỗi lỗi một dòng: ngày – lỗi – vì sao – cách tránh. Đọc trước mỗi video. Lỗi mới (do người dùng chỉ ra hoặc người soi bắt được) ghi ngay vào đây rồi đóng gói lại skill.

| Ngày | Lỗi | Vì sao | Cách tránh |
|---|---|---|---|
| 23/11/2026 | Video mẫu: mặt KOL đổi giữa các bối cảnh (giây 1, 4, 15, 47) | Mỗi cảnh tạo ảnh KOL riêng không khóa mặt | Mọi ảnh KOL sửa từ ảnh chuẩn đã duyệt; cổng `khoa_mat.py`; người dùng duyệt tờ mặt |
| 23/11/2026 | Video mẫu: hình xăm ở ngực lúc có lúc không | Muse tự thêm chi tiết | Lệnh có câu "không hình xăm, không vòng cổ"; người soi mặt soi cả cổ ngực |
| 23/11/2026 | Lấy `crop` có biến `t` trong FFmpeg báo lỗi | `crop` w/h chỉ tính một lần | Đẩy máy bằng `scale … eval=frame` rồi `crop` cố định (đã sửa trong `dung_video.py`) |
| 23/11/2026 | Phụ đề cắt giữa từ ghép ("làm du / lịch ơi") | Chia cụm cứng 4 chữ | Chia theo dấu câu rồi chia đều 2–4 chữ (đã sửa) |
| 23/11/2026 | Phụ đề, thẻ đặt cao quá (60%) so với mẫu | Ước sai vị trí | Đo mẫu: phụ đề 77,5%, thẻ 70,5%, thẻ kết đáy 73,5% chiều cao |
| 23/11/2026 | Muse từ chối tạo ảnh bộ đồ "áo hai dây lụa satin + sơ mi trễ một bên vai" | Bộ lọc an toàn của Muse | Dùng áo hai dây **linen** cổ V kín đáo, sơ mi khoác **ngay ngắn hai vai**; lệnh L1 đã sửa |
| 23/11/2026 | Tờ KOL: bộ 3 Muse đổi tóc sang đen, mặt bè, mũi to (agent chấm 3/5); bộ 1, 2 cười to làm mắt híp, da hơi mịn | Muse trôi mặt khi đổi nhiều bộ trong một tin | Lệnh L2 thêm câu khóa mặt chi tiết + "cười mỉm vừa phải, da thật có vân"; chỉ dùng bộ mặt ≥ 4/5 |
| 23/11/2026 | Anh An yêu cầu chung cho mọi KOL: da mặt xinh mịn trắng, không nốt ruồi | Chuẩn thẩm mỹ của anh | Lệnh ảnh và clip có câu da trắng sáng mịn, không nốt ruồi/chấm nâu; nd-soi-mat-kol chặn nếu có |
| 23/11/2026 | Clip Muse trôi mặt (mặt bè, tóc ngả nâu sáng, đổi người) ở 5/8 cảnh vòng 1 | Ảnh khung đầu toàn thân, mặt nhỏ (~90 px); câu "máy trôi lại gần" làm Muse đẩy sát rồi vẽ lại mặt | Ảnh khung đầu phải là **trung cảnh, mặt rộng ≥ 15% khung** (tạo sẵn trên Muse, không cắt phóng ảnh nhỏ); đính thêm ảnh bộ đồ đã duyệt làm "ảnh tham chiếu mặt"; lệnh clip ghi **MÁY CỐ ĐỊNH như trên chân máy, không đẩy vào mặt** |
| 23/11/2026 | Clip đổi bối cảnh giữa chừng (c1 từ cửa nhà chữ A sang hiên khác) | Máy đẩy sát mặt rồi Muse vẽ nền mới | Câu "bối cảnh giữ nguyên y như khung đầu suốt clip, không đổi sang chỗ khác" + máy cố định |
| 23/11/2026 | KOL nhíu mày, mếu khi nói câu than thở (nỗi đau) | Muse diễn theo nghĩa câu | Câu "luôn tươi cười kể cả khi nói câu than thở, không mếu, không nhíu mày" |
| 23/11/2026 | Son đỏ đậm, má đậm ở cảnh hoàng hôn | Ánh cam + Muse tự trang điểm đậm | "son hồng cam bóng nhẹ, má hồng đào nhạt, mặt chiếu sáng dịu trung tính" |
| 23/11/2026 | Muse báo xong nhưng không gắn video vào chat, hoặc chỉ trả 1/2 video | Lỗi Muse | Nhắn "gửi tệp video đó vào đây" / "còn thiếu VIDEO 2, tạo đúng như trên"; tab nền phải cuộn tới video mới tải được |
| 23/11/2026 | Bản nháp v1 phóng khung 1,2–1,36 lần làm mất bối cảnh, mặt chiếm cả khung | Clip Muse đã chặt sẵn | Phóng tối đa 1,14 lần; cú "đẩy vào" xen kẽ 1,0 / 1,14 |
| 23/11/2026 | Câu than c5 trượt soi mặt 5 lần liền (mặt ấm ức, đổi người) | Muse diễn theo nghĩa câu than | Viết lại câu than thành câu hỏi vui ngắn ("…đúng không nào?"), dặn "mỉm cười dịu suốt clip"; vẫn hỏng đoạn cuối thì dùng đoạn đạt + phủ ảnh/khung rộng |
| 23/11/2026 | Tiếng ngắn hơn hình 0,75 giây khi nối 20 đoạn (lệch khẩu hình dồn dần) | Khung đệm AAC + làm tròn khung từng đoạn | Đoạn trung gian dùng tiếng PCM, độ dài tròn số khung, `-frames:v` (đã sửa trong `dung_video.py`) |
| 23/11/2026 | Sửa `cat` tay làm mất cụm "điện thoại thôi" (người xem hiểu sai: ảnh do agent chụp) | Cắt theo giây không xem mốc chữ | Mỗi lần sửa `cat` phải chạy `so_loi.py` trên thành phẩm với lời ghép đủ 8 cảnh: THIẾU chữ là CHẶN |
| 23/11/2026 | Whisper gộp khoảng lặng vào mốc một chữ ("rồi" 3,92–4,82) nên còn lặng 0,8 giây | Mốc chữ Whisper không chính xác ở chỗ ngừng | `lap_ke_hoach.py` dò thêm lặng thật bằng `silencedetect` rồi cắt |
| 23/11/2026 | Nhạc chìm hẳn cuối bài, tắt cụt | `loudnorm` động + nén làm nhạc bị kéo xuống | Trộn không nén, đo rồi bù cố định về −14 LUFS + `alimiter`; nhạc nhỏ dần 0,9 giây cuối |
| 23/11/2026 | Nhiều ảnh tĩnh chèn (≈13% video) làm giống trình chiếu | Dùng ảnh chèn để che lỗi mặt | Ảnh chèn chỉ khi lời nói về ảnh/view, ≤ 1,3–2,4 giây, có đẩy chậm; còn lại giữ KOL |
| 23/11/2026 | Trong lúc chạy, nhiều chat dùng Claude in Chrome làm trình duyệt đang chọn đổi hồ sơ liên tục | Lựa chọn trình duyệt dùng chung | Gọi `select_browser` deviceId ngay trước mỗi lệnh Muse; báo điều phối nhắc chat khác tạm dừng |
| 23/11/2026 | Ảnh tĩnh kết (khung clip nguyên cỡ) đặt sau cú đã phóng 1,12 làm nhảy hình, đổi cỡ mặt đúng lúc thẻ kết | Dùng ảnh khác khung thay vì dừng hình | Dừng hình trên khung cuối của CHÍNH cú đó: `"giu_cuoi"` trong video.json → `"giu"` (tpad) trong ke-hoach |
| 23/11/2026 | `khoa_mat.py kiem` chỉ so md5, không biết clip chỉ được dùng một đoạn (vd c5 0–5,8 giây) | Phiếu có điều kiện nhưng máy không kiểm | Ghi đoạn được phép vào ghi chú cảnh trong video.json; người dựng và giám sát đối chiếu `cat` với ghi chú; đoạn ngoài phạm vi phải chấm lại |
| 23/11/2026 | Video Booster gia đình: Muse ra ảnh khung đầu toàn thân dù lệnh ghi "trung cảnh gần" | Muse hay trả khung rộng hơn lệnh | Nhắn lại ngay trong đoạn chat "máy đứng GẦN hơn, cắt từ thắt lưng, không thấy bàn chân"; vẫn rộng thì cắt chặt ≤ 1,25 lần |
| 23/11/2026 | Clip c2–c7 mặt trôi sang tròn bè, già, son cam đậm (soi mặt 6,3/10) dù ảnh khung đầu đúng | Đính ảnh bộ đồ (mặt đã hơi tròn) làm tham chiếu; lệnh clip không tả khuôn mặt; mặt chỉ ~120–160 px | Đính ẢNH MẶT CHUẨN GỐC cắt cận (gui/mat-chuan.jpg) làm tham chiếu, lệnh có đoạn "KHÓA GƯƠNG MẶT": trái xoan thon, V-line, không mặt tròn/bè, son hồng đào không cam |
| 23/11/2026 | Muse tự thêm một bé lạ áo hồng sau lưng KOL (c4) | Muse thêm người khi cảnh có trẻ em ở cảnh khác | Lệnh clip ghi "trong khung chỉ có…, không thêm người lạ suốt clip" |
| 23/11/2026 | Clip c8 đọc thêm chữ "Booster" sau câu kết; túi biến mất sau giây 7 | Muse tự chốt tên sản phẩm | Cắt trước chữ thừa, dừng hình khung cuối (`giu_cuoi`) |
| 23/11/2026 | Trang Muse chặn `eval` (CSP) khi dùng lại mẫu lệnh từ localStorage | CSP của muse.ai | Lưu mẫu lệnh dạng chuỗi rồi `replace`, không `eval` |
| 23/11/2026 | Câu kể chuyện "áo trắng lấm lem hết rồi" làm Muse diễn mặt mếu 4 giây | Muse diễn theo nghĩa câu (như câu than) | Dặn rõ "nói bằng giọng trêu đùa, vừa nói vừa cười, không mếu"; tạo 2 bản song song để chọn |
| 23/11/2026 | Giữ clip đạt từ vòng trước khi các clip khác đã tạo lại theo cách mới → lộ lệch mặt (c1, c8) | So chéo giữa các cảnh khắt khe hơn so từng clip | Khi đổi cách khóa mặt thì tạo lại cả bộ clip cùng lúc |
| 23/11/2026 | "Booster" bị cắt cụt thành "Boost" dù cắt sau mốc chữ Whisper | Whisper đặt mốc kết thúc tên riêng có phụ âm tắc sớm ~0,45 giây | Đặt chỗ cắt theo độ to: lùi tới khi tiếng < −40 dB rồi +0,05 giây; nghe lại đoạn cắt bằng Whisper riêng |
| 23/11/2026 | Bối cảnh 7/8 khối cùng một góc sân, máy giặt đặt giữa sân | Tạo mọi khung đầu từ một ảnh gia đình chuẩn | Lên bảng cảnh với mỗi cảnh một chỗ khác (hiên sau, bờ ao, đồng lúa, ngõ), ánh sáng đổi theo giờ; đồ điện đặt đúng chỗ thật (máy giặt dưới mái hiên, có ổ điện) |
| 23/11/2026 | Mặt KOL tròn ngay từ ảnh khung đầu nên clip nào cũng tròn | Ảnh khung đầu không đính ảnh mặt chuẩn | Lệnh L2 luôn đính ảnh mặt chuẩn cận (mat-chuan.jpg) và tả mặt thon; soi mặt ảnh khung đầu cạnh mặt chuẩn trước khi tạo clip |
| 23/11/2026 | Clip c7 Muse vẽ túi sản phẩm SAI MẪU (màu hồng xanh, chữ méo) | Lệnh động tác bảo "nhấc túi" trong khi ảnh khung đầu không có túi → Muse tự vẽ túi | Không bao giờ bảo KOL cầm/nhấc sản phẩm nếu ảnh khung đầu không có sẵn sản phẩm đúng mẫu; muốn có thì vẽ sản phẩm vào ảnh khung đầu trước (đính ảnh sản phẩm thật) |
| 23/11/2026 | Vẽ lại ảnh khung đầu làm tóc đổi màu (caramel, mái dày) lệch các cảnh khác | Lệnh vẽ lại chỉ tả mặt, không khóa màu tóc theo các cảnh đã dùng | Khi vẽ lại một cảnh, đính kèm một khung của cảnh liền kề làm mẫu tóc/da, ghi "tóc nâu sẫm như ảnh X" |
| 23/11/2026 | Phủ ảnh tĩnh CÓ MẶT KOL lên đoạn đang nói làm miệng đứng yên | Che đoạn mặt lỗi bằng ảnh khung đầu | Chỉ phủ ảnh không có mặt KOL (sản phẩm, cận chi tiết); ảnh tĩnh liền nhau ≤ 2,4 giây |
| 23/11/2026 | Hoàng hôn làm mặt KOL má bầu, tròn | Ánh cam xiên + Muse | Lệnh ghi "ánh sáng trung tính dịu trên mặt, mặt thon như ảnh chuẩn"; đính khung cảnh khác làm mẫu tóc/da |
| 23/11/2026 | `khoa_mat.py cham` chấm cả clip trong khi chỉ dùng một đoạn | Cổng không biết đoạn dùng | Người soi ghi rõ "chấm theo đoạn dùng từ–đến" trong phiếu |
