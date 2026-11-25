---
status: draft
version: 0.2.1
updated: 2026-11-25
owner: Founder Đức Tuệ Nam
---

# MỤC TIÊU XƯỞNG VIDEO AI — bám sát tệp này khi cải tiến

> Bản Claude soạn từ toàn bộ trao đổi với Founder (bản 0.1.0 sáng 25/11, bản 0.2.0 tối 25/11 sau khi thử bộ cài thật), **chờ Founder duyệt**. Mọi đề xuất thay đổi bộ cài, skill, kho tài nguyên đều phải trả lời được: *"Việc này giúp học viên làm video nhanh hơn, tốt hơn hay dễ hơn ở chỗ nào?"*
>
> Hỏi gì về xưởng (cài, cập nhật, thêm tài nguyên, tùy biến, lưu ở đâu) thì đọc tệp này trước, rồi mới tới `BAN_DO_KHO.md` (vị trí từng thứ, quy trình), `LUU_TRU_VA_PHAT_HANH.md` (R2, phát hành), `QUY_CHUAN_MO_RONG.md` (khuôn tài nguyên và tùy biến).

## 1. Mục tiêu trong một câu

**Học viên ZENOTERA AI Academy, dù không biết kỹ thuật và chỉ có máy 8 GB RAM, dán một câu lệnh là có ngay một xưởng làm video tự động nằm trong Bộ Não AI của mình. Xưởng lấy nội dung thật từ bộ não, hỏi đúng những gì còn thiếu, tự chọn cảnh, nhạc, tiếng, rồi dựng ra video ngắn dùng được cho kinh doanh. Về sau, học viên chỉ cần dán lại đúng câu lệnh đó là nhận thêm skill và tài nguyên mới, không mất những gì đã làm.**

## 2. Câu lệnh gửi học viên (bản chuẩn, copy nguyên khối)

Nguồn gốc duy nhất: `cai/README.md`. Sửa câu lệnh thì sửa ở đó rồi chép lại vào đây.

Học viên mở Claude (thẻ Code, **This computer**), chọn **đúng thư mục Bộ Não AI** đã cài ở buổi trước, rồi dán:

```
Cài Xưởng Video AI vào bộ não này. Chạy đúng một lệnh theo máy của tôi, ngay trong thư mục đang mở, chờ chạy xong rồi báo kết quả bằng tiếng Việt dễ hiểu:
- Windows: powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.ps1 | iex"
- Mac: curl -fsSL https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.sh | bash
Lệnh chạy lâu (10–30 phút): chạy nền và chờ, đừng chạy lại giữa chừng. Nếu lệnh DỪNG thì đọc dòng DỪNG và làm đúng hướng dẫn trong đó. Có dòng ⚠ thì giải thích cho tôi và làm theo dòng đó (hỏi tôi trước khi xóa hay chuyển thứ gì).
```

Dặn thêm học viên:
- Cài xong **đóng hẳn Claude rồi mở lại** đúng thư mục bộ não.
- Muốn cập nhật (từ bản 0.2.6): mở Claude đúng thư mục bộ não, gõ **`/cap-nhat-xuong`** (hoặc nhắn "Cập nhật Xưởng Video AI"). Không có gì mới thì Claude báo ngay một dòng; có thì tự tải phần mới, đặt đúng chỗ, báo "có gì mới". Dán lại câu cài ở trên cũng được, kết quả như nhau.
- Không dùng câu cài cũ từ kho `an-binh-video-ai`. Câu cũ chép skill vào thư mục chung của máy (`C:\Users\<tên>\.claude\skills`), và Claude sẽ dùng bản cũ đó thay bản mới. Bộ cài mới tự phát hiện và nhắc chuyển bản cũ vào Thùng rác.
- Thử lần đầu: *"Dựng video giới thiệu bản thân cho tôi theo cấu trúc BNI"*.

## 3. Hành trình của học viên (năm bước)

