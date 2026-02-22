---
title: "Connector Contents Advanced"
linkTitle: "Connector Contents - In Depth"
weight: 40
description: "Description"
---

Now that you have an understanding of the UI components to a connector, let's take a look at the connector file structure, and how the UI translates the the files that make up the connector.

## Prerequisites

From FortiSOAR version **7.6.4**, uploading, editing, and debugging connectors requires approval from **System Configurations**. This allows users to upload/create custom connectors and custom widgets.
![img.png](764_requirements_connectors.png?height=500px)

---

## Connector Structure

The basic structure of a connector is as follows:

```
connector/
├── info.json
├── connector.py
├── operations.py
```

## `info.json`

The `info.json` file contains information about the name and version of the connector, logo image file names, the configuration parameters, the set of functions supported by the connector, and their input parameters. **All field names in the `info.json` file must be unique.**

The file has **3 main parts**:

1. **Metadata** — Information about the connector (name, version, logo, etc.)
2. **Configuration** — Parameters used to set up the connector configuration page
3. **Operations** — Actions the connector can perform, with associated metadata and parameters

---

### 1. Metadata

Top-level keys containing information about the connector.

#### Essential Fields

| Field     | Description                                | Example              |
|-----------|--------------------------------------------|----------------------|
| `name`    | Connector's internal API name (kebab-case) | `"sample-connector"` |
| `label`   | Display label shown to the user            | `"Sample Connector"` |
| `version` | Semantic version number                    | `"1.0.0"`            |

#### All Metadata Fields

{{% expand title="Expand me..." %}}

| Field             | Description                        | Example                      |
|-------------------|------------------------------------|------------------------------|
| `name`            | Connector's internal name          | `"sample-connector"`         |
| `label`           | Display label for the connector    | `"Sample Connector"`         |
| `description`     | Description of the connector       | `"Connector description..."` |
| `publisher`       | Name/email of the publisher        | `"anonyges@gmail.com"`       |
| `cs_approved`     | Whether connector is CS approved   | `true` / `false`             |
| `cs_compatible`   | Whether connector is CS compatible | `true` / `false`             |
| `version`         | Version number                     | `"1.0.0"`                    |
| `category`        | Connector category type (array)    | `["Analytics and SIEM"]`     |
| `icon_small_name` | Filename of the small icon         | `"connector_logo_small.png"` |
| `icon_large_name` | Filename of the large icon         | `"connector_logo_large.png"` |

{{% /expand %}}

