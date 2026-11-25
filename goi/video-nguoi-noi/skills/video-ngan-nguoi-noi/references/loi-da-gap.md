# Các lỗi đã gặp

Mỗi dòng là một lỗi thật, ghi lại để không lặp.

## Lời và âm thanh

| Lỗi | Cách tránh |
|---|---|
| Từ lặp ở chỗ cắt, nghe cả bài không thấy | Nghiệm thu nghe riêng từng đoạn cắt; chọn lần nói theo đảo tiếng |
| Mất đầu câu | Điểm vào lấy theo từ đầu tiên nghe được, không theo đảo năng lượng |
| Khoảng lặng 1,4 giây ở giây thứ 5, các mục khác vẫn báo đạt | Đo bằng VAD; bộ nén nâng tiếng ồn phòng nên đo năng lượng không thấy |
| Tăng tốc giọng 1,12 lần bị chê nhanh | Giữ tốc độ thật, `toc` = 1.0 |
| Đo đủ lời báo sai 59% vì nghe từng cụm trên tiếng đã trộn nhạc | Nghe cả bài và đo đoạn mất liền nhau |
| Nhạc đặt theo số cố định lúc to lúc nhỏ | Đo LUFS thật, nhạc thấp hơn giọng 22 dB |
| Whisper nghe sai tên riêng | Ghi `goi-y.txt`; chữ phụ đề lấy từ `loi.txt`, Whisper chỉ cho giờ |
| Ghép câu tạo lại bị lặng 0,8 giây, phải xuất lại | Khi ghép không thêm `apad`; cắt lặng cuối đoạn mới; bước ảnh tĩnh đo lặng bằng VAD trước khi xuất |
| "Claude" đứng ngay trước dấu phẩy bị đọc thành "Clau-đờ" | Viết lại câu để chữ Claude không đứng trước dấu phẩy, ví dụ "Claude và ChatGPT", "Trong Claude vào" |
| Giọng đọc r, gi thành z ("rê-pô" thành "dây pô", "Gi-Sáp") | Giữ nguyên chữ tiếng Anh (`repo`, `GSAP`); chỉ phiên âm khi bản gốc đọc sai (`Three J S`, `Ép-Ép-Em-Péc`) |
| Phụ đề ghi số bằng chữ làm khớp lời tụt dưới 85% | Phụ đề ghi chữ số (20, 5, 3); bản đọc mới viết số bằng chữ |
| Máy nghe ra hai chữ khác nhau ở cùng một chỗ ("tự chạy" thành "tự chơi", "tự chờ") | Coi là đọc lỗi, tạo lại riêng câu đó |
| Dùng nhạc kho YouTube Audio Library cho video đăng Facebook, TikTok | Chỉ dùng bài trong `boNhac` có ghi nguồn và quyền dùng ngoài YouTube; ghi tên bài, tác giả, link vào content |
| Dấu phẩy sau `Ây‑Ai,` giữa câu làm ngắt nhịp dở ("nhờ AI, đọc") | Đặt chữ AI ở cuối vế: "muốn đưa cho AI,", "giao tài liệu nào cho AI?" |
| Máy nghe ra một chữ thừa sau chỗ nghỉ ("Một, muốn kín"), đoạn cắt riêng lại nghe ra câu bịa | Đo bằng VAD: không có tiếng ở khoảng đó thì là máy nghe nhầm, không tạo lại |
| Anh chê giọng rời rạc, giọng máy dù đã thêm thán từ | Đo ra mỗi hơi chỉ 0,8 đến 1,2 giây; viết bản đọc liền hơi, bỏ dấu phẩy và `<#...#>`, bước ảnh tĩnh tự báo khi dưới 1,6 giây |
| Sửa giọng rời rạc bằng cách bỏ hết dấu phẩy: 10/11 dấu phẩy không còn nghỉ, anh nghe liền quá, khó hiểu | Giữ dấu phẩy ở chỗ chuyển ý, chạy `nghi_dau_phay.py`, nhắm 1,6 đến 2,0 giây mỗi hơi |
| `nghi_dau_phay.py` chèn chồng nghỉ vào dấu phẩy đã có nghỉ sẵn (15-omni-voice: 10 chỗ, một hơi tụt từ 1,61 xuống 1,46 giây). Giờ chữ Whisper lệch sớm khoảng 0,2 giây, cửa sổ tìm ±0,15 giây trượt mất chỗ lặng thật | Đã sửa: lấy đoạn lặng dài nhất trong ±0,35 giây quanh dấu câu. Đo `do_nhip.py` cả trước và sau khi chèn; sau chèn mà tụt dưới 1,6 thì xem lại công cụ trước khi viết lại lời |
| Câu liệt kê nhiều vế ngắn có dấu phẩy ("nam hay nữ, trẻ hay già, trầm hay cao") làm mỗi hơi chỉ khoảng 1 giây, kéo trung bình cả bài dưới 1,6 | Gộp liệt kê thành một vế ("nam nữ già trẻ hay trầm cao đều chiều được hết"), tạo lại riêng câu đó rồi ghép |
| Cắt lặng đầu đoạn giọng mới bằng `silenceremove` ngưỡng -40 dB làm mất phụ âm đầu: "Không" thành "Tông" | Cắt đầu bằng `-ss` cách điểm có tiếng khoảng 0,08 giây, chỉ dùng `silenceremove` cho đuôi. Nghe lại đoạn mới bằng Whisper trước khi ghép, kèm `goi_y` là chính câu đó: đoạn ngắn nghe `vad=False` mà không gợi ý thì Whisper bịa cả câu ("Hãy subscribe cho kênh...", 17-linkedin) |
| Chữ đồng âm gần đúng với số đứng cạnh số: "113 từ sáo" máy đọc, Whisper và cả người nghe đều dễ hiểu thành "113 từ sáu" (17-linkedin). Thêm "rỗng" vẫn bị nghe thành số | Đổi hẳn từ khác ("từ ngữ máy móc"), không cố giữ. Khi `nghe_lai_giong.py` báo một chữ thường bị nghe thành số thì coi là lỗi thật, không bỏ qua như số viết bằng chữ |
| Video mẫu nói sai tính năng: "kết nối thẳng vào LinkedIn, tự vận hành từ A tới Z, tự đăng, tự trả lời", README ghi rõ bộ skill không kết nối, không đăng (17-linkedin) | Đọc README trước khi viết kịch bản, kiểm cả tính năng chứ không chỉ số liệu. Chỗ mẫu nói sai mà tài liệu nói ngược lại thường là móc câu tốt hơn: "nhưng nó cố tình không tự đăng" |
| Bước `nghiem-thu` trong `dung.py` chạy 5 phút, không in dòng nào rồi dừng mã 1; chạy riêng `nghiem_thu.py` và `dung.py --tu nghiem-thu` đều ĐẠT trong 18 giây (17-linkedin) | Lỗi tạm thời, không phải video hỏng. Chạy lại `--tu nghiem-thu` một lần; lần hai vẫn lỗi mới tìm nguyên nhân. Không bàn giao khi chưa có một lần ĐẠT |
| `nghe_lai_giong.py` báo sai "câu dính" và "lặng 1,84 giây" (17-linkedin, 18-rag): khung đo dựa giờ chữ Whisper, mà nghe không gợi ý thì Whisper lệch và bịa câu; lặng dài tính từ khoảng cách giữa chữ | Đã sửa 08/11/2026: đo trên sóng âm (dB so với phân vị 95, khung 10 ms), khung từ 0,3 giây trước tới 0,8 giây sau chữ cuối câu; lặng dài cũng đo trên sóng âm. `hoi_quy.py` thử trên bản thật (không được báo) và bản cố tình làm hỏng (phải bắt đúng chỗ) |
| Remotion chép nguyên liệu vào Temp ổ C mỗi lần xuất, ảnh tĩnh, bìa và không xóa: 325 thư mục, 24 GB sau một tuần (08/11/2026) | Đã sửa: trỏ TEMP của lệnh con vào thư mục riêng của lần chạy rồi xóa. Thư mục cũ trong Temp chung chỉ người dùng tự xóa, lúc không có phiên nào đang dựng; xóa không ảnh hưởng thành phẩm hay dự án |
| `thay_doan_giong.py` cắt theo giờ chữ Whisper (sớm khoảng 0,25 giây) nên sót đuôi chữ cũ "luôn" 0,15 giây sau đoạn mới (19-4skill-P2), nghe như vấp; `do_nhip` thấy một hơi 0,22 giây lạ | Đã sửa: chỗ cắt là giữa khe lặng thật dài nhất quanh ranh giới, không có khe ≥ 60 ms thì dừng. Sau mỗi lần ghép, liệt kê hơi VAD: hơi dưới 0,4 giây ở chỗ ghép là sót. Có mục trong `hoi_quy.py` |
| Đánh số dòng cảnh lệch một lần nữa (19-4skill-P2: cảnh đầu chỉ 1,44 giây), dù đã ghi ở mục Quy trình | `lap_canh.py` in mỗi cảnh kèm "dòng a–b «câu đầu» | chữ trên hình", đọc cột này trước khi xem ảnh tĩnh; `kiem_so_dong()` chặn cảnh hở, chồng và mốc nằm ngoài cảnh (mã thoát 3) |
| Biểu đồ `bieu-do` làm tròn số về nguyên: 15,8 hiện "16k", lệch lời "hơn 15 nghìn" | Đưa số nguyên thật (15811) và bỏ `donVi`, biểu đồ hiện 15.811 |
| Chọn nhạc `cong-nghe` (YouTube Audio Library, chưa kiểm quyền) cho video 20, vì luật nhạc chỉ để người tự soát (11/11/2026) | Đã đưa vào code: `nhacDuocDung` trong `da-chot.json`, `tron_am.py` dừng nếu bài ngoài danh sách. Thêm bài mới thì kiểm quyền, ghi NGUON.md rồi mới thêm vào danh sách |
| Luật đã chốt chỉ nằm trong chữ hướng dẫn nên bị quên: video 17, 18 để nguyên "AI" (đọc thành "ai"), bản đọc thiếu câu cảm thán, dù bản 14, 15 đã làm đúng (08/11/2026) | Luật máy kiểm được đưa vào `da-chot.json`; `tao_giong.py` tự thay và chặn trước khi gửi, `nghiem_thu.py` đọc lại `giong/*.da-gui.txt`. Không dựa vào trí nhớ người làm |
| `nghi_dau_phay.py` không thấy khe lặng thì chèn vào điểm nhỏ tiếng nhất trong ±0,15 giây; điểm đó là khe giữa "tự" và "tin" nên giọng vấp (18-rag, giây 3,27) | Đã sửa: tìm chỗ nhỏ tiếng kéo dài ≥ 80 ms, lệch về sau tới 0,6 giây; vẫn to hơn -30 dB thì bỏ qua, không chèn. Có mục kiểm trong `hoi_quy.py` |
| Viết "RAG chính là cách" thì máy ngắt "RAG" thành một hơi riêng 0,26 giây, nhịp tụt 1,56 (18-rag bản 2). "RAG là cách" thì liền | Từ viết tắt tiếng Anh đứng đầu câu nên nối thẳng với "là", tránh chen từ đệm ngay sau nó |
| README có ảnh động demo giao diện (18-rag: chia đoạn, trích dẫn của RAGFlow) | Tải vào thư mục riêng, chuyển thành mp4 rộng 1080 bằng ffmpeg, cắt từng khúc theo câu, dùng `man-web` với `video`. Ghi nguồn "Ảnh động trong README của ..." và kiểm giấy phép kho chứa ảnh; không có giấy phép thì ghi vào mục cần làm trước khi đăng |
| Tham số cảm xúc và thẻ (laughs), (sighs) gửi qua Vibi không có tác dụng | Cảm xúc lấy từ câu chữ, xem mục viết lời ở `kich-ban.md` |
| Trang có chữ hiện dần khi cuộn tới (chatvideopro.com, 21-story-cutter): `chup_web.py` chụp ngay sau khi cuộn nên ảnh tối mờ, chỉ thấy thanh menu | Đã sửa: chờ `--cho` giây (mặc định 2) sau khi cuộn, đưa chữ `--den-chu` lên khoảng 15% đầu khung và gửi một lần cuộn thật. Luôn mở ảnh chụp ra xem trước khi lập cảnh |
| Bản tóm tắt chủ đề người dẫn gửi (tóm từ video người khác) ghi sai: "Astra" xếp cùng Claude là mô hình suy luận (thật ra là GPT-6 Astra), plugin chia hai tầng mô hình đắt rẻ (trang chính thức không nói), "tiết kiệm 70 đến 80%" (không có nguồn) | Coi bản tóm tắt như video mẫu: kiểm từng ý ở trang gốc, chỉ nói phần có nguồn. Ý hay nhưng không phải tính năng thì nói là cách làm của kênh |
| Máy đọc "Grok" nghe thành "group" (bản thử 21-story-cutter) | Tên không bắt buộc thì bỏ khỏi lời đọc, vẫn ghi trong content; cần đọc thì thử cách viết khác và thêm vào `docDung` |
| Bản đọc thử tên (`giong/thu-ten`) gửi trước khi thêm luật đọc mới vẫn nằm trong `giong/`, nghiệm thu đọc mọi `giong/*.da-gui.txt` nên báo ✘ dù bản thử không vào video (22-team-6-dev) | Đọc thử luôn ra `giong/thu-nghiem/`, không để cạnh bản cả bài |
| Video mẫu chỉ có link Facebook, không có phụ đề dạng chữ, không lấy được file (22-team-6-dev); đọc khung nhỏ không ra chữ | Tua đến khung có số thứ tự, phóng to riêng thanh tên kho GitHub. Mẫu dùng số liệu cũ (sao), nói sai số agent (5 thay vì 4) và nêu kho không giấy phép: kiểm từng kho bằng API, thay kho sai |
| `gstack` máy đọc thành "gu-stack" | Đã thêm `docDung`: gstack thành "G Stack" |
| Lại đánh `den` lệch một dòng ở video 22 (giống video 19) | Bảng `dòng a–b` in ra khi lập cảnh bắt được ngay: luôn đọc bảng đó trước khi xem ảnh tĩnh; cảnh đầu `tu` 0, `den` là dòng đầu của cảnh sau đếm từ 1 |
| Làm lại reel "6 skill" (22-team-6-dev) gọi cả /code-review và /security-review là thứ phải cài, trong khi Claude Code đã tích hợp sẵn; người dẫn góp ý | Luật 15: kiểm tình trạng từng món ở nguồn gốc, ghi `tinh-trang.json`; món có sẵn phải nói "có sẵn/tích hợp sẵn". Lập cảnh và nghiệm thu chặn nếu sai |
| "giỏi thật" ở câu mở bị máy đọc thành "giỏi thất" (22-team-6-dev, người dẫn nghe ra); Whisper có gợi ý vẫn ghi đúng chữ nên máy không bắt | Đổi từ ("giỏi lắm"), tạo lại riêng câu đó, nghe máy KHÔNG gợi ý để chắc. Câu mở nằm ở đầu file: `thay_doan_giong.py` không tìm được khi tên riêng bị nghe sai ("Claude" thành "Cloud"), ghép tay tại khe lặng thật dài nhất sau câu. Câu đầu video quan trọng nhất: đọc thử riêng câu mở trước khi tạo cả bài |
| Tiêu đề cảnh nền sáng dài 21 ký tự ("Không đọc hết một lúc") xuống hai dòng, dòng cam phía dưới bị thẻ che mất (23-skill-ben-trong) | Giữ `tren` khoảng 19 ký tự trở xuống; ảnh tĩnh bắt được, soát kỹ dòng `duoi` có hiện đủ không || Chụp bảng bằng `chup_web.py --den-chu` với chữ ở dưới bảng: chữ đó lên 15% khung nên đầu bảng bị cắt mất (23-skill-ben-trong) | Đặt `--den-chu` là chữ trong hàng đầu của bảng, rồi xem ảnh trước khi đặt toạ độ khoanh |
| Chụp bảng bằng `chup_web.py --den-chu` với chữ ở dưới bảng: chữ đó lên 15% khung nên đầu bảng bị cắt mất (23-skill-ben-trong) | Đặt `--den-chu` là chữ trong hàng đầu của bảng, rồi xem ảnh trước khi đặt toạ độ khoanh |
| Nghe lại cả file giọng 89 giây, Whisper bịa "hãy subscribe cho kênh..." rồi bỏ cả 25 giây cuối, báo khớp 68% dù giọng đúng (23-skill-ben-trong) | `nghe_lai_giong.py` nay tự cắt file trên 45 giây thành khúc khoảng 30 giây ở chỗ lặng rồi nghe từng khúc; cùng file đó đạt 92% |
| Chữ trên cảnh `flow-chu` dài quá khoảng 15 ký tự mỗi dòng ("MÀ KHÔNG ĐƯỢC GỌI?", "3 ĐIỀU HAY HIỂU SAI") xuống ba dòng, che mặt (23-skill-ben-trong) | Giữ mỗi dòng `flow-chu` khoảng 15 ký tự, soát ảnh tĩnh trước khi xuất |
| Bản giải thích khái niệm rút còn 40 giây bị chê kém hấp dẫn hơn video mẫu có chương (23-skill-ben-trong) | Dùng khuôn D trong kich-ban.md: chia phần, mỗi phần có thẻ chương, thêm ví dụ chạy thật và phần hay hiểu sai |
| Máy đọc "MIT" (giấy phép) thành "Meet" (bản thử 25-agenttube) | Không đọc tên giấy phép; nói "mã nguồn mở", ghi MIT trong content và chữ nguồn trên hình |
| Bản đọc "Kho này tên là..." máy đọc thành "Con này" (25-agenttube), Whisper không gợi ý nghe đúng "Con" | Nghĩa vẫn đúng thì sửa `loi.txt` theo lời đã đọc, không tạo lại; nghe lại không gợi ý trước khi lập cảnh |
| Một hơi 2,11 giây (25-agenttube): câu mở dài không dấu phẩy, `nghi_dau_phay.py` chỉ chèn ở dấu câu. Tạo lại câu mở có thêm dấu phẩy thì máy đọc "agent" thành "Asian", bỏ | Tìm khe giữa hai từ đã có (Whisper thấy khe ≥ 0,2 giây) ở các hơi dài, chèn 0,15 giây lặng vào điểm nhỏ tiếng nhất của khe đó; chỉ chèn khi điểm đó dưới khoảng -30 dB và nằm giữa hai từ, đo lại `do_nhip.py` |
| Ảnh chụp trang GitHub `zoom` 1,5 nhìn quá nhỏ trên điện thoại, phải dựng ảnh tĩnh lần 2 (25-agenttube) | Khoanh nút Star thì đặt `zoom` khoảng 2,2 và `x` sao cho `x` + 980/(0,907×zoom) ≤ 1080 (khoảng 590); ảnh README 1440 rộng thì `zoom` 1,6 quanh chỗ khoanh |

