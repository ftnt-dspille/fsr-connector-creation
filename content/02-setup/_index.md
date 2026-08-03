---
title: "Getting Started"
linkTitle: "2. Getting Started"
description: "Set up your Python development environment with your choice of VSCode or PyCharm."
weight: 20
---

This section will help you set up your Python development environment for building FortiSOAR connectors.

## Choose your IDE

You can build connectors in **either IDE** -- pick one and follow its setup pages:

| IDE | Setup pages | Recommended? |
|-----|-----------|--------------|
| **VSCode** + FortiSOAR Connector extension | [Install VSCode Extension]({{< relref "01-install-vscode-extension" >}}) | ✅ Recommended -- purpose-built for connectors |
| **PyCharm** + FortiSOAR RDK plugin | [Install PyCharm, UV, and Python]({{< relref "02-install-pycharm-python" >}}) → [Debug Python Code]({{< relref "03-debug-python" >}}) → [Install SOAR RDK]({{< relref "04-install-soar-rdk" >}}) | Alternative -- uses the RDK plugin |

Both paths use **uv** to install Python and share the same [Python primer]({{< relref "05-python-primer" >}}).

## Prerequisites

Before you begin, make sure you have the following:

- A computer running **Windows 10+** or **macOS 12+**.
- An internet connection to download installers.
- Administrator or standard user permissions to install software.

## Next steps

Pick your IDE above and follow its setup guide, then continue to [Build Your First Connector]({{< relref "04-create-connector" >}}).