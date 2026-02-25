---
title: "Install SOAR RDK"
linkTitle: "Install SOAR RDK"
description: "Install and configure the FortiSOAR PyCharm RDK plugin so you can develop, test, and export connectors directly from your IDE."
weight: 10
---

The **FortiSOAR RDK** (Remote Development Kit) is a PyCharm plugin that lets you develop, test, and package connectors without leaving your IDE. In this section you'll install the plugin, connect it to your Python environment, and learn how to use its core features.

---

## Prerequisites

Before installing the RDK, make sure you have the following ready:

| Requirement          | Details                                                  |
|----------------------|----------------------------------------------------------|
| **PyCharm**          | Community or Professional edition installed and running. |
| **Python Installed** | Installed via uv (or another method).                    |

{{% notice note %}}
If you haven't installed PyCharm or Python yet, complete the [Installing PyCharm, UV, and Python]({{< relref "01-install-pycharm-python" >}}) guide first. That guide covers installing PyCharm, setting up uv, and installing Python 3.12.
{{% /notice %}}

---

## 1. Download the SOAR RDK plugin

1. Download the RDK `.zip` file to the machine where PyCharm is installed.
   
   {{% resources style="note" title="FortiSOAR PyCharm RDK Download" pattern=".*\.zip" /%}}

{{% notice warning %}}
Do **not** unzip the file. PyCharm expects the plugin as a `.zip` archive.
{{% /notice %}}

---

## 2. Install the plugin in PyCharm

1. Open **PyCharm**.
2. Open the Pycharm Settings**Settings**.
    - Windows / Linux: `File → Settings`
    - macOS: `PyCharm → Settings`
      ![img.png](pycharm_settings.png)
3. Navigate to the **Plugins** section in the settings, and click the **⚙️ gear icon** at the top of the Plugins panel
   ![img.png](plugin_settings.png)
4. Select **Install Plugin from Disk**
   ![img.png](install_plugin_from_disk.png)
6. Browse to the downloaded RDK `.zip` file and select it.

You will see the FortiSOAR RDK plugin listed in the Plugins panel.

7. Click **Apply**, then **OK**
   ![img.png](apply_ok_after_upload.png?height=500px)

You should see a **FortiSOAR RDK** entry in the PyCharm toolbar.
    ![img_1.png](rdk_installed.png?height=500px)


---

## 3. Configure the Python environment

The RDK needs to know where your Python interpreter lives so it can install its dependencies.

1. Click **FortiSOAR RDK** from the toolbar.
2. Select **Configure Python Path**.
   ![img.png](configure_python.png)
3. Point to your Python 3 installation.
   
   {{< tabs >}}
   {{% tab title="Windows (uv)" %}}
   If you installed Python with uv, the default path is:

```text
   %USERPROFILE%\.local\bin\python.exe
```

You can also find it by running this in PowerShell:

```powershell
   uv python list
```

{{% /tab %}}
{{% tab title="macOS (uv)" %}}
If you installed Python with uv, the default path is:

```text
   $HOME/.local/bin/python3
```

You can also find it by running this in Terminal:

```bash
   uv python list
```

