---
name: video-ngan-nguoi-noi
description: Sản xuất trọn một video ngắn dọc 9:16 dạng người thật nói đầu và cuối, đoạn giữa là giọng trên mô hình đồ họa và cảnh AI: viết kịch bản từ video mẫu hoặc chủ đề, kiểm nguồn, nhắc tạo cảnh trám trên Google Flow, dựng từ file quay, tự nghiệm thu, làm ảnh bìa, viết content đăng kèm và giao đủ trong một thư mục. Dùng ngay khi người dùng muốn làm video review công cụ, video giải nỗi đau, viết kịch bản video ngắn, làm lại theo video mẫu, dựng file vừa quay theo phong cách kênh, viết caption cho video của kênh, hoặc câu ngắn "Edit video <tên file> cho tôi" (tự cắt lặng, nói hỏng, thêm phụ đề, nhạc; agent video-dung dựng, video-cham-diem chấm), hoặc "Dựng một video giới thiệu bản thân cho tôi theo cấu trúc BNI" (tự hỏi một lượt thông tin còn thiếu, tự ghi hồ sơ, tự dùng ảnh, video của người dùng nếu có, không có thì không mặt, giọng AI miễn phí), kể cả khi không nói chữ "skill". Không hỏi duyệt từng bước. Không dùng cho cắt livestream, làm biến thể quảng cáo hay dựng có duyệt từng bước (dùng skill ab-edit).
---

# Sản xuất video ngắn người nói

Đầu vào: chủ đề hoặc video mẫu. Đầu ra: một thư mục gồm video đã nghiệm thu, ảnh bìa, content đăng, bảng nguồn.

Có mẫu thì tự xem và tự dựng. Chỉ dừng ở các cửa duyệt ghi dưới đây, không hỏi câu thừa. Người dùng đã dặn tự làm trọn thì làm từ mẫu đến bàn giao, chỉ báo kết quả cuối và những chỗ cần họ nghe, xác nhận.

## Luật đã chốt (đọc trước mỗi video)

Mọi thứ người dẫn đã duyệt nằm trong `references/da-chot.md`, phần máy kiểm được nằm trong `references/da-chot.json`. Không làm khác luật này khi chưa có bản nâng cấp được duyệt.

- `tao_giong.py` tự thay cách đọc (AI thành Ây‑Ai, MCP, API, USB-C...) và kiểm cảm xúc của bản đọc trước khi gửi. Sai luật thì dừng, không tốn credit. Không tự viết lại cách đọc bằng tay để lách.
- Video giới thiệu công cụ, skill, plugin: kiểm tình trạng hiện tại của từng món ở nguồn gốc, ghi `tinh-trang.json` (`{"ngayKiem": "dd/mm/yyyy", "mon": [{"ten", "trangThai": "co-san" | "plugin-chinh-thuc" | "cai-them", "cachLay", "nguon"}]}`). Món có sẵn thì lời nói rõ "có sẵn, gõ lệnh là dùng", không gọi là thứ phải cài. `lap_canh.py` và `nghiem_thu.py` chặn nếu thiếu hoặc sai (luật 15).
- `nghiem_thu.py` đọc lại chữ đã gửi (`giong/*.da-gui.txt`); sai luật là ✘, không bàn giao.
- Câu kết (luật 9, đổi 16/11/2026): câu hỏi thật, rồi chỉ về bình luận ghim ("Hướng dẫn cài từng bước mình để sẵn ở bình luận ghim nhé!"). Cấm "Comment CÀI, mình gửi...", "bình luận chữ ... để nhận", "inbox nhận" vì Meta coi là kéo tương tác, YouTube cấm đổi thưởng lấy tương tác. Máy chặn ở bản đọc, `loi.txt` và `canh.json`. Content có mục bình luận ghim soạn sẵn với chỗ trống `[DÁN LINK HƯỚNG DẪN]`.
- Sửa skill xong luôn chạy `python scripts/hoi_quy.py`: hỏng một mục là chưa được dùng bản sửa. Gặp lỗi mới thì thêm mẫu vào `scripts/hoi_quy/` trước khi sửa.

## Dò trùng trước khi làm (bắt buộc)

Nhận việc xong chạy ngay `python rut_kinh_nghiem.py "<dự án>" --bat-dau` để tính giờ từ đầu (tạo thư mục dự án trước).

Người dẫn làm nhiều video và có thể quên chủ đề đã làm. Mỗi video bàn giao xong được ghi vào sổ `so-video.csv` ở thư mục kênh (số, dự án, chủ đề, từ khóa, nguồn, ngày). Mỗi lần người dẫn giao video mới, trước khi làm gì khác, chạy với nguyên câu yêu cầu của họ cùng tên công cụ, tên kho, từ khóa chính:

```bash
python tim_trung.py "<thư mục kênh>" "<câu yêu cầu của người dẫn>" "<tên công cụ>" "<từ khóa>"
```

Script dò sổ video theo hai chiều (từ khóa mới có trong sổ, từ khóa cũ có trong câu yêu cầu), rồi dò thêm `du-an/` và `BAI-DANG/` để biết trạng thái.

