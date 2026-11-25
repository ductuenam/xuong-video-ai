// Chụp khung cuối mỗi cảnh từ bundle, dùng chung một trình duyệt nên nhanh hơn gọi "remotion still" từng lần.
// node anh_tinh.cjs <thư mục engine> <bundle> <props.json> <thư mục ra>
const {createRequire} = require('module');
const fs = require('fs');
const path = require('path');
const [engine, bundle, fileProps, ra] = process.argv.slice(2);
const {openBrowser, renderStill, selectComposition} = createRequire(path.join(engine, 'package.json'))('@remotion/renderer');

(async () => {
  const props = JSON.parse(fs.readFileSync(fileProps, 'utf-8'));
  const trinhDuyet = await openBrowser('chrome');
  try {
    const comp = await selectComposition({serveUrl: bundle, id: 'MoHinh', inputProps: props, puppeteerInstance: trinhDuyet, logLevel: 'error'});
    fs.mkdirSync(ra, {recursive: true});
    for (const [i, c] of props.canh.entries()) {
      // 92% cảnh: các thẻ đã hiện đủ theo mốc, phụ đề vẫn còn
      const frame = Math.min(comp.durationInFrames - 1, Math.round((c.tu + (c.den - c.tu) * 0.92) * comp.fps));
      await renderStill({composition: comp, serveUrl: bundle, inputProps: props, frame, output: path.join(ra, `${String(i + 1).padStart(2, '0')}.jpg`), imageFormat: 'jpeg', jpegQuality: 90, scale: 0.4, puppeteerInstance: trinhDuyet, logLevel: 'error'});
    }
  } finally {
    await trinhDuyet.close({silent: true});
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
