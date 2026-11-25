# Phân tích video mẫu "Anh chị làm du lịch, nghỉ dưỡng đâu rồi"

Tệp: `video-mau/mau-nghi-duong.mp4`. Phân tích 23/11/2026 bằng FFmpeg (dò cắt cảnh, khung 1–2 hình/giây) và Whisper large-v3 (lời có mốc từng chữ). Khung lưu ở `phan-tich-mau/khung/`, tờ khung có giờ `to_01–03.jpg`, khung lớn `zoom6.jpg`, lời `loi.json`.

## 1. Thông số

| Mục | Giá trị |
|---|---|
| Độ dài | 51,3 giây |
| Khung | 1080×1920, 24 hình/giây, mã AV1 |
| Tiếng | AAC 48 kHz stereo, độ to cả bài −14,1 LUFS, LRA 4 LU |
| Số cú cắt | 16 (trung bình 3,0 giây/cú) |
| Số bối cảnh | 7 chỗ khác nhau + quay lại chỗ đầu để kết (8 khối) |

## 2. Đây là video gì (điều người giao việc chưa nói)

Không phải video review khu nghỉ cho khách du lịch. Đây là **video quảng cáo khóa học làm video bằng AI agent, nhắm vào chủ khu nghỉ / người làm du lịch**. KOL ảo vừa đi "review" khu nghỉ (để chứng minh), vừa nói với chủ khu: chỉ cần gửi vài tấm ảnh, agent tự nhận ra khu, tự viết lời, đưa người mẫu ảo vào; không phải mời người nổi tiếng, không phải tự quay. Kết: đăng ký khóa học.

→ Skill phải làm được **2 loại lời** trên cùng một hình:
- **Loại A – chào dịch vụ cho chủ khu** (đúng như mẫu): nói với "anh chị làm du lịch".
- **Loại B – review cho khách du lịch** (video thật giao chủ khu đăng): nói với "cả nhà / các bạn", khoe phòng, view, giá, đặt phòng. Cùng khung cảnh, cùng nhịp, khác lời.

## 3. Bảng cảnh

| Giây | Bối cảnh | Cỡ cảnh, máy | KOL làm gì | Chữ trên hình |
|---|---|---|---|---|
| 0,0–0,9 | **Ảnh chủ khu gửi**: nhà chữ A, ảnh nằm giữa, trên dưới là chính ảnh đó phóng to làm mờ | Ảnh tĩnh | — | Ô vàng "Ảnh chủ khu gửi" giữa trên |
| 0,9–2,3 | Cửa nhà chữ A gỗ, đèn mây treo, số phòng 07, lan can sắt đen | Trung (gối trở lên), máy cầm tay hơi lắc | Vẫy tay chào, tay trái cầm mũ cói | Ô xanh ngọc "Người mẫu ảo do AI tạo ra" |
| 2,3–3,4 | Như trên | Cận trung (hông trở lên), đẩy vào | Nói, cười | — |
| 3,4–4,8 | Như trên | Cận (ngực trở lên) | Nói "chưa đến bao giờ đâu nhá" | Ô đỏ nghiêng "CHƯA TỪNG ĐẾN ĐÂY!" |
| 4,8–11,2 | Cầu thang sắt giữa vườn, đèn dây bóng tròn, dãy nhà chữ A trên cột, đá tảng | Toàn thân → trung; 3 cú | Đứng trên bậc, tay vịn lan can, vẫy, đưa tay "trình bày" | Ô ảnh góc; ô vàng "CHỈ VÀI TẤM ẢNH"; ô xanh "AGENT TỰ NHẬN RA" |
| 11,2–17,6 | Hiên gỗ trước nhà chữ A cửa mở, ghế sắt, đèn mây | Trung ngồi bắt chéo chân → cận | Chỉ tay lên đèn mây, tay đặt ngực | Ô ảnh góc; ô xanh "AGENT TỰ VIẾT LỜI GIỚI THIỆU" |
| 17,6–24,3 | Phòng ngủ gỗ trong nhà chữ A: giường trắng, máy lạnh, gương bầu dục, tranh treo, mũ cói trên giường | Ngồi mép giường trung → cận | Hai tay diễn giải, nghiêng đầu | Ô ảnh góc (phải trên); ô đỏ "BAO ĂN, BAO Ở, CHỜ LỊCH" |
| 24,3–31,3 | Ban công lan can trắng, đèn dây, võng, mái tôn xanh nhà chữ A | Trung, đi vào rồi tựa lan can | Hai tay ngửa "lấy đâu ra thời gian" | Ô vàng "KHÔNG CÓ THỜI GIAN QUAY" |
| 31,3–37,8 | Đỉnh đồi nhìn xuống vịnh biển xanh, đảo, tàu | Trung → cận | Hai tay làm khung "chụp ảnh" | Ô ảnh góc; ô vàng "CHỈ CẦN CHỤP ẢNH"; ô xanh "NGƯỜI MẪU ẢO" |
| 37,8–44,6 | Sàn gỗ ngắm hoàng hôn, trời hồng cam, biển | Trung | Ôm trái dừa có ống hút, chỉ tay ra biển, xòe tay | Ô ảnh góc; ô vàng "TUẦN NÀO CŨNG CÓ VIDEO MỚI" |
| 44,6–51,3 | Quay lại cửa nhà chữ A 07, cửa mở | Toàn thân → cận | Giơ ngón tay "một buổi", xòe tay mời | Ô vàng "HỌC 1 BUỔI LÀ LÀM ĐƯỢC"; thẻ kết |

