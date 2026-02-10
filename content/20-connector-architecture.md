---
title: Understanding Connector Architecture
linkTitle: Connector Architecture
weight: 30
---

## Overview

Before building connectors, you need to understand how they're structured and how they integrate with FortiSOAR. This section explains the key components and concepts that make connectors work.

## What is a Connector?

A connector is a Python package that enables FortiSOAR to communicate with external systems. It acts as a bridge, translating FortiSOAR requests into API calls and converting responses back into FortiSOAR-compatible formats.

### Real-World Example

Think of a connector like a universal adapter for electrical plugs:
- **FortiSOAR** is your device that needs power (data/actions)
- **External API** is the wall socket with a specific format
- **Connector** is the adapter that makes them work together

When you want to check if an IP is malicious using VirusTotal:
1. FortiSOAR sends a request to the VirusTotal connector
2. The connector translates this into a VirusTotal API call
3. VirusTotal returns its response in its format
4. The connector normalizes this into FortiSOAR's format
5. FortiSOAR receives standardized data it can use

## Connector Anatomy

Every FortiSOAR connector follows a standard directory structure:

```
my-connector/
├── connector.py          # Main connector logic
├── info.json            # Connector metadata and operations
├── operations.py        # Individual operation functions
├── requirements.txt     # Python dependencies
├── images/              # Connector icons
│   ├── large.png       # 100x100 pixels
│   └── small.png       # 40x40 pixels
└── playbooks/          # Sample playbooks (optional)
    └── playbooks.json
```

Let's explore each component.

## The info.json File

This is the connector's blueprint—it defines everything FortiSOAR needs to know about your connector.

### Basic Metadata

```json
{
  "name": "threat-intel-api",
  "label": "Threat Intel API",
  "version": "1.0.0",
  "description": "Enriches indicators with threat intelligence data",
  "publisher": "YourCompany",
  "category": "Threat Intelligence",
  "icon_small_name": "small.png",
  "icon_large_name": "large.png"
}
```

| Field | Purpose | Example |
|-------|---------|---------|
| name | Unique identifier (no spaces/special chars) | threat-intel-api |
| label | Display name in FortiSOAR UI | Threat Intel API |
| version | Connector version (x.y.z format) | 1.0.0 |
| publisher | Your organization name | YourCompany |
| category | Type of integration | Threat Intelligence |

### Configuration Section

Defines what users need to configure to use your connector:

```json
{
  "configuration": {
    "fields": [
      {
        "title": "Server URL",
        "name": "server_url",
        "type": "text",
        "required": true,
        "visible": true,
        "editable": true,
        "description": "API server URL (e.g., https://api.example.com)",
        "tooltip": "The base URL for API requests",
        "placeholder": "https://api.example.com"
      },
      {
        "title": "API Key",
        "name": "api_key",
        "type": "password",
        "required": true,
        "visible": true,
        "editable": true,
        "description": "Your API authentication key"
      },
      {
        "title": "Verify SSL",
        "name": "verify_ssl",
        "type": "checkbox",
        "required": false,
        "visible": true,
        "editable": true,
        "value": true,
        "description": "Verify SSL certificates for HTTPS connections"
      }
    ]
  }
}
```

**Field Types Available:**
- `text` - Single-line text input
- `password` - Masked text input
- `textarea` - Multi-line text
- `integer` - Numeric input
- `checkbox` - True/false toggle
- `select` - Dropdown menu
- `multiselect` - Multiple selection dropdown
- `datetime` - Date/time picker

### Operations Section

Defines the actions your connector can perform:

```json
{
  "operations": [
    {
      "operation": "get_ip_reputation",
      "title": "Get IP Reputation",
      "description": "Retrieves reputation data for an IP address",
      "category": "investigation",
      "annotation": "get_reputation",
      "enabled": true,
      "parameters": [
        {
          "title": "IP Address",
          "name": "ip_address",
          "type": "text",
          "required": true,
          "visible": true,
          "editable": true,
          "description": "IP address to check",
          "tooltip": "Enter a valid IPv4 or IPv6 address"
        }
      ],
      "output_schema": {
        "reputation": "",
        "confidence": 0,
        "last_seen": ""
      }
    }
  ]
}
```

**Operation Categories:**
- `investigation` - Data gathering and analysis
- `remediation` - Fixing or responding to issues  
- `containment` - Blocking or isolating threats
- `miscellaneous` - Other operations

