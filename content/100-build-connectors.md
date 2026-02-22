---
title: Building FortiSOAR Connectors Workshop
linkTitle: Build Connectors
weight: 100
---

## Lab Overview

**Duration:** 120 minutes  
**Difficulty:** Intermediate

**What You'll Learn:**

- Understand what connectors are and how they integrate third‑party tools with FortiSOAR.
- Learn essential Python concepts used in connectors, including HTTP requests and error handling.
- Create custom connectors using both the FortiSOAR web‑based Connector Wizard and the Rapid Development Kit (RDK) plug‑in for PyCharm.
- Build three connectors of increasing complexity: a basic “Advice” connector, a medium “Activities” connector and a more advanced “Pokémon” connector.
- Validate, debug and export/import connectors and use them within playbooks.

## Prerequisites

Before starting this workshop, ensure you have:

- A FortiSOAR instance (version 7.6.4 or later) with custom connector creation enabled.
- A role that permits creating and configuring connectors.
- PyCharm with the **FortiSOAR Rapid Development Kit (RDK)** installed.
- Python 3.8+ and the `requests` library available in your environment.
- Basic familiarity with REST APIs and JSON.

If you haven’t used FortiSOAR before, review the **Introduction to Connectors** section of the Connectors Guide to learn about permissions and how connectors integrate with the platform【239421472099449†L20-L35】.

---

## Part 1 – Understanding Connectors

### Overview

Connectors are FortiSOAR’s integration points with third‑party products. Each connector exposes
*operations* (actions) that can be used in playbooks to perform tasks such as lookups, creating tickets or retrieving threat intelligence. Custom connectors allow you to integrate services not available in the Content Hub. FortiSOAR provides several approaches for building a connector: using the web‑based
**Connector Wizard**, the AI‑assisted **FortiAI**, manually via the **Rapid Development Kit (RDK)** or by hand‑crafting the connector files【239421472099449†L20-L35】. In this workshop we focus on the Connector Wizard and the RDK plug‑in.

A connector is defined by two principal files:

- **info.json** – metadata describing the connector’s name, version, configuration fields and operations.
- **connector.py** and **operation files** – Python code that implements the `execute` and `check_health` functions and each operation. The base class for connectors extends `Connector` and provides these functions【239421472099449†L1248-L1260】.

When developing a connector you’ll also create optional files (playbooks, images and requirements) and bundle everything into a `.tgz` for import【239421472099449†L1315-L1331】.

### Key Components

| Component | Description | Purpose |
|-----------|-------------|---------|
| **Display Name / API Name** | The human‑friendly name and the internal variable name of the connector. | Distinguishes your connector in the UI and in code. |
| **Version** | Version in `x.y.z` format. | Enables multiple versions; must increment when updating. |
| **Description & Category** | Describes your connector and categorises it (Threat Intel, Ticketing, etc.). | Helps users understand the connector’s purpose. |
| **Configuration Fields** | Parameters that users must supply when configuring the connector (e.g., API token, base URL).  Supported field types include Text, Integer, Select, Checkbox, Password and JSON. | Allows the connector to be tailored to each environment. |
| **Operations** | Actions exposed by the connector; each operation has a display name, API name, HTTP method and optional endpoint. | Defines what the connector can do. |

### How It Works

1. **Connector creation** – In the Wizard or RDK you specify metadata (name, version, category).
2. **Add configuration fields** – Define the inputs needed to authenticate or parameterise API calls; mark fields as required or optional and select the appropriate data type.
3. **Add operations** – For each action, specify its title, API name, HTTP method and optional endpoint; add input parameters (arguments) if required.
4. **Implement code** – Write Python functions for each operation. The `execute` function maps the operation name to your function and returns its result【239421472099449†L1248-L1260】. Always implement `check_health` to verify configuration parameters.
5. **Validate and package** – Use the RDK’s **Validate Connector** to ensure naming conventions, descriptions and icons meet standards.
6. **Import and test** – Install the connector via Content Hub and use the operations in playbooks【239421472099449†L1463-L1492】. When a playbook step calls your connector, FortiSOAR passes a dictionary containing the configuration, parameters and selected operation【239421472099449†L1493-L1499】.

