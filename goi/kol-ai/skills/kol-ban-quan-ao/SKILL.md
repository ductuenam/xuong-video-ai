---
name: kol-ban-quan-ao
description: Làm video dọc 9:16 khoảng 28 giây, một KOL AI riêng của shop (gương mặt và căn phòng cố định) mặc sản phẩm và nói giọng người bán hàng livestream chuyên nghiệp, 3 cảnh nói xen 2 cảnh cận chi tiết, cuối lùi máy ra toàn thân mời nhắn. Tất cả ảnh và clip tạo trên Muse (muse.ai) qua Claude in Chrome; dựng, so lời, soi mắt, khớp màu chạy trên máy bằng Python và FFmpeg. Từ link Shopee hoặc ảnh sản phẩm, skill lập nguồn, tạo ảnh KOL mặc đồ, viết lời có nguồn, sinh lệnh Muse, tự soát, dựng, cho người soát độc lập chấm rồi lưu kho. Dùng ngay khi người dùng muốn làm video KOL bán quần áo, video người mẫu AI giới thiệu quần áo, video livestream bán hàng bằng AI, dựng KOL riêng cho shop, nhờ KOL mặc thử một mẫu áo, chọn sản phẩm Shopee để làm video, làm thêm video bán quần áo, kể cả khi không nói chữ "skill".
---

# KOL AI bán quần áo giọng livestream (chạy trên Muse)

Cách làm này đã cho ra 5 video mẫu được chủ kênh duyệt ngày 20/11/2026 (đầm nhung, váy len, áo dạ, set cardigan, áo phao). Mỗi video khoảng 28 giây; 5 video từ chọn hàng tới lưu kho khoảng 75 phút khi chạy 2 video song song.

**Bốn điều cốt lõi, đừng đổi khi chưa thử:**
- **Một KOL, một phòng, mọi video. KOL là gương mặt của shop: tuyệt đối không được sai mặt. Da mặt trắng sáng mịn, không nốt ruồi, không chấm nâu.** Mọi ảnh đều sửa từ `kol-chuan.png`, chỉ thay trang phục. Không tạo mặt mới cho từng video. Mặt, chân và mẫu áo phải qua **cổng khóa mặt** (`scripts/khoa_mat.py`) ở ảnh gốc và ở từng cảnh; chưa qua thì script viết lệnh, dựng, lưu kho đều dừng.
- **Chuẩn là video mẫu, không phải điểm.** Video mới đặt cạnh video trong `video-mau/` của gói và không được kém ở mặt, da, chân, áo, giọng, nhịp chèn cận. Kém thì chưa giao, dù điểm cao.
- **Lời 35–44 chữ mỗi cảnh, giọng livestream, câu nét mặt bắt buộc.** Đây là phần đã thử nhiều vòng mới đạt; `viet_lenh.py` sinh đúng nguyên văn.
- **Cận che nối, lùi máy ra toàn thân.** Tiếng chạy liền; hình xen cảnh cận đúng lúc lời nói về chi tiết đó, đồng thời che chỗ nối và đoạn mắt xấu.

Video là nội dung bán hàng dùng người ảo: phần đúng sự thật về sản phẩm quan trọng ngang phần đẹp.

## Trước khi bắt đầu

1. `python scripts/kiem_may.py`. Còn ✘ thì sửa theo dòng → bên dưới. Lần đầu: chép `cau-hinh.mau.json` thành `cau-hinh.json`, hỏi người dùng từng mục rồi điền.
2. Trình duyệt: `list_connected_browsers` → `select_browser` → mở muse.ai, thấy ô "Nhắn tin". Shopee cần hồ sơ đã đăng nhập (chưa đăng nhập bị chặn ở trang kiểm tra). Không đăng nhập thay người dùng.
3. Mỗi video một thư mục trong `thu_muc_lam_viec`, đặt tên `NN-ten-ngan` (ví dụ `01-vay-len-nau`). `thu_muc_lam_viec` và `thu_muc_kol` phải nằm trong thư mục Claude Code đang mở, vì trình duyệt chỉ đính được ảnh từ đó lên Muse.
4. Chưa có `kol.json` trong `thu_muc_kol` → làm Bước 0 trước.

