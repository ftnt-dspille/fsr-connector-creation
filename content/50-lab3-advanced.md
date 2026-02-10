---
title: "Lab 3: Advanced Connector Development"
linkTitle: "Lab 3: Advanced"
weight: 50
---

## Lab Overview

**Duration:** 120 minutes

**Difficulty:** Advanced

**What You'll Build:**
A production-ready threat feed connector with data ingestion, enrichment playbooks, and advanced features.

## Learning Objectives

By the end of this lab, you will be able to:
- Implement data ingestion with scheduling support
- Create pluggable enrichment playbooks
- Add custom functions for Dynamic Values
- Implement production features (rate limiting, retry logic, bulk operations)
- Use the FortiSOAR RDK for professional development

## Prerequisites

- Completed Lab 1 and Lab 2
- Understanding of FortiSOAR playbooks
- Familiarity with the SOAR Framework Solution Pack

---

## Part 1: Understanding Advanced Concepts

### Data Ingestion Overview

Data ingestion allows connectors to automatically pull data from external sources and create FortiSOAR records on a schedule or in real-time.

**Three Ingestion Modes:**

| Mode | Description | Use Case |
|------|-------------|----------|
| `scheduled` | Runs on a timer | Periodic threat feed updates |
| `notification` | Listener-based | Real-time email monitoring |
| `app_push` | Application pushes data | Webhook receivers |

### Pluggable Enrichment Framework

Instead of modifying core enrichment playbooks, you can create connector-specific enrichment playbooks that plug into the enrichment process.

**Benefits:**
- No modification of existing playbooks
- Modular and maintainable
- Easy to enable/disable per connector
- Consistent enrichment interface

### Custom Functions

Expose connector operations as reusable functions in Dynamic Values, making them available throughout FortiSOAR without creating playbook steps.

---

## Part 2: Building the Advanced Connector

We'll build a connector for "ThreatStream" (fictional threat intelligence feed) with full data ingestion and enrichment capabilities.

### Task 2.1: Create Connector Structure

Using the Connector Wizard or manually, create the base connector:

1. Navigate to **Content Hub > Create > New Connector**

2. Enter connector details:
   - **Name**: ThreatStream
   - **API Identifier**: threatstream
   - **Version**: 1.0.0
   - **Category**: Threat Intelligence
   - **Publisher**: Your Organization

3. Add configuration fields:

```json
{
  "title": "Server URL",
  "name": "server_url",
  "type": "text",
  "required": true,
  "visible": true,
  "editable": true,
  "value": "https://api.threatstream.example.com",
  "description": "ThreatStream API server URL"
},
{
  "title": "API Key",
  "name": "api_key",
  "type": "password",
  "required": true,
  "visible": true,
  "editable": true,
  "description": "Your ThreatStream API key"
},
{
  "title": "Verify SSL",
  "name": "verify_ssl",
  "type": "checkbox",
  "required": false,
  "visible": true,
  "editable": true,
  "value": true,
  "description": "Verify SSL certificates"
}
```

### Task 2.2: Implement Core Operations

Create three core operations in `operations.py`:

