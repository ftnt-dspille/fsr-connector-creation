---
title: "Lab 2: Intermediate Connector"
linkTitle: "Lab 2: Intermediate"
weight: 40
draft: true
---

## Lab Overview

**Duration:** 90-120 minutes

**Difficulty:** Intermediate

**What You'll Build:**
A threat intelligence connector that integrates with AlienVault OTX (Open Threat Exchange). This connector demonstrates API authentication, multiple operations, pagination, and production-ready features.

## Learning Objectives

- Implement API key authentication
- Create multiple related operations
- Handle paginated API responses
- Use the Connector Wizard for faster development
- Implement response normalization
- Add conditional fields based on user input

## Prerequisites

- Completed Lab 1
- AlienVault OTX account (free at otx.alienvault.com)
- FortiSOAR instance access

---

## Part 1: Understanding AlienVault OTX API

### API Overview

AlienVault OTX provides threat intelligence data through a REST API.

**Base URL:** `https://otx.alienvault.com/api/v1`
**Authentication:** API Key in X-OTX-API-KEY header
**Rate Limits:** 1000 requests/hour (free tier)

### Operations We'll Implement

1. **Get IP Reputation** - Lookup threat data for an IP
2. **Get Domain Reputation** - Lookup threat data for a domain
3. **Search Pulses** - Search threat intelligence pulses

### Example API Request

```bash
curl -X GET \
  'https://otx.alienvault.com/api/v1/indicators/IPv4/8.8.8.8/general' \
  -H 'X-OTX-API-KEY: your-api-key-here'
```

### Get Your API Key

1. Sign up at https://otx.alienvault.com
2. Click your username > **Settings**
3. Copy your **OTX Key**
4. Keep it secure-you'll need it for configuration

---

## Part 2: Building with the Connector Wizard

Instead of creating files manually, we'll use FortiSOAR's Connector Wizard for faster development.

### Create New Connector

1. Navigate to **Content Hub** > **Create**
2. Click **New Connector**
3. Click **Let's start by defining a connector**

### About Connector Screen

Configure the basic details:

| Field | Value |
|-------|-------|
| Connector Name | AlienVault OTX |
| API Identifier | alienvault-otx |
| Version | 1.0.0 |
| Publisher | Your Name |
| Description | Threat intelligence integration with AlienVault OTX |
| Category | Threat Intelligence |

Upload connector logos (100x100 and 40x40 pixels).

Click **Save & Continue**.

---

## Part 3: Configuring Authentication

### Configuration Screen

Add the following configuration fields:

**Field 1: Server URL**
- **Display Name:** Server URL
- **API Name:** server_url
- **Type:** Text
- **Required:** Yes
- **Default Value:** `https://otx.alienvault.com`
- **Description:** OTX API server URL

**Field 2: API Key**
- **Display Name:** API Key
- **API Name:** api_key
- **Type:** Password
- **Required:** Yes
- **Description:** Your OTX API key from Settings
- **Tooltip:** Find this in your OTX account settings

**Field 3: Verify SSL**
- **Display Name:** Verify SSL Certificate
- **API Name:** verify_ssl
- **Type:** Checkbox
- **Required:** No
- **Default Value:** true
- **Description:** Verify SSL certificates for HTTPS

Click **Save & Continue**.

---

## Part 4: Adding Operations

### Operation 1: Get IP Reputation

**Action Metadata:**
- **Title:** Get IP Reputation
- **Category:** Investigation
- **Description:** Retrieves threat intelligence for an IP address

**Parameters:**
1. **IP Address**
   - Type: Text
   - Required: Yes
   - Description: IPv4 address to query

Click **Save & Create Connector**.

### Open in Code Explorer

After creation, click **Open in Code Explorer** to add our implementation logic.

---

## Part 5: Implementing Operations

### Edit operations.py

Click `operations.py` and add our operation logic:

```python
"""
AlienVault OTX Connector Operations
"""

import requests
from connectors.core.connector import ConnectorError, get_logger

logger = get_logger('alienvault-otx')


def make_api_call(config, endpoint, method='GET', data=None):
    """
    Makes authenticated API calls to OTX.
    
    Args:
        config: Connector configuration
        endpoint: API endpoint path
        method: HTTP method
        data: Request body for POST/PUT
    
    Returns:
        dict: API response data
    """
    try:
        url = f"{config['server_url']}/api/v1/{endpoint}"
        headers = {
            'X-OTX-API-KEY': config['api_key'],
            'Content-Type': 'application/json'
        }
        
        verify_ssl = config.get('verify_ssl', True)
        
        logger.info(f'API Call: {method} {url}')
        
        if method == 'GET':
            response = requests.get(url, headers=headers, verify=verify_ssl, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, verify=verify_ssl, timeout=30)
        else:
            raise ConnectorError(f'Unsupported HTTP method: {method}')
        
        # Handle HTTP errors
        if response.status_code == 401:
            raise ConnectorError('Authentication failed. Check your API key.')
        elif response.status_code == 403:
            raise ConnectorError('Access forbidden. Check your API key permissions.')
        elif response.status_code == 404:
            return {'found': False, 'message': 'No data found'}
        elif response.status_code == 429:
            raise ConnectorError('Rate limit exceeded. Wait before retrying.')
        elif response.status_code >= 500:
            raise ConnectorError(f'OTX server error: {response.status_code}')
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        raise ConnectorError('Request timed out')
    except requests.exceptions.ConnectionError:
        raise ConnectorError('Cannot connect to OTX API')
    except ValueError:
        raise ConnectorError('Invalid JSON response from API')


def get_ip_reputation(config, params):
    """
    Retrieves threat intelligence for an IP address.
    """
    try:
        ip_address = params.get('ip_address', '').strip()
        if not ip_address:
            raise ConnectorError('IP address is required')
        
        # Basic IP validation
        octets = ip_address.split('.')
        if len(octets) != 4:
            raise ConnectorError('Invalid IPv4 address format')
        
        logger.info(f'Looking up IP: {ip_address}')
        
        # Get general IP info
        general = make_api_call(config, f'indicators/IPv4/{ip_address}/general')
        
        # Get reputation data
        reputation = make_api_call(config, f'indicators/IPv4/{ip_address}/reputation')
        
        # Get malware data
        malware = make_api_call(config, f'indicators/IPv4/{ip_address}/malware')
        
        # Normalize response
        result = {
            'indicator': ip_address,
            'indicator_type': 'IP',
            'reputation': _calculate_reputation(general, reputation),
            'pulse_count': general.get('pulse_info', {}).get('count', 0),
            'threat_score': _calculate_threat_score(reputation),
            'malware_families': [m.get('detections', {}).get('family') 
                                for m in malware.get('data', [])[:5]],
            'country': general.get('country_name'),
            'asn': general.get('asn'),
            'last_seen': general.get('pulse_info', {}).get('most_recent'),
            'validation': general.get('validation', []),
            'raw_data': {
                'general': general,
                'reputation': reputation,
                'malware': malware
            }
        }
        
        logger.info(f'IP reputation retrieved: {result["reputation"]}')
        return result
        
    except ConnectorError:
        raise
    except Exception as e:
        logger.exception(f'Failed to get IP reputation')
        raise ConnectorError(f'Operation failed: {str(e)}')


def get_domain_reputation(config, params):
    """
    Retrieves threat intelligence for a domain.
    """
    try:
        domain = params.get('domain', '').strip()
        if not domain:
            raise ConnectorError('Domain is required')
        
        logger.info(f'Looking up domain: {domain}')
        
        # Get domain general info
        general = make_api_call(config, f'indicators/domain/{domain}/general')
        
        # Get malware samples
        malware = make_api_call(config, f'indicators/domain/{domain}/malware')
        
        # Normalize response
        result = {
            'indicator': domain,
            'indicator_type': 'Domain',
            'reputation': _calculate_domain_reputation(general),
            'pulse_count': general.get('pulse_info', {}).get('count', 0),
            'alexa_rank': general.get('alexa'),
            'malware_samples': len(malware.get('data', [])),
            'whois': general.get('whois'),
            'last_seen': general.get('pulse_info', {}).get('most_recent'),
            'raw_data': {
                'general': general,
                'malware': malware
            }
        }
        
        logger.info(f'Domain reputation retrieved: {result["reputation"]}')
        return result
        
    except ConnectorError:
        raise
    except Exception as e:
        logger.exception(f'Failed to get domain reputation')
        raise ConnectorError(f'Operation failed: {str(e)}')


def search_pulses(config, params):
    """
    Searches OTX pulses (threat intelligence reports).
    """
    try:
        query = params.get('query', '').strip()
        if not query:
            raise ConnectorError('Search query is required')
        
        max_results = params.get('max_results', 10)
        
        logger.info(f'Searching pulses for: {query}')
        
        # Search pulses
        data = make_api_call(config, f'search/pulses?q={query}&limit={max_results}')
        
        results = data.get('results', [])
        
        # Normalize results
        normalized_results = []
        for pulse in results:
            normalized_results.append({
                'id': pulse.get('id'),
                'name': pulse.get('name'),
                'description': pulse.get('description'),
                'author': pulse.get('author_name'),
                'created': pulse.get('created'),
                'modified': pulse.get('modified'),
                'tags': pulse.get('tags', []),
                'indicator_count': pulse.get('indicator_count', 0),
                'tlp': pulse.get('TLP'),
                'public': pulse.get('public')
            })
        
        result = {
            'query': query,
            'count': len(normalized_results),
            'pulses': normalized_results
        }
        
        logger.info(f'Found {len(normalized_results)} pulses')
        return result
        
    except ConnectorError:
        raise
    except Exception as e:
        logger.exception(f'Failed to search pulses')
        raise ConnectorError(f'Operation failed: {str(e)}')


def _calculate_reputation(general, reputation):
    """Helper function to calculate reputation from API data"""
    
    pulse_count = general.get('pulse_info', {}).get('count', 0)
    rep_score = reputation.get('reputation', {}).get('threat_score', 0)
    
    if pulse_count == 0 and rep_score == 0:
        return 'Unknown'
    elif rep_score >= 7 or pulse_count >= 10:
        return 'Malicious'
    elif rep_score >= 4 or pulse_count >= 5:
        return 'Suspicious'
    else:
        return 'Clean'


def _calculate_domain_reputation(general):
    """Helper function for domain reputation"""
    
    pulse_count = general.get('pulse_info', {}).get('count', 0)
    
    if pulse_count == 0:
        return 'Unknown'
    elif pulse_count >= 10:
        return 'Malicious'
    elif pulse_count >= 5:
        return 'Suspicious'
    else:
        return 'Clean'


def _calculate_threat_score(reputation):
    """Calculate 0-100 threat score"""
    
    activities = reputation.get('reputation', {}).get('activities', [])
    if not activities:
        return 0
    
    # Count malicious activity types
    malicious_types = ['malware', 'scanning', 'spam']
    score = 0
    for activity in activities:
        if activity.get('name', '').lower() in malicious_types:
            score += 20
    
    return min(score, 100)
```