## Hình

| Lỗi | Cách tránh |
|---|---|
| Chữ đỏ trên cảnh tối khó đọc | Dùng `nen: true` |
| Hình người vẽ tay trông thô | Thay bằng cảnh AI hoặc ảnh thật |
| Đồ họa đứng yên | Mô hình nền sáng đã có chuyển động chậm và linh vật, thẻ hiện theo `moc` |
| Ảnh trong khung chỉ lộ đỉnh đầu | Chỉnh `catAnh`, xem tờ soát |
| Logo Flow lộ ở góc | Clip trong ô nhỏ đã phóng để cắt góc; toàn màn có nhãn che |
| `hai-phe` dùng cho "hiểu nhầm / đúng là" thì ý sai hiện viền xanh, ý đúng viền đỏ, phải dựng ảnh tĩnh lần 2 (26-tiet-kiem-claude) | `hai-phe` là hai quan điểm ngang nhau, phe đầu luôn xanh. Sai rồi đúng thì dùng `truoc-sau` (trước đỏ dấu ✕, sau xanh dấu ✓) |
| Video bị bạc màu trên trình phát | Render bt709, yuv420p; nghiệm thu đã kiểm |
| Thẻ đè phụ đề | Chỉnh `viTriPhuDe` theo từng cảnh |

