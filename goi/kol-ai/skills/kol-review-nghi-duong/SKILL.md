---
name: kol-review-nghi-duong
description: Làm video dọc 9:16 khoảng 45–55 giây, KOL AI (mặc định KOL riêng của bạn, mặt khóa y như video đã duyệt, trang điểm xinh hơn, đồ nghỉ dưỡng tông kem trắng be) đi review một khu nghỉ dưỡng, homestay, resort - 7 bối cảnh, cắt 2,5–4 giây một cú, KOL nói vào máy tự nhiên như vlog, phụ đề từ khóa vàng, ô ảnh góc "Ảnh chủ khu gửi", nhãn AI, nhạc nền - theo video mẫu "Anh chị làm du lịch, nghỉ dưỡng đâu rồi". Nhận ảnh chủ khu gửi (hoặc tạo bối cảnh minh họa), đặt KOL vào đúng từng chỗ trên Muse, viết lời theo khuôn 5 phần, tạo clip nói, dựng bằng script, rồi 4 agent giám sát chấm so với video mẫu. Dùng ngay khi người dùng muốn làm video review khu nghỉ, homestay, resort, villa, khách sạn, nhà gỗ, glamping bằng KOL AI hoặc người mẫu ảo, video chào dịch vụ làm video cho chủ khu du lịch, video giống mẫu nghỉ dưỡng, hoặc gửi ảnh khu nghỉ nhờ làm video, kể cả khi không nói chữ "skill". Không dùng cho video KOL bán quần áo (kol-ban-quan-ao), lookbook (kol-lookbook) hay video người thật nói.
---

# KOL AI review khu nghỉ dưỡng

Chuẩn là video mẫu (51,3 giây; video mẫu không đi kèm kho công khai — muốn so cạnh thì tự đặt video mẫu của mình vào `video-mau/mau-nghi-duong.mp4` trong thư mục skill) và bản phân tích `references/phan-tich-mau.md` — đọc bản phân tích trước video đầu tiên. Video mới phải **không kém mẫu ở mặt nào** và **hơn mẫu ở mặt KOL** (mẫu bị đổi mặt giữa các cảnh).

**Bốn điều cốt lõi:**
1. **Một KOL, một mặt, mọi cảnh.** Mọi ảnh KOL sửa từ ảnh chuẩn đã duyệt (`assets/anh-goc-kol.png` — KOL riêng của bạn, tự tạo theo `assets/README.md`), không bao giờ tạo mặt mới. Cổng `scripts/khoa_mat.py` + agent `nd-soi-mat-kol` + **người dùng duyệt mặt** (máy đạt chưa đủ: đã có lần agent nói "giống" mà người dùng nói "không giống").
2. **Hình khớp lời.** Lập bảng cảnh trước: câu nào – bối cảnh nào – động tác gì. Nói đèn thì đứng cạnh đèn, nói hoàng hôn thì đang hoàng hôn.
3. **Lời tự nhiên, đúng sự thật.** Khuôn 5 phần, câu ngắn, chữ đệm khẩu ngữ, không hứa sai, KOL tự nhận người mẫu ảo.
4. **Giám sát trước khi giao.** 3 người soi chấm độc lập rồi `nd-giam-sat-cuoi` quyết. Giữ bản nháp và phiếu từng vòng.

## Agent giám sát (bộ cài chép vào `~/.claude/agents`)

| Agent | Lúc dùng | Chấm |
|---|---|---|
| `nd-soi-mat-kol` | Tờ KOL, ảnh KOL trong bối cảnh, clip, thành phẩm | Danh tính, không méo, xinh/trang điểm, bộ đồ (10) |
| `nd-soi-loi-giong` | Kịch bản trước Muse; clip và thành phẩm | Khuôn, tự nhiên, sự thật, minh bạch AI, thời lượng (10) |
| `nd-cham-so-mau` | Thành phẩm, đặt cạnh video mẫu | 10 mục dựng: nhịp, đẩy vào, hình khớp lời, chữ, ô ảnh, nhãn, nhạc, cảm giác |
| `nd-giam-sat-cuoi` | Sau 3 người soi | ĐẠT / SỬA LẠI, kiểm chéo người soi |

