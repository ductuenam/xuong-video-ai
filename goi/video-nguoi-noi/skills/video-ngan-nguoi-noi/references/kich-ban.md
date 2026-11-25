# Viết kịch bản

## 1. Bóc video mẫu (khi có)

Dùng video mẫu để học cấu trúc, không chép lời, tên kênh, linh vật hay bộ màu y hệt.

Ghi lại: thời lượng, số cảnh và nhịp cắt, cấu trúc thông điệp theo giây, cách minh họa, điều đáng học.

Lấy lời bằng `whisper_vi.nghe`, lấy khung hình bằng FFmpeg. Không kết luận về thứ chưa nghe hoặc chưa xem được.

## 2. Kiểm nguồn trước khi viết

Mỗi con số hay khẳng định trong lời phải có dòng trong bảng nguồn. Đọc tài liệu gốc của công cụ, không tin video mẫu.

Bảng bắt buộc trong `kich-ban.md` của dự án:

| Thông tin trong lời | Nguồn | Trạng thái |
|---|---|---|
| ... | Liên kết, mục cụ thể | Đã đọc ngày..., có cần xem lại trước khi đăng không |

Video mẫu nói khác nguồn thì lập bảng "Video mẫu nói / Kiểm lại / Xử lý". Không có nguồn thì bỏ. Chưa chắc thì nói đúng mức nguồn ghi, ví dụ "README ghi có người gặp", không kết luận vi phạm hay an toàn thay nguồn.

## 3. Nguồn hình cho phần mềm được nói tới

Không cài phần mềm lên máy chỉ để làm video. Người nhận bàn giao không có máy mạnh vẫn phải làm được. Chọn theo thứ tự:

1. **Hình thật của trang công khai:** GitHub, tài liệu, bảng giá. Dùng `scripts/chup_web.py` rồi mô hình `man-web`, khoanh đúng chỗ đang nói, ghi nguồn và ngày chụp.
2. **Công cụ dùng được trên web:** thao tác thật rồi quay, bằng `chup_web.py --quay` với trang công khai. Trang phải đăng nhập thì người dùng tự đăng nhập; soát và che tên tài khoản, nội dung riêng.
3. **Mô hình đồ họa minh họa:** cho khái niệm và phần không có hình thật. Không vẽ giả giao diện để người xem tưởng là thật.

**Hệ quả với lời:** chưa dùng thật thì không nói như đã dùng. Viết "tài liệu ghi", "theo trang của họ". Không viết "mình thử thấy", "chạy rất mượt", "ai cũng vấp". Chính video mẫu chỉ được nói điều nguồn xác nhận.

## 4. Chọn khuôn

### Khuôn A: Giải một nỗi đau (mẫu: video MarkItDown, khoảng 70 giây)

| Nhịp | Việc phải làm được |
|---|---|
| Nỗi đau | Gọi đúng tình huống khó chịu người xem đang gặp |
| Giải pháp | Trấn an, rồi nêu tên công cụ |
| Lợi ích | Chỉ đúng chỗ, nói nó cho biết gì |
| Kết quả | Cảm giác sau khi dùng, so sánh trước và sau |
| Cách làm | Các bước ngắn, làm theo được ngay |
| Lưu ý | Giới hạn và phương án thay thế, tạo độ tin cậy |
| Kết | Rủ thử, câu hỏi thật, chỉ về bình luận ghim, tên kênh |

### Khuôn B: Review có quan điểm (mẫu: video FlowKit, khoảng 2 phút)

| Nhịp | Việc phải làm được |
|---|---|
| Mở | Câu gây chú ý lấy từ chính công cụ, cộng số liệu thật |
| Nó làm gì | Một màn dây chuyền |
| Điểm khó nó giải | Kèm trải nghiệm thật của kênh, thứ video mẫu không có |
| Cách làm lạ | Sơ đồ nhiều lớp |
| Tin vui, tin buồn | Hai mặt rõ ràng |
| Rủi ro | Lấy từ tài liệu của chính công cụ, không suy đoán |
| Lập trường | Nói thẳng nên dùng hay không |
| Câu hỏi chia phe | Cho người xem lý do bình luận |

### Khuôn C: Giải thích một khái niệm (mẫu: video Skill, khoảng 1 phút)

| Nhịp | Việc phải làm được |
|---|---|
| Mở | Tình huống người xem đang gặp, không hỏi định nghĩa suông |
| Ví von | Một hình ảnh đời thường duy nhất, dùng xuyên suốt |
| Nó gồm gì | Mở hình ví von ra thành thứ cụ thể |
| So với thứ dễ nhầm | Hai vế ngắn |
| Thật sự là gì | Hình thật từ tài liệu gốc |
| Lưu ý | Rủi ro từ tài liệu |
| Kết | Câu hỏi khiến người xem kể chuyện của họ |

