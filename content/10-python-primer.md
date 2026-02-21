---
title: Python Essentials for Connectors
linkTitle: Python Primer
weight: 20
---

## Overview

This section covers the Python concepts you need to build FortiSOAR connectors. Don't worry if you're not a Python expert. We'll focus only on what's relevant for connector development. 

## Python Basics for Connectors

### Variables and Data Types

Connectors work with different data types to handle API requests and responses.

**Strings** - Text data like URLs, usernames, and messages:
```python
server_url = "https://api.example.com"
username = "admin"
api_endpoint = f"{server_url}/users/{username}"  # String formatting
```


**Integers and Floats** - Numbers for timeouts, limits, and counts:
```python
timeout = 30
max_results = 100
confidence_score = 0.85
```

**Booleans** - True/False values for flags and conditions:
```python
verify_ssl = True
is_malicious = False
```

**Lists** - Ordered collections of items:
```python
ip_addresses = ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
threat_types = ["malware", "phishing", "c2"]
```

**Dictionaries** - Key-value pairs (like JSON):
```python
config = {
    "server_url": "https://api.example.com",
    "api_key": "secret123",
    "timeout": 30
}

# Accessing values
url = config["server_url"]
key = config.get("api_key", "default")  # With default value
```

### Functions

Functions organize code into reusable blocks. In connectors, each operation is a function.

```python
def get_ip_reputation(config, params):
    """
    Retrieves reputation data for an IP address.
    
    Args:
        config: Connector configuration (dict)
        params: Operation parameters (dict)
    
    Returns:
        dict: Reputation data
    """
    ip_address = params.get('ip_address')
    server_url = config.get('server_url')
    
    # Function logic here
    result = {
        'ip': ip_address,
        'reputation': 'clean',
        'confidence': 85
    }
    
    return result
```

### Working with JSON

Connectors constantly convert between Python dictionaries and JSON for API communication.

```python
import json

# Python dict to JSON string
data = {"name": "malware.exe", "hash": "abc123"}
json_string = json.dumps(data)

# JSON string to Python dict
response_text = '{"status": "success", "data": {"count": 5}}'
response_data = json.loads(response_text)
count = response_data['data']['count']  # Access nested values
```

### Making HTTP Requests

The `requests` library handles API calls in connectors.

```python
import requests

# GET request
response = requests.get(
    'https://api.example.com/users',
    headers={'Authorization': 'Bearer token123'},
    timeout=30
)

# POST request with JSON body
response = requests.post(
    'https://api.example.com/alerts',
    json={'severity': 'high', 'message': 'Suspicious activity'},
    headers={'Content-Type': 'application/json'}
)

# Check response
if response.status_code == 200:
    data = response.json()
else:
    error_message = f"API returned status {response.status_code}"
```

### Error Handling

Proper error handling makes connectors reliable and user-friendly.

```python
from connectors.core.connector import ConnectorError

def check_ip_reputation(config, params):
    try:
        ip_address = params.get('ip_address')
        
        if not ip_address:
            raise ConnectorError('IP address is required')
        
        # Make API call
        response = requests.get(f"{config['url']}/ip/{ip_address}")
        response.raise_for_status()  # Raises error for 4xx/5xx status
        
        return response.json()
        
    except requests.exceptions.Timeout:
        raise ConnectorError('Request timed out. Check server connectivity.')
    except requests.exceptions.ConnectionError:
        raise ConnectorError('Cannot connect to server. Verify the URL.')
    except Exception as e:
        raise ConnectorError(f'Unexpected error: {str(e)}')
```

### String Manipulation

Working with strings for formatting URLs, messages, and parsing data.

```python
# String concatenation
url = base_url + "/api/v1/" + endpoint

# f-strings (recommended)
url = f"{base_url}/api/v1/{endpoint}"
message = f"Found {count} results for query '{search_term}'"

# String methods
email = "  USER@EXAMPLE.COM  "
clean_email = email.strip().lower()  # "user@example.com"

domain = "api.example.com"
if domain.startswith("api."):
    subdomain = domain.split(".")[0]  # "api"
```

