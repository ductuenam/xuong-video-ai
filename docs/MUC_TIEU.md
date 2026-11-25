---
status: draft
version: 0.1.0
updated: 2026-11-25
owner: Founder Đức Tuệ Nam
---

# MỤC TIÊU XƯỞNG VIDEO AI — bám sát tệp này khi cải tiến

> Bản Claude soạn ngày 25/11/2026 từ toàn bộ trao đổi với Founder, **chờ Founder duyệt**. Mọi đề xuất thay đổi bộ cài, skill, kho tài nguyên đều phải trả lời được: *"Việc này giúp học viên làm video nhanh hơn, tốt hơn hay dễ hơn ở chỗ nào?"*

## 1. Mục tiêu trong một câu

**Học viên ZENOTERA AI Academy, dù không biết kỹ thuật và chỉ có máy 8 GB RAM, dán một câu lệnh là có ngay một xưởng làm video tự động nằm trong Bộ Não AI của mình. Xưởng lấy nội dung thật từ bộ não, tự chọn đúng cảnh, nhạc, tiếng, rồi dựng ra video ngắn dùng được cho kinh doanh. Về sau, học viên chỉ cần dán lại đúng câu lệnh đó là nhận thêm skill và tài nguyên mới, không mất những gì đã làm.**

## 2. Hành trình của học viên (năm bước)

| Bước | Học viên làm | Hệ thống lo | Trạng thái 25/11 |
|---|---|---|---|
| **1. Cài bộ não** | Cài Claude Code (gói Pro, máy tính), dán **câu lệnh tải bộ não** (ở phần mô tả bài học trên AIA) | Tải kho "Bộ Não AI Khởi Động" (`github.com/ductuenam/bo-nao-ai-khoi-dong`), dựng các ngăn 00–07; câu kích hoạt hướng dẫn nạp tài liệu, **chỉ ghi khi học viên gõ OK** | Đã có, đang dùng |
| **2. Cài xưởng video** | Mở Claude đúng thư mục bộ não, dán **một câu lệnh cài xưởng** | Kiểm máy, chọn gói nhẹ hoặc đủ theo RAM và ổ trống, tải phần mềm + kho cảnh/nhạc/tiếng từ R2, kiểm mã, thêm ngăn `08_XUONG_VIDEO`, chép skill cấp 1, dựng thử 10 giây, báo `XƯỞNG SẴN SÀNG` | Kho tài nguyên v1 xong; **bộ cài chưa viết** |
| **3. Thực hành** | Nói một câu: "dựng video giới thiệu bản thân theo BNI", "edit video <tệp>"… | Lấy lời từ ngăn 01–05 (không bịa), chọn cảnh qua chỉ mục, dựng, tự chấm, trả thành phẩm | Skill có sẵn (mã kế thừa), **chưa sửa theo kho mới** |
| **4. Làm video nâng cao** | Nói việc muốn làm (ảnh bìa vẽ AI, KOL AI…), không phải "mở" gì vì mọi skill đã cài sẵn | Kiểm điều kiện lúc làm (`CHUAN_BI_THEM.md`): đủ thì làm luôn; thiếu tài khoản/khóa thì báo cần chuẩn bị gì, cách làm, có tốn phí không, và đề xuất cách làm được ngay | Thiết kế xong 25/11; bộ cài và skill chưa làm |
| **5. Nhận cập nhật, tự mở rộng** | Dán lại câu lệnh cài. Muốn lưu kiểu video riêng, thêm cảnh/nhạc của mình thì nói một câu | Tải phiên bản mới (gói không đổi thì không tải lại); đồ `cua-toi`, `mau-cua-toi` không bao giờ bị ghi đè | Quy chuẩn và công cụ phía kho xong; **skill `xuong-mo-rong` chưa viết** |

## 3. Học viên là ai (thiết kế cho họ)

- Chủ doanh nghiệp nhỏ, chủ yếu ngành dịch vụ, dưới khoảng 20 người, **tự làm marketing và bán hàng mỗi ngày**; kèm chuyên gia, huấn luyện viên làm một mình. Họ cần video đều đặn để bán hàng, không có thời gian học dựng phim.
- Không biết code, không quen dòng lệnh. Máy Windows hoặc Mac, nhiều máy chỉ có 8 GB RAM, mạng có lúc chập chờn.
- Nói và đọc tiếng Việt; video làm cho khách Việt.
- Đã có Bộ Não AI từ bước 1, đó là nguồn nội dung chính.

