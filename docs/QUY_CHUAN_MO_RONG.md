---
status: draft
version: 0.1.0
updated: 2026-11-24
owner: Founder Đức Tuệ Nam
---

# QUY CHUẨN MỞ RỘNG XƯỞNG VIDEO AI

Mục đích: thêm gói năng lực mới, loại AI mới, tài nguyên mới, kiểu video mới (do kho chung phát hành hoặc do học viên tự yêu cầu) mà **không phải sửa bộ cài**, và AI luôn tìm đúng thứ cần trong một đến ba bước đọc, không phải quét ổ đĩa.

Năm nguyên tắc:
1. **Sổ đăng ký là nguồn sự thật.** Mọi thứ tồn tại trong xưởng phải có một dòng trong sổ. Thứ không có trong sổ coi như không có.
2. **Đọc theo tầng L0 → L3.** AI đi từ chỉ dẫn ngắn nhất xuống tệp cụ thể, không lướt thư mục.
3. **Một khuôn chỉ mục cho mọi loại tài nguyên.** Thêm loại mới chỉ là thêm một thư mục theo đúng khuôn.
4. **Phân chủ rõ ràng.** Mỗi dòng có cột `chu`: `kho` (kho chung, bản cập nhật được thay) hoặc `hoc-vien` (không bao giờ bị thay).
6. **Không gắn tên riêng.** Tên tệp, mã, thư mục, nội dung chỉ mục dùng từ chung, không mang tên công ty hay cá nhân nào. Nguồn gốc mã kế thừa chỉ ghi ở `third_party/` (giấy phép MIT bắt buộc giữ).
5. **Không giả định bộ não cố định.** Bộ não của học viên có thể đã thêm ngăn, đổi tên ngăn; xưởng dò bằng bản đồ, không dò theo số ngăn.

## 1. Bốn tầng đọc của AI

| Tầng | Tệp | AI đọc khi | Nội dung |
|---|---|---|---|
| L0 | Khối `<!-- XUONG-VIDEO:BEGIN … END -->` trong `CLAUDE.md` của bộ não | Mỗi phiên | 5 dòng: xưởng ở đâu, đọc gì tiếp, 3 luật |
| L1 | `<XUONG>/CHI_MUC_XUONG.md` | Mỗi việc liên quan video | Việc làm được, câu lệnh mẫu, việc nào cần chuẩn bị thêm, loại tài nguyên đang có, kiểu video của học viên, liên kết tới bản đồ bộ não |
| L2 | `<XUONG>/BAN_DO_BO_NAO.md` và `<XUONG>/tai-nguyen/<loai>/CHI_MUC.md` | Khi cần lời, dữ liệu hoặc tài nguyên | Vai trò → ngăn thật của bộ não; bảng tài nguyên theo nhóm |
| L3 | Tệp cụ thể (`.md` ngăn bộ não, `.mp4`, `.jpg` xem trước) | Khi đã chọn xong | Nội dung |

Bản máy đọc của L1 là `<XUONG>/xuong.json`. Bộ cài và skill đọc, ghi tệp này. AI đọc `CHI_MUC_XUONG.md`, được sinh lại từ `xuong.json` mỗi lần thay đổi.

`<XUONG>` là thư mục xưởng trong bộ não. Tên mặc định `08_XUONG_VIDEO`. Nếu bộ não đã có ngăn số 08, bộ cài lấy số trống kế tiếp (09, 10…). Đường dẫn thật ghi trong khối L0 và trong `xuong.json`; mọi skill đọc đường dẫn từ đó, không viết cứng `08_`.

## 2. Bản đồ bộ não (thích ứng mọi bộ não)

Bộ cài (và lệnh "cập nhật bản đồ bộ não") làm:
1. Đọc `INDEX.md` của bộ não, liệt kê các thư mục cấp 1 (bỏ thư mục ẩn, `00_HOP_THU_NHAP`, chính `<XUONG>`).
2. Gán mỗi thư mục vào **vai trò chuẩn** dựa trên tên ngăn, mô tả và từ khóa trong `INDEX.md`:

