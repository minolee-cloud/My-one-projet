// index.html 을 프레임별로 캡처해 rose-jjondeugi.mp4 로 만든다.
// 사용법: python3 prepare.py && python3 make_audio.py && node render.js   (필요: numpy, pillow, playwright, ffmpeg)
// 테스트: node render.js 1 4.5 6.8 8 13.5 15.5 → 해당 초의 PNG만 frames/ 에 저장
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, T = 24;
const dir = path.join(__dirname, 'frames');

(async () => {
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir);
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 720, height: 1280 } });
  page.on('pageerror', e => { console.error(e); process.exit(1); });
  await page.goto('file://' + path.join(__dirname, 'index.html') + '?capture');
  await page.evaluate(() => window.ready);
  const canvas = page.locator('canvas');
  const times = process.argv.length > 2 ? process.argv.slice(2).map(Number) : [...Array(FPS * T).keys()].map(i => i / FPS);
  for (const [i, t] of times.entries()) {
    await page.evaluate(t => window.renderAt(t), t);
    await canvas.screenshot({ path: path.join(dir, `f${String(i).padStart(4, '0')}.png`) });
  }
  await browser.close();
  if (process.argv.length > 2) return;
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(dir, 'f%04d.png'),
    '-i', path.join(__dirname, 'rose-jjondeugi.wav'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20',
    '-c:a', 'aac', '-b:a', '160k', '-shortest', path.join(__dirname, 'rose-jjondeugi.mp4')]);
  fs.rmSync(dir, { recursive: true, force: true });
  console.log('rose-jjondeugi.mp4 done');
})();
