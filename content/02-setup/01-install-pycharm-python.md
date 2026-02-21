---
title: "Installing PyCharm, UV, and Python"
description: "A step-by-step guide to installing PyCharm on Windows and macOS, setting up Python via uv, and creating your first project."
weight: 1
---

This guide walks you through installing **PyCharm**, using **uv** to install **Python**, and creating your first project to verify everything works.

---

## 1. Install PyCharm

Download and install PyCharm for your operating system.

{{< tabs >}}
{{% tab title="Windows" %}}

### Download

1. Download the [PyCharm installer (.exe)](https://www.jetbrains.com/pycharm/download/#section=windows) from JetBrains.
   ![img.png](page1/download_pycharm.png?height=200px)

2. Run the installer and follow the wizard steps. Click **Next**
   ![img_1.png](page1/pycharm_install_inital.png)
3. Choose the installation location, the default location should be fine. Click **Next**
4. Select the desired installation options. I recommend checking all the options.
   ![img_2.png](page1/pycharm_installation_options.png)
5. Select an existing Start menu folder or create a new one. The folder contains the application shortcut in the Start menu. Click **Install** to begin the installation.
   ![img.png](page1/add_pycharm_to_start.png)
6. Once completed, choose whether to reboot immediately or manually at a later time. Click **Finish** to complete the installation.
   ![img.png](page1/reboot_pc_or_not_pycharm.png)
7. PyCharm is now available from the start menu. (The version may be different on yours, that's ok!)
   ![img.png](page1/pycharm_in_start_menu.png)

### Launch PyCharm

To run PyCharm, find it in the **Windows Start menu** or use the **desktop shortcut**. You can also run the launcher batch script or executable in the installation directory under `bin`.

When you run PyCharm for the first time, you can take several steps to complete the installation, customize your instance, and start working with the IDE.

{{% /tab %}}
{{% tab title="macOS" %}}

### Download

1. Navigate to the [PyCharm downloads page](https://www.jetbrains.com/pycharm/download/#section=mac) from JetBrains.
2. Select the processor type (Intel or Apple Silicon) and click Download.
   ![img.png](page1/pycharm_download_mac.png?height=250px)

2. Open the `.dmg` file and drag **PyCharm** into the **Applications** folder.
   ![img.png](page1/drag_dmg_to_apps.png?height=400px)

### Launch PyCharm

Open PyCharm from **Applications** or use **Spotlight** (`Cmd + Space` → type "PyCharm"). When you run PyCharm for the first time, macOS may ask you to confirm that you want to open an application downloaded from the internet. Click **Open** to proceed.
![img.png](page1/pycharm_first_launch.png?height=500px)

{{% /tab %}}
{{< /tabs >}}

---

## 2. Install uv

**uv** is a fast Python package and project manager written in Rust. We'll use it to install Python itself.

{{< tabs >}}
{{% tab title="Windows" %}}

Open **PowerShell** and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, **restart your terminal** so that the `uv` command is available on your PATH.

Verify the installation:

```powershell
uv --versionwd
```

{{% /tab %}}
{{% tab title="macOS" %}}

Open **Terminal** and run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, **restart your terminal** (or run `source $HOME/.local/bin/env`) so that the `uv` command is available on your PATH.

Verify the installation:

```bash
uv --version
```

{{% /tab %}}
{{< /tabs >}}

---

## 3. Install Python with uv

With uv installed, you can install Python in a single command. This works the same on both operating systems.

```bash
uv python install 3.12
```

Verify Python is available:

```bash
uv python list
```

You should see Python 3.12 listed in the output.

---

## 4. Create your first project

Now let's create a project using PyCharm's built-in wizard, configured to use **uv** as the interpreter type.

### Create a new project in PyCharm

1. Launch **PyCharm**.
2. On the Welcome screen, click **New Project**.
3. In the **New Project** dialog, configure the following:
   
   | Setting              | Value                                                                       |
   |----------------------|-----------------------------------------------------------------------------|
   | **Project type**     | Select **Pure Python** from the left sidebar.                               |
   | **Location**         | Choose where to save your project (e.g., `PycharmProjects/MyFirstProject`). |
   | **Interpreter type** | Click **uv**.                                                               |
   | **Python version**   | Select **3.12** from the dropdown.                                          |
   | **Path to uv**       | PyCharm should auto-detect the uv binary. If not, set it manually.          |
   
   The default uv path on Windows is `%USERPROFILE%\.local\bin\uv.exe`
   The default uv path on Mac is `$HOME/.local/bin/uv`
   
   You'll see a note confirming that a uv environment will be created in the project root (`.venv`).

4. Optionally check **Create Git repository** if you want version control from the start.
   ![img.png](page1/pycharm_project_confirmation.png)
5. Click **Create**.

After 15-20 seconds, you'll see a project window open in PyCharm with a .venv/ and a pyproject.toml

![img.png](page1/myFirstProject.png)

### Run a test script

1. In the PyCharm project explorer, right-click the project root and select **New → Python File**. Name it `hello.py`.
   ![img.png](page1/add_new_python_file.png)
   ![img.png](page1/helloy_py.png)
2. If you get a popup about adding the file to git, click **Add**
   ![img.png](page1/add_to_git.png)
   {{% notice note %}}
   Git is not in the scope of this workshop, but it's a great way to version control your code. This simply means you can track and save changes to your code over time, share code and collaborate with others, and easily revert to previous versions if needed.
   {{% /notice %}}

2. Add the following code to `hello.py`:
   
   ```python
   import sys

   def main():
       print("Hello from PyCharm!")
       print(f"Python version: {sys.version}")
       print("Your environment is set up correctly.")

   if __name__ == "__main__":
       main()
   ```
3. Your pycharm should look like this
   ![img.png](page1/pyhcarm_with_hello_py.png)

#### Execute Python code

##### Option 1

1. Right-click the file in the editor and select **Run 'hello'**, or press `Ctrl+Shift+F10` (Windows) / `Ctrl+Shift+R` (macOS).
   ![img.png](page1/right_click_run_python.png)

##### Option 2

1. Find the **Run** button in the toolbar and click it.
   ![img.png](page1/run_python_button.png)

##### Option 3

1. Open the terminal **inside** Pycharm. The icon is in the bottom left corner.
   ![img.png](page1/open_terminal_pycharm.png)
2. Type `uv run hello.py` and click Enter.

#### Find the output

You should see output at the bottom of the window similar to:

```text
Hello from PyCharm!
Python version: 3.12.x (main, ...) [...]
Your environment is set up correctly.
```

![img.png](page1/example_pycharm_output.png)

Congrats on setting up PyCharm and Python! You now have a working environment to start your Python journey.