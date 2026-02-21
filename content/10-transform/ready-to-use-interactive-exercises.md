---
title: Ready-to-Use Interactive
linkTitle: Ready-to-Use Interactive
weight: 10
---

# Ready-to-Use Interactive Exercises for FortiSOAR Workshop

## Instructions

Copy and paste these exercises directly into your workshop modules at the indicated locations.

---

## FOR MODULE: 01-introduction.md

### INSERT AFTER: "Check Your Understanding" section

```markdown
---

## 🎯 Hands-On: Connector Scavenger Hunt

**Time:** 10 minutes

Before writing code, let's explore what connectors look like in practice.

### Activity

**In your FortiSOAR instance:**

1. Navigate to **Content Hub > Connectors**
2. Find and examine **THREE different connectors**
3. For each connector, document:

**Connector Analysis Worksheet:**

| Connector Name | Category | # of Operations | Auth Type | One Interesting Feature |
|----------------|----------|-----------------|-----------|------------------------|
| Example: VirusTotal | Threat Intel | 12 | API Key | Batch file scanning |
| 1. _____________ | _______ | ____ | _______ | _________________ |
| 2. _____________ | _______ | ____ | _______ | _________________ |
| 3. _____________ | _______ | ____ | _______ | _________________ |

**Finding Info:**
- **Category:** Shown in connector tile
- **# of Operations:** Click connector → Look at available actions
- **Auth Type:** Check configuration fields
- **Interesting Feature:** Any operation that caught your eye

### Discussion Questions

After completing your analysis:

1. **What patterns did you notice?** Are connectors in the same category similar?

2. **Which connector seems most complex?** What makes you think that?

3. **Which auth method was most common?** (API Key, OAuth, Basic Auth, etc.)

{{% expand "What others typically discover" %}}
**Common Patterns:**
- Most connectors use API key authentication (simplest)
- Threat intelligence connectors average 8-12 operations
- "Get" operations are more common than "Create/Update"
- Similar categories have similar operation types

**Most Complex:** 
- ServiceNow, Jira, or Microsoft Sentinel connectors (lots of operations)
- Complexity comes from supporting many different actions

**Most Common Auth:** 
- API Key authentication (70%+ of connectors)
{{% /expand %}}

### Bonus Challenge

**Export and peek inside a connector:**

1. Find the **Have I Been Pwned** connector (or similar simple connector)
2. Click the **•••** menu → **Export**
3. Extract the .tgz file
4. Open `info.json` in a text editor
5. Can you find where operations are defined?

{{% notice tip %}}
Don't worry about understanding everything yet. You're building intuition about connector structure!
{{% /notice %}}

---
```

---

## FOR MODULE: 10-python-primer.md

### INSERT AFTER: "Working with JSON" section

```markdown
---

## 🐛 Debug Challenge: API Response Handling

**Time:** 15 minutes

Real APIs don't always return clean data. Practice handling messy responses!

### Challenge 1: Defensive Parsing

This code looks up threat intelligence but crashes on some responses. **Find and fix all the bugs.**

```python
def get_threat_intelligence(config, params):
"""Get threat intel for an indicator"""

# Get indicator from params
indicator = params['indicator']  # 🐛 Bug #1

# Make API call
url = f"{config['server']}/api/check"
response = requests.post(url, json={'value': indicator})

# Parse response
data = response.json()
threat_score = data['score']  # 🐛 Bug #2

# Return result
return {
'indicator': indicator,
'threat_score': threat_score,
'is_malicious': data['verdict']['malicious']  # 🐛 Bug #3
}
```

### Test Cases

Test your fixed function with these scenarios:

```python
# Test 1: Missing indicator parameter
config = {'server': 'https://api.example.com'}
params = {}  # Oops, no 'indicator' key
result = get_threat_intelligence(config, params)  # Should not crash!

# Test 2: API returns error
# Simulated response: {"error": "Rate limit exceeded", "status": 429}
# Your code should handle this gracefully

