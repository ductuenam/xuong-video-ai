---
status: current
version: 1.0.0
updated: 2026-11-25
owner: Founder Đức Tuệ Nam
---

# BẢN ĐỒ KHO XƯỞNG VIDEO AI — đọc tệp này TRƯỚC TIÊN

Founder chỉ cần nói một câu kiểu *"hoàn thiện bộ cài video AI"*, *"thêm hoạt cảnh mới vào kho"*, *"thêm nhạc"*, *"sửa skill làm video BNI"*. Tệp này cho AI biết **mọi thứ nằm ở đâu, làm theo quy trình nào, dùng công cụ nào, luật nào không được phạm** — không cần Founder giải thích lại.

**Đọc ngay sau tệp này: [MUC_TIEU.md](MUC_TIEU.md)**: mục tiêu, hành trình 5 bước của học viên, thước đo "đạt", nguyên tắc, thứ tự ưu tiên. Mọi cải tiến phải bám tệp đó.

Đọc tiếp khi cần sâu: [KIEN_TRUC.md](KIEN_TRUC.md) (bộ cài, bộ skill cài đủ + cổng sẵn sàng, việc còn phải sửa) · [QUY_CHUAN_MO_RONG.md](QUY_CHUAN_MO_RONG.md) (luật mã, tên, cột nhãn) · [LUU_TRU_VA_PHAT_HANH.md](LUU_TRU_VA_PHAT_HANH.md) (R2, GitHub) · [../cong-cu/README.md](../cong-cu/README.md) (công cụ).

## 1. Toàn cảnh: một cửa vào, ba nơi chứa

```
D:\ductuenam\workspace\zenotera-ai-academy\repos\xuong-video-ai\     ← CỬA VÀO DUY NHẤT (kho mã, lên GitHub)
│   _kho-nang\  ──lối tắt (junction)──►  E:\xuong-video-ai-kho\     ← đồ nặng: video, zip (KHÔNG lên GitHub)
│                                              goi\vN\*.zip  ──Founder tải lên──►  Cloudflare R2
└── PHIEN_BAN.json  (đường tải + sha256 từng gói)  ──bộ cài đọc──►  máy học viên
```