### Khuôn D: Mổ xẻ cơ chế, có chương (mẫu: 23-skill-ben-trong, khoảng 90 đến 100 giây)

Dùng khi giải thích một thứ chạy bên trong ra sao, hoặc khi video mẫu đã chia chương. Không rút gọn thành bản lướt khoảng 40 giây: người dẫn chê bản 40 giây của video 23 "chưa hấp dẫn bằng video mẫu", bản mẫu phân tích chi tiết hơn và có cấu trúc.

| Nhịp | Việc phải làm được |
|---|---|
| Mở | Nỗi đau cụ thể ("cài cả chục skill mà không được gọi"), hứa sửa được, báo trước số phần |
| Mục lục | Một cảnh liệt kê các phần (`danh-sach-buoc`) |
| Mỗi phần | Thẻ chương trên clip có mặt (`flow-chu` "PHẦN 1" và câu hỏi của phần), rồi 2 đến 3 cảnh đồ họa, mỗi câu một hình |
| Cấu tạo | Hình thật của vật được nói: cây thư mục (`cay-thu-muc`), file mở ra soi từng vùng (`tep-ma`) |
| Cơ chế | Các mức hoặc các bước sáng dần, rồi một ảnh chụp tài liệu gốc làm bằng chứng |
| Ví dụ chạy thật | Một ví dụ gần nghề người xem, đi từ yêu cầu tới kết quả, cảnh có chữ "Minh họa" |
| Hay hiểu sai | 2 đến 3 điều, mỗi điều một hình (`truoc-sau`, `hai-phe`, ảnh tài liệu) |
| Kết | Câu hỏi thật, chỉ về bình luận ghim |

Phải hay hơn mẫu ở ít nhất hai điểm: ví dụ gần người xem hơn, thêm phần dễ nhầm mà mẫu bỏ qua, và mọi ý có nguồn gốc.

Chủ đề không hợp các khuôn trên thì lập khuôn mới theo cùng cách, ghi lại vào file này sau khi video được duyệt.

## 5. Quy tắc viết lời

**Độ dài theo nội dung, không mặc định 1 phút.** Danh sách hoặc review nhiều công cụ: 1 phút 30 đến 2 phút 30. Một công cụ, một khái niệm: 45 đến 75 giây. Rút nhiều so với video mẫu thì báo người dùng phần bị bỏ. Có video cùng chủ đề hai độ dài thì ghi vào content để đăng thử, so tỉ lệ xem hết, thời gian xem, lượt lưu.

**Kiểm từng công cụ được kể tên.** Video danh sách: mỗi công cụ phải có trang chính thức hoặc kho mã xác nhận; không xác minh được thì bỏ khỏi lời.

- Xưng hô theo hồ sơ kênh. Câu ngắn, viết để nói, đọc to phải trôi.
- Câu đầu phải khiến người xem dừng lại, không chào hỏi.
- Có trải nghiệm thật của người dẫn thì đưa vào, không có thì không dựng chuyện. Câu khẳng định về người dẫn thì đánh dấu để họ xác nhận.
- Mỗi màn một luận điểm làm tiêu đề, ví dụ "Khó nhất không phải là đẹp".
- Không dùng từ trong `tuCam` của hồ sơ. Không rủ người xem làm việc có thể gây hại tài khoản của họ, nêu rõ điểm mình chủ động đổi so với mẫu.
- Ghi cách đọc tên tiếng Anh khó đọc.
- **Giọng AI nói liền hơi như người thật.** Đo người thật (video mẫu 12.prompt): một hơi khoảng 2,9 giây, nghỉ khoảng 0,22 giây. Viết kiểu cũ (câu ngắn, nhiều dấu phẩy, chèn `<#0.3#>` sau mỗi câu) chỉ đạt khoảng 1 giây một hơi, nghe rời rạc giọng máy. Cách viết:
  - `loi.txt` vẫn chia cụm ngắn cho phụ đề; bản đọc `doc-tts.txt` gộp cả đoạn ý thành một dòng, chỉ xuống dòng ở 1 đến 2 chỗ chuyển ý lớn, không dùng `<#...#>`.
  - **Giữ dấu phẩy ở chỗ chuyển ý** ("Vào trang là có ô tìm, cần việc gì thì gõ việc đó") để người nghe kịp hiểu thao tác. Chỉ bỏ dấu phẩy thừa và dấu phẩy sau `Ây‑Ai`. Bỏ hết dấu phẩy thì nghe liền quá, nhanh, khó hiểu (người dùng chê khi thử 08/11/2026).
  - Sau khi tạo giọng, chạy `nghi_dau_phay.py` để chèn nghỉ khoảng 0,15 giây vào những dấu phẩy máy đọc dính, 0,25 giây ở dấu chấm.
  - Nối ý bằng từ người thật hay dùng: "mà", "thì", "là", "nghĩa là", "chứ không phải ... đâu", "luôn", "này", "đó", "nha", "rồi".
  - Đo bằng `python do_nhip.py <file giọng>`: mỗi hơi nên từ 1,6 đến 2,0 giây. Dưới 1,6 là rời rạc, trên 2,0 là thiếu chỗ ngắt.
  - Tránh câu liệt kê nhiều vế ngắn có dấu phẩy ("từng khung hình, từng nốt nhạc") và vế mở đầu dưới 4 chữ có dấu phẩy ("Cài cũng nhẹ, gõ...", "Anh chị chọn phong cách, đưa..."): máy ngắt thành hơi 0,5 đến 0,8 giây. Nối bằng "rồi", "vì", "và" thành một vế. Video 16 sửa ba câu như vậy, nhịp lên từ 1,58 thành 1,79 giây.
  - Tránh chữ đọc gần giống số ngay sau một con số ("113 từ sáo" nghe thành "113 từ sáu"): đổi từ khác.
