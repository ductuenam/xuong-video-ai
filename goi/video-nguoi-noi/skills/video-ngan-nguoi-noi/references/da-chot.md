# Sổ luật đã chốt

Những gì người dẫn đã nghe, xem và duyệt. **Không đổi khi chưa có một bản nâng cấp được duyệt.** Luật nào máy kiểm được thì đã nằm trong code, không dựa vào trí nhớ của người làm.

## Luật và nơi máy kiểm

| # | Luật | Chốt | Máy kiểm ở đâu | Bị chặn lúc nào |
|---|---|---|---|---|
| 1 | "AI" đọc là "Ây‑Ai", viết `Ây‑Ai` với gạch không ngắt U+2011. Không dùng `A.I.`, `Ây Ai`, `Ây-Ai` | 06/11/2026 | `da-chot.json` → `docDung`, `kiem_chot.py` | `tao_giong.py` tự thay trước khi gửi; nghiệm thu đọc lại chữ đã gửi |
| 2 | "MCP" đọc là "Em‑Xi‑Pi", "API" là "Ây‑Pi‑Ai", "USB-C" là "Diu‑Ét‑Bi Xê" | 06/11 đến 08/11/2026 | như trên | như trên |
| 3 | Số trong bản đọc viết bằng chữ, không viết số thập phân (2.5 bị đọc "hai năm") | 06/11/2026 | `camViet` | `tao_giong.py` dừng, không tốn credit |
| 4 | Cảm xúc từ câu chữ: ngoài đoạn cuối có ít nhất 1 câu cảm thán hoặc câu hỏi tu từ, có tiểu từ nói chuyện (nha, luôn, đó, này...); đoạn cuối có câu hỏi và kết bằng dấu chấm than. Thẻ (laughs), (sighs) và tham số emotion qua Vibi không có tác dụng | 07/11 và 08/11/2026 | `cam`, `kiem_chot.py` | `tao_giong.py` dừng; nghiệm thu báo ✘ |
| 5 | Giọng nhân bản trên Vibi, MiniMax speech-2.8-hd, tốc độ 1,09 | 06/11/2026 | `giong` trong `da-chot.json`, cấu hình `giongAI` của hồ sơ | |
| 6 | Nhịp: mỗi hơi 1,6 đến 2,0 giây, nghỉ 0,15 giây ở dấu phẩy, 0,25 ở dấu chấm, giữ dấu phẩy ở chỗ chuyển ý, không dùng `<#..#>` | 08/11/2026 (bản 14-prompt-v2) | `do_nhip.py`, bước ảnh tĩnh | Ảnh tĩnh báo ✘ |
| 7 | Chèn nghỉ chỉ vào khe lặng thật, không bao giờ vào khe giữa hai âm tiết trong một từ | 08/11/2026 (lỗi "tự tin" video 18) | `nghi_dau_phay.py` (bỏ qua chỗ to hơn -30 dB), `hoi_quy.py` | Hồi quy hỏng thì không đóng gói |
| 8 | Nghiệm thu máy ĐẠT và soát `to-soat.jpg` bằng mắt mới bàn giao | 05/11/2026 | `nghiem_thu.py` | |
| 9 | Kết video: câu hỏi thật cho người xem, rồi chỉ về bình luận ghim ("Hướng dẫn ... mình để sẵn ở bình luận ghim nhé!"). Cấm "Comment CÀI, mình gửi...", "bình luận chữ ... để nhận", "inbox nhận" (Meta coi là kéo tương tác, YouTube cấm đổi thưởng lấy tương tác). PDF hướng dẫn có Zalo và web của kênh, không ghi tên cá nhân | 07/11/2026, nâng cấp 16/11/2026 (người dẫn yêu cầu bỏ "comment nhận quà") | `camViet` trong `da-chot.json` (bản đọc), `kiem_cau_ket()` trong `kiem_chot.py` gọi ở `nghiem_thu.py` (loi.txt, canh.json); mẫu `hoi_quy/sai-ket-comment-*.txt` | `tao_giong.py` dừng; nghiệm thu báo ✘ |
| 10 | Không ghi nhãn "AI minh họa" trên hình; bật nhãn AI của nền tảng khi đăng | 07/11/2026 | người làm soát | |
| 11 | Nhạc chỉ lấy bài Pixabay (beat-vlog, phonk, future-bass), ghi công trong content | 07/11/2026 | `nhacDuocDung` trong `da-chot.json`, `kiem_nhac()` gọi trong `tron_am.py` (từ 11/11/2026, sau khi video 20 suýt dùng bài YouTube) | Bước trộn dừng, chưa xuất được |
| 12 | Có file người dẫn tự quay thì dựng từ file quay; chỉ có video mẫu hoặc chủ đề thì làm bằng giọng AI | 08/11/2026 | người làm chọn, xem SKILL.md | |
| 13 | Dựng xong không để rác trên ổ hệ thống: Remotion dùng thư mục tạm riêng `%TEMP%\video-ngan\<lần chạy>`, xong thì xóa đúng thư mục đó; không đụng Temp chung vì phiên khác có thể đang dựng | 08/11/2026 | `tam_rieng()` trong `chung.py` (dùng ở `dung.py`), `lap_bia.py` của skill bìa | Mỗi lần chạy in "(dọn thư mục tạm … MB)"; không thấy dòng này là chưa dọn |
| 14 | Mọi video gắn nhận diện của kênh: watermark góc dưới phải suốt video, outro ở cuối; intro chỉ khi video dài hơn `introKhiDaiHon` (60 giây). File nằm trong `nhanDien` của hồ sơ, không nằm trong skill | 09/11/2026 | `gan_nhan_dien.py` (bước `nhan-dien` của `dung.py`), `hoi_quy.py` dựng thử video giả | Gắn lỗi (sai độ dài, mất tiếng, sai khung) thì dừng, không ra `thanh-pham.mp4` |
| 15 | Video giới thiệu công cụ, skill, plugin (nhất là làm lại từ video mẫu): kiểm tình trạng HIỆN TẠI của từng món ở nguồn gốc (tài liệu chính thức, danh mục chợ plugin, trang repo) và ghi `tinh-trang.json` (`co-san`, `plugin-chinh-thuc`, `cai-them`, cách lấy, nguồn, ngày kiểm). Món đã tích hợp sẵn thì nói rõ "có sẵn, gõ lệnh là dùng", không gọi là skill phải cài, không gộp vào "cài N skill". Số sao lấy từ trang repo lúc làm, không chép từ mẫu | 12/11/2026 (người dẫn góp ý video 22: /code-review, /security-review có sẵn) | `kiem_tinh_trang()` trong `kiem_chot.py`, gọi ở `lap_canh.py` và `nghiem_thu.py`; mẫu `hoi_quy/cong-cu-*` | Lập cảnh dừng mã 3; nghiệm thu báo ✘ |