Cách thao tác Muse (đính ảnh, gửi lệnh, tải ảnh, tải clip, lỗi hay gặp): `references/lam-tren-muse.md`. Đọc trước lần đầu.

## Bước 0: Dựng KOL riêng (một lần cho cả shop; chạy thử đo được khoảng 3 phút trên Muse, chưa kể lúc chọn ảnh)

1. Chép `kol.mau.json` vào `thu_muc_kol` thành `kol.json`. Hỏi người dùng: tên KOL, cách gọi khách ("cả nhà", "các chị"), giọng (miền Bắc/miền Nam), mô tả gương mặt, mô tả phòng. Gợi ý sẵn theo mẫu nếu họ chưa nghĩ ra.
   - Muốn dùng mặt người thật (chủ shop, nhân viên): **phải có sự đồng ý bằng văn bản của người đó**, đặt ảnh chân dung vào `thu_muc_kol` và điền `anh_khach`.
   - Không dựng gương mặt giống người nổi tiếng.
2. `python scripts/viet_lenh.py kol` → `lenh-kol.txt`. Gửi trên Muse (đính ảnh khách nếu có). Tải 4 ảnh về, ghép cho người dùng chọn 1.
3. Lưu ảnh đã chọn thành `<thu_muc_kol>/kol-chuan.png`. Ảnh đạt: toàn thân từ đỉnh đầu tới chân, hai mắt mở, tay đủ ngón, phòng gọn có vật mốc (giá treo, chậu cây), **gương mặt ưa nhìn, sang**, **chân thon, da sáng mịn đều màu, đầu gối sáng không thâm** (chọn ảnh có chân đẹp nhất; chân xấu ở ảnh chuẩn sẽ đi vào mọi video). Không ưng ảnh nào thì tạo lại, đừng chọn đỡ.
4. Cắt mặt chuẩn và chân chuẩn: điền `kx_chuan` trong `kol.json`, chạy `python scripts/khoa_mat.py chuan <thu_muc_kol>`, mở `xem-chuan.jpg`: khung mặt lọt trọn mặt và mái, khung chân lọt trọn hai chân. Đây là ảnh mọi cảnh về sau phải so.
5. **Thử giữ mặt** trước khi làm video: làm Bước 2 với một bộ đồ bất kỳ rồi chạy cổng khóa mặt (`khoa_mat.py anh`). Mặt chấm dưới 4 thì viết `mo_ta_nguoi` chi tiết hơn và làm lại; Muse giữ mặt tốt nhất khi ảnh chuẩn nhìn thẳng, đủ sáng.
6. Ghi ngày dựng và nguồn gương mặt (AI tạo / ảnh người thật có đồng ý) vào `kol.json`.

## Bước 1: Chọn sản phẩm và lập nguồn (khoảng 3 phút)

- Tìm trên Shopee theo từ khóa, sắp bán chạy (`&sortBy=sales`). Chọn loại khác các video trước, màu nổi trên tường phòng KOL, có ảnh chi tiết và đánh giá khách cụ thể.
- Đọc trang bằng `get_page_text`. Lấy id ảnh từ thẻ `img`, tải `https://down-vn.img.susercontent.com/file/<id>` vào `shopee/` của thư mục video, ghép bảng có số thứ tự rồi chọn màu.
- Ghi `nguon.md` theo `references/mau-ghi-chu.md`: mục "Được nói" (mỗi ý kèm nguồn), mục "Không nói" (chỗ mâu thuẫn, ý không có nguồn). Lấy đúng số "Đã bán".

## Bước 2: Ảnh KOL mặc sản phẩm và ảnh cắt (khoảng 4 phút)

1. Chép `video.mau.json` vào thư mục video thành `video.json`, điền `ten` và `mo_ta` (màu, chất, cổ, tay, dáng, chiều dài, chi tiết, đồ phối, giày). Áo khoác thì phối áo trong và quần/váy hợp; váy, chân váy thì đổi cả bộ theo ảnh phối của nhà bán.
   - `chi_tiet_khoa`: 2–5 chi tiết dễ bị vẽ sai, ghi cả cái KHÔNG được thành ("cổ lá sen bẻ tròn màu kem, không phải cổ đứng", "đúng 4 cúc", "túi có nắp ở thân dưới, không có túi ngực"). Script chèn nguyên văn vào lệnh ảnh và lệnh clip; thiếu mục này thì không ra lệnh.
   - **Chân:** bộ đồ lộ chân (váy, chân váy ngắn, quần short) thì lệnh đã có câu chân từ `mo_ta_chan` của `kol.json`. Nếu ảnh nhà bán phối quần tất, tất cao, bốt thì phối theo, che chân gọn hơn. Không tự thêm tất trắng cao gối khi nhà bán không phối.