- Giọng AI: cảm xúc đến từ câu chữ. Thêm vừa phải thán từ, dấu chấm than, câu hỏi tu từ ở móc câu, chỗ bất ngờ và câu kết ("ơ, chỗ cũ lại hỏng!", "Thấy chưa, ..."); phần giải thích giữ giọng đều.

## 6. Câu kết (bắt buộc)

Kết đủ hai nhịp (đổi 16/11/2026):

1. **Câu hỏi thật** gắn với việc của người xem, để họ có chuyện kể và bình luận tự nhiên.
2. **Chỉ về bình luận ghim:** hướng dẫn hoặc tài liệu để sẵn ở bình luận ghim.

Ví dụ: "Anh chị đang làm giao diện cho ngành gì? Hướng dẫn cài từng bước mình để sẵn ở bình luận ghim nhé!"

**Cấm** xin bình luận một chữ để đổi tài liệu: không "Comment CÀI, mình gửi...", không "bình luận chữ ... để nhận", không "inbox nhận...". Lý do: Meta coi là kéo tương tác (engagement bait) và giảm phân phối, YouTube cấm đổi phần thưởng lấy tương tác; dùng lặp ở mọi video càng dễ bị phạt. `kiem_chot.py` chặn "comment" đi kèm "gửi"/"nhận" hoặc kèm một từ khóa viết hoa, trong bản đọc lẫn `loi.txt`.

Trên hình dùng `ket-comment` (tên loại cảnh giữ nguyên): `tieuDe` là câu hỏi, khung cam tự hiện "XEM BÌNH LUẬN GHIM" (đổi chữ bằng `tuKhoa` nếu cần, không ghi chữ COMMENT). Có hướng dẫn thì làm tờ PDF và soạn bình luận ghim theo `content-dang.md`. Video không có gì để cài thì để tài liệu đúng chủ đề ở bình luận ghim, không kết bằng câu hỏi suông.

## 7. Sản phẩm của bước này

Trong thư mục dự án:

- `kich-ban.md`: tiêu đề đề xuất (3 cái, chọn 1), cách video mẫu làm và kênh làm khác gì, bảng kịch bản hình, bảng nguồn, những điểm chủ động đổi, chú ý khi quay.
- `loi-thoai.txt`: lời đọc thuần, mỗi câu một dòng.

Bảng kịch bản hình:

| # | Lời | Hình | Mô hình hoặc cảnh | Quay |
|---|---|---|---|---|
| 1 | ... | ... | `nguoi-chu` | Nhìn camera |
| 2 | ... | ... | `day-chuyen` | Chỉ lấy giọng |

Người dẫn nhìn camera ở đầu và cuối; đoạn giữa chỉ lấy giọng và có thể đọc theo chữ. Tỉ lệ đoạn giữa dùng đồ họa và cảnh AI càng nhiều thì càng đỡ phải quay lại.

Lời dùng được mô hình có sẵn thì dùng lại. Cần mô hình mới thì báo sớm.

## 8. Chuẩn quay (gửi người dẫn)

- Quay dọc 9:16 bằng điện thoại, tối thiểu 1080p, ánh sáng trước mặt, phòng yên.
- Mặt ở khoảng giữa khung, chừa khoảng trần trống trên đầu để đặt chữ. Đoạn nhìn camera giữ nguyên bối cảnh.
- Nói sai thì dừng một nhịp rồi nói lại cả câu.
- **Gửi file gốc.** Qua Zalo hoặc Messenger sẽ bị nén, kiểm tra độ phân giải khi nhận: dưới 1080p thì báo người dùng trước khi dựng.