# Test 3: Nested data is missing
# Simulated response: {"score": 85}  # Missing 'verdict' key
# Should not crash with KeyError
```

{{% expand "Hint #1: Crash Prevention" %}}
**Problem:** Using `params['indicator']` throws `KeyError` if key doesn't exist.

**Fix Pattern:**

```python
indicator = params.get('indicator')
if not indicator:
    raise ConnectorError('Indicator is required')
```

**Why:** Always use `.get()` for dictionary access in connectors. Then validate required fields.
{{% /expand %}}

{{% expand "Hint #2: API Errors" %}}
**Problem:** `response.json()` might fail, or response might contain error message instead of data.

**Fix Pattern:**

```python
response.raise_for_status()  # Raises error for 4xx/5xx
data = response.json()

# Check for API-level errors
if 'error' in data:
    raise ConnectorError(f"API error: {data['error']}")
```

{{% /expand %}}

{{% expand "Hint #3: Safe Navigation" %}}
**Problem:** Accessing nested dictionary keys like `data['verdict']['malicious']` crashes if any level is missing.

**Fix Pattern:**

```python
# Option 1: Chained .get()
is_malicious = data.get('verdict', {}).get('malicious', False)

# Option 2: Check each level
verdict = data.get('verdict')
is_malicious = verdict.get('malicious', False) if verdict else False
```

{{% /expand %}}

{{% expand "Complete Solution" %}}

```python
def get_threat_intelligence(config, params):
    """Get threat intel for an indicator"""

    try:
        # Validate required parameters
        indicator = params.get('indicator')
        if not indicator:
            raise ConnectorError('Indicator value is required')

        # Build URL with validation
        server_url = config.get('server')
        if not server_url:
            raise ConnectorError('Server URL not configured')

        # Make API call
        url = f"{server_url}/api/check"
        response = requests.post(
            url,
            json={'value': indicator},
            timeout=30
        )

        # Check HTTP status
        response.raise_for_status()

        # Parse response
        data = response.json()

        # Check for API-level errors
        if 'error' in data:
            raise ConnectorError(f"API error: {data.get('error', 'Unknown error')}")

        # Safe navigation of nested data
        threat_score = data.get('score', 0)
        verdict = data.get('verdict', {})
        is_malicious = verdict.get('malicious', False)

        # Return normalized response
        return {
            'indicator': indicator,
            'threat_score': threat_score,
            'is_malicious': is_malicious,
            'confidence': verdict.get('confidence', 'unknown'),
            'raw_response': data
        }

    except requests.exceptions.Timeout:
        raise ConnectorError('Request timed out. Try again.')

    except requests.exceptions.ConnectionError:
        raise ConnectorError(f'Cannot connect to {server_url}')

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 401:
            raise ConnectorError('Authentication failed. Check API key.')
        elif status == 429:
            raise ConnectorError('Rate limit exceeded. Wait and retry.')
        else:
            raise ConnectorError(f'HTTP error {status}')

    except json.JSONDecodeError:
        raise ConnectorError('Invalid JSON response from API')

    except Exception as e:
        raise ConnectorError(f'Unexpected error: {str(e)}')
```

**Key Improvements:**

1. ✅ Validates all inputs before use
2. ✅ Uses safe dictionary access throughout
3. ✅ Handles specific error types with helpful messages
4. ✅ Includes timeout protection
5. ✅ Returns consistent structure even if some fields missing
6. ✅ Includes raw response for debugging
   {{% /expand %}}

### Challenge 2: Your Turn

Write a function that handles this API response safely:

```python
# API sometimes returns:
{"status": "success", "data": {"user": {"name": "John", "email": "john@example.com"}}}

# Other times returns:
{"status": "error", "message": "User not found"}