Mã thoát 1 là đã có video: dừng lại, báo người dẫn tên video cũ, trạng thái (sẵn sàng, đã lên lịch, ĐÃ ĐĂNG) và hỏi làm tiếp theo góc khác hay bỏ. Trùng một phần (cùng chủ đề, khác độ sâu) thì đề xuất làm phần 2 chỉ nói phần video cũ chưa nói, không lặp ví dụ cũ (23-skill-ben-trong là phần 2 của 05-skill). Phần 2 hay video giải thích cơ chế thì đi sâu theo khuôn D trong kich-ban.md, ít nhất chi tiết bằng video mẫu, không rút thành bản lướt. Người dẫn đã biết và vẫn bảo làm (bản dài, bản cập nhật) thì làm, ghi lý do vào content.

## Chọn cách làm theo file trong thư mục chủ đề

Mở từng video trong thư mục chủ đề, xem vài khung hình và nghe lời:

| Thấy gì | Làm thế nào |
|---|---|
| **Có file người dẫn tự quay**, nói kịch bản của kênh (đúng mặt người dẫn, thường là file gốc điện thoại hoặc máy quay, có nói lặp, nói hỏng) | **Dựng từ file quay**: bóc lời bằng `boc_loi.py`, chọn lần nói tốt nhất, cắt ghép như mục "Dựng", dùng cảnh `nguoi*` cho đầu và cuối. Không tạo giọng AI. Lời trong file quay là kịch bản: viết `loi.txt` theo đúng lời đã nói |
| **Chỉ có video mẫu** của kênh khác (tải về, người khác nói) | **Tự làm trọn bằng giọng AI và clip kho**: mục "Không quay" |
| Có cả hai | Video mẫu để tham khảo cách làm, dựng từ file người dẫn quay |
| **Chỉ có link video mẫu** (Facebook, TikTok), không có file | Facebook không cho lấy file trực tiếp. Hỏi người dẫn một lần: cho tải về (nêu tên file, nguồn, cỡ), tự gửi file, hay làm theo những gì xem được. Không tải được thì mở trên trình duyệt, đọc chú thích, tua từng khung có số thứ tự và phóng to tên kho GitHub hiện trên hình (`zoom` vùng thanh tên kho), rồi kiểm từng kho như mục "Chỉ có chủ đề". Kho mẫu nêu không có giấy phép hoặc không đúng tính năng mẫu nói thì thay bằng kho đúng, ghi vào content |
| **Chỉ có chủ đề**: một câu, một ảnh tóm tắt, không có video | Tự tìm kho GitHub nhiều sao nhất đúng chủ đề (API tìm kiếm, sắp theo sao), đọc README, viết kịch bản riêng: giải thích khái niệm bằng một tình huống đời thường, rồi giới thiệu kho đó để thử. Ảnh của người khác chỉ dùng làm chủ đề, không đưa vào video, không chép bố cục. Làm bằng giọng AI như mục "Không quay". Không có thư mục chủ đề thì tạo `<số kế tiếp>.<chủ đề>` trong thư mục kênh |

Không chắc file nào là file quay thì đối chiếu mặt với ảnh trong `anhThamChieu` của hồ sơ kênh. Nhận ra được thì làm luôn, không hỏi lại người dùng.

## Chuẩn bị

Câu lệnh đầu tiên trên máy mới: chạy `python cai_dat.py "<thư mục kênh>"` NGAY, không hỏi. Script tự cài phần mềm thiếu (winget trên Windows, Homebrew trên Mac, pip, npm), tự kiểm lại, tự chép agent; chỉ khi máy chặn (diệt virus như Bkav, thiếu quyền) nó in lệnh PowerShell: đưa nguyên các lệnh đó cho người dùng dán vào PowerShell chạy quyền quản trị (Windows) hoặc Terminal (Mac, tự gõ mật khẩu máy khi Homebrew hỏi; Claude không gõ thay), rồi chạy lại `cai_dat.py`.


0. Cần trang nhắc lời khi quay: `python nhac_loi.py <dự án>`, đọc từ `loi-thoai.txt`.
1. Tìm `ho-so-kenh.json` ở thư mục kênh. Chưa có hoặc chưa cài: đọc `references/so-tay.md`, chạy `scripts/cai_dat.py`.
2. Mọi lệnh Python chạy từ thư mục `scripts/` của skill, đặt `PYTHONUTF8=1`.
3. Mỗi video một thư mục: `<thư mục kênh>/du-an/<số>-<tên>/`.

## 8 bước

| # | Việc | Ai | Tài liệu |
|---|---|---|---|
| 1 | Bóc video mẫu, kiểm lại mọi số liệu | Claude | `references/kich-ban.md` |
| 2 | Viết kịch bản theo khuôn, kèm bảng nguồn và lời đọc | Claude, **người dùng duyệt** | `references/kich-ban.md` |
| 3 | Đối chiếu kho cảnh, nhắc tạo cảnh còn thiếu trên Flow | Claude nhắc, **người dùng tạo hoặc đồng ý cho Claude tạo** | `references/canh-tram-flow.md` |
| 4 | Quay và gửi file gốc, hoặc tạo giọng AI nếu người dùng chọn không quay | **Người dùng** quay, hoặc Claude tạo giọng và **người dùng nghe duyệt** | Mục "Chuẩn quay" trong `references/kich-ban.md`; mục "Không quay" bên dưới |
| 5 | Chọn lần nói, lập dữ liệu, dựng, tự nghiệm thu | Claude | Mục "Dựng" bên dưới |
| 6 | Làm ảnh bìa | Claude | skill `anh-bia-video` |
| 7 | Viết content đăng | Claude | `references/content-dang.md` |
| 8 | Giao đủ một thư mục | Claude, **người dùng xem và tự đăng** | Mục "Bàn giao" |