```python
"""
operations.py - ThreatStream connector operations
"""
import requests
from connectors.core.connector import get_logger, ConnectorError
from datetime import datetime, timedelta

logger = get_logger('threatstream')


def make_api_call(config, endpoint, method='GET', params=None, data=None):
    """
    Reusable function for API calls with error handling
    """
    server_url = config.get('server_url', '').rstrip('/')
    api_key = config.get('api_key')
    verify_ssl = config.get('verify_ssl', True)
    
    url = f"{server_url}/api/v1/{endpoint}"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data,
            verify=verify_ssl,
            timeout=30
        )
        
        # Handle rate limiting with retry
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            raise ConnectorError(
                f'Rate limit exceeded. Retry after {retry_after} seconds.'
            )
        
        # Handle authentication errors
        if response.status_code == 401:
            raise ConnectorError('Authentication failed. Check your API key.')
        
        # Handle other errors
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f'API request failed: {str(e)}')
        raise ConnectorError(f'API request failed: {str(e)}')


def get_indicators(config, params):
    """
    Fetch threat indicators with pagination support
    """
    indicator_type = params.get('indicator_type', 'all')
    confidence = params.get('min_confidence', 50)
    limit = params.get('limit', 100)
    offset = params.get('offset', 0)
    
    # For data ingestion, get indicators since last pull
    since = params.get('since')
    if since:
        query_params = {
            'type': indicator_type,
            'confidence__gte': confidence,
            'modified__gte': since,
            'limit': limit,
            'offset': offset
        }
    else:
        query_params = {
            'type': indicator_type,
            'confidence__gte': confidence,
            'limit': limit,
            'offset': offset
        }
    
    response = make_api_call(config, 'indicators', params=query_params)
    
    # Normalize response
    indicators = response.get('objects', [])
    
    return {
        'indicators': indicators,
        'count': len(indicators),
        'total': response.get('meta', {}).get('total_count', 0),
        'next_offset': offset + limit if len(indicators) == limit else None
    }


def get_indicator_details(config, params):
    """
    Get detailed information about a specific indicator
    
    This operation is exposed as a custom function for Dynamic Values
    """
    indicator_value = params.get('indicator_value')
    
    if not indicator_value:
        raise ConnectorError('Indicator value is required')
    
    endpoint = f'indicators/{indicator_value}'
    response = make_api_call(config, endpoint)
    
    # Extract and normalize key fields
    return {
        'value': response.get('value'),
        'type': response.get('type'),
        'confidence': response.get('confidence'),
        'severity': response.get('severity'),
        'tags': response.get('tags', []),
        'first_seen': response.get('first_seen'),
        'last_seen': response.get('last_seen'),
        'description': response.get('description'),
        'raw_data': response
    }


def bulk_enrich_indicators(config, params):
    """
    Enrich multiple indicators in a single request
    
    Production feature for performance optimization
    """
    indicator_values = params.get('indicator_values', [])
    
    if not indicator_values:
        raise ConnectorError('At least one indicator value is required')
    
    # Split into batches of 100
    batch_size = 100
    all_results = []
    
    for i in range(0, len(indicator_values), batch_size):
        batch = indicator_values[i:i + batch_size]
        
        data = {
            'indicators': batch
        }
        
        response = make_api_call(config, 'indicators/bulk', method='POST', data=data)
        all_results.extend(response.get('results', []))
    
    return {
        'total_enriched': len(all_results),
        'results': all_results
    }
```

### Task 2.3: Update info.json for Operations

Add operations to `info.json`:

```json
{
  "operations": [
    {
      "operation": "get_indicators",
      "title": "Get Indicators",
      "description": "Fetch threat indicators with filtering and pagination",
      "category": "investigation",
      "annotation": "get_indicators",
      "enabled": true,
      "parameters": [
        {
          "title": "Indicator Type",
          "name": "indicator_type",
          "type": "select",
          "options": ["all", "ip", "domain", "url", "filehash", "email"],
          "value": "all",
          "required": false,
          "visible": true,
          "editable": true,
          "description": "Type of indicators to retrieve"
        },
        {
          "title": "Minimum Confidence",
          "name": "min_confidence",
          "type": "integer",
          "value": 50,
          "required": false,
          "visible": true,
          "editable": true,
          "description": "Minimum confidence score (0-100)"
        },
        {
          "title": "Limit",
          "name": "limit",
          "type": "integer",
          "value": 100,
          "required": false,
          "visible": true,
          "editable": true,
          "description": "Maximum number of results to return"
        }
      ],
      "output_schema": {
        "indicators": [],
        "count": "",
        "total": "",
        "next_offset": ""
      }
    },
    {
      "operation": "get_indicator_details",
      "title": "Get Indicator Details",
      "description": "Get detailed information about a specific indicator",
      "category": "investigation",
      "annotation": "get_indicator_details",
      "enabled": true,
      "include_as_function": true,
      "function_category": "ThreatStream",
      "parameters": [
        {
          "title": "Indicator Value",
          "name": "indicator_value",
          "type": "text",
          "required": true,
          "visible": true,
          "editable": true,
          "description": "The indicator value to look up (IP, domain, hash, etc.)"
        }
      ],
      "output_schema": {
        "value": "",
        "type": "",
        "confidence": "",
        "severity": "",
        "tags": [],
        "description": ""
      }
    },
    {
      "operation": "bulk_enrich_indicators",
      "title": "Bulk Enrich Indicators",
      "description": "Enrich multiple indicators in a single request",
      "category": "investigation",
      "annotation": "bulk_enrich_indicators",
      "enabled": true,
      "parameters": [
        {
          "title": "Indicator Values",
          "name": "indicator_values",
          "type": "json",
          "required": true,
          "visible": true,
          "editable": true,
          "value": "[]",
          "description": "List of indicator values to enrich"
        }
      ],
      "output_schema": {
        "total_enriched": "",
        "results": []
      }
    }
  ]
}
```