# Sometimes even:
{"status": "success", "data": null}
```

**Your function should:**

- Return the email if available
- Return `None` if user not found
- Raise `ConnectorError` with helpful message on errors

{{% expand "Solution Template" %}}

```python
def get_user_email(config, params):
    """Safely extract email from API response"""

    try:
        # Make API call (implementation omitted)
        data = response.json()

        # TODO: Check status field
        status = data.get('status')
        if status == 'error':
            # TODO: Return error message
            pass

        # TODO: Safely navigate to email
        # Remember: data field might be None or missing 'user'

        # TODO: Return email or None

    except Exception as e:
        raise ConnectorError(f'Failed to get user email: {str(e)}')
```

{{% /expand %}}

---

```

---

## FOR MODULE: 20-connector-architecture.md

### INSERT AFTER: "Data Flow in Connectors" section

```markdown
---

## 🔍 Interactive Exercise: Trace the Execution

**Time:** 15 minutes

Understanding data flow is crucial. Let's trace a real execution!

### Scenario

A playbook executes this step:

```yaml
Action: Get IP Reputation
Connector: ThreatIntel
Configuration: Production API
Parameters:
  ip_address: "192.0.2.1"
  include_history: true
```

### Your Task

**Trace what happens step-by-step:**

1. **Starting Point:**
    - What function receives this first?
    - In which file is this function?
    - What parameters does it receive?

2. **Routing:**
    - How does the connector know which operation to run?
    - What data structure maps operation names to functions?

3. **Execution:**
    - Where is the actual API call made?
    - What information does this function need from `config`?
    - What information comes from `params`?

4. **Response:**
    - What format should the function return?
    - Where does this data go after returning?
    - How can the playbook access this data?

### Fill in the Sequence Diagram

Complete this flow by filling in the blanks:

```
1. FortiSOAR receives playbook step request
   ↓
2. Calls: __________.__________(config, operation, params)
   File: __________
   ↓
3. Function maps operation name "___________" to function _________
   ↓
4. Calls: __________.__________(config, params)
   File: __________
   ↓
5. Function extracts: ip_address = params.get('___________')
   ↓
6. Function builds URL: f"{config['___________']}/api/v1/ip/{ip_address}"
   ↓
7. Makes HTTP request: requests.___(url, headers=..., timeout=___)
   ↓
8. Response received: status code ___ = success
   ↓
9. Normalizes data and returns: {"ip": ..., "reputation": ..., ___}
   ↓
10. FortiSOAR stores result at: vars.steps.___________.data
```

{{% expand "Click to check your answers" %}}

```
1. FortiSOAR receives playbook step request
   ↓
2. Calls: connector.execute(config, operation, params)
   File: connector.py
   ↓
3. Function maps operation name "get_ip_reputation" to function get_ip_reputation
   ↓
4. Calls: operations.get_ip_reputation(config, params)
   File: operations.py
   ↓
5. Function extracts: ip_address = params.get('ip_address')
   ↓
6. Function builds URL: f"{config['server_url']}/api/v1/ip/{ip_address}"
   ↓
7. Makes HTTP request: requests.get(url, headers=..., timeout=30)
   ↓
8. Response received: status code 200 = success
   ↓
9. Normalizes data and returns: {"ip": "192.0.2.1", "reputation": "malicious", "confidence": 95}
   ↓
10. FortiSOAR stores result at: vars.steps.Get_IP_Reputation.data
```

**Key Points:**

- `connector.py` is the traffic controller
- `operations.py` does the actual work
- Config provides connection info (URLs, keys)
- Params provide operation-specific inputs
- Result becomes available in playbook variables
  {{% /expand %}}

### Bonus Challenge: Find the Bug

This connector is failing. Where's the problem?

**Playbook Error Message:**

```
Error executing step Get_IP_Reputation:
ConnectorError: 'ip_address'
```

**connector.py:**

```python
def execute(self, config, operation, params, **kwargs):
    operations = {
        'get_ip_reputation': get_ip_reputation,
        'get_domain_reputation': get_domain_reputation
    }

    return operations[operation](config, params)
