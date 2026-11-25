---
name: kol-mac-thu-mot-khung
description: Làm video dọc 9:16 khoảng 20 giây, KOL của bạn mặc thử một sản phẩm (áo khoác, áo, quần, set đồ) và nói giới thiệu như người bán hàng online, quay như điện thoại cầm tay một khung, vừa nói vừa quay lưng khoe áo, tay chạm đúng chi tiết khi nói, không cận chèn, không nhạc, không chữ — theo video mẫu "Áo khoác nam cho các anh". Skill phân tích mẫu, lập nguồn Shopee, tạo ảnh KOL mặc đồ (giữ mặt đã duyệt, trang điểm xinh hơn), viết lời 5 nhịp qua cổng nguồn, tạo 2 cảnh 10 giây trên Muse, soát bằng máy, dựng nối mềm, rồi 5 agent giám sát chấm so với video mẫu. Dùng ngay khi người dùng muốn làm video KOL giới thiệu áo khoác, video mặc thử đứng một chỗ, video giống mẫu áo khoác bomber, video KOL giới thiệu đồ nam do KOL của bạn mặc, video "cho các anh", hoặc gửi một video mẫu KOL đứng một chỗ nói và muốn làm giống, kể cả khi không nói chữ "skill". Không dùng cho video chèn cận + lùi máy (kol-ban-quan-ao), lookbook nhiều bộ (kol-lookbook) hay video người thật.
---

# KOL mặc thử một khung (KOL của bạn)

**Chuẩn là video mẫu** (20,3 giây, AI Veo, một khung, quay lưng, 5,6 chữ/giây; video mẫu không đi kèm kho công khai — muốn so cạnh thì người dùng tự đặt video mẫu của mình vào `video-mau/mau-ao-khoac.mp4` trong thư mục skill) và bản phân tích `references/phan-tich-mau.md`. Video mới phải KHÔNG KÉM mẫu ở mọi mặt (mặt, trang phục, lời, giọng, khung, nối). Điểm cao mà kém mẫu thì chưa giao.

**Bốn điều cốt lõi:**
1. **Mặt KOL không được lệch.** Mọi ảnh sửa từ `kol-chuan.png` trong thư mục `thu_muc_kol` (KOL riêng của bạn, tự tạo theo `assets/README.md`, đã duyệt mặt). Cổng `scripts/khoa_mat.py` chặn viết lệnh, dựng, lưu kho khi phiếu mặt dưới 4 hoặc người dùng chưa duyệt. Agent chấm "giống" chưa đủ: **người dùng duyệt mặt** (tờ `to-kol-duyet.jpg`) trước khi tạo clip.
2. **KOL phải xinh — bằng CHỌN ẢNH, không bằng sửa mặt.** Lệnh ảnh KHÔNG dùng câu "trang điểm lại cho xinh": ghi "giữ nguyên trang điểm, son hồng nude như ảnh 1" (23/11: câu trang điểm làm son đỏ, mắt hẹp; 3 vòng nhờ Muse sửa mặt làm mặt 4 → 3 → 2). Tạo 2 ảnh một lượt, chọn ảnh xinh và đúng mặt nhất; không đạt thì tạo LẠI từ `kol-chuan.png`, không sửa mặt nhiều vòng. **Da mặt xinh, mịn, trắng sáng, KHÔNG nốt ruồi, chấm nâu, tàn nhang** (người dùng 23/11, áp dụng mọi KOL; lệnh ảnh và lệnh clip đã có câu này, agent soi mặt chặn nếu có). Đùi trắng mịn; mặc short thì soi kỹ đùi, đầu gối ở ảnh gốc.
3. **MẶC ĐỊNH từ 23/11: nhánh TỰ NHIÊN** (`references/nhanh-tu-nhien.md`, người dùng chê AK01 cứng): máy cầm tay rung nhẹ nhưng KHÔNG tiến gần, người dồn trọng tâm, bước nửa bước, quay lưng trong lúc nói ở clip 1; lệnh ghi thứ tự động tác gắn với chữ, không chia từng giây; **clip 2 bắt đầu từ khung cuối clip 1** (khung mắt mở) nên chỗ nối liền, không cần chèn cận; tiếng đuôi clip 1 chồng lên khoảng lặng đầu clip 2, không đứng hình. Cách cũ dưới đây chỉ dùng khi nhánh tự nhiên hỏng: **Một khung, máy đứng yên, hai cảnh cùng bắt đầu từ `goc-khung.png`.** Mặt các clip Muse lệch nhau (son, kẻ mắt) hoặc có đoạn mắt nhắm → dùng **nhánh có chèn cận** (`references/nhanh-chen-can.md`, người dùng chọn 23/11): mọi chỗ chuyển giữa đoạn có mặt đi qua cận chi tiết áo hoặc cảnh quay lưng, cận rơi đúng chữ đang nói. Khi mặt các clip khớp nhau thì mới nối thẳng: cảnh 1 kết đúng tư thế khung đầu nên chỗ nối gần như không thấy (hòa hình 0,24 giây). Không cắt nhảy như mẫu (người dùng chê cắt nhảy "trông vẫn AI").
4. **Lời 5 nhịp, mỗi câu có nguồn:** mở so sánh → lợi ích theo tình huống → thông tin mua → chi tiết cầm nắm → kêu gọi + câu chốt. 38–46 chữ mỗi cảnh.