{{% notice tip %}}
The helper functions (`_calculate_reputation`, etc.) centralize reputation logic, making it easier to maintain and adjust thresholds.
{{% /notice %}}

### Update connector.py

The wizard created connector.py, but we need to update the operations mapping:

```python
def execute(self, config, operation, params, **kwargs):
    """Execute connector operations"""
    try:
        operations = {
            'get_ip_reputation': get_ip_reputation,
            'get_domain_reputation': get_domain_reputation,
            'search_pulses': search_pulses
        }
        
        if operation not in operations:
            raise ConnectorError(f'Unknown operation: {operation}')
        
        return operations[operation](config, params)
        
    except ConnectorError:
        raise
    except Exception as e:
        logger.exception(f'Operation {operation} failed')
        raise ConnectorError(f'Operation failed: {str(e)}')
```

---

## Part 6: Adding Remaining Operations to info.json

Edit info.json to add the other two operations. In the Code Explorer, click Form View for easier editing:

**Operation 2: Get Domain Reputation**
- Title: Get Domain Reputation
- Category: Investigation
- Parameter: Domain (text, required)

**Operation 3: Search Pulses**
- Title: Search Threat Pulses
- Category: Investigation
- Parameters:
  - Query (text, required)
  - Max Results (integer, optional, default: 10)