## The connector.py File

This is your connector's main controller. It inherits from FortiSOAR's base `Connector` class and implements two required methods:

```python
from connectors.core.connector import Connector, ConnectorError, get_logger

logger = get_logger('threat-intel-api')

class ThreatIntelAPI(Connector):
    
    def execute(self, config, operation, params, **kwargs):
        """
        Routes operation requests to the appropriate function.
        
        Args:
            config (dict): Connector configuration from info.json
            operation (str): Operation name to execute
            params (dict): Parameters for the operation
        
        Returns:
            dict: Operation results
        """
        logger.info(f'Executing operation: {operation}')
        
        try:
            # Map operation names to functions
            operation_map = {
                'get_ip_reputation': get_ip_reputation,
                'get_domain_reputation': get_domain_reputation
            }
            
            if operation not in operation_map:
                raise ConnectorError(f'Unknown operation: {operation}')
            
            # Execute the requested operation
            return operation_map[operation](config, params)
            
        except Exception as e:
            logger.exception(f'Operation failed: {operation}')
            raise ConnectorError(str(e))
    
    def check_health(self, config):
        """
        Validates that the connector configuration works.
        
        Args:
            config (dict): Connector configuration
        
        Returns:
            bool: True if healthy, raises ConnectorError otherwise
        """
        try:
            # Test connectivity
            response = requests.get(
                f"{config['server_url']}/health",
                headers={'Authorization': f"Bearer {config['api_key']}"},
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                raise ConnectorError(
                    f'Health check failed with status {response.status_code}'
                )
        
        except requests.exceptions.ConnectionError:
            raise ConnectorError('Cannot connect to server. Check the URL.')
        except requests.exceptions.Timeout:
            raise ConnectorError('Connection timed out.')
        except Exception as e:
            raise ConnectorError(f'Health check failed: {str(e)}')
```

### Key Methods Explained

| Method | Purpose | When Called |
|--------|---------|-------------|
| `execute()` | Routes and executes operations | Every time an action runs |
| `check_health()` | Validates configuration | When users click "Test Configuration" |

## The operations.py File

This file contains your actual operation logic. Each operation is a standalone function:

```python
import requests
from connectors.core.connector import ConnectorError

def get_ip_reputation(config, params):
    """
    Retrieves threat intelligence for an IP address.
    
    Args:
        config (dict): Connector configuration
        params (dict): Operation parameters
    
    Returns:
        dict: Normalized reputation data
    """
    try:
        # Extract parameters
        ip_address = params.get('ip_address')
        if not ip_address:
            raise ConnectorError('IP address is required')
        
        # Build API request
        url = f"{config['server_url']}/v1/ip/{ip_address}"
        headers = {
            'Authorization': f"Bearer {config['api_key']}",
            'Content-Type': 'application/json'
        }
        
        # Make API call
        response = requests.get(
            url,
            headers=headers,
            verify=config.get('verify_ssl', True),
            timeout=30
        )
        
        # Handle response
        response.raise_for_status()
        data = response.json()
        
        # Normalize response for FortiSOAR
        return {
            'ip_address': ip_address,
            'reputation': data.get('verdict', 'unknown').lower(),
            'confidence': data.get('confidence_score', 0),
            'last_seen': data.get('last_activity_date'),
            'threat_types': data.get('threat_categories', []),
            'raw_response': data
        }
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ConnectorError(f'IP address {ip_address} not found')
        elif e.response.status_code == 401:
            raise ConnectorError('Authentication failed. Check your API key.')
        else:
            raise ConnectorError(f'API error: {e.response.status_code}')
    
    except requests.exceptions.Timeout:
        raise ConnectorError('Request timed out. Try again later.')
    
    except Exception as e:
        raise ConnectorError(f'Operation failed: {str(e)}')
```

## Data Flow in Connectors

Let's trace what happens when a playbook runs a connector action:

```
1. Playbook executes "Get IP Reputation" step
   ↓
2. FortiSOAR calls connector.execute() with:
   - config = {"server_url": "...", "api_key": "..."}
   - operation = "get_ip_reputation"
   - params = {"ip_address": "1.1.1.1"}
   ↓
3. Connector routes to get_ip_reputation(config, params)
   ↓
4. Operation function:
   a. Extracts parameters
   b. Builds API URL
   c. Makes HTTP request
   d. Processes response
   ↓
5. Returns normalized data to FortiSOAR
   ↓
6. Data available in playbook as {{steps.Get_IP_Reputation.data}}
```