Không tự đăng lên mạng xã hội. Không tự trừ credit Flow khi người dùng chưa đồng ý số credit.

## Dựng

Trong thư mục dự án cần có:

| File | Nội dung |
|---|---|
| `doan.json` | `{"nguon": [file...], "doan": [[số nguồn, từ giây, đến giây]...], "toc": 1.0}` |
| `loi.txt` | Mỗi dòng một cụm phụ đề, đúng lời đã nói, đúng chính tả tên riêng |
| `canh.json` | Danh sách cảnh, xem `references/mo-hinh-canh.md` |
| `goi-y.txt` | Tên riêng để Whisper nghe đúng, cách nhau bằng dấu phẩy |
| `nhac.txt` | Tên bài trong `nhacDuocDung` của `references/da-chot.json` (hiện có beat-vlog, phonk, future-bass), đổi bài giữa các video. Bài khác trong `boNhac` chưa kiểm quyền ngoài YouTube, `tron_am.py` sẽ chặn |
| `public/` | Ảnh riêng của video. Ảnh và video trang web tạo bằng `chup_web.py`, lưu ở `public/web/` |

Trình tự:

1. Tạo `doan.json` chỉ có `nguon`, chạy `python boc_loi.py <dự án>` để có các đảo tiếng trong `boc-loi-<số>.txt`.
2. So với lời đọc, chọn lần nói tốt nhất cho từng câu. Nói lại nhiều lần thì giữ lần sau cùng trọn câu, nghe riêng để chắc. Giữ nguyên tốc độ nói thật, `toc` = 1.0. Không để khoảng lặng quá 0,7 giây.
3. Ghi `doan`, `loi.txt`, `canh.json`, rồi chạy cả dây chuyền:

```bash
python dung.py "<dự án>"
```

Lệnh này dừng sau khi có `soat-tinh-*.jpg`: ảnh khung cuối từng cảnh, chưa xuất video. Xem bằng mắt: khung cắt, ô khoanh lệch, chữ tràn, thẻ đè phụ đề. Phụ đề ở khung cuối phải thuộc chính cảnh đó (`tu`, `den` đếm cụm từ 1). Bước này cũng đo khoảng lặng trong file giọng, có ✘ thì sửa giọng trước. Sửa thì `--tu canh`, ảnh ra lại trong vài chục giây. Ổn rồi mới xuất:

```bash
python dung.py "<dự án>" --tu render
```

Chạy một mạch không dừng: thêm `--het`. Giờ từng bước ghi ở `thoi-gian.csv` của dự án, dùng để so tốc độ giữa các video.

Bước cuối `nhan-dien` (`gan_nhan_dien.py`) chạy sau khi nghiệm thu đạt: gắn watermark suốt video, intro khi video dài hơn `introKhiDaiHon` (mặc định 60 giây, video ngắn phải vào thẳng móc câu) và outro, theo `nhanDien` của hồ sơ kênh. Tiếng intro, outro tự chỉnh về gần độ to của video. Ra `render/thanh-pham.mp4`, đây là file bàn giao; `ra.mp4` là bản chưa gắn, nghiệm thu và tờ soát vẫn đo trên bản này. Watermark phủ đúng khung nhãn tên kênh ở góc dưới phải (300×112, chỗ che logo Flow), nên phải là ảnh 600×224 kín khung, không để hở góc. Chỉ đổi phần nhận diện thì chạy `--tu nhan-dien`.

Sửa sau khi đã xuất: `--tu master` khi sửa đoạn cắt, `--tu phu-de` khi sửa `loi.txt`, `--tu canh` khi sửa cảnh hoặc chữ. `--den canh` để dừng sớm.

Mã thoát 2 ở bước `canh` nghĩa là thiếu clip trong kho: quay lại bước 3.

Remotion lỗi bundle hoặc render, hoặc cần dựng cho đơn vị không có giấy phép Remotion: dùng skill `video-ngan-hyperframes`. Skill đó chạy cùng `canh.json` và cùng mã cảnh `engine/src/MoHinh.tsx`, chỉ thay bước tạo `hinh-cam.mp4`, rồi quay lại đây từ bước `tron`. Thêm mẫu cảnh mới ở đây là bản dự phòng có luôn; sửa `MoHinh.tsx` chỉ được dùng các hàm Remotion mà `engine-hf/shim/remotion.tsx` của skill đó đã có (AbsoluteFill, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame), dùng hàm khác thì thêm vào shim trong cùng lần sửa.

## Không quay: giọng AI và clip kho

Trình tự đã chạy ổn (video 07 đến 14, mỗi video 8 đến 12 phút từ mẫu đến bàn giao):

1. Bóc mẫu, kiểm từng số và từng công cụ ở nguồn gốc (`references/kich-ban.md`).
2. Viết `loi.txt` (cụm ngắn cho phụ đề) và `doc-tts.txt` (bản đọc liền hơi, giữ dấu phẩy ở chỗ chuyển ý, có thán từ ở móc câu, chỗ bất ngờ, câu kết).
3. Tạo giọng, cắt nghỉ dài, chèn nghỉ ở dấu phẩy, đo nhịp (lệnh bên dưới). Từ máy nghe nghi sai thì đo VAD trước khi tạo lại.
4. Chụp trang công khai bằng `chup_web.py`, lập `canh.json`, chạy `dung.py` để có ảnh tĩnh; sửa đến khi không còn ✘.
5. `--tu render`, nghiệm thu, xem `to-soat.jpg`.
6. Bìa, content, tờ hướng dẫn PDF, bàn giao, báo thời gian từng khâu.