Quy luật dựng:
- **Mỗi bối cảnh 5–7 giây, 1–3 cú.** Đổi bối cảnh đúng chỗ đổi câu/ý. Trong một bối cảnh, cú sau đẩy vào gần hơn (toàn → trung → cận), như người quay cầm điện thoại bước lại gần.
- **Cảnh đi theo lời:** nói "đèn mây, sàn gỗ" thì đang ở hiên có đèn mây; nói "mời người nổi tiếng... bao ăn bao ở" thì ở phòng ngủ; nói "chụp mấy tấm ảnh" thì ở chỗ view đẹp nhất; nói "cảnh hoàng hôn" thì đang hoàng hôn.
- **Mở và kết cùng một chỗ** (cửa nhà chữ A) → vòng tròn, nhận diện khu.
- Máy cầm tay, rung nhẹ, ngang mắt hoặc thấp hơn một chút; không có cảnh flycam, không có cảnh vắng người (trừ 0,9 giây ảnh chủ khu).

## 4. Lời (đã sửa chữ Whisper nghe sai theo phụ đề trên hình)

| Giây | Lời | Phần |
|---|---|---|
| 1,0–4,4 | Anh chị làm du lịch ơi, căn nhà chữ A này em chưa đến bao giờ đâu nhá. | Móc câu: gọi đúng người + điều bất ngờ |
| 5,0–11,0 | Chủ khu chỉ gửi em mấy tấm ảnh thôi. Em đưa cho agent xem, nó nhận ra ngay đây là chỗ nghỉ trên đồi nhìn ra biển. | Chứng minh |
| 11,4–17,2 | Đến cái đèn mây với sàn gỗ ngoài hiên này nó cũng để ý đấy, rồi nó tự viết lời giới thiệu hợp với chỗ này luôn. | Chứng minh (chi tiết) |
| 17,7–23,8 | Em ngồi đây cho khách dễ hình dung. Mời người nổi tiếng về quay thật thì anh chị phải bao ăn bao ở, còn phải chờ lịch nữa. | Nỗi đau 1: thuê KOL |
| 24,5–30,9 | Mà anh chị lo khách lo phòng cả ngày rồi, lấy đâu ra thời gian tự quay tự dựng video đều đều được cơ chứ? | Nỗi đau 2: không có thời gian |
| 31,4–37,4 | Giờ anh chị chỉ cần chụp mấy tấm ảnh thôi. Agent lo phần kịch bản, rồi đưa người mẫu ảo như em vào đi lại, nói chuyện như khách thật đấy. | Giải pháp |
| 37,9–44,5 | Chỗ nào đẹp thì anh chị cứ chụp gửi agent nhá. Hôm nay làm cảnh hoàng hôn, rồi mai làm phòng ngủ, tuần nào cũng có video mới để đăng. | Lợi ích đều đặn |
| 44,5–51,0 | Học một buổi, cài đặt xong là làm được. Chỉ cần ra lệnh là agent làm hộ phần còn lại. Đăng ký ở link bên dưới nhá. | Kêu gọi |

