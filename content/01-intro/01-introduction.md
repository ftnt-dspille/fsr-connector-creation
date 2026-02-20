---
title: "What are Connectors?"
linkTitle: "What are Connectors?"
weight: 10
---

# TODO
continue this page

## What is a FortiSOAR Connector?

A **connector** is an integration that allows FortiSOAR to communicate with external tools, services, and platforms. Connectors are how FortiSOAR talks to other products to support the following:

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

## Hands on

- Navigate to the public Content Hub and explore the connectors available https://fortisoar.contenthub.fortinet.com/list.html?contentType=all
- Click the different tabs to filter for specific content (Solutions Packs, Connectors, and Widgets)
  ![img.png](content_hub_filters.png)
- How many connectors are available?
- Search for a product you've worked with in the past. What "Actions" does it have out of the box?

