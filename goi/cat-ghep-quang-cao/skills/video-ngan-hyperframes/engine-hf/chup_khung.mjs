// Chụp khung soát của trang HyperFrames bằng Chrome headless, trước khi render (không cần HyperFrames CLI).
// node chup_khung.mjs <index.html> <props.json> <thư mục ra> <chrome.exe>
// Mỗi cảnh một ảnh ở mốc 92% thời lượng cảnh, cùng mốc với anh_tinh.cjs của bản Remotion để so được với nhau.
// Video trong ảnh soát do trình duyệt tự tua nên có thể lệch vài khung; bản render thật do HyperFrames lấy khung bằng FFmpeg.
import puppeteer from 'puppeteer-core';
import {readFileSync, mkdirSync} from 'node:fs';
import {pathToFileURL} from 'node:url';

const [trang, props, ra, chrome] = process.argv.slice(2);
const p = JSON.parse(readFileSync(props, 'utf8'));
mkdirSync(ra, {recursive: true});
const b = await puppeteer.launch({executablePath: chrome, headless: true, args: ['--allow-file-access-from-files', '--autoplay-policy=no-user-gesture-required']});
try {
  const tr = await b.newPage();
  const loi = [];
  tr.on('pageerror', (e) => loi.push(String(e)));
  await tr.setViewport({width: 1080, height: 1920});
  await tr.goto(/^https?:/.test(trang) ? trang : pathToFileURL(trang).href, {waitUntil: 'networkidle0'});
  await tr.evaluate(() => document.fonts.ready);
  if (loi.length) throw new Error('Trang lỗi: ' + loi.join(' | '));
  for (const [i, c] of p.canh.entries()) {
    const t = Math.round((c.tu + (c.den - c.tu) * 0.92) * 30) / 30;
    await tr.evaluate((t) => {
      window.dispatchEvent(new CustomEvent('hf-seek', {detail: {time: t, waitUntil() {}}}));
      for (const v of document.querySelectorAll('video')) {
        const s = +v.dataset.start, d = +v.dataset.duration, trong = t >= s && t < s + d;
        v.style.visibility = trong ? 'visible' : 'hidden';
        if (trong) v.currentTime = t - s + +v.dataset.mediaStart;
      }
    }, t);
    await tr.evaluate(() => Promise.all([...document.querySelectorAll('video')].filter((v) => v.style.visibility === 'visible').map((v) => new Promise((r) => (v.seeking ? v.addEventListener('seeked', r, {once: true}) : r())))));
    await tr.evaluate(() => Promise.all([...document.images].map((im) => im.decode().catch(() => 0))));
    await tr.screenshot({path: `${ra}/${String(i + 1).padStart(2, '0')}.jpg`, type: 'jpeg', quality: 90});
  }
  if (loi.length) throw new Error('Trang lỗi khi tua: ' + loi.join(' | '));
  console.log('chụp xong', p.canh.length, 'cảnh');
} finally {
  await b.close();
}