### Activity – Connector Scavenger Hunt

Spend a few minutes exploring your FortiSOAR instance:

1. Navigate to **Automation> Connectors**.
2. Locate a connector you use regularly (e.g., VirusTotal or FortiGate).
3. Click its **Actions & Playbooks** tab and note the operations available.
4. How might you extend this connector? Write down one new action you would like to add.

---

## Part 2 – Python Primer for Connector Developers

While connectors are configured through the UI, the underlying logic is written in Python. This section introduces the key language features needed to implement operations.

### Essential Concepts

- **Functions**: Operations are Python functions that accept configuration and input parameters and return a dictionary result. Define functions using `def` and return a Python dictionary (`dict`) to represent JSON.
- **Modules & Imports**: Place shared helper functions in separate modules (e.g., `util.py`) and import them using relative imports (`from .util import helper_function`)【239421472099449†L1266-L1271】.
- **HTTP Requests**: Use the popular `requests` library to call external APIs. A simple GET request looks like:
  
  ```python
  import requests

  def get_random_advice(config, params):
      base_url = config.get('base_url', 'https://api.adviceslip.com')
      response = requests.get(f'{base_url}/advice')
      response.raise_for_status()
      data = response.json()
      return {'slip': data['slip']['advice']}
  ```
  
  `response.raise_for_status()` raises an exception for non‑2xx responses; `requests` converts JSON responses into Python dictionaries.

- **Error Handling**: Wrap API calls in `try/except` blocks. When an error occurs, raise `ConnectorError` from `connectors.core.connector` to report a failure to FortiSOAR【239421472099449†L1463-L1473】.
  
  ```python
  from connectors.core.connector import ConnectorError

  try:
      response = requests.get(url, timeout=10)
      response.raise_for_status()
  except requests.exceptions.RequestException as e:
      raise ConnectorError(f'API request failed: {e}')
  ```

- **Mapping Operations**: In `connector.py` implement an `execute` method that maps operation names to functions【239421472099449†L1248-L1260】:
  
  ```python
  supported_operations = {
      'get_random_advice': get_random_advice,
      'get_activity': get_activity
  }

  def execute(self, config, operation, params, **kwargs):
      if operation not in supported_operations:
          raise ConnectorError(f'Unsupported operation: {operation}')
      return supported_operations[operation](config, params)
  ```

### Practice Exercise

Write a short script that fetches a random joke from the **Official Joke API** at `https://official-joke-api.appspot.com/jokes/programming/random`:

1. Open a Python REPL.
2. Use `requests.get` to call the URL and print the returned JSON.
3. Modify your code to extract and print the joke’s `setup` and `punchline`.

{{% expand "Need help? Click for a hint" %}}
Use `response.json()` to convert the response to a Python list and index `[0]` to access the first joke.
{{% /expand %}}

---

## Part 3 – Create Your First Connector: “Advice” (Basic)

### Overview

In this section you will build a simple connector that retrieves a random piece of advice from the **Advice Slip** API. This example introduces the core concepts of connector creation without any authentication or complex parameters.

### Task 3.1 – Define Connector Metadata

1. Open FortiSOAR and navigate to **Content Hub> Create> New Connector**.
2. On the *About Connector* screen, provide the following details:
   
   | Field | Value | Notes |
         |------|------|------|
   | **Connector Name** | Advice Connector | This is the display name shown in the UI. |
   | **API Identifier** | `advice_connector` | Must be alphanumeric and unique. |
   | **Version** | `1.0.0` | Semantic versioning is recommended. |
   | **Description** | Retrieves random life advice using the Advice Slip API. | Appears on the connector card. |
   | **Category** | Utilities | Helps users find your connector. |

3. (Optional) Leave **Publisher** as “Community”.

Click **Save & Continue** to proceed.

### Task 3.2 – Configure Fields

This API does not require authentication, but we’ll add a `base_url` field so users can override the API endpoint:

1. On the *Configuration* screen click **+ Add Field**.
2. In the form, set:
    
    - **Title:** Base URL
    - **Type:** Text
    - **API Name:** `base_url` (auto‑populated)
    - **Default Value:** `https://api.adviceslip.com`
    - **Required:** Yes

