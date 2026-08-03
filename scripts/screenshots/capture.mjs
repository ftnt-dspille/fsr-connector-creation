#!/usr/bin/env node
/**
 * Captures workshop screenshots by driving the FortiSOAR Connector extension
 * inside code-server (a real Node extension host, painted in a browser) with
 * Playwright.
 *
 * Why code-server and not vscode.dev: the extension is a Node-platform
 * extension (`main`, no `browser` entrypoint) that spawns Python. The web
 * extension host runs extensions in a webworker with no child_process, so it
 * can never load there. code-server runs the real thing server-side and only
 * ships the UI to the browser, so everything works.
 *
 * Run `./run.sh` rather than calling this directly -- it builds the VSIX, starts
 * the container, seeds a workspace, and then invokes this script.
 *
 * Usage: node capture.mjs [--url http://localhost:8443] [--out ../../static/screenshots]
 *                         [--only tree,palette] [--theme dark|light]
 */
import { chromium } from "playwright";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const HERE = path.dirname(fileURLToPath(import.meta.url));

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

// code-server opens an empty window unless the workspace folder is named in the
// query string. Without it the FortiSOAR view has no registry to read and every
// tree locator times out.
const FOLDER = arg("folder", "/home/coder/project");
const URL = arg("url", "http://localhost:8443").replace(/\/$/, "") +
  `/?folder=${encodeURIComponent(FOLDER)}`;
const OUT = path.resolve(HERE, arg("out", "../../static/screenshots"));
const THEME = arg("theme", "dark");
const ONLY = arg("only", "").split(",").filter(Boolean);

const VIEWPORT = { width: 1440, height: 900 };

// Tree rows are addressed by their visible label, never by index. The tree
// prepends advisory rows ("Python not found -- click to fix", "Configure
// connector first…") whose presence depends on the environment, so nth(0) is
// not stably the connector.
const CONNECTOR_LABEL = "Hello World";
const OPERATION_LABEL = "Say Hello";

/**
 * The shot list. Each entry: an id (becomes <id>.png), the doc page it serves
 * (so a reader of this file knows what breaks if the shot changes), and an
 * async `run(page)` that leaves the UI in the state to capture.
 *
 * `clip` optionally narrows the capture to a region -- 'sidebar' crops to the
 * activity+side bar, which is what most tree-view instructions need.
 */