### Working with Lists and Loops

Processing multiple items in connector responses.

```python
# Iterating over lists
ip_addresses = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]

for ip in ip_addresses:
    print(f"Checking {ip}")

# List comprehension (transform lists efficiently)
indicators = [
    {"value": "1.1.1.1", "type": "ip"},
    {"value": "evil.com", "type": "domain"}
]
ip_only = [item['value'] for item in indicators if item['type'] == 'ip']
```

### Dictionary Operations

Connectors frequently manipulate dictionary data from API responses.

```python
# Accessing nested data safely
response = {
    "data": {
        "user": {
            "name": "John",
            "email": "john@example.com"
        }
    }
}

# Safe access with get()
name = response.get('data', {}).get('user', {}).get('name', 'Unknown')

# Merging dictionaries
defaults = {"timeout": 30, "verify_ssl": True}
user_config = {"timeout": 60}
config = {**defaults, **user_config}  # timeout=60, verify_ssl=True

# Extracting values
api_response = {
    "id": 123,
    "timestamp": "2024-01-25",
    "severity": "high",
    "details": "Long description..."
}

# Get only needed fields
summary = {
    "id": api_response.get("id"),
    "severity": api_response.get("severity")
}
```

### Classes (Basic Understanding)

Connectors are Python classes, but you don't need deep OOP knowledge.

```python
from connectors.core.connector import Connector
from operations import operations

class MyConnector(Connector):
    """Your connector inherits from the base Connector class"""
    
    def execute(self, config, operation, params, **kwargs):
        """This method is called when your connector runs"""
        
        # Route to the right operation
        if operation == 'get_ip_reputation':
            return self.get_ip_reputation(config, params)
        elif operation == 'block_ip':
            return self.block_ip(config, params)
    
    def check_health(self, config):
        """Tests if configuration works"""
        try:
            response = requests.get(config['server_url'] + '/health')
            return response.status_code == 200
        except:
            return False
```

## Common Patterns in Connectors

### Pattern 1: API Request Template

```python
def make_api_call(config, endpoint, method='GET', data=None):
    """Reusable function for API calls"""
    
    url = f"{config['server_url']}{endpoint}"
    headers = {
        'Authorization': f"Bearer {config['api_token']}",
        'Content-Type': 'application/json'
    }
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        raise ConnectorError(f"API call failed: {str(e)}")
```

## Python Practice Exercise

Try this simple exercise to practice the concepts:

**Task:** Write a function that processes a list of indicators and returns only malicious ones.

```python
def filter_malicious(indicators):
    """
    Args:
        indicators: List of dicts like [{"value": "1.1.1.1", "score": 85}, ...]
    
    Returns:
        List of malicious indicators (score >= 70)
    """
    # Your code here
    pass

# Test data
test_indicators = [
    {"value": "1.1.1.1", "score": 25},
    {"value": "2.2.2.2", "score": 85},
    {"value": "3.3.3.3", "score": 92},
    {"value": "4.4.4.4", "score": 10}
]

# Expected result: [{"value": "2.2.2.2", "score": 85}, {"value": "3.3.3.3", "score": 92}]
```

{{% expand "Click to see the solution" %}}
```python
def filter_malicious(indicators):
    """Filter indicators with score >= 70"""
    return [ind for ind in indicators if ind.get('score', 0) >= 70]

# Or with a regular loop:
def filter_malicious(indicators):
    malicious = []
    for indicator in indicators:
        if indicator.get('score', 0) >= 70:
            malicious.append(indicator)
    return malicious
```
{{% /expand %}}

## Key Takeaways

- **Dictionaries** are everywhere in connectors—they represent configuration, parameters, and responses
- **Error handling** with try/except makes connectors reliable
- **The requests library** handles all HTTP communication
- **String formatting** with f-strings keeps code readable
- **List comprehensions** process data efficiently
- You don't need to be a Python expert—these fundamentals cover 90% of connector development

## Next Steps

Now that you understand the Python essentials, you're ready to learn about FortiSOAR connector architecture and build your first connector!
