---
status: draft
version: 0.1.0
updated: 2026-11-24
owner: Founder Đức Tuệ Nam
---

# KIẾN TRÚC XƯỞNG VIDEO AI (cài vào Bộ Não AI của học viên)

## 1. Mục tiêu đo được

1. Học viên mở Claude (thẻ Code, **This computer**) đúng thư mục Bộ Não AI đã cài ở buổi 1, dán **một câu lệnh**, không phải tải hay chọn thư mục gì thêm.
2. Không cần Git, winget, Homebrew, quyền quản trị, không gõ mật khẩu máy.
3. Máy RAM 8 GB dựng được video BNI và Edit video.
4. Chạy lại cùng câu lệnh = cập nhật bản mới, **không đụng** dữ liệu bộ não, video, mẫu và cảnh riêng của học viên.
5. Học viên tự thêm "kiểu video của tôi", cảnh của tôi, nhạc của tôi bằng một câu nói với AI; hệ thống tự lưu đúng chỗ và tự ghi chỉ mục.

## 2. Ba lớp, ba nơi lưu

| Lớp | Nội dung | Nơi lưu gốc | Dung lượng |
|---|---|---|---|
| **Mã** | Bộ cài, skill, agent, chỉ mục, tài liệu | GitHub công khai `ductuenam/xuong-video-ai` (thư mục này) | khoảng 15 MB |
| **Tài nguyên** | Kho cảnh đã nén, ảnh xem trước, nhạc, tiếng hiệu ứng | Cloudflare R2 (xem `LUU_TRU_VA_PHAT_HANH.md`); bản chuẩn ở `E:\xuong-video-ai-kho\` (xem `BAN_DO_KHO.md`) | v1: 882 MB đủ, 217 MB nhẹ, 18 MB nhạc + tiếng |
| **Máy** | Python, FFmpeg, Node, mô hình Whisper | Tải từ nguồn chính hãng lúc cài | 0,5–3 GB tùy gói |

Tệp `PHIEN_BAN.json` nối ba lớp: ghi phiên bản, đường tải, mã kiểm (sha256) và dung lượng từng gói. Bộ cài chỉ đọc tệp này, không đoán.

## 3. Bộ skill: cài đủ một lần, kiểm điều kiện lúc làm

**Quyết định của Founder ngày 25/11/2026: không chia cấp.** Một câu lệnh cài **mọi skill, mọi agent, kho tài nguyên và phần mềm**; skill rất nhẹ, chỉ kho tài nguyên nặng. Các gói dưới đây chỉ là cách xếp thư mục cho dễ quản lý, người dùng không phải "mở" gì.

| Gói (`goi/`) | Skill | Agent | Người dùng cần chuẩn bị thêm |
|---|---|---|---|
| `video-nguoi-noi` | `video-ngan-nguoi-noi` (Edit video, BNI, video người nói, video không quay) | `video-dung`, `video-cham-diem` | Không. Giọng AI miễn phí |
| `cat-ghep-quang-cao` | `ab-edit` (cắt livestream, biến thể quảng cáo, quảng cáo duyệt từng bước), `anh-bia-video`, `video-ngan-hyperframes` | `kiem-duyet-doc-lap` | Ảnh bìa vẽ AI: khóa Google Vertex. Cắt livestream dài: nên có máy 16 GB |
| `kol-ai` | `kol-ban-quan-ao`, `kol-lookbook`, `kol-mac-thu-mot-khung`, `kol-review-nghi-duong`, `video-cay-canh` | 20 agent soi, chấm | Tài khoản Muse + Claude in Chrome |

**Cổng sẵn sàng (thay cho "lên cấp"):** mỗi `goi.json` ghi `dieu_kien_theo_skill`. Danh mục điều kiện, cách kiểm, cách chuẩn bị và cách làm tạm nằm ở `xuong-mau/08_XUONG_VIDEO/CHUAN_BI_THEM.md` (chép vào bộ não học viên). Khi người dùng yêu cầu một việc:
- Đủ điều kiện → Claude làm luôn theo ý người dùng.
- Thiếu → Claude báo thiếu gì, để làm phần nào, cách chuẩn bị, có tốn phí không, và đề xuất cách làm được ngay với thứ đang có.
- Nội dung chưa rõ → tìm trong bộ não trước, không có thì hỏi hoặc đề xuất. Không bịa.

Lộ trình học (dễ trước, khó sau) là việc của giáo trình, không phải việc của bộ cài.

## 4. Sau khi cài, bộ não của học viên trông thế này

```
<Bộ Não AI của học viên>/
├─ 00 … 07                      giữ nguyên, bộ cài không đụng
├─ 08_XUONG_VIDEO/              ngăn mới, học viên nhìn thấy
│   ├─ HUONG_DAN.md             các câu lệnh làm video
│   ├─ CHI_MUC_XUONG.md         chỉ mục L1 của xưởng (AI đọc đầu tiên)
│   ├─ CHUAN_BI_THEM.md         việc nào cần tài khoản/khóa gì, cách kiểm, cách chuẩn bị
│   ├─ ho-so-kenh.json          tự điền từ ngăn 01–04 (tên, giọng văn, liên hệ)
│   ├─ xuong.json               sổ đăng ký xưởng (máy đọc)
│   ├─ BAN_DO_BO_NAO.md         vai trò → ngăn thật của bộ não (tự dò)
│   ├─ tai-nguyen/
│   │   ├─ canh/                CHI_MUC.md, chi-muc.csv, xem-truoc/, <nhom>/<ma>.mp4, cua-toi/
│   │   ├─ nhac/                cùng khuôn
│   │   └─ am/                  cùng khuôn (thêm loại mới = thêm thư mục cùng khuôn)
│   ├─ mau-cua-toi/             kiểu video riêng của học viên, _chung/RUT_KINH_NGHIEM.md
│   ├─ du-an/                   mỗi video một thư mục làm việc
│   └─ thanh-pham/              video xong, đặt tên ngày_ten.mp4
├─ .claude/skills, .claude/agents   đủ mọi skill, agent của xưởng
└─ .may-video/                  ẩn: Python, FFmpeg, Node, mô hình Whisper
```

- Ảnh, video thật của học viên: **dùng thẳng từ ngăn 06**, không chép bản thứ hai.
- `.may-video/` được đặt trên ổ còn trống nhiều nhất. Nếu không cùng ổ với bộ não, bộ cài ghi đường dẫn thật vào `08_XUONG_VIDEO/.may-video.json`.
- Bộ cài thêm **một mục** vào `CLAUDE.md` và một dòng vào `INDEX.md` của bộ não (giữa hai dấu `<!-- XUONG-VIDEO:BEGIN/END -->` để lần cập nhật sau thay đúng chỗ):
  - Việc làm video: đọc `08_XUONG_VIDEO/CHI_MUC_XUONG.md` trước.
  - Không đọc lướt `.may-video/`, không mở lần lượt video trong `tai-nguyen/`: chọn qua `tai-nguyen/<loai>/CHI_MUC.md`, xem ảnh xem trước khi cần.
  - Nội dung lời video lấy từ ngăn 01–05, không bịa.
  - Trước mỗi việc, kiểm điều kiện theo `08_XUONG_VIDEO/CHUAN_BI_THEM.md`: đủ thì làm luôn theo ý người dùng; thiếu thì báo cần chuẩn bị gì và đề xuất cách làm được ngay.

> Tên `08_XUONG_VIDEO` là mặc định; nếu bộ não đã có ngăn 08, bộ cài lấy số trống kế tiếp. Chi tiết sổ đăng ký, bản đồ bộ não, khuôn tài nguyên, gói năng lực: [QUY_CHUAN_MO_RONG.md](QUY_CHUAN_MO_RONG.md).

## 5. Học viên tự mở rộng (không cần biết code)

| Học viên nói | Hệ thống làm |
|---|---|
| "Lưu kiểu video này của tôi" (kèm 1 video mẫu hoặc mô tả) | Tạo `mau-cua-toi/<ten-mau>/MAU.md` (nhịp, độ dài, cấu trúc lời, phụ đề, nhạc) + `video-mau.mp4`, ghi 1 dòng vào `CHI_MUC_XUONG.md`. Lần sau nói "làm video theo kiểu <tên>" là dùng |
| "Thêm cảnh này vào kho của tôi" | Chuẩn hóa về 9:16, đặt `tai-nguyen/canh/cua-toi/<nhom>/U00x.mp4`, tạo ảnh xem trước, ghi dòng vào `tai-nguyen/canh/chi-muc.csv` với `chu=hoc-vien` |
| "Thêm bài nhạc này" | Chép vào `nhac/cua-toi/`, hỏi nguồn và quyền dùng, ghi vào `nhac/NGUON.md` |
| "Lần sau làm X khác đi" | Ghi vào `mau-cua-toi/<ten>/MAU.md` mục "Rút kinh nghiệm", không sửa skill gốc |

Luật cập nhật: **mọi thứ có chữ `cua-toi` hoặc `chu=hoc-vien` là của học viên, bản cập nhật không bao giờ ghi đè.** Skill gốc nằm trong `.claude/` có thể bị thay khi cập nhật, nên mọi tùy biến phải nằm ở `mau-cua-toi/`, không sửa skill gốc.

Giai đoạn 2 cần viết skill nhỏ `xuong-mo-rong` làm 4 việc trên.

## 6. Bộ cài một câu lệnh (đã viết 25/11/2026, xem `cai/README.md`)

Khác bản thiết kế: phần mềm đặt ngoài bộ não (`%LOCALAPPDATA%\XuongVideoAI`, Mac `~/Library/Application Support/XuongVideoAI`) vì bộ não có thể đồng bộ đám mây; Windows dùng Python chính hãng python.org (Smart App Control chặn Python do uv tải về) và ghim `ctranslate2==4.8.2`; FFmpeg, Node có sẵn trên máy thì dùng luôn.

1. Kiểm môi trường: đang chạy trên máy học viên và đang mở thư mục có `INDEX.md` + ngăn 01–07. Sai thì dừng và chỉ cách chuyển.
2. Kiểm máy: hệ điều hành, RAM, ổ trống, card NVIDIA. Chọn `nhe` (≤ 8 GB RAM hoặc ổ < 6 GB) hay `du`.
3. Cài vào thư mục người dùng, không cần quyền quản trị: `uv` + Python 3.12, FFmpeg bản chạy ngay, Node bản giải nén.
4. Tải gói tài nguyên theo `PHIEN_BAN.json`, kiểm sha256, giải nén thẳng vào `08_XUONG_VIDEO/`. Đứt mạng thì chạy lại tải tiếp.
5. Chép **mọi** skill, agent (đọc mọi `goi/*/goi.json`) vào `.claude/` của bộ não; ghi mục vào `CLAUDE.md`, `INDEX.md`; điền `ho-so-kenh.json` từ ngăn 01–04.
5b. Kiểm các điều kiện trong `CHUAN_BI_THEM.md` (khóa Google, Muse, Claude in Chrome, RAM), ghi vào `xuong.json › dieu_kien`, rồi in bảng ngắn: "Đã làm được ngay: … · Muốn làm thêm X thì cần chuẩn bị: …". Thiếu điều kiện **không** làm hỏng bước cài.
6. Whisper theo RAM: ≤ 8 GB dùng `small` (hoặc `large-v3-turbo` int8), ≥ 16 GB dùng `large-v3`. Video BNI dùng mốc thời gian chữ của giọng edge-tts, không cần Whisper.
7. Dựng thử video 10 giây; đạt thì in `XƯỞNG SẴN SÀNG` và tóm tắt đã đặt gì ở đâu.

## 7. Đã sửa trong mã kế thừa (25/11/2026)

- Bỏ `cai_dat.py`, `tim_bo_nao.py`, `nhap_kho.py`; thay bằng bộ cài `cai/` (mục 6, chi tiết `cai/README.md`).
- Mọi skill đọc `<bộ não>/.claude/xuong-video.json` (bộ cài ghi): xưởng ở đâu, Python, FFmpeg, Node, engine Remotion, mô hình Whisper. Hàm chung `cau_hinh_xuong()` trong `chung.py` của từng skill, tự thêm FFmpeg/Node của xưởng vào PATH.
- Đường dẫn `~/.claude/...` → `.claude/...` của bộ não (skill, agent cài cấp dự án).
- Thư mục kênh = ngăn xưởng: cảnh ở `tai-nguyen/canh/` (tìm qua cột `tep` của `chi-muc.csv`, bỏ dòng `trang_thai=an`), nhạc `NH000x`, tiếng `AM000x`; mã cảnh cũ đổi theo `bang-doi-ten.csv` (K071, K006 không còn trong kho mới).
- Whisper theo cấu hình (`small` máy thường, `large-v3` máy ≥ 16 GB hoặc có GPU), thiếu bộ nhớ tự lùi về `small`.
- `ab-edit`, `kol-*`, `video-cay-canh`: thư mục làm việc mặc định nằm trong `08_XUONG_VIDEO/du-an/<skill>/`, thành phẩm `thanh-pham/`.
- Bỏ tên đơn vị cũ: thương hiệu mẫu `brands/vi-du.json`, mặc định `--brand vi-du`. Thông báo bản quyền MIT giữ ở `third_party/` (bắt buộc).

## 8. Nguồn kế thừa

- Mã: xem `third_party/NGUON_GOC.md`. Các skill ở `goi/` hiện là **bản chép nguyên trạng**, chưa sửa.
- Tài nguyên: gói zip 1,46 GB nhận ngày 24/11/2026 (226 cảnh, 3 nhạc Pixabay, 7 tiếng hiệu ứng). Danh mục ban đầu và bảng đổi tên: `tai-nguyen/_doi-chieu/`. Kho gốc `E:\Video-AI` đã xóa ngày 25/11/2026 sau khi chuyển đủ sang bản chuẩn.
- Mã cảnh viết cứng trong skill (mục 7): `K055`→`CA0116`, `K049`→`CA0110`, `K082`→`CA0182`, `N031`→`CA0080`, `N100`→`CA0152`. Tên nhạc, tiếng cũ (`beat-vlog`, `luot`…) đổi sang tên mới theo `bang-doi-ten.csv` (ví dụ `beat-vlog` → `NH0001_hiphop-vlog-tre-trung.mp3`; `future-bass` bắt đầu giây 9,5).
