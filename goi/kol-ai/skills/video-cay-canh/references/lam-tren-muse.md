# Làm trên Muse (muse.ai) qua Claude in Chrome

Muse không có API cho tài khoản thường. Claude điều khiển trang muse.ai bằng tiện ích **Claude in Chrome** trên trình duyệt đã đăng nhập Muse. Mọi thao tác dưới đây đã chạy thật ngày 20/11/2026.

## Giới hạn đã đo

| Mục | Con số |
|---|---|
| Ảnh mỗi lượt | **Tối đa 4.** Gửi 5 thì Muse làm 4 rồi báo cảnh thứ 5 phải gửi lượt sau |
| Video mỗi lượt | 4 làm được, khoảng 2–3 phút |
| Chạy song song | Mở 3 đoạn chat phụ cùng lúc được, 10 clip xong trong khoảng 3 phút |
| Ảnh ra | 1152×2048, định dạng webp |
| Clip ra | 704×1248 hoặc 720×1280, 10 giây, 24 khung/giây. Tiếng nền rất nhỏ (−31 đến −45 LUFS), coi như không có |
| Tật quen | Máy thường đi sâu hơn lệnh; khoảng 1/5 clip **tự nhảy sang góc khác** giữa chừng (`kiem_clip.py` bắt được) |

## Lỗi đã gặp và cách xử lý

| Lỗi | Nghĩa | Làm gì |
|---|---|---|
| "Video generation isn't available in your country or region" | **Tài khoản** bị Meta xếp vào vùng chưa mở. Không phải do IP: tài khoản khác trên cùng mạng vẫn tạo được | Không gửi lại. Chuyển sang tài khoản Muse dự phòng. Tài khoản bị chặn vẫn tạo ảnh được, dùng nó làm ảnh |
| Trang trắng "AsyncSocketException… Connection reset" | Mất kết nối | Tải lại trang, đoạn chat vẫn còn |
| Ô nhập không tìm thấy (`textarea` null) | Trang chưa tải xong hoặc đang mở khung xem ảnh | Đợi 3 giây, bấm nút `[aria-label="Đóng"]` rồi thử lại |
| Tab treo, lệnh JS không trả về | Cửa sổ Muse bị che hoặc thu nhỏ | Nhờ người dùng đưa cửa sổ Muse lên trước |

## Các bước

**0. Chọn đúng trình duyệt.** `list_connected_browsers` → chọn trình duyệt có tab muse.ai đã đăng nhập (không chắc thì mở thử từng cái, hỏi người dùng); mở `https://muse.ai` và kiểm đã đăng nhập (có ô "Nhắn tin").

**1. Mở đoạn chat phụ mới** (mỗi lượt một đoạn chat để chạy song song):
```js
[...document.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Đoạn chat phụ mới')?.click();
```

**2. Gửi lệnh** (nội dung lấy từ `lenh/anh-N.txt` hoặc `lenh/video-N.txt`):
```js
const ta=document.querySelector('textarea');
Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(ta, NOI_DUNG);
ta.dispatchEvent(new Event('input',{bubbles:true}));
await new Promise(r=>setTimeout(r,800));
document.querySelector('button[aria-label="Gửi"]').click();
```
Mỗi lần gọi JS chỉ chờ tối đa 40 giây, chờ lâu hơn thì gọi nhiều lần.

**3. Đính kèm ảnh khi tạo video:** dùng `find` tìm phần tử `file-input`, rồi `file_upload` với đường dẫn ảnh trong `<du_an>/anh/` (tối đa 4 ảnh, dưới 10 MB mỗi lần). Đợi 4 giây cho ảnh tải lên rồi mới gửi lệnh. Ảnh phải nằm trong thư mục Claude được phép đọc.

**4. Tải ảnh về.** Ảnh nằm trong nút `[aria-label^="Mở hình ảnh đã tạo"]`. Ảnh nhỏ 498px là ảnh xem trước; bấm mở để tải bản to, lấy `img` có `naturalWidth ≥ 1000` và **src mới** (không trùng ảnh đã có, nếu không sẽ tải nhầm một ảnh nhiều lần):
```js
const out=[];
for (const b of [...document.querySelectorAll('[aria-label^="Mở hình ảnh đã tạo"]')]) {
  const ten=b.getAttribute('aria-label').replace('Mở hình ảnh đã tạo ','').trim();
  const known=new Set([...document.querySelectorAll('img')].filter(x=>x.naturalWidth>=1000).map(x=>x.src));
  let im=b.querySelector('img');
  if(!im||im.naturalWidth<1000){ b.click(); im=null;
    for(let k=0;k<30&&!im;k++){await new Promise(r=>setTimeout(r,500));
      im=[...document.querySelectorAll('img')].find(x=>x.naturalWidth>=1000&&!known.has(x.src));}
    document.querySelector('[aria-label="Đóng"]')?.click(); await new Promise(r=>setTimeout(r,800)); }
  if(!im){out.push(ten+' KHONG');continue;}
  const bl=await (await fetch(im.src)).blob(); const a=document.createElement('a');
  a.href=URL.createObjectURL(bl); a.download=ten+'.webp'; document.body.appendChild(a); a.click(); a.remove();
  out.push(ten+' '+im.naturalWidth); await new Promise(r=>setTimeout(r,400));
}
JSON.stringify(out)
```
Sau đó chạy `python scripts/gom_file.py <du_an> anh`.

**5. Tải clip về.** Lấy `<video>` có `videoHeight ≥ 1000` (bỏ video 480×480 là ảnh đại diện Muse), tải bằng blob, đặt tên tạm theo lượt (`lo1-1.mp4`…). Tên không quan trọng vì `gom_file.py <du_an> clip --mau "lo*.mp4"` tự so khung đầu với ảnh để biết clip nào của cảnh nào.

**6. Dọn thư mục tải về** sau mỗi lô (xóa `lo*.mp4` cũ) để lô sau không gom nhầm.

## Không làm
- Không bấm "Luôn cho phép", "Kết nối", hay chấp thuận quyền thay người dùng. Đó là việc cấp quyền, người dùng tự bấm.
- Không đọc tin nhắn riêng, thư hay dữ liệu khác của người dùng trên trình duyệt.
