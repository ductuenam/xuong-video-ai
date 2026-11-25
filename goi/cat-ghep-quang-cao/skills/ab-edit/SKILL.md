---
name: ab-edit
description: Skill AB Edit nâng cao (Windows), cho người muốn tự điều khiển từng khâu: dựng video quảng cáo hoàn chỉnh từ file quay người nói thật có duyệt từng bước (bảng GIỮ/BỎ, kịch bản hình 6 phần, chỉnh màu da, lọc ồn, khối chữ theo thương hiệu, cảnh trám, soát chính sách quảng cáo), cắt livestream dài thành nhiều video ngắn 45–180 giây trọn ý, và tạo 3–5 biến thể khác hook từ 1 video Final để test quảng cáo. Xuất 9:16 / 4:5 / 1:1 / 16:9, chấm độc lập bằng agent video-cham-diem. Dùng khi người dùng nói "cắt livestream", "cắt clip từ live", "làm biến thể", "xào nấu thêm video", "đổi hook", "dựng video ads", "dựng video quảng cáo có duyệt từng bước", "edit video theo thương hiệu, cho tôi duyệt từng bước", hoặc thả file vào 02-source-tho của video-studio. KHÔNG dùng cho câu ngắn "Edit video <tên file> cho tôi" hay video giới thiệu bản thân BNI: hai câu đó thuộc skill video-ngan-nguoi-noi.
---

# Skill AB Edit (`ab-edit` · v3 · Windows)

Skill dựng và edit video của An Bình AI. Ba chế độ nâng cao: A dựng video quảng cáo hoàn chỉnh từ file quay thô (có duyệt từng bước khi người dùng muốn), B cắt livestream thành nhiều video ngắn, C tạo biến thể từ 1 video Final.

## Phân việc với skill `video-ngan-nguoi-noi`

Câu ngắn "Edit video <tên file> cho tôi" (một file quay, ra video dọc có phụ đề, nhạc nhẹ) và video giới thiệu bản thân BNI thuộc skill `video-ngan-nguoi-noi` (lệnh `edit.py`, `bni.py`, agent `video-dung` dựng, `video-cham-diem` chấm). Skill này chỉ nhận việc nâng cao: cắt livestream (B), làm biến thể quảng cáo (C), dựng video quảng cáo theo thương hiệu có duyệt từng bước (A).

## Chế độ tự động (khi người dùng giao việc nâng cao mà không đòi duyệt)

KHÔNG hỏi duyệt từng bước. Làm trọn theo trình tự:

1. **Tìm file**: tìm `<tên file>` trong thư mục đang mở, `video-studio/02-source-tho/` và các thư mục con (khớp gần đúng tên, bỏ dấu). Không thấy thì mới hỏi đúng một câu: file nằm ở đâu.
2. **Đoán mặc định, không hỏi**: có người nói quay thật → chế độ A; file dài hơn 20 phút → chế độ B. Khổ hình theo file gốc (quay dọc → 9:16, ngang → 16:9). Thương hiệu = `config.json › brand_mac_dinh` (hoặc `brands/<tên>.json` duy nhất mà người dùng đã tạo). Phụ đề karaoke cho video ngắn. Nhạc nền không lời, thấp hơn giọng 22 dB.
3. **Tự dựng** theo đúng skill này (chế độ A/B/C bên dưới) cho tới khi `scripts/nghiem_thu.py` báo ĐẠT. Việc dài (nhiều clip livestream) thì có thể giao một agent con làm theo skill này, kèm đường dẫn file, chế độ, khổ, thương hiệu, thư mục dự án.
4. **Gọi agent `video-cham-diem`** giao CHỈ: đường dẫn video thành phẩm, file gốc, `loi.txt`/phụ đề nếu có. Không kể cho người soát là mình đã làm gì. Agent trả phiếu chấm ĐẠT hoặc SỬA LẠI kèm giây.
5. **SỬA LẠI** → sửa đúng từng lỗi trong phiếu, xuất bản mới `-v2`, `-v3` (không ghi đè bản cũ), rồi gọi lại `video-cham-diem` (một agent mới, không dùng lại phiên cũ). Tối đa 3 vòng. Sau 3 vòng vẫn lỗi thì dừng, báo rõ lỗi gì, đã thử gì.
6. **Báo người dùng** (ngắn, lời thường): đường dẫn video, thời lượng, những gì đã cắt/sửa, **phiếu chấm cuối của `video-cham-diem`** (dán nguyên bảng), phần máy chưa kiểm được (chưa nghe bằng tai), những con số trên màn hình cần người dùng xác nhận trước khi đăng.