const SHOTS = [
  {
    id: "connector-tree",
    doc: "02-setup/01-install-vscode-extension.md -- the FortiSOAR Connectors view",
    clip: "sidebar",
    async run(page) {
      await openFortisoarView(page);
      await expandConnector(page);
    },
  },
  {
    id: "command-palette",
    doc: "02-setup/01-install-vscode-extension.md -- Command Palette → FortiSOAR: …",
    async run(page) {
      await closeQuickInput(page);
      await page.keyboard.press(modifier() + "+Shift+P");
      await page.waitForSelector(".quick-input-widget", { state: "visible" });
      await page.keyboard.type("FortiSOAR: ", { delay: 20 });
      await page.waitForTimeout(600);
    },
  },
  {
    id: "connector-context-menu",
    doc: "04-create-connector/* -- right-click the connector → Configure / Export",
    keepPointer: true,
    async run(page) {
      await openFortisoarView(page);
      await rightClickRow(page, CONNECTOR_LABEL);
    },
  },
  {
    id: "operation-context-menu",
    doc: "04-create-connector/04-test-and-debug -- right-click an operation → Run Operation",
    keepPointer: true,
    async run(page) {
      await openFortisoarView(page);
      await expandConnector(page);
      await rightClickRow(page, OPERATION_LABEL);
    },
  },
  {
    id: "walkthrough",
    doc: "02-setup/01-install-vscode-extension.md -- the guided walkthrough table",
    async run(page) {
      await runCommand(page, "FortiSOAR: Open Walkthrough");
      await page.waitForSelector(".gettingStartedContainer, .welcomePageContainer", {
        timeout: 20000,
      });
      await page.waitForTimeout(1500);
    },
  },
  {
    id: "new-connector-prompt",
    doc: "04-create-connector/01-create-connector -- the first New Connector prompt",
    async run(page) {
      // The wizard is a chain of quick inputs, not a dialog. Shoot the first
      // one (the name prompt, with its validation hint) and back out -- walking
      // the whole chain would scaffold a connector into the seeded workspace
      // and change every later shot.
      await runCommand(page, "FortiSOAR: New Connector");
      await page.waitForSelector(".quick-input-widget", { state: "visible", timeout: 20000 });
      await page.waitForTimeout(600);
    },
  },
  {
    id: "configure-form",
    doc: "04-create-connector/02-add-configuration §5 -- the Configure Connector form",
    async run(page) {
      await closeEditors(page);
      await openFortisoarView(page);
      await rightClickRow(page, CONNECTOR_LABEL);
      await clickMenuItem(page, "Configure Connector");
      await waitForFormWebview(page, "Configure");
    },
    // Save after the shot: an unconfigured connector makes Run Operation open a
    // "Configure Now / Run Anyway" warning instead of the parameter form, which
    // is what broke the run-form and run-output shots the first time.
    async after(page) {
      await clickFormButton(page, "Save");
      await page.waitForTimeout(4000);
      await closeEditors(page);
    },
  },
  {
    id: "run-form",
    doc: "04-create-connector/04-test-and-debug §3 -- the operation parameter form",
    async run(page) {
      // The configure step's health check left the output panel open; it would
      // fill the bottom third of a shot that is about the form.
      await closePanel(page);
      await openFortisoarView(page);
      await expandConnector(page);
      await rightClickRow(page, OPERATION_LABEL);
      await clickMenuItem(page, "Run Operation");
      await waitForFormWebview(page, OPERATION_LABEL);
    },
  },
  {
    id: "run-output",
    doc: "04-create-connector/04-test-and-debug -- results in the FortiSOAR Output channel",
    async run(page) {
      // Follows run-form: submitting the form runs the operation for real, and
      // the extension shows the FortiSOAR channel itself. First run also
      // creates the managed venv, so allow generous time.
      await clickFormButton(page, "Run");
      await page.waitForSelector(".part.panel", { state: "visible", timeout: 180000 });
      await page.waitForFunction(
        () => document.querySelector(".part.panel")?.textContent?.includes("completed"),
        undefined,
        { timeout: 180000 },
      );
      await page.waitForTimeout(800);
    },
  },
  {
    id: "export-validation",
    doc: "04-create-connector/04-test-and-debug §9 -- pre-export validation issues",
    async run(page) {
      await closeEditors(page);
      await openFortisoarView(page);
      await rightClickRow(page, CONNECTOR_LABEL);
      await clickMenuItem(page, "Export Connector as Tarball");
      // The fixture ships no icon files, so validation returns warnings and the
      // issue picker opens before any save dialog.
      await page.waitForSelector(".quick-input-widget", { state: "visible", timeout: 30000 });
      await page.waitForTimeout(600);
    },
  },
];

// Deliberately not captured: a paused breakpoint. It needs a debug session,
// a gutter click at a line number that moves whenever operations.py changes,
// and a stop that races the capture -- three ways to produce a wrong frame
// silently. Shoot that one by hand on desktop VSCode.

// The workbench keybindings follow the *browser's* platform, not the server's:
// code-server on Linux still renders ⌘ shortcuts when viewed from macOS. Match
// the machine Playwright runs on.
const MODIFIER = process.platform === "darwin" ? "Meta" : "Control";
function modifier() {
  return MODIFIER;
}

async function closeQuickInput(page) {
  await page.keyboard.press("Escape");
  await page.waitForTimeout(150);
}

async function runCommand(page, command) {
  await closeQuickInput(page);
  await page.keyboard.press(modifier() + "+Shift+P");
  await page.waitForSelector(".quick-input-widget", { state: "visible" });
  await page.keyboard.type(command, { delay: 15 });
  await page.waitForTimeout(500);
  await page.keyboard.press("Enter");
  await page.waitForTimeout(1200);
}