```

**operations.py:**

```python
def get_ip_reputation(config, params):
    ip = params['ip_address']  # Line 15
    url = f"{config['server_url']}/ip/{ip}"
    response = requests.get(url)
    return response.json()
```

**What's wrong and how do you fix it?**

{{% expand "Click for the diagnosis" %}}
**Problem:** Line 15 in operations.py uses `params['ip_address']` which throws `KeyError` if the parameter is missing or misspelled in the playbook.

**Symptom:** Error message shows `'ip_address'` which is the KeyError string representation.

**Fix:**

```python
def get_ip_reputation(config, params):
    ip = params.get('ip_address')
    if not ip:
        raise ConnectorError('IP address parameter is required')

    url = f"{config['server_url']}/ip/{ip}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()  # Also add error checking
    return response.json()
```

**Lesson:** Always use `.get()` for parameter access and validate required fields with helpful error messages.
{{% /expand %}}

---

```

---

## FOR MODULE: 30-lab1-basic-connector.md

### INSERT BEFORE: "Part 3: Writing the info.json File"

```markdown
---

## Part 2.5: API Exploration First!

**Time:** 15 minutes

Before writing any code, let's understand the API we're integrating.

### 🌐 Hands-On: Test the API Manually

**Step 1: Basic API Call**

Open your terminal and run:

```bash
curl http://ip-api.com/json/8.8.8.8
```

**Expected Result:**

```json
{
  "status": "success",
  "country": "United States",
  "city": "Mountain View",
  ...
}
```

✅ **Write down:** What HTTP status code did you get? _______

### **Step 2: Test Edge Cases**

Try these requests and document what happens:

```bash
# Invalid IP
curl http://ip-api.com/json/999.999.999.999

# Private IP
curl http://ip-api.com/json/192.168.1.1

# IPv6
curl http://ip-api.com/json/2001:4860:4860::8888
```

**Document Your Findings:**

| Test Case | HTTP Status | Response | Notes |
|-----------|-------------|----------|-------|
| Valid IP | 200 | `{"status": "success", ...}` | Full data returned |
| Invalid IP | ___ | _____________________ | _______________ |
| Private IP | ___ | _____________________ | _______________ |
| IPv6 | ___ | _____________________ | _______________ |

{{% expand "Click to see typical results" %}}
| Test Case | HTTP Status | Response | Notes |
|-----------|-------------|----------|-------|
| Valid IP | 200 | `{"status": "success", ...}` | Full data returned |
| Invalid IP | 200 | `{"status": "fail", "message": "invalid query"}` | Still returns 200! |
| Private IP | 200 | `{"status": "fail", "message": "reserved range"}` | Can't geolocate private IPs |
| IPv6 | 200 | `{"status": "success", ...}` | Works! |

**Critical Discovery:** This API returns HTTP 200 even for errors. You must check the `status` field in the JSON response!
{{% /expand %}}

### **Step 3: Identify Rate Limits**

Run this command 50 times quickly (or use a loop):

```bash
for i in {1..50}; do
  curl -s http://ip-api.com/json/8.8.8.8 | grep -E "status|message"
  sleep 1
