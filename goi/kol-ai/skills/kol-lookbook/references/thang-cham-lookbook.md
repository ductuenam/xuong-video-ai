# Thang chấm video lookbook (lập 21/11/2026)

Ba agent soát độc lập, mỗi agent chấm phần của mình, cộng lại 10 điểm. **ĐẠT khi tổng ≥ 9 VÀ không có lỗi nào loại "CHẶN"**. Lỗi CHẶN là lỗi người xem bình thường thấy ngay ở tốc độ thường; có một lỗi CHẶN là SỬA LẠI dù tổng điểm cao.

| Agent | Phần | Điểm tối đa |
|---|---|---|
| `sku-lb-soi-da-mat` | Da và mặt ở mọi cảnh có mặt, nhất là cận mặt | 3,5 |
| `sku-lb-soi-trang-phuc` | Quần áo, phụ kiện, tay chân, đúng sản phẩm | 4 |
| `sku-lb-cham-dung` | Nhịp cắt, liền mạch giữa cảnh, ảnh sản phẩm góc, chữ, âm thanh, cảm giác quay thật | 2,5 |

## Da và mặt (3,5)
- Da thật: thấy lỗ chân lông, vân da, chút không đều màu; KHÔNG da sáp, nhựa, bóng loáng, mịn như lọc ảnh (1,5).
- Mặt giữ đúng một người qua mọi cảnh, đúng mặt KOL của shop (ảnh `kol/mat-chuan.png`, tờ `khoa-mat/to-mat.jpg`) (1).
- Mắt hai bên cân, chớp cùng lúc, không lé, tròng không méo; răng không dính khối; tai, khuyên tai, tóc mái không đổi (1).
- Chân (trong phần da): chân trần phải trắng sáng, mịn, đều màu như `kol/chan-chuan.png`, đầu gối sáng; quần tất/tất/bốt phải gọn, đúng bộ.
- CHẶN: mặt có nốt ruồi, chấm nâu, tàn nhang đậm thấy được (chủ shop chốt 23/11: da KOL xinh, mịn, trắng sáng, sạch, vẫn thật); mặt đổi người hoặc khác mặt chuẩn (bè, đầy, tròn ra; dài, gầy, cằm nhọn đi; già đi; son đổi màu rõ); mắt méo; da sáp thấy rõ ở cận mặt; khuyên tai/tóc đổi giữa hai khung liền; chân trần đầu gối thâm, da chân đỏ/sẫm/sần thấy rõ ở cảnh cận chân.

## Quần áo, phụ kiện (4)
- Đúng sản phẩm Shopee (màu, kiểu, chi tiết) (1).
- Cùng một bộ qua mọi cảnh của bộ đó: không đổi màu, kiểu, số khuy, túi áo; phụ kiện không mọc/mất (1).
- Vật lý phụ kiện: túi luôn có điểm tựa (tay cầm, quai trên vai/khuỷu); quai nối liền vào túi; buông tay là túi phải rơi/đung đưa theo trọng lực, KHÔNG lơ lửng; mũ nằm trên đầu; khăn quàng nối liền (1).
- Tay chân: đủ năm ngón, không dính, không xuyên vải; giày, tất, gấu quần đúng ở mọi cảnh (1).
- CHẶN: túi/vật lơ lửng; phụ kiện mọc ra hoặc biến mất; đổi tay xách túi giữa hai khung liền; ngón tay thừa/thiếu thấy được; quần áo đổi màu/kiểu.

## Dựng và cảm giác thật (2,5)
- Cắt đúng phách, mỗi cảnh 1,5–2,5 giây (trừ cảnh máy tiến dài), không cắt giữa lúc đang chớp mắt hay giữa động tác dở (0,75).
- Hai cảnh liền nhau cùng bộ khác cỡ khung (toàn thân ↔ trung cảnh ↔ cận) hoặc khớp tư thế; không có "nhảy" cùng cỡ khung (0,5).
- Ảnh sản phẩm ở góc phải (dưới ở cảnh toàn/chân, trên ở cảnh máy tiến — chủ đích, đổi đúng khung cắt, không tính là lỗi) đúng bộ đang mặc, tách nền sạch, không che mặt/sản phẩm/giày/tay; chữ thương hiệu rõ, không sai chính tả — CHỈ chấm chữ khi kế hoạch có `"chu"` (chưa có tên shop thì để trống là đúng, không trừ) (0,5).
- Cảm giác quay thật: rung nhẹ, hạt hình, không khựng, không tua (0,25).
- Âm thanh: nhạc đủ tới cuối, khoảng −14 LUFS, tắt dần (0,5).


Quy ước chấm thêm: video không có túi/phụ kiện thì mục vật lý phụ kiện cho đủ điểm. Mắt: 0,3 giây đầu mỗi cảnh phải mở mắt; một lần nhắm > 0,3 giây giữa cảnh là chớp dài (lỗi nhẹ, trừ 0,1).

## So với video mẫu đã duyệt (bắt buộc)
Mỗi người chấm đặt video mới cạnh video mẫu đã duyệt: `~/.claude/skills/kol-lookbook/video-mau/*.mp4` của gói và video shop đã duyệt trong `<thu_muc_du_an>/video-da-duyet/` (nếu có). Ghi từng mặt phần mình chấm là KHÔNG KÉM hay KÉM (kèm giây). **KÉM ở bất kỳ mặt nào là chưa giao, dù tổng ≥ 9.** Chuẩn là video đã duyệt, không phải điểm số.