## Quy trình

- Mỗi lần người dùng góp ý hoặc mình tự sửa một lỗi, đưa luôn cách làm mới vào skill (tài liệu, mã hoặc bước kiểm), đóng gói và cài lại ngay trong lần đó, không để dồn.
- Video mẫu trùng chủ đề video đã làm: báo người dùng, làm bản khác hẳn (dài hơn, góc khác) chứ không làm lại y hệt.

| Lỗi | Cách tránh |
|---|---|
| Video mẫu dùng số cũ (16-lemo: mẫu nói 1.426 sao, 43 phong cách; kho thật đã 13.427 sao, 66 phong cách) | Luôn đọc số mới qua API, README ngày làm; ghi vào content số cũ của mẫu và số đã cập nhật |
| Clip kết P06 lộ logo trên nắp laptop ở khung cuối | Đọc ghi chú `danh-muc-canh.csv` trước khi chọn clip kết; soát khung cuối cảnh `ket-comment` trong `soat-tinh` |
| Đánh số `tu`, `den` trong `canh.json` từ 0 trong khi quy ước đếm từ 1: mọi cảnh chạy sớm một câu so với lời (15-omni-voice) | Dòng đầu `loi.txt` là cụm 1, `tu: 0` chỉ dùng cho đầu video. Trong `soat-tinh-*.jpg`, phụ đề ở khung cuối phải thuộc chính cảnh đó; thấy phụ đề của câu trước là lệch số |
| File qua điện thoại bị nén 480×854 | Xin file gốc; kiểm độ phân giải khi nhận rồi báo ngay |
| Lưu thành phẩm sai chỗ | Chép vào đúng thư mục chủ đề |
| Hỏi những câu tự tìm được | Có mẫu thì tự xem, tự dựng; chỉ dừng ở cửa duyệt |
| Số trong video mẫu đã cũ | Kiểm lại nguồn gốc trước khi viết |
| Gắn nhầm video thay vì avatar, mất credit | Luôn vào mục Avatars, soát huy hiệu trước khi gửi |

