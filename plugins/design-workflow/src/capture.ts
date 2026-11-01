import { access, mkdir, open, readFile, realpath, stat, unlink } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { constants } from 'node:fs';
import { isIP } from 'node:net';
import { extname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import { randomUUID } from 'node:crypto';
import { chromium } from 'playwright-core';
import type { Browser, Page, Request } from 'playwright-core';
import type { BrowserStep, CaptureSpec } from './engine.ts';
import { MAX_CAPTURE_DIMENSION } from './engine.ts';

const TIMEOUT_MS = 30_000;
const MAX_ASSET_BYTES = 16 * 1024 * 1024;
const FILE_ORIGIN = 'http://design-workflow.invalid';
const AXE_SOURCE = createRequire(import.meta.url).resolve('axe-core/axe.min.js');
const CONTENT_TYPES: Record<string, string> = {
  '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8',
  '.svg': 'image/svg+xml', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp',
  '.avif': 'image/avif', '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2',
  '.ttf': 'font/ttf', '.otf': 'font/otf', '.txt': 'text/plain; charset=utf-8',
};

function inside(root: string, path: string): boolean {
  const rel = relative(root, path);
  return rel !== '' && rel !== '..' && !rel.startsWith(`..${sep}`) && !isAbsolute(rel);
}

function loopback(hostname: string): boolean {
  const host = hostname.replace(/^\[|\]$/g, '').toLowerCase();
  return host === 'localhost' || host === '::1' || (isIP(host) === 4 && host.startsWith('127.'));
}

async function browserExecutable(explicit?: string): Promise<string> {
  const selected = explicit ?? process.env.DESIGN_WORKFLOW_CHROME;
  const candidates = selected ? [selected] : [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable', '/opt/google/chrome/chrome',
  ];
  for (const candidate of candidates) {
    try { await access(candidate, constants.X_OK); return candidate; } catch { /* 次の候補を調べる。 */ }
  }
  throw new Error(selected
    ? `Browser dependency unavailable: executable is not accessible: ${selected}`
    : 'Browser dependency unavailable: install Chromium or Chrome, or set DESIGN_WORKFLOW_CHROME to its executable');
}

async function performStep(page: Page, step: BrowserStep): Promise<void> {
  const locator = page.locator(step.selector);
  switch (step.action) {
    case 'click': await locator.click(); break;
    case 'fill': await locator.fill(step.value); break;
    case 'press': await locator.press(step.key); break;
    case 'assert-visible': await locator.waitFor({ state: 'visible' }); break;
    case 'assert-text': {
      await locator.waitFor({ state: 'visible' });
      const text = await locator.textContent();
      if (!text?.includes(step.text)) throw new Error(`Text assertion failed for ${step.selector}: expected ${JSON.stringify(step.text)}`);
      break;
    }
    case 'assert-accessible': {
      // ページの CSP に左右されないよう、script 要素を作らずに axe を評価する。
      await page.evaluate(await readFile(AXE_SOURCE, 'utf8'));
      const violations = await locator.evaluate(async element => {
        // 注入した axe はページの型に現れないため、ここで形を宣言する。
        const { axe } = window as unknown as { axe: { run(context: Element): Promise<{ violations: { id: string; impact: string; nodes: unknown[] }[] }> } };
        const result = await axe.run(element);
        return result.violations.map(v => `${v.id} (${v.impact}, ${v.nodes.length})`);
      });
      if (violations.length) throw new Error(`Accessibility assertion failed for ${step.selector}: ${violations.join('; ')}`);
      break;
    }
    case 'assert-no-overflow': {
      // 文字列ごとに、選択範囲と途中で切り取る祖先の外へ横にはみ出していないかを測る。
      // スクロールできる祖先、効いている省略記号、clip で隠した要素（視覚的に隠したラベル）は除く。
      const overflowing = await locator.evaluate(root => {
        const intentional = (style: CSSStyleDeclaration) => ['auto', 'scroll'].includes(style.overflowX)
          || style.clip !== 'auto' || style.clipPath !== 'none'
          || (style.textOverflow === 'ellipsis' && style.overflowX !== 'visible');
        const outside = (text: DOMRect, element: Element) => {
          const box = element.getBoundingClientRect();
          return text.left < box.left - 0.5 || text.right > box.right + 0.5;
        };
        const found: string[] = [];
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        for (let node = walker.nextNode(); node; node = walker.nextNode()) {
          const content = node.textContent?.trim();
          if (!content) continue;
          const chain: Element[] = [];
          for (let element = node.parentElement; element && element !== root; element = element.parentElement) chain.push(element);
          const styles = chain.map(element => getComputedStyle(element));
          if (styles.some(intentional)) continue;
          const range = document.createRange();
          range.selectNodeContents(node);
          // display:none の内容や style 要素の文字列は描画されないため測らない。
          if (!range.getClientRects().length) continue;
          const text = range.getBoundingClientRect();
          const bounds = [root, ...chain.filter((_, index) => styles[index].overflowX !== 'visible')];
          if (bounds.some(element => outside(text, element))) found.push(content.slice(0, 40));
        }
        return found;
      });
      if (overflowing.length) throw new Error(`Overflow assertion failed for ${step.selector}: ${overflowing.slice(0, 20).join('; ')}`);
      break;
    }
  }
}

export async function captureEvidence(options: {
  workspaceRoot: string; artifactRoot: string; approvedPaths: string[]; spec: CaptureSpec; signal?: AbortSignal; executablePath?: string;
}): Promise<{ artifacts: string[]; details: unknown }> {
  // 1. ブラウザー起動前に対象と承認済みファイルの範囲を確定する。
  const { spec } = options;
  if (!Number.isInteger(spec.width) || !Number.isInteger(spec.height) || spec.width < 1 || spec.height < 1 || spec.width > MAX_CAPTURE_DIMENSION || spec.height > MAX_CAPTURE_DIMENSION)
    throw new Error('Invalid capture viewport');
  if (!spec.target || spec.target.length > 4096 || (spec.steps?.length ?? 0) > 100) throw new Error('Invalid capture target or steps');
  const workspace = await realpath(options.workspaceRoot);
  const approvedFiles = new Set<string>();
  if (spec.kind === 'file') {
    for (const path of options.approvedPaths) {
      const resolved = resolve(workspace, path);
      if (!inside(workspace, resolved)) throw new Error('Approved asset escapes workspace');
      approvedFiles.add(resolved);
    }
  }
  let target: URL;
  if (spec.kind === 'file') {
    if (isAbsolute(spec.target) || !['.html', '.htm', '.svg'].includes(extname(spec.target).toLowerCase())) throw new Error('File capture requires a workspace-relative HTML or SVG target');
    const file = await realpath(resolve(workspace, spec.target));
    if (!approvedFiles.has(resolve(workspace, spec.target))) throw new Error('File target is not approved');
    if (!inside(workspace, file)) throw new Error('File target escapes workspace');
    const parts = relative(workspace, resolve(workspace, spec.target)).split(sep).map(encodeURIComponent);
    target = new URL(`/${parts.join('/')}`, FILE_ORIGIN);
  } else if (spec.kind === 'web') {
    try { target = new URL(spec.target); } catch { throw new Error('Invalid web capture target'); }
    if (!['http:', 'https:'].includes(target.protocol) || !loopback(target.hostname) || target.username || target.password)
      throw new Error('Web capture requires an exact loopback HTTP(S) origin without credentials');
  } else throw new Error('Unsupported capture target; remote and Figma capture are not supported');

  const executablePath = await browserExecutable(options.executablePath);
  if (options.signal?.aborted) throw new Error('Capture aborted');
  const controller = new AbortController();
  let browser: Browser | undefined;
  const abort = () => { controller.abort(); void browser?.close().catch(() => {}); };
  const onExternalAbort = () => abort();
  options.signal?.addEventListener('abort', onExternalAbort, { once: true });
  if (options.signal?.aborted) abort();
  const timer = setTimeout(abort, TIMEOUT_MS);
  const created: string[] = [];
  const ensureActive = () => { if (controller.signal.aborted) throw new Error(options.signal?.aborted ? 'Capture aborted' : 'Capture timed out'); };
  try {
    ensureActive();
    try {
      browser = await chromium.launch({ executablePath, headless: true, timeout: TIMEOUT_MS, args: ['--proxy-server=direct://', '--proxy-bypass-list=*'] });
    } catch (error) {
      ensureActive();
      throw new Error(`Browser dependency unavailable: could not launch ${executablePath}: ${error instanceof Error ? error.message : String(error)}`);
    }
    ensureActive();
    // 2. 新規コンテキストを使い、ページ読込み前に通信経路を制限する。
    const context = await browser.newContext({ viewport: { width: spec.width, height: spec.height }, serviceWorkers: 'block', acceptDownloads: false });
    context.setDefaultTimeout(10_000);
    context.setDefaultNavigationTimeout(15_000);
    const page = await context.newPage();
    const failures: string[] = [];
    let initialNavigation = true;
    const navigationTarget = new URL(target.href);
    navigationTarget.hash = '';
    const fail = (message: string) => { if (failures.length < 20) failures.push(message); };
    page.on('popup', popup => { fail('Popup blocked'); void popup.close().catch(() => {}); });
    page.on('download', () => fail('Download blocked'));
    page.on('framenavigated', frame => {
      if (frame === page.mainFrame() && frame.url() !== target.href) fail(`Unexpected navigation: ${frame.url()}`);
    });
    page.on('requestfailed', request => fail(`Resource failed: ${request.url()} (${request.failure()?.errorText ?? 'unknown error'})`));
    page.on('response', response => { if (response.status() >= 400) fail(`Resource returned HTTP ${response.status()}: ${response.url()}`); });
    await context.routeWebSocket('**/*', socket => { fail(`WebSocket blocked: ${socket.url()}`); socket.close(); });
    await context.route('**/*', async route => {
      const request: Request = route.request();
      let url: URL;
      try { url = new URL(request.url()); } catch { fail('Invalid resource URL'); await route.abort(); return; }
      if (!['GET', 'HEAD'].includes(request.method()) || url.origin !== target.origin || url.username || url.password) {
        fail(`Request blocked: ${request.method()} ${request.url()}`); await route.abort(); return;
      }
      if (request.isNavigationRequest()) {
        if (!initialNavigation || request.frame() !== page.mainFrame() || url.href !== navigationTarget.href) {
          fail(`Unexpected navigation blocked: ${request.url()}`); await route.abort(); return;
        }
        initialNavigation = false;
      }
      try {
        if (spec.kind === 'web') {
          // continue は転送先を再検査しないため、HTTP リダイレクトを追わずに取得する。
          const response = await route.fetch({ maxRedirects: 0, timeout: 15_000 });
          try {
            if (response.status() >= 300 && response.status() < 400 && response.status() !== 304) throw new Error(`HTTP redirect blocked: ${url.href}`);
            await route.fulfill({ response });
          } finally { await response.dispose(); }
          return;
        }
        const decoded = decodeURIComponent(url.pathname);
        if (decoded.includes('\0') || decoded.includes('\\')) throw new Error('Invalid asset path');
        if (!approvedFiles.has(resolve(workspace, `.${decoded}`))) throw new Error('Asset is not in the approved source scope');
        const file = await realpath(resolve(workspace, `.${decoded}`));
        if (!inside(workspace, file)) throw new Error('Asset escapes workspace');
        const info = await stat(file);
        if (!info.isFile() || info.size > MAX_ASSET_BYTES) throw new Error('Asset is not a regular file or exceeds size limit');
        const bytes = await readFile(file);
        if (bytes.length > MAX_ASSET_BYTES) throw new Error('Asset exceeds size limit');
        await route.fulfill({ status: 200, contentType: CONTENT_TYPES[extname(file).toLowerCase()] ?? 'application/octet-stream', body: request.method() === 'HEAD' ? '' : bytes });
      } catch (error) {
        fail(`Capture resource unavailable: ${url.pathname} (${error instanceof Error ? error.message : String(error)})`);
        if (!controller.signal.aborted) await route.abort().catch(error => fail(`Resource abort failed: ${String(error)}`));
      }
    });
    // 3. 宣言された操作と描画済みアセットを確認してから画像を取得する。
    await page.goto(target.href, { waitUntil: 'load' });
    const actions: Array<{ action: string; selector: string; result: 'passed' }> = [];
    for (const step of spec.steps ?? []) {
      ensureActive();
      await performStep(page, step);
      actions.push({ action: step.action, selector: step.selector, result: 'passed' });
    }
    const brokenAssets = await page.evaluate(async () => {
      await document.fonts.ready;
      return [
        ...Array.from(document.querySelectorAll('img')).filter(image => !image.complete || image.naturalWidth === 0).map(image => image.currentSrc || image.src),
        ...Array.from(document.fonts).filter(font => font.status === 'error').map(font => `font: ${font.family}`),
      ];
    });
    if (brokenAssets.length) throw new Error(`Capture contains failed images or fonts: ${brokenAssets.join(', ')}`);
    const screenshot = await page.screenshot({ type: 'png' });
    ensureActive();
    if (failures.length) throw new Error(`Capture resource/navigation failure: ${failures.join('; ')}`);
    const details = { id: spec.id, kind: spec.kind, target: spec.target, url: page.url(), title: await page.title(), viewport: { width: spec.width, height: spec.height }, actions, limitations: 'Browser request restrictions are not an OS sandbox. Loopback GET requests can have side effects; use disposable local targets.' };
    // 4. ページを停止し、遅れて判明した失敗も確認してから証跡を書き出す。
    ensureActive();
    await context.close();
    ensureActive();
    if (failures.length) throw new Error(`Capture resource/navigation failure: ${failures.join('; ')}`);
    await mkdir(options.artifactRoot, { recursive: true });
    const stem = `capture-${randomUUID()}`;
    const png = join(options.artifactRoot, `${stem}.png`);
    const receipt = join(options.artifactRoot, `${stem}.json`);
    const pngFile = await open(png, 'wx');
    created.push(png);
    try { await pngFile.writeFile(screenshot); } finally { await pngFile.close(); }
    ensureActive();
    const receiptFile = await open(receipt, 'wx');
    created.push(receipt);
    try { await receiptFile.writeFile(JSON.stringify(details, null, 2) + '\n'); } finally { await receiptFile.close(); }
    ensureActive();
    if (failures.length) throw new Error(`Capture resource/navigation failure: ${failures.join('; ')}`);
    return { artifacts: [png, receipt], details };
  } catch (error) {
    await Promise.all(created.map(path => unlink(path).catch(() => {})));
    if (controller.signal.aborted) ensureActive();
    throw error;
  } finally {
    clearTimeout(timer);
    options.signal?.removeEventListener('abort', onExternalAbort);
    await browser?.close().catch(() => {});
  }
}