done
```

**Question:** Did you hit a rate limit? What was the error message?

{{% expand "What to expect" %}}
**Rate Limit:** 45 requests per minute for free tier

**When hit:**

```json
{
  "message": "You have exceeded the maximum number of requests. Please try again later."
}
```

**For your connector:** You'll need to handle this gracefully!
{{% /expand %}}

### **Step 4: Plan Your Error Handling**

Based on your testing, list the error scenarios your connector must handle:

1. ✅ Invalid IP format
2. ✅ Private IP addresses
3. ✅ Rate limit exceeded
4. ✅ Network timeout
5. ✅ [Add your own] _______________
6. ✅ [Add your own] _______________

{{% notice tip %}}
**Pro Tip:** Testing the API first prevents surprises later! You now know exactly what your connector needs to handle.
{{% /notice %}}

### **Step 5: Design Your Response Format**

Look at the full API response. Which fields will you include in your connector's output?

**Available Fields:**

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

**Your Normalized Response Design:**

Required fields (always include):

- [ ] _______________
- [ ] _______________
- [ ] _______________

Optional fields (include if useful):

- [ ] _______________
- [ ] _______________

{{% expand "Suggested design" %}}
**Core Security/Investigation Fields:**

```json
{
  "status": "success",
  "ip_address": "8.8.8.8",
  "country": "United States",
  "country_code": "US",
  "city": "Mountain View",
  "region": "California",
  "isp": "Google LLC",
  "latitude": 37.4192,
  "longitude": -122.0574,
  "timezone": "America/Los_Angeles"
}
```

**Rationale:**

- IP address for correlation
- Country/city for geolocation
- ISP for infrastructure investigation
- Coordinates for mapping
- Skip: zip code, org name (less useful for security)
  {{% /expand %}}

### **Ready to Code?**

You now understand:

- ✅ How the API works
- ✅ What errors can occur
- ✅ What data you'll return
- ✅ Edge cases to handle

**Next:** Write the connector code with confidence!

---

```

### INSERT AFTER: Lab completion section

```markdown
---

## 🎯 Enhancement Challenges

Your basic connector works! Now level it up with these challenges.

### Challenge 1: Batch IP Lookup (Beginner)
**Goal:** Process multiple IPs in one operation

**Requirements:**
- Accept comma-separated IP addresses
- Return array of results
- Handle individual failures gracefully

**Starter Code:**
```python
def batch_lookup_ips(config, params):
    """
    Lookup multiple IPs at once
    
    Expected input: {"ip_addresses": "8.8.8.8, 1.1.1.1, 192.168.1.1"}
    Expected output: {"results": [...], "success_count": 2, "failed_count": 1}
    """
    
    # TODO: Parse comma-separated IPs
    ip_list = 
    
    # TODO: Loop through IPs
    results = []
    for ip in ip_list:
        try:
            # TODO: Call get_ip_location for each
            pass
        except ConnectorError as e:
            # TODO: Add error result
            pass
    
    # TODO: Return summary
    return {
        'results': results,
        'success_count': len([r for r in results if r.get('status') == 'success']),
        'failed_count': len([r for r in results if r.get('status') != 'success'])
    }
```

**Test Cases:**

```python
# Test 1: All valid
params = {'ip_addresses': '8.8.8.8, 1.1.1.1, 9.9.9.9'}

# Test 2: Mix of valid and invalid
params = {'ip_addresses': '8.8.8.8, invalid, 1.1.1.1'}

# Test 3: Empty input
params = {'ip_addresses': ''}
```

{{% expand "Solution" %}}

```python
def batch_lookup_ips(config, params):
    """Lookup multiple IPs at once"""

    # Parse IP list
    ip_string = params.get('ip_addresses', '')
    if not ip_string:
        raise ConnectorError('IP addresses parameter is required')

    # Split and clean
    ip_list = [ip.strip() for ip in ip_string.split(',') if ip.strip()]

    if not ip_list:
        raise ConnectorError('At least one IP address is required')

    # Process each IP
    results = []
    for ip in ip_list:
        try:
            result = get_ip_location(config, {'ip_address': ip})
            results.append(result)
        except ConnectorError as e:
            results.append({
                'status': 'failed',
                'ip_address': ip,
                'error': str(e)
            })

    # Return summary
    success_count = len([r for r in results if r.get('status') == 'success'])
    failed_count = len(results) - success_count

    return {
        'results': results,
        'total_processed': len(results),
        'success_count': success_count,
        'failed_count': failed_count
    }
```

{{% /expand %}}

**Verification:**

- [ ] Processes multiple IPs successfully
- [ ] Handles mix of valid/invalid IPs
- [ ] Returns summary statistics
- [ ] Provides clear error messages

---

### Challenge 2: Smart Caching (Intermediate)

**Goal:** Avoid repeated lookups for same IP

**Requirements:**

- Cache results in memory
- Expire after 1 hour
- Track cache hit rate

**Hints:**

```python
from datetime import datetime, timedelta

