# Bộ lệnh Muse cho video lookbook (mọi ảnh và clip đều tạo trên Muse)

**Luật da KOL (chủ shop chốt 23/11/2026): da mặt KOL xinh, mịn, trắng sáng nhưng vẫn thật (không sáp, không nhựa). KHÔNG nốt ruồi, KHÔNG chấm nâu, KHÔNG tàn nhang đậm — "mặt có nốt ruồi là không ai rước".** Mọi lệnh ảnh và clip có mặt đều chép câu da ở dưới; cổng khóa mặt chặn mục này.

Luật chung khi gửi Muse:
- **Mỗi tin MỘT yêu cầu** (một ảnh hoặc một clip). Gửi nhiều cái một lúc Muse hay báo "lỗi nội bộ" và chỉ làm một.
- Chờ Muse báo xong (ảnh ~30 giây, clip ~1–2 phút) rồi mới gửi tin sau. Tin sau bắt đầu bằng "Yêu cầu mới, chỉ MỘT …".
- Mỗi video mở **một đoạn chat phụ mới** ("Đoạn chat phụ mới"), không làm trong đoạn chat chính.
- Đính ảnh: dùng ô "Đính kèm file" (Claude in Chrome: `file_upload` vào ô file-input).
- Tải về: xem `muse-js.md` (soi trên trang trước khi tải, gom nhiều tệp vào một gói rồi tải một lần).
- Đặt tên tệp ngay trong lệnh ("đặt tên b1-tien.mp4") để lúc tải nhận đúng tệp.

---

## Bước 0 — KOL thương hiệu của anh chị (làm MỘT lần, dùng cho mọi video sau)

KOL là gương mặt của shop: **mọi video phải là đúng một người, không sai mặt dù một cảnh.** Cách duy nhất giữ được mặt trên Muse là **không bao giờ tạo người mới** cho từng video: có MỘT ảnh toàn thân chuẩn của KOL, và mọi bộ đồ là **sửa trang phục trên chính ảnh đó**.

Thư mục KOL (`thu_muc_kol` trong cau-hinh.json, mặc định `<thu_muc_du_an>/kol/`):
- `kol-chuan.png` — ảnh TOÀN THÂN chuẩn: đứng thẳng giữa khung, thấy rõ mặt, mắt mở, **hai chân trắng sáng, mịn, đầu gối sáng không thâm** (mọi chân sau sẽ so với chân này), studio phông trơn.
- `kol.json` — `{"anh_chuan": "kol-chuan.png", "anh_chan_chuan": "", "mo_ta": "<tóc, son, khuyên tai, dáng>"}`.
- Chạy `python scripts/khoa_mat.py chuan <thu_muc_kol>` → `mat-chuan.png`, `chan-chuan.png`, MỞ `xem-chuan.jpg` kiểm.
- **Anh chị tự duyệt** `xem-chuan.jpg`: đây là mặt chuẩn của shop. Chưa ưng thì làm lại, đừng đi tiếp.

