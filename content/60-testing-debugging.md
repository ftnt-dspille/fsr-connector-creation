---
title: "Testing, Debugging, and Deployment"
linkTitle: "Testing & Deployment"
weight: 60
---

## Module Overview

**Duration:** 60 minutes

**What You'll Learn:**
- Debug connector issues effectively
- Write unit tests for connectors
- Validate connector code quality
- Deploy connectors to production
- Monitor connector performance

---

## Part 1: Debugging Connectors

### Understanding the Connector Execution Flow

When a connector operation executes:

1. **FortiSOAR receives request** → Playbook step invokes connector
2. **Configuration loaded** → Connector config passed to `execute()` method
3. **Operation routed** → `connector.py` routes to appropriate function
4. **Function executes** → `operations.py` function runs
5. **Response returned** → Result sent back to playbook
6. **Logged** → Execution logged to `connectors.log`

### Task 1.1: Enable Debug Logging

**Step 1:** Increase log verbosity

Edit `/opt/cyops-integrations/integrations/configs/config.ini`:

```ini
[logging]
connector_logger_level = DEBUG
```

**Step 2:** Restart the integration service

```bash
sudo systemctl restart cyops-integrations
```

**Step 3:** Add logging to your connector

```python
from connectors.core.connector import get_logger

logger = get_logger('your_connector_name')

def your_operation(config, params):
    logger.debug(f'Operation called with params: {params}')
    
    try:
        logger.info('Making API request')
        response = make_api_call(config, endpoint)
        logger.debug(f'API response: {response}')
        
        return response
        
    except Exception as e:
        logger.error(f'Operation failed: {str(e)}', exc_info=True)
        raise
```

{{% notice warning %}}
Never log sensitive information like passwords, API keys, or personal data! Use DEBUG level sparingly in production.
{{% /notice %}}

### Task 1.2: Monitor Connector Logs

**View real-time logs:**
```bash
tail -f /var/log/cyops/cyops-integrations/connectors.log
```

**Search for specific connector:**
```bash
grep "your_connector_name" /var/log/cyops/cyops-integrations/connectors.log
```

**View errors only:**
```bash
grep "ERROR" /var/log/cyops/cyops-integrations/connectors.log | tail -n 50
```

**Log Format:**
```
2024-01-25 10:30:45 INFO your_connector_name operations get_ip_reputation(): Starting operation
2024-01-25 10:30:45 DEBUG your_connector_name operations get_ip_reputation(): Request params: {'ip': '8.8.8.8'}
2024-01-25 10:30:46 ERROR your_connector_name operations get_ip_reputation(): API request failed: Connection timeout
```

### Task 1.3: Use the dev_execute Method

During development, use `dev_execute` to avoid service restarts:

In `connector.py`:
```python
def execute(self, config, operation, params, *args, **kwargs):
    # For development - reloads code on every execution
    return self.dev_execute(config, operation, params)
    
    # For production - use this instead:
    # supported_operations = {'get_reputation': get_ip_reputation}
    # return supported_operations[operation](config, params)
```

{{% notice tip %}}
Remember to switch back to the standard `execute()` method before production deployment!
{{% /notice %}}

### Task 1.4: Common Issues and Solutions

**Issue: ConnectorError: No module named 'your_module'**
```
Solution: Install missing dependency
$ sudo /opt/cyops-integrations/.env/bin/pip install your_module --break-system-packages
```

**Issue: Health check fails immediately**
```
Solution: Check connector logs for the specific error
$ grep "check_health" /var/log/cyops/cyops-integrations/connectors.log | tail -n 10
```

**Issue: Operation returns None**
```
Solution: Ensure your operation function returns data (not just prints it)
# Bad:
def get_data(config, params):
    result = api_call()
    print(result)  # ✗

# Good:
def get_data(config, params):
    result = api_call()
    return result  # ✓
```

**Issue: Changes to info.json not reflected**
```
Solution: Reimport the connector
$ sudo /opt/cyops-integrations/.env/bin/python /opt/cyops-integrations/integrations/manage.py reimport_connector -n connector_name -cv 1.0.0 -migrate
```

---

## Part 2: Writing Unit Tests