Không hỏi giữa chừng những việc tự quyết được (chọn lần nói, chọn nhạc, chọn cảnh trám, cỡ chữ). Ở chế độ tự động, các "cửa duyệt" của bản thủ công bên dưới được thay bằng: tự lập bảng (GIỮ/BỎ, số – nguồn, tờ ảnh tĩnh), tự soát theo bảng đó, và đính bảng vào báo cáo cuối để người dùng xem lại. Số liệu không có nguồn thì KHÔNG đưa lên màn hình (bỏ đi), không bịa.

Người dùng nói rõ "cho tôi duyệt từng bước" thì mới dùng các cửa duyệt thủ công.

## Đọc trước khi làm
1. `config.json` — thư mục studio (mặc định `video-studio` trong thư mục làm việc), Python, Chrome. Máy mới/lần đầu: `python scripts/kiem_tra_may.py`.
2. `references/chuan-dung-video-ads.md` (chuẩn hình/âm/kịch bản 6 phần, xào nấu) → `references/vpcs.md`.
3. Thương hiệu = `brands/<tên>.json`. Chưa có → chép `brands/_mau.json` thành `brands/<tên>.json` và điền; ở chế độ tự động thì dùng `_mau.json` (không CTA, không logo). `an-binh-ai.json` là ví dụ một hồ sơ đã điền đủ.

Python: đặt `PYTHONUTF8=1`, chạy script trong `scripts/`.

## Thư mục studio (`config.json › studio`)
`01-video-mau` mẫu tham khảo · `02-source-tho` **file gốc — chỉ đọc** · `03-kich-ban` · `04-giong-doc` · `05-tai-nguyen` (fonts, nhac-nen, sfx, logo, broll) ·
`06-thanh-pham` video xuất · `07-du-an/<tên>` file làm việc của từng dự án (`python scripts/tao_du_an.py <tên> --brand <b> --che-do dung|livestream|bien-the`) · `_backup`.

**Kho tài nguyên chung** (`config.json › kho_tai_nguyen`, mặc định thư mục `kho-tai-nguyen` trong thư mục làm việc — học viên tải từ kho tài nguyên Drive của lớp): nhạc nền, SFX, video cảnh trám, font, icon. Chép file cần dùng vào `07-du-an/<tên>`, không sửa/xoá trong kho. Có Obsidian thì đặt `obsidian_vault` rồi chạy `python -I scripts/kho_tai_nguyen.py` để lập danh mục.

**Chọn nhạc theo THẺ NHẠC, không đoán theo tên bài** (tên bài "piano" có thể là country có lời). `scripts/phan_tich_nhac.py` chấm BPM, cảm xúc, có lời hay không. **Âm lượng nhạc/SFX tính theo dB đo được, không dùng tỉ lệ cố định**: chuẩn giọng −16 LUFS trước khi trộn, nhạc thấp hơn giọng 22 dB, đỉnh SFX ≈ −12 dBFS. Máy chấm vẫn có thể sai — báo người dùng nghe lại bài đã chọn.