3. Click **Apply** then **Save & Continue**.

Fields named `name` or `default` are reserved and cannot be used【239421472099449†L114-L133】.

### Task 3.3 – Add the “Get Random Advice” Operation

1. On the *Actions* screen click **+ Action** to create an operation.
2. Under **Action Metadata** fill in:
    
    - **Title:** Get Random Advice
    - **Category:** Investigation (or another appropriate category)
    - **Description:** Fetches a random piece of advice from the Advice Slip API.

3. Under **Action Parameters** no fields are required because this operation needs no inputs.
4. Click **Save** to add the operation.

### Task 3.4 – Implement the Operation Code

If you are using the RDK plug‑in in PyCharm:

1. In PyCharm, click **FortiSOAR RDK> Create New FortiSOAR Connector** and supply the metadata above.
2. In the **Operations** tab, add a new operation with the API name `get_random_advice` and select **Generate default operation code**.
3. Open the generated `get_random_advice.py` file and replace the function body with the following:
   
   ```python
   import requests
   from connectors.core.connector import ConnectorError

   def get_random_advice(config, params):
       base_url = config.get('base_url', 'https://api.adviceslip.com')
       url = f'{base_url}/advice'
       try:
           resp = requests.get(url, timeout=10)
           resp.raise_for_status()
       except requests.exceptions.RequestException as exc:
           raise ConnectorError(f'API request failed: {exc}')
       data = resp.json()
       return {'advice': data['slip']['advice']}
   ```

4. Save the file and return to the **Execute** tab. Select your configuration and click **Run**.

**Expected Result:** A JSON response containing an `advice` key with a string value. For example:

```json
{
  "advice": "Don’t compare your life to others."
}
```

If you define an output schema, the RDK will display it in the **Captured Output Schema** section and allow you to save it.

### Task 3.5 – Practice Extension

Add a second operation called **Search Advice**:

1. Create a new operation with API name `search_advice`.
2. Under **Action Parameters** add one **Text** parameter named `query`.
3. Implement the function to call `f'{base_url}/advice/search/{query}'` and return a list of matching slips.
4. Test your function via the **Execute** tab.

{{% notice tip %}}
When you add arguments to an operation, use the **Required** attribute to enforce mandatory inputs and the **Visible** attribute to control whether a field appears in the playbook designer.
{{% /notice %}}

---

## Part 4 – Medium Complexity: “Activities” Connector

### Overview

The **Bored API** (`https://www.boredapi.com/api/activity`) provides random activities to cure boredom. In this exercise you will build a connector that retrieves activities and supports optional parameters.

### Task 4.1 – Set Up Metadata and Configuration

Create a new connector using the Wizard or RDK:

- **Name:** Activities Connector
- **API Identifier:** `activities_connector`
- **Version:** `1.0.0`
- **Category:** Utilities
- **Description:** Suggests random activities to reduce boredom.

Add a configuration field:

- **Title:** Base URL
- **API Name:** `base_url`
- **Type:** Text
- **Default Value:** `https://www.boredapi.com/api`
- **Required:** Yes

### Task 4.2 – Create the “Get Activity” Operation

Add an operation named **Get Activity** with API name `get_activity` and description “Returns a random activity; optionally filter by participants”.

Under **Action Parameters**, add one parameter:

| Property | Value |
|---|---|
| **Title** | Participants |
| **API Name** | `participants` |
| **Type** | Integer |
| **Description** | (Optional) Number of participants for the activity |

Do not mark it as required so users may leave it blank.

### Task 4.3 – Implement the Operation Code

In the generated `get_activity.py` file, replace the stub with:

```python
import requests
from connectors.core.connector import ConnectorError


def get_activity(config, params):
    base_url = config.get('base_url', 'https://www.boredapi.com/api')
    participants = params.get('participants')
    url = f'{base_url}/activity'
    if participants:
        url += f'?participants={participants}'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ConnectorError(f'Failed to fetch activity: {exc}')
    return resp.json()  # returns keys: activity, type, participants, price, link, key
```

Use the **Execute** tab to test the operation with and without the `participants` parameter. Verify that the output schema includes fields such as `activity`, `type`, `participants`, `price` and `link`.