## Bản mẫu đã duyệt

| Bản | Duyệt | Dùng làm gì |
|---|---|---|
| 14-prompt-v2 | 08/11/2026 | Chuẩn nhịp giọng (1,6 đến 2,0 giây mỗi hơi, giữ dấu phẩy chỗ chuyển ý) |
| 17-linkedin bản 2, 18-rag bản 2 | 08/11/2026 | Chuẩn quy trình sau khi khóa luật: đọc Ây‑Ai, cảm xúc từ câu chữ ("…đó!", "Vậy làm sao…đây?", "nè!", "nha"), chèn nghỉ không cắt giữa từ, nghe lại đo trên sóng âm. Lời đọc nằm trong `scripts/hoi_quy/dat-*-v2-duyet.txt`, phải luôn qua cổng kiểm |

## Thủ tục khi sửa skill (bắt buộc)

1. Gặp lỗi mới: lưu một mẫu thật vào `scripts/hoi_quy/` (`sai-*.txt` phải bị bắt, `dat-*.txt` phải đạt) hoặc thêm một mục vào `hoi_quy.py`.
2. Sửa code hoặc luật. Luật máy kiểm được thì đưa vào `da-chot.json`, không chỉ viết chữ trong tài liệu.
3. Chạy `python dong_goi.py` ở thư mục chứa skill. Lệnh này chạy hồi quy trước; hỏng một mục là dừng, không đóng gói.
4. Ghi một dòng vào bảng trên: luật gì, ngày chốt, máy kiểm ở đâu.

## Nâng cấp một luật đã chốt

Chỉ khi người dẫn muốn đổi. Làm bản thử, người dẫn nghe hoặc xem và duyệt, rồi mới sửa `da-chot.json`, cập nhật mẫu `dat-*.txt` cho đúng chuẩn mới, ghi ngày nâng cấp vào bảng.
