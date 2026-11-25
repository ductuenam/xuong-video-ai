# Xưởng Video AI

Kho chuẩn của bộ làm video cài vào **Bộ Não AI** của học viên bằng **một câu lệnh**. Trạng thái: mã **0.2.9** (0.2.9: kho 31 nhạc, 47 tiếng, BNI bỏ câu dịch máy móc, dựng theo bộ nhớ còn trống; 0.2.7: cập nhật xem trước + sao lưu tệp học viên sửa + dọn bộ cài cũ 24/11; 0.2.8: nhạc tự khớp video, tiếng khớp điểm nhấn, học viên tự thêm nhạc/tiếng đúng chuẩn; bộ cài Windows đã thử thật từ GitHub trên bộ não mới tinh 25/11; skill BNI bản 2.2: khung 5 nhịp không cứng, bài 30 hoặc 60 giây, ảnh riêng từng bài, giọng tự quay, chặn lời hứa ngành có quy định; cập nhật nhanh `/cap-nhat-xuong` chỉ tải phần bổ sung; Mac chưa thử trên máy thật); tài nguyên **v2** (226 cảnh, 31 nhạc, 47 tiếng) trên Cloudflare R2.

## Cài (học viên)

Mở Claude **đúng thư mục Bộ Não AI**, dán câu trong [cai/README.md](cai/README.md). Dán lại = cập nhật, không mất đồ của mình.

## Đọc theo thứ tự

0. **[docs/BAN_DO_KHO.md](docs/BAN_DO_KHO.md) — đọc trước tiên**: mọi thứ nằm ở đâu, Founder nói gì thì làm gì, quy trình bổ sung, luật phiên bản, cách làm việc.
0b. **[docs/MUC_TIEU.md](docs/MUC_TIEU.md)**: mục tiêu, hành trình học viên, thước đo, thứ tự ưu tiên.
1. [docs/KIEN_TRUC.md](docs/KIEN_TRUC.md) — mục tiêu, bộ skill cài đủ một lần + cổng sẵn sàng, bộ não sau khi cài, cách học viên tự mở rộng, việc phải sửa.
2. [docs/QUY_CHUAN_MO_RONG.md](docs/QUY_CHUAN_MO_RONG.md) — sổ đăng ký, bốn tầng đọc của AI, bản đồ bộ não, khuôn tài nguyên chung, gói năng lực, luật cập nhật.
3. [docs/LUU_TRU_VA_PHAT_HANH.md](docs/LUU_TRU_VA_PHAT_HANH.md) — để mã ở GitHub, tài nguyên ở Cloudflare R2, quy trình phát hành.
4. [tai-nguyen/canh/CHI_MUC.md](tai-nguyen/canh/CHI_MUC.md) — 226 cảnh theo 23 nhóm, 64 cảnh trong gói nhẹ.
5. [cong-cu/README.md](cong-cu/README.md) — công cụ làm kho (nén, nhập, đóng gói, kiểm).

## Bản đồ thư mục

| Thư mục | Nội dung |
|---|---|
| `goi/video-nguoi-noi/` | Edit video, video BNI, video người nói: 1 skill, 2 agent. Không cần chuẩn bị gì |
| `goi/cat-ghep-quang-cao/` | Cắt livestream, quảng cáo, ảnh bìa, HyperFrames: 3 skill, 1 agent (ảnh bìa vẽ AI cần khóa Google) |
| `goi/kol-ai/` | KOL AI, lookbook, nghỉ dưỡng, cây cảnh: 5 skill, 20 agent (cần Muse + Claude in Chrome) |
| `xuong-mau/08_XUONG_VIDEO/` | Khung ngăn mới sẽ chép vào bộ não học viên |
| `tai-nguyen/<loai>/` | Chỉ mục từng loại (cảnh, nhạc, tiếng) theo một khuôn chung. **Không chứa video, nhạc** (để ở R2) |
| `cong-cu/` | Công cụ làm kho cho người làm kho (không phát cho học viên) |
| `_kho-nang/` | Lối tắt sang `E:\xuong-video-ai-kho\` (video, zip, báo cáo). Không lên GitHub |
| `cai/` | Bộ cài một câu lệnh: `cai.ps1` (Windows), `cai.sh` (Mac), `cai_xuong.py` (phần chính) |
| `phieu/` | Phiếu giao việc nội bộ, không đưa lên GitHub công khai |
| `third_party/` | Giấy phép MIT của mã kế thừa |

Cả 3 gói trong `goi/` **cài đủ một lần**, không chia cấp. Việc nào cần chuẩn bị thêm thì Claude kiểm lúc làm theo `xuong-mau/08_XUONG_VIDEO/CHUAN_BI_THEM.md`.

Các skill trong `goi/` kế thừa một phần mã nguồn mở (nguồn và giấy phép MIT: `third_party/`), đã sửa theo kiến trúc mới (`docs/KIEN_TRUC.md` mục 7).