**Cách A — shop đã có KOL (ảnh/video KOL đã duyệt, hoặc người mẫu thật đã đồng ý bằng văn bản):** lấy một ảnh toàn thân đẹp nhất đã duyệt làm `kol-chuan.png`. Nếu ảnh đó chân chưa đẹp hoặc không thấy chân, sửa trên Muse:
```
Yêu cầu mới, chỉ MỘT ảnh, đặt tên kol-chuan.png: sửa ảnh đính kèm. Giữ Y HỆT cô gái: gương mặt, đường nét, trang điểm, tóc, khuyên tai, màu da, tuổi, vóc dáng — KHÔNG đổi mặt, không làm mặt tròn hơn, bè hơn, gầy hơn, dài hơn. Đặt cô ấy đứng thẳng giữa một studio phông xám nhạt trơn, toàn thân từ đỉnh đầu tới giày, có khoảng trống trên đầu và dưới chân, một tay chống hông nhẹ, tay kia buông, cười mỉm khép miệng, mắt mở. Mặc áo len trơn màu kem và chân váy ngắn trơn màu xám để thấy rõ chân, giày thể thao trắng trơn. CHÂN: đôi chân thon thẳng, da chân trắng sáng mịn đều màu như da mặt, đầu gối sáng sạch không thâm không đỏ, không vết, không sần, không gân xanh. Không túi, không vòng tay, không mũ. Da thật có lỗ chân lông. Dọc 9:16, ảnh chụp thật, không chữ, không logo.
```
**Cách B — chưa có KOL, tạo KOL AI mới (không giống người thật, người nổi tiếng nào):**
```
Tạo 4 ảnh chụp chân thực, khung dọc 9:16, mỗi ảnh là cùng MỘT cô gái Việt Nam khoảng 23 tuổi, gương mặt trái xoan hiền, dễ mến, KHÔNG giống bất kỳ người nổi tiếng nào; tóc <dài đen gợn sóng, mái thưa>, trang điểm nhẹ, không kẻ mắt đuôi dài, son <hồng san hô nhạt>, khuyên tai <ngọc trai đinh tán nhỏ>. Cô ấy đứng thẳng toàn thân giữa studio phông xám nhạt trơn, từ đỉnh đầu tới giày, một tay chống hông nhẹ, cười mỉm khép miệng, mắt mở. Áo len trơn màu kem, chân váy ngắn trơn màu xám, giày thể thao trắng trơn. CHÂN: đôi chân thon thẳng, da chân trắng sáng mịn đều màu như da mặt, đầu gối sáng sạch không thâm không đỏ. Không túi, không vòng tay, không mũ. Da thật có lỗ chân lông, không lọc mịn. Không chữ, không logo. Bốn ảnh khác nhau nhẹ về gương mặt để tôi chọn một.
```
Chọn 1 ảnh (anh chị chọn), lưu `kol-chuan.png`, chạy lệnh `chuan`, anh chị duyệt.

**Ảnh chuẩn phải sạch da mặt.** Ảnh chuẩn (cách A hay B) có tàn nhang, nốt ruồi, chấm nâu thì làm sạch MỘT lần trên Muse trước khi làm video (mọi ảnh sau sửa từ ảnh này):
```
Yêu cầu mới, chỉ MỘT ảnh, đặt tên kol-chuan-sach.png: sửa ảnh đính kèm. Giữ Y HỆT gương mặt, đường nét, dáng mặt, mắt, mũi, môi, son, tóc, mái, khuyên tai, trang phục, tư thế, phông, ánh sáng, khung hình — KHÔNG đổi mặt. CHỈ làm sạch da mặt: xóa hết tàn nhang, nốt ruồi, chấm nâu; da mịn, trắng sáng, đều màu, vẫn có vân da thật tự nhiên, không sáp, không nhựa, không bóng. Dọc 9:16, ảnh chụp thật, không chữ, không logo.
```

---

## Luật đồ phối để chân luôn đẹp (cận chân rất nhiều trong lookbook)
- Muse vẽ chân trần hay ra da hồng sẫm, đầu gối thâm, sần — phóng to ở cảnh cận chân là hỏng cả video. Thứ tự ưu tiên đồ phối: **quần dài / chân váy dài qua gối → quần tất (đen mờ, màu da mờ) + bốt/giày → tất cao gối + bốt cao**. Chân trần chỉ khi bộ đồ bắt buộc (váy ngắn của shop mà phối tất không hợp).
- Có chân trần thì lệnh ảnh VÀ lệnh clip phải chép nguyên câu chân: "đôi chân thon thẳng, da chân trắng sáng mịn đều màu như da mặt, đầu gối sáng sạch không thâm không đỏ, không vết, không sần, không gân xanh".
- Ảnh cận chân hoặc clip chân ra đầu gối thâm: sửa trên Muse (KHÔNG sửa bằng code, ra màu cam): đính ảnh lỗi + `kol/chan-chuan.png`, lệnh "Yêu cầu mới, chỉ MỘT ảnh: sửa ảnh 1, CHỈ sửa da hai chân cho giống da chân ở ảnh 2 (trắng sáng, mịn, đầu gối sáng không thâm), giữ y hệt mọi thứ khác: giày, tất, váy, nền, khung hình." Rồi tạo lại clip chân từ ảnh đã sửa.

