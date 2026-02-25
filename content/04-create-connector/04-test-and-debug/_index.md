---
title: "Test and Debug"
linkTitle: "Test and Debug"
description: "Run each operation in the RDK, inspect the results, use breakpoints to step through your code, and learn how to troubleshoot common issues."
weight: 4
---

Your connector has configuration, a health check, and three operations. In this chapter you'll run each one, inspect the live API responses, and use PyCharm's debugger to step through the code when something goes wrong.

{{% notice note %}}
If you need a refresher on breakpoints, stepping, and the debug panel, see the [Debug Python Code]({{< relref "02-debug-python" >}}) chapter.
{{% /notice %}}

---

## 1. Test the health check

Before testing operations, always verify the configuration first.

1. In the RDK panel, go to the **Configuration** tab.
2. Confirm the values:

   | Field | Value |
   |---|---|
   | **Server URL** | `https://icanhazdadjoke.com` |
   | **User-Agent** | `FortiSOAR Dad Jokes Connector (workshop)` |

3. Click the **Run** button (health check).
4. The output panel should show a **success** message.

<!-- ![img.png](images/health_check_success.png) -->

If it fails, check:
- Your machine has internet access.
- The Server URL has no trailing `/`.
- The field names in `info.json` match the keys in `operations.py` (`server_url`, `user_agent`).

---

## 2. Test Get Random Joke

1. Switch to the **Operations** tab in the RDK panel.
2. Select **Get Random Joke** from the operation dropdown.
3. This operation has no parameters, so click **Execute Action** right away.

You should see a JSON response like this in the output panel:

```json
{
    "id": "R7UfaahVfFd",
    "joke": "My dog used to chase people on a bike a lot. It got so bad I had to take his bike away.",
    "status": 200
}
```

<!-- ![img.png](images/test_random_joke.png) -->

{{% notice tip %}}
Run it a few times, and you'll get a different joke each time. Save one of the `id` values (e.g., `R7UfaahVfFd`) for the next test.
{{% /notice %}}

---

## 3. Test Get Joke by ID

1. Select **Get Joke by ID** from the operation dropdown.
2. In the **Joke ID** parameter field, paste one of the IDs from the previous test (e.g., `R7UfaahVfFd`).
3. Click **Execute Action**.

Expected output:

```json
{
    "id": "R7UfaahVfFd",
    "joke": "My dog used to chase people on a bike a lot. It got so bad I had to take his bike away.",
    "status": 200
}
```

Now test the error handling. Lets try an ID that doesn't exist:

1. Enter `this-id-is-fake` in the Joke ID field.
2. Click **Execute Action**.
3. You should see an error: `API error: 404 Not Found`.

<!-- ![img.png](images/test_joke_by_id.png) -->

This confirms our `_make_request` error handling is working. `response.raise_for_status()` caught the 404 and our `except` block converted it to a `ConnectorError`.

---

## 4. Test Search Jokes

1. Select **Search Jokes** from the operation dropdown.
2. Fill in the parameters:

   | Parameter | Value |
   |---|---|
   | **Search Term** | `cat` |
   | **Limit** | `5` |

3. Click **Execute Action**.

Expected output (your results may vary):

```json
{
    "current_page": 1,
    "limit": 5,
    "next_page": 1,
    "previous_page": 1,
    "results": [
        {
            "id": "iGJeEg4YDb",
            "joke": "What do you call a pile of cats? A meowntain."
        },
        {
            "id": "AQn3wPKeqrc",
            "joke": "It was raining cats and dogs the other day. I almost stepped in a poodle."
        }
    ],
    "search_term": "cat",
    "status": 200,
    "total_jokes": 3,
    "total_pages": 1
}
```

<!-- ![img.png](images/test_search_jokes.png) -->

Try a few more searches to explore the API:

| Search Term | What you'll find |
|---|---|
| `hipster` | 2 jokes about hipsters |
| `dog` | Several dog-related jokes |
| `math` | Math puns |
| `asdfghjkl` | An empty results list (great for testing edge cases) |

---

## 5. Debug an operation with breakpoints

Now let's use PyCharm's debugger to step through an operation and see exactly what happens at each stage.

### Set a breakpoint

1. Open `operations.py` in the editor.
2. Find the `search_jokes` function.
3. Click in the **gutter** next to the line `search_term = params.get("search_term")` to set a red breakpoint dot.

<!-- ![img.png](images/breakpoint_search_jokes.png) -->

### Run in debug mode

1. In the RDK, select **Search Jokes** and fill in `Search Term: dog` and `Limit: 3`.
2. Instead of clicking **Execute Action** normally, click the **Debug** button (the bug icon 🪲) next to it.

PyCharm pauses execution at your breakpoint. The line is highlighted in blue.

### Step through the code

Use the debugger controls to walk through the function:

| Step | Press | What you'll see                                                                     |
|---|---|-------------------------------------------------------------------------------------|
| 1 | `F8` (Step Over) | `search_term` now equals `"dog"` in the Variables tab.                              |
| 2 | `F8` | The `if not search_term` check is skipped (it has a value).                         |
| 3 | `F8` | `query_params` is created: `{"term": "dog"}`.                                       |
| 4 | `F8` | `limit` equals `3`.                                                                 |
| 5 | `F8` | `query_params` is now `{"term": "dog", "limit": 3}`.                                |
| 6 | `F7` (Step Into) | Jump into `_make_request`.                                                          |
| 7 | `F8` | Watch `url` become `"https://icanhazdadjoke.com/search"`.                           |
| 8 | `F8` | Watch `headers` populate with your User-Agent.                                      |
| 9 | `F8` | The `requests.get(...)` call fires. Watch `response` appear.                        |
| 10 | `F8` | `response.raise_for_status()` passes (status 200).                                  |
| 11 | `F8` | `response.json()` parses the JSON. Expand it in the Variables tab to see the jokes. |
| 12 | `F9` (Resume) | Execution finishes. The result appears in the RDK output panel.                     |

<!-- ![img.png](images/debug_stepping.png) -->

{{% notice tip %}}
Try adding a **Watch** expression for `len(response.json().get('results', []))` to see the result count update live as you step through the code.
{{% /notice %}}

---

## 6. Debug an error scenario

Let's intentionally cause an error and trace it through the debugger.

1. Set a breakpoint on the `response.raise_for_status()` line inside `_make_request`.
2. In the RDK, select **Get Joke by ID** and enter `this-does-not-exist` as the Joke ID.
3. Click **Debug**.
4. When execution pauses, hover over `response` in the Variables tab. You'll see:
   - `response.status_code` = `404`
   - `response.reason` = `"Not Found"`
5. Press `F8` - `raise_for_status()` throws an `HTTPError`.
6. Press `F8` - execution jumps to the `except requests.exceptions.HTTPError` block.
7. Press `F8` - the `ConnectorError` is raised with the message `"API error: 404 Not Found"`.

This is exactly how you'll debug real connector failures. You will often set a breakpoint in `_make_request`, reproduce the issue, and inspect what the API actually returned.

---

## 7. Common issues and troubleshooting

| Symptom | Likely cause | Fix                                                                                   |
|---|---|---------------------------------------------------------------------------------------|
| `ConnectorError: Cannot connect to...` | No internet, firewall blocking, or wrong URL. | Check network access. Verify the Server URL.                                          |
| `ConnectorError: API error: 404 Not Found` | Invalid joke ID or wrong endpoint path. | Check the `endpoint` string in your function.                                         |
| `KeyError: 'server_url'` | The field `name` in `info.json` doesn't match the key used in `operations.py`. | Ensure `"name": "server_url"` in config fields.                                       |
| `ModuleNotFoundError: requests` | The `requests` library isn't installed. | Click **Install Requirements** in the RDK Details tab, or run `pip install requests`. |
| Operation not found / unknown | The `operation` key in `info.json` doesn't match the key in `OPERATION_MAP`. | Compare the strings exactly, they're case-sensitive.                                  |
| Health check passes but operations fail | Health check uses `/` but the operation might use a different endpoint. | Debug the specific operation to see which URL is called.                              |

---

## 8. Export the connector

Once all three operations pass testing, you can package the connector for deployment.

1. Go to the **Details** tab in the RDK.
2. *(Optional)* Click **Validate Connector** to run the automated checks. Fix any warnings.
3. *(Optional)* Click **Generate Playbooks** to create sample playbooks from your operations.
4. *(Optional)* Click **Generate Documents** to create documentation.
5. Click **Export**.
6. Choose a destination folder.
7. The RDK packages everything into a `.tgz` file (e.g., `dad-jokes-1.0.0.tgz`).

This `.tgz` file can be uploaded directly to FortiSOAR under **Content Hub → Connectors → Import**.

---

## Summary

You've built, tested, and debugged a complete connector from scratch:

- ✅ **Health check** - verified API connectivity
- ✅ **Get Random Joke** - tested a no-parameter operation
- ✅ **Get Joke by ID** - tested with valid and invalid IDs
- ✅ **Search Jokes** - tested with different search terms and limits
- ✅ **Debugger** - stepped through live API calls with breakpoints
- ✅ **Error handling** - traced a 404 error through the exception chain
- ✅ **Export** - packaged the connector as a `.tgz` for deployment


### 🎉 Congratulations!

You've completed the **Build Your First Connector** section. You now know how to:

1. Create a connector project with the RDK
2. Add configuration fields
3. Define operations with parameters
4. Write Python functions that call a real API
5. Test and debug operations locally
6. Export a deployable `.tgz` package

You're ready to build connectors for any REST API.
