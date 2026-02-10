---
title: "Connector Contents"
linkTitle: "Connector Contents"
weight: 30
description: "Description"
---

# TODO
continue this page

## Common Connector Components

Most connectors follow these established patterns:

### Configuration Pattern

- Store reusable connection details (URL, credentials)
- Multiple configurations per connector (dev, prod, different regions)
- Health check validates configuration

### Operations Pattern

- Each action is a separate operation (get_ip_reputation, block_domain)
- Operations share configuration
- Standard input/output format

### Authentication Patterns

- **API Key**: Pass key in header or query parameter
- **Basic Auth**: Username/password
- **OAuth**: Token-based authentication
- **Custom**: Signature generation, multi-factor auth

## Summary

In this module, you learned:

- ✓ Connectors are Python-based integrations that extend FortiSOAR's capabilities
- ✓ The standard connector architecture includes connector.py, info.json, and operations.py
- ✓ Three development methods: Manual (full control), Wizard (fast), RDK (professional)
- ✓ Data flows from playbooks through connector.py to operations.py to external APIs
- ✓ Understanding the architecture helps you build better, more maintainable connectors

**Next Steps:**

Ready to write some code? The next module covers essential Python concepts you'll need for connector development. Even if you know Python, we recommend reviewing it to see how specific patterns apply to FortiSOAR connectors.
