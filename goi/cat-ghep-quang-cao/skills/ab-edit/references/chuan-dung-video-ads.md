# Chuẩn dựng video Ads (AB Edit v2) — áp cho mọi thương hiệu

Đúc kết từ các video đã dựng và được duyệt (một thương hiệu phong thủy: 2 video ads và 1 bản xào nấu, 10–13/10/2026).
Phần riêng của từng thương hiệu (màu, font, logo, từ cấm, CTA) nằm trong `brands/<tên>.json`; mẫu điền: `brands/_mau.json`.

## 1. Thông số
- Khổ mặc định **4:5 · 1440×1800 · 50fps** (Ads Facebook/Instagram). 3:4 (1440×1920) hoặc 9:16 (1080×1920) khi order yêu cầu.
- Source quay 50fps → canvas 50fps (đặt 60 sẽ khựng). Video mẫu 60fps vẫn dùng làm cảnh trám được.
- Dài 1:15–2:15. Không phụ đề chạy liên tục — chỉ **khối chữ từ khoá**.
- Giọng người nói **−16 LUFS**, nhạc nền **−18 dB** (vào 0,5s, ra 2s), không có khoảng lặng chết.

## 2. Khung kịch bản 6 phần
| Phần | Thời lượng | Nội dung | Hình |
|---|---|---|---|
| Hook | 0–5s | Câu hỏi nỗi đau / câu khách **tự kiểm tra được ngay** / "2 lỗi…" | Người nói nửa trên + hình minh hoạ/sản phẩm nửa dưới + tiêu đề 2–3 dòng trên đường giao |
| Thân bài | 5–60s | 2–3 ý đánh số, mỗi ý: dấu hiệu → hậu quả | Người nói xen trung/cận + cảnh trám đúng từ khoá + sơ đồ tự làm |
| Giải pháp | 15–25s | Sản phẩm: đặc điểm, phiên bản, thành phần | Ảnh/clip sản phẩm, khung "3 phiên bản", nhãn chỉ chi tiết |
| Khác biệt / uy tín | 5–10s | Quy trình riêng, đội ngũ, phản hồi khách | Cảnh thật của thương hiệu, thẻ feedback chữ to |
| Ưu đãi / đồng hành | 0–10s | Hỗ trợ sau bán (nếu có) | Đội ngũ, bảng thông tin |
| CTA | 6–10s | "Để lại SĐT / bình luận" | Người nói + dải tối + CTA của thương hiệu, logo outro 3s |

## 3. Người nói chính
- `scripts/master_nguoi_noi.py`: dựng đứng, màu tươi + cà da, **làm mịn da chỉ vùng mặt–cổ** (giữ nét kính/mắt/tóc), lọc tạp âm, −16 LUFS, H.264 70 Mbps.
  Đo tâm mặt trước bằng `face-match.swift` (vài khung 540×960), thử 1 khung bằng `PREVIEW=<giây>`.
- Cắt lời bằng `edl-tool.py` (propose → đọc bảng câu, NG = câu nói lại → verify nghe lại). Hai chữ dính liền không có khe lặng: thử whisper ở vài mốc
  (vd 19.38 / 19.48 / 19.60) và chọn mốc ra đúng chữ đầu. Whisper hay "nghe" ra chữ ở đoạn thở nhỏ — soi năng lượng âm trước khi cắt.
- **Không zoom / đẩy cận** trên người nói. Đổi khung trung W ↔ cận C bằng **cắt cứng** ở mỗi chỗ ngắt câu.
- Toạ độ CapCut: đơn vị = nửa khung, **y dương = đẩy hình LÊN**, x dương = sang phải. Nguồn đứng 2160×3840 trong 1440×1800, mặt ở (0,47; 0,33):
  W `scale 1.45, x 0.02, y −0.062` (mặt ~28%), C `scale 2.10, x 0.089, y −0.327` (~30%). Không để x đẩy lộ viền đen (W ≥ 1440 + 2·|x|·720).