### Task 4.4 – Knowledge Check

Answer these questions before moving on:

1. Why is it important to mark a configuration field or parameter as **required**?
2. What happens if your operation raises an unhandled Python exception?
3. How would you add an operation to search for activities by type (e.g., `"education"`)?

{{% expand "Check your answers" %}}

1. Required fields ensure users supply critical information; FortiSOAR will not allow the connector to run without these values.
2. Unhandled exceptions cause the connector to fail; raising `ConnectorError` allows FortiSOAR to record a clear error message【239421472099449†L1463-L1473】.
3. Add a `type` parameter, construct the URL with `?type=<value>` and return the JSON result; follow the same pattern as in Task 4.3.
   {{% /expand %}}

---

## Part 5 – Advanced Example: “Pokémon” Connector

### Overview

This connector demonstrates how to implement multiple operations, handle path parameters and parse API responses. It integrates with the **PokéAPI** (`https://pokeapi.co/api/v2`) to fetch details about Pokémon and abilities.

### Task 5.1 – Define Metadata and Configuration

Create a new connector:

- **Name:** Pokémon Connector
- **API Identifier:** `pokemon_connector`
- **Version:** `1.0.0`
- **Category:** Utilities
- **Description:** Retrieves information about Pokémon species and abilities.

Add a configuration field:

- **Title:** Base URL
- **API Name:** `base_url`
- **Type:** Text
- **Default Value:** `https://pokeapi.co/api/v2`
- **Required:** Yes

### Task 5.2 – Implement the “Get Pokémon Info” Operation

Create an operation with:

- **Title:** Get Pokémon Info
- **API Name:** `get_pokemon_info`
- **Description:** Returns basic information about a Pokémon by name.

Add one **Text** parameter named `pokemon_name` and mark it **Required**.

In `get_pokemon_info.py` implement:

```python
import requests
from connectors.core.connector import ConnectorError


def get_pokemon_info(config, params):
    base_url = config.get('base_url', 'https://pokeapi.co/api/v2')
    name = params.get('pokemon_name')
    if not name:
        raise ConnectorError('pokemon_name is required')
    url = f'{base_url}/pokemon/{name.lower()}'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ConnectorError(f'Error retrieving Pokémon: {exc}')
    data = resp.json()
    # extract selected fields
    types = [t['type']['name'] for t in data['types']]
    abilities = [a['ability']['name'] for a in data['abilities']]
    return {
        'id': data['id'],
        'name': data['name'],
        'height': data['height'],
        'weight': data['weight'],
        'types': types,
        'abilities': abilities
    }
```

### Task 5.3 – Implement the “Get Ability Info” Operation

Create another operation:

- **Title:** Get Ability Info
- **API Name:** `get_ability_info`
- **Description:** Retrieves details about a specific Pokémon ability.

Add one **Text** parameter named `ability_name` (required). Implement the following in `get_ability_info.py`:

```python
import requests
from connectors.core.connector import ConnectorError


def get_ability_info(config, params):
    base_url = config.get('base_url', 'https://pokeapi.co/api/v2')
    ability = params.get('ability_name')
    if not ability:
        raise ConnectorError('ability_name is required')
    url = f'{base_url}/ability/{ability.lower()}'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        if resp.status_code == 404:
            raise ConnectorError(f'Ability {ability} not found')
        raise ConnectorError(f'HTTP error: {exc}')
    except requests.exceptions.RequestException as exc:
        raise ConnectorError(f'Error retrieving ability: {exc}')
    data = resp.json()
    effect_entries = [e['effect'] for e in data['effect_entries'] if e['language']['name'] == 'en']
    return {
        'id': data['id'],
        'name': data['name'],
        'effect': effect_entries[0] if effect_entries else ''
    }
```

### Task 5.4 – Test and Save Output Schemas

Use the **Execute** tab to test both operations. Try values such as `pikachu`, `bulbasaur` or `overgrow`. Save the captured output schemas for each operation using **Save Output Schema
** to ensure the connector’s info.json reflects the structure of your return objects. This facilitates mapping dynamic values in playbooks.

### Task 5.5 – Challenge