## Configuration vs Parameters

Understanding the difference is crucial:

**Configuration** (from `config` parameter):
- Set once per connector instance
- Examples: Server URL, API keys, credentials
- Stored securely in FortiSOAR database
- Defined in info.json "configuration" section

**Parameters** (from `params` parameter):
- Provided each time an operation runs
- Examples: IP address to check, time range for query
- Can use dynamic values from playbook
- Defined in info.json "operations" → "parameters" section

Example in code:
```python
def search_threats(config, params):
    # Configuration - same for all executions
    base_url = config['server_url']
    api_key = config['api_key']
    
    # Parameters - different each time
    search_query = params['query']
    max_results = params.get('max_results', 100)
    
    # Make API call using both
    url = f"{base_url}/search?q={search_query}&limit={max_results}"
    headers = {'Authorization': f'Bearer {api_key}'}
```

## Error Handling Strategy

Connectors should handle errors gracefully and provide helpful feedback:

```python
from connectors.core.connector import ConnectorError

def handle_api_errors(response):
    """Converts API errors to user-friendly messages"""
    
    status_code = response.status_code
    
    error_messages = {
        400: 'Invalid request. Check your input parameters.',
        401: 'Authentication failed. Verify your API key.',
        403: 'Access denied. Check your permissions.',
        404: 'Resource not found.',
        429: 'Rate limit exceeded. Try again later.',
        500: 'Server error. Contact the API provider.',
        503: 'Service unavailable. Try again later.'
    }
    
    message = error_messages.get(
        status_code,
        f'API returned unexpected status: {status_code}'
    )
    
    raise ConnectorError(message)
```

## Connector Lifecycle Events

You can add optional methods to handle connector lifecycle events:

```python
class MyConnector(Connector):
    
    def on_add_config(self, config):
        """Called when a new configuration is added"""
        logger.info('New configuration added')
        # Initialize resources, start services, etc.
    
    def on_update_config(self, old_config, new_config):
        """Called when configuration is updated"""
        logger.info('Configuration updated')
        # Reload settings, reconnect, etc.
    
    def on_delete_config(self, config):
        """Called when configuration is deleted"""
        logger.info('Configuration deleted')
        # Clean up resources, stop services, etc.
    
    def on_activate(self, config):
        """Called when connector is activated"""
        logger.info('Connector activated')
    
    def on_deactivate(self, config):
        """Called when connector is deactivated"""
        logger.info('Connector deactivated')
```

## Best Practices Summary

**Do:**
- ✅ Validate all input parameters
- ✅ Provide clear, actionable error messages
- ✅ Use timeouts on all HTTP requests
- ✅ Normalize API responses to consistent format
- ✅ Log important operations and errors
- ✅ Handle pagination for large result sets

**Don't:**
- ❌ Store credentials in code
- ❌ Use hardcoded values for configurable items
- ❌ Ignore HTTP errors
- ❌ Return raw API responses without normalization
- ❌ Skip input validation

## Connector Development Methods

FortiSOAR offers three ways to build connectors:

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Manual** | Learning, full control | Complete flexibility | More time-consuming |
| **Wizard** | Quick prototypes | Fast, guided process | Limited customization |
| **RDK (PyCharm)** | Professional development | IDE features, debugging | Requires PyCharm setup |

In this workshop, we'll use all three methods so you can choose the right tool for each situation.

## Check Your Understanding

Before moving to the labs, ensure you can answer:

1. What are the two required methods in connector.py?
2. What's the difference between configuration and parameters?
3. Where do you define connector operations?
4. How do you provide helpful error messages to users?
5. What data structure do connectors use for configuration and responses?

{{% expand "Click to check your answers" %}}
1. **execute()** (routes operations) and **check_health()** (validates configuration)
2. **Configuration** is set once per connector instance (URLs, keys). **Parameters** are provided each time an operation runs (IP to check, search query)
3. In the **info.json** file under the "operations" array
4. Use **ConnectorError** with clear, actionable messages
5. **Dictionaries** (Python dicts / JSON objects)
{{% /expand %}}

## Next Steps

You now understand how connectors are structured and how they work within FortiSOAR. Time to build your first connector!