---

## Part 3: Implementing Data Ingestion

### Task 3.1: Enable Ingestion in info.json

Add ingestion support to your connector metadata:

```json
{
  "ingestion_supported": true,
  "ingestion_modes": ["scheduled"],
  "ingestion_preferences": {
    "modules": ["threat_intel_feeds", "indicators"],
    "launch_name": "Configure ThreatStream Ingestion"
  }
}
```

### Task 3.2: Create Fetch Playbook

Create a playbook to fetch data from ThreatStream:

**Playbook Name:** `ThreatStream > Fetch Indicators`

**Tags:** `threatstream`, `dataingestion`, `fetch`

**Steps:**

1. **Start** (Referenced trigger)

2. **Configuration** (Set Variable)
   ```json
   {
     "indicator_type": "{{vars.input.params.indicator_type}}",
     "min_confidence": "{{vars.input.params.min_confidence}}",
     "limit": "{{vars.input.params.limit}}"
   }
   ```

3. **Get Last Pull Time** (Utilities > Get Global Variable)
   - Variable Name: `ThreatStream_LastPullTime_{{vars['audit_info']['cyops_playbook_iri'].split('/')[-1].replace('-','_')}}`
   - Default Value: `{{arrow.utcnow().shift(days=-7).format('YYYY-MM-DDTHH:mm:ss')}}Z`

4. **Fetch** (ThreatStream > Get Indicators)
   - Indicator Type: `{{vars.indicator_type}}`
   - Minimum Confidence: `{{vars.min_confidence}}`
   - Limit: `{{vars.limit}}`
   - Since: `{{vars.steps.Get_Last_Pull_Time}}`

5. **Return Data** (Set Variable)
   ```json
   {
     "data": "{{vars.steps.Fetch.indicators}}"
   }
   ```

### Task 3.3: Create Record Creation Playbook

**Playbook Name:** `ThreatStream > Create Records`

**Tags:** `threatstream`, `dataingestion`, `create`

**Steps:**

1. **Start** (Referenced trigger)

2. **Create** (Create Record)
   - Module: Threat Intel Feeds (or Indicators)
   - Field Mapping:
     - Value: `{{vars.item.value}}`
     - Type: `{{vars.item.type}}`
     - Confidence: `{{vars.item.confidence}}`
     - Description: `{{vars.item.description}}`
     - Tags: `{{vars.item.tags}}`
     - First Seen: `{{vars.item.first_seen}}`
     - Last Seen: `{{vars.item.last_seen}}`
     - Source: `ThreatStream`

3. Configure the loop: Check "Execute this step once for each record in a dataset"
   - Input Dataset: `{{vars.input.records}}`

### Task 3.4: Create Ingest Parent Playbook

**Playbook Name:** `ThreatStream > Ingest`

**Tags:** `threatstream`, `dataingestion`, `ingest`

**Steps:**

1. **Start** (Scheduled/Manual trigger)

2. **Fetch Data** (Reference Playbook)
   - Playbook: `ThreatStream > Fetch Indicators`
   - Pass configured parameters

3. **Create Records** (Reference Playbook)
   - Playbook: `ThreatStream > Create Records`
   - Records: `{{vars.steps.Fetch_Data.data}}`

4. **Update Last Pull Time** (Utilities > Set Global Variable)
   - Variable Name: `ThreatStream_LastPullTime_{{vars['audit_info']['cyops_playbook_iri'].split('/')[-1].replace('-','_')}}`
   - Value: `{{arrow.utcnow().format('YYYY-MM-DDTHH:mm:ss')}}Z`

{{% notice tip %}}
The playbook collection containing these three playbooks must be tagged with `dataingestion` and `threatstream` to be recognized by the Data Ingestion Wizard.
{{% /notice %}}

---

## Part 4: Building Pluggable Enrichment

### Task 4.1: Create Enrichment Playbook

Pluggable enrichment playbooks integrate seamlessly with the SOAR Framework's enrichment process.

**Playbook Name:** `IP Address > ThreatStream > Enrichment`

