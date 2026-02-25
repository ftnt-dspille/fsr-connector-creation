---
title: "Add Operations"
linkTitle: "Add Operations"
description: "Define three operations - Get Random Joke, Get Joke by ID, and Search Jokes - with parameters, and write the Python code that powers them."
weight: 3
---

Operations are the actions your connector exposes to FortiSOAR playbooks. In this chapter you'll create three operations, define their input parameters, and write the Python functions that call the Dad Joke API.

---

## 1. Plan the operations

Here's what we're building, mapped to the API endpoints:

| Operation | API Endpoint | Parameters | Returns |
|---|---|---|---|
| **Get Random Joke** | `GET /` | *(none)* | A random joke with `id` and `joke` |
| **Get Joke by ID** | `GET /j/<joke_id>` | `joke_id` (required) | A specific joke |
| **Search Jokes** | `GET /search?term=<query>` | `search_term` (required), `limit` (optional) | A list of matching jokes |

---

## Operation 1 - Get Random Joke

### Add the operation in the RDK

1. In the RDK panel, click the **Operations** tab.
2. Click **Add Operation**.
3. Fill in the following:

| Property | Value |
|---|---|
| **Title** | `Get Random Joke` |
| **API Name** | `get_random_joke` (auto-generated) |
| **Description** | `Fetches a random dad joke from the API.` |
| **Enabled** | ✅ Checked |

This operation has **no parameters** - it just returns a random joke.

Click **Save**.

<!-- ![img.png](images/op_get_random_joke.png) -->

### Verify in info.json

Open `info.json` and confirm the operation appears in the `operations` array:

```json
{
    "operations": [
        {
            "operation": "get_random_joke",
            "title": "Get Random Joke",
            "description": "Fetches a random dad joke from the API.",
            "parameters": [],
            "enabled": true
        }
    ]
}
```

### Write the Python function

Open `operations.py` and add the following function below `check_health`:

```python
def get_random_joke(config, params):
    """Fetch a random dad joke."""
    return _make_request(config)
```

That's it - one line. The `_make_request` helper already calls the base URL (`/`) which returns a random joke.

---

## Operation 2 - Get Joke by ID

### Add the operation in the RDK

1. Click **Add Operation** again.
2. Fill in:

| Property | Value |
|---|---|
| **Title** | `Get Joke by ID` |
| **API Name** | `get_joke_by_id` |
| **Description** | `Fetches a specific dad joke by its unique ID.` |
| **Enabled** | ✅ Checked |

### Add the parameter

This operation needs a **joke_id** parameter so the user can specify which joke to fetch.

1. In the operation you just created, click **Add Parameter**.
2. Fill in:

| Property | Value |
|---|---|
| **Title** | `Joke ID` |
| **API Name** | `joke_id` |
| **Type** | `Text` |
| **Required** | ✅ Checked |
| **Editable** | ✅ Checked |
| **Visible** | ✅ Checked |
| **Tooltip** | `The unique ID of the joke to retrieve (e.g., R7UfaahVfFd).` |

<!-- ![img.png](images/op_get_joke_by_id.png) -->

Click **Save**.

### Verify in info.json

```json
{
    "operation": "get_joke_by_id",
    "title": "Get Joke by ID",
    "description": "Fetches a specific dad joke by its unique ID.",
    "parameters": [
        {
            "title": "Joke ID",
            "type": "text",
            "name": "joke_id",
            "required": true,
            "editable": true,
            "visible": true,
            "tooltip": "The unique ID of the joke to retrieve (e.g., R7UfaahVfFd)."
        }
    ],
    "enabled": true
}
```

### Write the Python function

Add to `operations.py`:

```python
def get_joke_by_id(config, params):
    """Fetch a specific joke by its ID."""
    joke_id = params.get("joke_id")
    if not joke_id:
        raise ConnectorError("Joke ID is required.")
    return _make_request(config, endpoint=f"/j/{joke_id}")
```

Notice how we read the parameter: `params.get("joke_id")`. The key `"joke_id"` matches the **API Name** we set in the RDK. This is how FortiSOAR passes user input to your function.

---

## Operation 3 - Search Jokes

### Add the operation in the RDK

1. Click **Add Operation** one more time.
2. Fill in:

| Property | Value |
|---|---|
| **Title** | `Search Jokes` |
| **API Name** | `search_jokes` |
| **Description** | `Searches for dad jokes matching a keyword. Returns a paginated list of results.` |
| **Enabled** | ✅ Checked |