2. `python scripts/viet_lenh.py anh <thư mục video>` → `lenh-anh.txt`. Trên Muse, đoạn chat mới: đính **`kol-chuan.png` trước**, rồi 1–2 ảnh nhà bán đã cắt bỏ mặt người mẫu và chữ quảng cáo. Gửi, tải 2 ảnh về.
3. Chọn ảnh mặt giống `kol-chuan.png` nhất, đúng màu và chi tiết sản phẩm. **Phóng to so từng chi tiết với ảnh nhà bán** (cổ, cúc, khóa, túi, bo tay): sai thì sửa ngay, vì lỗi ở ảnh đi hết vào video. Lưu thành `anh-goc.png`, ghi `kx` vào `video.json`.
3b. **CỔNG KHÓA MẶT – ảnh gốc:** `python scripts/khoa_mat.py anh <thư mục video>` → `khoa-mat/to-anh.jpg` (mặt chuẩn cạnh mặt ảnh gốc, chân chuẩn cạnh chân ảnh gốc, ảnh gốc cạnh ảnh nhà bán, kèm số đo màu da chân). Giao tờ này cho agent `kol-livestream-soat` chấm (không tự chấm ảnh mình làm), rồi ghi điểm: `python scripts/khoa_mat.py cham <thư mục video> anh-goc.png mat=5 chan=5 ao=5 --nguoi kol-livestream-soat`. Mặt, chân, áo dưới 4 là CHẶN: sai cổ áo (vd cổ đứng thay cổ lá sen), đầu gối thâm, mặt khác người đều phải tạo lại ảnh, không được ghi "lỗi nhẹ" rồi đi tiếp. `viet_lenh.py video` tự kiểm cổng này.
3c. **Bộ đồ lộ đầu gối:** nhìn kỹ đầu gối ở ảnh gốc. Hơi hồng, có bóng là lên clip sẽ thành sần, thâm. Nhờ Muse sửa ảnh trước khi cắt: đính ảnh gốc rồi `chan-chuan.png`, lệnh "Sửa ảnh 1, giữ nguyên tuyệt đối mọi thứ, chỉ sửa da hai chân cho giống da chân ở ảnh 2: trắng sáng mịn đều màu, đầu gối phẳng sáng cùng màu đùi, không ửng đỏ, không thâm, không sần, da thật không bóng nhựa. Tạo 2 ảnh". Không sửa da bằng code (ra màu cam). Sửa xong chạy lại cổng ảnh gốc.
3d. **Da mặt (luật chung mọi KOL, chủ kênh 23/11):** da mặt, cổ, tay phải trắng sáng mịn, **không nốt ruồi, không chấm nâu, không tàn nhang, không mụn**. Phóng to mặt ở ảnh gốc; thấy chấm nào thì nhờ Muse sửa: "Sửa ảnh 1, giữ nguyên tuyệt đối mọi thứ, chỉ xóa nốt ruồi, chấm nâu trên mặt, da mặt trắng sáng mịn đều màu, da thật không bóng nhựa. Tạo 2 ảnh". Cổng khóa mặt chấm mục `da` cho mọi tệp có mặt; dưới 4 là CHẶN.
4. Cắt ảnh:
   ```bash
   python scripts/cat_anh.py <thư mục video> anh-goc.png <kx> can-tren=0.28,0.20,0.46 can-duoi=0.27,0.54,0.46
   ```
   Ra `goc-toan.png`, `goc-tren.png` (70% chiều cao từ đỉnh đầu, mặt to gần gấp đôi, đỡ lỗi mắt), `can-tren.png`, `can-duoi.png`, đều 720×1280. `kx` = tâm người theo chiều ngang − 0,35 (người đứng giữa thì `0.15`–`0.16`). Mở 4 ảnh xem: cận không lọt mặt, cận dưới có giày. Ghi `kx` để dùng cho `lui_may.py`.