## Giọng AI đọc "Ây Ai" tách thành hai nhịp

Dấu hiệu: Whisper ghi "Ây, ai" có dấu phẩy, đo năng lượng thấy khe trên 100 ms giữa hai tiếng. Sửa: tạo lại đúng câu đó, viết `Ây‑Ai,` (gạch nối không ngắt U+2011, có dấu phẩy sau). `A.I.` bị đọc thành tiếng Việt "ai", không dùng. Sau khi tạo giọng phải đo mọi chỗ AI trong bài.

## Chữ hai dòng đè nhau

Chữ hoa tiếng Việt có dấu chồng (Ỗ, Ũ, Ắ) cao hơn hẳn chữ thường, dòng dưới chạm dòng trên nếu `lineHeight` nhỏ. Giữ tối thiểu 1,3 với chữ hoa, 1,24 với tiêu đề thường. Khi soát, phóng to tiêu đề có dấu chồng, thu nhỏ không thấy lỗi này.

## Câu kết "Comment CÀI, mình gửi..." (16/11/2026)

21/23 video kết bằng "Comment CÀI / LOCAL / DỰNG / TEAM / MẪU, mình gửi...". Meta coi xin bình luận để đổi tài liệu là kéo tương tác (engagement bait) và giảm phân phối, YouTube cấm đổi phần thưởng lấy tương tác; lặp ở gần mọi video càng dễ bị phạt. Sửa: giữ câu hỏi thật, thay vế mời bằng "Hướng dẫn ... mình để sẵn ở bình luận ghim nhé!"; khung cam trên hình thành "XEM BÌNH LUẬN GHIM". Khóa bằng `kiem_cau_ket()` (bản đọc, `loi.txt`, `canh.json`) và mẫu `hoi_quy/sai-ket-*.txt`. Video cũ sửa thành bản `-sach`, không ghi đè bản đã đăng.

