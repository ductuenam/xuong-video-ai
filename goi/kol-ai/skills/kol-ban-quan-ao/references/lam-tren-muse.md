# Làm trên Muse (muse.ai) qua Claude in Chrome

Muse không có API cho tài khoản thường. Claude điều khiển trang muse.ai bằng tiện ích **Claude in Chrome** trên trình duyệt anh chị đã đăng nhập Muse. Mọi thao tác dưới đây đã chạy thật khi làm 5 video mẫu.

## Giới hạn đã đo

| Mục | Con số |
|---|---|
| Video mỗi tin | 3 cảnh nói khoảng 2–3 phút; 2 cảnh cận khoảng 2 phút |
| Ảnh mỗi tin | Tối đa 4 ảnh |
| Chạy song song | 2 video cùng lúc (4 đoạn chat) chạy ổn |
| Ảnh ra | khoảng 1152×2048, định dạng webp |
| Clip ra | 720×1280, 10 giây, 24 khung/giây, có giọng nói |
| Tốc độ nói | 4,6–4,9 chữ/giây; lời 44 chữ kết thúc quanh giây 9,3–9,8 |

## Lỗi đã gặp và cách xử lý

| Lỗi | Nghĩa | Làm gì |
|---|---|---|
| "Video generation isn't available in your country or region" (Không tạo được video ở quốc gia/khu vực của bạn) | Tài khoản bị xếp vào vùng chưa mở tạo video (không phải do mạng) | Không gửi lại. Chuyển sang tài khoản Muse dự phòng. Tài khoản bị chặn vẫn tạo ảnh được |
| Một video trong lô báo "lỗi nội bộ" | Muse lỗi riêng video đó | Nhắn ngay trong đoạn chat đó: "Tạo lại VIDEO n đúng y như lệnh trên… Chỉ tạo 1 video này" (mất thêm khoảng 2 phút) |
| Báo đã hết lượt trong 24 giờ | Hạn mức tài khoản | Dừng, báo người dùng; dùng tài khoản dự phòng hoặc chờ |
| Trang trắng "Connection reset" | Mất kết nối | Tải lại trang, đoạn chat vẫn còn. Đọc lại trang trước, không gửi lại để tránh tạo trùng |
| Ô nhập không tìm thấy | Trang chưa tải xong hoặc đang mở khung xem ảnh | Đợi 3 giây, bấm `[aria-label="Đóng"]` rồi thử lại |
| Lệnh JS không trả về | Cửa sổ Muse bị che hoặc thu nhỏ | Nhờ người dùng đưa cửa sổ Muse lên trước |

## Các bước

**0. Chọn đúng trình duyệt.** `list_connected_browsers` → `select_browser` → mở `https://muse.ai`, kiểm đã đăng nhập (có ô "Nhắn tin"). Không đăng nhập thay người dùng.

**1. Mở đoạn chat mới** cho mỗi tin (để chạy song song và để Muse không lẫn ảnh của tin trước): mở `https://muse.ai/thread/new`, hoặc:
```js
[...document.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Đoạn chat phụ mới')?.click();
```

**2. Đính ảnh.** Gán nhãn cho ô chọn tệp rồi dùng `find` lấy ref và `file_upload` (không bấm nút đính kèm, vì sẽ mở hộp chọn tệp của Windows):
```js
document.querySelector('input[type=file]').setAttribute('aria-label','o-tai-anh'); 'ok'
```
Đính đúng thứ tự ghi trong lệnh (ảnh 1 trước, ảnh 2 sau). Một lần `file_upload` đính được nhiều ảnh (tổng dưới 10 MB). Đợi 4 giây cho ảnh tải lên rồi mới gửi.
`file_upload` chỉ nhận tệp nằm trong thư mục Claude Code đang mở (hoặc thư mục đã thêm vào phiên). Báo lỗi "only files this session is allowed to read" thì đặt `thu_muc_lam_viec` và `thu_muc_kol` bên trong thư mục đang mở, hoặc nhờ người dùng thêm thư mục đó vào phiên.

