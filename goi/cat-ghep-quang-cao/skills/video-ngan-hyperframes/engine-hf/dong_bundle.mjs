// Đóng bundle cho bản HyperFrames: node dong_bundle.mjs <thư mục ra>
// Đọc src/ (chép từ engine Remotion của skill, kèm kenh.json), thay gói remotion bằng shim/.
import {build} from 'esbuild';
import {readFileSync, writeFileSync, mkdirSync, copyFileSync} from 'node:fs';
import {join, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

const goc = dirname(fileURLToPath(import.meta.url));
const ra = process.argv[2];
mkdirSync(join(ra, 'fonts'), {recursive: true});
await build({
  entryPoints: [join(goc, 'shim', 'vao.tsx')], bundle: true, outfile: join(ra, 'app.js'), format: 'iife', minify: true,
  jsx: 'automatic', loader: {'.json': 'json'}, define: {'process.env.NODE_ENV': '"production"'}, logLevel: 'error',
  alias: {remotion: join(goc, 'shim', 'remotion.tsx'), '@remotion/google-fonts/BeVietnamPro': join(goc, 'shim', 'font-be-vietnam.ts'), '@remotion/google-fonts/Montserrat': join(goc, 'shim', 'font-montserrat.ts')},
  nodePaths: [join(goc, 'node_modules')],
});
// Font: Be Vietnam Pro 400–900 thường, Montserrat 900 thường và nghiêng, đủ bộ chữ tiếng Việt
const css = [];
const lay = (goi, ten) => {
  const thu = join(goc, 'node_modules', '@fontsource', goi);
  let s = readFileSync(join(thu, ten), 'utf8');
  for (const m of s.matchAll(/url\(\.\/files\/([^)]+)\)/g)) if (m[1].endsWith('.woff2')) copyFileSync(join(thu, 'files', m[1]), join(ra, 'fonts', m[1]));
  s = s.replace(/url\(\.\/files\/([^)]+\.woff2)\) format\('woff2'\), url\([^)]+\) format\('woff'\)/g, "url(fonts/$1) format('woff2')").replace(/font-display: swap/g, 'font-display: block');
  css.push(s);
};
for (const w of [400, 500, 600, 700, 800, 900]) lay('be-vietnam-pro', `${w}.css`);
lay('montserrat', '900.css');
lay('montserrat', '900-italic.css');
writeFileSync(join(ra, 'fonts.css'), css.join('\n'));
console.log('bundle xong:', ra);