Cấu trúc: **móc câu (4 giây) → chứng minh (13 giây) → nỗi đau (13 giây) → giải pháp + lợi ích (13 giây) → kêu gọi (6 giây)**. 213 chữ.

## 5. Cách nói — vì sao nghe tự nhiên

- **Tốc độ trung bình 4,6 chữ/giây**, nhưng **dao động 3,9–6,2**: câu kể chậm lại (3,9 ở "mà anh chị lo khách lo phòng"), câu liệt kê/lợi ích nhanh lên (6,2 ở "giờ anh chị chỉ cần..."). Không đều như máy đọc.
- **Câu ngắn 5–18 chữ, ngắt hơi 0,3–0,6 giây giữa câu**, có chỗ nối liền không ngắt (13,6 → 16,0). Không có khoảng lặng dài quá 0,7 giây.
- **Từ đệm khẩu ngữ miền Bắc đặt cuối câu:** "nhá", "đâu nhá", "thôi", "đấy", "luôn", "cơ chứ", "nữa". Gần như câu nào cũng có một chữ đệm → nghe như đang nói chuyện, không phải đọc quảng cáo.
- **Xưng "em", gọi "anh chị"**, gọi agent là "nó" (thân mật, như kể chuyện người thứ ba).
- **Câu hỏi tu từ** ("lấy đâu ra thời gian... được cơ chứ?") lên giọng cuối.
- **Tự nhận là người mẫu ảo** ngay trong lời ("người mẫu ảo như em") → minh bạch, không lừa người xem.
- **Cảm xúc theo phần:** móc câu hào hứng, ngạc nhiên; chứng minh kể chuyện vui; nỗi đau đồng cảm, nhăn nhẹ, hai tay ngửa; giải pháp tự tin; kết thân thiện. Mặt luôn cười, mắt nhìn máy.
- **Động tác tay khớp chữ:** vẫy khi chào; chỉ lên khi nói "đèn mây"; đặt tay lên ngực "nó tự viết"; hai tay ngửa "lấy đâu ra"; hai tay làm khung ảnh "chụp"; chỉ ra biển "chỗ nào đẹp"; giơ một ngón "một buổi"; xòe tay mời ở câu kết.

## 6. Trang phục, trang điểm, ngoại hình KOL mẫu

- **Áo hai dây lụa satin màu kem** cổ chữ V, **sơ mi linen trắng rộng khoác ngoài, mở cúc, trễ một bên vai**, **chân váy linen màu be dài quá gối, xẻ tà bên**, **kính râm gọng nâu cài trên đầu**. Đạo cụ: mũ cói rộng vành (cầm tay hoặc đặt trên giường), trái dừa có ống hút ở cảnh hoàng hôn. Một bộ đồ cho cả video (khách nhìn thấy cùng một người đi một chuyến).
- Bảng màu: kem – trắng – be, hòa với gỗ nâu đỏ và biển xanh; KOL nổi bật nhưng không lấn bối cảnh.
- Tóc nâu dài quá ngực, uốn sóng lớn, mái thưa. Trang điểm kiểu Hàn: da căng bóng nhẹ, má hồng, môi hồng cam bóng, mắt kẻ nhẹ.
- **Lỗi của mẫu (mình phải làm tốt hơn):** mặt KOL đổi rõ giữa các bối cảnh (giây 1,2 mặt tròn mắt to; 4,2 mặt dài hơn, mũi khác; 15,5 mặt khác hẳn; 47 lại khác). Hình xăm chữ ở ngực lúc có lúc không. → Đây đúng là điều anh dặn "mặt không được lệch": skill có cổng khóa mặt từng cảnh.