**Tags:** `threatstream`, `IP_Enrichment`

**Steps:**

1. **Start** (Referenced trigger with parameters)
   - `indicator_value`: The IP address to enrich
   - `style_colors`: Enrichment styling (from parent)

2. **Configuration** (Set Variable)
   ```json
   {
     "indicator_value": "{{vars.input.params.indicator_value}}",
     "style_colors": "{{vars.input.params.style_colors}}",
     "reputation_thresholds": {
       "good": 30,
       "suspicious": 70,
       "malicious": 90
     }
   }
   ```

3. **Get Indicator Details** (ThreatStream > Get Indicator Details)
   - Indicator Value: `{{vars.indicator_value}}`

4. **Determine Reputation** (Decision)
   - Condition 1: `{{vars.steps.Get_Indicator_Details.confidence >= vars.reputation_thresholds.malicious}}`
     → Set reputation to "Malicious"
   - Condition 2: `{{vars.steps.Get_Indicator_Details.confidence >= vars.reputation_thresholds.suspicious}}`
     → Set reputation to "Suspicious"
   - Default: Set reputation to "Good"

5. **Format Enrichment Summary** (Utilities > Format as RichText)
   ```markdown
   #### ThreatStream Intelligence
   
   **Confidence:** {{vars.steps.Get_Indicator_Details.confidence}}%
   **Severity:** {{vars.steps.Get_Indicator_Details.severity}}
   **First Seen:** {{vars.steps.Get_Indicator_Details.first_seen}}
   **Last Seen:** {{vars.steps.Get_Indicator_Details.last_seen}}
   
   **Tags:** {{vars.steps.Get_Indicator_Details.tags | join(', ')}}
   
   {{vars.steps.Get_Indicator_Details.description}}
   ```

6. **Return Enrichment Data** (Set Variable)
   ```json
   {
     "reputation": "{{vars.reputation}}",
     "data": {
       "confidence": "{{vars.steps.Get_Indicator_Details.confidence}}",
       "severity": "{{vars.steps.Get_Indicator_Details.severity}}",
       "tags": "{{vars.steps.Get_Indicator_Details.tags}}"
     },
     "summary": "{{vars.steps.Format_Enrichment_Summary}}",
     "enrichment_source": "ThreatStream"
   }
   ```

### Task 4.2: Test Enrichment Integration

1. Navigate to any IP indicator in FortiSOAR
2. Click **Enrich**
3. Your ThreatStream enrichment should automatically run
4. Verify the enrichment summary appears in the indicator's description

---

## Part 5: Advanced Features

### Task 5.1: Implement Rate Limiting

Add rate limiting to prevent API throttling:

```python
import time
from functools import wraps

# Rate limiter decorator
class RateLimiter:
    def __init__(self, calls_per_second=5):
        self.calls_per_second = calls_per_second
        self.last_call = 0
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            time_since_last_call = current_time - self.last_call
            
            if time_since_last_call < (1.0 / self.calls_per_second):
                sleep_time = (1.0 / self.calls_per_second) - time_since_last_call
                time.sleep(sleep_time)
            
            self.last_call = time.time()
            return func(*args, **kwargs)
        
        return wrapper

# Apply to API call function
rate_limiter = RateLimiter(calls_per_second=5)

@rate_limiter
def make_api_call(config, endpoint, method='GET', params=None, data=None):
    # ... existing implementation
    pass
```

### Task 5.2: Add Retry Logic with Exponential Backoff

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_session_with_retries():
    """
    Create a requests session with automatic retries
    """
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Update make_api_call to use session
def make_api_call(config, endpoint, method='GET', params=None, data=None):
    session = get_session_with_retries()
    # ... rest of implementation using session.request()
```

### Task 5.3: Implement Response Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedResponse:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())

# Global cache instance
response_cache = CachedResponse(ttl_seconds=300)

def get_indicator_details_cached(config, params):
    """
    Cached version of get_indicator_details
    """
    indicator_value = params.get('indicator_value')
    cache_key = f"indicator_{indicator_value}"
    
    # Try cache first
    cached_result = response_cache.get(cache_key)
    if cached_result:
        logger.info(f'Returning cached result for {indicator_value}')
        return cached_result
    
    # Fetch from API
    result = get_indicator_details(config, params)
    
    # Cache result
    response_cache.set(cache_key, result)
    
    return result
```

---