**Bài học clip Muse (AK01, 23/11/2026):**
- Lệnh clip đính 2 ảnh: ảnh 1 = `goc-khung.png` (khung đầu), ảnh 2 = cận mặt cắt từ chính ảnh gốc đã duyệt (`mat-chuan-lon.png`), chỉ để giữ mặt.
- **Không quay lưng trong cảnh có lời dài:** cảnh có quay lưng làm mặt đổi khi quay lại (s1 lần 1, 2 mặt 3/5). Muse có khi tự cho quay lưng ở cuối cảnh (s2 lần 2): dùng luôn làm cảnh khoe lưng, nhưng phải xem lời kêu gọi có rơi vào lúc quay lưng không.
- Mặt KOL lúc NÓI trên Muse vốn tròn hơn ảnh tĩnh (video đã duyệt cũng vậy): agent so với ảnh tĩnh sẽ khắt hơn; khi chấm, đưa thêm tờ mặt video đã duyệt làm mốc. Mắt lim dim là lỗi hay gặp nhất: lệnh ghi rõ "mắt mở sáng suốt video".
- **Cảnh khoe lưng làm riêng** (s3-lung, không lời) trong cùng tin với 2 cảnh nói; khi dựng, đè hình nó lên đoạn cảnh nói có mắt nhắm (`"chen": [["s3-lung.mp4", từ, đến, giây_vào]]` trong ke-hoach.json), tiếng vẫn chạy như video mẫu quay lưng giữa câu. Chỉ lấy đoạn trước khi xoay và lúc quay lưng (xoay lại hay đổi tóc). `"hinh_cuoi_den"` giữ khung đẹp ở cuối để né cái nháy mắt cuối clip.
- Giới hạn lượt: mỗi cảnh tạo tối đa 3 lần; vẫn dưới ngưỡng thì dựng BẢN THỬ (`dung_mot_khung.py ... --ban-thu`, tên tệp có "ban-thu") gửi người dùng xem quyết, không tự tạo thêm.

## Đội giám sát (nằm ở `%USERPROFILE%\.claude\agents\`, cài bằng `cai_dat.py` của kho)
| Agent | Khi nào | Chấm |
|---|---|---|
| `soi-mat-trang-diem-kol` | Ảnh gốc, clip, thành phẩm | Mặt /3 + phiếu mặt |
| `soi-ao-xoay-lung-kol` | Ảnh gốc, clip, thành phẩm | Trang phục, tay /3 + phiếu áo |
| `soi-loi-giong-kol` | Lời trước Muse, tiếng sau Muse | Lời, giọng /2,5 |
| `cham-so-mau-kol` | Thành phẩm cạnh mẫu | Dựng /1,5, thua/ngang/hơn |
| `giam-sat-kol-mot-khung` | Cuối cùng | ĐẠT / SỬA LẠI |
Thang: `references/thang-cham.md`. Agent vừa tạo trong phiên chưa gọi được bằng tên: gọi agent `general-purpose` và dặn "đọc `%USERPROFILE%\.claude\agents\<tên>.md` rồi đóng đúng vai". Mỗi lúc chỉ chạy 1 agent cho nhẹ máy. Không tự chấm ảnh mình làm.

## Trước khi bắt đầu
- Lần đầu: chép `cau-hinh.mau.json` thành `cau-hinh.json` rồi điền; tạo KOL riêng theo `assets/README.md` (đặt `kol.json` + `kol-chuan.png` vào `thu_muc_kol`). Rồi `python -X utf8 scripts/kiem_may.py`.
- Thư mục video: `<thu_muc_lam_viec>/akNN-<ten>/` (phải nằm trong thư mục đang mở Claude Code để đính ảnh lên Muse). Chép `kol-chuan.png` từ `thu_muc_kol` vào đó.
- Trình duyệt: Claude in Chrome, `list_connected_browsers` → chọn đúng trình duyệt đã đăng nhập Muse (muse.ai) và Shopee (người dùng tự đăng nhập). Tab riêng, đóng khi xong. Nhiều chat dùng chung Muse thì chạy lần lượt, không gửi song song.

