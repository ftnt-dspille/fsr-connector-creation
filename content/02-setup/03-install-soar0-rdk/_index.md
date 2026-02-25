---
title: "Install SOAR RDK"
linkTitle: "Install SOAR RDK"
weight: 10
description: "Description"
---

In this section we will be installing and configuring the PyCharm RDK in FortiSOAR

### Download SOAR RDK ZIP

1. Download the file below to your machine that has pycharm
   
   {{% resources style="tip" title="FortisSOAR PyCharm RDK Download" pattern=".*\.zip" /%}}

2. Open PyCharm
3. Navigate to **Settings > Plugins**
4. Click **Install Plugin from Disk**
5. Select the downloaded RDK `.zip` file
6. Restart PyCharm

### Configure Python Environment

1. Click **FortiSOAR RDK** from the toolbar
2. Select **Configure Python Path**
3. Point to your Python 3 installation
4. Click **OK** to install dependencies

### Import Existing Connector

1. Click **FortiSOAR RDK > Import FortiSOAR Connector**
2. Browse to your connector's `.tgz` file
3. The connector opens in the RDK interface

### Use RDK Features

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