Giao agent chạy lần lượt, một agent một lúc (cho nhẹ máy). Đưa agent đường dẫn thư mục video, không dán ảnh vào lời giao. Agent mới cài chỉ nạp ở phiên sau: trong phiên đang chạy thì giao `general-purpose` với lời "đóng vai, làm đúng tệp `~/.claude/agents/<tên>.md`".

## Trước khi bắt đầu

- Đọc `references/so-loi.md`.
- Thư mục video nằm **trong thư mục Claude Code đang mở** (trình duyệt chỉ đính được ảnh từ đó). Cấu trúc: `kol/`, `boi-canh/`, `anh-kol/`, `phieu/`, `lenh/`, `loi.json`, `video.json`, `ke-hoach.json`, `CHECKLIST.md`.
- Muse: `references/lam-tren-muse.md`. Nhiều chat cùng dùng Muse thì chạy lần lượt.

## Bước 1: Bối cảnh (5–10 phút)

- **Có ảnh chủ khu gửi (video thật):** chọn 7 chỗ đẹp nhất theo khuôn bối cảnh (cửa/mặt tiền, lối đi, hiên, phòng ngủ, ban công, view, hoàng hôn hoặc chỗ đặc trưng), `python scripts/cat_916.py <ảnh> boi-canh/bcN.png --tam x,y`. Ghi `nguon.md`: mỗi ảnh thấy gì (để lời chỉ nói cái có thật), tên khu, giá, liên hệ chủ khu xác nhận. Thiếu chỗ nào thì bỏ cảnh đó, không bịa.
- **Chưa có ảnh (video thử, video chào dịch vụ):** tạo bối cảnh minh họa trên Muse theo `references/lenh-muse.md` L0; ô ảnh góc ghi "Bối cảnh minh họa" thay "Ảnh chủ khu gửi".

## Bước 2: KOL và bộ đồ (5 phút + chờ duyệt)

1. Muse L1: đính ảnh chuẩn, trang điểm xinh hơn, 3 bộ đồ học phong cách mẫu (tông kem – trắng – be, linen, satin, kính râm cài đầu, mũ cói). Lưu `kol/1-bo1.png`…
2. `python scripts/khoa_mat.py kol <thư mục video>` → `khoa-mat/to-kol.jpg`. Giao `nd-soi-mat-kol` chấm (QUA khi danh tính ≥ 3,5/4).
3. **Gửi người dùng tờ KOL duyệt** (mặt, trang điểm, chọn 1 bộ). Chưa duyệt không làm tiếp. Lần sau cùng KOL + cùng bộ đã duyệt thì dùng lại, không cần duyệt lại tờ này.

## Bước 3: Lời và bảng cảnh (5 phút)

- Viết `loi.json` theo `references/khuon-loi.md` (loại A chào dịch vụ / loại B review cho khách). Mỗi cảnh: `loi` ≤ 40 chữ, `tu_khoa` (tô vàng), `the` (+ `the2`) với `khi_noi`.
- `python scripts/soat_loi.py <thư mục video>` phải QUA, rồi giao `nd-soi-loi-giong` (lúc 1) chấm kịch bản; sửa tới khi QUA.
- Viết `video.json`: `kol_chuan`, `bo_do` (mô tả nguyên văn bộ đã duyệt), `canh`: `id`, `boi_canh`, `anh_kol`, `clip`, `tu_the` (tư thế ảnh khung đầu), `dong_tac` (động tác theo giây trong clip, khớp chữ).

## Bước 4: Ảnh KOL trong bối cảnh (10 phút)