| Bước | Học viên làm | Hệ thống lo | Trạng thái 25/11 tối |
|---|---|---|---|
| **1. Cài bộ não** | Cài Claude Code (gói Pro, máy tính), dán **câu lệnh tải bộ não** | Tải kho "Bộ Não AI Khởi Động", dựng các ngăn 00–07; **chỉ ghi khi học viên gõ OK** | Đã có, đang dùng |
| **2. Cài xưởng video** | Mở Claude đúng thư mục bộ não, dán **câu lệnh ở mục 2** | Kiểm máy; chọn gói cảnh đủ/nhẹ theo RAM và ổ; tải phần mềm (không cần quyền quản trị, không cần Git); tự lo Visual C++; tải kho cảnh/nhạc/tiếng từ R2 (kiểm mã sha256, đứt mạng tải tiếp); thêm ngăn `08_XUONG_VIDEO`; chép đủ skill, agent; dựng thử; báo `XƯỞNG SẴN SÀNG` | **Xong, bản 0.2.5.** Đã thử thật từ GitHub trên bộ não mới tinh (mục 7) |
| **3. Thực hành** | Nói một câu: "tôi muốn làm video giới thiệu bản thân", "edit video <tệp>"… | Đọc bộ não, nhắc lại thông tin đã có, **hỏi một lượt** cái còn thiếu (kèm gợi ý, cho trả lời "làm luôn"), dựng, tự soát, cho người chấm độc lập chấm, trả thành phẩm; **xin OK trước khi ghi vào bộ não** | **Video BNI xong (skill bản 2.2)**; edit video chạy được |
| **4. Làm video nâng cao** | Nói việc muốn làm (ảnh bìa vẽ AI, KOL AI…) | Kiểm điều kiện lúc làm (`CHUAN_BI_THEM.md`): đủ thì làm luôn; thiếu tài khoản/khóa thì báo thiếu gì, cách chuẩn bị, có tốn phí không, và đề xuất cách làm được ngay | Đã thử: xin video KOL thì báo đúng thiếu Claude in Chrome, Muse (có phí), mặt KOL |
| **5. Nhận cập nhật, tự mở rộng** | Gõ `/cap-nhat-xuong` khi rảnh (hoặc khi Founder báo có bản mới). Muốn lưu kiểu video riêng, thêm cảnh/nhạc của mình thì nói một câu | Không có gì mới: báo một dòng, không đụng gì. Có mới: thay mã, chỉ tải **gói bổ sung** cảnh/nhạc mới, đặt đúng chỗ, báo "có gì mới"; đồ `cua-toi`, `mau-cua-toi`, video đã làm không bao giờ bị ghi đè | **Xong bản 0.2.6, đã thử** trên bộ não giả (mục 5.3). Skill `xuong-mo-rong`: **chưa viết** |

## 4. Học viên là ai (thiết kế cho họ)

- Chủ doanh nghiệp nhỏ, chủ yếu ngành dịch vụ, dưới khoảng 20 người, **tự làm marketing và bán hàng mỗi ngày**; kèm chuyên gia, huấn luyện viên làm một mình. Cần video đều đặn để bán hàng, không có thời gian học dựng phim.
- Không biết code, không quen dòng lệnh. Máy Windows hoặc Mac, **nhiều máy 8 GB RAM, có máy chỉ 4 GB**, mạng có lúc chập chờn, có máy chưa từng cài Visual C++.
- Nói và đọc tiếng Việt, ba miền; video làm cho khách Việt.
- Đã có Bộ Não AI từ bước 1, đó là nguồn nội dung chính.

## 5. Cập nhật: Founder thêm gì thì học viên nhận ra sao

Có **ba loại thứ** Founder có thể thêm. Mỗi loại đi một đường khác nhau.

### 5.1 Mã, skill, agent, tài liệu hướng dẫn (chữ và code)

- **Ở đâu:** kho GitHub công khai `ductuenam/xuong-video-ai` (thư mục `goi/`, `cai/`, `xuong-mau/`, chỉ mục tài nguyên `tai-nguyen/*/chi-muc.csv`).
- **Founder làm:** nói với Claude cần sửa hay thêm gì. Claude sửa, thử trên bộ não giả, rồi đẩy lên GitHub (`git push`), kèm tăng số phiên bản trong `PHIEN_BAN.json`.
- **Có tự đồng bộ xuống máy học viên không:** **không tự động.** Đẩy lên GitHub là bản mới sẵn sàng ngay, nhưng máy học viên chỉ nhận khi **học viên gõ `/cap-nhat-xuong`** (hoặc dán lại câu lệnh cài).
- **Luật cho người làm kho:** mỗi lần đẩy thứ muốn học viên nhận, **tăng `phien_ban`** trong `PHIEN_BAN.json` và thêm một dòng `co_gi_moi` bằng tiếng Việt dễ hiểu. Không tăng số thì máy học viên báo "đã là bản mới nhất" và không nhận.
- **Học viên tải gì khi cập nhật:** cả bộ mã, chỉ vài MB, chưa tới một phút. Skill và agent của kho được chép đè bằng bản mới; mọi thứ của học viên được giữ (mục 5.4). Phần mềm đã có (Python, FFmpeg, Node, Remotion, Whisper) không tải lại.