## Bước 3: Viết lời và động tác (khoảng 3 phút)

Đọc sổ lỗi trong `references/soat-do-that.md` **trước khi viết**. Khuôn lời và lời mẫu: `references/lenh-mau.md`, mục "Lời mẫu đã đạt".

Điền vào `video.json`:
- `l1`, `l2`, `l3`: mỗi cảnh **35–44 chữ**. Cảnh 1 chào và nêu nhu cầu, khoe tổng thể; cảnh 2 khoe chi tiết, chất vải, số đơn, lời khách; cảnh 3 màu, size, dịp mặc, rồi mời nhắn.
- Viết số, size, đơn vị theo cách đọc ("size em-mờ", "năm mươi cân", "ba phân"), "nhà bán" thay "shop".
- Chỉ nói kiểu phối đang thấy trên hình; mọi ý có trong `nguon.md`; không kể trải nghiệm mặc thử, không bịa khan hiếm hay giảm giá.
- `v1`, `v2`: động tác giây 0–8,5, đổi mỗi khoảng 1,5 giây, ghi rõ tay chạm đâu. Cảnh 1 mở bằng nghiêng người vẫy chào; cảnh 2 có một động tác khoe chi tiết ở eo hoặc cổ tay. Phần 8,5–10 giây script tự thêm.
- `d1`, `d2`: động tác cảnh cận trên (một ngón chạm chi tiết rồi vuốt nhẹ) và cận dưới (dồn trọng lượng giữa hai chân, gấu khẽ lay, không bước).

Rồi `python scripts/viet_lenh.py video <thư mục video>`. Script chặn lời quá 44 chữ, chữ viết tắt, chữ "shop", và có **cổng nguồn**: mỗi vế của lời, sau khi bỏ các cụm trong bảng "Được nói" của `nguon.md`, các câu kéo khách và chữ đệm, còn bất kỳ chữ có nghĩa nào là bị chặn (script in đúng chữ đó để thêm vào bảng kèm nguồn, hoặc bỏ). Cụm khan hiếm, giảm giá, cam kết, so sánh tuyệt đối ("sắp hết", "hàng hiệu", "rẻ nhất"…) luôn bị chặn dù bảng có ghi. Ghi vào bảng cụm cụ thể ("cổ bẻ màu kem", "mười nghìn đơn", "dạ"), không ghi cụm chung như "đều xinh". Dùng lại lời của video cũ vẫn phải qua cổng này (lỗi đã gặp: lời cũ có "đi Đà Lạt" không có nguồn). Cổng không biết hình: câu về kiểu phối ("mặc quần hay chân váy") vẫn phải tự soát với hình đang có. Ra `tin1.txt`, `tin2.txt`, `loi1-3.txt`.

## Bước 4: Gửi Muse (Muse chạy khoảng 3 phút)

- **Tin 1** (đoạn chat mới): đính `goc-tren.png` rồi `goc-toan.png`, gửi `tin1.txt` → `s1-noi`, `s2-noi`, `s3-xoay`.
- **Tin 2** (đoạn chat mới khác, gửi ngay không chờ): đính `can-tren.png` rồi `can-duoi.png`, gửi `tin2.txt` → `q4-can-tren`, `q5-can-duoi`.
- Cận phải khớp cảnh nói tới từng chi tiết (nắp túi, cổ tay, móng). Muse hay tự thêm chi tiết ở cảnh nói khác ảnh gốc; khi đó cắt ảnh cận trên từ chính một khung cảnh 2 (vùng dưới cằm, khung 9:16, phóng về 720×1280) và tạo lại cận từ ảnh đó.
- Mỗi cảnh chỉ tạo 1 bản. Làm nhiều video: gửi 2 video cùng lúc (4 đoạn chat), soát và dựng video trước trong lúc video sau đang tạo.
- Xong thì tải clip theo nhãn với tiền tố `vNN-` (đoạn JS ở `lam-tren-muse.md` mục 5).

## Bước 5: Soát bằng máy (khoảng 3 phút)