{{

#### Example

```json
{
  "name": "sample-connector",
  "version": "1.0.0",
  "label": "Sample Connector",
  "description": "Connector description here.",
  "publisher": "anonyges@gmail.com",
  "icon_large_name": "connector_logo_large.png",
  "icon_small_name": "connector_logo_small.png",
  "category": [
    "Analytics and SIEM"
  ]
}
```

> **Naming Convention:**
> - Title: `"Sample Connector"` → `"Organization ProductName"`
> - API name: `"sample-connector"` → `"org-productName"`

---

### 2. Configuration

`info.json` > `configuration` (dict)

Contains the configuration parameters used to set up the connector configuration page.
![img.png](configuration_details.png?height=500px)

#### Field Structure

Each field in the `configuration.fields` array can include the following key-value pairs:

{{% expand title="Expand me..." %}}

| Key           | Type    | Description                                                                                                                                              |
|---------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `title`       | string  | Display name of the field                                                                                                                                |
| `name`        | string  | Internal field identifier                                                                                                                                |
| `type`        | string  | Field type (e.g., : text, password, checkbox, integer, decimal, datetime, phone, email, file, richtext, json, textarea, image, select, and multiselect.) |
| `required`    | boolean | Whether the field is mandatory                                                                                                                           |
| `editable`    | boolean | Whether the user can edit the field                                                                                                                      |
| `visible`     | boolean | Whether the field is visible                                                                                                                             |
| `description` | string  | Field description                                                                                                                                        |
| `tooltip`     | string  | Tooltip text                                                                                                                                             |
| `placeholder` | string  | Placeholder text                                                                                                                                         |
| `validation`  | object  | Validation rules (see below)                                                                                                                             |

{{% /expand %}}

#### Validation Object

```json
{
  "pattern": "regex pattern for validation",
  "patternError": "Error message if validation fails"
}
```

#### Example

```json
{
  "configuration": {
    "fields": [
      {
        "title": "URL",
        "type": "text",
        "name": "url",
        "required": true,
        "visible": true,
        "editable": true,
        "validation": {
          "pattern": "^https?://...",
          "patternError": "Server URL must begin with https and end without '/'. Port number can be added, e.g. https://example.com:80."
        }
      }
    ]
  }
}
```

---

### 3. Operations

`info.json` > `operations` (list of dicts)

Contains the actions that the connector can perform and their associated metadata and parameters. Operations map to playbook actions.

![img.png](operation_to_connector.png?height=500px)

Inside a playbook, the operations are used to display the available actions, the the parameters used
![img.png](operatio_to_playbook.png?height=500px)

#### Operation Structure

| Key           | Type    | Description                            |
|---------------|---------|----------------------------------------|
| `operation`   | string  | Internal operation identifier          |
| `title`       | string  | Display name of the operation          |
| `description` | string  | Description of what the operation does |
| `parameters`  | array   | Input parameters for the operation     |
| `enabled`     | boolean | Whether the operation is active        |

#### Parameter Structure

Each parameter in the `parameters` array follows the same structure as configuration fields:

| Key        | Type    | Description                        |
|------------|---------|------------------------------------|
| `title`    | string  | Display name                       |
| `name`     | string  | Internal identifier                |
| `type`     | string  | Field type (e.g., `"text"`)        |
| `required` | boolean | Whether the parameter is mandatory |
| `visible`  | boolean | Whether the parameter is visible   |
| `editable` | boolean | Whether the user can edit it       |
| `value`    | string  | Default value                      |
| `tooltip`  | string  | Tooltip text                       |

#### Example

```json
{
  "operations": [
    {
      "operation": "do_something",
      "title": "Do Something",
      "description": "Do Something and Returns Something.",
      "parameters": [
        {
          "title": "something",
          "type": "text",
          "name": "something",
          "required": true,
          "visible": true,
          "editable": true,
          "value": "",
          "tooltip": "hello world"
        }
      ],
      "enabled": true
    }
  ]
}
```

{{% notice note %}}
Parameters are not always required for operations, but are often needed to allow users to filter data, or take specific action on data.
{{% /notice %}}

### Full `info.json` Example

{{% expand title="Expand me..." %}}

```json
{
  "name": "sample-connector",
  "version": "1.0.0",
  "label": "Sample Connector",
  "description": "Naming convention.\nTitle should be change from \"Sample Connector\" --> \"Organization ProductName\"\nAPI name should change from \"sample-connector\" --> \"org-productName\"",
  "publisher": "anonyges@gmail.com",
  "icon_large_name": "connector_logo_large.png",
  "icon_small_name": "connector_logo_small.png",
  "category": [
    "Analytics and SIEM"
  ],
  "configuration": {
    "fields": [
      {
        "title": "URL",
        "type": "text",
        "name": "url",
        "required": true,
        "visible": true,
        "editable": true,
        "validation": {
          "pattern": "^https?:\\/\\/...",
          "patternError": "Server URL must begin with https and end without '/'. Port number can be added, e.g. https://example.com:80."
        }
      }
    ]
  },
  "operations": [
    {
      "operation": "do_something",
      "title": "Do Something",
      "description": "Do Something and Returns Something.",
      "parameters": [
        {
          "title": "something",
          "type": "text",
          "name": "something",
          "required": true,
          "visible": true,
          "editable": true,
          "value": "",
          "tooltip": "hello world"
        }
      ],
      "enabled": true
    }
  ]
}
```

{{% /expand %}}