## 7. Chữ trên hình

| Lớp | Kiểu | Vị trí | Lúc nào |
|---|---|---|---|
| Nhãn "Video do AI tạo ra" | Ô đen bo tròn, chữ trắng đậm nhỏ (~26 px ở 1080) | Góc trên trái (x≈20, y≈30) | Suốt video |
| Nhãn "Người mẫu ảo do AI tạo ra" | Ô xanh ngọc (#16967f) chữ trắng đậm | Ngay trên phụ đề | Giây 1–2 (lần đầu KOL xuất hiện) |
| Phụ đề | Chữ trắng đậm rất dày, viền đen mỏng + bóng; **2–4 chữ một lần**; **1 từ khóa tô vàng (#FFE14A)** | Giữa ngang, khoảng 58–62% chiều cao | Suốt video, đổi theo từng cụm |
| Thẻ nhấn ý | Ô màu, chữ HOA đậm, nghiêng 2–4°: vàng (#FFE14A chữ đen) cho lợi ích, đỏ (#E0213F chữ trắng) cho nỗi đau/bất ngờ, xanh ngọc (#16967f chữ trắng) cho "agent làm gì" | Ngay trên phụ đề | 1–2 giây, khoảng 1 thẻ mỗi bối cảnh, tổng 10 lần |
| Ô ảnh góc "Ảnh chủ khu gửi" | Ảnh nhỏ ~145×110 px viền trắng dày kiểu ảnh lấy liền, chú thích chữ đen nhỏ ở dưới | Góc trên trái, dưới nhãn AI (phòng ngủ: góc trên phải để né máy lạnh) | 1,5–2 giây đầu mỗi bối cảnh mới (6 lần) |
| Mở đầu "Ảnh chủ khu gửi" | Ảnh chủ khu giữa khung, trên dưới là ảnh đó phóng to làm mờ; ô vàng chữ đen | Giữa trên | 0–0,9 giây |
| Thẻ kết | Ô xanh ngọc bo góc, dòng 1 chữ HOA trắng đậm "KHÓA HỌC LÀM VIDEO BẰNG AI AGENT", dòng 2 chữ vàng nhỏ "Đăng kí ở link bên dưới", tam giác vàng chỉ xuống | Ngang ngực, ~57% chiều cao | 2 giây cuối |

## 8. Âm thanh

- Giọng nữ trẻ miền Bắc, rõ, hơi nũng nịu thân thiện (không phải giọng livestream chốt đơn).
- **Có nhạc nền chạy suốt**, nhẹ, vui: ở khoảng lặng giữa câu đo được −14 đến −21 dB, tức nhạc thấp hơn giọng khoảng 8–10 dB. Không nghe tiếng ồn hiện trường rõ.
- Cả bài −14 LUFS (chuẩn mạng xã hội).

## 9. Bài học đưa vào skill

1. Lời theo khuôn 5 phần, ~210 chữ cho ~50 giây, mỗi câu có chữ đệm khẩu ngữ, tốc độ dao động.
2. 7 bối cảnh + quay lại chỗ đầu; mỗi bối cảnh 1 clip nói ~7 giây, cắt 2–3 cú đẩy vào.
3. Hình khớp lời: lập bảng "câu nào – bối cảnh nào – động tác gì" trước khi tạo clip.
4. Một bộ đồ kiểu nghỉ dưỡng màu kem – trắng – be cho cả video; đạo cụ theo bối cảnh (mũ cói, trái dừa).
5. Chữ trên hình 6 lớp như bảng mục 7; nhãn AI bắt buộc.
6. Nhạc nền nhẹ dưới giọng 8–10 dB, −14 LUFS.
7. Mặt KOL phải đồng nhất hơn mẫu: cổng khóa mặt từng cảnh + người dùng duyệt mặt.