## Part 6: Using the FortiSOAR RDK

The FortiSOAR Rapid Development Kit (RDK) is a PyCharm plugin that streamlines connector development.

### Task 6.1: Install the RDK

1. Download the RDK from the FortiSOAR documentation
2. Open PyCharm (version 2024.1 or later)
3. Navigate to **Settings > Plugins**
4. Click **Install Plugin from Disk**
5. Select the downloaded RDK `.zip` file
6. Restart PyCharm

### Task 6.2: Configure Python Environment

1. Click **FortiSOAR RDK** from the toolbar
2. Select **Configure Python Path**
3. Point to your Python 3 installation
4. Click **OK** to install dependencies

### Task 6.3: Import Existing Connector

1. Click **FortiSOAR RDK > Import FortiSOAR Connector**
2. Browse to your connector's `.tgz` file
3. The connector opens in the RDK interface

### Task 6.4: Use RDK Features

**Test Configuration:**
- Select your configuration from the dropdown
- Click **Run** to test health check
- View results in the output panel

**Test Operations:**
- Navigate to the Operations tab
- Select an operation
- Fill in test parameters
- Click **Execute Action**
- Review output and debug as needed

**Code Formatting:**
- Right-click in any Python file
- Select **Format Document**
- Code is automatically formatted

**Export Connector:**
- Click **FortiSOAR RDK > Export**
- Choose destination
- Connector is packaged as `.tgz`

{{% notice note %}}
The RDK provides IntelliSense, syntax highlighting, and integrated testing - significantly speeding up development for complex connectors.
{{% /notice %}}

---

## Part 7: Verification and Testing

### Verification Checklist

Complete these checks to confirm your advanced connector is production-ready:

**Data Ingestion:**
- [ ] Connector metadata includes `ingestion_supported: true`
- [ ] Fetch playbook successfully retrieves data
- [ ] Create playbook correctly maps fields to FortiSOAR records
- [ ] Ingest playbook successfully runs end-to-end
- [ ] Last pull time is saved and used in subsequent runs
- [ ] Data Ingestion Wizard correctly displays configuration options

**Pluggable Enrichment:**
- [ ] Enrichment playbook is tagged with correct indicator type tag
- [ ] Enrichment accepts `indicator_value` and `style_colors` parameters
- [ ] Enrichment returns properly formatted summary
- [ ] Enrichment integrates with SOAR Framework's enrichment process

**Custom Functions:**
- [ ] Operation includes `"include_as_function": true` in info.json
- [ ] Function appears in Dynamic Values under correct category
- [ ] Function executes correctly when called from Dynamic Values

**Advanced Features:**
- [ ] Rate limiting prevents API throttling
- [ ] Retry logic handles transient failures
- [ ] Response caching improves performance
- [ ] Bulk operations reduce API calls

### Integration Testing

Test the complete workflow:

1. **Configure Data Ingestion:**
   - Navigate to connector configuration
   - Click **Configure Data Ingestion**
   - Complete the wizard
   - Verify schedule is created

2. **Run Manual Ingestion:**
   - Trigger the ingest playbook manually
   - Monitor execution in Playbook Execution History
   - Verify records are created in the target module

3. **Test Enrichment:**
   - Create or select an indicator
   - Click **Enrich**
   - Verify ThreatStream enrichment runs
   - Check enrichment summary in indicator description

4. **Use Custom Function:**
   - Create a new playbook
   - Add a Set Variable step
   - Open Dynamic Values
   - Navigate to ThreatStream category
   - Select your custom function
   - Provide test value
   - Execute playbook and verify result

---

## Part 8: Best Practices for Production

### Security Considerations

**1. Credential Management:**
```python
# Never log sensitive data
logger.info(f"Connecting to {server_url}")  # ✓ Good
logger.info(f"Using API key {api_key}")      # ✗ Bad!

# Use password field type for credentials in info.json
{
  "type": "password",  # Ensures UI masking and encryption
  "name": "api_key"
}
```

**2. Input Validation:**
```python
import re

def validate_ip_address(ip):
    """Validate IP address format"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        raise ConnectorError('Invalid IP address format')
    return ip

def get_indicator_details(config, params):
    indicator_value = params.get('indicator_value')
    validated_value = validate_ip_address(indicator_value)
    # ... continue with validated value
```