### Task 2.1: Understand Test Structure

FortiSOAR RDK automatically creates test files for each operation:

```
connector-name/
├── tests/
│   ├── __init__.py
│   ├── test_get_ip_reputation.py
│   ├── test_get_domain_reputation.py
│   └── test_common.py
```

### Task 2.2: Write a Basic Unit Test

Create `tests/test_get_ip_reputation.py`:

```python
"""
Unit tests for get_ip_reputation operation
"""
import pytest
from unittest.mock import Mock, patch
from operations import get_ip_reputation
from connectors.core.connector import ConnectorError


class TestGetIPReputation:
    
    @pytest.fixture
    def mock_config(self):
        """Mock connector configuration"""
        return {
            'server_url': 'https://api.example.com',
            'api_key': 'test_key_12345',
            'verify_ssl': True
        }
    
    @pytest.fixture
    def mock_response(self):
        """Mock successful API response"""
        return {
            'ip': '8.8.8.8',
            'reputation': 'Good',
            'confidence': 95,
            'country': 'United States'
        }
    
    def test_successful_request(self, mock_config, mock_response):
        """Test successful IP reputation lookup"""
        
        with patch('operations.make_api_call') as mock_api:
            mock_api.return_value = mock_response
            
            params = {'ip_address': '8.8.8.8'}
            result = get_ip_reputation(mock_config, params)
            
            assert result['ip'] == '8.8.8.8'
            assert result['reputation'] == 'Good'
            assert result['confidence'] == 95
            
            # Verify API was called correctly
            mock_api.assert_called_once()
    
    def test_missing_ip_parameter(self, mock_config):
        """Test error handling for missing IP address"""
        
        params = {}  # No IP address provided
        
        with pytest.raises(ConnectorError) as exc_info:
            get_ip_reputation(mock_config, params)
        
        assert 'IP address is required' in str(exc_info.value)
    
    def test_invalid_ip_format(self, mock_config):
        """Test validation of IP address format"""
        
        params = {'ip_address': 'not_an_ip'}
        
        with pytest.raises(ConnectorError) as exc_info:
            get_ip_reputation(mock_config, params)
        
        assert 'Invalid IP address' in str(exc_info.value)
    
    def test_api_authentication_failure(self, mock_config):
        """Test handling of authentication errors"""
        
        with patch('operations.make_api_call') as mock_api:
            mock_api.side_effect = ConnectorError('Authentication failed')
            
            params = {'ip_address': '8.8.8.8'}
            
            with pytest.raises(ConnectorError) as exc_info:
                get_ip_reputation(mock_config, params)
            
            assert 'Authentication failed' in str(exc_info.value)
    
    def test_api_rate_limiting(self, mock_config):
        """Test handling of rate limit errors"""
        
        with patch('operations.make_api_call') as mock_api:
            mock_api.side_effect = ConnectorError('Rate limit exceeded')
            
            params = {'ip_address': '8.8.8.8'}
            
            with pytest.raises(ConnectorError) as exc_info:
                get_ip_reputation(mock_config, params)
            
            assert 'Rate limit' in str(exc_info.value)
```

### Task 2.3: Run Unit Tests

**Using pytest directly:**
```bash
cd /opt/cyops-integrations/integrations/connectors/connector-name
pytest tests/ -v
```

**Using FortiSOAR RDK:**
1. Open connector in RDK
2. Click **Run Unit Test** button
3. View results in output panel

**Expected output:**
```
tests/test_get_ip_reputation.py::TestGetIPReputation::test_successful_request PASSED
tests/test_get_ip_reputation.py::TestGetIPReputation::test_missing_ip_parameter PASSED
tests/test_get_ip_reputation.py::TestGetIPReputation::test_invalid_ip_format PASSED
tests/test_get_ip_reputation.py::TestGetIPReputation::test_api_authentication_failure PASSED
tests/test_get_ip_reputation.py::TestGetIPReputation::test_api_rate_limiting PASSED

======================== 5 passed in 0.42s ========================
```

---

## Part 3: Code Validation

### Task 3.1: Use the Validate Connector Tool

The RDK includes a validation tool that checks for common issues:

