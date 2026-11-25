# Bộ mô hình cảnh (canh.json)

```json
{"canh": [{"loai": "nguoi-chu", "tu": 0, "den": 4, "tren": "CHỮ TRÊN", "duoi": "CHỮ DƯỚI", "at": 3, "viTriPhuDe": 1560}]}
```

**Quy ước chung**

- `tu`, `den`: số thứ tự cụm trong `loi.txt`, đếm từ 1. `tu: 0` là đầu video. Cảnh `tu: 5, den: 8` chạy từ lúc dòng 5 bắt đầu đến lúc dòng 8 bắt đầu (gồm dòng 5, 6, 7); `moc: 6` là lúc dòng 6 bắt đầu, nên `moc` nằm từ `tu` đến `den - 1`. Sau bước `canh`, `dung.py` in "dòng a–b: «câu đầu»" cho từng cảnh: chữ trên hình phải nói đúng ý câu đó, lệch là chữ chạy trước giọng (lỗi mẫu thử BNI 24/11/2026). `den: "het"` ở cảnh cuối là hết lời cộng giữ khung cuối.
- Các cảnh phải nối liền: `den` cảnh trước bằng `tu` cảnh sau.
- `moc`, `at`: số nguyên là cụm lời, số thực là giây tính từ đầu cảnh (`0.7`), `[8, 0.9]` là cụm 8 cộng 0,9 giây. Số `0` là giây 0.
- `viTriPhuDe`: toạ độ y của phụ đề. Đặt để không đè thẻ và mặt, khoảng 1300 đến 1560.
- Tên clip (`ten`, `canhNen`, `o[].ten`) là mã trong `danh-muc-canh.csv`.
- Mặt thật lấy từ master đúng giờ của cảnh, trừ khi đặt `nguon` riêng.

## Cảnh có mặt người

| loai | Dùng khi | Trường riêng |
|---|---|---|
| `nguoi` | Chuyển ý, nói toàn màn | Không có |
| `nguoi-chu` | Mở đầu, nhấn câu chính | `tren`, `duoi`, `at` |
| `nguoi-so` | Nêu số liệu | `the: [{hinh, so, ten, them?}]`, `moc` (mỗi thẻ một mốc, tối đa 2 thẻ) |
| `ket-phe` | Kết chia phe | `cauHoi`, `phe: [a, b]`, `den: "het"` |
| `ket-comment` | Kết: câu hỏi và khung "XEM BÌNH LUẬN GHIM" (không còn chữ COMMENT) | `nhan`, `tieuDe`, `tuKhoa?` (chữ trong khung cam, mặc định XEM BÌNH LUẬN GHIM; từ khóa một chữ kiểu CÀI bị bỏ qua), `den: "het"`, `clip?` khi không quay (phụ đề dài thì đặt `viTriPhuDe` khoảng 1480 để không đè nhãn kênh). Clip kết chọn theo ý câu hỏi kết và KHÔNG trùng clip kết của 5 video gần nhất, `lap_canh.py` chặn và gợi ý clip khác (bảng `GOI_Y_KET` trong `kiem_chot.py`); cố tình lặp thì thêm `choLapCanhKet: true` |

## Cảnh AI

| loai | Dùng khi | Trường riêng |
|---|---|---|
| `flow-chu` | Chữ lớn trên clip kho | `ten`, `tren`, `duoi`, `y`, `nen` (nền tối sau chữ), `tuGiay` (bỏ qua đoạn đầu clip, dùng cho clip Q mở đầu trung tính) |
| `ten-cong-cu` | Nêu tên công cụ, nền clip mờ | `ten` (tên công cụ), `nhan`, `canhNen` (mã clip) |

Nhãn tên kênh tự che logo góc dưới phải của clip; dòng phụ dưới tên lấy từ `nhanCanhAI` trong hồ sơ, để trống thì chỉ hiện tên kênh. Không đặt chữ quan trọng ở vùng đó.

## Cảnh đồ họa nền sáng