---

## Bước 2 — Ảnh toàn thân từng bộ = SỬA ĐỒ trên ảnh KOL chuẩn (đính: ảnh 1 = kol/kol-chuan.png, ảnh 2–3 = ảnh shop)
```
Yêu cầu mới, chỉ MỘT ảnh, đặt tên toan-bN.png. Sửa ảnh 1 (ảnh người mẫu). Giữ CHÍNH XÁC khuôn mặt, đường nét, trang điểm, màu son, kiểu tóc, mái, khuyên tai, màu da, tuổi và vóc dáng của cô ấy — KHÔNG đổi mặt, không làm mặt tròn hơn, bè hơn, đầy hơn, gầy hơn, dài hơn hay già hơn. MẶT GIỮ Y HỆT ẢNH 1 như chụp cùng một lần: cùng cỡ và dáng mắt, KHÔNG kẻ mắt đuôi dài (chỉ viền mi mảnh như ảnh 1), son đúng độ đậm như ảnh 1. DA MẶT xinh, mịn, trắng sáng, sạch: KHÔNG nốt ruồi, KHÔNG chấm nâu, KHÔNG tàn nhang (ảnh 1 có thì xóa đi), vẫn là da thật có vân da tự nhiên, không sáp, không nhựa, không bóng. Nhắc lại, miệng cười mỉm khép nhỏ như ảnh 1. Giữ tư thế đứng giữa khung, một tay chống hông nhẹ, tay kia buông, cười mỉm khép miệng, mắt mở nhìn máy. Chỉ thay toàn bộ trang phục cho đúng như sản phẩm ở ảnh 2 (ảnh của nhà bán): <tả chi tiết nhận diện: màu CHỮ HOA, chất liệu, cổ, cúc/khóa, túi, tay, gấu, vân, dáng, độ dài>. Phối <quần dài / chân váy dài / quần tất + bốt — theo luật đồ phối>, <giày trơn không logo>. Bỏ hết trang phục cũ. KHÔNG túi, KHÔNG vòng tay, KHÔNG đồng hồ, KHÔNG nhẫn, KHÔNG dây chuyền, KHÔNG mũ, KHÔNG kính. <Nếu lộ chân: câu chân.> Đổi phông thành phông giấy trơn màu <màu hợp áo>, sàn cùng màu, ánh sáng studio mềm. Khung dọc 9:16, TOÀN THÂN từ đỉnh đầu tới giày, có khoảng trống trên đầu và dưới chân, cỡ người trong khung như ảnh 1. Da thật thấy lỗ chân lông, không lọc mịn, không bóng. Ảnh chụp thật, không chữ, không logo.
```
Mỗi bộ 2 phương án (hai tin). Bị cổng chặn thì tạo lại với câu mở đầu nêu đích danh lỗi vừa gặp: "Ảnh trước bị LỖI MẶT: <mọc nốt ruồi ở hàm / kẻ mắt đuôi sắc / mắt hẹp dài, mặt già hơn …> — lần này tuyệt đối tránh." (video thử 23/11: bộ 2, 3 bị chặn vì vậy, tạo lại 1 lần là đạt). **Sau đó bắt buộc qua cổng khóa mặt bước ảnh** (mục "Cổng khóa mặt" trong SKILL.md): `khoa_mat.py anh` → agent chấm mặt, áo, chân → anh chị xem `to-anh.jpg`. Mặt hoặc áo dưới 4 thì làm lại, KHÔNG đưa sang bước clip.
Bộ sau có thể đính thêm ảnh toàn thân bộ trước đã qua cổng làm ảnh tham chiếu mặt, nhưng ảnh 1 luôn là `kol-chuan.png`: sửa chồng ảnh này sang ảnh khác nhiều lần thì mặt trôi dần.

