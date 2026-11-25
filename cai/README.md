# Bộ cài một câu lệnh

## Câu học viên dán vào Claude

Mở Claude (thẻ Code, **This computer**) **đúng thư mục Bộ Não AI** đã cài ở buổi trước, dán nguyên đoạn sau:

```
Cài Xưởng Video AI vào bộ não này. Chạy đúng một lệnh theo máy của tôi, ngay trong thư mục đang mở, chờ chạy xong rồi báo kết quả bằng tiếng Việt dễ hiểu:
- Windows: powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.ps1 | iex"
- Mac: curl -fsSL https://raw.githubusercontent.com/ductuenam/xuong-video-ai/main/cai/cai.sh | bash
Lệnh chạy lâu (10–30 phút): chạy nền và chờ, đừng chạy lại giữa chừng. Nếu lệnh DỪNG thì đọc dòng DỪNG và làm đúng hướng dẫn trong đó. Có dòng ⚠ thì giải thích cho tôi và làm theo dòng đó (hỏi tôi trước khi xóa hay chuyển thứ gì).
```

## Cập nhật (từ bản 0.2.6)

Học viên mở Claude đúng thư mục bộ não, gõ **`/cap-nhat-xuong`** (hoặc dán lại câu trên). Không có gì mới: một dòng `✔ ĐÃ LÀ BẢN MỚI NHẤT`, không đụng gì. Có mới: thay mã, tài nguyên chỉ tải gói bổ sung (`PHIEN_BAN.json › goi_bo_sung`), báo "có gì mới" (`co_gi_moi`). Không mất video, mẫu, cảnh riêng.

Biến môi trường (chỉ có hiệu lực trong lần chạy đó; skill `/cap-nhat-xuong` tự đặt):

| Biến | Làm gì |
|---|---|
| `XUONG_XEM=1` | Chỉ xem trước: bản đang có → bản mới, có gì mới, tải bao nhiêu, tệp gốc học viên đã sửa sẽ được cất, dấu vết bộ cài cũ. Không thay đổi gì |
| `XUONG_DON_BAN_CU=1` | Học viên đã OK dọn bộ cài cũ 24/11: chép giữ đồ học viên vào xưởng, kiểm đủ, rồi chuyển phần bản cũ vào Thùng rác, ghi `NHAT_KY_DON_BAN_CU.md` |
| `XUONG_CAI_LAI=1` | Chạy đủ các bước (sửa máy), vẫn giữ đồ học viên, không tải lại tài nguyên đã có |

An toàn (`an_toan.py`, kế hoạch `docs/KE_HOACH_CAI_CAP_NHAT_AN_TOAN.md`): tệp gốc học viên đã sửa được cất vào `<Xưởng>/.sao-luu/<giờ>/` trước khi thay (so dấu vân tay `.dau-van-tay.json`); giữ mọi dòng chỉ mục không phải của kho; kiểm ổ trước khi tải; báo nếu bộ não nằm trong OneDrive/Drive.

## Bộ cài làm gì

| Bước | Việc | Ở đâu |
|---|---|---|
| `cai.ps1` / `cai.sh` | Kiểm đúng thư mục bộ não; tải `uv`, cài Python 3.12 riêng; tải mã xưởng từ GitHub | Phần mềm đặt ngoài bộ não: Windows `%LOCALAPPDATA%\XuongVideoAI` (ổ C dưới 6 GB thì sang ổ trống nhất), Mac `~/Library/Application Support/XuongVideoAI` |
| `cai_xuong.py` 1 | Kiểm RAM, ổ, GPU → chọn gói cảnh `du` (ổ trống ≥ 6 GB, không xét RAM) hay `nhe` | |
| 2 | FFmpeg, Node: dùng bản có sẵn trên máy, thiếu thì tải bản chạy ngay; thư viện Python | thư mục phần mềm |
| 3 | Remotion (`npm install`) | thư mục phần mềm `engine/` |
| 4 | Tạo ngăn `08_XUONG_VIDEO` (trùng số thì số trống kế tiếp) từ `xuong-mau/`, không đè tệp đã có | bộ não |
| 5 | Tải gói tài nguyên theo `PHIEN_BAN.json` (nối tiếp khi đứt mạng, kiểm sha256), giải nén, ghi chỉ mục (giữ dòng `chu=hoc-vien`), sinh `CHI_MUC.md` | `08_XUONG_VIDEO/tai-nguyen/` |
| 6 | Chép mọi skill, agent (đè tệp của kho, giữ tệp học viên thêm); tải Whisper theo RAM (`small` / `large-v3`); ghi `.claude/xuong-video.json` | `.claude/` của bộ não |
| 7 | Ghi `xuong.json`, khối `XUONG-VIDEO` vào `CLAUDE.md` và `INDEX.md`, dựng thử 3 giây, in bảng "làm được ngay / cần chuẩn bị" | bộ não |

## Thử bộ cài (người làm kho)

Chỉ thử trên bộ não giả trong `%TEMP%\zaios_<việc>\` (có `INDEX.md` và ngăn `01_...`):

```powershell
$env:XUONG_NGUON='<kho mã này>'; $env:XUONG_MAY="$env:TEMP\zaios_cai_xuong\may"; $env:XUONG_GOI='nhe'
cd "$env:TEMP\zaios_cai_xuong\Bo-Nao-AI"; Get-Content -Raw -Encoding utf8 "$env:XUONG_NGUON\cai\cai.ps1" | iex
```

`XUONG_NGUON` bỏ qua bước tải mã từ GitHub; `XUONG_MAY` đặt phần mềm vào thư mục thử; `XUONG_GOI` ép gói cảnh.

**Cổng bắt buộc trước mỗi lần phát hành:** `python -X utf8 cong-cu/thu_cap_nhat.py` và `python -X utf8 cong-cu/thu_am.py` (nhạc, tiếng: quyền, chọn bài, nối vòng, khớp điểm nhấn, học viên tự thêm) phải in `ĐẠT HẾT` (cài, cập nhật, xem trước, sao lưu, ổ đầy, đứt giữa chừng, đổi tên ngăn, dọn bộ cài cũ; thư mục nhà và Thùng rác đều giả).
