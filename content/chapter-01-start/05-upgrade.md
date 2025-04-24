---
title: Upgrade
menuTitle: Upgrade
weight: 50
---

Sometimes, new features will be added to the building environment and
your local hugo environment will need an update. To do so, you will need
to:

1. check out the `tec-builder-template` project in GitLab
2. copy the folders to your own project

### Step 1. Check out the `tec-builder-template` project

All latest files are in this repo: [tec-builder-template](https://svl-devops-gitlab01.fortilab.fortinet.com/tec-content/devops/tec-builder-template) in GitLab.
Make sure you can access this repo. If not, ask an admin to add you as
a member.

If this is the first time, clone it.

```shell
git clone git@svl-devops-gitlab01.fortilab.fortinet.com:tec-content/devops/tec-builder-template.git
```

If you have this cloned already, you can update it use the `git pull` command:

```shell
cd tec-builder-template
git pull

```

### Step 2. Delete old folders and copy the new folders over

1. Delete the old folders in your own project.

   Because newer version may remove some outdated files, it is better to remove old folders.

   ```shell
   cd /your/own/project

   rm -rf archetypes
   rm -rf assets
   rm -rf i18n
   rm -rf layouts
   rm -rf static
   rm -rf themes
   ```

   {{% notice info %}}
   If you have customized code in the `layouts` folder, make a back up copy and later copy them back. And make sure `hugo serve` does not give errors or warnings.
   {{% /notice %}}

1. Copy everything in the `tec-builder-template/hugo-builder` folder into your own project.

   ```shell
   cd /your/cloned/tec-builder-template
   cp -r hugo-builder/* /your/own/project/

   ```

### Step 3. DONE

Now you can check your own project and find some files/folders may
have been changed. And you should see new features or bug fixes
that have been copied over. Make sure `hugo serve` does not give you warnings or errors.

You can now continue your work flow as usual.
