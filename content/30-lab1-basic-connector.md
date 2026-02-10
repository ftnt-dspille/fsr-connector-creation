---
title: "Lab 1: Building a Basic Connector"
linkTitle: "Lab 1: Basic Connector"
weight: 30
---

## Lab Overview

**Duration:** 60-90 minutes

**Difficulty:** Beginner

**What You'll Build:**
A simple connector that fetches public IP geolocation data from the ip-api.com free API. This connector requires no authentication and demonstrates core connector concepts.

## Learning Objectives

By the end of this lab, you will be able to:
- Create a connector's file structure manually
- Write a basic info.json configuration
- Implement simple GET API requests
- Test and debug your connector
- Import and use your connector in FortiSOAR

## Prerequisites

- FortiSOAR instance access (7.4.0+)
- Basic text editor
- Completed Python primer section
- Understanding of connector architecture

---

## Part 1: Understanding What We're Building

### The API We'll Use

We're integrating with ip-api.com, a free IP geolocation service:

**Endpoint:** `http://ip-api.com/json/{IP_ADDRESS}`

**Example Request:**
```bash
curl http://ip-api.com/json/8.8.8.8
```

**Example Response:**
```json
{
  "status": "success",
  "country": "United States",
  "countryCode": "US",
  "region": "CA",
  "regionName": "California",
  "city": "Mountain View",
  "zip": "94043",
  "lat": 37.4192,
  "lon": -122.0574,
  "timezone": "America/Los_Angeles",
  "isp": "Google LLC",
  "org": "Google Public DNS",
  "as": "AS15169 Google LLC",
  "query": "8.8.8.8"
}
```

### What Our Connector Will Do

1. Accept an IP address as input
2. Query the ip-api.com service
3. Return formatted geolocation data
4. Handle errors gracefully

This is perfect for learning because:
- No authentication required (keeps it simple)
- Free and reliable API
- Clear request/response structure
- Real security use case (IP investigation)

---

## Part 2: Creating the Connector Structure

### Step 1: Create the Connector Directory

Create a folder named `ip-geolocation` with this structure:

```
ip-geolocation/
├── connector.py
├── info.json
├── operations.py
├── requirements.txt
└── images/
    ├── large.png
    └── small.png
```

{{% notice tip %}}
You can use any folder location you prefer. We'll package it later for import to FortiSOAR.
{{% /notice %}}

### Step 2: Create Connector Icons

For this lab, you can use simple placeholder images or download icons from any source. The connector needs:

- **large.png** - 100x100 pixels
- **small.png** - 40x40 pixels

Place both in the `images/` folder.

{{% notice note %}}
In production connectors, icons should represent the integrated product. For learning, any appropriate icon works.
{{% /notice %}}

---

## Part 3: Writing the info.json File

This file defines your connector's metadata and operations.

**Create `info.json` with this content:**

```json
{
  "name": "ip-geolocation",
  "label": "IP Geolocation",
  "version": "1.0.0",
  "description": "Retrieves geographical location data for IP addresses using ip-api.com",
  "publisher": "Workshop Participant",
  "cs_approved": false,
  "cs_compatible": true,
  "category": "Investigation",
  "icon_small_name": "small.png",
  "icon_large_name": "large.png",
  "help_online": "https://ip-api.com/docs",
  "configuration": {
    "fields": [
      {
        "title": "Service URL",
        "name": "server_url",
        "type": "text",
        "description": "IP-API service endpoint URL",
        "tooltip": "The base URL for ip-api.com service",
        "required": true,
        "editable": true,
        "visible": true,
        "value": "http://ip-api.com"
      }
    ]
  },
  "operations": [
    {
      "operation": "get_ip_location",
      "title": "Get IP Geolocation",
      "description": "Retrieves geographical location data for an IP address",
      "category": "investigation",
      "annotation": "get_location",
      "enabled": true,
      "parameters": [
        {
          "title": "IP Address",
          "name": "ip_address",
          "type": "text",
          "description": "IP address to lookup",
          "tooltip": "Enter a valid IPv4 address",
          "required": true,
          "editable": true,
          "visible": true,
          "placeholder": "8.8.8.8"
        }
      ],
      "output_schema": {
        "status": "",
        "country": "",
        "region": "",
        "city": "",
        "isp": "",
        "query": ""
      }
    }
  ]
}
```

