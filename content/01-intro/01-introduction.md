---
title: "What are Connectors?"
linkTitle: "What are Connectors?"
weight: 10
---

# TODO
continue this page

## What is a FortiSOAR Connector?

A **connector** is a Python-based integration that allows FortiSOAR to communicate with external tools, services, and platforms. Think of connectors as bridges that let FortiSOAR:

- Fetch data from security tools (threat intelligence feeds, SIEMs, firewalls)
- Perform actions on external systems (block IPs, create tickets, quarantine endpoints)
- Ingest security events and alerts automatically (through playbooks)
- Enrich indicators with additional context

For example, a VirusTotal connector lets FortiSOAR check file hashes against VirusTotal's database, enriching your threat intelligence without manual lookups.

## Why Build Custom Connectors?

While FortiSOAR provides 700+ pre-built connectors, you might need a custom connector when:

- You're integrating with a proprietary or internal tool
- You need specific functionality not available in existing connectors (e.g., a connectors missing actions)
- You want to combine multiple API calls into a single action
- Your organization has unique integration requirements

## Check Your Understanding

Before proceeding, ensure you can answer:

1. What are the three main files in every connector?
2. What is the purpose of the `info.json` file?
3. Which development method requires PyCharm?
4. When would you choose manual development over the Connector Wizard?

{{% expand "Click to check your answers" %}}

1. **connector.py** (main class), **operations.py** (action implementations), and **info.json** (metadata/configuration)
2. The **info.json** defines the connector's metadata, configuration parameters, operations, and their input/output specifications
3. The **FortiSOAR RDK** is a PyCharm plugin
4. Choose **manual development** when you need full control, want to learn internals deeply, have complex logic that's hard to manage in web UI, or need to integrate with version control systems
   {{% /expand %}}

