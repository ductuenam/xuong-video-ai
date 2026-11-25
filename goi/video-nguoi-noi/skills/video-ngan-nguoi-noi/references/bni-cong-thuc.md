# Công thức bài giới thiệu bản thân BNI

Đây là **nguồn duy nhất** của khung BNI: SKILL.md, người chấm và `bni.py` chỉ trỏ về đây. Tệp này chỉ cho **mạch** (nói gì trước, gì sau). Còn **lời** thì AI tự viết cho hợp từng người: chuyện thật của họ, chữ của nghề họ, đúng giọng họ. Không có câu mẫu nào để chép.

**Mục đích:** người CHƯA từng gặp nghe MỘT lần là nhắc lại được **tên gì, làm gì, giúp ai**, rồi mới tới vì sao tin được và nên giới thiệu ai cho họ. Nghe xong chưa trả lời được ba câu đó là bài hỏng, câu chữ hay tới đâu cũng vậy (Founder chấm 25/11/2026: bài đi thẳng vào chuyện, chưa nói mình là ai, phục vụ ai, nên nghe khó và không ra mạch).

## 1. Khung sườn 5 nhịp

Giữ **thứ tự**, còn cách nói thì tự do. Hai nhịp liền nhau có thể gộp vào một câu, miễn người nghe vẫn nhận ra từng ý.

| Nhịp | Người nghe cần biết | Gợi ý |
|---|---|---|
| 1. Tôi là ai | Tên, thương hiệu, vai trò | Tên nói trong khoảng 5 giây đầu |
| 2. Làm gì, cho ai | Nghề, nhóm khách chính, họ được gì | Nói bằng chữ khách hay dùng, không dùng chữ quảng cáo |
| 3. Vì sao tin | Một điều thật, dễ hình dung | Chuyện một khách, một con số, một nơi đã làm: chọn MỘT |
| 4. Nhờ giới thiệu ai | Một nhóm người, cách nhận ra họ, mời họ điều gì | Một lời xin mỗi video. Xin khách trực tiếp hoặc người hay gặp khách trước mình (phòng BNI ưu tiên kiểu sau) |
| 5. Câu dễ nhớ + tên | Câu tả nghề sống động, rồi nhắc tên | Câu dễ nhớ giữ nguyên qua các tuần |

**Độ dài** (`doDai` trong `bni.json`):
- **30 giây (mặc định).**
  - Giọng máy thường cần 70–118 chữ. Máy đo độ dài giọng thật (18–30 giây) và báo cần thêm hay bớt bao nhiêu chữ.
  - Tự quay giọng thường 70–150 chữ, tùy người nói nhanh hay chậm.
- **60 giây.** Dùng cho sự kiện networking hay giới thiệu dài.
  - Vẫn đủ 5 nhịp; nhịp 3 kể trọn chuyện (tình huống → việc mình làm → kết quả).
  - Thường 150–230 chữ.
  - Thư mục dự án thêm đuôi `-60`, để không trùng bản 30 giây làm cùng ngày.
- **15 giây (Reels).** Chưa làm được. Nói rõ với người dùng và đề nghị bản 30 giây. Không tự cắt bớt nhịp.

**Hai kiểu bài, cùng một khung:**
- **Giới thiệu lần đầu (mặc định):** đăng trang cá nhân, gửi nhóm, chiếu buổi đầu gặp. Nhịp 2 nói nghề chính và nhóm khách chính.
- **Bài tuần BNI** (`"kieu": "tuan"` trong `bni.json`): người trong phòng đã quen mình. Sổ BNI có tuần cũ thì coi là bài tuần, không cần hỏi, trừ khi người dùng nói làm lại video giới thiệu.
  - Nhịp 1–2 nói gọn "ai, làm gì, cho ai" trong một câu, nối luôn sang **một mảng nhỏ tuần này** và nói mảng đó thành lời.
  - Thẻ `chuDe` ghi mảng tuần này. Chuyện và lời xin đi theo mảng đó.
  - Câu mở có thể giữ cố định các tuần cho người trong phòng quen tai. Phần đổi là mảng, chuyện và lời xin. Lúc viết 2–3 bản thì các bản khác nhau ở cách kể chuyện và lời xin, câu mở có thể giống nhau.
- **Đăng công khai cho khách xem** (trang cá nhân, nhóm khách hàng, không phải phòng BNI): nhịp 4 có thể là lời mời thẳng người xem ("ai đang … thì nhắn mình") thay vì nhờ giới thiệu. Vẫn giữ một nhóm người cụ thể.