Có `tren`, `duoi` là tiêu đề hai dòng. Tiêu đề nên là một luận điểm.

| loai | Dùng khi | Trường riêng |
|---|---|---|
| `day-chuyen` | Quy trình nhiều bước sáng dần | `buoc: [[biểu tượng, tên]...]` tối đa 9, `moc` mỗi bước một mốc |
| `hai-o-canh` | So sánh hai clip, ô thứ hai mờ dần | `o: [{ten, nhan}, {ten, nhan}]`, `moc: [hai ô hiện, ô 2 mờ]` |
| `anh-goc` | Một nguồn tỏa ra nhiều cảnh | `anh`, `catAnh?`, `o: [3 clip]`, `moc: [ảnh hiện, tỏa ra]` |
| `ba-lop` | Sơ đồ 3 lớp nối nhau | `gach?` (chữ gạch ngang), `lop: [3 {mau, ten, phu, kyHieu, phuSau?}]`, `moc` 6 mốc: lớp 3 hiện, chữ gạch hiện, lớp 2 hiện, lớp 3 sáng, lớp 1 hiện và chạy dây 1, chạy dây 2 |
| `tin-vui-buon` | Hai mặt của vấn đề | `vui: {nhan, ten, lenh?, ketQua?}`, `buon: {nhan, ten, dong?, canhBao?}`, `moc`: thẻ vui, thẻ buồn, cảnh báo |
| `canh-bao` | Danh sách rủi ro hiện dần | `dong: [[do\|vang\|xanh, tên, phụ]...]` tối đa 4, `moc` mỗi dòng một mốc |
| `hai-phe` | Hai quan điểm | `phe: [{nhan, ten, phu}, {nhan, ten, phu}]`, `moc` hai mốc |
| `so-tay` | Giải thích quy trình như một cuốn sổ, các bước đánh dấu xong | `ten`, `khi`, `buoc: [...]` tối đa 4, `tep?`, `chu?`, `moc`: sổ hiện, dòng khi nào, bước đầu, file mẫu, hoàn thành |
| `truoc-sau` | Trước và sau khi dùng | `truoc`, `sau`: `{nhan, ten, dong: [...]}`, `moc` hai mốc |
| `bieu-do` | So sánh số liệu có nguồn | `cot: [{ten, so, donVi?, noiBat?}]`, `nguon`, `moc` mỗi cột một mốc |
| `danh-sach-buoc` | Các bước cài, làm theo | `buoc: [{ten, phu?}]` tối đa 5, `moc` mỗi bước một mốc |
| `khung-chat` | Mô phỏng hội thoại với AI, có chữ "Minh họa" | `ten`, `tin: [{ai?, chu}]`, `moc` mỗi tin một mốc |
| `bang-mau` | So bộ màu theo ngành, tô trang thu nhỏ bằng màu thật, có chữ "Minh họa" | `trang: [{nhan, ten, mau: [chính, phụ, nhấn, nền, chữ, chữ trên nút?], nen?, chuTrang?, serif?, tranh?: [...], ghi?}]` 1 hoặc 2 trang, `nguon?`, `moc` mỗi trang một mốc |
| `luoi-the` | Tối đa 20 tên chia nhóm màu, sáng theo từng đợt | `nhom: [{ten, o: [...]}]` tối đa 5 nhóm, `sang: [[tên...]...]` mỗi đợt một danh sách, thẻ khác mờ đi, `moc` mỗi đợt một mốc |
| `khoi-noi` | Quy trình ghép khối nối dây, có chữ "Minh họa" | `khoi: [{ten, phu?}]` tối đa 3, `moc` mỗi khối một mốc, thêm một mốc cuối để xung sáng chạy trên dây, `loi?: {o, tu, den, nhan?, xong?}` đánh dấu khối thứ `o` hỏng từ giây `tu` đến `den` rồi hiện đã sửa (tính bằng giây từ đầu cảnh, chưa nhận mốc theo cụm lời) |
| `bieu-tuong` | Nêu chủ đề bằng biểu tượng 3D nền đen | `ma` (mã trong kho `khoBieuTuong` của hồ sơ, tự chép vào dự án) hoặc `anh` (file trong `public/`), `tren`, `duoi?` |
| `man-web` | Hình thật của trang web, khoanh đúng chỗ đang nói | `anh` hoặc `video` (đường dẫn trong `public/`), `x`, `y`, `zoom`, `cao`, `khoanh: [{x, y, w, h}]` theo pixel trang rộng 1080, `moc` mỗi khung một mốc, `nguon` (ví dụ "Ảnh chụp từ github.com, 06/11/2026") |
| `repo` | Giới thiệu kho mã nguồn khi không chụp được trang thật | `chu`, `ten`, `moTa`, `so: [[giá trị, nhãn]...]`, `nhan?` |
| `terminal` | Gõ lệnh | `lenh`, `chuChay?` |
| `cay-thu-muc` | Cây thư mục, file sáng theo từng đợt | `tep: [{ten, cap?, ghi?, san?}]` (tên kết thúc "/" là thư mục, `cap` là độ thụt), `dot: [{sang?: [...], tat?: [...], nhan?}]`, `moc` mỗi đợt một mốc, `kieu`: `cau-truc` (file hiện dần theo đợt, `san` là hiện sẵn) hoặc `chay` (cả cây hiện sẵn, đang mở viền cam, đã dùng dấu xanh, `tat` mờ kèm chữ "không mở"), `minhHoa?`. Tối đa 7 dòng |
| `tep-ma` | Mở một file, soi từng vùng dòng | `ten`, `dong: [...]` tối đa 10 dòng, mỗi dòng dưới 40 ký tự, `vung: [{tu, den, nhan}]` (số dòng đếm từ 1), `moc` mỗi vùng một mốc |

