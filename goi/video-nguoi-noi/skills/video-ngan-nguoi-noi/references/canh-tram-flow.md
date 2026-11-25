# Cảnh trám trên Google Flow

## Đối chiếu kho rồi nhắc người dùng

Sau khi kịch bản được duyệt, đọc `danh-muc-canh.csv` (cột `ma, dung, bo_cuc, nhom, file, ghi_chu`), chỉ lấy cảnh có `dung` = `co`. Mỗi cảnh trong bảng kịch bản hình gán một mã. Thiếu thì nhắc đúng mẫu:

```
Kịch bản cần N cảnh, kho có sẵn X, cần tạo thêm Y (Y × 12 = Z credit):
| Mã mới | Dùng ở câu | Mô tả | Có mặt người dẫn |
Prompt từng cảnh:
<mã>: <prompt đủ để dán>
Sau khi tạo: tải về <thư mục kho>, thêm dòng vào danh-muc-canh.csv.
```

Kho đủ thì nói rõ "kho hiện có là đủ, không cần tạo thêm". Clip không được gán trước thì `lap_canh.py` sẽ dừng và liệt kê mã thiếu.

Ưu tiên tái sử dụng kho. Mỗi clip tốn credit, nên chỉ tạo mới khi cảnh đó thật sự mang nội dung. Chưa có credit thì chuyển sang mô hình đồ họa.

## Cấu hình đã kiểm chứng

| | Video | Ảnh |
|---|---|---|
| Chế độ | Ingredients | Image |
| Mô hình | Omni 1.1 Flash | Nano Banana 2.1 |
| Tỉ lệ | 9:16 | 9:16 |
| Khác | 720p, 8 giây, x1 | x1 |
| Chi phí khi kiểm (11/2026) | 12 credit/clip | 0 credit |

Giá có thể đổi: đọc số trên màn hình trước khi gửi.

## Prompt

**Cảnh có mặt người dẫn**, gắn avatar của kênh:

```text
The man from the reference images, same face, same hairstyle, wearing [TRANG PHỤC]. [MÔ TẢ CẢNH]. Natural candid movement, not looking at the camera, not speaking, mouth closed. Photorealistic, shot on a modern cinema camera, soft natural light, warm tones with subtle orange accents, shallow depth of field, slow subtle camera movement. Vertical 9:16 composition. Any screen is seen from behind or too blurred to read. No text, no captions, no logos, no brand marks, no watermark, no extra fingers, no distorted hands, no extra people in focus.
```

Thêm bố cục:
- Để đặt thẻ ở trên: `Composition: medium shot, the top of his head sits at the vertical center of the frame, upper half of the frame is a clean uncluttered softly blurred background, his body fills the lower half.`
- Toàn màn: `Composition: he fills the frame naturally, balanced vertical framing with some headroom.`

Laptop dễ hiện logo: đặt máy ở góc ngang để không thấy nắp, chỉ cấm trong prompt là chưa đủ.

**Cảnh không người**, không gắn avatar:

```text
[MÔ TẢ CẢNH]. Vertical 9:16, cinematic, photorealistic high-end 3D render, very dark background with orange and teal glow, shallow depth of field, slow smooth camera movement, main subject in the middle, no people, no faces, no readable text, no letters, no numbers, no logos, no watermark, no music.
```

## Khi Claude thao tác Flow giúp

Chỉ làm khi người dùng đồng ý số credit. Không nhập mật khẩu, người dùng tự đăng nhập.

- Tạo project mới cho mỗi đợt. Làm 1 đến 2 cảnh mẫu để duyệt, đạt mới làm hàng loạt.
- Gắn avatar mỗi lần vì nó bị gỡ sau khi tạo: `+` → **Avatars** → tên avatar. Luôn bấm mục Avatars, bộ lọc có thể tự về All và chọn nhầm video mới nhất. Soát ảnh gắn kèm là mặt tròn có huy hiệu avatar.
- Bấm vào khung nhập theo toạ độ, không theo ref. Gõ prompt rồi bấm mũi tên gửi, Enter có lúc không gửi. Xác nhận ô nhập đã trống.
- Chờ ít nhất 8 giây giữa hai lần gửi. Gửi nhanh hơn thì lệnh sau mất mà không báo lỗi, chữ có thể lẫn vào prompt trước.
- Sau lô: đếm đủ số clip, tìm chữ "Failed", xem lưới khung đầu. Clip kiểm bằng cách di chuột để tự phát, không kéo timeline vì tab dễ đơ.
- Chụp màn hình lỗi quá thời gian là chuyện thường trên tab nặng: chụp lại vài lần, đọc trạng thái bằng JavaScript, hoặc mở project trong tab mới.
- Người dùng tự tải clip, trừ khi họ yêu cầu Claude tải.
- Claude tải giúp chỉ chạy được khi trình duyệt đã tắt "Hỏi nơi lưu trước khi tải". Đang bật thì nút tải mở hộp thoại Save As, Claude không bấm được. Nhờ người dùng tắt trong cài đặt trình duyệt, Claude không tự đổi. Không lấy đường link ảnh có chữ ký bằng cách khác.