### 5.2 Tài nguyên: cảnh video, nhạc, tiếng hiệu ứng (tệp nặng)

- **Ở đâu:** tệp thật để trên Cloudflare R2 (`taivido.zenotera.com`), đóng thành gói theo phiên bản `v1`, `v2`…; **chỉ mục** (mô tả, từ khóa từng cảnh) đi theo GitHub. Bản đã phát hành là khóa, không ghi đè.
- **Founder làm:** thả tệp vào `_kho-nang\nguon-moi\canh\` (hoặc `nhac\`, `am\`), nói "bổ sung kho". Claude nén, gắn nhãn, soát chéo, Founder duyệt tờ mẫu, đóng gói `v<N+1>`. Founder tự tải gói lên R2 (nhập mật khẩu két). Claude điền đường dẫn vào `PHIEN_BAN.json` rồi đẩy GitHub. Quy trình đầy đủ: `BAN_DO_KHO.md` mục 5.
- **Có tự đồng bộ không:** cũng **không tự động**; học viên nhận khi dán lại câu lệnh.
- **Đã giữ được:** cùng phiên bản thì không tải lại; khi giải nén, tệp đã có và đúng cỡ thì bỏ qua; dòng chỉ mục của học viên (`chu=hoc-vien`) và thư mục `cua-toi` không bị đụng.

### 5.3 Cập nhật chỉ tải phần bổ sung (làm xong bản 0.2.6, 25/11 tối)

Trước bản 0.2.6, mỗi lần lên phiên bản tài nguyên mới bộ cài **tải lại nguyên gói** (882 MB / 217 MB / 18 MB) dù chỉ thêm vài cảnh. Nay:

- **Đóng gói:** `dong_goi.py --phien-ban v<N+1>` ngoài 3 gói đủ còn đóng **`bo-sung-v<N>-v<N+1>.zip`**, chỉ chứa tệp mới hoặc đã đổi (so mã CRC từng tệp với gói bản trước), và ghi vào mục `goi_bo_sung` của `PHIEN_BAN.json`. `tai_len_r2.py` tự tải gói này lên cùng.
- **Máy học viên:** bộ cài nhớ bản đang có (`xuong.json`). Đang ở v1 mà kho đã lên v3 thì tải `bo-sung-v1-v2` rồi `bo-sung-v2-v3`, chỉ giải nén tệp đúng gói nhẹ/đủ của máy đó vào `tai-nguyen/`. Thiếu một mắt xích, hoặc máy mới cài, thì tải gói đủ như cũ.
- **Không có gì mới** (mã và tài nguyên đều cùng số): bộ cài in `✔ ĐÃ LÀ BẢN MỚI NHẤT` và dừng ngay, không chạy bước nào, chỉ tốn vài giây tải gói mã vài MB.
- **Có bản mới:** cuối cùng in `ĐÃ CẬP NHẬT 0.2.5 → 0.2.6. Có gì mới:` kèm các dòng `co_gi_moi` của những bản học viên chưa có.
- **Học viên làm:** gõ `/cap-nhat-xuong` (skill mới, cài cùng xưởng). Claude chạy lệnh, đọc kết quả, báo lại bằng lời dễ hiểu. Nói "cài lại xưởng" thì Claude thêm `XUONG_CAI_LAI=1` để chạy đủ các bước sửa máy (vẫn không tải lại tài nguyên đã có).

**Đã thử 25/11** (thế giới tí hon trong `%TEMP%\zaios_cap_nhat_2511`, không đụng kho thật và R2; 16/16 mục ĐẠT): cài mới v1 tải gói đủ; chạy lại báo "đã là bản mới nhất"; ra v2 thêm 1 cảnh, sửa 1 tiếng → gói bổ sung đúng 3 tệp; cập nhật **xóa gói đủ v2 khỏi nơi tải mà vẫn lên được** (chứng minh chỉ tải bổ sung), cảnh mới vào đúng chỗ, tiếng sửa được thay; cảnh riêng, thành phẩm, dòng `chu=hoc-vien` còn nguyên; in đúng dòng "có gì mới" của 0.2.6; skill `cap-nhat-xuong` có trong bộ não; `XUONG_CAI_LAI=1` chạy đủ bước. Các bước nặng (thư viện, Remotion, Whisper, dựng thử) được thay bằng bản giả trong lần thử này; phần đó đã thử thật ở mục 7.

### 5.4 Thứ của học viên không bao giờ bị đụng khi cập nhật

Đã thử thật ngày 25/11 (bộ não thử "Bộ Não AI của Lan"): sau khi cập nhật, ghi chú riêng, cảnh riêng, dòng chỉ mục riêng, mục 5 "Của tôi" trong `CHI_MUC_XUONG.md` và video đã làm đều còn nguyên.

- Các ngăn 00–07 của bộ não (xưởng chỉ đọc; muốn ghi thì xin OK).
- `08_XUONG_VIDEO/du-an/`, `thanh-pham/`, `anh-video-cua-toi/`, `mau-cua-toi/`, `ho-so-kenh.json`.
- Mọi đường dẫn có `cua-toi`, mọi dòng `chu=hoc-vien`.
- Tệp học viên tự thêm vào trong thư mục skill (bộ cài chỉ chép đè tệp của kho, không xóa tệp lạ).

### 5.5 Đề xuất thêm (chờ Founder duyệt)

- **Nhắc có bản mới:** khi học viên làm video, Claude so số phiên bản trên máy với `PHIEN_BAN.json` trên GitHub. Có bản mới thì nhắc một dòng "Xưởng có bản mới (thêm X cảnh ngành spa…), gõ /cap-nhat-xuong để nhận". Học viên không phải theo dõi nhóm Zalo. *(Chưa làm.)*
- ~~Ghi thay đổi cho học viên~~: **đã làm 0.2.6** (mục `co_gi_moi` trong `PHIEN_BAN.json`).

## 6. Mức linh động: làm video theo ý mình được tới đâu

Mục tiêu Founder đặt: **linh động tối đa.** Skill là đường mòn đã thử kỹ, không phải giới hạn.

### 6.1 Làm được ngay (25/11)

| Học viên muốn | Được không | Cách |
|---|---|---|
| Video giới thiệu bản thân, edit video quay thô, cắt livestream, biến thể quảng cáo, ảnh bìa, video KOL AI, cây cảnh | Được | Mỗi loại có skill riêng, đã thử |
| Đổi nội dung, độ dài, giọng, cách xưng hô, câu chữ trong các loại trên | Được | Nói thẳng ý muốn; khung chỉ giữ mạch, lời AI viết riêng cho từng người (ví dụ BNI: khung 5 nhịp, không cứng) |
| Video theo chủ đề tự chọn, không quay mặt (đồ họa + giọng AI + cảnh kho) | Được | Skill `video-ngan-nguoi-noi` phần "Không quay": tự viết kịch bản từ chủ đề hoặc video mẫu, ghép từ các loại cảnh có sẵn |
| Làm giống một video mẫu người dùng đưa | Được, trong phạm vi các loại cảnh có sẵn | Skill phân tích mẫu, viết lại kịch bản, ghép bằng các loại cảnh dưới đây |
| Dùng ảnh, video, sản phẩm của chính mình | Được | Thả vào `anh-video-cua-toi/` hoặc thư mục `anh/` của dự án |

**Các loại cảnh có sẵn để AI tự ghép** (mỗi câu nói chọn một loại): cảnh có chữ trên clip kho hoặc ảnh của học viên (`flow-chu`); danh sách bước (`danh-sach-buoc`); so sánh hai phía (`hai-phe`, `truoc-sau`); con số (`nguoi-so`); khung chat với AI (`khung-chat`); thẻ nhắc (`canh-bao`); cảnh kết mời liên hệ (`ket-comment`). Kèm phụ đề, nhạc, tiếng hiệu ứng. Chi tiết: `goi/video-nguoi-noi/skills/video-ngan-nguoi-noi/references/mo-hinh-canh.md`.

### 6.2 Chưa làm được hoặc chưa tiện

- **Kiểu hình mới hoàn toàn** chưa có trong các loại cảnh trên (ví dụ chữ chạy kiểu điện ảnh, chia đôi màn hình hai người nói, bản đồ chuyển động): Claude của học viên có thể tự viết thêm, nhưng dễ lỗi và mất công. Cách đúng: Founder thấy kiểu nào nhiều người cần thì nói với Claude ở kho này, thêm thành **mẫu cảnh mới**, thử kỹ, phát hành qua cập nhật (mục 5.1). Mọi học viên cùng nhận.
- **Lưu kiểu video riêng để lần sau gọi lại** ("Lưu kiểu video này của tôi"): khuôn đã có (`mau-cua-toi/<ten-kieu>/MAU.md`), **skill `xuong-mo-rong` chưa viết**. Hiện Claude vẫn làm được bằng tay nếu học viên yêu cầu, nhưng chưa thống nhất.
- **Thêm cảnh, nhạc của riêng học viên vào kho** ("Thêm cảnh này vào kho"): khuôn đã có (`tai-nguyen/<loai>/cua-toi/` + dòng `chu=hoc-vien`), cũng chờ skill `xuong-mo-rong`.
- **Cảnh theo ngành của học viên:** kho v1 thiên về công nghệ/AI; chưa có cảnh spa, bảo hiểm, ăn uống, bất động sản… Không có ảnh thật thì video chỉ dùng được nền màu dịu.

### 6.3 Hướng để linh động tối đa (thứ tự em khuyên)

1. **Skill `xuong-mo-rong`:** học viên nói một câu là lưu kiểu video, thêm cảnh/nhạc của mình, ghi rút kinh nghiệm. Tùy biến nằm ngoài skill gốc nên cập nhật không mất.
2. **Bổ sung kho cảnh theo ngành** của học viên thật (hỏi ngành lúc đăng ký), kèm gói bổ sung nhẹ (mục 5.3).
3. **Thêm mẫu cảnh mới theo nhu cầu thật:** skill ghi lại câu nói nào không tìm được cảnh hay kiểu hình hợp; mỗi tuần tổng hợp thành danh sách cần làm.
4. **Một đường "video tự do":** học viên mô tả video muốn làm, Claude lập bảng cảnh từ các loại có sẵn cho duyệt rồi dựng, không cần đúng skill nào.

## 7. Kết quả thử thật ngày 25/11/2026 và những gì đã sửa

**Cách thử:**
- Bộ não giả dựng từ đúng bộ quà "Bộ Não AI Khởi Động", tên thư mục có dấu và dấu cách.
- Dán đúng câu lệnh ở mục 2, tải từ GitHub.
- Mở Claude mới hoàn toàn trong bộ não đó và nói như học viên (`claude -p` với `--setting-sources project,local`).

| Tình huống | Kết quả |
|---|---|
| Cài mới tinh | Đạt, `XƯỞNG SẴN SÀNG` |
| Dán lại để cập nhật từ GitHub | Đạt, giữ nguyên đồ của học viên |
| Mở sai thư mục | Dừng ngay, báo rõ |
| Bộ não có hồ sơ → "muốn làm video giới thiệu bản thân" | Đọc bộ não, hỏi 5 câu còn thiếu, dựng video 26 giây, chấm 9/10, xin OK trước khi ghi bộ não |
| Bộ não trống | Hỏi đủ 6 câu kèm ví dụ, không bịa |
| Xin video KOL AI | Báo đúng thiếu gì, cách chuẩn bị, phí, việc làm được ngay |

**Lỗi tìm ra và đã sửa** (bộ cài 0.2.4–0.2.5, skill BNI 2.2):
- **Thư viện bị lệch phiên bản:** thư viện âm thanh `av` bản 19 không khớp `faster-whisper`, làm skill KOL và cắt livestream đổ khi nghe giọng. Đã ghim `av` 19.0.2 và vá. Không lùi về `av` 18 được vì Windows chặn bản đó.
- **Skill cũ cài chung máy đè bản mới:** bộ cài nay cảnh báo. Máy Founder có 9 skill và 23 agent cũ, cài tối 24/11 từ kho `an-binh-video-ai`; đã chuyển vào Thùng rác ngày 25/11.
- **Máy thiếu Visual C++:** học viên gặp với bộ cài cũ, bộ cài mới trước đó cũng sẽ dính. Nay bộ cài tự chép bộ Visual C++ chính hãng Microsoft vào thư mục của xưởng, không cần quyền quản trị.
- **Máy RAM thấp:** học viên máy 3,9 GB tải mô hình nghe giọng 3 GB rồi không mở được. Nay máy dưới 8 GB luôn dùng mô hình nhỏ, có cảnh báo; máy dưới 6 GB dựng nhẹ hơn.
- **Lỗi video BNI** (4 vai người dùng × 2 vòng, khoảng 57 lỗi): ghi ở `goi/video-nguoi-noi/skills/video-ngan-nguoi-noi/references/loi-da-gap.md`.

**Chưa thử được:**
- Máy Mac thật.
- Máy thật chỉ 4 GB RAM.
- Máy Windows thật chưa từng cài Visual C++. Nhánh này đã ép chạy để kiểm, nhưng chưa thử trên máy như vậy.

## 8. Lưu ý khi dạy và hỗ trợ học viên

- **Hạn mức Claude:** một video BNI trọn vẹn (hỏi, viết, dựng, chấm) dùng lượng tương đương khoảng 3 USD giá API của bản Opus. Gói Pro có thể chạm giới hạn sau 1–2 video mỗi 5 giờ. Nói trước với học viên; người làm nhiều nên dùng gói Max.
- **Không để bộ não trong OneDrive, Google Drive:** kho cảnh khoảng 0,9 GB và video thành phẩm nằm trong bộ não sẽ bị đồng bộ lên mạng. *(Đề xuất sau: chuyển kho tài nguyên ra thư mục phần mềm, ngoài bộ não.)*
- **Ổ trống:** mỗi bộ não cần thêm khoảng 1 GB; phần mềm chung khoảng 2–5 GB tùy máy. Bộ cài dừng khi ổ còn dưới 2 GB.
- **Giọng máy miễn phí** chỉ có 1 giọng nam, 1 giọng nữ, đều giọng Bắc. Học viên miền Trung, miền Nam nên tự thu giọng (skill đã có luồng tự thu).
- **Đăng video có giọng máy:** nhắc học viên bật nhãn "Nội dung do AI tạo" trên Facebook.
- **Lỗi hay gặp khi cài:** mỗi lỗi ghi một mục trong sổ hỗ trợ (`docs/04_CURRICULUM_AND_DELIVERY/HO_TRO_HOC_VIEN/` ở kho học viện), kèm cách tự sửa.

## 9. Thế nào là "đạt" (thước đo)

1. Chỉ một câu lệnh. Không cần Git, winget, Homebrew, quyền quản trị, không gõ mật khẩu máy. **Đạt trên Windows (25/11).**
2. Máy 8 GB RAM dựng được video BNI và Edit video. **Đạt trên máy giả lập 8 GB.**
3. Dán lại câu lệnh là cập nhật; dữ liệu bộ não, video, mẫu và cảnh riêng của học viên còn nguyên. **Đạt (25/11).**
4. Học viên tự thêm kiểu video, cảnh, nhạc của mình bằng một câu nói. *Chưa: chờ `xuong-mo-rong`.*
5. Nội dung lời trong video lấy từ bộ não, không bịa. **Đạt trong các lần thử.**
6. *(Đề xuất)* Cài xong trong **≤ 20 phút** với mạng 20 Mbps, gói nhẹ.
7. *(Đề xuất)* Video đầu tiên (BNI khoảng 30 giây) ra trong **≤ 15 phút** kể từ khi cài xong. *Lần thử 25/11: khoảng 10 phút.*
8. *(Đề xuất)* **≥ 9/10 cảnh** AI chọn hợp với câu nói đi kèm.
9. *(Đề xuất)* Học viên lần đầu tự làm đúng hết các bước, không phải hỏi nhóm hỗ trợ, ở **≥ 8/10 lần thử**.
10. *(Đề xuất)* Mọi tài nguyên phát cho học viên đều rõ nguồn và quyền dùng.
11. *(Đề xuất)* Cập nhật khi chỉ thêm vài cảnh tốn **dưới 100 MB** tải về. **Đạt trên bộ thử (25/11, mục 5.3); chờ lần bổ sung kho thật v2 để đo trên R2.**
12. *(Đề xuất)* Không có gì mới thì `/cap-nhat-xuong` trả lời trong **dưới 1 phút** và không đụng tệp nào.

## 10. Nguyên tắc thiết kế (không đánh đổi)

1. **Bộ não là trung tâm.** Xưởng nằm trong bộ não, đọc nội dung từ bộ não; không bắt học viên tìm hay chọn thư mục.
2. **Hỏi đúng cái thiếu, một lượt.** Có trong bộ não thì không hỏi lại; thiếu thì hỏi kèm gợi ý; học viên bận thì cho "làm luôn". Không bịa.
3. **Khung giữ mạch, không ép lời.** Công thức (như BNI 5 nhịp) chỉ là đường đi; lời viết riêng cho từng người.
4. **Chọn bằng chỉ mục, không bằng tên tệp.** AI đọc `CHI_MUC.md`, cần thì xem ảnh xem trước. Nhãn đúng với hình là sống còn.
5. **Nhẹ mà vẫn nét.** Video dọc 720×1280, CRF 22, SSIM ≥ 0,97. Gói nhẹ cho máy yếu; Whisper chọn theo RAM.
6. **Cài đủ một lần, thiếu gì nhắc nấy.** Mọi skill cài sẵn. Việc cần tài khoản, khóa, máy mạnh thì kiểm đúng lúc làm và hướng dẫn chuẩn bị.
7. **Không cần quyền quản trị, không bảng hỏi khó hiểu.** Phần mềm đặt trong thư mục của xưởng, ngoài bộ não.
8. **Của học viên là bất khả xâm phạm.** `cua-toi`, `chu=hoc-vien`, `mau-cua-toi` không bao giờ bị ghi đè. Tùy biến nằm ngoài skill gốc. Ghi vào ngăn 00–07 phải xin OK.
9. **Cải tiến liên tục theo phiên bản.** Mã ở GitHub, tài nguyên ở R2, gói đã phát hành thì khóa, mỗi lần bổ sung là bản mới. Học viên nhận bằng `/cap-nhat-xuong`, chỉ tải phần mới.
10. **Sạch tên và sạch quyền.** Không mang tên đơn vị cũ của mã kế thừa, không phát lại nguyên tệp nhạc; tài nguyên chưa rõ quyền phải ghi rõ và có kế hoạch thay.
11. **Tự kiểm trước khi giao.** Skill tự soát và có người chấm độc lập; bộ cài kiểm thư viện và dựng thử trước khi báo sẵn sàng; kho chạy `kiem_kho.py` trước mỗi lần phát hành; mỗi bản bộ cài thử trên bộ não giả trong `%TEMP%`.

## 11. Thứ tự việc tiếp theo (em khuyên, chờ Founder chốt)

1. ~~Gói bổ sung cho tài nguyên~~: **xong 0.2.6** (mục 5.3).
2. **Thử trên máy thật của học viên:** một máy 4–8 GB, một máy chưa từng cài Visual C++, một máy Mac. Đo thời gian theo thước đo 6–7.
3. **Skill `xuong-mo-rong`** (mục 6.3 việc 1).
4. **Bổ sung cảnh theo ngành** của học viên thật (spa, ăn uống, bất động sản, giáo dục, bảo hiểm…).
5. **Nhắc có bản mới** (mục 5.5) và chuyển kho tài nguyên ra ngoài bộ não (mục 8).
6. Sửa dần các skill còn lại (cắt ghép, ảnh bìa, KOL AI) theo kho mới, ưu tiên skill học viên dùng nhiều.

## 12. Lộ trình nâng kho tài nguyên cho mọi ngành (Founder duyệt 25/11/2026)

Ký hiệu: ✅ xong · 🔄 đang làm · 📝 chờ làm · ⏸️ để sau. Làm việc nhanh trước (nhạc, tiếng, ảnh), quay video sau. Xong mục nào thì đánh dấu và ghi ngày.

### 12.1 Hiện trạng (đếm chỉ mục ngày 25/11)

| Loại | Có | Vấn đề |
|---|---|---|
| Cảnh video | 226 | 163 cảnh (72%) là công nghệ: màn hình ảo, biểu đồ, robot, máy chủ, lập trình |
| Cảnh ngành nghề | 12 | Mỗi ngành 1 cảnh; 9/12 chỉ có ở gói đủ |
| Cảnh có người | khoảng 15 | Thiếu khách hàng, chủ shop, tư vấn, đội nhóm |
| Nhạc nền | 3 | Quá ít, dễ trùng; nguồn Pixabay không cho phát lại nguyên tệp |
| Tiếng hiệu ứng | 7 | Cả 7 chưa rõ nguồn và quyền dùng |

Hệ quả: máy 8 GB (đa số học viên) chỉ nhận gói nhẹ 64 cảnh, 43 cảnh công nghệ. Chủ spa làm video thì máy không có cảnh ngành mình, rơi về 4 cảnh nền dịu dùng chung, làm vài video là lặp.

### 12.2 Các việc

| # | Việc | Vì sao | Trạng thái |
|---|---|---|---|
| 1 | **Máy 8 GB nhận đủ kho cảnh:** chọn gói đủ theo ổ trống (≥ 6 GB), không theo RAM | Cảnh chiếm ổ, không ăn RAM; đa số học viên có gấp 3,5 lần cảnh | 🔄 25/11: đã sửa bộ cài, phát hành cùng đợt nhạc + tiếng (máy đang gói nhẹ tự lên gói đủ một lần, tải khoảng 880 MB) |
| 2 | **Nhạc nền sạch quyền:** 20–30 bài chia theo tâm trạng (ấm áp, tin cậy, sang trọng, vui, cảm xúc, dồn dập) và nhịp; chỉ nhận CC0/miền công cộng (được phát lại trong gói) | Ít nhạc thì video trùng nhau; nhạc Pixabay không được đóng gói phát lại | 🔄 25/11: đã tải 30 bài CC0 từ Free Music Archive (trang từng bài ghi CC0, không phải nhạc AI) vào `_kho-nang\nguon-moi\nhac\`. Đã đo, gắn nhãn theo từ điển tâm trạng (`tu-dien-am.json`), nhập thử qua luật ĐẠT 30/30. Mã 0.2.8 (25/11) cho máy dùng được: kiểm quyền theo chỉ mục, tự bắt đầu ở giây gợi ý, nối vòng bài ngắn, chọn bài đủ dài. Còn: Founder nghe xong (2 bài méo `lofi_03`, `edm_04` đề xuất bỏ) → nhập kho, đóng gói v2, Founder tải lên R2 |
| 3 | **Tiếng hiệu ứng sạch quyền:** khoảng 30–40 tiếng CC0 (tiền về "ting ting", vỗ tay, tiếng cười, thông báo, vút, bụp, mở cửa hàng…); thay 7 tiếng chưa rõ nguồn | Tiếng chưa rõ quyền không được dùng trong video đăng công khai | 🔄 25/11: đã tải 40 tiếng CC0 (BigSoundBank 26, Kenney 8, OpenGameArt 4…) vào `_kho-nang\nguon-moi\am\`; còn thiếu tiếng cười, "wow" đám đông, glitch, ka-ching. Đã đo, gắn nhãn 6 nhóm, nhập thử qua luật ĐẠT 40/40. Mã 0.2.8: gọi tiếng bằng mã hoặc mô tả, giây mạnh nhất trùng lúc hình đổi. Còn: nhập kho, gói v2 cùng nhạc |
| 4 | **Ảnh minh họa + biểu tượng:** ảnh AI theo nhịp bài bán hàng và theo ngành (nhẹ, rẻ, nhanh hơn video); bộ biểu tượng nền trong (tích, mũi tên, khung giá, sao, quà); bộ dựng cho ảnh phóng to/lia nhẹ | Lấp nhanh chỗ thiếu ngành và thiếu người trong khi chờ quay video | 📝 |
| 5 | **Lớp cảnh "kinh doanh chung"** 100–150 cảnh theo nhịp bài bán hàng: nỗi đau, giải pháp/dịch vụ, bằng chứng, đời sống Việt, cảm xúc; người Việt do AI tạo, không chữ, không logo | Dùng được cho mọi ngành; đây là chỗ thiếu nhất | ⏸️ sau việc 4 (Claude soạn sẵn bộ câu lệnh tạo cảnh) |
| 6 | **Lớp cảnh theo ngành** 20–30 cảnh/ngành. Ưu tiên: spa-làm đẹp, ăn uống-cà phê, giáo dục-coaching, bất động sản, bảo hiểm-tài chính, bán online-thời trang; sau: nha khoa-phòng khám, nội thất-xây dựng, du lịch-khách sạn, thực phẩm sạch, dịch vụ gia đình | Chọn theo danh sách ngành học viên thật, không đoán | ⏸️ chờ Founder gửi danh sách ngành |
| 7 | **Skill `xuong-mo-rong`:** học viên nói "thêm 10 ảnh cửa hàng của tôi vào kho", máy tự gắn nhãn, dùng về sau | Không kho nào phủ hết ngành ngách; đồ thật của học viên hợp nhất | 📝 |
| 8 | **Phát hành thử v2** (lớp chung khoảng 60 cảnh + 3 ngành đông nhất + nhạc + tiếng), cho 3 học viên giả 3 ngành làm video, chấm | Thước đo 8: ≥ 9/10 cảnh hợp lời | ⏸️ |
| 9 | **Cài, cập nhật, dọn bản cũ an toàn tuyệt đối:** xem `KE_HOACH_CAI_CAP_NHAT_AN_TOAN.md` (19 tình huống, dọn bộ cài cũ 24/11, luôn hỏi học viên trước) | Không bao giờ mất dữ liệu học viên; không để rác 3 GB của bản cũ | ✅ mã 25/11 (Founder duyệt kế hoạch 25/11 tối), bộ thử 38/38 ĐẠT; phát hành bản 0.2.7 |
| ✅ | Cập nhật chỉ tải phần bổ sung (bản 0.2.6) | Thêm tài nguyên không bắt cả lớp tải lại 900 MB | ✅ 25/11 |

## 13. Cách dùng tệp này

- Đọc ở đầu mỗi đợt làm xưởng video, và mỗi khi Founder hỏi về cài đặt, cập nhật, tùy biến.
- Đề xuất nào không phục vụ mục 1 thì để sau.
- Founder chốt điều gì (thước đo, thứ tự, ngành cần thêm cảnh) thì sửa ngay tại đây, ghi ngày. Tiến độ việc ghi ở ZAIOS Core, không ghi checklist ở đây.
- Câu lệnh ở mục 2 phải luôn khớp `cai/README.md`.
