# Công cụ làm kho (cho người làm kho, không phát cho học viên)

Quy trình đầy đủ và thứ tự dùng: [../docs/BAN_DO_KHO.md](../docs/BAN_DO_KHO.md) mục 5. Chạy từ thư mục kho mã, luôn với `python -I -X utf8` (cần Python 3.12, ffmpeg/ffprobe trong PATH; `do_am.py` cần numpy, matplotlib).

| Tệp | Làm gì | Ghi vào đâu |
|---|---|---|
| `chung.py` | Đường dẫn chung, đọc/ghi chỉ mục. Chạy riêng = sinh lại `CHI_MUC.md` cả 3 loại từ `chi-muc.csv` | `tai-nguyen/*/CHI_MUC.md` |
| `nen_canh.py` | Nén cảnh mới theo chuẩn bản 1 + ảnh 5 khung + báo cáo SSIM | `_kho-nang/nguon-moi/_da-nen/` |
| `do_am.py` | Đo nhạc/tiếng (giây, LUFS, đỉnh, nhịp, độ lớn mỗi 2 giây) + ảnh sóng/phổ | `_kho-nang/nguon-moi/_do-am/` |
| `nhap_kho.py` | Nhập tệp đã gắn nhãn: cấp mã, đổi tên, chuyển vào bản chuẩn, ảnh xem trước, ghi chỉ mục + bảng đổi tên. Chạy thử nếu không có `--ghi` | `_kho-nang/ban-chuan/`, `tai-nguyen/` |
| `dong_goi.py` | Đóng 3 zip của phiên bản mới (store, ngày cố định → đóng lại ra đúng sha256), `--ghi-phien-ban` cập nhật `PHIEN_BAN.json` | `_kho-nang/goi/vN/` |
| `kiem_kho.py` | Kiểm chỉ mục ↔ tệp ↔ gói ↔ `PHIEN_BAN.json`; `--sau` giải nén thử | Không ghi gì |
| `huong-dan/GAN_NHAN_CANH.md` | Giao nguyên văn cho tác tử con gắn nhãn cảnh (ảnh 5 khung) | |
| `huong-dan/GAN_NHAN_AM.md` | Gắn nhãn nhạc, tiếng từ số đo + ảnh phổ | |

Chạy thử trên bản sao: đặt `XUONG_REPO` (bản sao thư mục kho mã có `tai-nguyen/`, `PHIEN_BAN.json`) và `XUONG_KHO_NANG` (bản sao kho nặng) trỏ vào `%TEMP%\zaios_<việc>\`.

Đã kiểm 25/11/2026: `dong_goi.py` đóng lại ra đúng sha256 của `goi/v1`; nén → nhập → sinh chỉ mục chạy trọn trên bản sao (cảnh dọc, cảnh ngang, tiếng mới, nhóm mới, thiếu nhãn thì dừng, nhập trùng thì dừng).