## 2. Máy kiểm gì

`python bni.py "<dự án>" --kiem` chạy trong vài giây, chưa tạo giọng. Sửa tới khi không còn ✘ rồi mới dựng.

**Chặn (✘), vì làm hỏng video hoặc sai mục đích:**
- Dòng phụ đề quá 28 ký tự, `ghiNho` quá 18 ký tự.
- Thiếu `mo` hoặc `bangChung`, hoặc `lienHe` dưới 2 chữ.
- Tên gọi chưa nói trong 20 chữ đầu.
- `doc-tts.txt` lệch `loi.txt`.
- Số chữ lệch rất xa độ dài đã chọn.
- Bài tuần (`"kieu": "tuan"`) có lời giống một tuần cũ từ 60% trở lên. Làm lại video giới thiệu lần đầu với lời cũ thì chỉ nhắc.
- Chép nguyên 8 chữ liền từ tệp này.
- Có ghi `giongTuQuay` mà chưa có tệp giọng.
- `phan` có nhịp 0 dòng.
- Ngành có quy định (bảo hiểm, tài chính, y tế, làm đẹp…) mà lời có chữ hứa hẹn (thu nhập, lợi nhuận, cam kết, trị dứt, giảm phí…).
- Sau khi tạo giọng: giọng ngoài khoảng giây của độ dài đã chọn.

**Nhắc (⚠), AI tự cân nhắc theo người:**
- Số chữ ngoài khoảng thường gặp.
- Câu vụn, dấu hai chấm, chữ số chưa viết thành chữ.
- Chữ trên thẻ dài hơn 14 ký tự. Bỏ qua được nếu bước dựng cảnh không báo tràn (bước đó đo bằng phông thật và chặn nếu tràn).
- Chữ máy dễ đọc sai: viết tắt, chữ tiếng Anh. Tự quay giọng thì không nhắc.
- Lời xin chung chung ở bất kỳ đâu trong bài.
- Chữ hứa hẹn ở ngành khác.
- `nganh` không có trong kho cảnh, `tamTrang` không hợp lệ.
- Bài tuần có chủ đề gần với một tuần cũ.

## 3. Viết cho nghe mượt

Video này để NGHE. Viết như người đó đang nói với một người mới quen.
- **Câu đầu tự hiểu được.** Muốn mở bằng một câu gợi chuyện hay câu hỏi thì câu đó phải ngắn và rõ, rồi tới tên ngay. Không mở bằng mảnh câu cụt (bài thử "Cỡ bốn tỷ mà vẫn nộp khoán." làm người nghe chưa biết ai đang nói, nói về gì).
- **Câu đủ ý, nối nhau như lời nói.** Không chặt thành mảnh 2–4 chữ, không viết kiểu tiêu đề có dấu hai chấm. Chuyển nhịp bằng lời nói thường.
- **Xưng hô một kiểu suốt bài,** đúng như người đó nói với khách. Đăng công khai thì gọi người xem chung chung ("anh chị", "mọi người", "bạn"), đừng chỉ gọi một giới.
- **Một ý chính mỗi nhịp.** Nhiều thành tích thì chọn cái người nghe dễ hình dung nhất.
- **Đọc to cả bài một lượt.** Chỗ nào vấp, hay phải đọc lại mới hiểu, thì viết lại.
- **Tự kiểm ba câu:** người lạ nghe xong trả lời được tên, làm gì, giúp ai không?
- Phụ đề: không ngắt dòng giữa một từ ghép ("tư / vấn"). Mỗi ý hiện thành thẻ thì nằm trên một dòng riêng.

## 4. Thiếu dữ liệu thì làm gì (không bịa, không độn)

