ZenPacks.zenoss.PagerDuty
===============================

About
-------------
This ZenPack extends Zenoss by providing a new PagerDuty notification type that allows to send Zenoss events to PagerDuty services via Events API v1.

### Prerequisites
| Prerequisite     | Restriction |
| :------- | ---: |
| Product | Zenoss 4.2.5 or higher    |
| Required ZenPacks    | None   |
| Other dependencies     | None |

ZenPack Installation / Removal
----------
Install or remove this ZenPack following the instructions in the Zenoss Resource Manager Admin Guide matching your Zenoss RM version.

Usage
---------
**1) Configure  PagerDuty instance**
In order for PagerDuty to work with Zenoss an API key should be obtained. In PagerDuty dashboard go to Configuration->API access->Create API Key. Choose API version "v1 Legacy". After that create an integration of type "Events API v1" for necessary services.

**2) In Zenoss**
Go to ADVANCED->Settings->PagerDuty. Enter your PagerDuty subdomain & API key generated before and click "Apply".    
Afer creating the notification of PagerDuty type, the following properties can be edited in notification content tab:

| Title     |Descritpion  |
| :------- | :---|
| Service | PagerDuty Service to send events to.| 
| Description| A brief text summary of the event.|
| Source     |The unique location of the affected system.|
| Details | Object with custom details to be sent. |





