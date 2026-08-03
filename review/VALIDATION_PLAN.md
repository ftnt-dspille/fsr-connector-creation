# VSCode connector workshop -- validation plan

Goal: every instruction in this workshop is provably true of the shipped
extension, and stays true when the extension changes.

Two repos are involved:

| Repo | Path | Role |
|---|---|---|
| Workshop | `TEC/fsr-connector-workshop` | Hugo site (this repo) |
| Extension | `IdeaProjects/fortisoar-connector-vscode` | `fortisoar.fortisoar-connector` |

---

## Done

### Layer 1 -- docs/manifest contract

The extension generates `docs-contract.json` (`npm run contract`) listing every
command id, on-screen label, settings key, view id, and walkthrough step it
contributes. A vendored copy lives at `scripts/docs-contract.json`.

- `scripts/lint-docs-contract.py` checks every command id, `FortiSOAR: <Title>`
  string, settings key, and walkthrough step title cited in `content/` against
  it. Runs in CI via `.github/workflows/docs-contract.yaml`. Currently **17
  pages, 0 errors, 0 warnings**.
- `test/integration/contract.itest.ts` (extension repo) asserts, in a live
  VSCode host, that the contract matches the manifest, every command id is
  actually registered, every menu entry resolves, every settings key has a
  schema, the `getStarted` walkthrough ships the documented eight steps in
  order, and no walkthrough button wears a different command's label.

Caught and fixed: `fortisoar.runOperation` was titled **"Launch Operation"**
while the docs and the extension's own walkthrough said **"Run Operation"**.
Renamed to "Run Operation" in `package.json` and `src/tree.ts`.

### Layer 2 -- screenshot harness

`scripts/screenshots/run.sh` builds the VSIX, boots code-server in Docker with
the extension and a seeded connector workspace, and drives it with Playwright.
**10/10 shots** from a clean container. See `scripts/screenshots/README.md` for
the trap list.

Every shot is referenced from the pages through the `shot` shortcode
(`layouts/shortcodes/shot.html`), which errors the Hugo build if the named PNG
is missing -- a renamed or dropped shot breaks loudly instead of rendering a
broken image. No "pending live capture" notes remain in `content/`.

`vscode.dev` is not an option -- the extension is a Node-platform extension that
spawns Python, and the web extension host is a webworker with no
`child_process`. code-server runs the real extension host server-side.

### Layer 3 -- golden path for the Day-3 build

`test/integration/goldenPath.itest.ts` (extension repo) builds the Dad Jokes
connector the way an attendee does, in a live VSCode host, against the real
`icanhazdadjoke.com`:

```
New Connector → replace config fields in info.json → _make_request helper →
Add Operation ×3 → Configure Connector (health check runs on save) →
Check Health → run all three operations → Debug Operation (real breakpoint) →
Run Tests (Mocked) → Export (archive shape checked)
```

**15/15 green.** Each stage asserts its own artifact. Where the extension does
something other than what a page claims, the test asserts the *real* behaviour
with a comment naming the divergence -- so the docs are what has to move.

Two run helpers were added: `FORTISOAR_ITEST_GREP` runs one suite in isolation
(the golden path alone is ~15s vs. minutes for everything), and
`FORTISOAR_ITEST_KEEP_WS` keeps the scratch workspace so a failing pytest can be
re-run by hand.

The first run found **five** defects (a sixth -- the export layout -- came
out of Layer 8b below). Nothing static had caught any of them.

**Extension bugs -- fixed:**

1. *Scaffolded tests could never collect, for any connector.* `conftest.py` put
   `dirname(tests/)` on `sys.path`, which in the default layout is the connector
   folder itself -- but the tests import the connector *by folder name*
   (`import_module("dad-jokes.operations")`), which needs the folder's **parent**.
   Every `Run Tests (Mocked)` died at collection with
   `ModuleNotFoundError: No module named 'dad-jokes'` (pytest exit 2). Both
   `buildConftest` and `buildUnittestBootstrap` now walk up to whichever ancestor
   actually contains `CONNECTOR_FOLDER`, so both scaffold layouts work.