| Lớp | Ở đâu | Chứa gì | Ai đưa lên mạng |
|---|---|---|---|
| **Mã + chỉ mục** | Thư mục kho mã này (ổ D) | Skill, agent, bộ cài, chỉ mục cảnh/nhạc/tiếng, tài liệu, công cụ làm kho | GitHub `ductuenam/xuong-video-ai` — Founder tạo kho và cho phép đẩy |
| **Đồ nặng** | `E:\xuong-video-ai-kho\` (mở qua `_kho-nang\`) | Bản chuẩn đã nén, gói zip từng phiên bản, báo cáo, hộp chờ đồ mới | Founder tải `goi\vN\*.zip` lên R2 |
| **Máy học viên** | `<Bộ Não AI>\08_XUONG_VIDEO\` | Bộ cài tự tải gói R2 + chép mã từ GitHub | Học viên dán một câu lệnh |

Vì sao tách ổ: ổ E còn hơn 300 GB, thêm hoạt cảnh nhiều năm không lo đầy; video không bao giờ lọt lên GitHub (giấy phép nhạc Pixabay cấm phát lại nguyên tệp). Lối tắt `_kho-nang` giúp vẫn mở mọi thứ từ một chỗ.

## 2. Bản đồ thư mục

### Kho mã (ổ D)
| Đường dẫn | Là gì |
|---|---|
| `docs/BAN_DO_KHO.md` | Tệp này |
| `docs/KIEN_TRUC.md` | Kiến trúc bộ cài, bộ skill cài đủ một lần + cổng sẵn sàng, bộ não học viên sau khi cài, **việc còn phải sửa (mục 6–7)** |
| `docs/QUY_CHUAN_MO_RONG.md` | Luật mã (`CA0001`…), tên tệp, nhóm, cột nhãn cảnh (3b) và nhạc/tiếng (3c), loại tài nguyên mới |
| `docs/LUU_TRU_VA_PHAT_HANH.md` | So sánh nơi lưu, cách đặt R2, quy trình phát hành |
| `PHIEN_BAN.json` | Phiên bản mã, phiên bản tài nguyên, đường tải + sha256 + MB từng gói, danh sách gói năng lực, Whisper theo RAM |
| `goi/video-nguoi-noi/`, `cat-ghep-quang-cao/`, `kol-ai/` | Skill và agent xếp theo việc, **cài đủ cả 3 một lần**; `goi.json › dieu_kien_theo_skill` ghi thứ người dùng tự chuẩn bị (hiện là bản chép mã kế thừa, chưa sửa xong) |
| `xuong-mau/08_XUONG_VIDEO/CHUAN_BI_THEM.md` | Danh mục điều kiện (khóa Google, Muse, Claude in Chrome, RAM): cách kiểm, cách chuẩn bị, cách làm tạm. Claude đọc trước mỗi việc cần điều kiện |
| `xuong-mau/08_XUONG_VIDEO/` | Khung ngăn sẽ chép vào bộ não học viên |
| `tai-nguyen/canh/`, `nhac/`, `am/` | `chi-muc.csv` (máy đọc, **nguồn sự thật của nhãn**) + `CHI_MUC.md` (AI đọc, sinh tự động) + `cua-toi/` (chỗ của học viên) |
| `tai-nguyen/nhac/NGUON.md` | Nguồn và giấy phép từng bài nhạc |
| `tai-nguyen/_doi-chieu/` | `bang-doi-ten.csv` (mã mới ↔ mã cũ ↔ tên gốc), danh mục gốc 24/11. Nội bộ, không chép sang máy học viên |
| `cong-cu/` | Công cụ làm kho: nén, đo âm, nhập kho, sinh chỉ mục, đóng gói, kiểm kho + `huong-dan/` gắn nhãn |
| `cai/` | Bộ cài một câu lệnh (**chưa viết**) |
| `phieu/` | Phiếu giao Antigravity (nội bộ, không lên GitHub) |
| `third_party/` | Giấy phép MIT của mã kế thừa — giữ nguyên |
| `_kho-nang/` | Lối tắt sang ổ E |

### Kho nặng (`E:\xuong-video-ai-kho\` = `_kho-nang\`)
| Đường dẫn | Là gì | Luật |
|---|---|---|
| `nguon-moi\canh\`, `nhac\`, `am\` | **Hộp chờ**: Founder thả hoạt cảnh, nhạc, tiếng mới vào đây (tên gì cũng được) | Không sửa tệp gốc |
| `nguon-moi\_da-nen\` | Bản nén + `5khung\` + `bao-cao-nen.csv` của lượt đang làm (do `nen_canh.py` tạo) | Nhập kho xong thì trống |
| `nguon-moi\_do-am\` | Ảnh sóng + phổ của nhạc/tiếng mới (do `do_am.py` tạo) | Tạm |
| `ban-chuan\tai-nguyen\canh\<nhom>\<MA>_<slug>.mp4`, `canh\xem-truoc\<MA>.jpg`, `nhac\…`, `am\…` | **Bản chuẩn**: đã nén, đặt tên, gắn nhãn. Gốc để đóng mọi gói | Chỉ thêm qua `nhap_kho.py`; không đổi tên tay |
| `goi\v1\` | 3 zip + `SHA256SUMS.txt` của bản 1 (đã đóng 25/11/2026) | **Khóa**: không sửa, không đóng đè |
| `goi\v2\` … | Mỗi lần bổ sung một phiên bản mới | |
| `bao-cao\v1\` | Báo cáo nén 24 lô của Antigravity, 7 ca kiểm, `gan-nhan\` (nhãn 2 vòng, soát chéo, sửa tay, tờ mẫu 20 cảnh) | Bằng chứng, giữ |

## 3. Hiện trạng (25/11/2026)

- **Tài nguyên bản v1** xong: 226 cảnh (23 nhóm, 64 cảnh gói nhẹ), 3 nhạc, 7 tiếng — đã nén, đặt tên, gắn nhãn hai vòng, Founder duyệt tờ mẫu. Gói: `kho-canh-du-v1.zip` 882 MB, `kho-canh-nhe-v1.zip` 217 MB, `nhac-am-v1.zip` 18 MB; sha256 đã ghi trong `PHIEN_BAN.json`.
- **Chưa có**: bộ cài `cai/`, sửa skill kế thừa (KIEN_TRUC mục 7), skill `xuong-mo-rong`. Founder chưa tạo R2, chưa tạo kho GitHub, chưa tải gói lên; thư mục này chưa `git init`.
- 7 tiếng hiệu ứng **chưa rõ giấy phép** (`giay_phep=chua-ro`); Founder quyết giữ ngày 25/11.
- Kỹ năng làm video cũ trên máy Founder (`~/.claude/skills/video-ngan-nguoi-noi`) trỏ kho cũ `E:\Video-AI` đã xóa ngày 25/11 → chưa có cảnh chèn cho tới khi bộ cài mới xong.
- Tiến độ chính thức ghi ở ZAIOS Core (dự án ZENOTERA AI Academy), không ghi checklist trong kho này.

## 4. Founder nói → AI làm gì

| Founder nói | Làm |
|---|---|
| "Kiểm kho", hoặc mở đầu bất kỳ việc nào dưới đây | `python -I -X utf8 cong-cu/kiem_kho.py` — phải ra `KHO SẠCH` trước khi làm tiếp |
| "Thêm hoạt cảnh mới" (đã thả vào `nguon-moi\canh`, hoặc đưa đường dẫn) | Quy trình 5, bước 1→7 |
| "Thêm nhạc / tiếng hiệu ứng" | Quy trình 5, nhánh nhạc/tiếng |
| "Cảnh CA0xxx tả sai / sửa nhãn" | Sửa đúng ô trong `tai-nguyen/canh/chi-muc.csv` → `python -I -X utf8 cong-cu/chung.py` sinh lại `CHI_MUC.md`. **Không cần đóng gói lại** (nhãn đi theo GitHub) |
| "Bỏ cảnh CA0xxx" | Đặt `trang_thai=an` (không xóa dòng, không dùng lại mã) → `chung.py`. Gói sau sẽ không còn cảnh đó |
| "Phát hành bản mới / đóng gói" | Quy trình 5, bước 5→7 |
| "Hoàn thiện bộ cài" / "sửa skill" | Đọc `KIEN_TRUC.md` mục 6–7; sửa trong `goi/` hoặc `cai/`; thử trên bộ não giả ở `%TEMP%\zaios_<việc>\` (mục 7) |
| "Thêm loại tài nguyên mới" (font, ảnh nền, khung chữ…) | `QUY_CHUAN_MO_RONG.md` mục 3: thêm dòng loại + thư mục cùng khuôn; thêm tiền tố vào `LOAI` trong `cong-cu/chung.py` |

## 5. Quy trình bổ sung tài nguyên (đã chạy thử trọn vẹn 25/11/2026)

Tất cả lệnh chạy từ thư mục kho mã. Mọi công cụ đều có chế độ chạy thử; chỉ ghi khi có `--ghi`.

1. **Nhận đồ**: Founder thả tệp vào `_kho-nang\nguon-moi\canh\` (hoặc `nhac\`, `am\`). Hỏi nguồn và giấy phép nếu chưa rõ.
2. **Nén / đo**:
   - Cảnh: `python -I -X utf8 cong-cu/nen_canh.py` → `_da-nen\` (tự đưa về 720×1280, 24 hình/giây, bỏ tiếng, CRF 22; SSIM < 0,97 thì CRF 20; vẫn thiếu thì `CAN_XEM`). Mức ưu tiên thấp nên máy vẫn dùng được. Nhiều cảnh (> 30) thì có thể giao Antigravity bằng phiếu theo mẫu `phieu/PHIEU_AG_NEN_KHO_CANH_01.md`.
   - Nhạc/tiếng: `python -I -X utf8 cong-cu/do_am.py` → số đo + ảnh sóng/phổ ở `_do-am\`.
3. **Gắn nhãn**: chia lô ~20 tệp cho tác tử con, giao nguyên văn `cong-cu/huong-dan/GAN_NHAN_CANH.md` (hoặc `GAN_NHAN_AM.md`), mỗi lô trả một `nhan.csv`. Một tác tử khác **soát chéo** ~10%. Ghép các lô thành một `nhan.csv`.
4. **Founder duyệt** tờ mẫu (~20 cảnh, ảnh 5 khung + nhãn, dạng HTML) — chỉ khi lô lớn hoặc có nhóm mới. Rồi nhập:
   `python -I -X utf8 cong-cu/nhap_kho.py --loai canh --nhan <nhan.csv>` (chạy thử) → thêm `--ghi`.
   Công cụ cấp mã tiếp theo, đổi tên `<MA>_<slug>`, chuyển vào `ban-chuan`, tạo ảnh xem trước, ghi `chi-muc.csv`, `bang-doi-ten.csv`, sinh lại `CHI_MUC.md`. Sau đó chép `nhan.csv` + `bao-cao-nen.csv` vào `_kho-nang\bao-cao\v<N+1>\` và dọn `nguon-moi\_da-nen\`.
5. **Đóng gói**: `python -I -X utf8 cong-cu/dong_goi.py --phien-ban v<N+1> --ghi-phien-ban` → `goi\v<N+1>\` + cập nhật `PHIEN_BAN.json`.
6. **Kiểm**: `python -I -X utf8 cong-cu/kiem_kho.py --sau` → phải `KHO SẠCH`.
7. **Báo Founder** (tiếng Việt dễ hiểu): thêm gì, gói nặng bao nhiêu, cần Founder tải 3 zip trong `goi\v<N+1>\` lên R2 thư mục `xuong-video/v<N+1>/`, rồi đẩy kho mã lên GitHub. AI **không tự tải lên**.

## 6. Luật phiên bản

- Mã tài nguyên (`CA0001`…) **không bao giờ đổi, không dùng lại**. Bỏ cảnh = `trang_thai=an`.
- Tên tệp khóa từ khi phát hành. Mô tả trong tên lệch thì sửa `mo_ta`, không đổi tên tệp.
- `goi\vN` đã đóng là khóa; bổ sung = `v<N+1>` đủ cả 3 gói (học viên mới tải một lần). Bộ cài so sha256 từng gói: gói nào không đổi thì không tải lại.
- Mọi đường dẫn có `cua-toi` hoặc dòng `chu=hoc-vien` là của học viên: không công cụ nào được ghi đè.
- Đổi nhãn không cần gói mới; đổi/thêm tệp thì cần gói mới.

## 7. Phương pháp làm việc với Founder (áp dụng mọi phiên)

- Nói tiếng Việt dễ hiểu, giải thích nguyên lý khi Founder hỏi; mỗi đề xuất có: vấn đề, các cách, cách khuyên chọn, lý do, hệ quả.
- **Hỏi trước** khi: xóa (luôn chuyển vào Thùng rác, không xóa hẳn), tải lên bất kỳ đâu (R2, GitHub, Drive), ghi ZAIOS Core, đụng `E:\Nam-Nao2` hay bộ não thật, đổi chuẩn nén.
- Thử bộ cài và công cụ chỉ trên bản sao trong `%TEMP%\zaios_<việc>\` (công cụ nhận biến `XUONG_REPO`, `XUONG_KHO_NANG` để trỏ sang bản sao). Không đặt dữ liệu thử trong `D:\ductuenam`.
- Việc nặng, lặp (nén hàng trăm cảnh): giao Antigravity bằng phiếu tự đủ, kiểm ngẫu nhiên kết quả. Việc cần mắt (gắn nhãn): tác tử con theo lô + một người soát chéo độc lập.
- "Xong" phải kèm bằng chứng chạy thật (`kiem_kho.py` ra `KHO SẠCH`, số tệp, sha256).
- Không dùng tên "An Bình" ở bất kỳ đâu (tên đơn vị cũ của mã kế thừa).

## 8. Quyết định đã chốt (bản 1)

| Ngày | Quyết định | Lý do |
|---|---|---|
| 24/11 | Mã ở GitHub, tài nguyên ở R2; Google Drive bỏ | R2 tải thẳng, không phí băng thông; Drive chặn tải tệp lớn |
| 24/11 | Nén CPU libx264 CRF 22, không dùng NVENC | Nén một lần, tải nhiều lần: CPU cho tệp nhẹ hơn 30–50% cùng độ nét |
| 25/11 | Gắn nhãn bằng mắt 2 vòng; từ bản 2 dùng ảnh 5 khung ngay | Vòng 1 (3 khung) sai nhiều ở chuyển động, chỗ chữ |
| 25/11 | Cảnh có dấu ✦ hoặc chữ in sẵn: giữ, ghi cột `co_dau_chu`, không nén lại | Founder: "gắn nhãn rồi tính" |
| 25/11 | Đổi tên CA0036 → `khoi-da-dien-tan-thanh-hat`; nhạc, tiếng đặt tên mô tả | Tên cũ sai hình / không gợi nội dung |
| 25/11 | Giữ 3 nhạc Pixabay và 7 tiếng `chua-ro` | Founder quyết |
| 25/11 | Xóa kho cũ `E:\Video-AI` và bản thử (vào Thùng rác) | Đã chuyển đủ 100% sang kho chuẩn |
| 25/11 | Bố trí "một cửa vào ổ D, đồ nặng ổ E" + bản đồ này + `cong-cu/` | Founder duyệt cách 2 |
| 25/11 | **Bỏ chia cấp**: cài đủ mọi skill một lần; skill cần tài khoản/khóa thì Claude kiểm lúc làm, thiếu thì báo cách chuẩn bị + đề xuất làm tạm; đủ thì làm theo ý người dùng | Founder: skill nhẹ, không bắt người dùng mở cấp | 