### Understanding the info.json Structure

Let's break down the key sections:

**Metadata:**
```json
{
  "name": "ip-geolocation",      // Unique identifier (no spaces)
  "label": "IP Geolocation",     // Display name in FortiSOAR
  "version": "1.0.0",            // Semantic versioning
  "category": "Investigation"    // Connector type
}
```

**Configuration:**
```json
{
  "configuration": {
    "fields": [
      {
        "title": "Service URL",          // Field label
        "name": "server_url",            // Variable name in code
        "type": "text",                  // Input type
        "required": true,                // Must be filled
        "value": "http://ip-api.com"    // Default value
      }
    ]
  }
}
```

**Operation Definition:**
```json
{
  "operation": "get_ip_location",    // Function name in code
  "title": "Get IP Geolocation",     // Display name
  "category": "investigation",        // Operation type
  "parameters": [...]                 // Input fields
}
```

---

## Part 4: Writing the operations.py File

This file contains your connector's operation logic.

**Create `operations.py` with this content:**

```python
"""
IP Geolocation Connector Operations
"""

import requests
from connectors.core.connector import ConnectorError, get_logger

# Initialize logger
logger = get_logger('ip-geolocation')


def get_ip_location(config, params):
    """
    Retrieves geographical location data for an IP address.
    
    Args:
        config (dict): Connector configuration containing server_url
        params (dict): Operation parameters containing ip_address
    
    Returns:
        dict: Formatted geolocation data
    
    Raises:
        ConnectorError: If the operation fails
    """
    try:
        # Extract and validate input
        ip_address = params.get('ip_address')
        if not ip_address:
            raise ConnectorError('IP address is required')
        
        # Get server URL from configuration
        server_url = config.get('server_url', 'http://ip-api.com')
        
        # Build the API endpoint
        endpoint = f"{server_url}/json/{ip_address}"
        
        logger.info(f'Querying geolocation for IP: {ip_address}')
        
        # Make the API request
        response = requests.get(endpoint, timeout=15)
        
        # Check if request was successful
        if response.status_code != 200:
            raise ConnectorError(
                f'API returned status code {response.status_code}'
            )
        
        # Parse JSON response
        data = response.json()
        
        # Check if the API returned success
        if data.get('status') != 'success':
            error_message = data.get('message', 'Unknown error')
            raise ConnectorError(f'API Error: {error_message}')
        
        # Format and return the response
        result = {
            'status': 'success',
            'ip_address': data.get('query'),
            'country': data.get('country'),
            'country_code': data.get('countryCode'),
            'region': data.get('regionName'),
            'city': data.get('city'),
            'zip_code': data.get('zip'),
            'latitude': data.get('lat'),
            'longitude': data.get('lon'),
            'timezone': data.get('timezone'),
            'isp': data.get('isp'),
            'organization': data.get('org'),
            'as_number': data.get('as'),
            'raw_response': data  # Include full response for reference
        }
        
        logger.info(f'Successfully retrieved location for {ip_address}')
        return result
        
    except requests.exceptions.Timeout:
        logger.error('Request timed out')
        raise ConnectorError(
            'Request timed out. The IP-API service may be unavailable.'
        )
    
    except requests.exceptions.ConnectionError:
        logger.error('Connection failed')
        raise ConnectorError(
            'Cannot connect to IP-API service. Check your network connection.'
        )
    
    except ValueError as e:
        logger.error(f'Invalid JSON response: {str(e)}')
        raise ConnectorError('Received invalid response from API')
    
    except Exception as e:
        logger.exception(f'Unexpected error: {str(e)}')
        raise ConnectorError(f'Operation failed: {str(e)}')
```

