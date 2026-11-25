---
name: video-cay-canh
description: Sản xuất hàng loạt video dọc 9:16 cho shop cây cảnh, sân vườn, tiểu cảnh theo kiểu "ảnh thiết kế chuyển động" - từ mô tả cảnh, Claude tạo ảnh thiết kế đẹp (nhiều cây, xếp tầng, có hồ cá) rồi biến thành clip máy quay lướt chậm như quay gimbal, tất cả trên Muse (muse.ai) qua Claude in Chrome; tự soi lỗi từng nửa giây (đứng hình, nhảy cảnh, cây biến hình), làm chậm có nội suy, lót nhạc sáng hợp không khí cảnh, chuẩn âm lượng, chấm cạnh video mẫu, viết caption và hướng dẫn đăng Reels lên Page. Một lô 10 video khác nhau khoảng 15 phút. Dùng ngay khi người dùng muốn làm video cây cảnh, video sân vườn, video tiểu cảnh, video thiết kế cảnh quan, video ban công, video hồ cá koi, làm thêm cảnh cho shop cây, ảnh thiết kế chuyển động, Reels cây cảnh, đăng video lên Page shop cây, kể cả khi không nói chữ "skill".
---

# Video cây cảnh: ảnh thiết kế chuyển động

Quy trình đã chạy thật ngày 20/11/2026: 10 cảnh khác nhau, ảnh và clip đều làm trên Muse, tự soi lỗi, dựng thành phẩm, khách duyệt "Đạt". Thời gian đo được: 10 ảnh khoảng 3 phút, 10 clip khoảng 3 phút (3 đoạn chat chạy song song), dựng khoảng 5 phút.

**Ba điều cốt lõi, đừng đổi khi chưa thử:**
- **Ảnh trước, clip sau.** Ảnh thiết kế đẹp quyết định 80% video. Clip luôn lấy đúng ảnh đó làm khung đầu.
- **Một cú máy liền, thật chậm.** Không cắt cảnh trong clip. Muse hay đi sâu hơn lệnh, nên lệnh dặn "một phần tư quãng đường" và dựng làm chậm 0,85.
- **Không giao clip chưa soi.** Khoảng 1/5 clip Muse tự nhảy sang góc khác giữa chừng.
- **Nhạc quyết định cảm xúc.** Hình đẹp mà nhạc tối, đục, dạo đầu lững lờ thì video "chán". Nhạc mẫu đã cắt sẵn đoạn hay; `dung.py` chặn nhạc nhạt.
- **Không giao video thua video mẫu.** Agent `sku-cc-cham-so-mau` đặt cạnh video mẫu, thua mặt nào sửa mặt đó.

## Đội làm việc (agent đi kèm gói)
| Agent | Việc |
|---|---|
| `sku-cc-thiet-ke` | Lên danh sách cảnh đa dạng, viết mô tả ảnh và kiểu máy vào `du-an.json` |
| `sku-cc-muse` | Gửi lệnh trên Muse, tải ảnh và clip về, gom đúng tên |
| `sku-cc-kiem-dung` | Soi lỗi, quyết cắt hay tạo lại, dựng thành phẩm |
| `sku-cc-cham-so-mau` | Đặt video thử cạnh video mẫu, chấm THUA / NGANG / HƠN từng mặt, ĐẠT mới giao |
| `sku-cc-dang-bai` | Viết caption, hướng dẫn hoặc đăng (khi được phép) |
Claude chính điều phối theo các bước dưới. Việc nhỏ có thể tự làm không cần gọi agent.

## Trước khi bắt đầu
1. `python scripts/kiem_may.py`. Còn ✘ thì sửa theo dòng → bên dưới. Lần đầu chép `cau-hinh.mau.json` thành `cau-hinh.json` và hỏi người dùng để điền.
2. Kiểm trình duyệt: `list_connected_browsers`, chọn đúng trình duyệt có Muse, mở muse.ai thấy ô "Nhắn tin".
3. Mỗi lô một thư mục trong `thu_muc_lam_viec`, ví dụ `lo-2026-11-20/`, chép `du-an.mau.json` thành `du-an.json`.

## Bước 1: Lên cảnh (2 phút)
Đọc `references/kho-canh.md`. Viết vào `du-an.json` đủ số cảnh người dùng xin, **mỗi cảnh khác nhau** về không gian, phong cách, giờ trong ngày, kiểu máy. Ưu tiên cây chủ lực của shop (`cau-hinh.json` → `shop.cay_chu_luc`). Rồi:
```bash
python scripts/lap_lenh.py <du_an>
```
Script chặn mô tả ngắn, trùng tên, có người; nhắc ⚠ khi cảnh thiếu ánh sáng có hướng, thiếu điểm nhấn màu, lô ít cảnh có nước (sửa mô tả rồi chạy lại); chia lượt 4 cảnh; ghi `lenh/anh-N.txt`, `lenh/video-N.txt`.

