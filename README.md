# FSR Connector Workshop Site

This repository contains a Hugo documentation site using the Relearn theme.

## References

- Hugo (source): https://github.com/gohugoio/hugo
- Hugo docs / install guides: https://gohugo.io/installation/
- Relearn theme (source): https://github.com/McShelby/hugo-theme-relearn

## Prerequisites

- `git`
- Hugo (Extended recommended)

Verify Hugo is installed:

```bash
hugo version
```

## Clone The Repository

Use one of the repository remotes:

```bash
git clone https://github.com/ftnt-dspille/fsr-connector-creation.git
cd fsr-connector-creation
```

## Install Hugo

Follow the official install instructions for your OS:

- macOS: https://gohugo.io/installation/macos/
- Linux: https://gohugo.io/installation/linux/
- Windows: https://gohugo.io/installation/windows/

After install, confirm:

```bash
hugo version
```

## Run Locally

Start the local development server:

```bash
hugo server -D
```

Then open:

- http://localhost:1313/

Stop the server with `Ctrl+C`.

## Build Static Site

Generate production files:

```bash
hugo
```

Output is written to `public/`.

## Notes

- Theme is configured in `config.toml` as `hugo-theme-relearn`.
- The theme is vendored in this repo under `themes/hugo-theme-relearn`.

## Verifying the VSCode extension steps

Pages under `content/02-setup/` and `content/04-create-connector/` tell attendees
to run commands by name. Those names come from the
[fortisoar-connector-vscode](https://github.com/ftnt-dspille/fortisoar-connector-vscode)
extension manifest, and they drift when a command is renamed.

`scripts/docs-contract.json` is a vendored copy of the contract that extension
publishes (`npm run contract` over there). The linter checks every command id,
command title, settings key, and walkthrough step title cited in `content/`
against it:

```bash
python3 scripts/lint-docs-contract.py             # errors fail the build
python3 scripts/lint-docs-contract.py --coverage  # also list unmentioned commands
python3 scripts/lint-docs-contract.py --strict    # warnings fail too
```

After the extension changes, re-vendor the contract and re-run:

```bash
python3 scripts/lint-docs-contract.py --refresh /path/to/fortisoar-connector-vscode
```

`scripts/docs-contract-ignore.txt` holds menu labels that are deliberately *not*
extension commands (VSCode built-ins, the PyCharm RDK plugin, OS dialogs).
Drafts (`draft: true`) are skipped unless you pass `--include-drafts`.
CI runs this via `.github/workflows/docs-contract.yaml`.