### Code Walkthrough

Let's understand each part:

**1. Input Validation:**
```python
ip_address = params.get('ip_address')
if not ip_address:
    raise ConnectorError('IP address is required')
```
Always validate that required parameters are provided.

**2. Build API Request:**
```python
server_url = config.get('server_url', 'http://ip-api.com')
endpoint = f"{server_url}/json/{ip_address}"
```
Use configuration for the base URL, build the full endpoint with the IP address.

**3. Make API Call:**
```python
response = requests.get(endpoint, timeout=15)
```
Always include a timeout to prevent hanging connections.

**4. Handle Response:**
```python
if response.status_code != 200:
    raise ConnectorError(f'API returned status code {response.status_code}')

data = response.json()
```
Check HTTP status and parse JSON response.

**5. Normalize Data:**
```python
result = {
    'status': 'success',
    'ip_address': data.get('query'),
    'country': data.get('country'),
    # ... more fields
}
```
Transform API response into a consistent FortiSOAR format.

**6. Error Handling:**
```python
except requests.exceptions.Timeout:
    raise ConnectorError('Request timed out...')
```
Catch specific exceptions and provide helpful error messages.

---

## Part 5: Writing the connector.py File

This is your connector's main controller.

**Create `connector.py` with this content:**

```python
"""
IP Geolocation Connector
Main connector class that routes operations
"""

from connectors.core.connector import Connector, ConnectorError, get_logger
import requests

# Import operation functions
from .operations import get_ip_location

# Initialize logger
logger = get_logger('ip-geolocation')


class IPGeolocation(Connector):
    """
    IP Geolocation connector for FortiSOAR
    Provides IP address location lookup using ip-api.com
    """
    
    def execute(self, config, operation, params, **kwargs):
        """
        Execute the requested operation.
        
        Args:
            config (dict): Connector configuration
            operation (str): Operation name to execute
            params (dict): Operation parameters
            **kwargs: Additional arguments
        
        Returns:
            dict: Operation results
        
        Raises:
            ConnectorError: If operation fails or is unknown
        """
        try:
            logger.info(f'Executing operation: {operation}')
            
            # Map operation names to functions
            operations = {
                'get_ip_location': get_ip_location
            }
            
            # Check if operation exists
            if operation not in operations:
                raise ConnectorError(f'Unknown operation: {operation}')
            
            # Execute the operation
            operation_func = operations[operation]
            result = operation_func(config, params)
            
            logger.info(f'Operation {operation} completed successfully')
            return result
            
        except ConnectorError:
            # Re-raise ConnectorErrors as-is
            raise
        
        except Exception as e:
            # Log and wrap unexpected errors
            logger.exception(f'Operation {operation} failed')
            raise ConnectorError(f'Operation failed: {str(e)}')
    
    def check_health(self, config):
        """
        Verify that the connector can reach the IP-API service.
        
        Args:
            config (dict): Connector configuration
        
        Returns:
            bool: True if healthy
        
        Raises:
            ConnectorError: If health check fails
        """
        try:
            logger.info('Running health check')
            
            # Get server URL from config
            server_url = config.get('server_url', 'http://ip-api.com')
            
            # Test with a known IP (Google DNS)
            test_endpoint = f"{server_url}/json/8.8.8.8"
            
            # Make test request
            response = requests.get(test_endpoint, timeout=10)
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    logger.info('Health check passed')
                    return True
            
            # If we get here, something is wrong
            raise ConnectorError(
                f'Health check failed: API returned status {response.status_code}'
            )
            
        except requests.exceptions.Timeout:
            raise ConnectorError('Health check timed out. Service may be unavailable.')
        
        except requests.exceptions.ConnectionError:
            raise ConnectorError('Cannot connect to IP-API service. Check the URL.')
        
        except Exception as e:
            logger.exception('Health check failed')
            raise ConnectorError(f'Health check failed: {str(e)}')
```

