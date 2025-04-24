---
title: Document Content and Folder Layout
menuTitle: Document Content
weight: 20
---

In your project, there is a **content** folder. This is your main working folder. All of your documents, images, files and sub-folders go into this folder.

{{%notice tip%}}
The browser will automatically updates the preview once your save your changes in VSCode. So have your browser and VSCode side by side.
{{%/notice%}}

{{%notice warning%}}
After published, the production server is going to replace all other files execept those in **content** folder. So if you have global js, css, image or data files, they will not be available.

Move images into content folder.

If you want to add hugo functionality or plugins, contact Jingshao.
{{%/notice%}}

## Content Folder Structure

All contents of the documents are in the **content** folder. You can create sub-folders
and they will become chapters.

Each folder including the **content** folder needs an **\_index.md** file. That is the first page when people see the chapter. You can have as many **.md** files and as many sub-folders as you want.

A typical layout of the files and folders in the **content** folder looks like this:

```text
content
├── _index.md
├── chapter-01
│   ├── _index.md
│   ├── 01-intro-page.md
│   ├── 02-config-network-page.md
│   ├── 03-check-result-page.md
│   ├── figure_a.png
│   ├── figure_b.png
│   ├── config_file.cfg
│   └── other_downloadable_files
└── chapter-02
    ├── _index.md
    ├── 01-page.md
    ├── 02-page.md
    └── 03-page.md
```

You can name your folder and file whatever you want, except for `_index.md` file.

## Meta Data in Each Markdown File

At the top of each markdown file, you have to add a section of meta data (also called front matter):

```yaml
---
title: Chapter One Home page
menuTitle: Ch 1 home page
weight: 10
---
```

The fields are:

1. **title**: This is the page title that will be displayed at the top of the page.
1. **menuTitle**: This is the menu label for this page that is displayed at the left side navigation panel.
1. **weight**: this is a number indicating the order of this page. If 2 pages are of the same weight, the order is decided by their file name.

## Images and Attachments

You can add images and downloadable files to the **content** folder or the chapter folder.

In the markdown file, you can reference them as:

- Images:

  ```markdown
  ![image title](your_image_file_name_here)
  ```

- Downloads:

  ```markdown
  [download link text](your_download_file_name_here)
  ```

  You can also use the `download` short code to create a download link. Some files for example .csv will be automatically displayed in the browser. The download short code creates a link with download attribute to tell the browser to download instead of displaying it:

  ```go
   The csv file can be downloaded
   {{</* download "patches/test.csv" */>}}here{{</* /download */>}}
  ```

  Check the [document]({{% relref 06-download-link %}})
  for more details.

{{%notice warning%}}
The build code in TEC will remove the `images` folder from the top level directory. So avoid putting your images into the top level `images` folder, `static` folder or the `assets/images` folder. It will work with your preview, but disappear after published.

As a simple rule, put all your content under the **content** folder.
{{%/notice%}}

Normally you can save the file in the same folder with the markdown file, so you don't need to prepend path to the file name. (use **(your_file_name)** instead of **(images/your_file_name)**)