## Luật làm việc (bắt buộc)
- **Không ghi/xoá trong `02-source-tho`.** Sao lưu vào `_backup` trước khi ghi đè. **Không bao giờ xoá video/âm thanh/ảnh** — kể cả file tạm dạng media (dùng `chung.xoa_tam`, tự dồn vào `_backup`). Bài học: script dọn rác từng xoá mất video thành phẩm.
- **Không tự đăng, không upload, không chia sẻ.** Xuất xong báo đường dẫn để người dùng xem.
- Video có người nói: dùng **giọng thật**. Cần giọng AI (lồng tiếng, đổi câu hook) thì dùng giọng miễn phí edge-tts (`vi-VN-HoaiMyNeural`, `vi-VN-NamMinhNeural`) hoặc ElevenLabs trên giao diện web do người dùng tự đăng nhập; không nhập mật khẩu thay.
- **Nhạc nền luôn KHÔNG LỜI** (instrumental). Tên bài ghi ca sĩ hoặc có "(feat.)", "vocal", "lyric" → bỏ.
- Soát chữ bằng `scripts/vpcs_check.py` (từ cấm + quy tắc gọi tên thương hiệu) trước khi quay chữ; soát hình bằng mắt trên bảng khung hình.
- **Luật cắt và chữ:**
  1. **Cắt lời chỉ được BỎ** — không đảo thứ tự câu, không sửa/ghép lời người nói (đảo là người nói "nói" điều họ chưa nói). Ngoại lệ duy nhất: chế độ C đưa 1 câu có thật lên làm hook — ghi rõ câu gốc ở giây nào và không làm đổi nghĩa.
  2. **Bảng GIỮ / BỎ**: sau `edl_tool propose`, lập bảng câu GIỮ / BỎ (lý do: lặng, nói lại, nói hỏng). Chế độ tự động: tự quyết theo bảng, đính bảng vào báo cáo. Chế độ thủ công: người dùng duyệt chữ trước khi ráp.
  3. **Mọi con số lên màn hình phải có nguồn** (giá, %, ngày, số lượng, số năm, chứng nhận…): lấy từ lời nói trong file, kịch bản, `brand.json` — không viết theo trí nhớ. Không có nguồn thì bỏ.
  4. **Tờ ảnh tĩnh trước khi render**: xuất 1 khung đại diện mỗi cảnh, ghép thành 1 tờ (đánh số cảnh + giây), tự soát (chữ đè mặt, chữ tràn, sai dấu) rồi mới render cả video. Sửa 1 cảnh thì chỉ xuất lại ảnh cảnh đó.
  5. **Chỉ bàn giao khi `scripts/nghiem_thu.py` báo ĐẠT và `video-cham-diem` chấm ĐẠT.** Còn ✘ thì tự sửa, xuất lại, chạy lại; không hỏi, không gửi bản lỗi. Không hạ ngưỡng để cho qua.
- Font, nhạc, cảnh trám phải có nguồn hợp lệ; không tải từ nguồn không rõ. Dữ liệu khách chỉ dùng trong dự án, không đưa vào skill.
- Báo tiến độ dạng "Bước x – đang làm gì – kết quả". Người dùng không biết code: giải thích bằng lời thường, không dán lệnh dài.

## 3 chế độ
Có **người nói quay thật** → A · **buổi live dài** → B · có **1 video Final** cần nhân bản → C.
Video **không quay, toàn đồ họa + giọng đọc** → dùng skill `video-ngan-nguoi-noi` (mục "Không quay") hoặc `video-ngan-hyperframes`.

### A. Dựng video hoàn chỉnh (`--che-do dung`)
1. Nhận file: source, video mẫu (nếu có), sản phẩm, từ cần né, khổ hình. Tạo dự án. **Kiểm file nhận**: `tu_kiem.py nhan <source/cảnh trám> --sua 07-du-an/<tên>`
   (keyframe cách > 2s hoặc tốc độ khung không đều → tạo `<tên>-lamviec.mp4` 1 keyframe/giây, dựng bằng bản này; file gốc giữ nguyên).