## 4. Thế nào là "đạt" (thước đo)

Phần 1–5 đã ghi trong `KIEN_TRUC.md`. Phần 6–10 là **con số em đề xuất, chờ Founder chốt**.

1. Chỉ một câu lệnh. Không cần Git, winget, Homebrew, quyền quản trị, không gõ mật khẩu máy.
2. Máy 8 GB RAM dựng được video BNI và Edit video.
3. Dán lại câu lệnh là cập nhật; dữ liệu bộ não, video, mẫu và cảnh riêng của học viên còn nguyên.
4. Học viên tự thêm kiểu video, cảnh, nhạc của mình bằng một câu nói.
5. Nội dung lời trong video lấy từ bộ não, không bịa.
6. *(Đề xuất)* Cài xong trong **≤ 20 phút** với mạng 20 Mbps, gói nhẹ.
7. *(Đề xuất)* Video đầu tiên (BNI khoảng 30 giây) ra trong **≤ 15 phút** kể từ khi cài xong.
8. *(Đề xuất)* **≥ 9/10 cảnh** AI chọn hợp với câu nói đi kèm (chấm trên 3 video mẫu mỗi lần phát hành).
9. *(Đề xuất)* Học viên lần đầu tự làm đúng hết các bước, không phải hỏi nhóm hỗ trợ về cài đặt, ở **≥ 8/10 lần thử**.
10. *(Đề xuất)* Mọi tài nguyên phát cho học viên đều rõ nguồn và quyền dùng.

## 5. Nguyên tắc thiết kế (không đánh đổi)

1. **Bộ não là trung tâm.** Xưởng nằm trong bộ não, đọc nội dung từ bộ não; không bắt học viên tìm hay chọn thư mục.
2. **Chọn bằng chỉ mục, không bằng tên tệp.** AI đọc `CHI_MUC.md` (mô tả, từ khóa, chuyển động, chỗ đặt chữ, dấu in sẵn), muốn xem thì mở ảnh xem trước, cuối cùng mới dùng video. Nhãn đúng với hình là sống còn.
3. **Nhẹ mà vẫn nét.** Video dọc 720×1280, nén CPU CRF 22, SSIM ≥ 0,97. Có gói nhẹ cho máy yếu. Whisper chọn theo RAM.
4. **Cài đủ một lần, thiếu gì nhắc nấy.** Mọi skill cài sẵn, không chia cấp. Việc nào cần tài khoản, khóa hay máy mạnh hơn thì Claude kiểm đúng lúc làm và hướng dẫn chuẩn bị; đủ rồi thì làm theo ý người dùng, không hỏi thừa. Thông tin nội dung chưa rõ thì tìm trong bộ não, không có thì hỏi hoặc đề xuất.
5. **Của học viên là bất khả xâm phạm.** `cua-toi`, `chu=hoc-vien`, `mau-cua-toi` không bao giờ bị ghi đè. Tùy biến nằm ngoài skill gốc.
6. **Cải tiến liên tục theo phiên bản.** Mã ở GitHub, tài nguyên ở R2, gói đã phát hành thì khóa, mỗi lần bổ sung là `v<N+1>`. Quy trình và công cụ ở `BAN_DO_KHO.md`, `cong-cu/`.
7. **Sạch tên và sạch quyền.** Không mang tên đơn vị cũ ("An Bình"), không phát lại nguyên tệp nhạc; tài nguyên chưa rõ quyền phải ghi rõ và có kế hoạch thay.
8. **Tự kiểm trước khi giao.** Skill tự soát và có người chấm độc lập; bộ cài dựng thử trước khi báo sẵn sàng; kho chạy `kiem_kho.py` trước mỗi lần phát hành.

## 6. Hiện trạng so với mục tiêu (25/11/2026)