Khi người dẫn chọn không quay. Bỏ `boc_loi.py`, `doan.json` chỉ cần `{"nguon": [], "giong": "<file giọng>"}`. Không dùng cảnh `nguoi*`: mở bằng `flow-chu` với clip có mặt người dẫn, kết `ket-comment` thêm `clip`. Clip kho dài 8 giây, cảnh dùng clip phải ngắn hơn 8 giây.

Tạo giọng bằng `scripts/tao_giong.py`, cấu hình ở `giongAI` trong hồ sơ. Đọc thử một đoạn gồm các từ khó, người dẫn nghe xong mới tạo cả bài:

```bash
python tao_giong.py "<dự án>" --chu "<đoạn thử>" --ra giong/thu-nghiem/thu
python tao_giong.py "<dự án>" --chu-file doc-tts.txt --ra giong/ca-bai
```

Viết bản đọc liền hơi theo mục "Giọng AI nói liền hơi" trong `references/kich-ban.md`. Sau khi tạo, cắt khoảng nghỉ dài mà không đổi tốc độ nói:

```bash
ffmpeg -i giong/ca-bai.mp3 -af "silenceremove=stop_periods=-1:stop_duration=0.25:stop_threshold=-40dB:stop_silence=0.2" -ar 48000 giong/giong-gon.wav
python nghi_dau_phay.py giong/giong-gon.wav loi.txt giong/giong-nghi.wav
python do_nhip.py giong/giong-nghi.wav
```

Tự nghe lại trước khi dựng bằng `python nghe_lai_giong.py <file giọng> <doc-tts.txt>`. Câu nào sai thì chỉ tạo lại câu đó rồi ghép, không tạo lại cả bài. Đoạn mới cắt lặng đầu bằng `-ss` cách tiếng đầu khoảng 0,08 giây, không dùng `silenceremove` ở đầu vì mất phụ âm. Đo khe nghỉ giữa các câu để tìm chỗ đọc dính, khe gần 0 giây là dính. Nghiệm thu báo khoảng lặng quá 0,7 giây thì cắt bớt trong file giọng.

Giữ nguyên từ tiếng Anh để máy tự đọc, chỉ viết lại đúng từ người dẫn nghe thấy sai. Bản đọc đã chốt nằm trong `docDung` của `references/da-chot.json`, `tao_giong.py` tự thay; từ mới bị đọc sai thì thêm vào đó, đừng chỉ sửa tay trong một bản đọc. Số viết bằng chữ; các trường hợp khác xem `references/loi-da-gap.md`. `loi.txt` vẫn ghi đúng chính tả. Máy nghe lại không bắt được lỗi phát âm vì Whisper tự sửa theo gợi ý, nên người dẫn phải nghe bản thử trước khi tạo cả bài. Nhãn AI phải bật khi đăng.

## Video giới thiệu bản thân (BNI, 30 giây)

Câu lệnh ngắn kiểu "Dựng một video giới thiệu bản thân cho tôi theo cấu trúc BNI" là đủ. Không phải video kênh: bỏ dò trùng, đọc thử, ảnh bìa, content, tờ hướng dẫn, ghi sổ video. Làm đúng 5 bước, mục tiêu dưới 10 phút kể cả lúc hỏi đáp:

**1. Tìm bộ não và đọc hồ sơ (1 phút).** Có công cụ `sb_search`, `sb_read`: đọc `00-START`, ghi chú hồ sơ cá nhân và ghi chú sản phẩm, dịch vụ chính; tìm toàn văn tối đa 2 lần. KHÔNG có công cụ đó (học viên thường không nối MCP): chạy `python "<skill>/scripts/tim_bo_nao.py"` TỪ thư mục đang mở (nó dò thư mục đang mở trước, rồi Desktop, Documents, Downloads, ổ D/E/F; chỉ đọc, in JSON). `loai` = `khoi-dong` là Bộ Não AI Khởi Động (thư mục thường, ngăn 01–06): đọc `INDEX.md`, rồi `01_CA_NHAN_VA_THUONG_HIEU/`, `02_SAN_PHAM_VA_BANG_GIA/`, `03_KHACH_HANG_MUC_TIEU/` (giọng văn ở `04_GIONG_VAN_VA_NGON_TU/` nếu có); ảnh, video của chính họ ở `06_KHO_MEDIA_VA_TAI_LIEU_GOC/anh/` và `.../video/` (xem "Sổ media" trong `INDEX.md`): CHÉP (không di chuyển) 2–4 file hợp nhất (ảnh mặt, cửa hàng, sản phẩm) sang `anh-video-cua-toi/` của thư mục kênh. `loai` = `obsidian` thì đọc ghi chú hồ sơ bằng Read/Grep trong kho đó. Không thấy bộ não thì tìm `ho-so-bni.md` trong thư mục kênh. **Thư mục kênh** khi có bộ não: dùng `thu_muc_kenh` trong JSON (`<cha của bộ não>/Video-AI`, NGOÀI bộ não, không bao giờ tạo `du-an/` trong các ngăn); chưa có thì chạy `python cai_dat.py "<thư mục đó>"` để tạo hồ sơ kênh mẫu. Cần đủ 7 ý: tên; nghề và thương hiệu; giúp ai; giải quyết việc gì (2–3 việc); một bằng chứng có số hoặc kết quả thật; khách lý tưởng ("khách tốt cho tôi là…"); liên hệ (Zalo, web). Câu ghi nhớ thì tự viết từ các ý trên. Đang mở trong Bộ Não AI Khởi Động thì vào thẳng việc video, không chạy lời chào nạp bộ não của CLAUDE.md trong đó.

