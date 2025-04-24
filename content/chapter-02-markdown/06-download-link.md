---
title: Download Links
weight: 60
---

## Download Link on Page

{{% notice info %}}
If your local preview runs into error with this feature, follow the two steps
outlined in section [Upgrade](../chapter-01-start/05-upgrade.html) in chapter 1.
{{% /notice %}}

To add a download link, use the `{{</*download*/>}}` shortcode:

Usages:

- With inner text:

  ```text
   The csv file can be downloaded
   {{</* download "patches/test.csv" */>}}here{{</* /download */>}}
  ```

  **Rendered output:**

  The csv file can be downloaded
  {{<download "patches/test.csv">}}here{{</download>}}

- If there is no inner text, the download href will be used:

  ```text
  Download the csv file: {{</* download "patches/test.csv" /*/>}}
  ```

  **Rendered output:**

  Download the csv: {{< download "patches/test.csv" />}}

## Download Link on Side Menu

If you want to have a download link on the side menu, you need to add a
`[[menu.shortcuts.params]]`

Example:

```toml
[[menu.shortcuts]]
name = "<i class='fas fa-download'></i> Download Test CSV"
url = "/chapter-02-markdown/patches/test.csv"
weight = 5
[[menu.shortcuts.params]]
download = true
```
