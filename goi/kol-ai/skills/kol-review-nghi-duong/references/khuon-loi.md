# Khuôn lời video KOL review khu nghỉ

Rút từ video mẫu (xem `phan-tich-mau.md` mục 4–5). Viết vào `loi.json` của thư mục video.

## Hai loại video, cùng một khung hình

| | Loại A – chào dịch vụ cho chủ khu (`"loai": "chao-dich-vu"`) | Loại B – review cho khách (`"loai": "review-khach"`) |
|---|---|---|
| Người xem | Chủ khu nghỉ, người làm du lịch | Khách đang tìm chỗ nghỉ |
| Gọi | "anh chị làm du lịch ơi", "anh chị" | "cả nhà ơi", "ai đang tìm chỗ đi biển…", "các bạn" |
| Móc câu | Điều bất ngờ: KOL chưa từng đến mà vẫn quay được | Điều đáng thèm: view, giá, một chi tiết lạ của khu |
| Chứng minh | Agent nhận ra khu, để ý chi tiết, tự viết lời | Khoe 2–3 chi tiết thật thấy trên ảnh (đèn, hiên, giường, view) |
| Nỗi đau | Thuê người nổi tiếng tốn, chờ lịch; không có thời gian tự quay | Đi chơi sợ phòng không giống ảnh, sợ chỗ đông, chỗ xa |
| Giải pháp | Gửi ảnh → agent + người mẫu ảo làm video | Khu này: phòng thật như ảnh chủ gửi, tiện ích có thật |
| Kêu gọi | Bình luận / nhắn / đăng ký để nhận cách làm | Nhắn khu để hỏi phòng trống, giá (chủ khu cấp) |

## Năm phần, ~210 chữ cho ~50 giây

| Phần | Cảnh | Chữ | Mục đích |
|---|---|---|---|
| Móc câu | c1 | 18–24 | Gọi đúng người + điều bất ngờ, ≤ 5 giây |
| Chứng minh | c2, c3 | 24–30 mỗi cảnh | Đi qua 2 chỗ, mỗi câu gắn với vật đang thấy |
| Nỗi đau | c4, c5 | 24–32 | Đồng cảm, câu hỏi tu từ "lấy đâu ra… cơ chứ?" |
| Giải pháp + lợi ích | c6, c7 | 26–30 | Chỉ cần ảnh; đều đặn video mới |
| Kêu gọi | c8 | 18–24 | Một hành động rõ, quay lại chỗ mở đầu |

Mỗi cảnh ≤ 40 chữ (Muse nói 4,6–5 chữ/giây, phải xong trước giây 8,5 của clip 10 giây). Cả bài 170–235 chữ.

## Luật nói tự nhiên

- Câu ngắn, chen dấu phẩy để Muse ngắt hơi; câu dài nhất ≤ 28 chữ.
- Mỗi cảnh ít nhất một chữ đệm cuối câu: "nhá", "nhé", "đấy", "thôi", "luôn", "cơ chứ", "nữa", "đâu". Một chữ đệm không lặp quá 3 lần cả bài.
- Xưng "em". Gọi agent là "nó" hoặc "agent" (Muse đọc "ây-giần" được; nghe lại bằng tai).
- Mỗi câu gắn với vật đang thấy trong bối cảnh của cảnh đó (nói đèn thì đứng cạnh đèn).
- Viết số, đơn vị bằng chữ theo cách đọc. Không chữ viết tắt in hoa (trừ "AI").
- Không văn viết: "tọa lạc", "sở hữu", "mang đến trải nghiệm", "đẳng cấp", "hoàn hảo".

## Luật sự thật (CHẶN nếu vi phạm)

- Mọi ý về khu (view, phòng, đèn, giá, tiện ích, khoảng cách) phải thấy trên ảnh chủ khu gửi hoặc có trong `nguon.md` chủ khu xác nhận.
- Video thử dùng bối cảnh minh họa: không tên khu, không giá, không địa chỉ.
- Người mẫu ảo không kể đã ở, đã ngủ, đã ăn thật.
- Không hứa kết quả: "chắc chắn", "cam kết", "kín phòng", "rẻ nhất", "duy nhất", "100%", "miễn phí" (trừ khi có thật và có giấy).
- Có tự nhận "người mẫu ảo" trong lời (như mẫu) và nhãn AI trên hình.

## Thẻ nhấn ý (`the`, `the2` mỗi cảnh)

- Chữ hoa ngắn 2–6 chữ, nhắc đúng cụm vừa nói. `khi_noi` = cụm 2–4 chữ trong lời để script tự đặt giờ.
- Màu: `do` cho nỗi đau, bất ngờ; `vang` cho lợi ích, con số; `xanh` cho "agent làm gì", "người mẫu ảo".
- Khoảng 1 thẻ mỗi cảnh, tổng 8–11 thẻ.

## Lời video thử 23/11 (đã qua máy soát)

Xem `video-thu/loi.json`. Mẫu câu c5 (nỗi đau, câu hỏi tu từ): "Mà cả ngày anh chị đã lo đón khách, dọn phòng rồi, lấy đâu ra thời gian tự quay tự dựng cho đều đặn được cơ chứ?"