- **Không có chuyện khách, không có số:** dùng điều thật nhất đã có, như số năm làm nghề, nơi làm, khách quen quay lại, một việc cụ thể họ hay làm. Bài ngắn hơn cũng được, máy chỉ đòi giọng đủ 18 giây. `bangChung` một dòng cũng được. Giá trong bảng giá chỉ đưa vào lời khi người dùng muốn.
- **Không nói muốn được giới thiệu tới ai:** AI suy ra từ nhóm khách và dịch vụ trong hồ sơ, ghi rõ "AI gợi ý" khi gửi các bản lời để người đó xác nhận. Người dùng nói "làm luôn" thì ghi `"xinDuyet": false` trong `soBni`.
- **Chưa có câu dễ nhớ:** đề xuất 2–3 câu ngay trong tin gửi các bản lời. Người dùng nói "làm luôn" thì chọn một câu và ghi `"cauDeNhoDuyet": false` trong `soBni`.
- Sổ có cờ `false` thì lần sau hỏi lại một câu cho chốt, rồi ghi `true`.
- **Không có ảnh:** báo trước rằng video sẽ dùng cảnh có sẵn hoặc nền màu, có ảnh thật sẽ đẹp hơn nhiều. Kho cảnh chưa có nghề đó thì cũng nói.
- **Hai mục tiêu trong một bài** (vừa tìm khách vừa tuyển người, vừa xin hai nhóm khác nhau): mỗi video một lời xin; hai nhóm chỉ được gộp khi cùng một dấu hiệu. Mục tiêu kia để video khác hay tuần sau, ghi vào `soBni.deDanh`.

## 5. Ngành có quy định quảng cáo

Gồm bảo hiểm, tài chính, đầu tư, y tế, nha khoa, làm đẹp có trị liệu, thực phẩm chức năng, giáo dục có cam kết đầu ra.
- Không hứa thu nhập, lợi nhuận, kết quả chắc chắn ("trị dứt", "cam kết đỗ", "thu nhập trăm triệu").
- Người làm đại lý hay nhân viên của một hãng thì thương hiệu trên video là tên của chính họ hoặc nhóm họ.
  - **Mặc định không nêu tên hãng.** Chỉ nhắc tên hãng như nơi họ làm ("tư vấn tại …") khi người đó tự nói hãng cho phép.
  - Không nêu khuyến mãi của hãng.
- Danh hiệu nội bộ ngành (MDRT, top doanh số): người ngoài nghe không hiểu, lại dễ nói sai khi diễn lại. Bỏ đi, hoặc chỉ nói đúng điều người dùng xác nhận.
- Video tuyển người làm cùng (dễ dính hứa thu nhập) không làm bằng khung này.
- Người dùng muốn nói những ý trên thì giải thích ngắn vì sao, rồi đề nghị cách nói an toàn, ví dụ kể việc đã làm được cho khách thay vì hứa. Đây là rào an toàn chung, không phải ý kiến pháp lý.

## 6. Tên riêng, chữ tiếng Anh, viết tắt

Giọng máy hay đọc sai tên thương hiệu, chữ tiếng Anh và viết tắt (ZENOTERA, VCCI, WOOD, AIA, MDRT, SME). Người lạ nghe viết tắt cũng khó hiểu.
1. Viết tắt chỉ người trong nghề biết thì thay bằng lời thường.
2. Tên riêng, hay chữ người dùng muốn giữ, thì ghi cách đọc vào `"docDung"` của `bni.json`, ví dụ `{"VCCI": "Vê Xê Xê I", "SME": "Ét Em I"}`. Phụ đề vẫn giữ chữ gốc; máy chỉ đổi lúc gửi cho giọng máy đọc. Cách đọc tên thương hiệu phải hỏi người dùng, không tự đoán.
3. Báo người dùng nghe lại đúng chỗ đó.

Chỉ có 2 giọng máy miễn phí, đều giọng Bắc (nam NamMinh, nữ HoaiMy). Người miền Nam hay miền Trung, hoặc muốn tự nhiên hẳn, thì khuyên tự quay giọng (SKILL.md bước 4b).

## 7. Phỏng vấn (một tin, chỉ hỏi cái còn thiếu, chữ dễ hiểu)

Đọc hồ sơ và sổ BNI trước, rồi bỏ những câu đã có lời đáp. Người bận hay hồ sơ mỏng thì chỉ hỏi 3 câu quan trọng nhất: 1, 3, 4, ghép thêm vào câu 1 nửa sau của câu 5 ("xưng gì, giọng máy hay tự quay"). Mỗi câu kèm một ví dụ trả lời thật ngắn.
1. Anh/chị giới thiệu mình thế nào: tên, làm nghề gì, khách chính là ai, họ được gì khi làm với anh/chị? Tên hiện trên video là tên anh/chị, tên cửa hàng, hay tên nhóm? Làm đại lý cho một hãng thì mặc định không nêu tên hãng (mục 5).
2. Video để đăng mạng, gửi nhóm (giới thiệu lần đầu) hay bài tuần BNI?
   - Chỉ hỏi khi sổ chưa có tuần nào. Trả lời "cả hai" thì làm bản giới thiệu lần đầu trước.
   - Bài tuần (kể cả khi suy ra từ sổ) thì luôn gợi ý 2–3 mảng chưa nói, và thêm câu "anh/chị chọn, hoặc em chọn theo chuyện anh/chị kể".
