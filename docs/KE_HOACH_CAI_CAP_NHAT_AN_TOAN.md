---
status: draft
version: 0.1.0
updated: 2026-11-25
owner: Founder Đức Tuệ Nam
---

# KẾ HOẠCH: CÀI, CẬP NHẬT, DỌN BẢN CŨ — KHÔNG BAO GIỜ MẤT DỮ LIỆU HỌC VIÊN

> Bản Claude soạn 25/11/2026 tối theo yêu cầu Founder: lường trước mọi tình huống, học viên luôn được hỏi trước, bộ cài mới dọn sạch bộ cài cũ ngày 24/11. **Chờ Founder duyệt.** Ký hiệu: ✅ xong · 🔄 đang làm · 📝 chờ làm · ⏸️ để sau. Mục tiêu chung ở `MUC_TIEU.md`, lộ trình tài nguyên ở `MUC_TIEU.md` mục 12.

## 1. Năm luật không đổi

1. **Đồ của học viên không bao giờ bị xóa hay ghi đè.** Mọi thứ không phải của kho đều là của học viên, kể cả khi không ghi nhãn.
2. **Trước khi thay một tệp của kho mà học viên đã sửa: cất bản cũ** vào `<Xưởng>/.sao-luu/<ngày giờ>/`, rồi báo ⚠.
3. **Hỏi trước khi làm.** Cập nhật: Claude cho xem trước "sẽ thay gì, tải bao nhiêu, giữ gì" rồi mới chạy. Dọn bản cũ: liệt kê từng thứ, học viên OK mới làm.
4. **Không xóa hẳn.** Dọn = chuyển vào Thùng rác (Windows Recycle Bin, Mac Trash), có nhật ký để khôi phục.
5. **Chạy lại bao nhiêu lần cũng an toàn.** Đứt mạng, tắt máy giữa chừng: chạy lại là đi tiếp, không hỏng, không nhân đôi.

## 2. Bộ cài cũ (24/11) để lại gì trên máy học viên

Đối chiếu mã bộ cài cũ (commit `a9e972c`, xem `third_party/NGUON_GOC.md`):

| # | Thứ | Ở đâu | Nặng | Nguy cơ nếu để nguyên |
|---|---|---|---|---|
| C1 | 9 skill cũ | `~/.claude/skills/` (chung cả máy) | nhỏ, riêng thư mục `engine/node_modules` của skill người nói vài trăm MB | **Claude dùng bản cũ thay bản mới** trong bộ não (đã thấy khi thử 25/11) |
| C2 | 23 agent cũ, trùng tên đủ 23 agent mới | `~/.claude/agents/` | nhỏ | Trong bộ não, agent của bộ não được ưu tiên; ở thư mục khác vẫn chạy bản cũ, gây nhầm |
| C3 | Thư mục `Video-AI` cạnh bộ não | `<thư mục cha của bộ não>/Video-AI/` | khoảng 1,5 GB | Chứa **cả đồ của học viên** (`du-an/`, video đã làm, `anh-video-cua-toi/`, `ho-so-kenh.json`) **lẫn bản chép kho cũ** (`kho-canh/`, `tai-nguyen/`) trùng với kho mới |
| C4 | Gói `KHO-HOC-VIEN.zip` (và có thể bản đã giải nén) | Downloads, Desktop, Documents | khoảng 1,5 GB | Rác, chiếm ổ |
| C5 | Cấu hình học viên tự điền trong skill cũ | `~/.claude/skills/<skill>/` (ví dụ `kol.json`, `cau-hinh.json`, `video.json`, `brands/*.json`, video mẫu tự đặt) | nhỏ | **Là đồ của học viên**: chuyển skill cũ vào Thùng rác mà không cứu ra thì học viên mất KOL và cấu hình |
| C6 | Phần mềm cài bằng winget/pip (FFmpeg, Node, Git, Python, thư viện) | hệ thống | lớn | Vô hại, có thể đang dùng cho việc khác: **không gỡ** |
| C7 | Mô hình Whisper tải theo skill cũ | thư mục đệm `~/.cache/huggingface/` | đến 3 GB | **Giữ và dùng lại**: bộ cài mới tải Whisper vào đúng chỗ đệm này, đã có thì không tải lại |
| C8 | Thư mục sao lưu của bộ cài cũ | `~/.claude/sao-luu-<tên>/<giờ>/skill|agent/` | nhỏ | Có thể chứa bản học viên từng sửa: chép giữ vào xưởng rồi mới dọn |

