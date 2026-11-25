// Quay một trang HTML hoạt hình thành video, dựng TỪNG KHUNG (không giật) qua Chrome headless + ffmpeg.
// Trang phải có: window.ve(t) (vẽ trạng thái tại giây t, trả Promise hoặc không) và window.SAN_SANG = true khi sẵn sàng.
// node quay-html.mjs --trang hook.html --out hook.mov --dur 6.6 [--w 3840 --h 2160 --fps 60] [--alpha]  [--anh 1,3,5 (chỉ chụp ảnh)]
//   --alpha: nền trong suốt → ProRes 4444 .mov (dùng làm lớp phủ trong CapCut); không có → H.264 .mp4
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { pathToFileURL } from 'node:url';
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const co = k => process.argv.includes('--' + k);
const W = +arg('w', 3840), H = +arg('h', 2160), FPS = +arg('fps', 60), DUR = +arg('dur', 6), OUT = arg('out', 'out.mov'), ALPHA = co('alpha');
const ANH = arg('anh') ? arg('anh').split(',').map(Number) : null;
const TRANG = pathToFileURL(path.resolve(arg('trang'))).href;  // v3: đúng cả ổ đĩa Windows và tên có dấu
const CHROME_MAC = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', CHROME_WIN = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const CHROME = process.env.CHROME || (process.platform === 'win32' ? CHROME_WIN : CHROME_MAC), PORT = 9400 + Math.floor(Math.random() * 500);
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'quayhtml-'));
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${tmp}`, `--window-size=${W},${H}`,
  '--hide-scrollbars', '--force-device-scale-factor=1', '--mute-audio', 'about:blank'], { stdio: 'ignore' });
process.on('exit', () => { try { chrome.kill('SIGKILL'); } catch {} });
for (const s of ['SIGINT', 'SIGTERM', 'SIGPIPE']) process.on(s, () => process.exit(1));
const ngu = ms => new Promise(r => setTimeout(r, ms));
let ws, id = 0; const cho = new Map();
const goi = (method, params = {}) => new Promise((res, rej) => { const i = ++id; cho.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
let tg; for (let k = 0; k < 60 && !tg; k++) { await ngu(200); try { tg = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find(t => t.type === 'page'); } catch {} }
ws = new WebSocket(tg.webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && cho.has(m.id)) { const c = cho.get(m.id); cho.delete(m.id); m.error ? c.rej(new Error(m.error.message)) : c.res(m.result); } };
await goi('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
if (ALPHA) await goi('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } });
await goi('Page.enable'); await goi('Runtime.enable');
await goi('Page.navigate', { url: TRANG });
const ev = async e => (await goi('Runtime.evaluate', { expression: e, awaitPromise: true, returnByValue: true })).result.value;
for (let k = 0; k < 150 && !(await ev('!!window.SAN_SANG')); k++) await ngu(200);
await ev('document.fonts.ready.then(()=>1)');
const fmt = ALPHA ? 'png' : 'jpeg';
const khung = async t => { await ev(`Promise.resolve(window.ve(${t})).then(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => requestAnimationFrame(() => setTimeout(r, 0))))))`);
  return Buffer.from((await goi('Page.captureScreenshot', { format: fmt, quality: fmt === 'jpeg' ? 93 : undefined })).data, 'base64'); };
if (ANH) { for (const t of ANH) { const f = OUT.replace(/\.(mov|mp4)$/, '') + `-t${t}.${fmt === 'png' ? 'png' : 'jpg'}`; fs.writeFileSync(f, await khung(t)); console.log('ảnh', f); } process.exit(0); }
const vArgs = ALPHA ? ['-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', '-vendor', 'apl0']
                    : ['-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart'];
const ff = spawn(process.env.FFMPEG || 'ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', ALPHA ? 'png' : 'mjpeg', '-framerate', String(FPS), '-i', '-', ...vArgs, OUT], { stdio: ['pipe', 'inherit', 'inherit'] });
const n = Math.round(DUR * FPS), t0 = Date.now();
for (let i = 0; i < n; i++) { const b = await khung(i / FPS); if (!ff.stdin.write(b)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 60 === 0) process.stdout.write(`\r${i}/${n} khung · ${((Date.now() - t0) / 1000).toFixed(0)}s`); }
ff.stdin.end(); await new Promise(r => ff.on('close', r));
console.log(`\nXong: ${OUT}`); process.exit(0);