- Muse L2: mỗi tin ảnh 1 = ảnh KOL bộ đồ đã duyệt + 3 bối cảnh → 3 ảnh khung đầu. Lưu `anh-kol/k1…k8.png` (`nhan_tai.py --vao anh-kol`). Đính bản JPG trong `gui/` (PNG 4 ảnh vượt 10 MB).
- **Khung đầu phải là TRUNG CẢNH GẦN từ hông trở lên, mặt rộng ≥ 15–20% bề ngang khung.** Video thử 23/11: khung đầu toàn thân (mặt ~90 px) cho 5/8 clip trôi mặt; khung trung cảnh gần thì giữ mặt. Không cắt phóng ảnh mặt nhỏ thay cho tạo ảnh mới (phóng > 2 lần vẫn trôi). Muse hay trả ảnh rộng hơn lệnh: soi lại, rộng quá thì tạo lại.
- Soi từng ảnh: mặt đúng, đồ đúng, người đúng tỉ lệ và đúng ánh sáng với cảnh, tay đủ ngón. `khoa_mat.py kol` lại rồi `nd-soi-mat-kol` chấm; ảnh nào mặt dưới 4/5 thì tạo lại ảnh đó (L4) — sửa ở ảnh rẻ hơn sửa ở clip.

## Bước 5: Clip nói (10–15 phút Muse)

- Muse L3: 2–3 clip một tin, chạy 2–3 tin song song (đoạn chat riêng). Tải về theo nhãn `cN-noi`. **Đính thêm ảnh bộ đồ đã duyệt làm "ảnh tham chiếu gương mặt, không dùng làm khung"**, và lệnh có: MÁY CỐ ĐỊNH như trên chân máy, không đẩy vào mặt, bối cảnh giữ nguyên; tròng mắt nâu đen không lens; son hồng cam không đỏ; "luôn tươi cười kể cả khi nói câu than thở, không mếu, không nhíu mày".
- **Câu than (nỗi đau) Muse hay diễn mặt ấm ức.** Viết câu đó ngắn, như câu hỏi vui ("…đúng không nào?"), dặn "mỉm cười dịu suốt clip".
- `python scripts/so_loi.py c1-noi.mp4="<lời c1>" …` cho mọi clip: khớp lời, chữ/giây, chữ cuối trước 8,5 giây.
- `python scripts/khoa_mat.py clip <thư mục video>` → `to-mat.jpg`, `to-do.jpg`. Giao `nd-soi-mat-kol` chấm từng clip, ghi `khoa_mat.py cham <thư mục> c1-noi.mp4 mat=4.5 do=5 --nguoi nd-soi-mat-kol`.
- Clip lỗi nặng (đổi mặt, đọc sai nghĩa, mất chữ, đổi giọng, méo tay): tạo lại đúng clip đó (L4), tối đa 3 lần.

## Bước 6: Dựng (5 phút)

`python scripts/lap_ke_hoach.py <thư mục video> --nhan-o-anh "Ảnh chủ khu gửi"` lập sẵn `ke-hoach.json` (Whisper lấy mốc chữ, cắt ở chỗ ngắt hơi, bỏ lặng dài, ngừng thêm sau câu hỏi, cảnh kết giữ 1,5 giây sau chữ cuối, đẩy vào 1,0 → 1,18 → 1,32, tự tính `toc_do` ≤ 1,08 để vừa ~53 giây). Ghi đè từng cảnh trong `video.json`: `"cat": [[tu, den, zoom, "ảnh phủ"], …]` (phần tử thứ 4 = phủ hình bằng ảnh, giữ tiếng: dùng khi lời nói về ảnh/view, hoặc che đoạn mặt lỗi), `"den_toi_da"` (cắt trước đoạn hỏng cuối clip). Kế hoạch gồm:
- `mo_dau`: 0,9 giây ảnh bối cảnh c1 + ô vàng "Ảnh chủ khu gửi" (video thử: "Bối cảnh minh họa").
- `doan`: mỗi cảnh 2–3 đoạn cắt **ở khoảng ngắt hơi giữa câu** (lấy mốc từ `so_loi.py`), đoạn sau `zoom` lớn hơn (1,0 → 1,2 → 1,35, `tam` vào mặt) hoặc `zoom_cuoi` để đẩy máy chậm; đoạn đầu mỗi cảnh có `o_anh` = ảnh bối cảnh đó. Cắt bỏ đoạn im lặng cuối clip (sau chữ cuối 0,15–0,3 giây). Nối lúc mắt mở.
- `the` lấy từ `loi.json` (script đặt giờ theo `khi_noi`), `nhan_ai`, `nhan_kol`, `the_ket`, `nhac` (`tai-nguyen/nhac/beat-vlog.mp3`, Pixabay, −21 dB).
- `python scripts/dung_video.py <thư mục video> --nhap` (bản nháp) → xem `phu-de.json` (sửa tay chữ sai), rồi `python scripts/dung_video.py <thư mục video> --chi-chu` (bản chuẩn). Mỗi vòng lưu `thanh-pham-vN.mp4`, không ghi đè vòng trước.

