---
title: Git
menuTitle: Git
weight: 30
---

[git official reference](https://git-scm.com/docs)

You can use git commands to do all git related tasks. Alternatively, you
can also use a GUI based git client. In VSCode, basic git functions are integrated. Try click around the Source Control button in VSCode to figure out.

Here are the git commands we most likely will use:

- `git clone`: Used to clone (copy) a git repository from the remote server to local.

  Example:

  ```sh
  git clone git@svl-devops-gitlab01.fortilab.fortinet.com:tec-content/devops/tec-user-guide.git
  ```

- `git pull`: Pull the latest updates from the remote server.
- `git add`: Stage changes so they can be committed later (saved)

  Example:

  ```sh
  # add all changes
  git add .
  ```

- `git commit`: Commit all staged changes, with commit message

  Example:

  ```sh
  git commit -a -m "Added chapter 3"
  ```

- `git push`: push local repository to remote server
- `git status`: check current status, you can see if there are any changes not committed yet.
- `git log`: Show all commit logs
- `git tag`: Add a tag to current commit. You will need this command
  to publish to TEC web site. You can also use Gitlab web interface to
  create new tags.

  Example:

  ```sh
  git tag v1.0.1
  git push --tags origin
  ```

## Example

A typical git work flow after you have already cloned the repo:

```sh
# check status
git status
# bring in any updates from remote
git pull

# Edit, preview, edit ...... until you are satisfied.

# stage all changs
git add .
# commit with a short and clear message
git commit -a -m "Added a new chapter on Git"
# push to server
git push
```
