# Tự kiểm, nhạc và đăng bài

## Tự kiểm (bắt buộc, không giao clip chưa soi)
1. `kiem_clip.py` bắt máy: đứng hình, nhảy cảnh. Có nhảy cảnh thì script tự ghi đoạn giữ vào `du-an.json`; đoạn liền ngắn hơn 6 giây thì tạo lại clip.
2. **Claude mở từng tờ soi `kiem/<ten>.jpg`** (20 khung, cách 0,5 giây) và xem bằng mắt:
   - cây, chậu đổi hình hoặc mọc thêm giữa chừng;
   - cá bơi trên bờ, nước chảy ngược, vật trôi lơ lửng;
   - xuất hiện người, chữ, logo;
   - khung cuối mờ nhòe hoặc lao sâu vào một mảng lá vô nghĩa.
   Lỗi ở cuối clip thì cắt bớt đuôi (sửa `cat` trong `du-an.json`); lỗi ở giữa thì tạo lại clip đó.
3. Sau `dung.py`, xem một tờ soi của thành phẩm để chắc chỗ cắt không còn vết nhảy.

## Nhịp và độ dài
- Làm chậm 0,85 lần (khách thật đã duyệt "chậm hơn một tí xíu là đẹp"); không chậm hơn 0,8 vì nội suy sẽ nhòe.
- Mỗi video 7–12 giây là đủ cho Reels cây cảnh. Muốn video dài hơn thì ghép 2–3 cảnh cùng phong cách bằng hòa tan 0,5 giây (không ghép kiểu cắt phụp).

## Nhạc
- **Nhạc là nửa cảm xúc của video.** Cùng một hình, nhạc sáng vào ngay đoạn hay thì video "đẹp", nhạc tối đục có dạo đầu lững lờ thì video "chán". Nhạc mẫu đi kèm đã cắt sẵn đoạn hay và chọn theo không khí cảnh; `dung.py` báo ✘ khi nhạc của thành phẩm nhạt hơn hẳn chuẩn.
- **Hay nhất khi đăng Facebook/TikTok:** đăng bản `-khong-nhac.mp4`, lúc đăng bấm biểu tượng nốt nhạc, gõ tìm "garden", "relaxing piano", "acoustic chill" hoặc mở mục Thịnh hành, nghe thử vài bài, chọn bài nhẹ mà sáng, kéo tới đoạn điệp khúc (đoạn hay nhất) cho khớp 10–12 giây. Nhạc trong thư viện được nền tảng cấp quyền cho bài đăng đó.
- Nhạc gắn sẵn vào file chỉ dùng nhạc shop có quyền (nhạc mua, nhạc có giấy phép rõ). Bài shop có giấy phép chỉ cho Facebook thì đặt tên `CHI-FACEBOOK-…`; `dung.py` sẽ gắn chữ `CHI-FACEBOOK` vào tên thành phẩm và **chỉ được đăng Facebook**. Kể cả trên Facebook, nhạc gắn sẵn vẫn có thể bị nhận diện và tắt tiếng.

## Caption mẫu
```
<Mô tả cảnh một câu, có tên cây chủ> 🌿
<Một câu về ý đồ thiết kế: cây cao - trung - thấp, chậu cùng bộ…>
<Câu hỏi mời bình luận>. Inbox/Zalo <số> để được tư vấn thiết kế miễn phí.
<3–5 hashtag của shop>
```
Không hứa "cây không bao giờ chết", không nói giá nếu shop chưa đưa.

## Đăng lên Page
**Muse tự đăng — CHƯA CHẠY ĐƯỢC, gói không bao gồm, chỉ thử khi người dùng tự nối và tự yêu cầu:** Muse đăng Reels qua công cụ kết nối **"Trình quản lý kinh doanh trên Meta"** (khác công cụ "Facebook" cá nhân). Lần thử báo `PROFESSIONAL_CONSENT_REQUIRED` và `INVALID_VIEWER_CONTEXT`: chủ Page phải tự bấm **Kết nối** trên thẻ Meta trong đoạn chat Muse, chọn Page; có thể Meta bắt tạo danh mục doanh nghiệp (BM) miễn phí. Mỗi bài Muse vẫn hỏi duyệt riêng. Claude không bấm cấp quyền thay.

**Cách dùng chính — đăng tay (luôn dùng được):** mở Facebook trên điện thoại → Page → Thước phim → chọn video `-khong-nhac.mp4` → chọn nhạc → dán caption → đăng. Khoảng 1 phút một video.

Claude chỉ đăng khi người dùng nói rõ "đăng" cho đúng video đó. Không tự đăng hàng loạt.