## Bước 7: Giám sát (10 phút)

1. Lần lượt: `nd-soi-mat-kol` (thành phẩm + to-mat), `nd-soi-loi-giong` (lúc 2), `nd-cham-so-mau`. Lưu phiếu vào `phieu/vN-<agent>.md`.
2. `nd-giam-sat-cuoi` → ĐẠT / SỬA LẠI. SỬA LẠI thì làm đúng danh sách việc, dựng vòng mới, chấm lại phần liên quan.
3. Lỗi mới → thêm dòng vào `references/so-loi.md`.
4. **Người dùng duyệt mặt** bằng tờ `khoa-mat/to-mat.jpg`, rồi `khoa_mat.py duyet <thư mục> --nguoi "<tên>" --ghi "<lời duyệt>"`.

## Bước 8: Giao

Báo: đường dẫn thành phẩm, độ dài, điểm 4 agent, so với mẫu (hơn/ngang/kém từng mặt), lỗi nhẹ còn lại, chữ cần nghe bằng tai (agent, tên riêng), việc phải kiểm trước khi đăng:
- **Nhãn AI:** giữ nhãn "Video do AI tạo ra" và bật nhãn nội dung AI của nền tảng.
- **Đúng khu thật:** chủ khu xem lại từng câu nói về khu; ảnh khu phải của chủ khu hoặc được phép dùng.
- **Gương mặt:** KOL không giống người nổi tiếng; mặt người thật chỉ dùng khi có đồng ý bằng văn bản.
- **Nhạc:** nhạc Pixabay dùng được trên mạng xã hội; nhạc "chỉ Facebook" không đưa lên nền tảng khác.

## Tệp trong skill

| Tệp | Dùng khi |
|---|---|
| `references/phan-tich-mau.md` | Hiểu video mẫu: bảng cảnh, lời, cách nói, chữ, nhạc |
| `references/khuon-loi.md` | Viết lời 2 loại A/B, luật sự thật |
| `references/lenh-muse.md` | Lệnh Muse L0–L4 |
| `references/lam-tren-muse.md` | Thao tác Muse qua Claude in Chrome |
| `references/ke-hoach-mau.json` | Kế hoạch dựng mẫu (video thử 23/11) |
| `references/so-loi.md` | Sổ lỗi — đọc trước, ghi thêm sau |
| `agents/*.md` | 4 agent giám sát |
| `scripts/khoa_mat.py` | Cổng khóa mặt: tờ KOL, tờ mặt từng cảnh, chấm, duyệt, kiểm |
| `scripts/soat_loi.py`, `so_loi.py` | Soát kịch bản; nghe lại clip so lời |
| `scripts/lap_ke_hoach.py` | Lập kế hoạch dựng tự động từ mốc lời |
| `scripts/viet_lenh.py` | Sinh lệnh Muse L2 (KOL vào bối cảnh), L3 (clip nói) từ video.json + loi.json |
| `scripts/dung_video.py` | Dựng: cân độ to từng clip, cắt đúng số khung (không lệch tiếng), đẩy máy, phủ ảnh, phụ đề từ khóa vàng không tách từ ghép, thẻ không tràn cảnh, ô ảnh, nhãn AI, thẻ kết, nhạc |
| `scripts/tach_khung.py` | Tờ khung 1 giây/ô, đặt cạnh video mẫu |
| `scripts/nhan_tai.py`, `cat_916.py` | Nhận tệp tải từ Muse; cắt ảnh chủ khu về 9:16 |
| `video-mau/`, `video-thu/` | Video mẫu; video thử, bản nháp và phiếu từng vòng (giáo trình trước – sau) |
