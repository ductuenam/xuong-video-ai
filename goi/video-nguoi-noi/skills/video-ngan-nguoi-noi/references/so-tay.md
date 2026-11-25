# Sổ tay vận hành

Dành cho người nhận bàn giao. Đọc một lần để thiết lập, sau đó chỉ cần nói việc với Claude.

## Quy trình này làm gì

Bạn đưa chủ đề hoặc một video mẫu. Claude viết kịch bản đã kiểm nguồn, báo cảnh AI cần tạo, nhận file bạn quay rồi dựng thành video, tự kiểm lỗi, làm ảnh bìa và viết content đăng.

| Bạn làm | Claude làm |
|---|---|
| Duyệt kịch bản | Bóc video mẫu, kiểm số liệu, viết kịch bản |
| Tạo cảnh trên Flow khi được nhắc | Đối chiếu kho, soạn prompt |
| Quay, gửi file gốc | Chọn lần nói, dựng, nghiệm thu, sửa lỗi |
| Duyệt bìa | Tạo hình qua API, ghép chữ, soát |
| Xem bản cuối, tự đăng | Viết content, gom vào một thư mục |

Thời gian đo được, máy có GPU NVIDIA: video quay thật 2 phút khoảng 5 phút máy chạy, 26 phút cả việc chọn lần nói và lập cảnh khi làm lần đầu. Video giọng AI 45 giây đến 2 phút: 8 đến 12 phút từ lúc nhận video mẫu đến bàn giao đủ video, bìa, content và tờ hướng dẫn.

## Cần có

| Thứ | Ghi chú |
|---|---|
| Claude Code hoặc ứng dụng Claude trên máy tính | Claude in Chrome nếu muốn Claude thao tác Flow giúp |
| Python 3.10 trở lên, Node.js LTS, FFmpeg | `cai_dat.py` sẽ kiểm, tự cài trình duyệt để chụp và quay trang web |
| Windows 10/11 | Đã chạy thật trên Windows 11. Hệ khác chưa thử |
| GPU NVIDIA | Không bắt buộc nhưng nhanh hơn nhiều |
| Tài khoản Google Flow | Có gói trả phí để đủ credit tạo clip |
| Tài khoản Vibi (không bắt buộc) | Làm video không quay bằng giọng nhân bản. Khi kiểm tháng 11/2026 là 1 credit mỗi ký tự, nên xem lại bảng giá. Chỉ nhân bản giọng của chính mình hoặc người đã đồng ý bằng văn bản |
| Google Cloud có bật thanh toán | Tạo ảnh bìa qua API, khoảng 900 đồng một ảnh 1K. Service account cần vai trò `roles/aiplatform.user` |
| Trình duyệt Chrome hoặc Cốc Cốc | |

## Chuẩn bị máy

Đã chạy thật: Windows 11, RTX 4060 Ti 16 GB, RAM 64 GB, 32 luồng. Tối thiểu ước tính, chưa thử: NVIDIA từ 8 GB VRAM, RAM 16 GB, nên 32 GB, CPU 8 luồng. Không có GPU vẫn chạy nhưng nghe lời chậm đi nhiều.

Dung lượng đo được: Whisper 2,9 GB, Remotion 825 MB, trình duyệt 720 MB, mỗi dự án 0,2 đến 0,6 GB. Nên để trống ít nhất 15 GB. Khi nghe lời dùng thêm khoảng 4,6 GB VRAM.

## Cài đặt

1. Cài 2 skill `video-ngan-nguoi-noi` và `anh-bia-video` từ các file `.skill`.
2. Chạy:

```bash
python cai_dat.py "D:/KENH CUA TOI"
```

   Lệnh này kiểm máy, cài engine, tạo thư mục kênh và `ho-so-kenh.json`. Cuối cùng in ra đường dẫn Python cần dùng.

3. **Điền `ho-so-kenh.json`:**

