---
name: kol-lookbook
description: Làm video lookbook thời trang dọc 9:16 khoảng 15–28 giây, KOL AI của shop mặc 3–5 bộ đồ (hoặc 1 mẫu nhiều màu) trong studio phông trơn hoặc phòng khách sáng, không lời chỉ có nhạc, cắt cảnh nguyên phách nhạc (toàn thân → cận chân → máy tiến vào ngang eo), ảnh sản phẩm thật (ma-nơ-canh tách nền) ở góc. Mọi ảnh và clip tạo trên Muse qua Claude in Chrome; dựng, soát trên máy bằng Python + FFmpeg; cổng khóa mặt (máy + agent + người dùng duyệt mặt) để KOL của shop tuyệt đối không sai mặt, luật đồ phối giữ chân đẹp, 5 agent riêng (đặt lệnh, cắt ghép, 3 agent chấm độc lập so với video mẫu đã duyệt) và chỉ giao khi đạt ≥ 9/10, không kém video mẫu. Dùng ngay khi người dùng muốn làm video lookbook, video KOL AI phối đồ, video affiliate Shopee thời trang không lời, video giới thiệu một mẫu áo nhiều màu, dựng KOL AI riêng cho shop, kể cả khi không nói chữ "skill".
---

# Video lookbook KOL AI (chạy trên Muse)