**3. Error Handling:**
```python
# Provide actionable error messages
try:
    response = make_api_call(config, endpoint)
except ConnectorError as e:
    # User-friendly message with troubleshooting hint
    raise ConnectorError(
        f'Failed to fetch indicators: {str(e)}. '
        'Please verify your API key and network connectivity.'
    )
```

### Performance Optimization

**1. Batch Processing:**
```python
# Process in batches instead of individual calls
def process_large_dataset(config, params):
    items = params.get('items', [])
    batch_size = 100
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = process_batch(config, batch)
        results.extend(batch_results)
    
    return results
```

**2. Pagination:**
```python
# Implement proper pagination
def get_all_indicators(config, params):
    all_indicators = []
    offset = 0
    limit = 100
    
    while True:
        response = get_indicators(config, {
            **params,
            'limit': limit,
            'offset': offset
        })
        
        indicators = response.get('indicators', [])
        all_indicators.extend(indicators)
        
        if not response.get('next_offset'):
            break
        
        offset = response['next_offset']
    
    return all_indicators
```

**3. Connection Pooling:**
```python
# Reuse connections for multiple requests
class ConnectorSession:
    def __init__(self):
        self.session = None
    
    def get_session(self):
        if not self.session:
            self.session = requests.Session()
            # Configure session (timeouts, retries, etc.)
        return self.session
    
    def close(self):
        if self.session:
            self.session.close()

# Use in connector.py lifecycle methods
connector_session = ConnectorSession()
```

### Documentation

Include comprehensive documentation:

**1. README.md:**
```markdown
# ThreatStream Connector

## Overview
Integrates ThreatStream threat intelligence platform with FortiSOAR.

## Configuration
- **Server URL**: ThreatStream API endpoint
- **API Key**: Your authentication key
- **Verify SSL**: Enable certificate verification

## Operations
### Get Indicators
Fetches threat indicators with filtering options.
**Parameters:**
- Indicator Type: Filter by indicator type
- Min Confidence: Minimum confidence threshold

### Bulk Enrich Indicators
Enriches multiple indicators in one request for improved performance.

## Data Ingestion
Supports scheduled ingestion of threat indicators into FortiSOAR.

## Troubleshooting
- **Authentication Failed**: Verify API key is correct
- **Rate Limit Exceeded**: Reduce ingestion frequency
```

**2. Release Notes:**
Track changes between versions in `release_notes.md`.

---

## Lab Summary

Congratulations! You've built a production-ready advanced connector with:

✓ Data ingestion with scheduling  
✓ Pluggable enrichment playbooks  
✓ Custom functions for Dynamic Values  
✓ Rate limiting and retry logic  
✓ Response caching  
✓ Bulk operations  
✓ RDK integration  

**Key Takeaways:**

1. **Data ingestion** requires three tagged playbooks: fetch, create, and ingest
2. **Pluggable enrichment** uses standardized parameters and return formats
3. **Custom functions** make connector operations reusable throughout FortiSOAR
4. **Production features** like rate limiting and caching are essential for reliability
5. **The RDK** accelerates development with testing and debugging tools

**Next Steps:**

- Explore data ingestion with `notification` and `app_push` modes
- Build enrichment playbooks for other indicator types
- Implement webhook listeners for real-time ingestion
- Create custom widgets to visualize connector data

---

## Additional Resources

- [FortiSOAR Connectors Guide](https://docs.fortinet.com/document/fortisoar/latest/connectors-guide/)
- [FortiSOAR RDK Documentation](https://docs.fortinet.com/document/fortisoar/latest/rdk/)
- [SOAR Framework Solution Pack](https://fortisoar.contenthub.fortinet.com/detail.html?entity=soar-framework)
- [Pluggable Enrichment Guide](https://github.com/fortinet-fortisoar/solution-pack-soar-framework/)

## Troubleshooting

**Issue:** Data ingestion wizard doesn't show my connector  
**Solution:** Ensure `ingestion_supported: true` is in info.json and playbooks are properly tagged

**Issue:** Enrichment playbook doesn't run  
**Solution:** Verify playbook has correct indicator type tag (e.g., `IP_Enrichment`) and is in an Active collection

**Issue:** Custom function not appearing in Dynamic Values  
**Solution:** Check that operation has `"include_as_function": true` and connector is published

**Issue:** Rate limiting errors persist  
**Solution:** Adjust `calls_per_second` in RateLimiter or add delays between batch operations
