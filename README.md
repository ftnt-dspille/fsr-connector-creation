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