async function openFortisoarView(page) {
  await closeQuickInput(page);
  // The view lives in its own activity-bar container titled "FortiSOAR". The
  // accessible label sits on the inner <a>, not the <li> -- targeting the li
  // silently matches nothing.
  const item = page.locator('.activitybar .monaco-action-bar li:has(a[aria-label*="FortiSOAR" i])');
  if (await item.count()) {
    // Clicking the icon TOGGLES the container: if a previous shot already
    // opened it, clicking again collapses the sidebar and every subsequent
    // locator times out. Only click when it isn't already the active one.
    const active = (await item.first().getAttribute("class"))?.includes("checked");
    const sidebarOpen = await page.locator(".monaco-workbench .part.sidebar").isVisible();
    if (!active || !sidebarOpen) {
      await item.first().click();
    }
  } else {
    await runCommand(page, "View: Show FortiSOAR");
  }
  await page.waitForSelector(".pane-body .monaco-list-row", { timeout: 20000 });
  await page.waitForTimeout(400);
}

function row(page, label) {
  return page.locator(".pane-body .monaco-list-row").filter({ hasText: label }).first();
}

async function rightClickRow(page, label) {
  const target = row(page, label);
  await target.waitFor({ state: "visible", timeout: 20000 });
  await target.click({ button: "right" });
  await page.waitForSelector(".context-view .monaco-menu", { state: "visible" });
  await page.waitForTimeout(400);
}

// Context-menu entries are `.action-label` spans inside the floating menu, and
// they carry the full command title -- "FortiSOAR: Configure Connector", not
// "Configure Connector" as the docs write it. Anchor the match so "Run Tests
// (Mocked)" can't be hit by a request for "Run Tests".
async function clickMenuItem(page, label) {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const item = page
    .locator(".context-view .monaco-menu .action-label")
    .filter({ hasText: new RegExp(`^\\s*(FortiSOAR:\\s*)?${escaped}\\s*$`) })
    .first();
  await item.waitFor({ state: "visible", timeout: 10000 });
  await item.click();
}

// The configure and run forms are webviews, which code-server renders in a
// nested iframe. Waiting on the editor tab title is enough -- the frame paints
// synchronously once its HTML is set.
async function waitForFormWebview(page, titleFragment) {
  await page
    .locator(`.tabs-container .tab`, { hasText: titleFragment })
    .first()
    .waitFor({ state: "visible", timeout: 30000 });
  await page.waitForTimeout(1500);
}

// Clicks a button inside the form webview. Playwright reaches into the nested
// iframes by frame-walking; the form is the innermost one.
async function clickFormButton(page, label) {
  for (const frame of page.frames()) {
    const btn = frame.locator(`button:has-text("${label}")`);
    if (await btn.count().catch(() => 0)) {
      await btn.first().click();
      return;
    }
  }
  throw new Error(`no "${label}" button found in any webview frame`);
}

// Close tabs by clicking their X, not via a keybinding or the palette. The
// Cmd+K Cmd+W chord is swallowed when focus sits inside a webview iframe, and
// palette prefix-matching silently lands on a neighbouring command -- "View:
// Close All Editors" resolved to a settings command, which opened a dirty
// settings.json tab that then sat in the background of every later frame.
async function closeEditors(page) {
  await closeQuickInput(page);
  for (let i = 0; i < 12; i++) {
    const tab = page.locator(".tabs-container .tab").first();
    if (!(await tab.count())) break;
    await tab.hover();
    const x = tab.locator(".tab-actions .codicon-close, .tab-actions .codicon-circle-filled").first();
    if (!(await x.count())) break;
    await x.click();
    await page.waitForTimeout(250);
    // A dirty editor pops a "Save / Don't Save" modal -- discard, we never want
    // capture-time edits persisted into the container.
    const dontSave = page.locator('.monaco-dialog-box button:has-text("Don\'t Save")');
    if (await dontSave.count()) {
      await dontSave.first().click();
      await page.waitForTimeout(300);
    }
  }
  await page.waitForTimeout(300);
}

async function closePanel(page) {
  const close = page.locator(".part.panel .title-actions .codicon-panel-close").first();
  if (await close.count()) {
    await close.click();
    await page.waitForTimeout(400);
  }
}

async function expandConnector(page) {
  const node = row(page, CONNECTOR_LABEL);
  await node.waitFor({ state: "visible", timeout: 20000 });
  if ((await node.getAttribute("aria-expanded")) === "false") {
    await node.click();
    await page.waitForTimeout(800);
  }
}