**2. Hỏi MỘT lượt (chỉ khi thiếu).** Gom tất cả trong một tin, đánh số, mỗi câu một dòng, có ví dụ trả lời, bỏ câu đã có trong hồ sơ:
1. Anh/chị tên gì, làm nghề gì, thương hiệu hay tên cửa hàng là gì?
2. Anh/chị giúp ai (khách là ai), giải quyết 2–3 việc gì cho họ?
3. Một kết quả nổi bật có số: bao nhiêu khách, bao nhiêu năm, kết quả cụ thể nào?
4. Khách tốt nhất để người khác giới thiệu cho anh/chị là ai? (càng cụ thể càng tốt, ví dụ "chị em văn phòng 30–45 tuổi bị đau vai gáy")
5. Số Zalo hoặc trang web để ghi ở cuối video?
6. Anh/chị có ảnh hoặc video của chính mình, cửa hàng, sản phẩm không? Có thì thả 2–4 file vào thư mục `anh-video-cua-toi` (em tạo sẵn và đưa đường dẫn). Muốn dùng giọng thật thì quay điện thoại đọc đúng lời em gửi, thả vào cùng thư mục, đặt tên có chữ `doc-loi`. Không có thì em dùng cảnh có sẵn và giọng đọc AI miễn phí.
Chờ trả lời rồi làm tiếp, không hỏi thêm lượt nữa; ý nào họ bỏ trống thì bỏ phần đó cho gọn, không bịa.

**3. Ghi hồ sơ.** Ghi các câu trả lời thành MỘT ghi chú mới (không sửa ghi chú cũ): có công cụ `sb_create` thì tạo "Ho so ca nhan BNI - <tên>" (tự vào `00-Inbox/AI/...`); kho Obsidian không có MCP hoặc không có bộ não thì `ho-so-bni.md` ở thư mục kênh. Báo họ tên ghi chú. Lần sau đọc lại ghi chú này, không hỏi lại. **Bộ Não AI Khởi Động có luật "chưa duyệt không ghi":** vẫn ghi `ho-so-bni.md` ở thư mục kênh (ngoài bộ não) để dựng ngay, KHÔNG ghi vào các ngăn khi chưa được duyệt. Cuối bước 5, trong lúc báo kết quả, đề xuất một bảng ngắn: ý nào thêm vào mục "Nhật ký bổ sung" ở cuối `01_CA_NHAN_VA_THUONG_HIEU/ho_so_founder_va_thuong_hieu.md` (chưa có mục đó thì đề xuất tạo ở cuối file; kèm ngày, không xóa dòng cũ), cất video vào `06_KHO_MEDIA_VA_TAI_LIEU_GOC/video/` tên `yyyy-mm-dd_thuong-hieu_gioi-thieu-bni.mp4`, thêm 1 dòng "Sổ media" trong `INDEX.md` và 1 dòng `NHAT_KY_PHAN_LOAI.md`; họ gõ OK thì mới ghi đúng các chỗ đó.

**4. Viết lời (1 phút).** 5 phần BNI, 13–16 dòng `loi.txt` (mỗi dòng ≤ 28 ký tự, dài hơn là phụ đề rớt chữ xuống dòng), khoảng 90–110 chữ đọc ra 23–27 giây: (1) "Xin chào, tôi là … " tên, nghề, thương hiệu; (2) giúp ai, việc gì; (3) một bằng chứng; (4) "Khách tốt cho tôi là …"; (5) câu ghi nhớ + nhắc lại tên. Chỉ dùng thông tin có trong hồ sơ. `doc-tts.txt` cùng lời, một đoạn, KHÔNG đặt dấu phẩy sau "Xin chào" hay giữa các ý ngắn (máy chặn khi vế trung bình dưới 9 chữ; chỗ nghỉ đã lấy từ dấu phẩy của `loi.txt`), vế dài nối bằng "và", "để", "mà", số viết bằng chữ, có ít nhất một dấu chấm than; `loi.txt` đặt dấu phẩy ở chỗ chuyển ý để `nghi_dau_phay.py` chèn nghỉ. Viết `bni.json` (khuôn trong đầu `scripts/bni.py`): `phan` là số dòng của 5 phần; chữ trên hình ngắn (tiêu đề ≤ 14 ký tự mỗi dòng, `ghiNho` ≤ 22 ký tự); `canh` chọn 3 clip hợp nghề cho vai mở, bằng chứng, kết từ danh mục cảnh (nhóm viet-nam, nganh-nghe, mặc định nền màu dịu K055, K049 và K082 sân thượng hoàng hôn, hợp mọi nghề; văn phòng: K076; phòng khám: K064; bán lẻ: K068. Kho chưa có cảnh spa, làm đẹp, ăn uống: khuyên học viên thả thêm ảnh cửa hàng, sản phẩm thật của mình vào `anh-video-cua-toi`, đẹp hơn mọi cảnh kho), người làm công nghệ mới dùng cảnh công nghệ (N031, N047); mỗi việc ở thẻ "Tôi giúp" nằm trên một dòng `loi.txt` riêng (2 việc chung một dòng thì thẻ sau sáng trễ); viết `doc-tts.txt` trước rồi cắt `loi.txt` từ đúng chữ đó (`bni.py` chặn khi lệch dưới 85%); `ghiNho` ≤ 18 ký tự; giọng AI chọn theo người: nam `vi-VN-NamMinhNeural`, nữ `vi-VN-HoaiMyNeural` (sửa `giongAI.voice_id` trong `ho-so-kenh.json`); `lienHe` từ 2 chữ trở lên (một chữ thì khung hiện "XEM BÌNH LUẬN GHIM").