## Bước 1: Mẫu mới? Phân tích (bỏ qua nếu dùng mẫu áo khoác)
ffmpeg bảng 2 khung/giây, dò cắt cảnh (`select='gt(scene,0.08)'` và độ lệch từng khung bằng OpenCV — đỉnh đơn lẻ > 3 lần trung bình là chỗ cắt), Whisper large-v3 có mốc chữ, đo âm. Ghi như `references/phan-tich-mau.md`: khung máy, chỗ nối, bảng động tác từng giây, lời, cấu trúc, chữ/giây, vì sao tự nhiên, chữ/nhạc, so với skill đang có.

## Bước 2: Chọn sản phẩm, lập nguồn (khoảng 5 phút)
Shopee tìm `&sortBy=sales`, mở trang bằng hồ sơ đã đăng nhập (chưa đăng nhập không thấy "Đã bán" và đánh giá). `get_page_text` lấy tên, giá, Đã bán, đánh giá, màu, mô tả, lời khách; bấm "Bảng quy đổi kích cỡ" chụp bảng size. Lấy id ảnh từ thẻ `img`, tải `https://down-vn.img.susercontent.com/file/<id>` vào `shopee/`, ghép bảng đánh số. Ghi `nguon.md` theo mẫu `references/mau-nguon.md`: bảng **Được nói** (cột 1 là các cụm được nói, cách nhau dấu phẩy — cổng nguồn đọc cột này) và **Không nói** (chỗ nhà bán ghi mâu thuẫn, như "Nỉ" mà mô tả là "dù").

## Bước 3: video.json, ảnh KOL mặc đồ (khoảng 4 phút trên Muse)
1. Chép `video.mau.json` thành `video.json`, điền `ten`, `mo_ta` (màu, chất, cổ, khóa, túi, bo, dáng), `phoi` (quần/chân váy, giày), `chi_tiet_khoa` (3–6 chi tiết dễ sai, ghi cả cái KHÔNG được thành; lưng áo luôn có một dòng vì có cảnh quay lưng), `anh_nha_ban`.
2. `python -X utf8 scripts/viet_lenh.py anh <thư mục>` → `lenh-anh.txt`. Muse đoạn chat mới: đính `kol-chuan.png` TRƯỚC, rồi ảnh trải phẳng đúng màu + ảnh cận cổ/khóa. Tải 2 ảnh.
3. Chọn ảnh mặt giống nhất, áo đúng từng chi tiết (soi túi tay áo: Muse hay thêm túi khóa kiểu MA-1), đùi đẹp → `anh-goc.png`. `python -X utf8 scripts/cat_khung.py <thư mục> --kx <tâm người − 0,34>` (đoán tự động hay lệch vì giá treo áo) → `goc-khung.png` (khung đầu–giữa đùi, kh 0,68), mở `xem-khung.jpg` soát.
4. **Cổng khóa mặt ảnh gốc:** `python -X utf8 scripts/khoa_mat.py anh <thư mục>` → `khoa-mat/to-anh.jpg`. Giao `soi-mat-trang-diem-kol` (mặt, trang điểm, đùi) rồi `soi-ao-xoay-lung-kol` (áo). Ghi điểm: `khoa_mat.py cham <thư mục> anh-goc.png mat=.. chan=.. ao=.. --nguoi <agent>`. Dưới 4 là làm lại ảnh.
5. **Tờ KOL cho người dùng duyệt:** `python -X utf8 scripts/to_kol_duyet.py <thư mục>` ghép mặt chuẩn | mặt ảnh gốc | ảnh gốc toàn thân | goc-khung | ảnh nhà bán vào `to-kol-duyet.jpg`, đưa đường dẫn cho người dùng xem. Được duyệt mới tạo clip; chờ thì làm sẵn Bước 4.

## Bước 4: Lời và lệnh clip
- Viết `l1`, `l2`, `v1`, `v2` trong `video.json` theo `references/mau-loi.md` (5 nhịp, từ đệm miền Bắc, gọi khách đúng đối tượng). Cảnh 1 phải có "quay lưng" (script chặn nếu thiếu).
- Cho `soi-loi-giong-kol` soát lời trước (vòng 0).
- `python -X utf8 scripts/viet_lenh.py video <thư mục>` → `tin1.txt`, `loi1.txt`, `loi2.txt`. Script chặn: quá 46 chữ, chữ số, chữ viết tắt, "shop", cụm cấm (chống nước, giữ ấm, giảm giá…), vế còn chữ không có trong bảng Được nói, ảnh gốc chưa qua cổng.