| Vai trò | Dùng cho video | Ngăn gốc của Bộ Não Khởi Động |
|---|---|---|
| `ho-so` | Tên, câu chuyện, thành tựu, liên hệ | `01_CA_NHAN_VA_THUONG_HIEU` |
| `san-pham` | Sản phẩm, giá, lời kêu gọi | `02_SAN_PHAM_VA_BANG_GIA` |
| `khach-hang` | Nỗi đau, khách lý tưởng, phản hồi | `03_KHACH_HANG_MUC_TIEU` |
| `giong-van` | Cách xưng hô, từ hay dùng, từ cấm | `04_GIONG_VAN_VA_NGON_TU` |
| `quy-trinh` | Cách làm, kịch bản | `05_QUY_TRINH_VA_CONG_VIEC` |
| `media` | Ảnh, video thật của học viên | `06_KHO_MEDIA_VA_TAI_LIEU_GOC` |
| `cong-ty` | Hồ sơ doanh nghiệp (nếu tách riêng) | `07_CONG_TY_…` |
| `khac` | Ngăn học viên tự thêm chưa rõ vai trò | (tùy) |

3. Ghi `BAN_DO_BO_NAO.md`: mỗi vai trò → danh sách ngăn thật kèm mô tả một dòng. Một vai trò có thể ứng với nhiều ngăn (ví dụ học viên có thêm `09_SAN_PHAM_MOI`). Ngăn không đoán được vai trò thì để `khac` và hỏi học viên **một lần**.
4. Ghi ngày dò. Khi `INDEX.md` của bộ não mới hơn ngày dò, AI tự dò lại trước khi làm video.

Luật dùng: lời video chỉ lấy từ ngăn có trong bản đồ, không bịa. Thiếu thông tin thì hỏi, rồi đề nghị lưu vào đúng ngăn của bộ não theo skill `phan-loai-bo-nao` (học viên duyệt trước khi ghi).

## 3. Khuôn tài nguyên (một khuôn cho mọi loại)

```
<XUONG>/tai-nguyen/<loai>/
├─ CHI_MUC.md          bảng theo nhóm cho AI đọc (sinh từ chi-muc.csv)
├─ chi-muc.csv         bản máy đọc
├─ xem-truoc/          ảnh nhỏ <ma>.jpg (loại hình ảnh, video)
├─ <nhom>/<ma>_<mo-ta-ngan>.<duoi>            tệp của kho chung
└─ cua-toi/<nhom>/<ma>_<mo-ta-ngan>.<duoi>    tệp của học viên
```

Các loại tài nguyên đã định:

| `loai` | Là gì | Tiền tố mã kho chung | Tiền tố mã học viên | Có ở bản 1 |
|---|---|---|---|---|
| `canh` | Video cảnh trám dọc 9:16 | `CA` | `UCA` | Có, 226 (`CA0001`–`CA0226`) |
| `nhac` | Nhạc nền | `NH` | `UNH` | Có, 3 (`NH0001`–`NH0003`) |
| `am` | Tiếng hiệu ứng | `AM` | `UAM` | Có, 7 (`AM0001`–`AM0007`) |
| `anh` | Ảnh nền, ảnh minh họa | `AN` | `UAN` | Chưa |
| `font` | Phông chữ có dấu tiếng Việt | `FO` | `UFO` | Chưa |
| `do-hoa` | Khung, thẻ, mẫu chữ động | `DH` | `UDH` | Chưa |
| `giong` | Hồ sơ giọng (tên giọng AI, tốc độ) | `GI` | `UGI` | Chưa |
| `nhan-vat` | KOL AI, nhân vật (ảnh khóa mặt) | `NV` | `UNV` | Chưa (gói `kol-ai`) |

Thêm loại mới = thêm một dòng vào bảng này (tiền tố 2 chữ chưa dùng) và một thư mục theo khuôn trên. Bộ cài, skill và AI đọc được ngay vì cùng khuôn.

### 3a. Luật đặt mã và tên tệp

| Thứ | Luật | Ví dụ |
|---|---|---|
| **Mã** | Tiền tố 2 chữ + 4 số; học viên thêm `U` phía trước. Duy nhất trong loại, **không bao giờ đổi, không dùng lại** kể cả khi tệp bị ẩn. Số tăng dần, không mang ý nghĩa | `CA0004`, `UCA0001` |
| **Tên tệp** | `<mã>_<mô-tả-ngắn>.<đuôi>`. Mô tả ngắn: chữ thường, không dấu, nối `-`, tối đa 32 ký tự, rút từ cột `mo_ta` | `CA0004_vong-man-hinh-ao-bao-quanh.mp4` |
| **Nhóm (thư mục)** | Chữ thường không dấu, nối `-`, 1–3 từ, là chủ đề chứ không phải nguồn tạo | `man-hinh-ao`, `nen-chu`, `viet-nam` |
| **Ảnh xem trước** | `xem-truoc/<mã>.jpg`, rộng 360 px, khung giây 3 | `xem-truoc/CA0004.jpg` |
| **Cấm** | Dấu tiếng Việt, khoảng trắng, chữ hoa trong mô tả, ký tự `… & # % ' "`, tên công ty, tên người, ngày tạo, tên công cụ tạo | ~~`MUSE N001-N100/N004.mp4`~~ |