```bash
python scripts/soat_lo.py <thư mục video> --tai vNN
```
Chuyển tệp từ thư mục tải về, so lời 3 cảnh (`so_loi.py`: mốc từng chữ, THIẾU/THỪA, chữ/giây), đo độ to đầu và cuối mỗi cảnh, ghép bảng khung `soat/lo.jpg`, soi mắt `soi-mat/`.

- Mở `soat/lo.jpg` và các trang `soi-mat/`: mặt đúng KOL, áo đúng, tay đủ ngón, cận không lọt mặt, cận dưới giữ khung. Ghi các đoạn nhắm mắt từ 3 ô liền trở lên.
- **CỔNG KHÓA MẶT – từng cảnh:** `python scripts/khoa_mat.py clip <thư mục video>` → `khoa-mat/to-mat.jpg` (mặt chuẩn đầu mỗi hàng, mặt cảnh 1, 2, 3 mỗi giây một ô) và `khoa-mat/to-chan.jpg` (chân chuẩn cạnh chân cảnh 3 và cảnh cận dưới). Người soát độc lập chấm mặt từng cảnh và chân, rồi ghi `khoa_mat.py cham … s1-noi.mp4 mat=5 --nguoi …` cho từng tệp. Một cảnh mặt dưới 4 hoặc chân dưới 4: tạo lại đúng cảnh đó. Tạo lại xong chạy lại lệnh `clip` (tệp đổi thì điểm cũ tự mất). `dung_chen_can.py` không dựng khi cổng chưa qua.
- Bắt nhíu mày (bảng soi mắt nhỏ không thấy): `ffmpeg -i s1-noi.mp4 -vf "fps=4,crop=280:150:220:150,scale=168:90,tile=8x5" -frames:v 1 soat/may-s1.jpg`.
- Whisper hay nghe "size" thành "sai", "dày" thành "giày": lệch ở chữ đó thường không phải lỗi, ghi lại để người dùng nghe. Lệch ở chữ khác thì nghe kỹ.
- Lỗi nặng (đổi mặt, sai áo, mất cả vế lời, đọc thừa tiếng, nhíu mày cả cảnh): tạo lại đúng cảnh đó theo mục "Tạo lại một cảnh" trong `lenh-mau.md`. Tối đa 3 lần một cảnh.
- **Soát độc lập vòng 1:** `python scripts/tach_khung_soat.py s1-noi.mp4 s2-noi.mp4 s3-xoay.mp4 q4-can-tren.mp4 q5-can-duoi.mp4 --out-dir soat-4k --fps 4`, rồi giao agent `kol-livestream-soat` chạy nền (đầu vào ghi trong tệp agent). Trong lúc chờ, lập kế hoạch dựng.

## Bước 6: Dựng (khoảng 3 phút)