**In RDK:**
1. Click **Validate Connector**
2. Review generated report

**From command line:**
```bash
cd /opt/cyops-integrations/integrations
python manage.py validate_connector -n connector-name -cv 1.0.0
```

**What gets validated:**

| Check | Description |
|-------|-------------|
| **Connector Structure** | Verifies required files exist |
| **info.json Syntax** | Validates JSON structure |
| **Operation Names** | Ensures camelCase naming |
| **Descriptions** | Checks for empty descriptions |
| **Icon Files** | Verifies correct image sizes |
| **Playbooks** | Checks playbook state (Inactive) |
| **Dependencies** | Validates requirements.txt |

### Task 3.2: Review Validation Report

Sample validation report:

```
Connector Validation Test Case Report: YourConnector v1.0.0

Test Case Execution Summary:

✓ PASS: Connector contains at least one action
✓ PASS: Action names are in camelCase
✓ PASS: Action descriptions are not empty
✓ PASS: Icon files are correct size (40x40, 100x100)
✓ PASS: Playbooks are in Inactive state
✗ FAIL: Operation 'Get Data' description not in sentence case
✗ FAIL: requirements.txt contains restricted versions (requests==2.28.0)
✗ WARN: No online documentation link provided

Recommendations:
1. Update operation description to start with capital letter
2. Remove version restrictions from requirements.txt
3. Add help_online URL to info.json
```

### Task 3.3: Fix Common Validation Issues

**Issue: Operation names not camelCase**
```json
// Bad
"operation": "Get_IP_Reputation"

// Good
"operation": "getIPReputation"
```

**Issue: Restricted dependency versions**
```
// Bad - requirements.txt
requests==2.28.0

// Good
requests>=2.28.0
```

**Issue: Playbooks in Active state**
- Open each playbook in the collection
- Set to **Inactive** state before packaging
- Active playbooks execute automatically (not desired for samples)

---

## Part 4: Performance Testing

### Task 4.1: Test with Large Datasets

Create a test playbook that processes bulk data:

```python
# Test with 1000 indicators
test_data = [f"192.168.1.{i}" for i in range(1, 1001)]

# Time the operation
import time
start_time = time.time()

result = bulk_enrich_indicators(config, {'indicator_values': test_data})

end_time = time.time()
duration = end_time - start_time

print(f"Processed {len(test_data)} indicators in {duration:.2f} seconds")
print(f"Average: {duration/len(test_data)*1000:.2f} ms per indicator")
```

**Performance Targets:**

| Operation Type | Target | Notes |
|----------------|--------|-------|
| Single lookup | < 2 seconds | Individual API calls |
| Bulk operation (100 items) | < 5 seconds | Batched requests |
| Health check | < 5 seconds | Connection validation |
| Data ingestion (1000 records) | < 60 seconds | Scheduled pulls |

### Task 4.2: Monitor API Rate Limits

Track API usage to avoid rate limiting:

```python
class APIMetrics:
    def __init__(self):
        self.calls = []
    
    def record_call(self):
        self.calls.append(datetime.now())
    
    def get_calls_last_minute(self):
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_calls = [c for c in self.calls if c > one_minute_ago]
        return len(recent_calls)
    
    def check_rate_limit(self, max_per_minute=60):
        current_rate = self.get_calls_last_minute()
        if current_rate >= max_per_minute:
            raise ConnectorError(f'Rate limit reached: {current_rate}/{max_per_minute} calls per minute')

# Use in operations
metrics = APIMetrics()

def get_ip_reputation(config, params):
    metrics.check_rate_limit()
    metrics.record_call()
    # ... rest of operation
```

---

## Part 5: Deployment

### Task 5.1: Package the Connector

**Using RDK:**
1. Click **Export**
2. Choose destination folder
3. Connector is saved as `.tgz` file

**Using command line:**
```bash
cd /opt/cyops-integrations/integrations/connectors
tar -czf connector-name.tgz connector-name/
```

**What gets packaged:**
```
connector-name.tgz
└── connector-name/
    ├── info.json
    ├── connector.py
    ├── operations.py
    ├── requirements.txt
    ├── images/
    │   ├── small_icon.png
    │   └── large_icon.png
    └── playbooks/
        └── playbooks.json
```