Vì sao tên tệp có cả mã lẫn mô tả: **AI tìm theo mã và chỉ mục** (chính xác, nhanh); **người xem thư mục đọc được mô tả** mà không cần mở chỉ mục. Mô tả trong tên chỉ để đọc cho tiện; khi lệch với `mo_ta` thì `chi-muc.csv` đúng, không đổi tên tệp (đổi tên làm hỏng đường dẫn đã lưu trong dự án cũ).

Cột `tu_khoa` (3–8 từ không dấu, cách nhau `;`, có cả từ đồng nghĩa người dùng hay nói, ví dụ `ban-hang;doanh-so;tang-truong;bieu-do`) là thứ giúp AI chọn cảnh chuẩn nhất. Bản 1 đã điền đủ 226 cảnh ngày 25/11/2026.

### 3b. Gắn nhãn bằng mắt (bắt buộc trước khi phát hành một tài nguyên hình ảnh)

Mô tả rút từ ghi chú cũ có thể sai, và một cảnh có thể đổi nội dung giữa clip (ví dụ `CA0025`: giây 2 là ổ khóa, giây 7 là lõi năng lượng). Vì vậy mỗi cảnh phải được một AI **nhìn ảnh 5 khung** (5% · 27,5% · 50% · 72,5% · 95% độ dài; bản 1 dùng 3 khung rồi soát lại bằng 5 khung) rồi điền theo `cong-cu/huong-dan/GAN_NHAN_CANH.md`:

| Cột (thêm cho `loai=canh`) | Điền gì | Ví dụ |
|---|---|---|
| `mo_ta` | Sửa cho đúng hình; nếu cảnh đổi nội dung thì tả cả hai đoạn | "Ổ khóa hologram, sau chuyển sang lõi năng lượng phát sáng" |
| `tu_khoa` | 5–8 từ không dấu, có cả cách người dùng hay nói | `bao-mat;an-toan;khoa;du-lieu;cong-nghe` |
| `mau` | 1–2 màu chủ đạo | `xanh-dam;cam` |
| `chuyen_dong` | `dung-yen`, `day-vao`, `lui-ra`, `lia-ngang`, `bay-qua`, `xoay` | `day-vao` |
| `cho_chu` | Chỗ trống đặt phụ đề: `tren`, `giua`, `duoi`, `khong` | `duoi` |
| `doi_noi_dung` | Cảnh có đổi hẳn nội dung giữa clip không: `co` (ghi giây đổi) hoặc `khong` | `co@4s` |
| `hop_video` | Loại video hợp: `bni`, `gioi-thieu-dn`, `quang-cao`, `day-hoc`, `tin-tuc`… | `gioi-thieu-dn;quang-cao` |
| `co_dau_chu` | Chữ, số, logo, dấu in sẵn trong hình hoặc người trông như thật; `khong` nếu sạch. AI tránh dùng cảnh có dấu cho video cần sạch, hoặc che/cắt khi dựng | `dau-sao@goc-phai-duoi` |

Cách làm (chi tiết ở `BAN_DO_KHO.md` mục 5): chia lô 20 cảnh cho các tác tử con, mỗi tác tử đọc ảnh 5 khung và trả bảng; một tác tử khác soát chéo ngẫu nhiên 10%; Founder xem mẫu 20 cảnh. Nếu phần mô tả trong **tên tệp** sai hẳn với hình thì đổi tên **trước khi phát hành bản 1** (ghi vào `bang-doi-ten.csv`). Từ khi phát hành, tên tệp khóa, chỉ sửa chỉ mục.

### 3c. Gắn nhãn bằng tai (nhạc và tiếng hiệu ứng)

