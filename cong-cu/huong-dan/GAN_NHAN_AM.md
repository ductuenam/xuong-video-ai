# Hướng dẫn gắn nhãn nhạc nền và tiếng hiệu ứng

AI không nghe được trực tiếp. Gắn nhãn dựa trên **số đo của máy** (`cong-cu/do_am.py`) và **ảnh dạng sóng + phổ** (`nguon-moi/_do-am/<tên>.png`, mở bằng Read), cộng thông tin trang nguồn (tên bài, thể loại trên Pixabay…). Không tả theo tên tệp.

Đọc ảnh:
- Dạng sóng to, dày đều = đoạn beat/cao trào; mỏng = dạo, lắng. Bảng `do_lon_moi_2s` (dB mỗi 2 giây) dùng để ghi mốc giây các đoạn.
- Phổ có vạch ngang song song kéo dài = tiếng có cao độ (chuông, "ting", "tít"); vùng sáng loang đều = tiếng ồn (gió vút, nhiễu); vệt dốc = tiếng lướt.
- Nhịp/phút máy ước có thể gấp đôi hoặc một nửa nhịp thật: hip hop, lo-fi thường 80–100; phonk, EDM 120–150. Ghi `~` trước số.

## Nhạc nền — cột của `nhan.csv`
`tep_goc,nhom,ten_nhom,slug,goi,nguon,giay_phep,mo_ta,tu_khoa,nhip_bpm,nang_luong,tam_trang,hop_video,doan,bat_dau_goi_y,do_lon_lufs`

| Cột | Ví dụ |
|---|---|
| `mo_ta` | "Nhạc hip hop vlog nhịp vừa, trống đều, vui và trẻ trung; giữa bài có đoạn lắng (bài gốc: Vlog Hip Hop · ProducesPlatinum)" |
| `tu_khoa` | `hip-hop;vlog;tre-trung;vui;gioi-thieu;nhac-nen` |
| `nhip_bpm` | `~92` |
| `nang_luong` | `nhe`, `vua`, `manh`, `tang-dan` |
| `tam_trang` | `vui;am-ap`: 1–3 từ trong từ điển `goi/video-nguoi-noi/skills/video-ngan-nguoi-noi/references/tu-dien-am.json` (vui, am-ap, soi-dong, tin-cay, sang-trong, thu-gian, cam-xuc, truyen-cam-hung, a-dong, thanh-tinh); `nhap_kho.py` tự đổi từ đồng nghĩa, chặn từ lạ |
| `hop_video` | `bni;gioi-thieu-dn;day-hoc` |
| `doan` | `0-4 mở nhẹ; 4-47 beat đều; 47-64 lắng; 64-110 beat lại; 110-114 tắt dần` |
| `bat_dau_goi_y` | Giây nên bắt đầu cắt (bỏ đoạn dạo quá nhỏ): `9.5` |
| `do_lon_lufs` | Số `lufs` máy đo: `-6.5` (càng gần 0 càng to, phải hạ nhiều khi có giọng) |

Nhạc phải có nguồn và quyền dùng rõ, ghi thêm vào `tai-nguyen/nhac/NGUON.md`. Không nhận bài YouTube Audio Library (chưa rõ quyền dùng ngoài YouTube), bài gắn Content ID, bài có nhãn AI.

## Tiếng hiệu ứng — cột của `nhan.csv`
`tep_goc,nhom,ten_nhom,slug,goi,nguon,giay_phep,mo_ta,tu_khoa,giay,diem_nhan_s,do_lon,dung_khi`

| Cột | Ví dụ |
|---|---|
| `nhom` | `giao-dien` (bật thẻ, thông báo, chụp…) hoặc `chuyen-canh` (lướt, vút) hoặc nhóm mới |
| `mo_ta` | "Tiếng gió vút dồn dần lên rồi cắt gọn ở giây 1,1" |
| `giay` | `1.33` |
| `diem_nhan_s` | Giây mạnh nhất, để đặt trùng lúc hình đổi: `1.10` |
| `do_lon` | `nho (đỉnh -12 dB, nên tăng 6 dB)`, `vua`, `rat-to (đỉnh vượt 0 dB, nên hạ 8 dB)` |
| `dung_khi` | `chuyển cảnh lớn; đặt giây 1,1 trùng điểm cắt cảnh` |