**3. Gửi lệnh** (nội dung lấy từ `tin1.txt`, `tin2.txt`, `lenh-anh.txt`, `lenh-kol.txt`; lệnh luôn viết một dòng vì Enter là gửi):
```js
const ta=document.querySelector('textarea');
Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(ta, NOI_DUNG);
ta.dispatchEvent(new Event('input',{bubbles:true}));
await new Promise(r=>setTimeout(r,800));
document.querySelector('button[aria-label="Gửi"]').click();
```
Hoặc bấm vào ô "Nhắn tin", gõ nội dung rồi nhấn Enter. Mỗi lần gọi JS chỉ chờ tối đa 40 giây, chờ lâu hơn thì gọi nhiều lần.

**4. Tải ảnh về.** Ảnh nằm trong nút `[aria-label^="Mở hình ảnh đã tạo"]`. Ảnh nhỏ là ảnh xem trước; bấm mở để lấy bản to (`naturalWidth ≥ 1000`) và chỉ lấy **src mới**:
```js
const out=[]; const TIEN_TO='vNN-anh';
let i=0;
for (const b of [...document.querySelectorAll('[aria-label^="Mở hình ảnh đã tạo"]')]) {
  const known=new Set([...document.querySelectorAll('img')].filter(x=>x.naturalWidth>=1000).map(x=>x.src));
  let im=b.querySelector('img');
  if(!im||im.naturalWidth<1000){ b.click(); im=null;
    for(let k=0;k<30&&!im;k++){await new Promise(r=>setTimeout(r,500));
      im=[...document.querySelectorAll('img')].find(x=>x.naturalWidth>=1000&&!known.has(x.src));}
    document.querySelector('[aria-label="Đóng"]')?.click(); await new Promise(r=>setTimeout(r,800)); }
  if(!im){out.push('KHONG');continue;}
  i++; const bl=await (await fetch(im.src)).blob(); const a=document.createElement('a');
  a.href=URL.createObjectURL(bl); a.download=`${TIEN_TO}${i}.webp`; document.body.appendChild(a); a.click(); a.remove();
  out.push(i+' '+im.naturalWidth); await new Promise(r=>setTimeout(r,400));
}
JSON.stringify(out)
```

**5. Tải clip về theo nhãn tên tệp.** Lệnh mẫu đã dặn Muse đặt tên (`s1-noi.mp4`, `q4-can-tren.mp4`…). Nhãn có thể có dạng `media-generation-s1-noi-0-…`, nên lọc bằng biểu thức, không đòi đuôi `.mp4`:
```js
const TIEN_TO='vNN-'; const out=[];
for (const v of [...document.querySelectorAll('video')].filter(v=>v.videoHeight>=1000)) {
  let e=v, nhan=''; for(let k=0;k<8&&e&&!nhan;k++){ nhan=(e.getAttribute&&e.getAttribute('aria-label'))||''; e=e.parentElement; }
  const m=nhan.match(/(s\d-(noi|xoay)|q\d-can-[a-z]+)/); if(!m){out.push('khong nhan: '+nhan.slice(0,40));continue;}
  const b=await (await fetch(v.currentSrc)).blob(); const a=document.createElement('a');
  a.href=URL.createObjectURL(b); a.download=TIEN_TO+m[1]+'.mp4'; document.body.appendChild(a); a.click(); a.remove();
  out.push(m[1]+' '+v.videoWidth+'x'+v.videoHeight); await new Promise(r=>setTimeout(r,800));
}
JSON.stringify(out)
```
Tệp về thư mục tải xuống (`thu_muc_tai_ve`). Sau đó `python scripts/soat_lo.py <thư mục video> --tai vNN` tự chuyển vào thư mục video và bỏ tiền tố. Tải ngay khi xong: khung chat chỉ giữ vài video mới nhất.

## Không làm
- Không bấm "Luôn cho phép", "Kết nối", không chấp thuận quyền thay người dùng.
- Không đọc tin nhắn riêng, thư hay dữ liệu khác trên trình duyệt.
- Không tìm cách lách chặn vùng hay bộ lọc của Muse.
