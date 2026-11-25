---
status: draft
version: 0.1.0
updated: 2026-11-25
---

# Đề xuất kho ảnh minh họa (việc 4 của MUC_TIEU mục 12, chờ Founder duyệt)

## 1. Vì sao làm ảnh trước video

| | Ảnh | Video cảnh trám |
|---|---|---|
| Tạo một cái | vài giây đến 1 phút (Nano Banana 2.1 trên AI Studio) | vài phút, tốn credit hơn nhiều |
| Dung lượng | khoảng 300–500 KB | khoảng 3–4 MB |
| 200 cái | khoảng 80 MB: vào được cả gói nhẹ | khoảng 800 MB |
| Dùng trong video | đã dùng được ngay: mã hiện có (`clip_toi` trong `bni.py`) biến ảnh thành clip dọc 8 giây có chuyển động phóng chậm | dùng thẳng |

Kho cảnh video hiện có 72% là công nghệ (màn hình ảo, robot, máy chủ), chỉ 12 cảnh ngành nghề, khoảng 15 cảnh có người. Học viên làm spa, cà phê, bảo hiểm… gần như không có cảnh đúng nghề. Ảnh lấp chỗ thiếu này nhanh và rẻ nhất. Về sau, ảnh đẹp nhất làm "ảnh gốc" để Founder biến thành video bằng công cụ tạo video (mục 6).

## 2. Kiểu ảnh

| Kiểu | Tỉ lệ trong kho | Dùng cho |
|---|---|---|
| **Ảnh chụp chân thực** (như ảnh chủ doanh nghiệp lo lắng Founder tạo 25/11) | khoảng 70% | Người Việt, cửa hàng, văn phòng nhỏ, khách hàng, đời sống. Đây là thứ học viên cần nhất, nhìn thật nên tin |
| **3D sạch, nền trơn** (khối, biểu tượng nổi) | khoảng 20% | Ý trừu tượng khó chụp: tăng trưởng, an toàn, tiết kiệm thời gian, kết nối, quà tặng, lịch hẹn |
| **Nền để đặt chữ** (mờ, ít chi tiết, có khoảng trống) | khoảng 10% | Thẻ chữ, câu dễ nhớ, lời kêu gọi; không giành chú ý với chữ |

Không làm tranh hoạt hình, đất sét, anime ở đợt đầu: lạc với video người thật nói.

**Luật chung cho mọi ảnh** (ghi sẵn vào mọi câu lệnh tạo ảnh):
- Dọc 9:16, độ phân giải 2K nếu có (1K vẫn dùng được, máy phóng chậm nên cần dư điểm ảnh).
- Không chữ, không số, không logo, không thương hiệu thật, không màn hình có giao diện thật.
- Người Việt Nam, bối cảnh Việt Nam (đồ vật, biển hiệu không chữ, ánh sáng thật). Không giống người nổi tiếng.
- Chủ thể ở giữa; 20% phía trên và 25% phía dưới thoáng để đặt chữ và phụ đề.
- Ánh sáng tự nhiên, màu ấm vừa phải; một kiểu máy ảnh cho cả bộ để các ảnh ghép cạnh nhau không lệch tông.
- Tay, mặt, chữ trên đồ vật phải soát kỹ (lỗi AI hay gặp nhất).

## 3. Chia nhóm và số lượng

Chia theo **nhịp bài bán hàng / BNI** chứ không theo chủ đề rời: máy chọn ảnh theo câu đang nói tới nhịp nào.

### Đợt 1: khoảng 210 ảnh

**Lớp chung, dùng cho mọi ngành (120 ảnh):**

| Nhóm | Số | Ví dụ |
|---|---|---|
| `noi-dau` Vấn đề, nỗi lo | 20 | chủ shop lo vì vắng khách, nhân viên quá tải, giấy tờ ngập bàn, điện thoại reo không ai nghe, kho hàng tồn |
| `giai-phap` Đang làm việc, đang phục vụ | 20 | tư vấn cho khách, cùng xem điện thoại, giao hàng tận nơi, họp nhóm nhỏ, chuẩn bị đơn |
| `ket-qua` Kết quả, khách vui | 20 | khách cười nhận hàng, cửa hàng đông, nhóm ăn mừng, bắt tay chốt việc, khách quay lại |
| `con-nguoi` Chân dung người làm nghề | 20 | nam, nữ, 25–55 tuổi, nhìn máy ảnh tự tin, đủ kiểu nghề (bán hàng, văn phòng, thợ, đầu bếp) |
| `boi-canh` Đời sống Việt | 20 | phố, chợ, quán cà phê, văn phòng nhỏ, gia đình, nhà mới, Tết |
| `khai-niem` 3D ý trừu tượng | 20 | mũi tên tăng, khiên an toàn, đồng hồ, lịch hẹn, hộp quà, giỏ hàng, tim, ngôi sao |

