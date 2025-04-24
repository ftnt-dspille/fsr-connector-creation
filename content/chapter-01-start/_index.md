---
title: From Zero to Publish a TEC Document
menuTitle: From Zero to Publish
weight: 10
---

All TEC projects use the following tools:

1. **VSCode**: the recommended editor
1. **Markdown**: a simple language to write the content of your project
1. **Hugo**: the program to generate the HTML pages and allow you to live preview your project
1. **Git**: the program to version control and publish your project to the TEC web site

This chapter will walk you step by step on how to publish a TEC document.
From preparing your laptop/desktop to editing, previewing, and eventually publish your project to the TEC website.

All you need to know is a few syntax on writing markdown text, a few commands
of hugo and git, and your content.

### First step

Before you start a new TEC project, contact the admin so they can create a GitLab repository for you.

Provide the following information:

1. title
1. description
1. type of the project: demo, workshop, xpert 2024, etc
1. who needs editing permission

### TL;DR

In summary, do the following:

1. Edit
1. Push to GitLab

   ```sh
   git commit -a -m "brief description of the editing"
   git push
   ```

1. Publish to TEC

   ```sh
   git tag v1.0.0
   git push origin v1.0.0
   ```

1. Go back to step 1 and use a new tag