**5. Dựng và chấm bằng agent, không hỏi duyệt (4–6 phút).** Giao agent `video-dung` (kèm đường dẫn hồ sơ, thư mục kênh, có ảnh hay không) dựng theo đoạn dưới; xong giao agent `video-cham-diem` chấm độc lập. Phiếu SỬA LẠI thì gửi lại `video-dung` sửa, tối đa 3 vòng. Báo người dùng: đường dẫn video, tên ghi chú hồ sơ, phiếu chấm, thời gian. Agent chưa có trên máy thì chạy `python cai_dat.py` (tự chép agent) hoặc tự làm đoạn dưới rồi chấm theo thang trong `agents/video-cham-diem.md`.

Đoạn dựng (agent `video-dung` làm, 3–4 phút): Dự án `<thư mục kênh>/du-an/<số>-bni-<tên>/`, rồi:
```bash
python bni.py "<dự án>"
```
Script tự: nhận ảnh, video trong `<thư mục kênh>/anh-video-cua-toi/` (ảnh tĩnh thành clip chuyển động nhẹ, video cắt 8 giây không tiếng) làm cảnh mở, bằng chứng, kết; không có thì chế độ không mặt (`loai.txt` = `gioi-thieu khong-mat`, chặn clip thư mục "CO MAT", chỉ lấy cảnh thật không người, chặn cảnh hoạt hình); tạo giọng (`giongTuQuay` trong `bni.json` thì lấy tiếng video tự quay, không thì `giongAI` của hồ sơ; học viên chưa có giọng nhân bản đặt `"giongAI": {"provider": "edge", "voice_id": "vi-VN-HoaiMyNeural"}` hoặc `vi-VN-NamMinhNeural`, cần `pip install edge-tts`); lập `canh.json`; chạy `dung.py --het`. Lỗi chữ tràn thì rút gọn chữ trong `bni.json` rồi chạy lại. Xem `to-soat.jpg` rồi giao `render/thanh-pham.mp4`. Máy học viên mới chưa có kho cảnh, kho nhạc: script tự tạo nền màu dịu (NEN1–3) và dựng chỉ có giọng (in ⚠, không dừng); hồ sơ kênh còn tên mẫu "TÊN KÊNH" thì tự điền thương hiệu. Có gói `KHO-HOC-VIEN.zip` (Drive của lớp: 226 cảnh AI không người, 3 bài nhạc Pixabay, 7 tiếng ngắn) trong Downloads, Desktop, Documents hoặc cạnh thư mục kênh thì `cai_dat.py`, `bni.py`, `edit.py` tự giải nén vào thư mục kênh và khai nhạc vào hồ sơ (`scripts/nhap_kho.py`); học viên chỉ cần tải gói về Downloads. Lần dựng đầu Remotion tải trình duyệt khoảng 120 MB, chậm thêm 1–2 phút là bình thường.

Luật đi kèm (máy kiểm): `loai.txt` có `gioi-thieu` thì `tao_giong.py`, `nghiem_thu.py` bỏ luật câu kết của kênh, vẫn giữ cách đọc, luật 9, cảm xúc, độ dài vế. Cảnh cho video giới thiệu phải thật, sang, hợp người làm nghề (văn phòng, góc làm việc, màn hình số liệu, thành phố Việt Nam); KHÔNG dùng hoạt hình, đồ chơi tí hon, đất sét, 3D cartoon, robot chạy băng chuyền như xe lửa (người dẫn chê 24/11/2026); `lap_canh.py` chặn clip có ghi chú "tí hon", "đất sét", "hoạt hình", "cartoon", "đồ chơi", nên thêm clip mới vào kho thì ghi đúng kiểu ở cột ghi_chu. Tự đặt cảnh bằng tay thì nhớ cách đếm mốc trong `mo-hinh-canh.md`.

## Edit video từ file quay (câu "Edit video <tên file> cho tôi", có thể kèm "dài 30 giây")

Không hỏi duyệt từng bước. Mục tiêu bản 30 giây: khoảng 10 phút kể cả chấm. Tìm file người dùng nói (thư mục làm việc, Downloads, Desktop; trùng tên thì lấy file mới nhất và nói rõ đã lấy file nào). Câu có "30 giây", "ngắn", "reels" thì `--dai 30` (hoặc số giây họ nói); không nói độ dài thì giữ trọn lời (bỏ `--dai`). Rồi:

0. Thư mục kênh: có bộ não thì chạy `python "<skill>/scripts/tim_bo_nao.py"` từ thư mục đang mở và dùng `thu_muc_kenh` (không bao giờ đặt trong bộ não); chưa có `ho-so-kenh.json` ở đó thì `python cai_dat.py "<thư mục kênh>"`. Không có bộ não thì dùng `Video-AI` trong thư mục đang mở.
1. **Bước 1, nghe và chia câu (1 phút):** `python edit.py "<thư mục kênh>" "<file quay>" [--dai 30]`. Script tự cắt viền đen (màn ngang trong khung dọc thì đặt giữa, nền mờ), nghe lời (đoạn Whisper lạc tiếng thì tự nghe lại), BỎ ậm ừ, lần nói hỏng (cả khi có "ờ" xen giữa), chữ lặp liền ("nhân viên nhân viên"), nói lại giữa câu, lặp ở chỗ nối, câu Whisper bịa; ghi `bo-cat.txt`; chia lời thành câu đánh số trong `cau.txt` (giờ, số giây, chữ) và một `chon.json` nháp, rồi DỪNG. Lời đã nghe lưu ở `nghe.json`, chạy lại không phải nghe lại.
2. **Cảnh của chính người dùng (nếu có):** `anh-video-cua-toi` có ảnh, video (hoặc ngăn 06 của bộ não thì CHÉP sang đó) thì `python canh_toi.py "<dự án>"` ra mã TOI1…, ưu tiên dùng trong `minhHoa` trước clip kho.
3. **Bước 2, Claude tự soạn `chon.json` (1–2 phút, không hỏi ai), giao agent `video-dung` hoặc tự làm:** đọc `cau.txt`, ghi:
   - `tieuDe`: "DÒNG 1|DÒNG 2", mỗi dòng ≤ 14 ký tự, đúng ý người nói ở câu đầu (đọc trong `cau.txt`, không cần nghe thử riêng).
   - `doan`: các câu giữ, đúng thứ tự gốc (không đảo). Bản 30 giây (25–35 giây): câu chào hoặc móc câu nêu chủ đề → 2–3 ý chính rõ nhất (định nghĩa, ví dụ cụ thể, kết quả, con số) → câu kết trọn ý. Bỏ câu rào đón, lặp ý, bỏ dở. Chỉ lấy một khúc của câu dài thì thêm `"chu": "<chép đúng chữ khúc đó từ cau.txt>"`; khúc phải là ý trọn.
   - `minhHoa` cho 2–4 khúc (bản 30 giây: 2–3; video 1–2 phút: 3–5), chiếm khoảng 30–50% thời lượng, KHÔNG ở câu đầu và câu cuối, hai cảnh minh họa không liền nhau:
     - Câu nêu khái niệm, hình ảnh: `{"loai": "flow-chu", "ten": "<TOI1 hoặc mã clip>", "tren": "...", "duoi": "..."}`. Clip kho lấy trong `kho-canh/danh-muc-canh.csv` có `nhom`, `ghi_chu` khớp ĐÚNG ý câu VÀ hợp nghề người nói, mỗi clip một lần; kho không có cảnh hợp nghề (làm bánh, spa, nông sản...) thì KHÔNG nhét cảnh công nghệ lạc đề: dùng TOI hoặc thẻ đồ họa bên dưới, và báo người dùng thả 3–5 ảnh, clip ngắn cửa hàng, sản phẩm vào `anh-video-cua-toi` rồi gõ lại lệnh. Chữ ≤ 14 ký tự lấy từ lời nói ở 2 giây đầu cảnh (chữ hiện ngay khi vào cảnh). Script tự cắt cảnh clip ≤ 7,5 giây.
     - Câu liệt kê việc, bước, lợi ích: `{"loai": "danh-sach-buoc", "tren": "...", "buoc": [{"ten": "..."}...]}` tối đa 5; mục viết đúng chữ người nói để script tự đặt mốc sáng đúng lúc nói.
     - So sánh hai phía: `hai-phe`, `truoc-sau`; số liệu: `nguoi-so`; nói chuyện với AI: `khung-chat`. Trường xem `references/mo-hinh-canh.md`; thiếu `moc` thì script tự đặt. Một cảnh phủ luôn câu kế tiếp (danh sách nói qua 2 câu): thêm `"gop": 1`.
     - Mọi chữ trên cảnh (kể cả `tren`, `duoi`) chỉ lấy từ lời của khúc đã chọn, không lấy từ câu đã bỏ.
   - `sua`: chữ Whisper nghe sai → đúng, ví dụ `{"skin": "skill", "đất đỏ": "đắt đỏ"}`. Sửa ở đây, KHÔNG sửa tay `loi.txt` (số dòng và mốc cảnh phải khớp). Không thêm bớt ý; chữ nghe vô nghĩa mà không chắc thì giữ, báo người dùng giây để họ tự nghe. Tên riêng trong `sua` và `tieuDe` tự vào `goi-y.txt` để nghiệm thu nghe đúng (thêm `goiY` nếu cần).
   Rồi `python edit.py "<dự án>" --chon --het`: tự tính dòng phụ đề, mốc cảnh, thẻ tiêu đề hiện đúng lúc nói chữ tiêu đề, điểm cắt giữa khe (không cụt chữ cuối), dựng, nghiệm thu, gắn nhận diện kênh. ⚠ lệch độ dài thì thêm, bớt câu rồi chạy lại.