Click **Save Changes**.

---

## Part 7: Testing the Connector

### Import and Configure

1. Click **Publish Connector**
2. Navigate to **Content Hub** > **Manage**
3. Find your **AlienVault OTX** connector
4. Click **Configure**
5. Enter your configuration:
   - **Server URL:** `https://otx.alienvault.com`
   - **API Key:** Your OTX API key
   - **Verify SSL:** Checked
6. Click **Save**
7. Click the health check refresh icon

**Expected Result:** Health check shows "Available"

### Create Test Playbook

Create a new playbook "Test OTX Connector" with these steps:

**Step 1: Test IP Reputation**
```
Connector: AlienVault OTX
Action: Get IP Reputation
IP Address: 198.18.0.1 (example malicious IP)
```

**Step 2: Test Domain Reputation**
```
Connector: AlienVault OTX
Action: Get Domain Reputation  
Domain: evil.com
```

**Step 3: Search Pulses**
```
Connector: AlienVault OTX
Action: Search Threat Pulses
Query: ransomware
Max Results: 5
```

**Step 4: Display Summary**
```
Set Variable: summary
Value:
IP Reputation: {{vars.steps.Test_IP.data.reputation}}
Threat Score: {{vars.steps.Test_IP.data.threat_score}}
Pulse Count: {{vars.steps.Test_IP.data.pulse_count}}

Domain Reputation: {{vars.steps.Test_Domain.data.reputation}}

Pulses Found: {{vars.steps.Search_Pulses.data.count}}
```

Execute the playbook and verify all steps complete successfully.

---

## Part 8: Advanced Features

### Add Pagination Support

For operations that return many results, implement pagination:

```python
def get_all_pulses(config, params):
    """Get all pulses with pagination"""
    
    all_pulses = []
    page = 1
    max_pages = params.get('max_pages', 10)
    
    while page <= max_pages:
        data = make_api_call(config, f'pulses/subscribed?page={page}')
        
        results = data.get('results', [])
        if not results:
            break
        
        all_pulses.extend(results)
        
        if not data.get('next'):
            break
        
        page += 1
    
    return {'pulses': all_pulses, 'total': len(all_pulses)}
```

### Add Response Caching

Implement simple caching to reduce API calls:

```python
import time

# Module-level cache
_cache = {}
_cache_ttl = 300  # 5 minutes

def get_cached_or_fetch(cache_key, fetch_func):
    """Cache API responses"""
    
    now = time.time()
    
    if cache_key in _cache:
        cached_data, timestamp = _cache[cache_key]
        if now - timestamp < _cache_ttl:
            logger.info(f'Cache hit: {cache_key}')
            return cached_data
    
    # Cache miss or expired
    logger.info(f'Cache miss: {cache_key}')
    data = fetch_func()
    _cache[cache_key] = (data, now)
    return data
```

---

## Verification

Test your connector with these scenarios:

- [ ] Health check passes with valid API key
- [ ] Health check fails with invalid API key
- [ ] IP reputation lookup returns correct data
- [ ] Domain reputation lookup works
- [ ] Pulse search returns results
- [ ] Error messages are clear and helpful
- [ ] Operations handle missing parameters gracefully

---

## Lab Summary

You've built a production-ready connector with:
- ✓ API key authentication
- ✓ Multiple related operations
- ✓ Proper error handling and user feedback
- ✓ Response normalization
- ✓ Reusable helper functions

## Next Steps

Ready for advanced features? Lab 3 covers data ingestion, enrichment playbooks, and custom functions!