# Store: {ip: (data, timestamp)}
cache = {}


def is_cache_expired(timestamp, max_age_hours=1):
    return datetime.now() - timestamp > timedelta(hours=max_age_hours)
```

**Bonus:** Add cache statistics operation:

```python
def get_cache_stats(config, params):
    """Return cache performance metrics"""
    return {
        'cached_ips': len(cache),
        'oldest_entry': ...,
        'hit_rate': ...
    }
```

---

### Challenge 3: Input Validation (Intermediate)

**Goal:** Validate IP addresses before making API calls

**Requirements:**

- Reject obviously invalid formats
- Reject private IP ranges
- Provide helpful error messages

**Starter Code:**

```python
import ipaddress


def validate_ip_address(ip_string):
    """
    Validate IP address format and type
    
    Returns: Validated IP string
    Raises: ConnectorError if invalid
    """
    try:
        # TODO: Parse IP address
        ip = ipaddress.ip_address(ip_string)

        # TODO: Check if private
        if ip.is_private:
            raise ConnectorError(
                f'{ip_string} is a private IP address and cannot be geolocated'
            )

        # TODO: Return validated IP
        return str(ip)

    except ValueError:
        # TODO: Provide helpful error
        raise ConnectorError(f'Invalid IP address format: {ip_string}')
```

**Test Cases:**

```python
# Should pass
validate_ip_address('8.8.8.8')
validate_ip_address('2001:4860:4860::8888')

# Should fail with helpful messages
validate_ip_address('not-an-ip')
validate_ip_address('192.168.1.1')  # Private
validate_ip_address('999.999.999.999')
```

---

### Challenge 4: Rate Limit Handling (Advanced)

**Goal:** Handle API rate limits gracefully

**Requirements:**

- Track request count
- Implement exponential backoff
- Queue requests when limit approached

**Pseudocode:**

```python
request_count = 0
last_reset = datetime.now()


def check_rate_limit():
    """Check if we're approaching rate limit"""
    global request_count, last_reset

    # Reset counter every minute
    if datetime.now() - last_reset > timedelta(minutes=1):
        request_count = 0
        last_reset = datetime.now()

    # If approaching limit, wait
    if request_count >= 40:  # Leave buffer before 45/min limit
        # TODO: Implement wait logic
        pass

    request_count += 1
```

---

### Challenge 5: Enrichment Playbook (Practical)

**Goal:** Build a playbook that uses your connector

**Requirements:**

1. Trigger: Manual or on new Alert
2. Extract IP addresses from Alert
3. Lookup geolocation for each IP
4. Add location data to Alert record
5. Create note with findings

**Playbook Steps:**

```
1. Extract IPs (regex or field)
2. Batch Lookup (your connector)
3. Filter Results (only successful lookups)
4. Update Alert (add custom fields)
5. Create Note (summary of locations)
```

{{% notice tip %}}
**Hint:** Use FortiSOAR's "Update Record" step to add location data as custom fields on the Alert.
{{% /notice %}}

---

### Your Progress Tracker

| Challenge | Status | Difficulty | Notes |
|-----------|--------|------------|-------|
| Batch Lookup | ⬜ | ★☆☆ | Process multiple IPs |
| Smart Caching | ⬜ | ★★☆ | Performance optimization |
| Input Validation | ⬜ | ★★☆ | Better error handling |
| Rate Limiting | ⬜ | ★★★ | Production-ready feature |
| Enrichment Playbook | ⬜ | ★★☆ | Real-world application |

**Completed:** _____ / 5

---

```

---

## FOR MODULE: Python Primer - Additional Exercise

### INSERT at end of module