## Bước 2: Tạo ảnh trên Muse (3 phút)
Theo `references/lam-tren-muse.md`: mỗi `lenh/anh-N.txt` gửi trong **một đoạn chat phụ mới**, gửi liền các lượt để chạy song song. Chờ xong, tải ảnh bằng đoạn JS ở mục 4, rồi:
```bash
python scripts/gom_file.py <du_an> anh
```
**Claude xem từng ảnh** (ghép lưới cho nhanh). Ảnh ít cây, lộn xộn, có người, có chữ, toàn một màu xanh, ánh sáng phẳng, trông như rừng hoang chứ không phải sân vườn có thiết kế thì sửa mô tả và tạo lại riêng cảnh đó. Người dùng muốn duyệt ảnh thì gửi lưới cho họ trước khi làm clip; người dùng đã nói "làm luôn" thì tự duyệt.

## Bước 3: Tạo clip trên Muse (3 phút)
Mỗi `lenh/video-N.txt`: mở đoạn chat phụ mới → đính kèm đúng các ảnh của lượt đó từ `anh/` → gửi lệnh. Gửi liền các lượt. Chờ xong, tải mọi `<video>` cao ≥ 1000px, đặt tên `lo<N>-<i>.mp4`, rồi:
```bash
python scripts/gom_file.py <du_an> clip --mau "lo*.mp4"
```
Gặp lỗi "not available in your country or region" thì **dừng**, báo người dùng chuyển tài khoản Muse dự phòng; không gửi lại.

## Bước 4: Soi lỗi (2 phút)
```bash
python scripts/kiem_clip.py <du_an>
```
Rồi **mở từng tờ `kiem/<ten>.jpg`** xem bằng mắt theo `references/tu-kiem-va-dang.md`. Clip phải tạo lại thì quay về Bước 3 riêng clip đó.

## Bước 5: Dựng (5 phút cho 10 video)
```bash
python scripts/dung.py <du_an>
```
Ra `thanh-pham/<ten>-khong-nhac.mp4` (để chọn nhạc trend lúc đăng) và bản có nhạc (mặc định 8 bài nhạc mẫu CC0 trong `nhac-mau/`, đã cắt sẵn đoạn hay, tự chọn bài theo không khí cảnh bằng `nhac-mau/khong-khi.json`; muốn chỉ định thì thêm `"nhac": "nhac-05"` vào cảnh; xem `nhac-mau/NGUON-NHAC.txt`). Dòng ✘ "NHẠC TỐI ĐỤC" nghĩa là nhạc nhạt hơn hẳn video mẫu: đổi bài rồi dựng lại cảnh đó. File có chữ `CHI-FACEBOOK` thì báo rõ "chỉ đăng Facebook". Chạy nền nếu lô lớn, chờ xong mới báo.

## Bước 5b: Chấm cạnh video mẫu (3 phút)
Gọi agent `sku-cc-cham-so-mau` với thư mục dự án. Nó chạy `scripts/to_so_sanh.py`, đặt từng video cạnh video mẫu trong `video-mau/`, chấm THUA / NGANG / HƠN theo 9 mặt. **Chỉ giao khi ĐẠT** (không thua mặt nào). SỬA LẠI thì làm đúng việc nó ghi (đổi nhạc, tạo lại ảnh hoặc clip, cắt đoạn), dựng lại, chấm lại. Sau 3 vòng không lên điểm thì báo người dùng kèm danh sách lỗi.

## Bước 6: Giao và đăng
Gửi người dùng các video kèm bảng: tên cảnh, kiểu máy, độ dài, clip nào đã cắt vì lỗi. Viết caption theo mẫu trong `references/tu-kiem-va-dang.md`. Đăng chỉ khi người dùng nói rõ, theo một trong hai cách ở đó.

## Sau mỗi lô
Người dùng chê điều gì, hoặc Claude tự bắt lỗi mới: ghi vào `references/so-loi.md` và sửa luôn mô tả mẫu hoặc script. Ghi số phút thực tế mỗi bước để lô sau nhanh hơn.

## Không làm
- Không dùng tài khoản, khóa API hay đường dẫn của người khác; mỗi khách dùng tài khoản Muse của mình.
- Không bấm cấp quyền, kết nối, đồng ý điều khoản thay người dùng.
- Không đưa nhạc `CHI-FACEBOOK` lên nền tảng khác Facebook.