Mỗi tệp được đo bằng máy (độ dài, độ lớn LUFS, nhịp/phút, đường năng lượng mỗi 2 giây) và xem ảnh dạng sóng + phổ, rồi điền `mo_ta`, `tu_khoa` như cảnh, thêm:

| Cột (`loai=nhac`) | Điền gì | Ví dụ |
|---|---|---|
| `nhip_bpm` | Nhịp/phút ước bằng máy, ghi `~` | `~92` |
| `nang_luong` | `nhe`, `vua`, `manh`, `tang-dan` | `manh` |
| `tam_trang` | 2–3 từ không dấu | `vui;tre-trung` |
| `hop_video` | Như cột của cảnh | `bni;gioi-thieu-dn` |
| `doan` | Các đoạn theo giây: dạo, beat, lắng, cao trào, hết | `0-4 mở nhẹ; 4-47 beat đều` |
| `bat_dau_goi_y` | Giây nên bắt đầu cắt nhạc | `9.5` |
| `do_lon_lufs` | Độ lớn cả bài; bài càng to càng phải hạ khi có giọng | `-6.5` |

| Cột (`loai=am`) | Điền gì | Ví dụ |
|---|---|---|
| `giay` | Độ dài, 2 số lẻ | `1.33` |
| `diem_nhan_s` | Giây mạnh nhất, đặt trùng lúc hình đổi | `1.10` |
| `do_lon` | `nho`, `vua`, `rat-to`, kèm lời khuyên tăng/giảm dB nếu lệch | `rat-to (nên hạ 8 dB)` |
| `dung_khi` | Tình huống hợp | `chuyển cảnh lớn` |

Bảng đối chiếu mã mới ↔ mã cũ ↔ tên gốc: `tai-nguyen/_doi-chieu/bang-doi-ten.csv` (nội bộ, không chép sang máy học viên).

**Cột chung của mọi `chi-muc.csv`:**

| Cột | Ý nghĩa |
|---|---|
| `ma` | Mã duy nhất trong loại |
| `loai` | Một trong các loại ở bảng trên |
| `nhom` | Nhóm chủ đề, chữ thường không dấu, nối `-` |
| `ten_nhom` | Tên nhóm tiếng Việt |
| `mo_ta` | Một câu mô tả để AI chọn |
| `tu_khoa` | Từ khóa, cách nhau bằng dấu `;` |
| `tep` | Đường dẫn tương đối trong thư mục loại |
| `xem_truoc` | Ảnh nhỏ (nếu có) |
| `thong_so` | Ví dụ `720x1280;24fps;10s` hoặc `128kbps;95s` |
| `nguon` | Nơi tạo hoặc tải |
| `giay_phep` | `kho-chung` (dùng trong video, không phát lại nguyên bộ), `cc0`, `pixabay`, `hoc-vien-tu-co`, `chua-ro` |
| `chu` | `kho` hoặc `hoc-vien` |
| `goi` | `nhe`, `du` (gói nào chứa) |
| `ngay_them` | YYYY-MM-DD |
| `trang_thai` | `dung` (đang dùng) hoặc `an` (ẩn, không chọn) |

Luật: không xóa dòng; muốn bỏ thì đặt `trang_thai=an`. Tài nguyên `giay_phep=chua-ro` không được dùng trong video đăng công khai.

## 4. Gói năng lực (thêm loại AI mới không sửa bộ cài)

Mỗi gói là một thư mục `goi/<ma-goi>/` có tệp `goi.json`:

```json
{
  "ma": "cat-ghep-quang-cao",
  "ten": "Cắt ghép, quảng cáo, ảnh bìa",
  "mo_ta": "Cắt livestream, biến thể quảng cáo, ảnh bìa, HyperFrames",
  "skills": ["ab-edit", "anh-bia-video", "video-ngan-hyperframes"],
  "agents": ["kiem-duyet-doc-lap"],
  "can_goi": ["video-nguoi-noi"],
  "can_tai_nguyen": ["canh", "nhac", "am"],
  "can_phan_mem": ["python", "ffmpeg", "whisper", "node"],
  "dieu_kien_theo_skill": {"anh-bia-video": ["khoa-google-vertex"], "ab-edit": ["ram-16gb-nen-co"]},
  "cau_lenh_mau": ["Cắt livestream <tên file> thành các clip ngắn", "Làm ảnh bìa cho video vừa dựng"]
}
```

