---
title: "Connector Contents Simplified"
linkTitle: "Connector Contents - Simple"
weight: 30
description: "Description"
---

# TODO

## Prerequisites

- Understanding of basic file structure
- Understanding of JSON format of files

## Common Connector Components

Most connectors consist of these 2 compoents

### Configuration Section UI

> Example connector configuration section

![img.png](alienvault_connector_configuration.png?height=400px)

- Stores reusable connection details (URL, credentials, SSL verify, tcp port)
    - **API Key**: Pass key in header or query parameter
    - **Basic Auth**: Username/password
    - **OAuth**: Token-based authentication
- Supports Multiple configurations per connector (dev, prod, different regions)
    - You can click "**Add Configuration**" to add additional configurations as needed
    - This is useful if you need have mulitple of the same product that you need to connect to
- Health check validates configuration
    - The health check helps you confirm that the connector is able to connect to the external API
  > example health check

![img.png](successful_health_check.png)

### Operations Section UI

- Each action is a separate operation (get_ip_reputation, block_domain)
- Operations are able to use configurations to authenticate to external systems
- Operations typically have parameters which are the input to the operation.
- Operations typically returns json back to the user which can be used to build dynamic playbooks

### Hands on

TODO - clean up

Find your favorite connector on the content hub in the discover tab. Install the connector. Analyze what fields are required to configure the connector. Analyze what actions are available to run the connector.

Edit the connector, go to the info.json file. What similarities do you see? 
