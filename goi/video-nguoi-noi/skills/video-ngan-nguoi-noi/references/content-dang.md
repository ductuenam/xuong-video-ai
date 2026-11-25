# Content đăng kèm video

Viết sau khi video đạt nghiệm thu, từ lời đã nói thật, không từ kịch bản dự kiến. Lưu `<số>-<tên>-content.md`.

## Cấu trúc file

```markdown
# <Tiêu đề đã chọn>

## Facebook Reels
<bài đăng>

## TikTok
<bài ngắn>

## YouTube Shorts
Tiêu đề: <dưới 100 ký tự>
Mô tả: <2 đến 3 câu và nguồn>

## Bình luận ghim
<1 câu>

## Nguồn
- <liên kết>: <dùng cho ý nào>

## Cần làm trước khi đăng
- <số cần xem lại, câu khẳng định cần người dẫn xác nhận>
- Bật nhãn nội dung AI nếu nền tảng yêu cầu, video có cảnh AI minh họa.
```

## Facebook Reels: 80 đến 150 từ

1. **Câu đầu:** cùng ý với móc câu của video nhưng không chép nguyên tiêu đề. Hiện được trước nút "Xem thêm", nên dưới 15 từ.
2. **Thân:** 3 đến 5 câu, mỗi câu một dòng. Nói ý chính và lập trường của kênh. Người không xem video vẫn hiểu.
3. **Kết:** câu hỏi thật như cuối video, rồi chỉ về bình luận ghim ("Hướng dẫn từng bước mình để ở bình luận ghim nhé"). Không xin bình luận một chữ để đổi tài liệu (xem mục 6 `kich-ban.md`).
4. **Thẻ:** 3 đến 5 thẻ sát chủ đề.

## TikTok: dưới 40 từ

Một câu gợi tò mò, một câu hỏi thật cho người xem, 3 đến 4 thẻ. Không viết "comment/bình luận chữ ... để nhận".

## Luật

- Xưng hô, người xem và câu kêu gọi theo hồ sơ kênh.
- Số liệu phải khớp video và bảng nguồn. Không thêm số mới.
- Quét `tuCam` của hồ sơ kênh, gặp thì đổi.
- Không hứa kết quả. Công cụ có rủi ro thì không chỉ nhắc mặt tốt.
- Câu kêu gọi không được khác video. Video không mời cài thì content cũng không mời cài.
- Viết như người thật nói. Không mở bằng "Bạn có biết".
- Thêm vài biểu tượng cảm xúc đầu câu hoặc đầu đoạn cho dễ nhìn, Facebook khoảng 3 đến 5 cái, TikTok 1 đến 2. Không dùng thay chữ.
- Đọc to một lượt trước khi giao.

## Bình luận ghim

Mỗi video có hướng dẫn hoặc tài liệu thì soạn sẵn bình luận ghim trong content: 1 đến 2 câu nói hướng dẫn gì, kèm chỗ trống `[DÁN LINK HƯỚNG DẪN]` để người dẫn dán link (Drive, web, Zalo). Ví dụ: "📌 Hướng dẫn cài Lightrag từng bước, có ảnh chụp từng màn: [DÁN LINK HƯỚNG DẪN]". Không viết "comment để nhận", "inbox nhận".

## Tờ hướng dẫn (để ở bình luận ghim)

Khi video có hướng dẫn hoặc tài liệu, làm thành PDF có màu theo kênh và có sơ đồ, không gửi file văn bản thuần. Sửa từ `references/mau-to-huong-dan.html`, xuất bằng `scripts/xuat_pdf.py`, mở ảnh xem trước để soát. Ghi rõ nguồn; chưa chạy thử thì ghi là chưa chạy thử.

Mọi tờ đều có khối liên hệ `lien-he` ở trang cuối và số Zalo ở chân trang, lấy từ `lienHe` trong hồ sơ kênh; không ghi tên cá nhân người dẫn. Thiếu thì `xuat_pdf.py` từ chối xuất. Lưu `<số>-<tên>-huong-dan.pdf` cùng thư mục video, ghi vào "Cần làm trước khi đăng" việc đưa tờ này lên Drive hoặc web rồi dán link vào bình luận ghim.

## Ví dụ (video FlowKit)

> Một repo GitHub tuyên bố AI làm video giỏi hơn bạn.
>
> Từ một ý tưởng, FlowKit tự viết truyện, tạo nhân vật, làm clip, lồng tiếng rồi đẩy lên YouTube.
> Nghe rất đã, nhưng nó dựa vào chính tài khoản Google đang mở của anh chị.
> README của nó ghi có người sau khi thử đã bị từ chối tạo video, kể cả khi làm bằng tay.
> Nếu muốn thử, đừng dùng tài khoản chính. Mình cũng chưa dám thử trên tài khoản đang làm kênh này.
>
> Đây là dân chủ hóa thật, hay chuyện thật mà hình máy vẽ? Anh chị đứng phe nào?
>
> #AI #GoogleFlow #VideoAI #FlowKit