## 4. Cảnh trám (B-roll)
- Chuẩn hoá trước bằng `prep-broll.py`: cắt 4:5 quanh chủ thể, lanczos, cùng chỉnh màu nhẹ → đồng nhất; **chậm 0,75×** (minterpolate mci).
- Mỗi cảnh 2–3,5s, gộp các cảnh ngắn liền nhau; đặt **đúng lúc người nói đọc từ khoá**.
- Chuyển cảnh **chậm, không blur**: vào "Rõ dần" 0,8s, ra "Mờ dần" 0,7s; 2 cảnh trám liền nhau = "Mix" 0,7s. Ảnh tĩnh Ken Burns rất chậm 1.00→1.04.
- Ảnh ở hook **không** "Rõ dần" (khung đầu phải có hình ngay).
- Clip Sony quay dọc không có cờ xoay → `transpose=2` (transpose=1 ra lộn ngược).
- Thiếu cảnh minh hoạ → **tự làm đồ hoạ HTML** (sơ đồ, khung sản phẩm, thẻ tự kiểm tra) rồi quay bằng `quay-html.mjs`; mẫu ở `scripts/do-hoa/`.
- Feedback tin nhắn: ảnh chụp chữ ~20px không đọc được trên điện thoại → **thẻ feedback chữ to** (ảnh thật + lời nguyên văn, không thêm sao), giữ ≥4s.

## 5. Khối chữ
- Font + màu theo `brand.json` (mặc định UTM Bebas / League Gothic; trắng / vàng #FFD400 / ô đỏ #C8102E; viền đen).
- **Không blur, không phát sáng, không ánh kim, không phóng to–thu nhỏ.** Hiệu ứng duy nhất: hiện dần + trượt lên 0,45s, ra mờ 0,35s.
- Kiểu: `title` (dòng nhỏ trắng + dòng lớn màu nhấn), `serif` (dòng lớn trắng), `hook` (2–3 dòng), `badge` (ô màu + chữ: "LỖI 1"),
  `stamp` (ô màu một dòng), `wipe`, `duo` (A – B + ô dưới), `labels` (nhãn chỉ chi tiết), `note` (chú thích nhỏ), `cta` (dải tối + 2 dòng).
- Mỗi khối 2–4s, không chồng nhau trên 1 track; chú thích phụ để track riêng. Đặt ở ngực người nói (y ≈ 0.62) hoặc dưới (0.76–0.80), không che mặt.
- Chạy `scripts/vpcs_check.py` trước khi quay chữ. Khối chữ đổi thời lượng phải quay lại.

## 6. Quy trình làm việc với người duyệt
1. Trình **ý tưởng + hook + kịch bản hình** → chờ duyệt.  2. Dựng: CLI đặt tư liệu (`NO_ANIM=1 ./rebuild.sh`), chỉnh sửa trên CapCut trực tiếp cho người duyệt xem.
3. Báo bảng thời điểm, phần dùng tạm, việc còn thiếu. 4. **Chỉ xuất khi được bảo** (thông số: `capcut-giao-dien.md`).

## 7. Xào nấu thêm video từ cùng source
- Hook mới = câu người nói mà khách tự kiểm tra được ngay; an toàn VPCS hơn hook "tiền/tài lộc".
- Lời: dùng lại câu tốt + **lần nói chưa dùng** (câu NG/dự phòng) để không trùng bản trước; bỏ câu nhạy cảm.
- Neo mọi cảnh trám/khối chữ theo **giây trong source** (`tl(src)`): đổi EDL là mọi thứ tự dời.
- Mỗi bản thêm ≥1 đồ hoạ mới (vd thẻ "Tự kiểm tra"); ngắn hơn (60–90s), đảo thứ tự cảnh trám.

## 8. Bẫy kỹ thuật
- ffmpeg thường thiếu drawtext/bilateral → `ffmpeg-full`. ffmpeg 8 làm hỏng `capcut render` → soi bằng ghép khung từ spec hoặc mở CapCut.
- zsh: `${G}[g]`, `${i}:v` phải có ngoặc nhọn. Zip tên tiếng Việt → `ditto -x -k`.
- Đã kéo nhạc/clip thư viện CapCut → **không rebuild** (file `.co-thu-vien`); muốn rebuild thì thêm lại nhạc sau.
- CapCut 9.5+: draft đã mở trong app → CLI phải thêm `--active-timeline`; luôn thoát CapCut trước khi CLI ghi.
