---
title: Installation
menuTitle: Installation
weight: 5
---

## Prerequisite

The Prerequisite steps are one-time steps that are needed to setup the editing and publishing environment. Once the environment is setup correctly, all you need to do are
the editing and publishing steps in the next section.

For Windows users, please check the next section for more detailed installation steps.

1. You need **vscode**, **git** and **hugo** installed on you laptop

   - Download and install VSCode from [the VSCode home page](https://code.visualstudio.com/download)

     - In VSCode, extensions can enhance the editing experience.
       Click the extensions button on the left side toolbar, search and install these extensions:
       - Hugo Language and Syntax Support
       - Code Spell Checker
       - Markdown All in One

   - Install **git**:

     Most likely you already have git in you OS. If not, install it.

   {{<tabs>}}
   {{% tab title="Windows" icon="fab fa-windows" %}}

   Download the latest install package [git for windows](https://git-scm.com/download/win). To make git work with ssh, when installing, make sure to select **Use external OpenSSH**.

   {{% /tab %}}
   {{% tab title="Linux" icon="fab fa-ubuntu" %}}
   For Ubuntu or Debian:

   ```sh
   sudo apt install git-all
   ```

   {{% /tab %}}
   {{% tab title="macOS" icon="fab fa-apple" %}}
   With macOS you can do

   ```sh
   brew install git
   ```

   {{% /tab %}}
   {{</tabs>}}

   - Install **hugo**:

   {{<tabs>}}
   {{% tab title="Windows" icon="fab fa-windows" %}}

   Download the latest install package from the gohugo [Github Releases Page](https://github.com/gohugoio/hugo/releases). Or use `winget install hugo`.

   {{% /tab %}}
   {{% tab title="Linux" icon="fab fa-ubuntu" %}}
   For Ubuntu or Debian:

   ```sh
   sudo apt install hugo
   ```

   {{% /tab %}}
   {{% tab title="macOS" icon="fab fa-apple" %}}
   With macOS you can do

   ```sh
   brew install hugo
   ```

   {{% /tab %}}
   {{</tabs>}}

1. Make sure you can access the internal GitLab: <https://svl-devops-gitlab01.fortilab.fortinet.com>
   Login by clicking the OIDC FAC button, with Fortinet credential.

   ![gitlab login screen](gitlab_login.png)
   {{% notice info %}}
   Login by clicking the **DevOps OIDC FAC** button, then use your Fortinet credentials on the Corporate SSO page.
   Do **not** use the GitLab username password fields.
   {{% /notice %}}

1. In GitLab, you need to copy your public ssh key to GitLab to be able to use git with ssh.
   _For Windows users, you will need to run`ssh-keygen` to generate a pair of key first._

   - Click the user icon at the top right corner of the page.
   - Select **edit profile** from the drop down menu
   - Then click **SSH Keys** from the left panel.
   - Copy and paste your ssh public key in your computer to the **Key** text area on that page.
     You need to copy the _text content_ of the public key file.
     The public key file normally is under `.ssh` folder and has a `.pub` extension.
   - Click **Add Key** button.

1. Your project will be assigned with a name and an url to the gitlab repository. For example: **sdwan-advanced** and `git@svl-devops-gitlab01.fortilab.fortinet.com:tec-content/sdwan-advanced.git`. We will use **PROJECT_NAME** and **GIT_URL** in all examples from now on.

   {{% notice info %}}
   There will be two git link for the project, one for https and one for ssh.
   We should use the ssh one.
   {{% /notice %}}

   The following steps are run in the terminal of your computer to download and initialize the documents:

   1. Clone the gitlab projec. These commands create a new folder with the name of [PROJECT_NAME] and download the project there:

      ```shell
      git clone [GIT_URL]
      cd [PROJECT_NAME]
      ```

   1. Open the project in vscode (You can also use VSCode's GUI to open the [PROJECT_NAME] folder):

      ```sh
      code .
      ```

   1. Start hugo server. The hugo server monitors all changes in the folder and allows you to preview in realtime the result as you are editing the documents:

      ```sh
      hugo server
      ```

      From the output of the hugo server, you will see the web pages are prepared. In the end the last few lines of the output will be something like:

      ```text
      ...
      Web Server is available at {{% colortext red %}}http://localhost:1313/{{% /colortext %}} (bind address 127.0.0.1)
      Press Ctrl+C to stop
      ```

   1. The output of the command will show you the preview URL (<http://localhost:1313/>). Open it in your browser to preview.
   1. From this point on, you can use VSCode to edit the documents, and the browser will automatically show your editing result.

### Possible Error with New Versions of Hugo

Hugo version 0.125.6 and above breaks the re-learn theme we include. `hugo server` command will fail with errors like

```sh
ERROR render of "page" failed: ...  error calling highlight: invalid Highlight option: page
```

To fix this error, you will need to update your local files. Follow the two steps
outlined in section [Upgrade](../chapter-01-start/05-upgrade.html) in chapter 1.
