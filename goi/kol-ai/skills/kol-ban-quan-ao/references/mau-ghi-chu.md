# Mẫu `nguon.md` (mỗi video một tệp)

Để người duyệt biết từng câu trong lời lấy từ đâu. Lời chỉ được nói những gì có ở mục "Được nói". `viet_lenh.py video` đọc cột đầu của bảng này làm cổng nguồn: giữ đúng tiêu đề `## Được nói` và bảng hai cột; ghi cụm cụ thể, không ghi cụm chung như "đều xinh", và không ghi vào bảng các chữ đã có trong câu kéo khách (ví dụ ghi "chuẩn cho từng người", không ghi "size chuẩn cho từng người luôn"), vì cụm dài sẽ nuốt chữ của câu kéo khách và bị chặn nhầm.

```markdown
# <Tên sản phẩm, màu chọn>

- Link: <link trang bán>
- Nhà bán: <tên>
- Giá thấy ngày <dd/MM>: <giá>
- Đã bán: <đúng số trên trang>
- Màu đang bán: <liệt kê theo nút chọn, không theo mô tả>
- Size: <bảng size, cân nặng gợi ý>

## Được nói
| Ý trong lời | Nguồn |
|---|---|
| <cụm cụ thể đúng như sẽ nói, ví dụ: cổ cao ba phân> | <tên sản phẩm / ảnh mô tả / lời khách> |
| <mười nghìn đơn> | <số "Đã bán 10k+"> |

## Không nói
- <chỗ nhà bán ghi mâu thuẫn, ví dụ thành phần sợi>
- <ý không có nguồn>

AI vẽ khác hàng thật: <ví dụ: logo, mặt sau áo>
Quyền dùng ảnh nhà bán: <chưa xin / đã có>
```