Lập `ke-hoach.json`: hai danh sách đoạn `tieng` và `hinh` (tệp, từ giây, đến giây), tổng độ dài bằng nhau. Mẫu đã đạt:
```json
{"tieng": [["s1-noi.mp4", 0, 9.90], ["s1-noi.mp4", 0, 0.25], ["s2-noi.mp4", 0.15, 9.85], ["s1-noi.mp4", 0.05, 0.25], ["s3-xoay.mp4", 0.25, 9.40]],
 "hinh":  [["s1-noi.mp4", 0, 9.50], ["q4-can-tren.mp4", 0.50, 4.45], ["q5-can-duoi.mp4", 0.50, 2.60],
           ["s2-noi.mp4", 5.55, 9.85], ["s3-lui.mp4", 0, 9.35]]}
```
- **Tiếng:** lấy liền 3 cảnh nói, cắt ở khoảng lặng thật (mức âm trong `soat_lo.py`). Tổng lặng giữa hai cảnh dưới 0,25 giây thì chèn đoạn lặng đầu của một cảnh (`["s1-noi.mp4", 0, 0.25]`) để có nhịp nghỉ.
- **Hình:** cảnh 1 kết lúc hai tay ở eo → cận trên (bàn tay chạm chi tiết ở eo); cuối cảnh 1 KOL hay cười híp mắt ở giây 9–9,5, nên cắt hình cảnh 1 sớm (khoảng 8,9) lúc mắt còn mở và cho cận trên dài ra, tiếng cảnh 1 vẫn chạy hết; cận dưới đặt đúng câu nói về dáng dài hoặc giày, chỉ dùng 1,5–2 giây đầu; cận phủ chỗ nối cảnh 1–2 và đoạn mắt xấu/nhíu mày; nối chỉ khi mắt mở.
- **Nửa người → toàn thân:** `python scripts/lui_may.py s3-xoay.mp4 s3-lui.mp4 --khung <kx>,0,0.70,0.70 --dai 0.9 --tu 0.05` (khung đầu cảnh lùi máy mắt còn mở). Tiếng cảnh 3 lấy từ khoảng 0,30 và chèn trước nó 0,25 giây lặng (`["s1-noi.mp4", 0, 0.25]`), để hình bắt đầu từ 0,05 vẫn khớp môi: lệch giữa điểm vào tiếng và điểm vào hình phải đúng bằng độ dài đoạn lặng chèn.
- **Cắt chữ lặp hoặc vế nói sai:** `tim_khoang_ngat.py` tìm khoảng ngắt, `nghe_thu.py` cho Whisper nghe thử từng phương án (nghe từ đầu cảnh, đoạn bắt đầu giữa câu Whisper hay bịa câu), chọn phương án nghe đúng. Cắt giữa cảnh nói thì hình nhảy tư thế: phủ chỗ cắt bằng khoảng 1 giây cận (có thể phát ngược clip cận chân bằng `-vf reverse` để không lặp đoạn đã dùng), điểm vào và ra khỏi cận lúc mắt mở.
- **Màu cận lệch:** `python scripts/khop_mau_can.py --mau s2-noi.mp4@7.0:<vùng áo> --can q4-can-tren.mp4@1.0:<vùng áo> --ra q4-mau.mp4`, mở `q4-mau-so.jpg` xem.
- Dựng: `python scripts/dung_chen_can.py ke-hoach.json ../<NN-ten>-kol.mp4` (1080×1920, 24 khung/giây, −14 LUFS, tiếng phòng nền −36 dB; in mốc từng đoạn hình).
- Nếu cần làm chậm cảnh cận bằng `minterpolate`: đặt `-t` TRƯỚC `-i`.

## Bước 7: Kiểm thành phẩm và soát độc lập vòng 2 (khoảng 3 phút)

- Ghép lời đã cắt thành `loi-tp.txt`, chạy `python scripts/so_loi.py <thành phẩm>=loi-tp.txt`: không được có chữ THỪA ở chỗ cắt.
- `python scripts/tach_khung_soat.py <thành phẩm> --out-dir soat-tp` và `python scripts/soi_mat.py <thành phẩm> --out-dir soat-tp`; xem kỹ quanh mỗi chỗ chuyển và đuôi video.
- Giao agent `kol-livestream-soat` (vòng 2) chấm thành phẩm **đặt cạnh 2 video trong `video-mau/`** (tờ khung 1 giây/ô của cả ba). **Chỉ giao khi ≥ 8,5/10, không lỗi CHẶN và không kém video mẫu ở mặt nào** (mặt, da, chân, áo, giọng, nhịp chèn cận). Lỗi CHẶN hoặc kém video mẫu: sửa rồi soát lại đúng chỗ đó.

## Bước 8: Lưu kho và giao

```bash
python scripts/luu_kho.py <thư mục video> <thành phẩm.mp4>
```
Chép thành phẩm, mọi clip Muse (`canh-goc/`), ảnh, nguồn, lệnh, lời, kế hoạch vào `thu_muc_kho`, để sau dùng lại cảnh mà không tạo lại. Script chỉ chép, không xóa.

Báo người dùng theo thứ tự: đường dẫn thành phẩm, độ dài, thời gian làm; điểm soát độc lập; lỗi nhẹ còn lại; chữ cần nghe bằng tai (size, số, tên riêng: Claude không nghe được bằng tai); điều phải kiểm trước khi đăng (dưới). Khi người dùng chỉ ra lỗi mới, thêm một dòng vào sổ lỗi `soat-do-that.md`.