### Task 5.2: Pre-Deployment Checklist

Before deploying to production, verify:

**Code Quality:**
- [ ] No hardcoded credentials or test data
- [ ] Debug logging removed or set to INFO level
- [ ] `dev_execute` changed back to `execute`
- [ ] All exceptions properly handled
- [ ] Input validation on all user-provided data

**Documentation:**
- [ ] README.md with configuration instructions
- [ ] Operation descriptions are clear
- [ ] Sample playbooks are included and inactive
- [ ] Troubleshooting section added

**Testing:**
- [ ] All unit tests pass
- [ ] Manual testing completed
- [ ] Performance tested with realistic data volumes
- [ ] Health check validates configuration correctly

**Metadata:**
- [ ] Version number follows semantic versioning (x.y.z)
- [ ] Publisher name is accurate
- [ ] Category is appropriate
- [ ] Icons are correct size and format

### Task 5.3: Deploy to FortiSOAR

1. **Upload Connector:**
   - Navigate to **Content Hub > Create**
   - Drag and drop the `.tgz` file
   - Or use **Import > Upload File**

2. **Configure:**
   - Click the connector card
   - Click **Add Configuration**
   - Enter connection details
   - Click **Test Connectivity**
   - Save configuration

3. **Verify Installation:**
   - Check connector appears in Content Hub
   - Health check shows "Available"
   - Sample playbooks imported successfully
   - Operations visible in Playbook Designer

### Task 5.4: Production Monitoring

After deployment, monitor:

**Connector Health:**
```bash
# Check connector status
curl -k -X GET "https://fortisoar-instance/api/integration/connectors/connector-name" \
  -H "Authorization: Bearer <token>"
```

**Error Rate:**
```bash
# Count errors in last hour
grep "ERROR" /var/log/cyops/cyops-integrations/connectors.log | \
  grep "connector-name" | \
  grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" | \
  wc -l
```

**Performance Metrics:**
- Average response time per operation
- Number of rate limit errors
- Failed health checks
- Playbook execution failures using this connector

---

## Part 6: Versioning and Updates

### Task 6.1: Semantic Versioning

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 1.0.0 → 1.1.0)
- **PATCH**: Bug fixes (e.g., 1.0.0 → 1.0.1)

**Examples:**

| Change | Version Update | Example |
|--------|----------------|---------|
| Fixed authentication bug | 1.0.0 → 1.0.1 | PATCH |
| Added new "Bulk Search" operation | 1.0.1 → 1.1.0 | MINOR |
| Changed parameter names in existing operations | 1.1.0 → 2.0.0 | MAJOR |

### Task 6.2: Update Existing Connector

When updating a connector:

1. **Increment version** in info.json
2. **Test thoroughly** - especially existing playbooks
3. **Document changes** in release_notes.md
4. **Consider migration** if breaking changes

**Example release_notes.md:**
```markdown
# Release Notes

## Version 1.1.0
**Release Date:** 2024-01-25

### New Features
- Added bulk enrichment operation for improved performance
- Implemented response caching with 5-minute TTL
- Added custom function for indicator lookup

### Enhancements
- Improved error messages for authentication failures
- Added retry logic for transient network errors
- Updated dependencies to latest versions

### Bug Fixes
- Fixed issue with special characters in domain names
- Resolved timeout on large dataset processing
- Corrected confidence score calculation

## Version 1.0.0
**Release Date:** 2024-01-01

### Initial Release
- Basic IP and domain reputation lookup
- Health check functionality
- Sample playbooks
```

### Task 6.3: Backward Compatibility

When updating connectors, maintain backward compatibility when possible:

**Bad (Breaking Change):**
```json
// Version 1.0.0
"parameters": [{
  "name": "ip",
  "type": "text"
}]

// Version 2.0.0 - BREAKS existing playbooks!
"parameters": [{
  "name": "ip_address",  // ✗ Changed parameter name
  "type": "text"
}]
```