| Trường | Ý nghĩa |
|---|---|
| `ten` | Tên kênh, hiện trên nhãn và cảnh kết |
| `chuLinhVat` | 2 chữ trên áo linh vật |
| `mauChinh`, `mauPhu`, `mauBia` | Màu thẻ đồ họa, màu nhấn, màu bìa |
| `xungHo`, `doiTuong` | Cách xưng hô, người xem của kênh |
| `khoCanh` | Thư mục kho và tên file danh mục |
| `nhac`, `tiengChuyenCanh` | Nhạc nền, tiếng chuyển cảnh. Đường dẫn tuyệt đối hoặc tính từ thư mục kênh |
| `thanhPham` | Nơi giao video |
| `anhAI` | Tài khoản tạo ảnh qua API: đường dẫn file khóa và mã project. Đổi tài khoản chỉ cần sửa ở đây. Không dán nội dung khóa vào hồ sơ |
| `anhThamChieu` | 2 đến 3 ảnh thật rõ mặt, dùng để giữ mặt |
| `giongAI` | Chỉ cần nếu làm video không quay: file chứa API key Vibi, mã giọng, tốc độ |
| `nhanCanhAI`, `nhanAnhAI` | Dòng ghi chú dưới tên kênh trên hình, để trống thì không hiện |
| `chanDung` | Tên skill chân dung |
| `tuCam`, `cta` | Từ không được dùng, câu kêu gọi mặc định |
| `lienHe` | Zalo, trang web in trên mọi tờ hướng dẫn |
| `nhanDien` | Nhận diện gắn vào mọi video: `watermark` (PNG 600×224 kín khung, phủ đúng nhãn tên kênh 300×112 ở góc dưới phải), `intro`, `outro` (video dọc 1080×1920 có tiếng), `introKhiDaiHon` (số giây; video ngắn hơn thì bỏ intro). Bỏ trống trường nào thì không gắn phần đó |

4. **Tạo chân dung:** vào Flow, tải 2 đến 3 ảnh thật rõ mặt, thử prompt trong skill `anh-bia-video` (`references/tao-hinh.md`). Khi đã ưng màu da và trang phục, nhờ Claude: "làm skill chân dung cho tôi từ các ảnh này, chốt màu da và trang phục mặc định", rồi ghi tên skill vào trường `chanDung`.

5. **Tạo avatar trên Flow** cho clip có mặt bạn: làm theo hướng dẫn trên Flow, đặt tên `Me`. Google có thể yêu cầu xác minh chính chủ. Chỉ dùng mặt của chính bạn hoặc người đã đồng ý.

6. **Tạo kho cảnh:** nhờ Claude soạn 20 cảnh không người và 20 đến 40 cảnh có mặt bạn theo `references/canh-tram-flow.md`. Tải về thư mục `kho-canh`, ghi vào `danh-muc-canh.csv`:

```csv
ma,dung,bo_cuc,nhom,file,ghi_chu
T01,co,T,ha-tang,Ten_file_tai_ve.mp4,Hành lang máy chủ
```

   Cột `dung` ghi `co` hoặc `khong`, `bo_cuc` ghi `T` (toàn màn) hoặc `D` (nửa trên trống). Mã trùng với mã dùng trong kịch bản.

7. **Nhạc:** chọn bài có quyền dùng ở mọi nền tảng sẽ đăng. Bài trong YouTube Audio Library có thể chỉ dùng được trên YouTube, kiểm trước khi đăng Facebook, TikTok. Ghi tên bài, tác giả, link vào `NGUON.md` của thư mục nhạc rồi khai trong `boNhac`. Bộ này không kèm nhạc và clip.

## Làm một video

Mở Claude ở thư mục kênh và nói một trong các câu:

- "Làm video review công cụ X, theo khuôn B."
- "Đây là video mẫu ..., làm kịch bản theo phong cách kênh mình."
- "Tôi quay xong rồi, file ở ..., dựng đi."
- "Sửa video 05: đổi chữ cảnh kết thành ..."

- "Video này tôi không quay, dùng clip kho và giọng AI."

Claude sẽ dừng để hỏi bạn: duyệt kịch bản, số credit cần tạo cảnh, nghe thử giọng nếu dùng giọng AI, xem bản cuối. Muốn Claude tự làm trọn thì nói rõ, Claude chỉ báo kết quả cuối và những chỗ cần bạn nghe.

