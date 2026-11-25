# Đoạn mã chạy trên trang muse.ai (Claude in Chrome → javascript_tool)

## Soi 6 khung một clip ngay trên trang (trước khi tải)
```js
window.soiClip = async (ten, ts) => {
  document.getElementById('soi-tam')?.remove();
  const btn = [...document.querySelectorAll('[aria-label]')].find(e => e.getAttribute('aria-label') === 'Mở video có hoạt ảnh ' + ten);
  btn.scrollIntoView(); await new Promise(r => setTimeout(r, 1500));
  const v0 = btn.querySelector('video') || btn.parentElement.querySelector('video') || btn.closest('div').parentElement.querySelector('video');
  const v = document.createElement('video'); v.src = v0.currentSrc || v0.src; v.muted = true; await new Promise(r => v.onloadeddata = r);
  const c = document.createElement('canvas'); c.width = ts.length * 240; c.height = 427; const g = c.getContext('2d');
  for (let i = 0; i < ts.length; i++) { v.currentTime = ts[i]; await new Promise(r => v.onseeked = r); g.drawImage(v, i * 240, 0, 240, 427); g.fillStyle = 'yellow'; g.fillText(ts[i], i * 240 + 4, 12); }
  c.id = 'soi-tam'; c.style = 'position:fixed;top:0;left:0;z-index:99999;border:2px solid red'; document.body.appendChild(c);
};
await window.soiClip('b1-tien.mp4', [0.5, 3, 5, 6.5, 8, 9.6])
```
Rồi `computer zoom` vùng [0,0,1444,430]. Xong gỡ: `document.getElementById('soi-tam')?.remove()`.

## Gộp nhiều clip thành MỘT gói rồi tải (mỗi thẻ chỉ tải được 1 tệp)
```js
const ten = ['b1-tien.mp4', 'b1-chan.mp4']; const phan = []; const dau = [];
for (const t of ten) {
  const btn = [...document.querySelectorAll('[aria-label]')].find(e => e.getAttribute('aria-label') === 'Mở video có hoạt ảnh ' + t);
  btn.scrollIntoView(); await new Promise(r => setTimeout(r, 1500));
  const v = btn.querySelector('video') || btn.parentElement.querySelector('video') || btn.closest('div').parentElement.querySelector('video');
  const b = await (await fetch(v.currentSrc || v.src)).arrayBuffer(); phan.push(new Uint8Array(b)); dau.push([t, b.byteLength]);
}
const js = new TextEncoder().encode(JSON.stringify(dau)); const n = new Uint8Array(4); new DataView(n.buffer).setUint32(0, js.length, false);
const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([n, js, ...phan])); a.download = 'goi-muse-' + Date.now() + '.bin'  /* nhiều chat cùng dùng Muse thì thêm tiền tố riêng, ví dụ 'lb-goi-muse-'; khi đó chạy tach_goi_muse.py với đường dẫn gói cụ thể (script chỉ tự tìm goi-muse-*.bin) */; document.body.appendChild(a); a.click();
```
Trên máy: `python scripts/tach_goi_muse.py clip` (tự lấy các gói `goi-muse-*.bin` trong `thu_muc_tai_ve` của cau-hinh.json). Gói hết clip của video trong MỘT lần tải (thẻ đã tải rồi thì mở thẻ mới).

## (Ưu tiên) Gom clip khi khung chat đã trôi — cuộn ngược tự nạp, giữ trong window.kho rồi tải MỘT gói
Khung chat Muse chỉ giữ vài video gần nhất trong trang; clip cũ "không thấy nút" cho tới khi cuộn lên.
```js
window.kho = window.kho || {};
const can = ['b1-tien.mp4','b2-tien.mp4','b3-tien.mp4','b1-chan.mp4','b2-chan.mp4','b3-chan.mp4'];
const lay = async () => { for (const t of can) { if (window.kho[t]) continue;
  const btn = [...document.querySelectorAll('[aria-label]')].find(e => e.getAttribute('aria-label') === 'Mở video có hoạt ảnh ' + t); if (!btn) continue;
  btn.scrollIntoView(); await new Promise(r => setTimeout(r, 1200));
  const v = btn.querySelector('video') || btn.parentElement.querySelector('video') || btn.closest('div').parentElement.querySelector('video');
  if (!v || !(v.currentSrc || v.src)) continue;
  window.kho[t] = new Uint8Array(await (await fetch(v.currentSrc || v.src)).arrayBuffer()); } };
const log = document.querySelector('[role="log"]'); let el = log; while (el && el.scrollHeight <= el.clientHeight) el = el.parentElement;
await lay();
for (let i = 0; i < 40 && can.some(t => !window.kho[t]); i++) { el.scrollTop -= 600; await new Promise(r => setTimeout(r, 900)); await lay(); }
JSON.stringify(can.map(t => [t, window.kho[t]?.length || 0]))   // đủ hết > 0 rồi mới tải:
// const dau = can.map(t => [t, window.kho[t].length]); ... new Blob([n, js, ...can.map(t => window.kho[t])]) ... a.click()
```