3. Một điều làm người ta tin anh/chị: một khách gần đây (lúc đến gặp chuyện gì, anh/chị làm gì, kết quả ra sao), một con số, hay một nơi đã làm? Có ảnh đúng việc đó không?
4. Anh/chị muốn có thêm khách nào? Họ hay than chuyện gì, hay đang gặp chuyện gì? Người quen của anh/chị nên rủ họ làm gì: nhắn Zalo, ghé cửa hàng, hay vào buổi học thử?
5. Anh/chị nói chuyện với khách kiểu nào, xưng gì? Muốn giọng máy (nam/nữ) hay tự quay giọng thật?
6. Có ảnh của mình không: ảnh rõ mặt, ảnh đang làm việc, ảnh với khách, cửa hàng? Gửi 1–5 tấm.

## 8. Theo giọng của người đó

- Lấy giọng từ ngăn giọng văn của bộ não và câu trả lời câu 5: từ hay dùng, cách xưng hô, câu dài hay ngắn, có đùa không.
- Viết **2–3 bản khác giọng** cho cùng nội dung. Ví dụ: một bản ấm kể chuyện, một bản chắc có số, một bản vui. Mỗi bản ghi một dòng "giọng gì, mở bằng gì" rồi lời đọc. Họ đã nói "làm luôn" thì chọn bản hợp hồ sơ nhất và nói rõ đã chọn bản nào.
- Dấu câu theo cách người đó nói. Dùng chữ của nghề họ, không dùng chữ sáo ("uy tín hàng đầu", "giải pháp toàn diện").

## 9. Hướng nghĩ theo ngành (KHÔNG chép)

Với mọi ngành, AI tự trả lời 4 câu từ hồ sơ của người đó:
- Mảng nhỏ nào khách hay cần nhất?
- Chuyện thật nào dễ hình dung nhất?
- Ai thường gặp đúng loại khách đó trước mình?
- Khách đó hay than gì?

Vài hướng để học cách nghĩ:
- **Bảo hiểm:** người gặp khách trước là người làm việc với gia đình trẻ hay chủ shop. Dấu hiệu là họ vừa có con, vừa mở cửa hàng.
- **Làm đẹp:** studio ảnh, tiệm áo cưới. Dấu hiệu là khách sắp có dịp quan trọng.
- **Kế toán, thuế:** luật sư, ngân hàng. Dấu hiệu là khách bị hỏi sổ sách, hồ sơ vay bị trả.
- **Nội thất, xây sửa:** môi giới. Dấu hiệu là khách vừa nhận nhà.
- **Đồ ăn, tiệc:** hành chính nhân sự công ty. Dấu hiệu là sắp có tiệc cuối năm.
- **Đào tạo:** trưởng phòng nhân sự. Dấu hiệu là nhân viên sắp phải làm việc mới.

Đây chỉ là ví dụ cách nghĩ. Người được giới thiệu tới phải lấy từ hồ sơ và câu trả lời của chính người dùng, không lấy từ danh sách này, để học viên cùng ngành không ra cùng một lời xin. Chuyện và chữ phải là của người đó: tên khách, số, giờ, nơi chốn, câu họ hay nói.

`nganh` trong `bni.json`:
- Chép ĐÚNG từ khóa trong cột từ khóa của `<Xưởng>/tai-nguyen/canh/CHI_MUC.md` (máy chỉ khớp nguyên từ khóa, và nhắc khi ghi sai). Dò bằng Grep chữ nghề không dấu trong tệp đó.
- Người ở Hà Nội hay Sài Gòn muốn có cảnh thành phố mình thì thêm `ha-noi` hoặc `sai-gon`.
- Chưa có tệp đó, hoặc không có từ khóa hợp nghề, thì để `nganh` rỗng và nói với người dùng như mục 4.

## 10. Câu dễ nhớ

- Câu tả nghề sống động, người nghe hình dung được, đọc dưới 3 giây. Chơi chữ hay có vần thì tốt, không bắt buộc.
- Chọn một lần, giữ nguyên qua các tuần (ghi trong sổ BNI). Chỉ đổi khi người đó muốn.
- `ghiNho` là bản ngắn của câu này hiện trên thẻ kết, tối đa 18 ký tự.

## 11. Sổ BNI của từng người

Tệp `<Xưởng>/mau-cua-toi/bni/so-bni.json` nằm trong vùng của học viên; bộ cài không bao giờ ghi đè. `bni.py` ghi thêm một dòng sau mỗi video đạt:

