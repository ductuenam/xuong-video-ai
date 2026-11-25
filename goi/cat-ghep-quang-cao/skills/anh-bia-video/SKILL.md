---
name: anh-bia-video
description: Làm ảnh bìa dọc 9:16 cho video ngắn theo công thức nền đen, ánh cam, tiêu đề lớn hai dòng, nhãn nghiêng, biểu tượng 3D phát sáng và mặt người dẫn nhìn lên. Hình do AI tạo không có chữ, chữ ghép bằng code nên luôn đúng dấu tiếng Việt. Dùng ngay khi người dùng muốn làm ảnh bìa, thumbnail, cover cho video ngắn, đổi chữ trên bìa, hoặc video vừa dựng xong cần bìa, kể cả khi không nói chữ "skill".
---

# Ảnh bìa video

Bìa gồm 2 lớp: **hình** tạo bằng Nano Banana qua API, **chữ** ghép bằng composition `AnhBia` của bộ `video-ngan-nguoi-noi`. Không để AI vẽ chữ vì sẽ sai dấu.

## Công thức

| Lớp | Vị trí | Quy tắc |
|---|---|---|
| Dòng 1, chữ trắng | Trên cùng | Vế gây tò mò, tối đa khoảng 14 ký tự một dòng để đủ to |
| Dòng 2, chữ cam | Ngay dưới | Vế xung đột hoặc lợi ích |
| Nhãn cam nghiêng | Dưới hai dòng | Câu hỏi mồi ngắn, không bắt buộc |
| Biểu tượng 3D phát sáng | Giữa khung | Hợp chủ đề, không dùng logo hãng |
| Mặt người dẫn | Dưới, 40% khung | Biểu cảm mạnh, nhìn lên biểu tượng |
| Mũi tên trắng cong | Chỉ vào biểu tượng | Không bắt buộc |
| Nhãn kênh | Góc dưới phải | Tự có |

Nền đen, chỉ một màu nhấn là cam. Cùng ý với móc câu video nhưng ngắn hơn: 3 đến 7 từ mỗi dòng.

## Các bước

1. **Chọn chữ.** Đề xuất 3 cách, chọn 1 tốt nhất theo tiêu đề video. Kiểm từ cấm trong `ho-so-kenh.json` của kênh.
2. **Tạo hình qua API.** Lấy prompt ở skill chân dung của kênh (tên ở trường `chanDung`), hoặc `references/tao-hinh.md`. Tạo 2 ảnh rồi chọn. Script tự gắn ảnh trong `anhThamChieu` của hồ sơ:

```bash
python tao_anh.py "<dự án>" --prompt "<prompt>" --ra public/bia-nen --so 2
```

   Tốn tiền thật, khoảng 900 đồng một ảnh: không tạo hàng loạt khi chưa cần. Mã thoát 1 là API từ chối hoặc không trả ảnh, xem lý do được in ra. Không có API thì làm tay trên Flow theo `references/tao-hinh.md`, tải bản 2K, không dùng ảnh chụp màn hình cho bản giao vì bị mềm.

3. **Soát hình:** đúng mặt, không biến dạng, biểu tượng hợp chủ đề.

4. **Ghi `bia.json`** trong thư mục dự án:

```json
{"anh": "bia-nen.png", "dong1": "AI làm video", "dong2": "giỏi hơn bạn?", "nhan": "Cái giá là gì?", "coChu": 112,
 "muiTen": {"tuX": 215, "tuY": 1240, "congX": 110, "congY": 860, "denX": 368, "denY": 800}}
```

   Ảnh để trong `public/` của dự án. `nhan`, `muiTen`, `coChu` có thể bỏ. `dayNen` đẩy hình xuống khi biểu tượng sát chữ, phần trống ở trên là nền đen.

5. **Xuất:**

```bash
python lap_bia.py "<thư mục dự án>"
```

   Script ở `scripts/` của skill này, ra `render/bia.jpg`.

6. **Soát bằng mắt** trước khi giao:
   - Chữ không tràn và không đè mặt, đúng dấu.
   - Mũi tên chỉ đúng biểu tượng, không cắt ngang mặt.
   - Mặt rõ, đúng người, không biến dạng.
      - Thu nhỏ còn khoảng 200 pixel chiều rộng vẫn đọc được chữ.

   Lỗi thì tự sửa: chữ tràn thì giảm `coChu`, mũi tên lệch thì chỉnh toạ độ. Hình xấu thì tạo lại. Chỉnh chữ không tốn gì, nên thử nhiều lần được.

## Lưu ý

- Dòng ghi chú dưới tên kênh lấy từ `nhanAnhAI` trong hồ sơ, để trống thì không hiện. Không dùng bìa để giả làm ảnh chụp sự việc có thật.
- Không dùng logo, ảnh, tên thương hiệu của người khác kiểu như họ đang bảo trợ. Tiêu đề không hứa kết quả chắc chắn.
- Tên tệp giao: `<số>-<tên>-bia.jpg`, để chung thư mục với video.