Mình là Claude, làm cho anh chị từ link sản phẩm Shopee tới video lookbook hoàn chỉnh. Anh chị chỉ cần: chọn sản phẩm, đăng nhập Muse (https://muse.ai — không phải meta.ai) trên trình duyệt có Claude in Chrome, có bài nhạc được phép dùng, và duyệt video cuối.

Cấu hình máy: `cau-hinh.json` cạnh tệp này (đường dẫn dự án, thư mục tải về, thư mục tạm, kho, thư mục nhạc, tên thương hiệu). Đọc bằng `scripts/chung.py`. Chạy mọi script bằng `python -X utf8 scripts/<tên>.py`, luôn đặt giới hạn thời gian cho lệnh dài.

## Đọc trước mỗi video
- `references/kinh-nghiem.md` — mọi lỗi đã làm mất điểm và cách tránh (đọc HẾT).
- `references/lenh-muse.md` — mẫu lệnh Muse đã đạt (ảnh và clip).
- `references/muse-js.md` — mã chạy trên trang Muse: soi clip trước khi tải, gom và tải nhiều clip một lần.
- `references/thang-cham-lookbook.md` — thang 10 điểm, lỗi CHẶN.
- `references/ke-hoach-mau.json` — kế hoạch dựng của một video đạt 9,02/10.
- `video-mau/` — video mẫu đã duyệt: chuẩn để so, video mới không được kém hơn.

## Bước 0 — KOL thương hiệu (một lần, dùng cho mọi video)
KOL là gương mặt của shop: **tuyệt đối không được sai mặt.** Thư mục KOL (`thu_muc_kol` trong cau-hinh.json, mặc định `<thu_muc_du_an>/kol/`) phải có `kol-chuan.png` (ảnh TOÀN THÂN chuẩn, mặt rõ, chân trắng mịn, đầu gối sáng) và `kol.json`. Chưa có thì làm theo `lenh-muse.md` mục "Bước 0" (cách A: KOL/người mẫu shop đã có; cách B: KOL AI mới). Rồi `python -X utf8 scripts/khoa_mat.py chuan <thu_muc_kol>` → `mat-chuan.png`, `chan-chuan.png`; **anh chị tự xem `xem-chuan.jpg` và duyệt** trước khi làm video nào.

## Cổng khóa mặt (bắt buộc, không bỏ qua được)
Học từ lỗi thật: video thử bị chủ shop chê "lấy KOL ở đâu mà xấu", "chân đầu gối thâm, không trắng" dù agent đã chấm đạt. Nên:
1. **Ảnh gốc** (sau bước 2): `khoa_mat.py anh <video>` → tờ `khoa-mat/to-anh.jpg` (mặt từng bộ cạnh mặt chuẩn, chân cạnh chân chuẩn, áo cạnh ảnh shop) → agent `sku-lb-soi-da-mat` chấm từng tệp (`khoa_mat.py cham`), ngưỡng 4/5 → `khoa_mat.py kiem <video> --buoc anh` phải qua thì mới gửi clip lên Muse.
2. **Clip** (sau bước 3): `khoa_mat.py clip <video> ke-hoach.json` → `to-mat.jpg` (mặt mỗi giây của clip máy tiến), `to-chan.jpg` (clip chân mỗi giây, đo màu da) → agent chấm → `dung_lookbook.py` tự DỪNG nếu clip nào trong kế hoạch chưa qua.
3. **Người dùng duyệt mặt** (sau khi 3 agent chấm đạt): anh chị tự mở `to-mat.jpg`, `to-anh.jpg` và xem video; ưng thì `khoa_mat.py duyet <video> --nguoi "<tên>" --ghi "<lời duyệt>"`. `luu_kho.py` DỪNG nếu chưa duyệt. Máy và agent chấm đạt CHƯA ĐỦ (đã gặp agent nói "giống" mà chủ shop nói "không giống").
Tệp nào đổi sau khi chấm/duyệt thì mất hiệu lực, phải chấm lại. Mặt lệch dù nhẹ (bè, đầy, dài, gầy, cằm nhọn, son đổi màu) là tạo lại ảnh/clip đó, không vá bằng dựng.

## Các bước một video
Thư mục một video: `<thu_muc_du_an>/<tên-video>/` gồm `boN/` (shopee/, toan.png, chan.png, goc.png, goc-tach.png, k-toan.png, k-chan.png), `clip/` (bN-tien.mp4, bN-chan.mp4), `nguon.md`, `ke-hoach.json`, `khoa-mat/`.
1. **Chọn sản phẩm** (anh chị đưa link, hoặc nhờ mình tìm mẫu bán chạy trên Shopee): 3–5 sản phẩm khác nhau, hoặc 1 mẫu có ≥ 3 màu khác rõ. Tải ảnh shop vào `boN/shopee/`, ghi `nguon.md` (tên, link, giá lúc chọn, số đã bán, màu dùng, đồ nào là đồ phối). Chọn đồ phối theo "Luật đồ phối để chân luôn đẹp" (`lenh-muse.md`): ưu tiên quần dài, váy dài, quần tất + bốt.
2. **Ảnh gốc trên Muse** — agent `sku-lb-lenh` viết lệnh; mình gửi Muse từng ảnh (mỗi tin một ảnh): toàn thân = **sửa đồ trên `kol-chuan.png`** (2 phương án mỗi bộ) → **cổng khóa mặt bước ảnh** → ảnh cận chân và ma-nơ-canh nền xanh sửa từ ảnh đã qua cổng → cổng lại cho `chan.png` → `tach_nen_xanh.py` → cắt khung đầu 720×1280. (Tùy chọn) đổi nền sang phòng khách trên ảnh đã qua cổng.
3. **Clip Muse** — mỗi bộ 2 clip: `bN-tien` (máy tiến tới ngang eo) và `bN-chan` (máy đứng yên, gấu xuống giày). Mỗi tin một clip; soi 6 khung ngay trên trang trước khi tải (mặt so với mặt chuẩn, chân); hỏng thì gửi lại kèm câu nêu đích danh lỗi. Gom tất cả clip vào một gói, tải một lần, `tach_goi_muse.py <thư mục>/clip`.
4. **Nhạc** — bài anh chị có quyền dùng (thư viện nhạc miễn phí bản quyền, nhạc đã mua, hoặc nhạc có sẵn trong ứng dụng đăng bài). Đo lưới phách `do_phach.py <bài>`. Gói có sẵn 1 bài CC0 dùng được mọi nền tảng: `nhac-mau/nhac-01-discoed-124bpm.mp3` (phach 0.4839, nhac_tu 4.274 — bỏ 4 giây dạo đầu nhỏ tiếng; xem `nhac-mau/NGUON-NHAC.txt`). Trong kế hoạch ghi `"nhac"` bằng ĐƯỜNG DẪN TUYỆT ĐỐI.
5. **Cắt ghép** — agent `sku-lb-dung`: bảng chớp, điểm cắt nguyên phách, kế hoạch `ke-hoach.json`, **cổng khóa mặt bước clip**, `tu_soat.py` phải ĐẠT (mở tờ mắt điểm cắt và tờ so mặt các bộ), dựng `dung_lookbook.py`, soát `tu_soat.py --video`. Chữ thương hiệu: `"chu"` = `ten_thuong_hieu` trong cau-hinh.json (để trống nếu chưa có).
6. **Chấm** — gọi 3 agent `sku-lb-soi-da-mat` (/3,5, gồm cả chân), `sku-lb-soi-trang-phuc` (/4), `sku-lb-cham-dung` (/2,5); đưa đường dẫn video, mốc cảnh, ảnh shop, `mat-chuan.png`, `chan-chuan.png`. Mỗi agent đặt video cạnh **video mẫu đã duyệt** (`video-mau/` của skill, `<thu_muc_du_an>/video-da-duyet/`) và ghi KHÔNG KÉM / KÉM từng mặt. **Chỉ giao khi tổng ≥ 9, không lỗi CHẶN, không KÉM mặt nào.** Chưa đạt thì sửa đúng chỗ agent chỉ, chấm lại cả 3.
7. **Người dùng duyệt mặt** (cổng bước 3), rồi **lưu và giao** — `luu_kho.py <thư mục video> <video>` (tự kiểm cổng); ghi `DIEM-CHAM.md` (điểm từng vòng); video anh chị duyệt chép vào `<thu_muc_du_an>/video-da-duyet/` để làm chuẩn so cho video sau; xóa thư mục tạm.

## Trước khi đăng
- Nhạc: chỉ đăng nơi bài nhạc được phép (đọc kỹ điều khoản của bài).
- Bật nhãn "nội dung AI" theo quy định của nền tảng; KOL là AI thì đừng để người xem tưởng người thật đang review.
- Ảnh góc là ma-nơ-canh AI dựng từ ảnh shop: đối chiếu màu với hàng thật, ghi chú màu lệch trong `nguon.md`.
- Không dùng gương mặt người thật khi chưa có đồng ý bằng văn bản; không làm KOL giống người nổi tiếng.

## Thời gian và số vòng (đo thật)
Video thử của gói (23/11/2026, KOL thương hiệu, 3 bộ): khoảng 4 giờ gồm ảnh gốc, 17 clip Muse, 5 bản dựng. Cổng khóa mặt chặn và bắt làm lại 12 lần (; thêm 1 vòng chủ shop yêu cầu da sạch không nốt ruồi) — đó là việc cổng phải làm. Thường cần 2–3 vòng chấm thành phẩm. Đã có lệnh mẫu sửa sẵn các lỗi trên nên lần sau ít vòng hơn.