## Vibi bảo trì giọng, chữ "ngách" đọc sai (21/11/2026, video 27)

- Vibi trả `HTTP 503 provider_under_maintenance` (MiniMax) gần 5 giờ, trước đó có lúc 401 `unknown_tenant`. Không gửi lại dồn dập: đặt lệnh canh 15 phút một lần (thử `--lay` tên task trước, không thấy thì gửi lại câu), tối đa 4 giờ, hết hạn thì báo người dẫn. Người dẫn báo Vibi chạy lại thì gửi ngay một lần.
- "ngách" giọng AI đọc thành "mách". Viết "cùng chủ đề" thay cho "ngách" ở cả lời đọc, `loi.txt` và content.
- Ghép câu mới vào giọng cả bài dễ làm nhịp vượt 2,0 giây (câu dài đọc một hơi). Đo `do_nhip.py` ngay sau `thay_doan_giong.py`; vượt thì chèn nghỉ 0,15–0,2 giây ở chỗ ngắt ý tự nhiên trong câu mới, rồi chạy `nghe_lai_giong.py` xem còn câu dính không.
- `nghe_lai_giong.py` nghe cả file đôi khi bịa câu "Hãy subscribe cho kênh..." làm lệch cả phần sau. Khi thấy chữ lạ đó, nghe lại theo khúc 20 giây trước khi kết luận giọng hỏng.
- Tiêu đề hoa trên `flow-chu` chỉ chứa khoảng 15 ký tự mỗi dòng ("LÀM KÊNH YOUTUBE" và "CHO KÊNH YOUTUBE" đều tràn); viết ngắn ngay từ đầu để khỏi dựng lại.