## Bước 5: Muse (khoảng 3 phút)
Đoạn chat mới, đính **chỉ `goc-khung.png`** (ảnh 1), dán `tin1.txt` (một dòng), gửi. Tải 2 clip theo nhãn `s1-noi`, `s2-noi` (mã JS ở `references/lam-tren-muse.md`, tiền tố `akNN-`).

## Bước 6: Soát bằng máy, dựng (khoảng 5 phút)
1. `python -X utf8 scripts/soat_lo.py <thư mục> --tai akNN` → so lời (THIẾU/THỪA, chữ/giây, hết lời ở giây mấy), mức âm đầu–cuối, `soat/lo.jpg`, `soi-mat/`.
2. `python -X utf8 scripts/khoa_mat.py clip <thư mục>` → `khoa-mat/to-mat.jpg`; `soi-mat-trang-diem-kol` chấm từng cảnh, ghi `cham`. Tách 12 khung/giây đoạn quay lưng giao `soi-ao-xoay-lung-kol`.
3. Lỗi nặng (đổi mặt, áo mọc chi tiết ở lưng, mất vế lời) → tạo lại riêng cảnh đó, đặt tên mới `s1-noi-b` rồi đổi tên lại, so md5. Tối đa 3 lần một cảnh.
4. `ke-hoach.json`: `{"doan": [["s1-noi.mp4", 0, <hết chữ cuối cảnh 1 + 0,15>], ["s2-noi.mp4", <ngay trước chữ đầu − 0,05>, <hết chữ cuối>]], "mem": 0.24, "lang_cuoi": 0.35}`. Chỗ nối: cảnh 1 lúc đã im, về tư thế khung đầu, mắt mở (xem `soi-mat`). Nói lặp thì tách thêm đoạn (`tim_khoang_ngat.py`, `nghe_thu.py`).
5. `python -X utf8 scripts/dung_mot_khung.py <thư mục>/ke-hoach.json <thư mục>/<ten>-v1.mp4` (1080×1920, −14 LUFS, in mốc nối). Chạy lại `so_loi.py` thành phẩm.

## Bước 7: Chấm, sửa tới khi không kém mẫu
Lần lượt (1 agent một lúc): `soi-mat-trang-diem-kol`, `soi-ao-xoay-lung-kol`, `soi-loi-giong-kol`, `cham-so-mau-kol` trên thành phẩm. Lưu phiếu từng vòng `cham/vongN-<agent>.md` và giữ bản nháp `<ten>-vN.mp4` (dùng cho giáo trình trước–sau). Sửa lỗi CHẶN → dựng `vN+1` → chấm lại đúng lỗi đó. Cuối cùng `giam-sat-kol-mot-khung`: ĐẠT (hoặc ĐẠT, CHỜ NGƯỜI DÙNG DUYỆT MẶT).

## Bước 8: Giao
- Người dùng duyệt mặt: `khoa_mat.py duyet <thư mục> --nguoi "<tên người duyệt>" --ghi "<lời người duyệt>"`.
- `python -X utf8 scripts/luu_kho.py <thư mục> <thành phẩm>` (cần cổng đã qua).
- Báo: link, độ dài, điểm từng agent, so với mẫu, chữ cần nghe bằng tai (size, bomber, số), lỗi nhẹ còn lại, điều kiểm trước khi đăng (hàng thật, quyền ảnh, giá, nhãn AI theo Luật Trí tuệ nhân tạo và quy định nền tảng, mặt không giống người nổi tiếng).
- Mỗi lỗi mới → ghi `references/so-loi.md`, sửa lệnh mẫu/script, đóng gói lại skill và cài lại.

## Tài liệu
- `references/phan-tich-mau.md` — bản phân tích video mẫu áo khoác.
- `references/thang-cham.md` — thang 10 điểm, ngưỡng giao.
- `references/mau-loi.md` — công thức 5 nhịp, lời mẫu đã chạy, từ đệm, cách gọi khách.
- `references/so-loi.md` — sổ lỗi riêng thể loại này (đọc trước khi viết lệnh).
- `references/lam-tren-muse.md` — đính ảnh, gửi lệnh, tải ảnh và clip trên Muse.
- `references/mau-nguon.md` — mẫu `nguon.md`.
- `references/nhanh-tu-nhien.md` — nhánh mặc định: máy cầm tay, người đi lại, nối khung cuối, lệnh mẫu AK02.
- `references/nhanh-chen-can.md` — nhánh có chèn cận: cắt ảnh cận, lệnh Muse cận nguyên văn, cách đặt cận trong `ke-hoach.json`.
