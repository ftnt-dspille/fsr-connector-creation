# Screenshot harness

Regenerates the VSCode-extension screenshots in `static/screenshots/` by driving
the real extension and photographing it. No hand-cropping, no stale frames.

```bash
./run.sh                          # full run, ~1 min after the first build
./run.sh --only connector-tree    # re-shoot one frame
./run.sh --keep                   # leave the container up at localhost:8443
EXT_REPO=/path/to/ext ./run.sh    # non-default extension checkout
```

Output lands in `static/screenshots/` alongside a `manifest.json` recording
which shot served which doc page.

Pages reference the shots through the `shot` shortcode, never a raw path:

```markdown
{{< shot run-form "The operation parameter form" >}}
```

It resolves `static/screenshots/<id>.png`, prefixes `HUGO_ASSET_PREFIX` (which
is what makes the images resolve under the GitHub Pages subpath -- `relURL` does
not, since `canonifyURLs` is off), and **errors the Hugo build** when the named
shot is missing. Renaming a shot without updating the pages fails the build
rather than shipping a broken image.

## Why code-server, and not vscode.dev

The extension is a **Node-platform** extension: `package.json` declares `main`
with no `browser` entrypoint, it is bundled `--platform=node`, and it spawns
Python to run connector operations. `vscode.dev` / `github.dev` run extensions
in a webworker with no `child_process` and no filesystem, so this extension can
never load there -- it is not a porting gap, it is the architecture.

`code-server` is a different thing: a real Node extension host running
server-side, shipping only the rendered UI to the browser. Everything works,
including the managed venv and debugging, and Playwright can drive the DOM.

Two consequences worth knowing:

- **Extensions resolve from Open VSX, not the MS marketplace.** The hard
  `extensionDependencies` (`ms-python.python`, `ms-python.debugpy`) are both
  published there, so `--install-extension` pulls them automatically.
- **There is no OS keychain in the container.** `SecretStorage` falls back to an
  in-memory/file store, so the "password fields go to the OS keychain" step
  behaves differently here. Don't capture keychain-specific UI from this
  harness -- shoot those on a desktop VSCode by hand.

## How it works

`run.sh`:

1. builds the VSIX from the extension repo (`npm run package`),
2. builds `Dockerfile` -- code-server **plus python3** (baked in, because
   without an interpreter the tree shows a "Python not found -- click to fix"
   row in every frame; installing it per-run was by far the slowest step),
3. seeds `/home/coder/.local/share/code-server/User/settings.json` so the UI is
   deterministic -- trust disabled, fixed dark theme, no welcome tab, no
   secondary sidebar, no command center,
4. extracts the `hello-world` connector fixture into `/home/coder/project` and
   writes `.fortisoar/local_data.json` so the tree has real content,
5. runs `capture.mjs`.

`capture.mjs` holds the shot list. Adding a screenshot is one entry:

```js
{
  id: "my-shot",                       // becomes my-shot.png
  doc: "page.md -- what it illustrates",
  clip: "sidebar",                     // optional: crop to activity+side bar
  keepPointer: true,                   // optional: for context-menu shots
  async run(page) { /* leave the UI in the state to capture */ },
}
```

## Traps this harness already works around

Each of these silently produced a wrong or empty frame:

- **The activity-bar icon toggles.** Clicking it when the view is already open
  *collapses* the sidebar, and every later locator times out. `openFortisoarView`
  only clicks when the container isn't already active.
- **`aria-label` lives on the inner `<a>`**, not the `<li>`. Targeting the `li`
  matches nothing and falls through to a command-palette fallback.
- **Keybindings follow the browser's platform, not the server's.** code-server
  on Linux renders ⌘ shortcuts when viewed from macOS, so the modifier is chosen
  from `process.platform` of the machine running Playwright.
- **Tree rows are addressed by label, never by index.** The tree prepends
  advisory rows ("Python not found…", "Configure connector first…") depending on
  the environment, so `nth(0)` is not stably the connector.
- **The pointer must be parked before capture** -- but *not* in the bottom-right
  corner, which is the notification bell and pops a "No Notifications" tooltip.
- **`?folder=` is required.** Without it code-server opens an empty window and
  there is no connector registry to render.
- **`docker cp` lands files owned by root.** code-server runs as `coder` and
  rewrites `settings.json` when it persists UI state; without a chown that write
  fails with EACCES and VSCode opens the file as a dirty tab with a "Failed to
  save" notification, which then sits behind every full-frame shot.
- **Context-menu labels carry the `FortiSOAR: ` prefix.** The menu reads
  "FortiSOAR: Configure Connector" even though the docs say "Configure
  Connector".
- **Never drive exact commands through the palette.** Prefix matching lands on
  neighbours -- "View: Close All Editors" resolved to a settings command and
  opened a settings.json tab. Click the real X on tabs and the panel instead.
- **An unconfigured connector doesn't open the run form.** `Run Operation` shows
  a "Configure Now / Run Anyway" warning first, so any shot of the parameter
  form has to run after the connector is configured -- that's what the
  `configure-form` shot's `after()` hook is for.
- **Webview forms live in nested iframes.** Reach their buttons by walking
  `page.frames()`, not from the top-level page.

## Failure output

A failed shot writes `FAILED-<id>.png` next to the others and the script exits
non-zero. Open that PNG first -- it shows exactly what the browser saw, which is
almost always faster than guessing at the selector.