// Park the pointer over dead space in the editor area so a hover tooltip from
// the previous step (the activity-bar "Testing" label, the status-bar
// notification bell) doesn't bleed into the capture. NOT the bottom-right
// corner -- that is the bell, and parking there pops "No Notifications".
async function parkPointer(page) {
  await page.mouse.move(Math.round(VIEWPORT.width * 0.72), Math.round(VIEWPORT.height * 0.62));
  await page.waitForTimeout(500);
}

async function clipFor(page, kind) {
  if (kind !== "sidebar") return undefined;
  const el = await page.locator(".monaco-workbench .part.sidebar").boundingBox();
  const bar = await page.locator(".monaco-workbench .part.activitybar").boundingBox();
  if (!el) return undefined;
  const x = bar ? Math.min(bar.x, el.x) : el.x;
  const width = bar ? el.x + el.width - x : el.width;
  return { x, y: el.y, width, height: el.height };
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: VIEWPORT,
    deviceScaleFactor: 2, // retina-quality PNGs for the Hugo site
    colorScheme: THEME === "light" ? "light" : "dark",
  });

  console.log(`opening ${URL}`);
  await page.goto(URL, { waitUntil: "domcontentloaded", timeout: 90000 });
  // Wait for the workbench shell, then for the extension host to finish
  // activating (our view container only appears once it has).
  await page.waitForSelector(".monaco-workbench", { timeout: 90000 });
  await page.waitForTimeout(6000);
  await dismissNotifications(page);
  // A restored editor tab (code-server reopens whatever was last open) would
  // sit behind every frame. `run.sh` starts a fresh container so this is
  // usually a no-op, but it matters when iterating against --keep.
  await closeEditors(page);

  const results = [];
  for (const shot of SHOTS) {
    if (ONLY.length && !ONLY.includes(shot.id)) continue;
    const file = path.join(OUT, `${shot.id}.png`);
    // Clear a FAILED- frame left by an earlier run: otherwise debugging debris
    // survives a green run and gets published with the site.
    fs.rmSync(path.join(OUT, `FAILED-${shot.id}.png`), { force: true });
    try {
      await shot.run(page);
      // Context-menu shots must keep the pointer where it is -- moving it would
      // hover-highlight a different menu row than the docs describe.
      if (!shot.keepPointer) await parkPointer(page);
      const clip = await clipFor(page, shot.clip);
      await page.screenshot({ path: file, clip });
      console.log(`  ✔ ${shot.id}.png`);
      results.push({ id: shot.id, ok: true, doc: shot.doc });
      // Optional post-capture step: leave state a later shot depends on.
      if (shot.after) await shot.after(page);
    } catch (e) {
      console.error(`  ✗ ${shot.id}: ${e.message.split("\n")[0]}`);
      await page
        .screenshot({ path: path.join(OUT, `FAILED-${shot.id}.png`) })
        .catch(() => undefined);
      results.push({ id: shot.id, ok: false, doc: shot.doc, error: e.message.split("\n")[0] });
    }
    await closeQuickInput(page).catch(() => undefined);
  }

  await browser.close();

  const failed = results.filter((r) => !r.ok);
  fs.writeFileSync(
    path.join(OUT, "manifest.json"),
    JSON.stringify({ theme: THEME, viewport: VIEWPORT, shots: results }, null, 2) + "\n",
  );
  console.log(`\n${results.length - failed.length}/${results.length} captured → ${OUT}`);
  if (failed.length) {
    console.error("failed: " + failed.map((f) => f.id).join(", "));
    process.exit(1);
  }
}

async function dismissNotifications(page) {
  // "Your workspace is not trusted", welcome toasts, etc. would sit on top of
  // every screenshot. Clear the notification center if it is showing.
  const clear = page.locator('.notifications-center a[title*="Clear" i]');
  if (await clear.count()) {
    await clear.first().click().catch(() => undefined);
  }
  const toasts = page.locator(".notification-toast .codicon-notifications-clear");
  const n = await toasts.count();
  for (let i = 0; i < n; i++) {
    await toasts.nth(0).click().catch(() => undefined);
    await page.waitForTimeout(150);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
