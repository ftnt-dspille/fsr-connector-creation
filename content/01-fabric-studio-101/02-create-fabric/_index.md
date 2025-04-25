---
title: "Creating a Fabric"
linkTitle: "Creating a Fabric"
weight: 30
description: "Creating your first Fabric environment"
---

## Overview

After successfully registering your Fabric Studio, you can create your first Fabric environment. You have two options:

- Creating a Fabric from the default minimal template
- Creating a Fabric from an existing template in a repository

## Creating from a Minimal Fabric

1. Navigate to Fabric Workspace
2. Click the **Create** button
3. Choose **Fabric**
   ![Creating a new Fabric](images/slide4_image1.png)
4. Enter a name or use the default
5. Click **OK**
   ![Naming your Fabric](images/slide4_image2.png)

Your first Fabric environment is now created with the following default components:

- "NAT Internet" router for internet access
- A switch connected to this router
- A management switch to allow Fabric Studio to control devices (configuration backup/restore, license installation, access, etc.)

![Default Fabric layout](images/slide5_image1.png)

## Adding Devices

### Add a FortiGate

1. Click the **+** button in the upper left of the topology view
2. From the menu, you can select:
    - **Switch**: a Fabric Studio switch
    - **Router**: a Fabric Studio router
    - **Device**: any supported Fortinet and third-party products
    - **FortiGate**: a shortcut to add a FortiGate device
3. Click on **FortiGate**
4. The FortiGate is added and automatically connected to the Management switch with an IP address in the management network

More information on supported products is available [here](https://register.fabricstudio.net/docs/fabric-studio/2.0.2/supported.html#fortinet-products)

### Connect the Device

To make the FortiGate functional:

1. Click the **Cable** button in the upper left
2. Click and drag from the FortiGate to the Switch
3. The FortiGate is now connected to the Switch through port 2, with an IP address
4. The DNS nameserver and default route are automatically configured

## Installing Your Fabric

To deploy your configured Fabric:

1. Click the **Install** button and confirm
2. The installation runs in the background with a progress window
3. Each device is installed by its own background task
4. You can monitor all tasks and logs from the task list

## Accessing Devices

To access your FortiGate:

1. Right-click on the FortiGate device and choose **Access**
2. Select your connection method (HTTPS, SSH, etc.)

{{% notice tip %}}
You can also perform general actions like Shutdown, Power-on, Configuration backup, and more from this menu.
{{% /notice %}}

You can also:

- Re-install only the FortiGate
- Uninstall it (destroying the VM) without affecting other devices

## Updating a Running Fabric

### Adding a New Device

To add a Lubuntu host to your existing Fabric:

1. Select the Lubuntu device from the device menu
2. Click the **Cable** button from the diagram
   ![Adding a Lubuntu host](images/slide13_image1.png)
3. Pull a cable to connect your Lubuntu to the FortiGate
4. Click the **Apply Changes** button to synchronize
   ![Connecting to FortiGate](images/slide13_image2.png)
5. Fabric Studio will install the VM

## Creating from a Fabric Template

For more complex setups, you can start with a pre-configured template:

1. Go to Fabric Workspace
2. Click on the **Create** button
3. Choose **Fabric from Template**

![Creating from template](images/slide15_image1.png)

{{% notice note %}}
Templates provide pre-configured environments with multiple devices and connections already set up for specific use cases.
{{% /notice %}}