**Tận dụng đồ đã cài (Founder dặn 25/11: có rồi thì dùng, thiếu mới cài, không xóa đi cài lại):**

| Thứ | Bộ cài mới làm gì |
|---|---|
| FFmpeg | Máy có sẵn và chạy được (`ffmpeg`, `ffprobe` trong PATH, kể cả bản winget của bộ cài cũ) thì dùng luôn; không có mới tải bản chạy ngay |
| Node | Có sẵn bản ≥ 18 thì dùng luôn; không thì tải |
| Visual C++ | Máy đã có thì không đụng; thiếu mới chép bản đi kèm (không cần quyền quản trị) |
| Mô hình Whisper, trình duyệt dựng hình (Remotion, Playwright) | Dùng chung chỗ đệm của máy: đã tải rồi thì không tải lại |
| Tài nguyên đã giải nén | Tệp đã có đúng cỡ thì bỏ qua; bản mới chỉ tải gói bổ sung |
| Python | **Riêng một bản cho xưởng** (cố ý): Python máy học viên mỗi người một phiên bản, cài thư viện vào đó dễ đụng phần mềm khác và từng bị Smart App Control chặn (25/11). Bản riêng không ảnh hưởng gì Python sẵn có |

## 3. Ma trận tình huống

| # | Tình huống | Hôm nay bộ cài làm gì | Rủi ro | Cách xử lý | Trạng thái |
|---|---|---|---|---|---|
| T1 | Cài mới trên bộ não mới | Đủ 7 bước, báo XƯỞNG SẴN SÀNG | — | — | ✅ thử thật 25/11 |
| T2 | Chạy lại khi không có gì mới | Báo `ĐÃ LÀ BẢN MỚI NHẤT`, không đụng gì | — | — | ✅ 0.2.6 |
| T3 | Có mã mới | Thay skill, agent, tệp hướng dẫn của kho | Học viên đã sửa skill gốc thì **mất bản sửa** | Luật 2: nhớ dấu vân tay tệp đã cài; khác thì cất `.sao-luu/` + ⚠ | ✅ 25/11 thử |
| T4 | Có tài nguyên mới, học viên ở bản liền trước hoặc bỏ lỡ nhiều bản | Tải chuỗi gói bổ sung; thiếu mắt xích thì tải gói đủ | — | — | ✅ 0.2.6 thử trên bộ thử |
| T5 | Máy chuyển gói nhẹ → gói đủ | Tải gói đủ một lần, tệp đã có bỏ qua | Tốn 880 MB một lần | Báo trước dung lượng trong bước xem trước (T8) | ✅ mã 25/11, phát hành 0.2.7 |
| T6 | Học viên tự thêm cảnh, nhạc, tiếng | Giữ tệp trong `cua-toi/` và dòng `chu=hoc-vien` | Dòng thiếu nhãn bị xóa; tệp đặt sai chỗ thì máy không dùng | Giữ **mọi dòng không phải `chu=kho`**; cất chỉ mục cũ trước khi ghi; skill `xuong-mo-rong` để thêm đúng khuôn | ✅ 25/11 thử (skill `xuong-mo-rong` còn 📝) |
| T7 | Học viên tự viết skill riêng, agent riêng | Không đụng (khác tên) | Trùng tên skill của kho thì bị thay | Luật 2 (T3) che luôn trường hợp này | ✅ 25/11 thử |
| T8 | Học viên muốn biết trước cập nhật làm gì | Không có, chạy luôn | Trái luật 3 | Chế độ **xem trước** `XUONG_XEM=1`: in bản đang có → bản mới, có gì mới, tải bao nhiêu MB, tệp nào sẽ cất sao lưu; `/cap-nhat-xuong` chạy xem trước, hỏi OK rồi mới chạy thật | ✅ 25/11 thử |
| T9 | Máy có bộ cài cũ 24/11 (bảng mục 2) | Chỉ báo ⚠ skill chung máy trùng tên | Rác 3 GB; Claude dùng nhầm skill cũ; đồ học viên nằm rải ở `Video-AI` | Bước **dọn bản cũ** (mục 4) | ✅ 25/11 thử trên máy giả có bản cũ thật (mã 24/11) |
| T10 | Đứt mạng, tắt máy giữa chừng | Gói tải dở được tải tiếp; `xuong.json` ghi sau cùng nên lần sau làm lại phần dở | — | Thêm vào bộ thử để giữ mãi | ✅ 25/11 thử |
| T11 | Ổ đầy khi đang giải nén | Chỉ dừng khi ổ còn dưới 2 GB | Giải nén dở | Kiểm trước: ổ trống ≥ 2 lần dung lượng sẽ tải, không đủ thì DỪNG kèm hướng dẫn | ✅ 25/11 thử |
| T12 | Bộ não nằm trong OneDrive/Google Drive | Không kiểm | Tệp "chỉ trên mây", đồng bộ 1–3 GB, chậm | Phát hiện đường dẫn OneDrive/Drive → ⚠ khuyên chuyển bộ não ra ngoài (không tự chuyển) | ✅ 25/11 (chỉ báo) |
| T13 | Học viên đổi tên ngăn `08_XUONG_VIDEO` | Tìm `*_XUONG_VIDEO` có `xuong.json` | Đổi thành tên khác thì tạo ngăn mới → hai xưởng | Tìm theo `xuong.json` ở mọi ngăn cấp 1, không theo tên | ✅ 25/11 thử |
| T14 | Hai bộ não trên một máy | Mỗi bộ não một xưởng, dùng chung phần mềm | — | — | ✅ theo thiết kế |
| T15 | Mở Claude sai thư mục | `cai.ps1`/`cai.sh` DỪNG, chỉ cách mở đúng | — | — | ✅ thử 25/11 |
| T16 | Claude đang mở khi cập nhật | Skill mới chỉ có hiệu lực sau khi mở lại | Dùng nhầm bản cũ trong phiên đó | Đã nhắc "đóng hẳn Claude rồi mở lại" | ✅ |
| T17 | Founder phát hành nhầm bản lỗi | Học viên cập nhật là nhận lỗi | Cả lớp hỏng | (a) cổng thử trước phát hành: bộ thử cập nhật thành công cụ cố định `cong-cu/thu_cap_nhat.py` + `hoi_quy.py`; (b) sửa = đẩy bản mới số cao hơn, học viên cập nhật lại | ✅ (a) có cổng thử; (b) theo quy trình |
| T18 | Máy Mac | Mã có, chưa thử máy thật | Lỗi chưa biết | Thử một máy Mac thật trước khi giao lớp | ⏸️ cần máy |
| T19 | Diệt virus / Smart App Control chặn | Đã xử lý Python, av, VC++ | Chặn kiểu mới | Dòng DỪNG chỉ cách, gom lỗi gặp thật vào bộ cài | ✅ phần đã gặp |