**Người dùng duyệt mặt (bắt buộc, máy đạt chưa đủ):** gửi người dùng tờ `khoa-mat/to-mat.jpg` (mặt chuẩn đầu mỗi hàng, mặt từng cảnh mỗi giây), hỏi "mặt KOL ở các cảnh có đúng là KOL của shop không?". Đã gặp: agent chấm "giống" mà chủ shop xem thì "không giống". Người dùng thấy lệch dù nhẹ (mặt dài, gầy, mắt khác) thì tạo lại đúng cảnh đó. Người dùng đồng ý thì ghi: `python scripts/khoa_mat.py duyet <thư mục video> --nguoi "<tên>" --ghi "<lời duyệt>"`.

Cổng khóa mặt cũng chạy ở đây: `luu_kho.py` dừng nếu `khoa-mat/phieu.json` chưa đủ điểm cho ảnh gốc và mọi cảnh, hoặc người dùng chưa duyệt mặt, hoặc có tệp đổi sau khi duyệt.

## Trước khi đăng công khai (nhắc mỗi lần giao)

- **Hàng thật:** trang phục trên video do AI dựng từ ảnh. Đối chiếu dáng, màu, chi tiết với hàng thật đang bán.
- **Quyền dùng:** ảnh của nhà bán và thương hiệu cần được phép.
- **Thông tin:** giá, size, màu còn hàng, số đã bán: kiểm lại lúc đăng.
- **Nhãn AI:** pháp luật Việt Nam về trí tuệ nhân tạo và quy định của từng nền tảng có nghĩa vụ ghi nhãn nội dung AI dễ gây nhầm là thật. Bật nhãn "Nội dung AI" khi đăng và đọc quy định hiện hành.
- **Gương mặt:** KOL không giống người nổi tiếng; mặt người thật chỉ dùng khi có đồng ý bằng văn bản.

## Khi có trục trặc

- **Muse chặn vùng hoặc hết lượt:** chuyển tài khoản Muse dự phòng; không có thì dừng, báo người dùng. Không tìm cách lách.
- **Mặt KOL trôi qua các video:** luôn sửa ảnh từ `kol-chuan.png`, không sửa từ ảnh của video trước. Cổng khóa mặt chặn ngay ở ảnh gốc.
- **Chân xấu (da sẫm, đầu gối thâm, chân to):** tạo lại ảnh gốc, nhắc lại câu chân; vẫn xấu thì đổi phối có quần tất, tất hoặc bốt nếu nhà bán có phối, hoặc chọn sản phẩm dài che chân.
- **Script in tiếng Việt báo lỗi `charmap`:** chạy bằng `python -X utf8 …`.
- **Máy không có card NVIDIA:** Whisper chạy chậm; đổi `whisper_model` thành `medium` trong `cau-hinh.json` và chạy `so_loi.py --model medium`.
- **Cảnh nói nào cũng nhắm mắt ở chỗ không che được:** tạo lại riêng cảnh đó, nêu đúng giây và lỗi trong lệnh. Không quá 3 lần một cảnh. Không vá mắt bằng ghép vùng mắt.

## Tệp trong skill

| Tệp | Dùng khi |
|---|---|
| `cau-hinh.mau.json`, `kol.mau.json`, `video.mau.json` | Mẫu cấu hình máy, KOL, từng video |
| `references/lam-tren-muse.md` | Thao tác Muse, lỗi Muse |
| `references/lenh-mau.md` | Lệnh mẫu và lời mẫu đã đạt |
| `references/soat-do-that.md` | Danh sách soát, cổng khóa mặt và sổ lỗi |
| `references/mau-ghi-chu.md` | Mẫu `nguon.md` |
| `agents/kol-livestream-soat.md` | Người soát độc lập (bộ cài chép vào `~/.claude/agents`) |
| `scripts/khoa_mat.py` | Cổng khóa mặt, chân, mẫu áo: tờ so, phiếu chấm, chặn khi lệch |
| `video-mau/` | Chỗ đặt video mẫu của bạn để so khi chấm (kho công khai không kèm video mẫu, xem `video-mau/README.md`) |
| `scripts/` | `kiem_may`, `viet_lenh`, `cat_anh`, `soat_lo`, `so_loi`, `soi_mat`, `tach_khung_soat`, `tim_khoang_ngat`, `nghe_thu`, `khop_mau_can`, `lui_may`, `dung_chen_can`, `luu_kho` |
