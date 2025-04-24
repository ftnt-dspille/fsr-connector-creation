---
title: Add Carousel to the Document
menuTitle: Carousel
weight: 40
# for carousel
carousel:
  - image: building.jpg
    caption: Building
  - image: lab.jpg
  - image: meeting.png
    caption: Meeting
  - image: plaza.jpeg
    caption: Open Space
  - image: work.jpg
    caption: Work

carousel2:
  - image: lab.jpg
    caption: Lab
  - image: meeting.png
    caption: Meeting
---

{{% notice info %}}
If your local preview runs into error with this feature, follow the two steps
outlined in section [Upgrade](../chapter-01-start/05-upgrade.html) in chapter 1.
{{% /notice %}}

### The Front Matter YAML

To add carousel effects to a page, you will need to add the following code in the front matter yaml part at the top of the md file:

```yaml
---
title: ...
menuTitle: ...
weight: ...

# Add the following for carousel effects with 5 images
carousel:
  - image: building.jpg
    caption: Building
  - image: lab.jpg
    # The caption field is optional
    # caption: Lab
  - image: meeting.png
    caption: Meeting
  - image: plaza.jpeg
    caption: Open Space
  - image: work.jpg
    caption: Work

----
```

### The image field

Here, the `image` field is the relative url of the image files. Remember we don't put images in
global folder, the simplest way is just put the images in the same folder of the .md file. then
you can just use the image's file name as the value.

Or if you want to be more organized, you can create an folder called `images` in the same folder
as the .md file, and put all images in there. Then the value of the `image` field should be something
like `images/image1_file_name`, `images/image2_file_name`, etc.

{{% notice info %}}

When adding carousel in `_index.md` file, you have to prepend the folder to the image name. For example, if the `_index.md` file is under folder `chapter-02-markdown`, and the image is called `building.jpg` under the same folder, then the value of the image field should be
`chapter-02-markdown/building.jpg`.

{{% /notice %}}

### Add Short Code

Then you can put this short code in your page:

```html

{{</* carousel */>}}

```

{{< carousel >}}

### Available options

You can specify `width` and `height` for carousel's size.

## Multiple Carousels

If you want to have multiple carousels on one page, add them with different names
in the front matter section:

```yaml
carousel2:
  - image: lab.jpg
    caption: Lab
  - image: meeting.png
    caption: Meeting
```

Then you can refer it with `name`, make sure it matches the name defined in
the front matter:

```html
{{</* carousel name="carousel2"*/>}}
```

{{< carousel name="carousel2">}}