```markdown
---

## 🏋️ Practice Project: Mini Connector Simulator

**Time:** 30 minutes

Build a simple Python script that simulates how connectors work. This hands-on practice solidifies your understanding before building real connectors.

### Project Requirements

Create a Python script that:
1. Has a "config" dictionary (like connector configuration)
2. Has a "params" dictionary (like operation parameters)
3. Makes an API call to a free public API
4. Handles errors gracefully
5. Returns normalized data

### Starter Template

```python
import requests
from datetime import datetime

# Simulate connector configuration
config = {
    'server_url': 'https://api.coinbase.com',
    'timeout': 30
}

# Simulate operation parameters
params = {
    'currency_pair': 'BTC-USD'
}

def get_crypto_price(config, params):
    """
    Simulates a connector operation that fetches cryptocurrency prices
    
    This is what you'll build!
    """
    # TODO: Your code here
    pass

# Test your function
if __name__ == '__main__':
    try:
        result = get_crypto_price(config, params)
        print("Success!")
        print(result)
    except Exception as e:
        print(f"Error: {e}")
```

### Step-by-Step Guide

**Step 1: Extract and validate parameters**

```python
def get_crypto_price(config, params):
    # Get the currency pair from params
    pair = params.get('currency_pair')
    if not pair:
        raise ValueError('Currency pair is required')

    # Continue to step 2...
```

**Step 2: Build the API URL**

```python
    # Get config values
base_url = config.get('server_url', 'https://api.coinbase.com')
timeout = config.get('timeout', 30)

# Build endpoint URL
# Coinbase API: /v2/prices/{currency-pair}/spot
url = f"{base_url}/v2/prices/{pair}/spot"

print(f"Calling: {url}")  # For debugging
```

**Step 3: Make the API call with error handling**

```python
    try:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()  # Raises error for 4xx/5xx

    data = response.json()

    # Continue to step 4...

except requests.exceptions.Timeout:
    raise Exception(f'Request timed out after {timeout} seconds')

except requests.exceptions.ConnectionError:
    raise Exception(f'Cannot connect to {base_url}')

except Exception as e:
    raise Exception(f'API call failed: {str(e)}')
```

**Step 4: Normalize the response**

```python
        # Coinbase returns: {"data": {"base": "BTC", "currency": "USD", "amount": "45000.00"}}
# We'll normalize to a cleaner format

price_data = data.get('data', {})

return {
    'currency_pair': pair,
    'price': float(price_data.get('amount', 0)),
    'base_currency': price_data.get('base'),
    'quote_currency': price_data.get('currency'),
    'timestamp': datetime.now().isoformat(),
    'raw_response': data  # Keep original for reference
}
```

### Complete Solution

{{% expand "Click to see complete working code" %}}

```python
import requests
from datetime import datetime

config = {
    'server_url': 'https://api.coinbase.com',
    'timeout': 30
}

params = {
    'currency_pair': 'BTC-USD'
}


def get_crypto_price(config, params):
    """Fetch cryptocurrency spot price from Coinbase"""

    try:
        # Extract and validate
        pair = params.get('currency_pair')
        if not pair:
            raise ValueError('Currency pair is required (e.g., BTC-USD)')

        # Build URL
        base_url = config.get('server_url', 'https://api.coinbase.com')
        timeout = config.get('timeout', 30)
        url = f"{base_url}/v2/prices/{pair}/spot"

        print(f"Fetching price for {pair}...")

        # Make API call
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        # Parse response
        data = response.json()
        price_data = data.get('data', {})

        # Normalize
        result = {
            'currency_pair': pair,
            'price': float(price_data.get('amount', 0)),
            'base_currency': price_data.get('base'),
            'quote_currency': price_data.get('currency'),
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'raw_response': data
        }

        return result

    except requests.exceptions.Timeout:
        raise Exception(f'Request timed out after {timeout} seconds')

    except requests.exceptions.ConnectionError:
        raise Exception(f'Cannot connect to {base_url}. Check your internet connection.')

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 404:
            raise Exception(f'Currency pair {pair} not found. Try BTC-USD, ETH-USD, etc.')
        else:
            raise Exception(f'API error: HTTP {status}')

    except ValueError as e:
        raise Exception(str(e))

    except Exception as e:
        raise Exception(f'Unexpected error: {str(e)}')