## 4. Thiết kế bước "dọn bản cũ" (T9)

**Bộ cài tự dò, không tự dọn.** Mỗi lần cài hoặc cập nhật, bộ cài dò các thứ ở mục 2 (chỉ đọc). Thấy dấu vết bản cũ thì in khối `⚠ PHÁT HIỆN BẢN CŨ` liệt kê từng thứ, dung lượng, sẽ làm gì. Skill `/cap-nhat-xuong` đọc khối này, giải thích cho học viên, **hỏi OK**, rồi chạy `XUONG_DON_BAN_CU=1`.

Khi được OK, theo thứ tự:

1. **Cứu đồ học viên trước** (chép, chưa xóa gì):
   - Trong skill cũ (C5): mọi tệp **không có trong danh sách tệp của bộ cài cũ** (biết chính xác từ commit `a9e972c`) là của học viên → chép sang `<Xưởng>/chuyen-tu-ban-cu/skills/<skill>/`. Tệp gốc học viên đã sửa (khác mã kiểm bản gốc) cũng chép theo.
   - Trong `Video-AI` (C3): `du-an/`, video thành phẩm, `anh-video-cua-toi/`, `ho-so-kenh.json` → chuyển vào đúng chỗ trong `<Xưởng>` (trùng tên thì thêm hậu tố, không đè). Cảnh, nhạc học viên tự thêm (không có trong kho v1) → `tai-nguyen/<loai>/cua-toi/` + dòng `chu=hoc-vien`.
   - Kiểm số tệp và dung lượng sau khi chép khớp với trước. Không khớp thì DỪNG, không bước tiếp.
2. **Chuyển vào Thùng rác** (chỉ thứ đã xác định chắc là của bộ cài cũ):
   - Skill cũ (C1): chỉ thư mục đúng tên 9 skill **và** có `SKILL.md` khớp dấu vết bộ cài cũ. Skill trùng tên mà nội dung lạ thì không đụng, chỉ báo.
   - Agent cũ (C2): chỉ 23 tệp đúng tên và khớp nội dung gốc; tệp đã bị sửa thì cứu như bước 1 rồi mới dọn.
   - Bản chép kho cũ trong `Video-AI` (`kho-canh/`, `tai-nguyen/` của kho), rồi thư mục `Video-AI` nếu đã trống.
   - Gói `KHO-HOC-VIEN*.zip` và thư mục giải nén của nó (C4).
