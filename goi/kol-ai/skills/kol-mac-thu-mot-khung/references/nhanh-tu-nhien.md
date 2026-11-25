# Nhánh TỰ NHIÊN (mặc định từ 23/11/2026, người dùng yêu cầu học lại mẫu)

Anh An chê AK01 cứng: máy đứng chết, người chôn chân, tay "chạm nhẹ" theo từng giây. Soi lại mẫu 4 khung/giây (`phan-tich-mau.md` mục "Học lại"):
- Máy **cầm tay**: nền trôi 0–16 px trên khung 270 (~6%), trôi đều, khẽ lia theo người.
- Người **dịch chuyển**: tâm người lệch trái phải ~25% khung, dồn trọng tâm, bước nửa bước.
- **Quay lưng trong lúc đang nói** (2,25–5,0 giây), có bước chéo, tóc vung, rồi bước về giữa.
- Tay rộng, đi theo ý câu (vẫy tả gió, chống hông, đút túi, chỉ xuống giỏ hàng).

## Cách làm (AK02 bomber be, 2 clip Muse, nối một mạch)
1. **Ảnh gốc:** thay áo trên ảnh KOL đã duyệt (chỉ đổi áo, giữ mặt) → mặt giữ y nguyên. `cat_khung.py` khung tới **trên đầu gối** (`--kh 0.74`), tự đặt `--kx` khi áo cùng màu tường (script dò tâm sai với áo be).
2. **Lệnh clip** — câu máy bắt buộc: "người quay ĐỨNG YÊN TẠI CHỖ, chỉ rung và lia nhẹ; máy TUYỆT ĐỐI KHÔNG tiến lại gần, không zoom: cỡ người giữ như ảnh 1, luôn thấy rõ cả đùi, kể cả giây cuối" (c2 lần 1 không có câu này: máy tiến sát 3 lần, mất đùi, agent chấm KÉM MẪU). Đếm số lượng: "xòe bàn tay ngửa như liệt kê", không giơ ngón đếm (Muse giơ sai số ngón).
   **Lệnh clip 1** (`tin-c1.txt` mẫu ở `references/mau-lenh-tu-nhien/`): "quay bằng điện thoại cầm tay, máy rung rất nhẹ, khẽ lia theo khi cô ấy bước, không zoom"; "người không đứng chôn chân: dồn trọng tâm, bước nửa bước…"; ghi **thứ tự động tác gắn với chữ** ("khi nói X thì…"), KHÔNG chia từng giây; quay lưng gắn vào câu "các anh nhìn sau lưng này", vừa nói vừa xoay. Giữ các câu mặt, da không nốt ruồi, áo, lưng trơn.
3. **Clip 2 bắt đầu từ khung cuối clip 1** (không dùng lại `goc-khung.png`): tách 24 khung/giây đoạn 9,3–10 giây, chọn khung mắt mở, miệng gần khép, nhìn thẳng (AK02: giây 9,633), gửi làm ảnh 1 kèm mặt chuẩn làm ảnh 2; lệnh ghi "nối tiếp liền mạch từ đúng tư thế đó", "KHÔNG quay lưng trong video này".
4. **Dựng (bản 3 AK02, đúng):** cắt clip 1 tại khung nối (bỏ thêm 0,15 giây lặng đầu); clip 2 nối ngay, KHÔNG đứng hình (đứng hình 0,2 giây bị agent bắt lỗi). Tiếng đuôi clip 1 (chữ cuối "rồi") giữ thêm ~0,2 giây, mờ dần, **chồng lên khoảng lặng đầu clip 2** (đo bằng `silencedetect`, AK02: 0,32 giây) bằng `adelay` + `amix normalize=0`. Âm chuẩn **−14 LUFS ±1** như mẫu (loudnorm một lượt hay ra −15,4: đo lại bằng `ebur128` rồi chỉnh `volume`, đỉnh dưới −0,5 dB). 1080×1920, 30 khung/giây.
5. Không cần chèn cận che nối: mặt ở chỗ nối là một khung nên không đổi.

## Đã đo ở AK02
- Muse làm theo đúng: bước chéo, quay lưng 2,5–5,0, lưng trơn, xoay lại cùng mặt (agent soi mặt 2,35/3, không lỗi chặn).
- Lời đúng từng chữ cả 2 clip; tổng 19,9 giây, 93 chữ.
- Máy Muse có lúc tiến gần (1,0–2,5 giây clip 1) dù lệnh ghi không zoom: chấp nhận vì giống người quay cầm tay.
- Lỗi nhẹ còn: cúi đầu nhắm mắt ~0,85 giây khi đang nói (5,6–6,5), đếm "sáu màu" giơ 3 ngón.