{{% /tab %}}
{{% tab title="Windows (without uv)" %}}
If you installed Python directly from [python.org](https://www.python.org/downloads/) or the Microsoft Store, the interpreter is usually in one of these locations:

```text
   C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python312\python.exe
   C:\Python312\python.exe
```

Not sure where it is? Open **PowerShell** and run:

```powershell
   where.exe python
```

Or if you have multiple versions:

```powershell
   py --list-paths
```

The `py --list-paths` command shows every Python version installed on your system and its full path. Pick the 3.12 entry.
{{% /tab %}}
{{% tab title="macOS (without uv)" %}}
If you installed Python from [python.org](https://www.python.org/downloads/), Homebrew, or pyenv, the interpreter is usually in one of these locations:

| Installation method | Typical path |
   |---|---|
| **python.org installer** | `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3` |
| **Homebrew** | `/opt/homebrew/bin/python3` (Apple Silicon) or `/usr/local/bin/python3` (Intel) |
| **pyenv** | `$HOME/.pyenv/versions/3.12.x/bin/python3` |
| **macOS system Python** | `/usr/bin/python3` (ships with Xcode Command Line Tools) |

Not sure where it is? Open **Terminal** and run:

```bash
   which python3
```

To see the exact version at that path:

```bash
   python3 --version
```

{{% notice warning %}}
Avoid using the macOS system Python (`/usr/bin/python3`) for connector development. It is managed by Apple and may be an older version. Prefer a Homebrew, pyenv, or python.org installation instead.
{{% /notice %}}
{{% /tab %}}
{{< /tabs >}}

4. Click **OK**. The RDK installs its required dependencies automatically.
    ![img.png](click_ok_install_deps.png)

{{% notice note %}}
If you see an error message about a missing `pip` package, you can install it manually by running `python3 -m ensurepip`.
or if uving uv you can run `uv pip install pip`
![img.png](uv_install_pip.png)

Then retry the configure python path step.
{{% /notice %}}

{{% notice tip %}}
If the RDK can't find Python, double-check that you ran `uv python install 3.12` (or installed Python 3.12 through another method) and that your terminal can resolve
`python3 --version`. See the [Python installation steps]({{< relref "01-install-pycharm-python#3-install-python-with-uv" >}}) for troubleshooting.
{{% /notice %}}

When successful, you should see the FortiSOAR Terminal show that it installed a few python packages
    ![img.png](successful_installing_rdk.png)

---

## 4. Import an existing connector

If you already have a connector packaged as a `.tgz` file, you can open it directly in the RDK. You can also export a connector from FortiSOAR and import it into the RDK.

Here is a sample connector you can download and import:
    {{% resources style="note" title="FortiSOAR Connector Download" pattern=".*\.tgz" /%}}

1. Click **FortiSOAR RDK → Import FortiSOAR Connector**.
    ![img.png](import_connector_example.png)
2. Browse to your connector's `.tgz` file and select it. Then click **Open**
    ![img.png](select_and_open_connector.png)

You should see a message indicating that the connector was successfully imported.
    ![img.png](successful_import.png)

You will also see a new folder in your project explorer. This is the connector files you imported.
    ![img.png](new_folder.png)
3. Open the folder
3. The connector project opens in the RDK interface with its `info.json`, `connector.py`, and any supporting files.

<!-- ![img.png](page3/imported_connector.png) -->

---

## 5. Using the RDK

Once the plugin is installed and configured, here are the core workflows you'll use during development.

### Test configuration (health check)

1. Select your connector configuration from the dropdown.
2. Click **Run** to execute the health check.
3. View the result in the output panel — a successful check confirms your credentials and connectivity.

### Test operations

1. Navigate to the **Operations** tab.
2. Select an operation from the list.
3. Fill in the required test parameters.
4. Click **Execute Action**.
5. Review the output and debug as needed.

{{% notice tip %}}
You can use PyCharm's built-in debugger alongside the RDK. Set breakpoints in `connector.py` before clicking **Execute Action** and the debugger will pause at your breakpoints. See the [Debug Python Code]({{< relref "02-debug-python" >}}) guide for a refresher on breakpoints and stepping.
{{% /notice %}}

### Format your code

1. Right-click anywhere in a Python file.
2. Select **Format Document** (or press `Ctrl+Alt+L` / `Cmd+Option+L`).
3. Your code is automatically formatted to follow Python conventions.

### Export a connector

When your connector is ready for deployment:

1. Click **FortiSOAR RDK → Export**.
2. Choose a destination folder.
3. The connector is packaged as a `.tgz` file, ready to upload to FortiSOAR.

---

## Next steps

With the RDK installed you're ready to start building connectors. In the next section you'll create your first connector from scratch and test it using the workflows above.