4. Còn ✘: lặp hoặc nói hỏng thì bỏ câu đó khỏi `chon.json` hoặc dùng `chu` cắt bớt rồi chạy lại bước 2; chữ tràn thì rút gọn chữ trong `minhHoa`. Tối đa 3 vòng. Xem `to-soat.jpg` bằng mắt.
5. Giao agent `video-cham-diem` chấm; báo người dùng đường dẫn, thời lượng, câu đã chọn và cảnh minh họa, `bo-cat.txt` tóm tắt, phiếu chấm, thời gian từng chặng.

## Luật nghiệm thu (bắt buộc)

- Chỉ bàn giao khi `nghiem_thu.py` báo ĐẠT. Còn ✘ thì tự sửa, xuất lại, chạy lại, không gửi bản lỗi.
- Sau 3 vòng vẫn còn ✘ thì báo rõ lỗi gì và đã thử gì.
- ĐẠT rồi vẫn phải tự mở `to-soat.jpg` xem bằng mắt: chữ tràn, mặt bị che, thẻ đè phụ đề, sai dấu. Watermark chỉ có trong `thanh-pham.mp4`: xem thêm vài khung của file này để chắc watermark không đè phụ đề hay thẻ.
- Không hạ ngưỡng để cho qua. Đổi thước đo thì phải thử trên một bản lỗi thật xem còn bắt được không.
- Khi báo, nói rõ phần máy chưa kiểm được: chưa nghe bằng tai, chưa xem trọn từng khung.

Các lỗi đã gặp và cách tránh: `references/loi-da-gap.md`.

## Bàn giao

Chép vào thư mục chủ đề bên trong `thanhPham` của hồ sơ kênh, cùng chỗ file quay nếu đã có thư mục đó:

- `<số>-<tên>.mp4`: video, chép từ `render/thanh-pham.mp4` (đã có watermark, intro, outro)
- `<số>-<tên>-bia.jpg`: ảnh bìa
- `<số>-<tên>-content.md`: content đăng và bảng nguồn
- `<số>-<tên>-huong-dan.pdf`: tờ hướng dẫn để link ở bình luận ghim, có liên hệ của kênh

Bản ngang 16:9, chỉ làm khi người dùng cần đăng YouTube thường hoặc chạy quảng cáo khung ngang: `python xuat_ngang.py "<dự án>"` ra `render/thanh-pham-ngang.mp4` (khung dọc giữ nguyên ở giữa, hai bên là chính video làm mờ), giao thêm `<số>-<tên>-ngang.mp4`. Không cắt khung dọc thành ngang vì sẽ mất phụ đề và thẻ.

File cũ đang mở trên máy người dùng thì không ghi đè: lưu bản mới thành `<tên>-v2.mp4`, báo họ đóng trình phát để đổi tên; bản cũ cất vào `ban-cu/`. Cùng một chủ đề có hai độ dài thì giao cả hai, ghi vào content để đăng thử so số liệu.

Ghi sổ video (bắt buộc, kể cả bản dài, bản làm lại):

```bash
python ghi_so_video.py "<thư mục kênh>" "<dự án>" --tu-khoa "Tên công cụ; tên kho; từ khóa chủ đề" --nguon "<link chính>"
```

Từ khóa ghi đủ tên riêng người dẫn có thể gõ lại sau này (tên công cụ, tên hãng, khái niệm), để lần sau `tim_trung.py` bắt được.

Rút kinh nghiệm tốc độ (bắt buộc, ngay sau ghi sổ):

```bash
python rut_kinh_nghiem.py "<dự án>" --ghi "nguyên nhân chậm nếu có"
```

Script đếm số lần làm lại (tạo giọng, vòng ảnh tĩnh, xuất), so phút cho mỗi 10 giây thành phẩm với trung vị 5 video trước, ghi `<kênh>/so-toc-do.csv`. Chuẩn: mỗi bước 1 lần. Lần nào làm lại thì ghi nguyên nhân vào `references/loi-da-gap.md`; lỗi đã có trong sổ mà vẫn lặp thì khóa bằng code, thêm bài vào `hoi_quy.py`. Mục tiêu: video sau nhanh hơn video trước cùng loại, chất lượng không giảm (nghiệm thu vẫn ĐẠT, không hạ ngưỡng nào để nhanh hơn).

Báo người dùng: đường dẫn, thời lượng, kết quả nghiệm thu, thời gian làm từng khâu, so với video trước (kết quả `rut_kinh_nghiem.py`) (`thoi-gian.csv` và giờ file), những số cần xem lại trước khi đăng, những việc chỉ họ làm được.

## Cập nhật skill

Hai cổng chặn trước khi tốn thời gian: `tao_giong.py` chặn bản đọc có vế trung bình dưới 9 chữ (máy sẽ đọc rời), nhắc khi dưới 10; `lap_canh.py` đo tiêu đề bằng phông thật, chặn chữ sẽ tràn dòng trước khi bundle.

Mỗi góp ý của người dùng hay lỗi tự sửa được thì đưa ngay vào skill: tài liệu trong `references/`, mã trong `scripts/` hoặc `engine/`, hoặc thêm một bước kiểm cho máy bắt được. Ghi lỗi vào `references/loi-da-gap.md`. Chạy lại `scripts/hoi_quy.py` trong cùng lần đó.