2. *The test venv had no engine and no connector deps.* It installed only
   `pytest` + `responses`, so even with the path fixed, importing the connector
   died on `from connectors.core.connector import ConnectorError` and then on
   `import requests`. `TestVenvManager.ensureReady` now also installs the bundled
   engine wheel and the connector's own `requirements.txt`, both keyed into the
   venv's cache marker.

   Note the unit test for #1 asserted the *broken* string
   (`sys.path.insert(0, REPO_ROOT)`) -- that's how it shipped. It now asserts the
   resolved-parent behaviour.

**Doc bugs -- fixed in `content/`:**

3. *The whole "debug an error scenario" exercise was fiction.*
   `icanhazdadjoke.com/j/<unknown-id>` answers **HTTP 200** with
   `{"message": "…not found", "status": 404}`. `raise_for_status()` never fires,
   so the promised `API error: 404 Not Found` never appears and page 04's §3/§6
   step-through (status_code 404 → HTTPError → except block) cannot be performed.
   Rewritten around what actually happens -- which is a better lesson anyway:
   status-code-only error handling silently returns the error body as data.
4. *`Run Tests (Mocked)` is not green out of the box.* The scaffolded mock fakes
   `{"ok": True}`; the workshop's `check_health` requires `id` + `joke`. Page 04
   §8 implied it passes untouched. Now documents adapting the fixture.
5. *Page 01's VSCode instructions didn't match the wizard.* It said "answer the
   prompts (name, version, description)" -- the wizard never asks for a version
   (hardcodes 1.0.0) and does ask for category, auth template, and starter
   operations. The scaffold is also not `"configuration": {}` (the auth template
   pre-fills `server_url` + `verify_ssl`), and the file tree shown was the RDK's,
   not the extension's. Page 03 likewise promised parameter **Title**, **Tooltip**
   and **Default value** prompts that Add Operation does not have (title is
   derived from the snake_case name; tooltip and default need an `info.json`
   edit).

### Layer 4 -- code snippets

`scripts/lint-code-snippets.py` extracts every fenced block in `content/` and
checks it: Python must compile, JSON must parse, and JSON that is an `info.json`
-- whole or a `configuration` / `operations` / single-operation fragment -- is
validated against the extension's `resources/info.schema.json` (vendored at
`scripts/info.schema.json`, refreshed with `--refresh /path/to/extension`).

It also cross-checks each page that shows *both* a complete `operations.py` and
a complete `info.json`: every declared operation must have a matching `def`, and
vice versa. That pair is what a reader copies wholesale, and a rename in one
without the other is invisible to every other check here. Verified to stay
silent on the clean page and fire in both directions when a handler is renamed.

Currently **70 snippets across 8 pages, 0 errors**. Runs in CI alongside the
contract linter. `<!-- snippet-lint: skip -->` on the line above a fence exempts
a deliberately-broken teaching example.

Caught and fixed: page 03's complete `info.json` had `"category": ["Utilities"]`
-- an array where the schema and the extension both want a string.

Scope note: this is a *parse*-level check. It does not import the snippets or
run them. The one page whose code is executed for real is the Day-3 build, and
that's Layer 3's job.

### Layer 5 -- the build-flow screenshots

Five new shots cover the Day-3 sequence: `new-connector-prompt`,
`configure-form`, `run-form`, `run-output`, `export-validation`. All ten are now
wired into the pages.

Caught and fixed while adding them:

- **`run.sh` copied `settings.json` in as root.** code-server runs as `coder`
  and rewrites that file whenever it persists UI state, so the write failed with
  EACCES and VSCode opened it as a *dirty* editor tab with a "Failed to save"
  notification -- which then sat in the background of every full-frame shot. The
  five original shots were all either sidebar-clipped or full-screen overlays,
  so nothing ever showed it. `run.sh` now chowns the file.
- **Context-menu labels carry the full command title** -- "FortiSOAR: Configure
  Connector", not "Configure Connector" as the docs write it.
- **`FAILED-<id>.png` frames survived a later green run** and were published
  with the site. `capture.mjs` now clears a shot's failure frame before
  re-attempting it.
- Driving the workbench through the **palette is unsafe for exact commands**:
  "View: Close All Editors" prefix-matched to a settings command and opened
  settings.json. Editor and panel closing now click the real X buttons.

Not captured, deliberately: a **paused breakpoint**. It needs a debug session, a
gutter click at a line number that moves whenever `operations.py` changes, and a
stop that races the capture -- three ways to produce a wrong frame silently.
Shoot that one by hand on desktop VSCode.