3. **Không gỡ** phần mềm hệ thống (C6). Thư mục Whisper (C7): chỉ báo dung lượng, học viên muốn thì nói riêng.
4. Ghi `<Xưởng>/NHAT_KY_DON_BAN_CU.md`: đã cứu gì đi đâu, đã chuyển gì vào Thùng rác, cách lấy lại.
5. Báo học viên bằng lời dễ hiểu: giải phóng bao nhiêu GB, đồ của anh/chị đã chuyển tới đâu, nhắc đóng và mở lại Claude.

Học viên từ chối dọn: xưởng mới vẫn chạy, nhưng ⚠ về skill chung máy trùng tên vẫn hiện mỗi lần cập nhật, vì nó làm Claude dùng nhầm bản cũ.

## 5. Luồng `/cap-nhat-xuong` sau khi làm xong kế hoạch

1. Học viên gõ `/cap-nhat-xuong`.
2. Claude chạy chế độ xem trước. Không có gì mới (và không có bản cũ cần dọn) → báo một dòng, xong.
3. Có mới → Claude nói: "Bản mới 0.2.7: thêm 30 bài nhạc… Sẽ tải 45 MB. Video, ảnh, mẫu của anh/chị giữ nguyên. Anh/chị đã sửa skill X, bản sửa sẽ được cất ở .sao-luu. Cập nhật nhé?" → học viên OK → chạy thật → báo "có gì mới".
4. Có dấu vết bản cũ → hỏi riêng một câu về dọn, OK mới dọn (mục 4).

## 6. Kiểm trước khi phát hành (cổng bắt buộc)

- `python -X utf8 cong-cu/thu_cap_nhat.py` (chạy trong `%TEMP%\zaios_thu_cap_nhat`, thư mục nhà và Thùng rác đều giả; phải in `ĐẠT HẾT`): T2, T3 (sửa skill gốc → có sao lưu), T4, T5, T6 (dòng thiếu nhãn còn), T8, T10 (ngắt giữa chừng rồi chạy lại), T11, T13, và T9 trên **một bộ não giả có dựng sẵn dấu vết bộ cài cũ** (skill, agent, `Video-AI` có đồ học viên, gói zip): đồ học viên phải còn đủ, rác vào Thùng rác.
- `hoi_quy.py` của skill người nói khi skill đổi.
- Thử một lần trên máy thật của học viên trước khi báo cả lớp.

## 7. Thứ tự làm (Claude khuyên)

| Bước | Việc | Phủ tình huống | Trạng thái |
|---|---|---|---|
| 1 | Sao lưu trước khi thay (dấu vân tay `.dau-van-tay.json`) + giữ mọi dòng không phải của kho | T3, T6, T7 | ✅ 25/11 (`cai/an_toan.py`) |
| 2 | Chế độ xem trước `XUONG_XEM=1` + `/cap-nhat-xuong` hỏi OK | T5, T8 | ✅ 25/11 |
| 3 | Dò + dọn bản cũ có cứu đồ học viên `XUONG_DON_BAN_CU=1` (dấu vết chính xác 11 commit + kho cũ: `cai/ban-cu-24-11.json`) | T9 | ✅ 25/11 |
| 4 | Kiểm ổ trước khi tải, phát hiện OneDrive/Drive/iCloud/Dropbox, tìm xưởng theo `xuong.json` | T11, T12, T13 | ✅ 25/11 |
| 5 | Bộ thử cố định `cong-cu/thu_cap_nhat.py`: **38/38 ĐẠT** 25/11 (T1–T4, T6–T11, T13, cài lại) | T10, T17 | ✅ 25/11 |
| 6a | Phát hành mã 0.2.7 (các bước trên + máy 8 GB nhận gói đủ) sau một lần cài thật đầy đủ trên bộ não giả | toàn bộ | 🔄 |
| 6b | Phát hành tài nguyên v2 (nhạc, tiếng mới) sau khi Founder nghe thử, gắn nhãn, tải lên R2; thử một máy học viên thật | toàn bộ | 📝 |
| 7 | Skill `xuong-mo-rong` | T6 | 📝 (MUC_TIEU 12, việc 7) |