**Lớp ngành, 6 ngành đông học viên trước × 15 ảnh (90 ảnh):** spa và làm đẹp; ăn uống và cà phê; giáo dục và coaching; bất động sản; bảo hiểm và tài chính; bán online và thời trang. Mỗi ngành chia đủ 5 nhịp: 3 nỗi đau, 3 đang làm, 3 kết quả, 3 bối cảnh nghề, 3 chân dung.

### Đợt 2: khoảng 75 ảnh

5 ngành sau × 15: nha khoa và phòng khám; nội thất và xây dựng; du lịch và khách sạn; thực phẩm sạch; dịch vụ gia đình. Thứ tự lấy theo danh sách ngành học viên thật của lớp.

## 4. Cách làm

1. **Claude soạn bộ câu lệnh** cho cả 210 ảnh vào một bảng (`ma`, `nhom`, `nganh`, câu lệnh tạo ảnh, ý dùng). Luật chung ở mục 2 nằm sẵn trong từng câu. Founder duyệt 10 câu mẫu trước.
2. **Tạo ảnh**, hai cách (Founder chọn):
   - (a) Founder dán từng câu vào AI Studio như ảnh mẫu. Chủ động chọn ảnh đẹp nhưng tốn công: 210 lần dán.
   - (b) Claude chạy cả bộ bằng một tệp lệnh qua khóa Google Vertex (loại khóa skill ảnh bìa đang dùng). Khóa nằm trong két, chạy qua `secrets run`, Founder cho phép một lần; nếu két chưa có khóa này thì Founder tạo và thêm vào két trước. Mỗi câu tạo 2 ảnh để chọn. Founder chỉ duyệt kết quả. Phí theo bảng giá Google tại lúc làm; Claude báo số ảnh và ước phí trước khi chạy.
3. **Soát và gắn nhãn bằng mắt** như kho cảnh: tác tử con xem từng ảnh, loại ảnh lỗi (tay, mặt, chữ lạ), điền nhãn: `mo_ta`, `tu_khoa`, `nhom`, `nhip`, `nganh`, `co_nguoi`, `phong_cach` (chup/3d/nen), `cho_chu`, `mau`. Một tác tử khác soát chéo 10%; Founder xem 20 ảnh mẫu.
4. **Nhập kho** loại `anh` (mã `AN0001`…, đã có chỗ trong `QUY_CHUAN_MO_RONG.md`), đóng vào gói cùng đợt cảnh, cả gói nhẹ.
5. **Sửa máy chọn cảnh**, thứ tự ưu tiên: ảnh, video của chính học viên → cảnh video khớp ngành, khớp nhịp → **ảnh kho khớp ngành, khớp nhịp** → nền dịu tự tạo. Ảnh thành clip 8 giây phóng chậm hoặc lia nhẹ.
6. **Công cụ học viên tự thêm ảnh** (như `them_am.py` của nhạc, tiếng): "thêm 10 ảnh cửa hàng của tôi vào kho", máy tự gắn nhãn, đặt tên, cho xem trước rồi mới ghi.

## 5. Một rào cần có ngay từ đầu

Người trong ảnh AI **không phải khách thật**. Ảnh nhóm `ket-qua`, `con-nguoi` chỉ dùng làm minh họa không khí, không đặt ở chỗ người xem hiểu là "đây là khách của tôi" hay "đây là tôi". Nhịp "vì sao tin" và "tôi là ai" của BNI ưu tiên ảnh thật của học viên. Chỉ mục ghi `ai_tao=co` để máy và người chấm biết. Các nền tảng đăng video cũng yêu cầu bật nhãn nội dung AI (đã có trong luật 10 của skill).

## 6. Video minh họa về sau

Khi có thời gian, lấy ảnh đẹp nhất mỗi nhóm làm ảnh gốc để tạo video:
- 5–8 giây, dọc 9:16, **một hành động đơn giản**: người gật đầu, rót cà phê, đưa hàng. Máy quay chuyển động chậm.
- Không có lời, không có chữ. Tiếng nền tắt (xưởng tự lồng nhạc, tiếng).
- Cùng mã nhóm với ảnh gốc, nên máy dùng được ngay. Video thay ảnh ở chỗ cần chuyển động, ảnh vẫn giữ làm dự phòng.
- Thứ tự: 20 ảnh `giai-phap` và `ket-qua` của lớp chung trước (dùng nhiều nhất), rồi tới ngành.

## 7. Thước đo

- Thử 3 học viên giả ở 3 ngành khác nhau: ít nhất 9/10 cảnh trong video khớp lời đang nói (thước đo 8 của MUC_TIEU).
- Không cảnh nào lặp lại trong cùng một video 30 giây.
- Ảnh lỗi (tay, mặt, chữ lạ) lọt vào kho: 0.