# Test the function
if __name__ == '__main__':

    # Test 1: Valid request
    print("Test 1: Valid currency pair")
    try:
        result = get_crypto_price(config, params)
        print(f"✓ Success! {result['currency_pair']} = ${result['price']}")
    except Exception as e:
        print(f"✗ Failed: {e}")

    print("\n" + "=" * 50 + "\n")

    # Test 2: Invalid currency pair
    print("Test 2: Invalid currency pair")
    try:
        bad_params = {'currency_pair': 'INVALID-PAIR'}
        result = get_crypto_price(config, bad_params)
        print(f"✓ Unexpected success: {result}")
    except Exception as e:
        print(f"✓ Correctly handled error: {e}")

    print("\n" + "=" * 50 + "\n")

    # Test 3: Missing parameter
    print("Test 3: Missing parameter")
    try:
        empty_params = {}
        result = get_crypto_price(config, empty_params)
        print(f"✓ Unexpected success: {result}")
    except Exception as e:
        print(f"✓ Correctly handled error: {e}")

    print("\n" + "=" * 50 + "\n")

    # Test 4: Different currency
    print("Test 4: Different currency (ETH)")
    try:
        eth_params = {'currency_pair': 'ETH-USD'}
        result = get_crypto_price(config, eth_params)
        print(f"✓ Success! {result['currency_pair']} = ${result['price']}")
    except Exception as e:
        print(f"✗ Failed: {e}")
```

{{% /expand %}}

### Run and Test

1. Save the complete code as `connector_practice.py`
2. Install requests: `pip install requests`
3. Run: `python connector_practice.py`

**Expected Output:**

```
Test 1: Valid currency pair
Fetching price for BTC-USD...
✓ Success! BTC-USD = $45234.56

==================================================

Test 2: Invalid currency pair
Fetching price for INVALID-PAIR...
✓ Correctly handled error: API error: HTTP 404

==================================================

Test 3: Missing parameter
✓ Correctly handled error: Currency pair is required

==================================================

Test 4: Different currency (ETH)
Fetching price for ETH-USD...
✓ Success! ETH-USD = $2345.67
```

### What You Practiced

- ✓ Parameter extraction and validation
- ✓ Building dynamic URLs
- ✓ Making HTTP requests with timeouts
- ✓ Handling multiple error types
- ✓ Normalizing API responses
- ✓ Testing different scenarios

**This is exactly what FortiSOAR connectors do!**

### Bonus Challenges

1. **Add more operations:**
    - Get historical prices
    - Compare multiple currencies
    - Calculate percentage change

2. **Improve error messages:**
    - Suggest valid currency pairs when invalid one used
    - Add retry logic for timeouts

3. **Add features:**
    - Cache recent results
    - Log all API calls
    - Rate limiting

---

```

---

## USAGE INSTRUCTIONS

1. **Copy the sections** you want from above
2. **Paste them** into your existing modules at the indicated locations
3. **Test each exercise** yourself first to ensure smooth experience
4. **Adjust timing** based on your workshop schedule
5. **Create answer keys** if conducting live training

---

## Quick Implementation Checklist

- [ ] Add API exploration exercise before Lab 1 coding
- [ ] Insert debugging challenges in Python Primer
- [ ] Add execution tracing exercise in Architecture module
- [ ] Include progressive challenges at end of each lab
- [ ] Add achievement tracker to workshop intro
- [ ] Create practice project for Python skills
- [ ] Add batch IP lookup challenge to Lab 1
- [ ] Insert "broken code" debugging scenarios
- [ ] Add peer review checklist (if group training)
- [ ] Create connector scavenger hunt for intro module

**Start with top 3-5 items for immediate impact!**