2. Phân tích mẫu (nếu có): bảng khung hình `ffmpeg fps=1/2,tile` + Whisper lời → công thức, nhịp, kiểu chữ.
3. Cắt lời: `whisper_vi.py` → `edl_tool.py propose` (bỏ lặng, bỏ câu nói lại) → bảng GIỮ/BỎ (luật 2) → ráp → `edl_tool.py verify` nghe lại bằng Whisper. Chỉ bỏ, không đảo (luật 1).
4. Kịch bản hình 6 phần (hook, vấn đề, giải pháp, bằng chứng, ưu đãi, kêu gọi) + bảng số – nguồn (luật 3).
5. Master người nói (`master_nguoi_noi.py`: màu, cà da, mịn da vùng mặt, lọc ồn, −16 LUFS); khung trung ↔ cận bằng cắt cứng, không zoom.
6. Cảnh trám đúng từ khoá, đồ hoạ HTML (`scripts/do-hoa/`), khối chữ (`scripts/titles/template.html` qua `make_titles.py`) hoặc phụ đề karaoke theo `brand.phu_de`. Phụ đề karaoke/đồ họa động: dùng engine Remotion của skill `video-ngan-nguoi-noi` (`engine/`) hoặc `video-ngan-hyperframes`; máy chưa có Remotion thì đốt phụ đề bằng FFmpeg (ASS) — đặt chữ tránh vùng mặt (`tim_mat.py`).
7. Ráp timeline + nhạc nền → tờ ảnh tĩnh từng cảnh (luật 4) → xuất → **`tu_kiem.py xuat <video> --brand <b> --moc <giây từng cảnh>`**
   (khung đen/đứng/cháy trắng, LUFS theo `brand.am_thanh.giong_lufs`, đỉnh, lặng chết, tờ soát khung → `<video>-soat/`). Còn ✘ thì sửa, xuất lại, kiểm lại
   đến khi sạch, rồi **`nghiem_thu.py` (luật 5)**. **Tự mở tờ soát xem bằng mắt** (chữ đè mặt, chữ sai/tràn, bố cục), rồi giao `video-cham-diem`.

### B. Livestream → nhiều video ngắn (`--che-do livestream`)
1. `tu_kiem.py nhan` file live (live hay thiếu keyframe/VFR → `--sua`) → Whisper toàn bộ buổi live → bản lời có giây.
2. Tìm đoạn **trọn ý** dài `brand.livestream.do_dai_giay` (mặc định 45–180s): câu mở đủ hút trong 3s đầu, có nội dung, có kết; không cắt giữa câu.
3. Chấm điểm (hook · giá trị · trọn ý · rủi ro VPCS) và gắn trụ nội dung (`brand.livestream.tru_noi_dung`) → bảng đề xuất. Chế độ tự động: dựng 3 đoạn điểm cao nhất, đính bảng cho người dùng chọn thêm.
4. Tờ ảnh tĩnh mỗi clip (khung hook + 1 khung giữa). Dựng hàng loạt: cắt lặng, mặt vào giữa khung dọc, phụ đề karaoke, tiêu đề hook 3s đầu, CTA theo `brand.cta`, kèm caption + hashtag. Mỗi clip chạy `tu_kiem.py xuat` (mã thoát 1 = có lỗi ✘) và qua `video-cham-diem`.

### C. Biến thể từ 1 video Final (`--che-do bien-the`)
1. Giữ thân bài; đề xuất 3–5 hook (câu khác trong source / lần nói chưa dùng / hook chữ + cảnh mở khác) và bộ cảnh trám khác.
2. Neo mọi cảnh trám/chữ theo **giây trong source** (đổi EDL là mọi thứ tự dời theo) → tờ ảnh khung mở của `V1…V5` → render hàng loạt → `tu_kiem.py xuat` từng bản.
3. Xuất kèm `bien-the.csv` (mã, hook, cảnh mở, cảnh trám, nhạc) để đối chiếu CTR/CPA khi chạy ads.

