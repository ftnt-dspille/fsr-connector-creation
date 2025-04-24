---
title: Commit and Push Changes to GitLab
menuTitle: Commit & Push
weight: 30
---

## Git Commit and Git Push

You can do this step as many times as you like. It is equivalent to
saving changes to the GitLab server.

You can either do it through GUI or through CLI.

### Through VSCode GUI

1. Save everything and make sure the documents are ok in the preview browser.
1. In VSCode, click the **Source Control Button** ![source control button](source_control.png?classes=inline&height=32px)
   on the left side tool bar.
1. Add all changes by clicking the **+** button on the **Changes** row. Notice the **+** button will show up when you mouse over the **Changes** row, and for each individual changed file, there is also a **+** button, which only add that file. The **+** button on the **Change** row adds all changes.
1. Add a commit message in the **Message** field
1. Click the **Commit** button.
1. Now all changes are saved locally. You need to push the changes to GitLab server.
   1. The **Commit** button will change its label to **Sync Changes**
   1. Click the **Sync Changes** button to push changes to GitLab server

> If you forget to click the **+** button or forget to even save the files, VSCode will ask you if you want to include all changes, click **YES** or **Save All & Commit**

![](vscode_commit.png)

### Through Command Line

Alternatively, if you are comfortable with git command line, you can do this through command line:

1. Make sure current git status is ok:
   ```sh
   git status
   ```
1. Stage all changes:
   ```sh
   git add .
   ```
1. Commit all staged changes:
   ```sh
   git commit -a -m 'brief description of this edit'
   ```
1. Push to gitlab server:
   ```sh
   git push
   ```
   If this is the first time you do a `git push`, it will fail and tell you to use a longer command to push: `git push --set-upstream origin [your branch name]`. Use that. The next time, you can just use `git push`.
