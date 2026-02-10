---
title: "Ways to Build Connectors"
linkTitle: "Ways to Build Connectors"
weight: 20
description: "Description"
---

# TODO
continue this page

FortiSOAR offers two development approaches, each with different trade-offs:

### Method 1: Connector Wizard

**Best for:** Quick prototypes, simple REST APIs, starting out with connectors

**Process:**

1. Open FortiSOAR
2. Navigate to Content Hub > Create > New Connector
3. Fill out UI forms for metadata, configuration, and actions
4. Use web editor for code customization
5. Publish directly from the UI

**Advantages:**

- No local development environment needed
- Testing in FortiSOAR

**Disadvantages:**

- Not ideal for complex logic
- Harder to version control
- Less suitable for team development

### Method 2: FortiSOAR RDK (PyCharm Plugin)

**Best for:** Professional development, team projects, complex connectors

**Process:**

1. Install RDK plugin in PyCharm
2. Create or import connector
3. Use IDE features (IntelliSense, debugging)
4. Test directly from PyCharm
5. Export when ready

**Advantages:**

- Full IDE capabilities (autocomplete, debugging, refactoring)
- Built-in testing and validation
- Best for maintaining large connectors
- Ability to use local AI agents for faster building (Bring your own AI required)

**Disadvantages:**

- Requires PyCharm (version 2024.1 or later)
- Pycharm learning curve
- Additional setup required

**For this workshop**, we'll use the Connector Wizard to understand the fundamentals and introduce the Pycharm Concepts.

{{% notice note %}}
You can switch between methods! Start with the Wizard to generate boilerplate, then export and continue manually if you need more control.
{{% /notice %}}