```json
{"ten": "Nguyễn Văn A", "cauDeNho": "câu dễ nhớ đọc ra", "ghiNho": "BẢN NGẮN TRÊN THẺ", "giong": "ấm áp, xưng mình",
 "mang": ["các mảng nhỏ có thể nói, mỗi tuần một"],
 "tuan": [{"ngay": "2026-11-25", "chuDe": "...", "xin": "...", "duAn": "2026-11-25_bni-...", "loi": "toàn bộ lời đọc"}]}
```

Sổ còn có các khóa `cauDeNhoDuyet`, `xinDuyet` (cờ chưa duyệt, mục 4) và `deDanh` (lời xin, mục tiêu để video sau). `soBni.mang` và `soBni.deDanh` được nối thêm vào sổ, không thay hẳn.

Trước khi viết bài tuần:
- Đọc sổ, chọn mảng chưa nói trong **4 bài gần nhất**.
- Mảng đã nói thì sau 4 bài được dùng lại, kể chuyện khác. Mảng mới mà chuyện gần mảng cũ thì vẫn được, miễn là góc nhìn khác, và nói rõ điều đó với người dùng.
- Hết mảng thì đề xuất mảng mới từ ngăn sản phẩm và khách hàng, rồi ghi vào `soBni.mang`. Hai ngăn đó trống thì hỏi người dùng một câu: "tuần này anh/chị muốn nói về việc gì?".
- Có lời xin trong `deDanh` thì ưu tiên dùng.

## 12. Lỗi hay gặp

- Chưa nói rõ mình là ai, làm gì, cho ai mà đã kể chuyện hay nêu chủ đề tuần (Founder chấm 25/11/2026).
- Câu vụn, câu kiểu tiêu đề, mở bằng mảnh câu người lạ không hiểu.
- Kể hết danh sách dịch vụ thay vì một mảng; xin chung chung ("ai cần thì giới thiệu", "bất kỳ ai").
- Thiếu dữ liệu mà bịa chuyện hay độn chữ cho đủ dài (thử 25/11/2026: máy cũ đòi thêm chữ, AI suýt bịa câu khách nói).
- Khuôn chữ của chính tệp này lọt vào lời (chấm 25/11/2026: bài nào cũng chuyển ý bằng "Tuần này", lời xin bằng "… nói giúp:"). Khung chỉ cần CÓ các ý, cách nói là của từng người.
- Thẻ danh sách (`chuDe.viec`, `xin.dong`) chỉ dùng khi nhịp đó THẬT có 2–3 ý, mỗi ý dùng chữ được nói trong chính nhịp đó (máy chặn nếu không có). Chỉ một ý thì để danh sách rỗng, thẻ thành cảnh có chữ. `bangChung` nên là kết quả ngắn của câu chuyện, không lộ hết chuyện trước khi kể.

## Nguồn (truy cập 25/11/2026)

- BNI chính thức: phần giới thiệu hằng tuần là để dạy cả phòng biết một lời giới thiệu tốt cho mình trông thế nào, không phải bán hàng. https://www.bni.com/the-latest/blog-news/what-happens-at-a-bni-meeting/
- Tài liệu đào tạo BNI Úc: chào → một mảng nhỏ (LCD) → giải thích → lời xin cụ thể → kết bằng tên và câu dễ nhớ. https://docs.google.com/presentation/d/1bZB1hooTONHlLJaIhb5SPRrnd-7JZybc/htmlpresent
- Ivan Misner (người sáng lập BNI): chia việc kinh doanh thành các mảng nhỏ nhất, mỗi tuần nói một mảng. https://www.goodreads.com/author_blog_posts/14916518-specific-is-terrific-with-lcd-s
- Official BNI Podcast tập 959: nói cụ thể, kể chuyện theo 3 nhịp tình huống → khó khăn → giải pháp. https://pod.wave.co/podcast/the-official-bni-podcast/episode-959-make-yourself-referrable
- Misner trên Entrepreneur: câu dễ nhớ là câu tả nghề sống động. https://www.entrepreneur.com/growing-a-business/entrepreneur-business-be-remembered-at-networking-events/60516
- Andy Bounds (BNI UK Podcast): mỗi bài trả lời muốn tới ai, vì sao người đó được lợi, người giới thiệu nên mở lời thế nào. https://shows.acast.com/the-bni-uk-podcast/episodes/6982059e19ef991f73a67716
