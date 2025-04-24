---
title: Edit Hugo Config File
menuTitle: Config Document
weight: 10
---

The first thing you want to do is to edit the config file
**config.toml**. This file contains some overall configurations of your project. You probably just need to edit this file once.

Open **config.toml** in VSCode by clicking its name in the left side panel.

## Must Change

Under section **[params]**, you must change these lines:

- **title = "..."**
- **author = "..."**
- **description = "..."**

## Pick a Theme

Now pick a theme by setting the **themeVariant**:

- **themeVariant**
  These are predefined Fortinet color themed variants:
  - `Demo`:
    A green color theme:
    ![Demo](demo.png?width=256px)
  - `Spotlight`:
    A purple color theme:
    ![Spotlight](spotlight.png?width=256px)
  - `UseCase`:
    A blue color theme:
    ![UseCase](usecase.png?width=256px)
  - `Workshop`:
    A red color theme:
    ![Workshop](workshop.png?width=256px)
  - `Xperts2023`:
    A special color theme for Xperts 2023:
    ![Xperts2023](xperts2023.png?width=256px)
  - `Xperts2024`:
    A special color theme for Xperts 2024:
    ![Xperts2024](xperts2024.png?width=256px)

## Helpful Resources Links

Defined in sections called `[[menu.shortcuts]]`. They are the links
corresponding to the left side _HELPFUL RESOURCES_ sections.

![shortcuts](menu-shortcuts.png?width=256px)

Leave the single page view for printing as is. Add more like this (weight determines the order, from small to large.):

```toml
[[menu.shortcuts]]
name = "<i class='fas fa-tools'></i> User Guide"
url = "https://tec.myfortinet.com/user-guide/"
weight = 11
```

## Other things to change

- **logoBannerText** This is the banner text under Fortinet logo
