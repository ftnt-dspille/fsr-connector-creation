---
title: "Create a New Connector"
linkTitle: "Create Connector"
description: "Use the RDK wizard to scaffold a new connector project and explore the generated files."
weight: 1
---

In this chapter you'll use the RDK to create a brand-new connector project, explore the files it generates, and take a quick look at the Dad Joke API we'll be connecting to.

---

## 1. Meet the API

Before writing any code, let's see what we're working with. Open a terminal and run:

```bash
curl -H "Accept: application/json" https://icanhazdadjoke.com/
```

You should get back something like:

```json
{
  "id": "R7UfaahVfFd",
  "joke": "My dog used to chase people on a bike a lot. It got so bad I had to take his bike away.",
  "status": 200
}
```

That's the entire API response for a random joke - an `id`, the `joke` text, and a `status` code. Simple, clean, and perfect for learning.

{{% notice tip %}}
You can also paste `https://icanhazdadjoke.com/` into a browser. By default it returns HTML, but the JSON response is what our connector will work with.
{{% /notice %}}

---

## 2. Open the New Connector wizard

1. Open **PyCharm** with the RDK plugin installed.
2. Click **FortiSOAR RDK** from the toolbar menu at the top.
3. Select **Create New FortiSOAR Connector**.

<!-- ![img.png](images/rdk_create_new_menu.png) -->

The **New FortiSOAR Connector** dialog appears.

---

## 3. Fill in the connector details

Enter the following values in the dialog:

| Parameter | Value | Notes |
|---|---|---|
| **Display Name** | `Dad Jokes` | The name users see in FortiSOAR. |
| **API Name** | `dad-jokes` | Auto-generated from the display name. Must be unique. |
| **Version** | `1.0.0` | Semantic versioning (`major.minor.patch`). |
| **Description** | `Fetches dad jokes from the icanhazdadjoke.com API.` | Shown on the connector listing page. |

<!-- ![img.png](images/new_connector_dialog.png) -->

Click **OK**.

{{% notice warning %}}
The **API Name** cannot match any existing Content Hub connector and cannot be changed later. Choose carefully.
{{% /notice %}}

---

## 4. Fill in the Details tab

After the wizard creates the project, the RDK opens the **Details** tab. Update these optional fields:

| Parameter | Value |
|---|---|
| **Publisher** | Your name or email (e.g., `Workshop Student`). |
| **Category** | Select **Utilities** from the dropdown. |

<!-- ![img.png](images/details_tab_filled.png) -->

Click **Save**.

---

## 5. Explore the generated project

Your project explorer now shows the connector scaffold:

```text
connector-dad-jokes/
├── info.json              ← Connector metadata, configuration, and operations
├── connector.py           ← Main connector class (execute, check_health)
├── operations.py          ← Operation function stubs
├── images/                ← Connector logo files
│   ├── small_icon.png
│   └── large_icon.png
├── playbooks/             ← Sample playbooks (generated later)
├── tests/                 ← Unit test files
├── docs/                  ← Generated documentation (later)
└── requirements.txt       ← Python dependencies
```

Let's look at the two most important files.

### info.json

Open `info.json` in the editor. Right now it contains the metadata you entered plus empty `configuration` and `operations` sections:

```json
{
    "name": "dad-jokes",
    "version": "1.0.0",
    "label": "Dad Jokes",
    "description": "Fetches dad jokes from the icanhazdadjoke.com API.",
    "publisher": "Workshop Student",
    "category": ["Utilities"],
    "configuration": {
        "fields": []
    },
    "operations": []
}
```

We'll populate `configuration` and `operations` in the next two chapters.

### connector.py

Open `connector.py`. This is the entry point FortiSOAR calls when your connector runs:

```python
from connectors.core.connector import Connector


class DadJokes(Connector):

    def execute(self, config, operation, params, **kwargs):
        """Called when FortiSOAR runs any operation."""
        pass

    def check_health(self, config):
        """Called when FortiSOAR tests the configuration."""
        pass
```

Two methods, two jobs:

- `execute` - routes to the correct operation function when a playbook calls the connector.
- `check_health` - verifies that the configuration works (we'll make it ping the API).

---

## 6. Quick reference - Details tab actions

The Details tab has several action buttons at the bottom. Here's what they do:

| Action | What it does | When to use |
|---|---|---|
| **Save** | Writes your changes to `info.json`. | After every change. |
| **Generate Playbooks** | Creates sample playbooks from your operations. | After defining all operations. |
| **Generate Documents** | Creates HTML/MD docs from your descriptions. | Before exporting. |
| **Validate Connector** | Checks naming, descriptions, icons, etc. Outputs an HTML report. | Before exporting. |
| **Install Requirements** | Installs packages from `requirements.txt`. | When adding dependencies. |
| **Export** | Packages the connector as a `.tgz` file. | When ready to deploy. |

---

## Summary

You now have a connector project scaffolded and ready to build on:

- ✅ Created the **Dad Jokes** connector via the RDK wizard
- ✅ Filled in the Details tab (publisher, category)
- ✅ Explored the generated file structure
- ✅ Reviewed `info.json` and `connector.py`
- ✅ Confirmed the Dad Joke API works with a quick `curl` test

In the next chapter, you'll add **configuration parameters** so the connector knows which server to talk to.