## Bước 3a — Ảnh cận chân (đính toan-bN.png đã chốt)
```
Yêu cầu mới, chỉ MỘT ảnh, đặt tên chan-bN.png: sửa ảnh đính kèm thành cảnh cận thấp từ <gấu váy / đầu gối> xuống sàn: GIỮ Y HỆT <váy/quần>, <tất>, <giày>, hai bàn chân đặt trên sàn. Giữ y hệt da chân của ảnh (nếu lộ chân: đôi chân thon thẳng, da chân trắng sáng mịn đều màu, đầu gối sáng sạch không thâm không đỏ, không sần). Cùng nền và sàn, cùng ánh sáng. Không thấy tay, áo, thân trên. Không chữ, không logo. Dọc 9:16, ảnh chụp thật.
```

## Bước 3b — Ma-nơ-canh ảnh góc (đính toan-bN.png)
```
Yêu cầu mới, chỉ MỘT ảnh, đặt tên goc-bN.png: chỉ lấy TRANG PHỤC của ảnh đính kèm (giống hệt áo, màu, quần/váy, tất, giày; KHÔNG túi, KHÔNG phụ kiện) mặc trên một ma-nơ-canh trắng không mặt của cửa hàng, toàn thân từ đầu tới chân, đứng thẳng giữa khung, trên nền XANH LÁ phẳng thuần (#00FF00), ánh sáng đều, không bóng trên nền, không sàn, không chữ, không logo. Dọc 3:4, ảnh sản phẩm chụp thật.
```
Trên máy: `python scripts/tach_nen_xanh.py goc-bN.png goc-tach-bN.png`.

## (Tùy chọn) Đổi nền phông trơn thành phòng trong nhà — làm trên ảnh đã chốt để GIỮ mặt
```
Yêu cầu mới, chỉ MỘT ảnh: sửa ảnh đính kèm. Giữ Y HỆT cô gái: gương mặt, tóc, trang điểm, khuyên tai, trang phục, dáng, khung hình và cỡ người trong khung. KHÔNG đổi mặt. CHỈ thay phông trơn và sàn bằng một phòng khách sáng sang trọng ban ngày: cửa kính khung trắng cao, sàn gỗ xương cá sáng, sofa vải bouclé màu be mờ phía sau, rèm voan trắng, một chậu cây xanh nhỏ; gọn gàng, không đồ lộn xộn, không chữ, không gương, không người khác. Ánh sáng trên người khớp với phòng. Dọc 9:16, ảnh chụp thật.
```
Làm cho cả ảnh toàn và ảnh chân của mọi bộ. Ghi `"nen": "phong"` vào kế hoạch dựng.

---

## Bước 4 — Clip Muse (mỗi bộ 2 clip; đính ảnh đã cắt 720×1280: k-toan-bN.png / k-chan-bN.png)

**Máy tiến** (`bN-tien.mp4`):
```
Yêu cầu mới, chỉ MỘT video, đặt tên bN-tien.mp4: dùng Muse Video tạo 1 video 10 giây từ ảnh vừa đính kèm (khung đầu). MỘT CẢNH LIỀN KHÔNG CẮT, không nói, không nhạc, không chữ, dọc 9:16. Máy quay TIẾN ĐỀU và rất chậm suốt 10 giây từ toàn thân vào đến NGANG EO (giây 0 toàn thân, giây 5 từ đầu đến đầu gối, giây 10 từ đầu đến eo) — không tiến gần hơn eo, không quay cận mặt. Cô ấy đứng tại chỗ, một tay chống hông, tay kia buông, đổi trọng tâm nhẹ, cười mỉm nhẹ khép miệng nhìn máy (không hở răng), mắt MỞ to tự nhiên suốt video, chớp nhanh và thưa, không nhắm mắt, không nheo mắt, đầu thẳng không nghiêng. KHUÔN MẶT VÀ DA MẶT giữ Y HỆT khung đầu suốt 10 giây như cùng một tấm ảnh, không thêm bất cứ đốm hay chấm nào lên da; không phúng má, không dài mặt, không cằm nhọn, không già đi, không kẻ mắt đậm thêm. <Tóc, son, khuyên tai từ kol.json mo_ta>. <Áo: màu, kiểu, chi tiết "giữ nguyên không biến dạng">; <quần/váy>, <giày>. Không túi, không vòng tay, không mũ, hai cổ tay trống. DA MẶT xinh, mịn, trắng sáng, sạch suốt 10 giây: không một đốm chấm nào trên da (không tàn nhang, không nốt ruồi, không chấm nâu) — khung đầu có thì làm mờ hết; vẫn là da thật có vân, không sáp, không nhựa. <Nếu nền phòng: CĂN PHÒNG giữ y hệt ảnh, không thêm đồ, không thêm người.> Son giữ đúng màu của khung đầu, không đậm lên, không cam, không đỏ gạch; khuyên tai giữ đúng cỡ đinh rất nhỏ như ảnh. Da thật khô lì, không bóng dầu. Bàn tay đủ năm ngón. Xong chỉ báo kích thước và thời lượng.
```

