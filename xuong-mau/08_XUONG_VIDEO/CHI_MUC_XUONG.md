# CHỈ MỤC XƯỞNG VIDEO (L1 — AI đọc tệp này đầu tiên khi làm video)

> Sinh từ `xuong.json`. Mục 1–4 do bộ cài ghi, cập nhật sẽ thay. Mục 5 là của Anh/Chị, không bao giờ bị ghi đè.
> Quy chuẩn đầy đủ: `docs/QUY_CHUAN_MO_RONG.md` trong kho Xưởng Video AI.

## 1. Làm được gì (đã cài đủ, nói là làm)
| Nhóm | Làm được | Câu lệnh mẫu | Cần chuẩn bị thêm |
|---|---|---|---|
| Video người nói | Edit video quay thô; video giới thiệu bản thân BNI; video không quay (đồ họa + giọng AI) | "Edit video <tên file> cho tôi" · "Dựng video giới thiệu bản thân cho tôi theo cấu trúc BNI" | Không |
| Cắt ghép, quảng cáo | Cắt livestream thành clip ngắn; biến thể quảng cáo đổi hook; dựng quảng cáo duyệt từng bước; đồ họa HyperFrames; ảnh bìa | "Cắt livestream <tên file> thành các clip ngắn" · "Làm ảnh bìa cho video vừa dựng" | Ảnh bìa vẽ AI: khóa Google Vertex |
| KOL AI và bán hàng | KOL AI bán quần áo, lookbook, mặc thử, review nghỉ dưỡng; video cây cảnh | "Làm video KOL bán mẫu áo này cho tôi <link Shopee>" | Tài khoản Muse + Claude in Chrome |

**Trước khi làm:** việc nào có ghi "Cần chuẩn bị thêm" thì kiểm lại thật theo `CHUAN_BI_THEM.md`. Đủ thì làm luôn. Thiếu thì báo người dùng thiếu gì, cách chuẩn bị, và đề xuất cách làm được ngay.

## 2. Lấy lời và dữ liệu ở đâu
Đọc `BAN_DO_BO_NAO.md`: vai trò (hồ sơ, sản phẩm, khách hàng, giọng văn, quy trình, media) → ngăn thật của bộ não. Không bịa; thiếu thì hỏi.

## 3. Tài nguyên (L2: mở `CHI_MUC.md` của đúng loại, không mở lần lượt tệp)
| Loại | Chỉ mục | Ghi chú |
|---|---|---|
| Cảnh trám | `tai-nguyen/canh/CHI_MUC.md` | Xem ảnh `tai-nguyen/canh/xem-truoc/<mã>.jpg` khi cần nhìn |
| Nhạc nền | `tai-nguyen/nhac/CHI_MUC.md` | Không phát lại nguyên tệp nhạc |
| Tiếng hiệu ứng | `tai-nguyen/am/CHI_MUC.md` | |

## 4. Để kết quả ở đâu
- Mỗi video một thư mục `du-an/<YYYY-MM-DD>_<ten-video>/`.
- Thành phẩm chép ra `thanh-pham/<YYYY-MM-DD>_<ten-video>.mp4`.
- Không đọc lướt thư mục phần mềm của xưởng (ghi ở `.claude/xuong-video.json`, mục `may`).

**Cập nhật xưởng** (giữ nguyên mọi thứ của Anh/Chị): gõ `/cap-nhat-xuong` (hoặc nhắn "Cập nhật Xưởng Video AI"). Không có gì mới thì Claude báo ngay; có thì chỉ tải phần mới và báo "có gì mới". Claude chạy lệnh:
- Windows: `powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.ps1 | iex"`
- Mac: `curl -fsSL https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.sh | bash`

## 5. Của tôi
| Thứ | Ở đâu | Có gì |
|---|---|---|
| Kiểu video của tôi | `mau-cua-toi/<ten-kieu>/MAU.md` | (chưa có) — nói "Lưu kiểu video này của tôi" |
| Rút kinh nghiệm chung | `mau-cua-toi/_chung/RUT_KINH_NGHIEM.md` | |
| Tài nguyên của tôi | `tai-nguyen/<loai>/cua-toi/` | (chưa có) — nói "Thêm cảnh/nhạc này vào kho" |