Create a third operation called **List Pokémon Types** that returns the list of available Pokémon types (`GET /type`). Use no input parameters and parse the `results` array to return only the names of the types.

{{% notice note %}}
The **execute** method in `connector.py` must be updated whenever you add new operations. Map the API names (`get_pokemon_info`, `get_ability_info`, `list_pokemon_types`) to their respective functions【239421472099449†L1248-L1260】.
{{% /notice %}}

---

## Part 6 – Using the Rapid Development Kit (RDK) Plug‑in

### Overview

The FortiSOAR Rapid Development Kit plug‑in for PyCharm streamlines connector development. Once installed, it provides a **FortiSOAR RDK** menu and tool window that allow you to create connectors, add configuration fields and operations, run unit tests, validate and export connectors.

### Key Features

- **Create New Connector / Import Connector:** Launches dialogs to create a new connector or import an existing `.tgz`.
- **Details Tab:** View and edit metadata (publisher, documentation URL, category, logo) and generate sample playbooks and documentation.
- **Configuration Tab:** Add configuration parameters; mark them required, visible or conditional.
- **Operations Tab:** Create operations, add arguments and generate default operation code.
- **Validation:** Runs a set of checks to ensure your connector meets best‑practice standards (at least one action, proper naming, descriptions, icons, etc.).
- **Export:** Packages your connector as a `.tgz` file for import into FortiSOAR.

### Task 6.1 – Create a Connector in PyCharm

1. Open your project in PyCharm and select **FortiSOAR RDK> Create New FortiSOAR Connector**.
2. Enter the metadata for one of your connectors (e.g., the Pokémon connector). Click **OK** to generate the project structure; the **info.json** file opens automatically.
3. Use the **Details** tab to set optional properties such as **Publisher**, **Category** and **Connector Logo**. Save your changes to update `info.json`.

### Task 6.2 – Add Configuration and Operations

1. On the **Configuration** tab click **Add Config Fields**. For each field complete the form and select attributes such as **Required**, **Visible** or **OnChange**. Click **Save** to write the configuration into `info.json`.
2. On the **Operations** tab click **Add New Operation** and specify the display name, API name, endpoint and HTTP method.
3. Use the **Arguments** tab to define input parameters and their attributes (required, visible, etc.).
4. Enable **Generate default operation code** to create the Python file for your operation. Then open the `.py` file and implement the logic as demonstrated in Parts 3–5.

### Task 6.3 – Run and Debug Operations

After saving a configuration or operation, PyCharm automatically generates run/debug configurations for health checks and operations:

1. Expand the connector folder in the Run/Debug drop‑down. You will see entries such as “<Connector Name>‑ Health Check” and “<Operation Name>”.
2. Select **Health Check** and click the Run or Debug icon to execute `check_health` with your saved configuration. Confirm that it returns `True`.
3. Select an operation configuration and run or debug it. Use breakpoints within your operation code to troubleshoot issues.

### Task 6.4 – Validate and Export

1. In the **Operations** tab click **Validate Connector** to ensure that your connector meets all quality checks (naming conventions, descriptions, playbooks not in Debug mode, correct icon sizes, etc.).
2. Click **Export** and choose a location to save the `.tgz` file.
3. Import the `.tgz` into your FortiSOAR instance via **Content Hub> Import**. When prompted, configure the connector using the same values you used for testing.

### Task 6.5 – Build a Playbook

Once imported, create a playbook to invoke your connector:

1. Navigate to **Automation> Playbooks** and create a new playbook.
2. Add a **Connector** step and select your connector and operation. Specify any input parameters.
3. Optionally add subsequent steps to process the result (e.g., parse the advice text or update a ticket).
4. Run the playbook and verify that the step executes successfully and returns the expected data【239421472099449†L1463-L1499】.

---

## Part 7 – Manual Connector Creation (Optional)

The Wizard and RDK simplify development, but you may sometimes need to build a connector manually (for example, when working without a GUI). Follow these steps【239421472099449†L736-L770】:

1. **Set up the directory structure** – create a folder named after your connector and add sub‑directories: `playbooks`, `images`, `packages`. Create the files `connector.py`, `info.json`, `requirements.txt` and `playbooks/playbooks.json`.
2. **Define `info.json`** – include fields for `name`, `label`, `version`, `publisher`, `category`, `configuration`, `operations` and optional `output_schema`【239421472099449†L772-L789】. See the sample in the guide for formatting details【239421472099449†L772-L805】.
3. **Implement `connector.py`** – extend the `Connector` class and implement `execute` and `check_health`【239421472099449†L1248-L1260】. Use additional lifecycle hooks (`on_add_config`, `on_update_config`, etc.) when needed【239421472099449†L1266-L1299】.
4. **Bundle dependencies** – list Python libraries in `requirements.txt` and place any custom packages in the `packages` directory【239421472099449†L1315-L1331】.
5. **Package** – create a `.tgz` file with `tar -czvf connector_name.tgz connector_name/`【239421472099449†L1315-L1331】.
6. **Import into FortiSOAR** – upload the `.tgz` via **Automation> Connectors** and configure the connector【239421472099449†L1344-L1368】.

Manual creation gives full control over the connector files but requires meticulous adherence to schema and naming conventions; minor errors often cause import failures.

---

## Part 8 – Troubleshooting and Best Practices

### Debugging Tips

- **Validate early:** Run **Validate Connector** frequently to catch issues such as missing descriptions or incorrect naming.
- **Check logs:** Connector logs are stored in `/var/log/cyops/cyops‑integrations/connectors.log`; use `logger = get_logger('<connector_name>')` to log messages【239421472099449†L1266-L1274】.
- **Handle errors gracefully:** Wrap API calls in `try/except` and raise `ConnectorError` with a descriptive message when something goes wrong【239421472099449†L1463-L1473】.
- **Use semantic versioning:** Increment your connector version whenever you make changes so playbooks can target specific versions【239421472099449†L1463-L1492】.
- **Write unit tests:** Use the RDK’s **Run Unit Test** feature to create tests for each operation; test files live in the `tests` folder and should be named `test_<operation>.py`.

### Best Practices

- Choose descriptive display names and API identifiers that reflect the functionality and avoid collisions with existing connectors.
- Provide meaningful descriptions and documentation URLs so other users understand what your connector does.
- Group related actions into one connector rather than creating multiple connectors for the same service.
- Keep configuration fields minimal and clearly indicate which fields are required.
- Test connectors thoroughly in a development environment before deploying to production.

---

## Verification and Summary

### Verification Checklist

Use this checklist to confirm your connectors are ready:

- [ ] The connector’s metadata (name, version, description) is complete and correctly defined.
- [ ] All configuration fields and operation parameters are defined with appropriate types and attributes.
- [ ] Each operation returns the expected output when tested via the **Execute** tab.
- [ ] Output schemas have been saved and are accurate.
- [ ] The connector passes the validation checks in the RDK.
- [ ] The exported `.tgz` imports successfully into your FortiSOAR instance【239421472099449†L1344-L1368】.
- [ ] Playbooks using the connector run without errors and return the correct data【239421472099449†L1463-L1499】.

### Lab Summary

In this workshop you:

- Learned how connectors integrate external services with FortiSOAR and explored key components like metadata, configuration fields and operations.
- Reviewed essential Python concepts for connector development, including functions, modules, HTTP requests and error handling.
- Built three connectors of increasing complexity using fun public APIs, implementing operations and handling parameters.
- Used the Rapid Development Kit plug‑in to streamline connector creation, test operations, validate quality and export connectors for import into FortiSOAR.
- Gained an introduction to manual connector creation, including the directory structure and required files.
- Practiced troubleshooting, debugging and applying best practices to ensure robust, maintainable connectors.

**Next Steps:
** Experiment with additional APIs or extend the connectors you built today (for example, add authentication, pagination or data ingestion). Explore FortiAI for AI‑assisted connector generation, and refer to the FortiSOAR Connectors Guide for advanced features such as updating connector configurations programmatically via
`update_connector_config`【239421472099449†L1514-L1549】.

---

{{% notice tip %}}
Continue your learning by exploring FortiSOAR playbooks and how connectors interact with orchestration workflows. Building custom connectors unlocks endless possibilities for automation within your SOC.
{{% /notice %}}