### Layer 6 -- command coverage

`--coverage` used to report 17 of 25 commands the workshop never mentioned,
including `initTests`, `runTestsMocked` and `debugOperation` -- steps Day 3
covers by heading but described in prose without naming the command, so the
contract linter couldn't protect them. All 25 are now named:

- the setup page gained a section on the other ways to populate the tree
  (`installSample`, both import commands) and the view's housekeeping commands
  (`refreshTree`, `removeConnector`, `revealInOS`, `runLast`);
- page 04 now names the palette form of every test and debug command
  (`debugOperation`, `initTests`, `runTests*`, `debugTests*`,
  `runOperationTests`, `resetTestEnvironment`).

**0 uncovered commands, 0 errors, 0 warnings.** Every command the workshop
mentions is now checked against the shipped manifest on every CI run.

### Layer 7 -- structure

The `02-setup` → `04-create-connector` jump is not a dropped section. Two
different things once lived at `03`:

- `content/03-python-primer.md` moved into the setup section in commit `9e3ca63`
  and is now `02-setup/05-python-primer.md` -- same title, 973 lines vs. the old
  965, so it grew rather than being truncated.
- `content/03-migrate-fpoc/` was deleted back in `f33e889` and nothing links to
  it any more.

Top-level section weights are 10 / 20 / 40, so the ordering is explicit and the
gap is cosmetic. Nothing to recover.

### Layer 8 -- integration tests in CI

The extension's CI ran `test:unit` only; the integration suite -- contract tests,
debug-session tests, and now the golden path -- had never run there. It does now,
as a second job in `.github/workflows/ci.yml`: Node 22, Python 3.12,
`contract:check`, then `xvfb-run -a pnpm run test:integration`.

The blocker was the fixture. `prepareWorkspace` extracted a hello-world tarball
from a sibling PyCharm-plugin checkout that only exists on a dev machine, and
threw when it was missing. It now falls back to
`resources/sample-connectors/hello-world`, which ships in the repo and is the
same connector. Verified by hiding the sibling checkout and running the suite:
**30/30 integration tests pass on the bundled sample.**

One thing to know: with the tarball absent, `test:e2e` reports "0 passing"
rather than failing. That's a silent skip, not a green -- the CI job deliberately
runs `test:integration` and not `test`, so nothing false-passes, but don't read
a `test` run on a machine without the fixture as e2e coverage.


### Layer 8b -- the export actually imports (live-verified)

The golden path originally asserted only that Export wrote a non-empty file.
Checking the artifact's *shape* turned up the worst defect of the lot.

**The extension exported a flat tarball** -- `info.json` at the archive root --
because `tar.c` packed from `cwd: reg.path`. Every FortiSOAR-importable bundle
nests everything under one top-level `<connector-name>/` directory: the RDK's
output does, the workshop's own shipped `hello-world.tgz` does, and pyfsr's
live-verified `pack_connector` documents it as a requirement.

Verified against a real 8.0.0 appliance, same connector packed both ways:

| Layout | Result |
|---|---|
| flat (what the extension produced) | **rejected** |
| nested `<name>/…` | installs, `status: Completed` |

So the workshop's final claim -- "this `.tgz` can be uploaded directly to
FortiSOAR under Content Hub → Connectors → Import" -- was **false for every
connector built with this extension**. Day 3's payoff step could not have
worked.

Worse, the failure is unrecognisable: the appliance answers a flat archive with
**"Connector with same name is already active"** -- verified with a name the box
had never seen, so an attendee would go hunting for a duplicate that doesn't
exist. That trap is now documented on page 04.

Fixed in `exportTarball` (pack from the connector's parent, prefixing every
entry with the folder name -- `validateFolderName` already guarantees that folder
matches `info.json.name`). Then re-verified end to end on the appliance: the
tarball the golden path produces **imports, configures, and executes** --
`get_random_joke` returned a real joke through the platform. Test connectors
were uninstalled afterwards.

The golden path now asserts the archive has exactly one top-level dir named for
the connector, that it contains info.json / connector.py / operations.py /
requirements.txt, and that no `__pycache__` or `build/` rides along.

