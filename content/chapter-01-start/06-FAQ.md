---
title: FAQ
menuTitle: FAQ
weight: 60
---

## General Questions

1. When I upgrade Hugo and now `hugo server` ran into errors.

   - This is probably due to incompatibility between versions.
     - First, make sure you upgrade to the latest Hugo.
     - Follow steps in section [Upgrade](05-upgrade.html) to upgrade your local environment.

1. After I publish to GitLab, my pipeline failed with error message about _Project `tec/tec-project-shared-ci` not found or access denied!_

   - All TEC document use a shared CI script to publish to the TEC website. You need permission to that project. Ask an admin to add
     you as a member of developer to that project.

1. After create and push a tag _0.1.2_, my new version does not show in the web site.

   - The version must start with a **v**. Use **v0.1.2** not **0.1.2** will work.

1. I heard that TEC has this great new feature but I don't see it in my setup. How to get it?
   - Follow steps in section [Upgrade](05-upgrade.html) to upgrade your local environment.

## Windows Specific Questions

1. When run `git clone`, it complains about authentication error because not public key is available.

   - This could because git is using its own ssh. Use this git configure command to let git use the system ssh:

     ```shell
     git config --global core.sshCommand C:/Windows/System32/OpenSSH/ssh.exe
     ```

1. When run `hugo server`, it complains about permission to open port 1313.

   - This probably is FortiClient is blocking hugo server from listening on any TCP port.
     You should see a notification pop up saying that. Open a ticket with mis to let them white list hugo on your computer.
