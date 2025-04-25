---
title: "Troubleshooting"
linkTitle: "Troubleshooting"
weight: 50
---

## Unable to SSH to Device

If you are unable to SSH to a device from outside Fabric Studio native console, the access may be turned off

### Global Settings

By Default the SSH Access via Public internet is disabled. 

Admin & Guest means = that you MUST be logged in to Fabric Studio web frontend to have access to the device using the SSH web frontend.

To verify SSH access, there are two layers we need to validate. The first layer is in the Fabric Studio **System > Settings** . Ensure that HTTPS and SSH ports are enabled. 
![img_2.png](img_2.png?height=400px)

#### Device Level
1. In the Fabric configuration, Right Click your Device and Click **Edit**
![img.png](img.png?height=350px)
2. Scroll down and Expand the **Access** Section
![img_1.png](img_1.png?height=400px)
3. Change the **HTTPS** and **SSH** _Allowed to_ column from **Allowed & Guest** to **Any**

More information is available on the Fabric Studio Docs: https://register.fabricstudio.net/docs/fabric-studio/2.0.2/security.html#ssh-access-to-device