Note the unit test that should have caught this. "Export -- tgz parity vs
hello-world fixture" compared the re-exported file set against the known-good
fixture, but *normalized the top-level prefix away* -- with a comment saying
"original tgz may have a top-level dir prefix; new tgz is flat from
connectorRoot". The difference was observed, written down, and accommodated. It
now asserts both archives carry the same single top-level directory.

Page 04 gained a section on the tarball's required layout and a **§10 Import into
FortiSOAR** walkthrough, so the workshop no longer stops one step short of the
platform.

### Layer 8c -- debug, for real, on the workshop's own connector

The golden path stubbed `startDebugging` everywhere (it captures the launch
config and runs the engine directly, since the engine swallows exceptions). Real
debug sessions were only ever exercised against the hello-world fixture, so page
04 §5 -- a 12-row table of what each `F10` shows while stepping through
`search_jokes` -- had never been performed on the connector attendees build.

It now is: a real debugpy session, breakpoint set on the exact line the page
tells you to break on (`search_term = params.get("search_term")`), asserting the
session pauses there and that `search_term == "dog"` and `limit == 3` in the
paused frame -- rows 1 and 4 of the documented table. **15/15 golden path.**


---

## Backlog, highest risk first

### P5 -- Commit the work

Both repos have all of the above uncommitted. Nothing here is committed or
pushed -- that's the one remaining step, and it's the author's call.

---

## Maintenance loop

When a command is renamed or added in the extension:

```bash
# extension repo
npm run contract && npm test          # unit + e2e + integration (incl. golden path)

# just the golden path (~15s, needs network)
FORTISOAR_ITEST_GREP="Golden path" npm run test:integration

# workshop repo
python3 scripts/lint-docs-contract.py --refresh /path/to/fortisoar-connector-vscode
python3 scripts/lint-docs-contract.py --coverage
python3 scripts/lint-code-snippets.py --refresh /path/to/fortisoar-connector-vscode
python3 scripts/lint-code-snippets.py
./scripts/screenshots/run.sh
```

## Traps worth not rediscovering

- **pnpm does not run `pre*` scripts.** A `pretest` hook is silently skipped,
  leaving stale `out-test/` output. Every script states its own dependencies.
- **`@vscode/test-electron` < 3 cannot launch VSCode 1.131+ on macOS** -- it
  spawns `Contents/MacOS/Electron`, the bundle ships `Code`. Fixed by the 3.1.0
  upgrade (requires Node ≥22).
- **A killed VSCode download leaves an `is-complete` marker on a corrupt
  cache.** Recovery is `rm -rf .vscode-test`.
- **Integration tests need modal stubs for the whole path**, not just the
  obvious dialog. Export opens a QuickPick *before* the save dialog whenever
  the connector has validation warnings (any connector without icon files).
- **The engine swallows connector exceptions.** `execute_operation.py` wraps
  `execute()` in `except Exception: print(e)` and exits **0**. A failing
  operation therefore looks successful to anything reading the exit code -- the
  reason `decideHealth` parses stdout instead. Assertions on run results have to
  read the engine's stdout, not its status.
- **`configureConnector`'s promise doesn't settle on submit**, only on
  cancel/dispose. A test that awaits the command after firing `submit` hangs
  until it disposes the panel.
- **Per-connector test venvs persist in globalStorage across runs.** A venv
  hand-patched while debugging will make the next run pass for the wrong reason.
  Delete `…/globalStorage/fortisoar.fortisoar-connector/test-venvs/<name>` before
  trusting a green.
- **`process.exit()` in the runner's catch skips its own `finally`** -- that's why
  `FORTISOAR_ITEST_KEEP_WS` prints nothing on a failing run. Find the kept
  workspace under `$TMPDIR/fortisoar-itest-ws-*`.
- **A connector tarball must have exactly one top-level directory** named for
  the connector. A flat archive is rejected by the appliance with the misleading
  "Connector with same name is already active" -- for a name it has never seen.
- **"Asserts a file was produced" is not a test of the file.** Export passed for
  months on existence + non-zero size while producing an archive FortiSOAR
  refused. Check the artifact's shape, not its presence.
- **A normalization in a test can hide the bug the test exists to find.** The
  tgz-parity test explicitly stripped the top-level prefix off both sides, with
  a comment noting the two archives differed. Observed, written down, accepted.
