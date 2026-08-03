---
title: "Install the VSCode Extension"
linkTitle: "Install VSCode Extension"
description: "Install the FortiSOAR Connector VSCode extension, set up Python, trust your workspace, and take the guided walkthrough."
weight: 1
---

This guide walks you through installing the **FortiSOAR Connector** VSCode extension and getting your environment ready for connector development.

---

## Prerequisites

| Requirement     | Details                                                                                                                       |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------|
| **VSCode 1.85+** | Download from [code.visualstudio.com](https://code.visualstudio.com).                                                         |
| **Python 3.9+**  | On your `PATH` or selectable via the Python extension. If you don't have Python yet, install it with `uv` -- see steps 2-3 of [Installing PyCharm, UV, and Python]({{< relref "02-install-pycharm-python#2-install-uv" >}}) (the `uv` + Python install is the same regardless of IDE). |
| **OS keychain**  | macOS Keychain, Windows Credential Manager, or Linux libsecret -- used for credential storage.                                 |

---

## 1. Install the extension

The marketplace listing is coming with v1.0; until then, install from a `.vsix` file:

{{< tabs >}}
{{% tab title="From a GitHub Release (easiest)" %}}
1. Go to the [Releases page](https://github.com/ftnt-dspille/fortisoar-connector-vscode/releases).
2. Download the `.vsix` from the latest tagged release (`v*`).
3. Open the **Extensions** view (`Cmd+Shift+X` / `Ctrl+Shift+X`).
4. Click the `...` menu at the top → **Install from VSIX...** → pick the downloaded `.vsix`.
5. Reload when prompted.
{{% /tab %}}
{{% tab title="From a built VSIX" %}}
1. Open the **Extensions** view (`Cmd+Shift+X` / `Ctrl+Shift+X`).
2. Click the `...` menu at the top → **Install from VSIX...** → pick `fortisoar-connector.vsix`.
3. Reload when prompted.
{{% /tab %}}
{{% tab title="Building from source" %}}
Clone the repo, run `pnpm install`, then either press `Cmd+Shift+B` (the default build task is **Build VSIX**) or run `pnpm run package`. The output `fortisoar-connector.vsix` lands at the project root, ready to install with the steps above.
{{% /tab %}}
{{< /tabs >}}

---

## 2. Install the Python tooling

The extension declares the [Microsoft Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and [debugpy](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy) as hard dependencies (needed for run/debug). If you don't have them, VSCode prompts on first activation:

> "Cannot activate the 'FortiSOAR Connector' extension because it depends on the 'Python' extension … Would you like to install the extension and reload the window?"

Click **Install and Reload** -- VSCode handles the install + reload in one go. No manual marketplace trip needed.

---

## 3. Open a folder and trust the workspace

1. Open a folder in VSCode that contains (or will contain) one or more connectors. **A folder must be open** -- the connector registry lives at `<workspace>/.fortisoar/local_data.json`.
2. **Trust the workspace** when prompted. The extension runs Python from connector source folders, which Restricted Mode blocks. Click **Trust** in VSCode's banner, or open the Command Palette and run `Workspaces: Manage Workspace Trust`.

---

## 4. Verify Python setup

Make sure Python 3.9+ is on your `PATH` (or selected via the Python extension). If it isn't, the extension's preflight surfaces a modal with **Select Interpreter / Open Settings / Install Python** the first time you Run / Debug / Check Health.

You can also check proactively: Command Palette → **`FortiSOAR: Check Python Setup`**.

{{% notice tip %}}
Set `fortisoar.pythonPath` in VSCode settings to override the Python interpreter used for the managed venv's base. Empty (default) uses the Python extension's selected interpreter, falling back to system Python.
{{% /notice %}}

---

## 5. The managed venv (first run)

On the first run of any operation, the extension creates a managed venv at its global storage path and installs the bundled `fortisoar_connector_engine` wheel. This takes ~5-15 seconds and shows a progress notification. Subsequent runs reuse it.

Each connector's own `requirements.txt` is automatically `pip install`-ed into the managed engine venv before the first Run / Debug / Check Health, and re-installed whenever the file changes. Tracked per-connector by a `sha256` of `requirements.txt` so unchanged files don't reinstall.

To force a clean reinstall: **`FortiSOAR: Reset Python Environment`** -- wipes the engine venv and clears every connector's install marker.

---

## 5b. Getting a connector into the view

You'll scaffold the Dad Jokes connector from scratch in the next section, but
there are three other ways to populate the **FortiSOAR Connectors** view:

| Command | What it does |
|---|---|
| **`FortiSOAR: Install Sample Connector`** | Drops a small working connector into the workspace -- handy for trying Run/Debug before you've written anything. |
| **`FortiSOAR: Import Connector from Folder`** | Registers a connector you already have on disk. |
| **`FortiSOAR: Import Connector (from tgz)`** | Extracts and registers an exported `.tgz`. |

Housekeeping commands for the view itself:

| Command | What it does |
|---|---|
| **`FortiSOAR: Refresh`** | Re-reads `local_data.json` and recomputes readiness. Use it when the tree looks stale. |
| **`FortiSOAR: Remove from List`** | Unregisters a connector. Files on disk are left alone. |
| **`FortiSOAR: Reveal in Finder/Explorer`** | Opens the connector folder in your OS file browser. |
| **`FortiSOAR: Run Last Operation`** | Re-runs the last operation with the same parameters -- the fastest edit/run loop. |

---

## 6. Walkthrough (recommended starting point)

The extension ships with a guided tour that walks you through the entire inner loop -- Python setup → connector → configure → run → debug → export. It opens automatically the first time you install the extension.

If you closed it and want to come back:

- Click the **book icon** (📖) in the **FortiSOAR Connectors** view title bar, **or**
- Open an empty workspace and click **Open the walkthrough** in the welcome view, **or**
- Command Palette → **`FortiSOAR: Open Walkthrough`**.

Already-completed steps stay ticked across reloads, so you can resume wherever you left off.

The walkthrough covers:

| Step | What it teaches |
|------|-----------------|
| **Open a project folder** | FortiSOAR tracks connectors per workspace. |
| **Set up Python** | Verify a Python 3.9+ interpreter is available. |
| **Get a connector** | Scaffold one, install a sample, or import a tgz. |
| **Configure credentials** | Right-click → Configure Connector. Password fields go to the OS keychain. |
| **Run your first operation** | Expand the connector, right-click an operation → Run Operation. |
| **Debug with breakpoints** | Set a breakpoint in `operations.py`, then Debug Operation. |
| **Write tests** | Scaffold pytest-based mocked + live tests, then run them. |
| **Export a tarball** | Right-click the connector → Export Connector as Tarball. |

---

## You're ready

Once the extension is installed and Python is verified, continue to [Build Your First Connector]({{< relref "04-create-connector" >}}).

The **FortiSOAR Connectors** view, with a connector expanded to its operations:

{{< shot connector-tree "The FortiSOAR Connectors tree view" >}}

Every command is also reachable from the Command Palette under `FortiSOAR:`:

{{< shot command-palette "The Command Palette filtered to FortiSOAR commands" >}}

And the guided walkthrough:

{{< shot walkthrough "The FortiSOAR getting-started walkthrough" >}}