**Good (Backward Compatible):**
```json
// Version 1.0.0
"parameters": [{
  "name": "ip",
  "type": "text"
}]

// Version 1.1.0 - Maintains compatibility
"parameters": [{
  "name": "ip",
  "type": "text"
}, {
  "name": "include_geolocation",  // ✓ Added new optional parameter
  "type": "checkbox",
  "required": false
}]
```

---

## Part 7: Troubleshooting Guide

### Common Issues and Solutions

**Issue: Connector not appearing after import**
```
Symptoms: .tgz uploads successfully but connector not visible
Solutions:
1. Check connector name matches folder name in .tgz
2. Verify info.json is valid JSON (use jsonlint.com)
3. Check logs: grep "import" /var/log/cyops/cyops-integrations/connectors.log
```

**Issue: Dependencies fail to install**
```
Symptoms: Connector imports but operations fail with ImportError
Solutions:
1. Check requirements.txt format (one package per line)
2. Install manually: 
   sudo /opt/cyops-integrations/.env/bin/pip install package-name --break-system-packages
3. Verify network connectivity from FortiSOAR instance
4. Check for OS-level dependencies (some packages require system libraries)
```

**Issue: Health check always fails**
```
Symptoms: Configuration saves but health check shows "Disconnected"
Solutions:
1. Add debug logging to check_health() function
2. Verify network connectivity: curl -k https://api.example.com
3. Check firewall rules
4. Validate API credentials
5. Review check_health() return value (must return True)
```

**Issue: Playbooks can't find connector operation**
```
Symptoms: Playbook step shows "Operation not found"
Solutions:
1. Verify operation name in info.json matches operations.py function
2. Check connector.py routes operation correctly
3. Confirm connector version in playbook matches installed version
4. Reimport connector if info.json was modified
```

**Issue: Custom function not appearing in Dynamic Values**
```
Symptoms: Function marked with include_as_function but not visible
Solutions:
1. Verify "include_as_function": true is set in operation definition
2. Confirm connector is published (not in draft state)
3. Check function_category is specified
4. Refresh page or clear browser cache
```

---

## Module Summary

You've learned essential skills for professional connector development:

✓ **Debugging** with logs, dev_execute, and systematic troubleshooting  
✓ **Testing** with unit tests and validation tools  
✓ **Performance** optimization and monitoring  
✓ **Deployment** packaging and distribution  
✓ **Maintenance** through versioning and updates  

**Best Practices Summary:**

1. **Log strategically** - enough to debug, not so much it impacts performance
2. **Test thoroughly** - unit tests, integration tests, and edge cases
3. **Validate before deployment** - use the validation tool
4. **Monitor in production** - track errors and performance
5. **Version carefully** - semantic versioning and backward compatibility
6. **Document everything** - README, release notes, and inline comments

---

## Workshop Completion

Congratulations! You've completed the FortiSOAR Connector Development Workshop.

You now have the skills to:
- Build connectors from simple to advanced complexity
- Implement data ingestion and enrichment
- Test and debug effectively
- Deploy and maintain production connectors

**Certification:**
[Certificate of Completion - FortiSOAR Connector Development Workshop]

**Next Steps:**
- Build a connector for your organization's tools
- Contribute to the FortiSOAR community
- Explore FortiSOAR Solution Packs
- Join the FortiSOAR Developer Community

---

## Additional Resources

**Documentation:**
- [FortiSOAR Connectors Guide](https://docs.fortinet.com/document/fortisoar/latest/connectors-guide/)
- [FortiSOAR RDK Documentation](https://docs.fortinet.com/document/fortisoar/latest/rdk/)
- [FortiSOAR API Reference](https://docs.fortinet.com/document/fortisoar/latest/api-guide/)

**Community:**
- FortiSOAR Community Forums
- GitHub - Partner Managed Content
- FortiSOAR Content Hub

**Tools:**
- PyCharm (with FortiSOAR RDK plugin)
- Postman (for API testing)
- JSON Validator (jsonlint.com)
- Python debugger (pdb)

## Feedback

We value your feedback! Please share your workshop experience:
- What worked well?
- What could be improved?
- What additional topics would you like covered?

Contact: fortisoar-training@fortinet.com

---

**Thank you for participating in this workshop!**