## Cảnh kết giơ hai tay lặp lại (21/11/2026)

Người dẫn chê cảnh kết giơ hai tay (P02) không hấp dẫn: P02 nằm ở 8/24 video, 6 trên 8 video gần nhất. Cùng một động tác ở cuối mọi video thì người xem quen mắt, lướt đi trước câu hỏi kết. Sửa: chọn clip theo ý câu hỏi (tò mò: P09 nửa đầu, P01; vui: P12, P36; hướng dẫn: P40, P38; ngẫm: P08). Khóa bằng `kiem_canh_ket()` trong `lap_canh.py`: trùng clip kết của 5 video đã dựng xong gần nhất thì dừng (mã 3) và gợi ý clip chưa dùng. Có mục `thu_canh_ket` trong `hoi_quy.py`.

## Vibi bảo trì cả chiều, tên task trùng, nối dự phòng ai33 (21/11/2026, video 28)

- `tao_giong.py --lay giong/ca-bai` tải nhầm giọng của video 27: tên task trên Vibi chỉ là "giong/ca-bai", trùng giữa mọi video. Đã sửa: tên task gửi lên kèm tên thư mục dự án (`<dự án>/giong/ca-bai`), `--lay` tìm đúng tên đó. Trước khi dùng file lấy về, so độ dài với lời đọc.
- Vibi trả 503 `provider_under_maintenance` lần hai trong ngày. Đã nối đường dự phòng: lỗi 401/403/5xx hoặc mất mạng thì `tao_giong.py` tự gửi sang `giongAI.duPhong` trong hồ sơ (ai33.pro / OpenSpeaker, cùng giọng nhân bản của người dẫn, model speech-02-hd). Trang này có thể trả kết quả từ model riêng của họ thay cho nhà cung cấp đã chọn, nên nghe lại kỹ hơn bản Vibi.
- Chèn nghỉ vào chỗ ngắt dòng phụ đề GIỮA câu (vd "sửa chính tả / thì không cần") làm nhịp tụt dưới 1,6 giây. `nghe_lai_giong.py` báo "câu dính" ở các chỗ này nhưng chỉ cần sửa chỗ có dấu chấm, chấm hỏi, chấm than.
- `donVi` của `bieu-do` không tự thêm khoảng trắng: ghi " dòng" có dấu cách đầu.


## Video giới thiệu bản thân BNI bị chặn ở tạo giọng (24/11/2026, mẫu thử lớp học)
- Triệu chứng: `tao_giong.py` báo "bản đọc cần chia đoạn, đoạn cuối là câu hỏi và câu chỉ về bình luận ghim" cho lời BNI; khung kết hiện "XEM BÌNH LUẬN GHIM" khi `tuKhoa` chỉ một chữ.
- Nguyên nhân: luật câu kết của kênh áp cho mọi video, chưa có loại video giới thiệu.
- Cách sửa: `loai.txt` = `gioi-thieu` (hàm `loai_du_an` trong `kiem_chot.py`, dùng ở `tao_giong.py` và `nghiem_thu.py`); `tuKhoa` từ 2 chữ. Hồi quy: `hoi_quy/gioi-thieu-bni-34.txt`.
- Lỗi phụ cùng lần: đặt `tu`/`den`/`moc` lệch sớm 1 dòng (tưởng `tu: 3` là sau dòng 3), chữ trên hình chạy trước giọng khoảng 1,5 giây; người soát độc lập bắt được. Cách tính đúng: `tu: N` là lúc dòng N bắt đầu. Đã ghi trong `mo-hinh-canh.md`; luôn đọc bảng "dòng a–b" mà `dung.py` in ra. Dự án 33 (BNI 23/11) cũng đặt mốc kiểu này, nên xem lại.