## Tải ẢNH gốc (khung chat chỉ có bản thu nhỏ 498×664; bản gốc 1344×1792 / 1152×2048 nằm trong trình xem ảnh)
Ảnh đặt tên trong lệnh ("đặt tên toan-b1.png") thì nút trên trang là "Mở hình ảnh đã tạo toan-b1.png".
```js
window.kho = window.kho || {};
window.layAnh = async (ds) => { for (const t of ds) { if (window.kho[t]) continue;
  document.querySelector('[aria-label="Đóng"]')?.click(); await new Promise(r=>setTimeout(r,800));
  const b = document.querySelector('[aria-label="Mở hình ảnh đã tạo ' + t + '"]'); if (!b) continue;
  const cu = new Set([...document.querySelectorAll('img')].map(x=>x.currentSrc||x.src));   // ảnh lớn đã có sẵn trong trang
  b.scrollIntoView(); b.click(); let im = null;
  for (let i=0;i<20 && !im;i++){ await new Promise(r=>setTimeout(r,500)); im = [...document.querySelectorAll('img')].find(x=>x.naturalWidth>1000 && !cu.has(x.currentSrc||x.src)); }
  // CHỈ lấy ảnh MỚI hiện ra sau khi bấm: bản cũ lấy "ảnh lớn đầu tiên" từng lấy nhầm một ảnh cũ (23/11). Tải về luôn so mặt/cỡ tệp.
  if (im) window.kho[t] = new Uint8Array(await (await fetch(im.currentSrc||im.src)).arrayBuffer());
  document.querySelector('[aria-label="Đóng"]')?.click(); await new Promise(r=>setTimeout(r,800)); } };
window.taiGoi = (ds) => { const dau = ds.map(t=>[t, window.kho[t].length]); const js = new TextEncoder().encode(JSON.stringify(dau)); const n = new Uint8Array(4); new DataView(n.buffer).setUint32(0, js.length, false);
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([n, js, ...ds.map(t=>window.kho[t])])); a.download = 'goi-muse-' + Date.now() + '.bin'  /* nhiều chat cùng dùng Muse thì thêm tiền tố riêng, ví dụ 'lb-goi-muse-'; khi đó chạy tach_goi_muse.py với đường dẫn gói cụ thể (script chỉ tự tìm goi-muse-*.bin) */; document.body.appendChild(a); a.click(); return dau; };
await window.layAnh(['toan-b1.png','toan-b2.png','toan-b3.png']);   // ảnh nào trả 0 là đã trôi khỏi trang: cuộn khung chat lên rồi gọi lại; ĐỦ hết > 0 rồi mới gọi taiGoi (thiếu ảnh nào taiGoi sẽ lỗi)
window.taiGoi(['toan-b1.png','toan-b2.png','toan-b3.png'])
```
Trên máy: `python scripts/tach_goi_muse.py <thư mục> <gói>` (tách được cả ảnh lẫn video). Gói video ~20 MB cần vài giây mới tải xong: kiểm cỡ tệp trước khi tách.

## Chờ một clip xong mà không treo lệnh
Một lệnh javascript chỉ được chạy tối đa khoảng 45 giây; chờ lâu hơn thì gọi lại nhiều lần:
```js
window.cho = async (t, s=38) => { for(let i=0;i<s/5;i++){ if(document.querySelector('[aria-label="Mở video có hoạt ảnh '+t+'"]')) return 'CO '+t; await new Promise(r=>setTimeout(r,5000)); } return 'CHUA '+t; };
await window.cho('b1-tien.mp4')   // 'CHUA' thì gọi lại; clip thường xong sau 40–90 giây
```
Đừng gộp quá nhiều bước (3 clip + chờ) vào một lượt thao tác trình duyệt: lượt dài bị ngắt giữa chừng. Mỗi lượt một clip: đính ảnh → gửi lệnh → chờ → soi.

## Gửi tin bằng mã (khi phím Enter không gửi)
Cửa sổ trình duyệt không có tiêu điểm thì phím Enter có thể không gửi: chữ nằm lại trong ô hoặc tin rơi mất. Gửi bằng nút "Gửi" và kiểm tin đã vào khung chat:
```js
const ta = document.querySelector('textarea[aria-label="Nhắn tin"]');   // ô nhắn tin là textarea
// (gõ chữ bằng computer type, hoặc gán: ta.focus(); document.execCommand('insertText', false, '<lệnh>'))
document.querySelector('button[aria-label="Gửi"]').click();
await new Promise(r => setTimeout(r, 4000));
document.querySelector('[role="log"]').innerText.includes('<tên tệp trong lệnh>') ? 'ĐÃ VÀO' : 'CHƯA VÀO — gửi lại'
```
