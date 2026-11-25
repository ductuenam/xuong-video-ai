# Hướng dẫn gắn nhãn cảnh video (bằng mắt) — giao nguyên văn cho tác tử con

Kho cảnh là video dọc 9:16 dài 8–10 giây, dùng làm cảnh chèn cho video ngắn tiếng Việt (giới thiệu doanh nghiệp, BNI, quảng cáo, dạy học). AI chọn cảnh bằng cách **đọc chỉ mục chữ**, nên chỉ mục phải ĐÚNG VỚI HÌNH. Tên tệp và ghi chú cũ có thể sai.

Mỗi cảnh có ảnh `5khung/<ten>.jpg`: 5 khung theo thời gian từ trái sang phải (5% · 27,5% · 50% · 72,5% · 95% độ dài), ngăn bằng vạch trắng. **Mở ảnh bằng Read cho TỪNG cảnh**, nhìn kỹ rồi mới điền. Không đoán theo tên tệp.

## Đầu ra

Một tệp CSV UTF-8 có tiêu đề, đúng các cột (ô có dấu phẩy thì bọc ngoặc kép):

`tep_goc,nhom,ten_nhom,slug,goi,nguon,giay_phep,mo_ta,tu_khoa,mau,chuyen_dong,cho_chu,doi_noi_dung,hop_video,co_dau_chu,ghi_chu`

| Cột | Điền gì |
|---|---|
| `tep_goc` | Tên tệp đúng như trong `_da-nen/` |
| `nhom` | Chọn nhóm có sẵn trong `tai-nguyen/canh/CHI_MUC.md` (bảng đầu tệp). Chỉ tạo nhóm mới khi không nhóm nào hợp; nhóm mới phải có `ten_nhom` tiếng Việt |
| `slug` | Mô tả ngắn cho tên tệp: chữ thường không dấu, nối `-`, tối đa 32 ký tự, rút từ `mo_ta` (ví dụ `o-khoa-chuyen-loi-nang-luong`) |
| `goi` | `nhe;du` nếu cảnh đẹp, dùng được nhiều loại video, nên có trong gói nhẹ; còn lại `du` |
| `nguon`, `giay_phep` | Theo phiếu giao (ví dụ `Muse`, `kho-chung`) |
| `mo_ta` | Một câu tiếng Việt có dấu, ≤ 25 chữ, tả đúng cái thấy: chủ thể, bối cảnh, ánh sáng. Cảnh đổi nội dung thì tả cả hai đoạn ("A, sau chuyển sang B") |
| `tu_khoa` | 5–8 từ khóa, chữ thường không dấu, nối `-`, cách nhau `;`. Gồm tên vật, chủ đề và cách người Việt hay gõ khi tìm (`bao-mat;an-toan;khoa;du-lieu;hacker`) |
| `mau` | TỐI ĐA 2 màu chủ đạo theo diện tích ở cả 5 khung (không tính điểm nhấn nhỏ); cảnh đổi màu nền hẳn thì màu đó phải có. Giá trị: `xanh-duong`, `xanh-la`, `xanh-ngoc`, `tim`, `cam`, `vang`, `do`, `hong`, `trang`, `den`, `xam`, `nau`, `be`, nối `;` |
| `chuyen_dong` | Chuyển động của MÁY QUAY, làm đúng 3 bước bên dưới |
| `cho_chu` | `tren`, `giua`, `duoi` (ghép `;`) — chỉ ghi vùng TRỐNG ở CẢ 5 khung; không có thì `khong`. Không ghi theo thói quen `tren;duoi` |
| `doi_noi_dung` | `khong`, hoặc `co@~<giây>s` nếu cảnh đổi HẲN sang cảnh khác (không tính vật xoay, sáng lên). Ước giây theo vị trí khung × độ dài |
| `hop_video` | 1–3 loại, nối `;`: `bni`, `gioi-thieu-dn`, `quang-cao`, `day-hoc`, `tin-tuc`, `ban-hang`, `chuyen-canh` |
| `co_dau_chu` | Soi kỹ từng khung, nhất là GÓC PHẢI DƯỚI (công cụ tạo video hay để dấu sao ✦ mờ) và mọi màn hình, bảng, thẻ. Ghi loại và vị trí: `dau-sao@goc-phai-duoi`, `chu:K012@giua`, `chu-vo-nghia@man-hinh`, `so@bang`; nhiều thứ nối `;`. Người trông như thật thêm `nguoi-that`. Hình hoàn toàn sạch mới ghi `khong` |
| `ghi_chu` | Điều bất thường: hình méo, vật biến dạng kiểu AI, tối khó dùng. Không chắc thì nói rõ ở đây, không bịa |

### `chuyen_dong` — 3 bước
1. Chọn một vật NỀN đứng yên (tường, sàn, tòa nhà) và chủ thể chính.
2. So khung 1 với khung 5: cỡ to hay nhỏ đi? nền dịch trái/phải/lên/xuống? rìa thấy thêm hay mất bớt cảnh?
3. Kết luận một giá trị:
   - `day-vao`: chủ thể và nền cùng TO DẦN, rìa mất bớt cảnh.
   - `lui-ra`: NHỎ DẦN, thấy thêm cảnh ở rìa.
   - `lia-ngang`: nền trượt ngang (hoặc dọc), cỡ gần như giữ nguyên.
   - `bay-qua`: máy lao xuyên qua cảnh hoặc dọc theo vật dài (hành lang, đường phố), nền đổi nhiều.
   - `xoay`: CẢ KHUNG xoay hoặc máy đi vòng quanh chủ thể (nền phía sau đổi góc).
   - `dung-yen`: nền GIỮ NGUYÊN; chỉ vật trong hình chuyển động (vật xoay, hạt bay) vẫn là `dung-yen`.
   Lỗi hay gặp ở bản 1: ghi `dung-yen` khi nền có dịch; ghi `xoay` khi chỉ vật xoay còn nền đứng yên.

## Luật
- Chỉ đọc ảnh và tệp đầu vào; chỉ ghi duy nhất tệp đầu ra được giao. Không sửa, xóa, di chuyển gì trên ổ D, ổ E.
- Đủ số dòng bằng số ảnh, đúng thứ tự.

## Bài học bản 1 (226 cảnh, 25/11/2026)
- Vòng 1 dùng ảnh 3 khung: soát chéo đúng 82,6%; mô tả, từ khóa tốt nhưng chuyển động và chỗ đặt chữ sai nhiều. Vòng 2 dùng 5 khung sửa 89 ô chuyển động, 147 ô chỗ chữ. **Từ bản 2: dùng 5 khung ngay từ đầu.**
- Mọi cảnh tạo bằng Google Flow (thường dài 8 giây) đều có dấu sao ✦ góc phải dưới.
- Sau khi gắn nhãn: một tác tử khác soát chéo ngẫu nhiên khoảng 10% (đọc lại ảnh, chấm từng ô); Founder xem tờ mẫu khoảng 20 cảnh trước khi nhập kho.