## Học viên mới không có cảnh mặt mình (24/11/2026, mẫu thử lớp học lần 2)
- Triệu chứng: skill mặc định mở và kết bằng clip có mặt người dẫn (P, X...). Máy học viên không có các clip đó nên `lap_canh.py` dừng mã 2 "thiếu cảnh, tạo trên Flow", học viên bị kẹt.
- Cách sửa: `loai.txt` thêm `khong-mat`; `lap_canh.py` chặn clip trong thư mục "... CO MAT ..." và in danh sách clip không người có thật trên máy để thay. Quét kho một lần thành bảng tên file (lần đầu viết `rglob` cho từng dòng danh mục, 400 dòng trên ổ USB chạy quá 5 phút).
- Còn để ngỏ: gợi ý clip kết trong `kiem_canh_ket` (`GOI_Y_KET`) vẫn toàn clip có mặt người dẫn.

## Cảnh hoạt hình trong video giới thiệu bản thân (24/11/2026, người dẫn xem bản không mặt)
- Triệu chứng: bản BNI không mặt dùng K071 (cửa hàng tí hon) và K006 (robot tí hon chạy băng chuyền như đoàn tàu). Người dẫn: cảnh hoạt hình 3D không hợp video giới thiệu bản thân.
- Cách sửa: video `gioi-thieu` ưu tiên cảnh thật, sang, hợp người làm nghề; `lap_canh.py` chặn clip có ghi chú "tí hon", "đất sét", "hoạt hình", "cartoon", "đồ chơi" và bỏ chúng khỏi danh sách gợi ý. Đã thử trên dự án 35: chặn đúng K006, K071.

## Quy trình BNI tự động cho học viên (24/11/2026, thử 3 trường hợp)
Câu lệnh "Dựng một video giới thiệu bản thân cho tôi theo cấu trúc BNI" → mục BNI trong SKILL.md + `scripts/bni.py`. Lỗi gặp khi thử và cách đã sửa:
- `bni.py` lần đầu đặt mốc cảnh lệch 1 dòng (hiểu sai `tu`). Đúng: `tu: N` là lúc dòng N bắt đầu; phần 1 có 2 dòng thì `tu 0, den 3`.
- Cảnh mặc định công nghệ viễn tưởng (N031 bảng số liệu, N100 thành phố neon) lạc với nghề spa → mặc định đổi sang cảnh đời thường Việt Nam; `bni.json` có `canh` để chọn cảnh hợp nghề.
- Phụ đề rớt chữ khi dòng > 28 ký tự, thẻ kết rớt chữ khi `ghiNho` > 22 ký tự → `bni.py` cảnh báo trước khi dựng.
- Các ý "việc làm" hiện trước lúc đọc tới → `bni.py` dò dòng có chữ đầu của từng việc.
- Giọng miễn phí (edge-tts, Microsoft) lỗi `NoAudioReceived` theo đợt, có lúc 10 lần liền → thử lại tới 20 lần; lần hỏng để lại file `ca-bai.mp3` rỗng làm lần sau tưởng đã có giọng → ghi file tạm rồi mới đổi tên, `bni.py` chỉ dùng lại giọng > 20 KB và khi lời đọc không đổi.
- Luật 9 đọc nhầm mã cảnh `ket-comment` + clip `TOI3` thành "comment TOI" → `kiem_ket_du_an` chỉ đọc chữ hiện trên hình (bỏ `loai`, `clip`, `ten`...). Hồi quy: mục "luật 9: mã cảnh ket-comment + TOI3".
- Chưa thử thật: học viên tự quay đọc lời làm giọng (`giongTuQuay`) — chỉ mới viết code, chưa có file quay mẫu.

