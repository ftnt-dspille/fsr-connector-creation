---
title: "Ways to Build Connectors"
linkTitle: "Ways to Build Connectors"
weight: 20
description: "Connector development options in FortiSOAR"
---

FortiSOAR provides two primary ways to build connectors. Both have the same result in generating a connector, but they are optimized for different use cases.

## Connector Wizard (UI-based)

The Connector Wizard is a guided, in-product designed to help users quickly create and test connectors directly within FortiSOAR. It is best suited for learning, prototyping, and straightforward REST integrations.
![img.png](connector_wizard.png?height=500px)

## FortiSOAR RDK (PyCharm Plugin)

The FortiSOAR RDK enables full local development of connectors using PyCharm. This workflow is intended for production-grade connectors that require complex logic, faster development iteration cycles, and stronger version control.
![img.png](create_connector_rdk_step1.png)
## Comparison

| Category                  | Connector Wizard                         | FortiSOAR RDK                  |
|:--------------------------|------------------------------------------|--------------------------------|
| Primary use               | Prototyping, simple integrations         | Production, complex connectors |
| Development environment   | FortiSOAR UI                             | Local IDE (PyCharm 2024.1+)    |
| Code editing              | Web editor                               | Full IDE                       |
| Debugging                 | None                                     | Full debugging                 |
| Code complexity           | Low–moderate                             | Moderate–high                  |
| Version control           | Manual / export-based                    | Native Git                     |
| Team collaboration        | Limited                                  | Strong                         |
| Testing                   | In-instance                              | IDE-driven                     |
| AI-assisted development   | FortiAI for new connectors, not existing | Supported (BYO AI)             |
| Setup effort              | Minimal                                  | Moderate                       |
| Long-term maintainability | Limited                                  | High                           |

{{% notice note %}}
These approaches are **not mutually exclusive**. You can start with the Wizard to create a connector, and then import it into the RDK for full development capabilities. Or vice versa.
{{% /notice %}}

You will get to use both approaches in this workshop. 