**Mọi gói đều cài ngay một lần, không chia cấp** (Founder chốt 25/11/2026). Bộ cài đọc mọi `goi/*/goi.json`, tự tính phần mềm và tài nguyên cần, chép đủ skill, agent, tự liệt kê việc làm được trong `CHI_MUC_XUONG.md`.

`dieu_kien_theo_skill`: thứ người dùng phải tự chuẩn bị (tài khoản, khóa, máy mạnh hơn), mã lấy từ danh mục `xuong-mau/08_XUONG_VIDEO/CHUAN_BI_THEM.md` (`*` = mọi skill trong gói). Bộ cài kiểm lúc cài và ghi `xuong.json › dieu_kien`; Claude kiểm lại thật trước mỗi việc: đủ thì làm luôn, thiếu thì báo cần chuẩn bị gì và đề xuất cách làm được ngay. Skill mới cần thứ mới → thêm một dòng vào danh mục đó. Thêm một loại AI mới (ví dụ "video hoạt hình", "podcast") chỉ cần thêm một thư mục gói với `goi.json`, không sửa bộ cài.

## 5. Học viên tự mở rộng

Skill `xuong-mo-rong` (giai đoạn 2) nhận các câu nói tự nhiên và luôn làm đủ 4 bước: **đặt tệp đúng khuôn → ghi dòng chỉ mục → sinh lại `CHI_MUC.md` → báo lại một dòng**. Trước khi ghi thì đề xuất và chờ học viên duyệt, như luật của bộ não.

| Học viên nói | Ghi vào |
|---|---|
| "Thêm cảnh / ảnh / nhạc / tiếng này vào kho" | `tai-nguyen/<loai>/cua-toi/<nhom>/U…` + dòng `chu=hoc-vien`. Video được chuẩn hóa về 9:16 kèm ảnh xem trước. Nhạc phải hỏi nguồn, ghi `giay_phep` |
| "Lưu kiểu video này của tôi" | `mau-cua-toi/<ten-kieu>/MAU.md` (+ video mẫu) + một dòng ở mục "Kiểu video của tôi" trong `xuong.json` |
| "Lần sau làm khác đi chỗ này" | Mục "Rút kinh nghiệm" trong `MAU.md` của kiểu đang dùng, hoặc `mau-cua-toi/_chung/RUT_KINH_NGHIEM.md` |
| "Tạo nhóm cảnh mới tên X" | Thêm nhóm vào `chi-muc.csv` (`chu=hoc-vien`) |
| "Tôi đã có khóa Google / tài khoản Muse" | Kiểm lại điều kiện theo `CHUAN_BI_THEM.md`, ghi đường dẫn khóa vào cấu hình (không chép nội dung khóa), cập nhật `xuong.json › dieu_kien` |
| "Cập nhật bản đồ bộ não" | Dò lại mục 2 |

Không bao giờ sửa skill gốc trong `.claude/` để tùy biến: bản cập nhật sẽ thay skill gốc. Tùy biến luôn nằm trong `mau-cua-toi/` và các dòng `chu=hoc-vien`.

## 6. Luật cập nhật

| Thứ | Khi chạy lại câu lệnh cài |
|---|---|
| Skill, agent trong `.claude/` (mọi gói) | Thay bằng bản mới; bản cũ cất vào `<XUONG>/.sao-luu/<ngày>/` |
| Tệp và dòng `chu=kho` | Thêm mới, cập nhật mô tả; dòng bị kho chung bỏ thì đặt `trang_thai=an`, không xóa tệp |
| Tệp và dòng `chu=hoc-vien`, `mau-cua-toi/`, `du-an/`, `thanh-pham/` | **Không đụng** |
| Khối L0 trong `CLAUDE.md`, mục 1–3 của `CHI_MUC_XUONG.md` | Thay toàn bộ phần giữa hai dấu đánh dấu |
| `BAN_DO_BO_NAO.md` | Dò lại, giữ các gán vai trò học viên đã trả lời |

## 7. Kiểm khi phát hành (bắt buộc trước mỗi bản)

1. Mọi tệp trong `tai-nguyen/` có đúng một dòng chỉ mục, và ngược lại.
2. Mã không trùng trong cùng loại.
3. Cài lên bộ não giả có ngăn 08 sẵn và có ngăn tự thêm: xưởng lấy số trống, bản đồ gán đúng vai trò.
4. Cài đè lên bộ não đã có tài nguyên, kiểu video của học viên: không mất tệp nào.