## Câu lệnh "Edit video <file>" (24/11/2026, thử với file quay 91 giây)
- Skill edit cũ (aduca-video-studio) trỏ tới thư mục studio không còn trên máy và có 4 cửa chờ duyệt → làm `scripts/edit.py` trong skill này, một lệnh, tự chấm.
- File quay màn ngang nằm trong khung dọc có viền đen → `edit.py` cắt viền (cropdetect), đặt giữa, nền mờ.
- Whisper bịa câu cuối "Hẹn gặp lại các bạn trong những video tiếp theo" (10 chữ trong 0,48 giây) và một câu 17 chữ trong 1,8 giây → bỏ câu từ 4 chữ nhanh hơn 7 chữ/giây.
- Đệm hai lần (edit.py đệm + lap_master.py đệm 0,06/0,12) làm khoảng lặng 0,74 giây → edit.py không đệm; tách đoạn ở khoảng lặng thật (silencedetect -32 dB) trên 0,45 giây.
- Lần đầu thử kéo điểm kết tới khoảng lặng kế tiếp → các đoạn chồng nhau, mất 101 từ → bỏ cách đó.
- Nói lại giữa câu trong cùng một đảo tiếng ("…nhận lương hàng | Các bạn sẽ được nhận lương hàng tháng…") → bỏ lần trước khi chuỗi ≥ 4 chữ lặp lại trong vòng 12 chữ.
- `nghiem_thu.py` bắt nhầm "lặp giữa đoạn" với câu bình thường ("…các bạn ra trường. | Các bạn có đang…") vì 2 chữ trùng trong 8 chữ cuối là tính → 2–3 chữ chỉ tính khi sát chỗ cắt (`lap_noi`); hồi quy có cả ca lặp thật và ca câu bình thường.
- Tiêu đề tự lấy 6 chữ đầu bị cắt ngang ý ("BẠN ĐANG LO / LẮNG VỀ TƯƠNG") → người giao việc đặt `--tieu-de` từ ý chính trong lời.
- Agent mới chép vào ~/.claude/agents chỉ nhận ở phiên Claude mở sau đó → `cai_dat.py` nhắc mở lại Claude.
- File quay gần như không có tiếng (mẫu quay HeyGen, -52 dB): edit.py chỉ nghe được 1 đảo; người giao việc phải báo người dùng file không có lời.
- Người chấm bắt lỗi CHẶN ở bản 1: bộ lọc "câu bịa theo tốc độ" bỏ nhầm nửa câu thật về lương. Gốc: nghe cả file, Whisper chép lặp đầu câu trước vào đoạn sau với giờ dồn giả và ghi "700 .000." thay cho "700 đến 1.200 euro". Sửa: câu nhanh bất thường thì đo tiếng thật (không có tiếng mới là bịa, bỏ); có tiếng thì NGHE LẠI riêng vùng đó (không nối ngữ cảnh) và thay lời. Tránh "dò nói lại" bỏ nhầm câu thật.
- Phụ đề Whisper sai chính tả ("đất đỏ") và ngắt dòng cắt đôi từ ghép → máy ngắt theo dấu câu rồi chia đôi ở chữ nối; thêm bước người dựng soát `loi.txt` trước khi xuất (không thêm bớt chữ).
- Hình người nói nhỏ (màn ngang 720x404 trong khung dọc) → dải giữa phóng 1,4 lần trên nền mờ.

## 24/11/2026 - Edit video thử máy học viên (lần 1, 111 giây, 25 phút)
- Thẻ tiêu đề `nguoi-chu` đặt `at` cố định, hiện trước giọng 2,2 giây (người chấm bắt). Sửa: edit.py tìm dòng có chữ của tiêu đề.
- Lọt "nhân viên nhân viên" (lặp 2 chữ liền nhau) và "agent nó khác skill / ờ / agent nó khác skill" (đảo ậm ừ xen giữa). Sửa: bắt lặp liền 2–3 chữ, bỏ qua đảo ậm ừ khi so đảo sau. Có bài hồi quy.
- Video chỉ có người nói, dễ nhàm (anh góp ý). Sửa: edit.py hai bước, Claude soạn chon.json chọn câu và 2–4 cảnh minh họa; mốc cảnh tự tính theo câu, clip kho tự cắt ≤ 7,5 giây.
- Sửa tay loi.txt làm lệch mốc cảnh. Sửa: chữ nghe sai ghi ở "sua" của chon.json.
- Bản 30 giây: edit.py --dai 30.
- Lần 2 (bản 30 giây, 24/11 18:27): chia câu băm 3 chữ một câu khi Whisper ghi khe 0 (sửa: tách ở khe dài nhất, hòa thì gần giữa, mỗi phần ≥ 3 giây); hồ sơ kênh mẫu có `chuLinhVat: "AB"` làm linh vật máy học viên mang chữ AB (sửa: để trống); nghiệm thu báo lặp "kiểm tra email, | kiểm tra chứng từ" (người nói liệt kê, hai đoạn liền nhau trong file gốc, sửa: không tính lặp 2–3 chữ ở đó). Có bài hồi quy.
- Lần 3–4 (18:37–18:56): Whisper có lần lạc tiếng (chữ Hàn, Nga, "GORDON") → edit.py tự nghe lại đoạn đó; nhạc nền làm "agent" thành "agile" lúc nghiệm thu → edit.py ghi goi-y.txt từ "sua"/tieuDe; cắt theo giờ chữ Whisper làm cụt đuôi chữ, lọt đầu chữ kế (chấm 7,5/10) → bám điểm cắt vào chỗ lặng thật, ưu tiên chỗ lặng SAU chữ cuối; tiếng chuyển cảnh đè chữ khi cảnh minh họa vào giữa câu → tron_am.py hạ đỉnh tiếng chuyển cảnh còn -24 dB cho loại edit. Gộp 3 khối của phiên chính: bo_lap_trong, cắt mép bằng VAD, tự chỉnh tốc độ (toc ≤ 1,2).