### Add the parameters

This operation needs two parameters - a required search term and an optional result limit.

**Parameter 1 - Search Term:**

1. Click **Add Parameter**.
2. Fill in:

| Property | Value |
|---|---|
| **Title** | `Search Term` |
| **API Name** | `search_term` |
| **Type** | `Text` |
| **Required** | ✅ Checked |
| **Editable** | ✅ Checked |
| **Visible** | ✅ Checked |
| **Tooltip** | `The keyword to search for (e.g., "cat", "hipster", "dog").` |

**Parameter 2 - Limit:**

1. Click **Add Parameter** again.
2. Fill in:

| Property | Value |
|---|---|
| **Title** | `Limit` |
| **API Name** | `limit` |
| **Type** | `Integer` |
| **Required** | ❌ Unchecked |
| **Editable** | ✅ Checked |
| **Visible** | ✅ Checked |
| **Default Value** | `20` |
| **Tooltip** | `Maximum number of results to return (1–30). Defaults to 20.` |

<!-- ![img.png](images/op_search_jokes.png) -->

Click **Save**.

### Verify in info.json

```json
{
    "operation": "search_jokes",
    "title": "Search Jokes",
    "description": "Searches for dad jokes matching a keyword. Returns a paginated list of results.",
    "parameters": [
        {
            "title": "Search Term",
            "type": "text",
            "name": "search_term",
            "required": true,
            "editable": true,
            "visible": true,
            "tooltip": "The keyword to search for (e.g., \"cat\", \"hipster\", \"dog\")."
        },
        {
            "title": "Limit",
            "type": "integer",
            "name": "limit",
            "required": false,
            "editable": true,
            "visible": true,
            "value": 20,
            "tooltip": "Maximum number of results to return (1-30). Defaults to 20."
        }
    ],
    "enabled": true
}
```

### Write the Python function

Add to `operations.py`:

```python
def search_jokes(config, params):
    """Search for jokes matching a keyword."""
    search_term = params.get("search_term")
    if not search_term:
        raise ConnectorError("Search Term is required.")

    query_params = {"term": search_term}

    limit = params.get("limit")
    if limit:
        query_params["limit"] = limit

    return _make_request(config, endpoint="/search", params=query_params)
```

Here the `params` dict from the `_make_request` helper gets passed as **query string parameters** - so `{"term": "cat", "limit": 5}` becomes `?term=cat&limit=5` in the URL.

---

## 2. Wire operations to connector.py

Now we need to tell `connector.py` how to route incoming operations to the correct function.

Open `connector.py` and replace its contents with:

```python
from connectors.core.connector import Connector
from .operations import (
    check_health,
    get_random_joke,
    get_joke_by_id,
    search_jokes,
)

# Map operation API names to their functions
OPERATION_MAP = {
    "get_random_joke": get_random_joke,
    "get_joke_by_id": get_joke_by_id,
    "search_jokes": search_jokes,
}


class DadJokes(Connector):

    def execute(self, config, operation, params, **kwargs):
        """Route to the correct operation function."""
        action = OPERATION_MAP.get(operation)
        if action:
            return action(config, params)
        raise ConnectorError(f"Unknown operation: {operation}")

    def check_health(self, config):
        return check_health(config)
```

{{% notice tip %}}
The `OPERATION_MAP` dictionary pattern is a clean way to route operations. The keys must match the **API Name** values in your `info.json` operations. When you add a new operation in the future, you just add one entry to the map and one function to `operations.py`.
{{% /notice %}}

---

## 3. Review the complete operations.py

Here's what your `operations.py` should look like with all the pieces together:

```python
import requests
from connectors.core.connector import ConnectorError


def _make_request(config, endpoint="", params=None):
    """
    Reusable helper for all Dad Joke API calls.

    Args:
        config:   Connector configuration dict.
        endpoint: URL path to append to the server URL (e.g., "/j/abc123").
        params:   Optional dict of query string parameters.

    Returns:
        dict: Parsed JSON response.

    Raises:
        ConnectorError: If the request fails.
    """
    url = f"{config['server_url']}{endpoint}"
    headers = {
        "Accept": "application/json",
        "User-Agent": config.get("user_agent", "FortiSOAR Connector")
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise ConnectorError(
            f"Cannot connect to {url}. Verify the Server URL."
        )
    except requests.exceptions.Timeout:
        raise ConnectorError(
            f"Request to {url} timed out after 30 seconds."
        )
    except requests.exceptions.HTTPError as e:
        raise ConnectorError(
            f"API error: {e.response.status_code} {e.response.reason}"
        )
    except Exception as e:
        raise ConnectorError(f"Unexpected error: {str(e)}")


def check_health(config):
    """Health check - fetch a random joke to verify connectivity."""
    result = _make_request(config)
    if result.get("id") and result.get("joke"):
        return True
    raise ConnectorError("Unexpected response. Check the Server URL.")


def get_random_joke(config, params):
    """Fetch a random dad joke."""
    return _make_request(config)


def get_joke_by_id(config, params):
    """Fetch a specific joke by its ID."""
    joke_id = params.get("joke_id")
    if not joke_id:
        raise ConnectorError("Joke ID is required.")
    return _make_request(config, endpoint=f"/j/{joke_id}")


def search_jokes(config, params):
    """Search for jokes matching a keyword."""
    search_term = params.get("search_term")
    if not search_term:
        raise ConnectorError("Search Term is required.")

    query_params = {"term": search_term}

    limit = params.get("limit")
    if limit:
        query_params["limit"] = limit

    return _make_request(config, endpoint="/search", params=query_params)
```

---

## 4. Review the complete info.json

And here's the full `info.json` with all metadata, configuration, and operations:

{{% expand "Click to view full info.json" %}}

```json
{
    "name": "dad-jokes",
    "version": "1.0.0",
    "label": "Dad Jokes",
    "description": "Fetches dad jokes from the icanhazdadjoke.com API.",
    "publisher": "Workshop Student",
    "icon_large_name": "large_icon.png",
    "icon_small_name": "small_icon.png",
    "category": [
        "Utilities"
    ],
    "configuration": {
        "fields": [
            {
                "title": "Server URL",
                "type": "text",
                "name": "server_url",
                "required": true,
                "editable": true,
                "visible": true,
                "value": "https://icanhazdadjoke.com",
                "tooltip": "Base URL of the Dad Joke API. Do not include a trailing slash."
            },
            {
                "title": "User-Agent",
                "type": "text",
                "name": "user_agent",
                "required": true,
                "editable": true,
                "visible": true,
                "value": "FortiSOAR Dad Jokes Connector (workshop)",
                "tooltip": "Custom User-Agent header sent with every request."
            }
        ]
    },
    "operations": [
        {
            "operation": "get_random_joke",
            "title": "Get Random Joke",
            "description": "Fetches a random dad joke from the API.",
            "parameters": [],
            "enabled": true
        },
        {
            "operation": "get_joke_by_id",
            "title": "Get Joke by ID",
            "description": "Fetches a specific dad joke by its unique ID.",
            "parameters": [
                {
                    "title": "Joke ID",
                    "type": "text",
                    "name": "joke_id",
                    "required": true,
                    "editable": true,
                    "visible": true,
                    "tooltip": "The unique ID of the joke to retrieve (e.g., R7UfaahVfFd)."
                }
            ],
            "enabled": true
        },
        {
            "operation": "search_jokes",
            "title": "Search Jokes",
            "description": "Searches for dad jokes matching a keyword. Returns a paginated list of results.",
            "parameters": [
                {
                    "title": "Search Term",
                    "type": "text",
                    "name": "search_term",
                    "required": true,
                    "editable": true,
                    "visible": true,
                    "tooltip": "The keyword to search for (e.g., cat, hipster, dog)."
                },
                {
                    "title": "Limit",
                    "type": "integer",
                    "name": "limit",
                    "required": false,
                    "editable": true,
                    "visible": true,
                    "value": 20,
                    "tooltip": "Maximum number of results to return (1-30). Defaults to 20."
                }
            ],
            "enabled": true
        }
    ]
}
```

{{% /expand %}}

---

## Summary

Your connector now has three fully defined operations:

- ✅ **Get Random Joke** - no parameters, returns a random joke
- ✅ **Get Joke by ID** - one required parameter (`joke_id`), returns a specific joke
- ✅ **Search Jokes** - one required parameter (`search_term`) and one optional parameter (`limit`), returns a paginated list
- ✅ All operations are wired to `connector.py` via the `OPERATION_MAP` pattern
- ✅ All operations reuse the `_make_request` helper for consistent headers and error handling

In the next chapter, you'll **test and debug** each operation using the RDK and PyCharm's debugger.