### Understanding the Connector Class

**The execute() Method:**
- Routes operations to the correct function
- Logs execution details
- Handles errors consistently

**The check_health() Method:**
- Tests configuration by making an API call
- Called when users click "Test Configuration"
- Returns True if successful, raises ConnectorError otherwise

---

## Part 6: Creating requirements.txt

This file lists Python packages your connector needs.

**Create `requirements.txt` with this content:**

```
requests==2.31.0
```

{{% notice note %}}
The `requests` library is the only external dependency for this simple connector. FortiSOAR includes this library by default, but it's good practice to list all dependencies.
{{% /notice %}}

---

## Part 7: Packaging the Connector

Now package your connector for import to FortiSOAR.

### Create the .tgz Package

Open a terminal in your connector directory and run:

```bash
cd /path/to/your/connectors
tar -czf ip-geolocation.tgz ip-geolocation/
```

This creates `ip-geolocation.tgz` containing your connector.

**Expected Output:**
```bash
$ ls -lh ip-geolocation.tgz
-rw-r--r-- 1 user staff 4.5K Jan 25 10:30 ip-geolocation.tgz
```

---

## Part 8: Importing to FortiSOAR

### Import the Connector

1. Log in to your FortiSOAR instance
2. Navigate to **Content Hub**
3. Click the **Create** tab
4. Click **Create** > **New Connector** or drag and drop your `.tgz` file
5. Browse to select `ip-geolocation.tgz`
6. Click **Open**

FortiSOAR will upload and install your connector.

### Configure the Connector

After import, FortiSOAR opens the configuration dialog:

1. In the **Configuration Name** field, enter `Default Configuration`
2. In the **Service URL** field, verify it shows `http://ip-api.com`
3. Click **Save**

### Test the Configuration

1. Click the **Refresh** icon (🔄) in the **Health Check** section
2. You should see **Available** status with a green checkmark

**Expected Result:**
The health check makes a test API call and confirms the connector can reach ip-api.com.

If you see **Disconnected**:
- Check that `http://ip-api.com` is accessible from your FortiSOAR instance
- Verify your network allows outbound HTTP connections
- Check the connector logs at `/var/log/cyops/cyops-integrations/connectors.log`

---

## Part 9: Testing the Connector

### Create a Test Playbook

1. Navigate to **Automation** > **Playbooks**
2. Create a new collection named "IP Geolocation Tests"
3. Create a new playbook named "Test IP Geolocation"
4. Set the trigger to **Manual**

### Add Connector Steps

**Step 1: Test with Google DNS**

1. Add a **Connector** step
2. Search for and select **IP Geolocation**
3. Choose the action **Get IP Geolocation**
4. Configure:
   - **IP Address:** `8.8.8.8`
5. Name the step `Test_Google_DNS`
6. Click **Save**

**Step 2: Test with Cloudflare DNS**

1. Add another **Connector** step
2. Configure:
   - **IP Address:** `1.1.1.1`
3. Name the step `Test_Cloudflare_DNS`
4. Click **Save**

**Step 3: Display Results**

1. Add a **Set Variable** step
2. Create a variable `summary` with value:
```jinja
Google DNS Location: {{vars.steps.Test_Google_DNS.data.city}}, {{vars.steps.Test_Google_DNS.data.country}}
Cloudflare DNS Location: {{vars.steps.Test_Cloudflare_DNS.data.city}}, {{vars.steps.Test_Cloudflare_DNS.data.country}}
```
3. Click **Save**

### Run the Playbook

1. Click **Save Playbook**
2. Click **Execute**
3. Watch the execution in real-time

**Expected Results:**
```
Google DNS Location: Mountain View, United States
Cloudflare DNS Location: [Location varies], [Country varies]
```

### Verify Connector Output

Click on the `Test_Google_DNS` step to see the full output:

```json
{
  "status": "success",
  "ip_address": "8.8.8.8",
  "country": "United States",
  "city": "Mountain View",
  "isp": "Google LLC",
  "latitude": 37.4192,
  "longitude": -122.0574,
  ...
}
```

---

## Part 10: Debugging and Troubleshooting

### Common Issues and Solutions

**Issue:** "IP address is required" error
**Solution:** Ensure the IP Address parameter is filled in the connector step

**Issue:** "Request timed out" error
**Solution:** 
- Check network connectivity to ip-api.com
- Increase timeout value in operations.py if needed
- Verify your FortiSOAR instance can make outbound HTTP requests

**Issue:** "Cannot connect to IP-API service"
**Solution:**
- Verify the Service URL in connector configuration
- Check firewall rules allow outbound HTTP on port 80
- Test connectivity: `curl http://ip-api.com/json/8.8.8.8`

**Issue:** Health check shows "Disconnected"
**Solution:**
- Review connector logs: `/var/log/cyops/cyops-integrations/connectors.log`
- Test the API manually from your FortiSOAR server
- Verify Python requests library is installed

### View Connector Logs

SSH to your FortiSOAR server and check logs:

```bash
tail -f /var/log/cyops/cyops-integrations/connectors.log | grep ip-geolocation
```

Look for your connector's log messages:
```
2024-01-25 10:45:23 INFO ip-geolocation Executing operation: get_ip_location
2024-01-25 10:45:23 INFO ip-geolocation Querying geolocation for IP: 8.8.8.8
2024-01-25 10:45:24 INFO ip-geolocation Successfully retrieved location for 8.8.8.8
```

---

## Enhancement Exercise

Now that your basic connector works, try adding these enhancements:

### Challenge 1: Add Batch Lookup

Modify the connector to accept multiple IP addresses and return results for all of them.

**Hints:**
- Add a new operation `batch_lookup_ips`
- Accept a textarea parameter with one IP per line
- Loop through IPs and call get_ip_location for each
- Return a list of results

{{% expand "Click to see solution approach" %}}
```python
def batch_lookup_ips(config, params):
    """Lookup multiple IPs"""
    ip_list = params.get('ip_addresses', '').split('\n')
    ip_list = [ip.strip() for ip in ip_list if ip.strip()]
    
    results = []
    for ip in ip_list:
        try:
            result = get_ip_location(config, {'ip_address': ip})
            results.append(result)
        except ConnectorError as e:
            results.append({
                'ip_address': ip,
                'status': 'failed',
                'error': str(e)
            })
    
    return {'results': results, 'total': len(results)}
```
{{% /expand %}}

### Challenge 2: Add Result Caching

Implement simple caching to avoid repeated lookups for the same IP.

**Hints:**
- Use a Python dictionary to store results
- Check cache before making API call
- Add cache expiry logic

### Challenge 3: Create an Enrichment Playbook

Build a playbook that:
1. Gets IP addresses from Alerts
2. Looks up their locations
3. Updates Alert records with location data

---

## Verification Checklist

Before completing this lab, verify:

- [ ] Connector imports successfully into FortiSOAR
- [ ] Health check shows "Available" status
- [ ] Test playbook executes without errors
- [ ] IP lookup returns valid location data
- [ ] Connector logs show no errors
- [ ] You understand each file's purpose
- [ ] You can explain how the connector works

---

## Lab Summary

Congratulations! In this lab, you:
- ✓ Created a complete connector file structure
- ✓ Wrote info.json with metadata and operations
- ✓ Implemented a working API integration
- ✓ Added proper error handling
- ✓ Packaged and imported your connector
- ✓ Tested it in a real playbook

**Key Takeaways:**
- Connectors follow a standard structure
- info.json defines everything FortiSOAR needs to know
- operations.py contains the actual API logic
- connector.py routes operations and validates health
- Error handling improves user experience
- Testing confirms everything works correctly

## Next Steps

You've built a working connector! Next, we'll create a more sophisticated connector with authentication, multiple operations, and advanced features in **Lab 2: Intermediate Connector**.