**Mỗi video giao gồm:** video (đã gắn watermark, intro, outro theo `nhanDien`), ảnh bìa, content đăng, tờ hướng dẫn PDF (có Zalo và web lấy từ `lienHe`) và bình luận ghim soạn sẵn. Câu kết luôn hỏi người xem rồi chỉ về bình luận ghim, không xin "comment chữ ... để nhận" (dễ bị coi là kéo tương tác). Bạn đưa tờ lên Drive hoặc web, dán link vào bình luận ghim rồi ghim lại.

**Độ dài:** theo nội dung, không ép 1 phút. Một công cụ 45 đến 75 giây; danh sách nhiều công cụ 1 phút 30 đến 2 phút 30.

**Giọng AI:** Claude viết lời liền hơi như người nói thật, giữ ngắt ở dấu phẩy, đo nhịp bằng `do_nhip.py`. Nghe thấy rời rạc hoặc nhanh khó hiểu thì báo đúng câu, Claude sửa và đưa cách sửa vào skill.

**Giữ API key an toàn:** lưu key vào một file riêng trên máy, ghi đường dẫn vào hồ sơ. Không dán key vào chat, không chụp màn hình trang có key. Lỡ lộ thì tạo key mới ngay.

**Hình phần mềm:** không cần cài phần mềm được nói tới. Claude chụp, quay trang công khai và ghi nguồn, nên lời chỉ nói theo tài liệu, không nói như đã dùng thử.

## Quyền và giấy phép

Tự kiểm tra trước khi dùng, nhất là khi dùng cho công ty. Đây không phải tư vấn pháp lý.

- **Remotion:** miễn phí khi tổ chức có tối đa 3 người, tính cả người không dùng Remotion. Từ 4 người phải mua giấy phép công ty ([giấy phép](https://www.remotion.dev/docs/license/pricing)). Điều khoản do Remotion quy định và có thể đổi.
- **Google Flow:** đọc điều khoản về sử dụng thương mại và việc tạo hình người thật. Bộ này che logo góc clip bằng nhãn; bạn cần tự kiểm tra việc này có phù hợp với điều khoản hay không. Dòng ghi chú AI trên hình lấy từ `nhanCanhAI` và `nhanAnhAI` trong hồ sơ, để trống thì không hiện.
- **Nhạc, tiếng hiệu ứng:** theo giấy phép của từng bài.
- **Nhãn nội dung AI:** bật khi nền tảng yêu cầu.
- **Logo, tên công cụ của hãng khác:** chỉ dùng để nói về sản phẩm đó, không để giống đối tác chính thức.

## Khi có sự cố

| Dấu hiệu | Cách xử lý |
|---|---|
| "Chưa cài engine" | Chạy lại `cai_dat.py` |
| Bước `canh` báo THIẾU CẢNH | Tạo cảnh trên Flow hoặc đổi sang mã có sẵn |
| Bước `phu-de` báo lệch lời | Sửa `loi.txt` theo đúng lời đã nói |
| Tạo ảnh báo 429 | Hết hạn mức tạm thời của Google, script tự chờ và thử lại. Bìa làm sau video, đừng để bìa chặn video |
| Tải file từ web không về máy | Trình duyệt đang hỏi nơi lưu; dùng API sẽ không vướng việc này |
| Nghiệm thu báo khoảng lặng hoặc lặp từ | Chỉnh `doan.json`, chạy `--tu master` |
| Whisper chạy rất chậm | Máy không có GPU hoặc thiếu thư viện CUDA, vẫn chạy được |
| Lần đầu chạy tải lâu | Whisper tải mô hình khoảng 3 GB |
| Video mờ | File gốc bị nén, xin lại file gốc |
| Ảnh tĩnh báo "giọng rời rạc" hoặc "giọng liền quá" | Viết lại bản đọc theo `kich-ban.md`, chạy `nghi_dau_phay.py` |
| `xuat_pdf.py` từ chối xuất | Tờ hướng dẫn thiếu khối liên hệ hoặc còn chữ mẫu, điền theo `lienHe` |
| Không ghi đè được video cũ | File đang mở trong trình phát, đóng lại rồi đổi tên |
| Flow không gửi được lệnh | Xem mục "Khi Claude thao tác Flow giúp" trong `references/canh-tram-flow.md` |