Biểu tượng trong `day-chuyen`: `y-tuong`, `viet`, `nhan-vat`, `anh`, `clip`, `mic`, `ghep`, `thumb`, `yt`, `terminal`, `duyet`, `doc`.

## Thêm mô hình mới

Sửa `engine/src/MoHinh.tsx`, thêm một `case` trong `VeCanh`, thêm dòng vào bảng trên. Chữ riêng của video đưa vào trường dữ liệu, không ghi cứng trong code. Kênh khác dùng cùng engine nên tên kênh và màu lấy từ `KENH`.

## Kiểu nền động

Mọi mô hình nền sáng nhận thêm trường `kieuNen`: `dao` (mặc định, quầng đào và hạt bay), `luoi` (lưới chấm trôi), `song` (sóng dưới đáy), `toi` (nền tối ánh cam, tiêu đề tự đổi màu sáng). Không đặt thì cảnh cũ vẫn là `dao`. Một video dùng tối đa 2 kiểu, dành `toi` cho khúc cao trào hoặc cảnh báo.

## Âm thanh theo video và theo cảnh

- Đổi nhạc: ghi vào `nhac.txt` của dự án một tên trong `boNhac` của hồ sơ, hoặc đường dẫn file. Mức nhạc đặt bằng `nhacDuoiGiong` (mặc định 10 LU); nhạc tự nén khi có giọng và nhô lên ở chỗ nghỉ. Chọn theo tâm trạng của bài, không dùng một bài cho mọi video.
- Trên một cảnh: `am` thay tiếng lúc vào cảnh, `amMoc` phát ở mỗi mốc (hợp với `danh-sach-buoc`, `khung-chat`). Giá trị là tên trong `boTieng`. Không đặt thì dùng `tiengChuyenCanh`.
- Mỗi tiếng chỉ phát 1,2 giây đầu. Tiếng dài hơn thì khai trong `boTieng` dạng `{"file": "...", "dai": 3.3}` để phát đủ số giây đó.
- Chỉ dùng tiếng khác ở vài chỗ cần nhấn, không đặt cho mọi cảnh.