**Cận chân** (`bN-chan.mp4`):
```
Yêu cầu mới, chỉ MỘT video, đặt tên bN-chan.mp4: dùng Muse Video tạo 1 video 10 giây từ ảnh vừa đính kèm (khung đầu). MỘT CẢNH LIỀN, không nói, không nhạc, không chữ, dọc 9:16. MÁY ĐỨNG YÊN TUYỆT ĐỐI, KHÔNG nghiêng lên, KHÔNG lùi, KHÔNG tiến: khung chỉ từ <gấu váy / đầu gối> xuống giày suốt 10 giây, không bao giờ thấy tay, eo, áo, mặt. Cô ấy đứng tại chỗ, đổi trọng tâm chậm từ chân này sang chân kia, nhón nhẹ một gót rồi đặt xuống, bàn chân KHÔNG xoay, giày/bốt giữ y hệt hình dạng, hai bàn chân LUÔN ở giữa khung, KHÔNG bước ra mép khung, không bắt chéo chân. <Giày, tất, quần/váy> giữ y hệt ảnh. DA CHÂN (nếu lộ) giữ y hệt ảnh suốt 10 giây: trắng sáng, mịn đều màu, đầu gối sáng không thâm không đỏ, không sần, không đổi màu khi cử động. Nền và sàn giữ y hệt ảnh. Xong chỉ báo kích thước và thời lượng.
```

**Sau mỗi clip:** soi 6 khung ngay trên trang (`muse-js.md`). Mặt khác người, áo đổi màu, máy nghiêng lên → gửi lại ngay, kèm một câu nêu đích danh lỗi vừa gặp ("Video trước bị lỗi: … — lần này tuyệt đối tránh").

**Câu da trong lệnh clip** (video thử 23/11): ĐỪNG viết kiểu "giữ tàn nhang như ảnh" hay "không thêm tàn nhang" (Muse vẽ tàn nhang dày dần). Viết như mẫu trên: "da mịn trắng sáng, sạch, không một đốm chấm nào (không tàn nhang, không nốt ruồi, không chấm nâu), khung đầu có thì làm mờ hết, vẫn có vân da thật". Lệnh clip càng gọn càng giữ mặt.

Vì sao từng câu: "tới ngang eo" — máy sát mặt làm mặt bè, da bóng; "giữ Y HỆT mặt ở giây 0" — Muse hay trôi mặt về cuối clip (dài ra, già đi, mọc tàn nhang); "chớp nhanh, không nhắm lâu" — cái nhắm dài làm hỏng điểm cắt; "không kẻ mắt đuôi dài, son cố định" — trang điểm lệch giữa các bộ bị chấm "khác người"; "máy đứng yên, không bước ra mép" — clip chân hay ngẩng máy hoặc bước ra khỏi khung.


**Soát trước khi sang clip (bắt buộc):** chạy cổng khóa mặt bước ảnh (`khoa_mat.py anh`, tờ `khoa-mat/to-anh.jpg`: ảnh toàn thân từng bộ cạnh `mat-chuan.png`, chân cạnh `chan-chuan.png`, áo cạnh ảnh shop) và nhìn riêng 3 thứ: màu son (không được đỏ/cam hơn mặt chuẩn), da (sạch: không nốt ruồi, chấm nâu, tàn nhang; mịn, trắng sáng mà vẫn có vân da thật), khuyên tai (giống mặt chuẩn). Lệch thì làm lại ảnh đó — clip Muse giữ nguyên son và da của ảnh khung đầu, sang bước clip mới phát hiện là phải làm lại cả clip.
