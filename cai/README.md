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

Học viên mở Claude đúng thư mục bộ não, gõ **`/cap-nhat-xuong`** (hoặc dán lại câu trên). Không có gì mới: một dòng `✔ ĐÃ LÀ BẢN MỚI NHẤT`, không đụng gì. Có mới: thay mã, tài nguyên chỉ tải gói bổ sung (`PHIEN_BAN.json › goi_bo_sung`), báo "có gì mới" (`co_gi_moi`). Không mất video, mẫu, cảnh riêng. `XUONG_CAI_LAI=1` = cài lại đủ bước.

## Bộ cài làm gì

| Bước | Việc | Ở đâu |
|---|---|---|
| `cai.ps1` / `cai.sh` | Kiểm đúng thư mục bộ não; tải `uv`, cài Python 3.12 riêng; tải mã xưởng từ GitHub | Phần mềm đặt ngoài bộ não: Windows `%LOCALAPPDATA%\XuongVideoAI` (ổ C dưới 6 GB thì sang ổ trống nhất), Mac `~/Library/Application Support/XuongVideoAI` |
| `cai_xuong.py` 1 | Kiểm RAM, ổ, GPU → chọn gói cảnh `du` (RAM ≥ 16 GB và ổ ≥ 6 GB) hay `nhe` | |
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