| Mảng | Đã có | Còn thiếu |
|---|---|---|
| Kho tài nguyên | v1: 226 cảnh (23 nhóm, 64 nhẹ), 3 nhạc, 7 tiếng; nén, đặt tên, gắn nhãn 2 vòng, đóng gói, Founder duyệt mẫu | Kho thiên về cảnh công nghệ/AI; ít cảnh ngành nghề của học viên; 7 tiếng chưa rõ quyền |
| Bộ cài | Kiến trúc, `PHIEN_BAN.json`, khung ngăn `xuong-mau/` | `cai/` (Windows + Mac) |
| Skill | 9 skill, 23 agent xếp 3 gói, cài đủ một lần; danh mục điều kiện `CHUAN_BI_THEM.md` (chép nguyên mã kế thừa) | Sửa đường dẫn kho mới, mã cảnh cũ, tên nhạc mới, Whisper theo RAM, bỏ tên riêng; skill `xuong-mo-rong` |
| Phát hành | Quy trình, công cụ đóng gói, kiểm kho | Founder tạo R2 + tên miền, kho GitHub, tải gói |
| Thử thật | Thử công cụ kho trên bản sao | Thử bộ cài trên máy 8 GB thật và một máy Mac |

## 7. Cố vấn: con đường tới mục tiêu

**Thứ tự em khuyên** (việc trước mở đường cho việc sau):

1. **Bộ cài đủ + video người nói chạy trọn từ đầu đến cuối**: bộ cài Windows cài mọi skill, kiểm điều kiện và in bảng "làm được ngay / cần chuẩn bị thêm"; sửa `video-ngan-nguoi-noi` theo kho mới → học viên dán một câu lệnh là ra video BNI. Đây là lời hứa chính, và cũng sửa luôn chỗ máy anh đang thiếu cảnh chèn.
2. **Anh tạo R2 + kho GitHub và tải gói v1 lên.** Thiếu bước này thì bộ cài không có gì để tải.
3. **Thử trên máy thật 8 GB** (một học viên hoặc máy cũ) rồi một máy Mac. Đo thời gian theo thước đo 6–7, ghi lại mọi chỗ vấp để sửa.
4. **Skill `xuong-mo-rong`** (lưu kiểu video của tôi, thêm cảnh/nhạc của tôi). Có nó thì học viên tự làm giàu xưởng của mình.
5. **Sửa dần các skill còn lại** theo kho mới và cổng sẵn sàng (cắt ghép, ảnh bìa, KOL AI), ưu tiên skill học viên dùng nhiều.

**Những điểm em thấy cần lưu ý:**

- **Kho cảnh nên bổ sung theo ngành của học viên.** 226 cảnh hiện tại phần lớn là công nghệ, AI, màn hình ảo, rất hợp video về AI. Nhưng học viên là chủ spa, bất động sản, giáo dục, ăn uống, dịch vụ… Bản v2 nên thêm cảnh theo 5–7 ngành phổ biến nhất trong lớp. Hỏi ngành ngay lúc học viên đăng ký là biết cần làm gì trước.
- **Bổ sung theo dữ liệu thật, không theo cảm tính.** Khi dựng, skill ghi lại câu nói nào không tìm được cảnh hợp. Tổng hợp các câu đó mỗi tuần thành danh sách cảnh cần làm thêm.
- **Quyền dùng là rủi ro khi phát cho số đông.** Nên thay 7 tiếng `chua-ro` bằng tiếng CC0 ở v2. Nhạc chỉ nhận nguồn có giấy phép rõ.
- **Nói rõ chi phí ngay từ đầu.** Bảng cuối bộ cài và `CHUAN_BI_THEM.md` ghi việc nào miễn phí, việc nào cần tài khoản trả phí (khóa Google, Muse), để học viên không kẹt giữa chừng.
- **Hỗ trợ là một phần sản phẩm.** Mỗi lỗi hay gặp khi cài nên có một mục trong sổ trả lời của nhóm hỗ trợ (`docs/04_CURRICULUM_AND_DELIVERY/HO_TRO_HOC_VIEN/`), kèm cách tự sửa.

## 8. Cách dùng tệp này

- Đọc ở đầu mỗi đợt làm xưởng video (sau `BAN_DO_KHO.md`).
- Đề xuất nào không phục vụ mục 1–5 thì để sau.
- Founder chốt điều gì (thước đo, thứ tự, ngành cần thêm cảnh) thì sửa ngay tại đây, ghi ngày. Tiến độ việc ghi ở ZAIOS Core, không ghi checklist ở đây.
