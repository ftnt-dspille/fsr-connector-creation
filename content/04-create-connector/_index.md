---
title: "Build Your First Connector"
linkTitle: "3. Build Your First Connector"
description: "A step-by-step walkthrough of building a FortiSOAR connector from scratch - from creating the project to testing live API calls - using the free Dad Joke API."
weight: 40
---

In this section you'll build a complete FortiSOAR connector from scratch using the **PyCharm RDK**. By the end, you'll have a working connector that talks to a real API, with configuration parameters, multiple operations, and a health check - all tested locally.

{{% notice note %}}
This section assumes you have completed the [setup guides]({{< relref "02-setup" >}}), including [installing PyCharm and Python]({{< relref "01-install-pycharm-python" >}}) and [installing the SOAR RDK]({{< relref "03-install-soar-rdk" >}}).
{{% /notice %}}

---

### The API we're using

We'll build a connector for [icanhazdadjoke.com](https://icanhazdadjoke.com/api). This is a free API that doesn't require authentication. This means we can focus on building a simple connector without worrying about API keys. 

The API has three endpoints we'll use for our connector: 

| Endpoint | Method | What it does |
|---|---|---|
| `GET /` | GET | Returns a random dad joke |
| `GET /j/<joke_id>` | GET | Returns a specific joke by its ID |
| `GET /search?term=<query>` | GET | Searches for jokes matching a keyword |

All endpoints return JSON when you send the header `Accept: application/json`.

{{% notice tip %}}
Even though this is a joke API, everything you learn here from configuration fields, operation parameters, and HTTP requests is directly applicable to tools like FortiManager, NSlookup, or any other REST API.
{{% /notice %}}

---

### What we're building

By the end of this section your connector will have a connector that requires a configuration for server url and a header, which performs a health check, and three operations/actions:

| Feature           | Details                                                          |
|-------------------|------------------------------------------------------------------|
| **Configuration** | Server URL and a custom User-Agent header                        |
| **Health Check**  | Verifies the API is reachable                                    |
| **Operation 1**   | **Get Random Joke** - fetches a random dad joke                  |
| **Operation 2**   | **Get Joke by ID** - fetches a specific joke using its ID        |
| **Operation 3**   | **Search Jokes** - searches for jokes by keyword with pagination |

---

### Chapters

{{% children description="true" %}}