## Bài học dựng thật
- **Đo đủ lời:** nghe CẢ BÀI rồi so với phụ đề, không nghe từng cụm ngắn trên tiếng đã trộn nhạc. Tỉ lệ khớp một mình không đủ: bản cố tình mất 8 giây vẫn đạt 87%, nên phải đo thêm đoạn mất liền nhau (< 8 từ). Truyền tên riêng của video qua `--goi-y` để Whisper nghe đúng. Nghi cụt chữ thì đo năng lượng trên file GỐC tại điểm ra, không đo trên master vì bộ nén đã nâng tiếng.
- **Khoảng lặng:** điểm vào phải lấy theo từ đầu tiên nghe được, không theo đảo năng lượng (có thể chỉ là tiếng ồn phòng). `nghiem_thu.py` đo bằng VAD, tối đa 0,7 s. Không tự tăng tốc giọng: 1,12 lần đã bị chê nhanh.
- **Từ lặp ở chỗ cắt:** nghe cả bài thì Whisper gộp mất từ lặp, phải nghe riêng từng đoạn cắt (`nghiem_thu.py` làm việc này). `edl_tool propose` chỉ là gợi ý, phải dò theo khoảng lặng rồi nghe từng đảo tiếng. Whisper có thể nghe ảo câu lặp → luôn `verify`.
- **Nguồn nhỏ (webcam 1080p ngang cắt dọc):** dùng `master_nguoi_noi.py --net 1.778` (không mịn da, không tăng sáng, phóng sẵn + làm nét). Bộ lọc mặc định làm da sáng và mất chi tiết ("lóa mờ"). Quay điện thoại dọc sẽ nét hơn hẳn.
- **Remotion phải xuất đúng màu:** `--color-space=bt709 --pixel-format=yuv420p --image-format=jpeg --jpeg-quality=100 --crf=14`; mặc định ra `yuvj420p/pc/bt470bg`, trình phát hiển thị bạc. Đặt video theo điểm ảnh nguyên (`Math.round`).
- **Ghép theo master, không theo bản nghe thử:** lấy giờ phụ đề từ chính `master.mp4`.
- **Cảnh AI (Flow, Veo…):** giữ nhãn "Cảnh AI minh họa" ở góc thay vì xóa, để ghi rõ cảnh do AI tạo.
- **Cảnh trám cắt từ video mẫu: soát khung ĐẦU và khung GIỮA từng clip** — điểm cắt sát chỗ chuyển cảnh dính 2–4 khung cảnh trước; lùi điểm vào 0,2–0,3s. Cảnh tiền mặt/đồng xu → bỏ (VPCS hình).
- FFmpeg cần driver NVIDIA đủ mới cho NVENC; máy không có GPU NVIDIA → `chung.ma_hoa()` tự dùng libx264 (chậm hơn).
- Giao CapCut (khi người dùng muốn tự chỉnh tiếp): 3 lớp + nhạc — L1 người nói, L2 cảnh trám ProRes 4444 nền trong suốt, L3 khối chữ ProRes 4444; kéo hẳn sang trái để chặn đúng mốc 0.

## Tệp
- `config.json` · `brands/` (`_mau` mẫu trống, `an-binh-ai` ví dụ đã điền, `thu-mau-xanh` thử đổi màu)
- `scripts/` — `chung.py` (đường dẫn, FFmpeg, luật an toàn), `kiem_tra_may.py`, `tao_du_an.py`, `vpcs_check.py`, `whisper_vi.py`, `edl_tool.py`, `master_nguoi_noi.py`, `tim_mat.py` (MediaPipe + `models/`), `make_titles.py`, `tu_kiem.py` (kiểm file nhận + tự kiểm sau xuất), `nghiem_thu.py` (cổng cuối: lặp từ, đủ lời, khoảng lặng, màu, độ nét, logo góc), `phan_tich_nhac.py`, `kho_tai_nguyen.py`, `titles/template.html`, `do-hoa/` (thẻ feedback, thẻ tự kiểm tra, khung 3 sản phẩm), `vendor/quay-html.mjs` (quay trang HTML thành video, Chrome headless).
- `references/` — chuẩn dựng video ads, VPCS.
- Agent chấm đi kèm (trong `.claude/agents/`): `video-cham-diem` (chấm độc lập, phiếu ĐẠT/SỬA LẠI kèm giây).
